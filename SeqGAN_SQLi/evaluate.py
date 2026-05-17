"""Sprint 5: Evaluation — ASR (real WAF + dev proxy), Syntax, Self-BLEU-3,
Relex Uniqueness, Type Entropy, Novel n-gram Ratio, Per-type Breakdown."""
import os
import sys
import argparse
import json
import math
import re
import numpy as np
import pandas as pd
import sqlparse
import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from src.reward import RewardOracle


# ── Existing metrics ──────────────────────────────────────────────────────────

def syntax_validity(payloads):
    count = 0
    for p in payloads:
        try:
            stmts = sqlparse.parse(p.strip())
            if stmts and stmts[0].tokens:
                count += 1
        except Exception:
            pass
    return count / len(payloads)


def asr_proxy(payloads):
    """Dev-mode ASR: heuristic bypass proxy (no Docker WAF)."""
    oracle = RewardOracle()
    bypassed = [oracle.bypass_proxy(p) > 0 for p in payloads]
    return np.array(bypassed, dtype=float)


def asr_real_waf(payloads, waf_endpoint: str, timeout: float = 5.0):
    """Real WAF ASR: calls ModSecurity Docker REST endpoint.

    Tiered scoring: bypass=1.0, partial=0.5 (some rules triggered), blocked=0.0.
    Falls back to dev proxy if endpoint unreachable.
    """
    scores = []
    for p in payloads:
        try:
            resp = requests.post(
                f"{waf_endpoint.rstrip('/')}/check",
                json={"payload": p},
                timeout=timeout,
            )
            if resp.status_code == 200:
                data = resp.json()
                if data.get("blocked", True):
                    score = 0.0
                elif data.get("rules_triggered", 0) > 0:
                    score = 0.5
                else:
                    score = 1.0
            else:
                score = float("nan")
        except Exception:
            score = float("nan")
        scores.append(score)
    arr = np.array(scores, dtype=float)
    # Fall back to dev proxy for any failed calls
    valid = ~np.isnan(arr)
    if valid.sum() == 0:
        print("  WARNING: WAF endpoint unreachable — falling back to dev proxy")
        return asr_proxy(payloads)
    if valid.sum() < len(arr):
        print(f"  WARNING: {(~valid).sum()} WAF calls failed — using dev proxy for those")
        proxy = asr_proxy(payloads)
        arr[~valid] = proxy[~valid]
    return arr


def self_bleu_3(payloads, max_samples=500):
    """Self-BLEU-3 on a subsample for speed."""
    try:
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    except ImportError:
        print("nltk not installed, skipping Self-BLEU")
        return float("nan")

    samples = payloads[:max_samples]
    tokenized = [p.split() for p in samples]
    smoother = SmoothingFunction().method1
    scores = []
    for i, hyp in enumerate(tokenized):
        refs = [t for j, t in enumerate(tokenized) if j != i]
        if not refs or not hyp:
            continue
        score = sentence_bleu(refs, hyp, weights=(1/3, 1/3, 1/3),
                              smoothing_function=smoother)
        scores.append(score)
    return float(np.mean(scores)) if scores else float("nan")


def bootstrap_ci(values, n_resamples=10000, confidence=0.95):
    arr = np.array(values)
    means = [arr[np.random.randint(0, len(arr), len(arr))].mean()
             for _ in range(n_resamples)]
    lo = np.percentile(means, (1 - confidence) / 2 * 100)
    hi = np.percentile(means, (1 + confidence) / 2 * 100)
    return float(arr.mean()), float(lo), float(hi)


# ── New metrics ───────────────────────────────────────────────────────────────

def relex_uniqueness(payloads):
    """Fraction of unique payloads after re-lexicalization placeholder removal."""
    normalized = set()
    for p in payloads:
        # Collapse whitespace to normalize minor variations
        norm = re.sub(r"\s+", " ", p.strip().lower())
        normalized.add(norm)
    return len(normalized) / max(len(payloads), 1)


def type_entropy(payloads, classifier_fn=None):
    """Shannon entropy (bits) of predicted attack type distribution.

    Higher entropy = more diverse attack types generated.
    Requires classifier_fn(payloads) -> list[str] of type labels.
    Falls back to token-heuristic if no classifier provided.
    """
    if classifier_fn is not None:
        labels = classifier_fn(payloads)
    else:
        # Simple heuristic classifier
        def _heuristic(p):
            pl = p.lower()
            if "sleep" in pl or "pg_sleep" in pl or "waitfor" in pl:
                return "time_blind"
            if "union" in pl and "select" in pl:
                return "union_based"
            if "or 1=1" in pl or "and 1=1" in pl:
                return "boolean_blind"
            if "extractvalue" in pl or "updatexml" in pl:
                return "error_based"
            if "xp_cmdshell" in pl or "exec" in pl:
                return "stacked_queries"
            return "other"
        labels = [_heuristic(p) for p in payloads]

    counts = {}
    for lbl in labels:
        counts[lbl] = counts.get(lbl, 0) + 1
    total = sum(counts.values())
    entropy = 0.0
    for c in counts.values():
        p = c / total
        if p > 0:
            entropy -= p * math.log2(p)
    return entropy


def novel_ngram_ratio(payloads, train_payloads, n=3):
    """Fraction of n-grams in generated payloads not seen in training set."""
    def get_ngrams(text, n):
        tokens = text.lower().split()
        return set(tuple(tokens[i:i+n]) for i in range(len(tokens) - n + 1))

    train_ngrams = set()
    for p in train_payloads:
        train_ngrams |= get_ngrams(p, n)

    if not train_ngrams:
        return float("nan")

    novel_count = 0
    total_count = 0
    for p in payloads:
        ngrams = get_ngrams(p, n)
        total_count += len(ngrams)
        novel_count += sum(1 for ng in ngrams if ng not in train_ngrams)

    return novel_count / max(total_count, 1)


def per_type_breakdown(payloads, bypass_arr, syntax_fn, classifier_fn=None):
    """Per attack-type breakdown: ASR, syntax rate, count."""
    if classifier_fn is not None:
        labels = classifier_fn(payloads)
    else:
        labels = ["unknown"] * len(payloads)

    syntax_flags = []
    for p in payloads:
        try:
            stmts = sqlparse.parse(p.strip())
            syntax_flags.append(1 if (stmts and stmts[0].tokens) else 0)
        except Exception:
            syntax_flags.append(0)

    type_stats = {}
    for i, (lbl, bypass, syn) in enumerate(zip(labels, bypass_arr, syntax_flags)):
        if lbl not in type_stats:
            type_stats[lbl] = {"count": 0, "bypass": [], "syntax": []}
        type_stats[lbl]["count"] += 1
        type_stats[lbl]["bypass"].append(float(bypass))
        type_stats[lbl]["syntax"].append(int(syn))

    breakdown = {}
    for lbl, stats in sorted(type_stats.items()):
        breakdown[lbl] = {
            "count": stats["count"],
            "asr": float(np.mean(stats["bypass"])) if stats["bypass"] else 0.0,
            "syntax": float(np.mean(stats["syntax"])) if stats["syntax"] else 0.0,
        }
    return breakdown


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, help="CSV with 'payload' column")
    parser.add_argument("--n_samples", type=int, default=1000)
    parser.add_argument("--waf_endpoint", default=None,
                        help="Real WAF REST URL (e.g. http://localhost:8080). "
                             "Omit to use dev proxy only.")
    parser.add_argument("--train_ref", default=None,
                        help="CSV with training payloads for novel n-gram computation")
    parser.add_argument("--out", default=None, help="JSON output for report")
    args = parser.parse_args()

    input_path = args.input if os.path.isabs(args.input) else os.path.join(ROOT, "..", args.input)
    df = pd.read_csv(input_path)
    payloads = df["payload"].fillna("").tolist()[:args.n_samples]
    N = len(payloads)
    print(f"Evaluating {N} samples from {input_path}")

    if N < 100:
        print(f"WARNING: N={N} < 100. Insufficient data for reliable evaluation.")

    # ── Syntax ────────────────────────────────────────────────────────────────
    syn_rate = syntax_validity(payloads)
    print(f"\nSyntax Validity:     {syn_rate:.1%}  ({'PASS' if syn_rate >= 0.9 else 'FAIL (< 90%)'})")
    if syn_rate < 0.9:
        print("  -> Fix Generator before reading ASR (invalid payloads can't attack WAF).")

    # ── ASR ───────────────────────────────────────────────────────────────────
    if args.waf_endpoint:
        print(f"\nUsing real WAF endpoint: {args.waf_endpoint}")
        bypass_arr = asr_real_waf(payloads, args.waf_endpoint)
        asr_label = "ASR (real WAF):"
    else:
        bypass_arr = asr_proxy(payloads)
        asr_label = "ASR (dev proxy):"

    asr_mean, asr_lo, asr_hi = bootstrap_ci(bypass_arr)
    print(f"{asr_label:<22}{asr_mean:.1%}  [CI: {asr_lo:.1%}–{asr_hi:.1%}, N={N}]")

    # ── Self-BLEU-3 ───────────────────────────────────────────────────────────
    print("Computing Self-BLEU-3 (may be slow)...")
    sb3 = self_bleu_3(payloads)
    if not np.isnan(sb3):
        flag = "PASS" if sb3 < 0.80 else ("WARN >= 0.80" if sb3 < 0.90 else "CRITICAL >= 0.90")
        print(f"Self-BLEU-3:         {sb3:.4f}  ({flag})")

    # ── Relex Uniqueness ──────────────────────────────────────────────────────
    rlx_uniq = relex_uniqueness(payloads)
    print(f"Relex Uniqueness:    {rlx_uniq:.3f}  ({'PASS' if rlx_uniq >= 0.80 else 'WARN < 0.80'})")

    # ── Type Entropy ──────────────────────────────────────────────────────────
    t_entropy = type_entropy(payloads)
    print(f"Type Entropy:        {t_entropy:.3f} bits  ({'PASS' if t_entropy >= 2.0 else 'WARN < 2.0'})")

    # ── Novel n-gram Ratio ────────────────────────────────────────────────────
    novel_ratio = float("nan")
    if args.train_ref:
        try:
            train_ref_path = (args.train_ref if os.path.isabs(args.train_ref)
                              else os.path.join(ROOT, "..", args.train_ref))
            train_df = pd.read_csv(train_ref_path)
            train_payloads = train_df["payload"].fillna("").tolist()
            novel_ratio = novel_ngram_ratio(payloads, train_payloads, n=3)
            print(f"Novel n-gram ratio:  {novel_ratio:.3f}  "
                  f"({'PASS' if novel_ratio >= 0.30 else 'WARN < 0.30'})")
        except Exception as e:
            print(f"Novel n-gram: skipped ({e})")
    else:
        print("Novel n-gram ratio:  skipped (no --train_ref provided)")

    # ── Length distribution ───────────────────────────────────────────────────
    lengths = [len(p.split()) for p in payloads]
    print(f"Length:  mean={np.mean(lengths):.1f}  std={np.std(lengths):.1f}  "
          f"min={min(lengths)}  max={max(lengths)}")

    trivial = sum(1 for p in payloads if len(p.split()) < 3 or p.strip() in {"--", ";", ""})
    trivial_rate = trivial / N
    print(f"Trivial seqs:        {trivial_rate:.1%}  ({'OK' if trivial_rate <= 0.01 else 'RF-5 TRIGGERED'})")

    # ── Per-type breakdown ────────────────────────────────────────────────────
    breakdown = per_type_breakdown(payloads, bypass_arr, syntax_validity)
    print("\nPer-type breakdown:")
    for lbl, stats in breakdown.items():
        print(f"  {lbl:<22} count={stats['count']:4d}  ASR={stats['asr']:.1%}  "
              f"syntax={stats['syntax']:.1%}")

    # ── Aggregate results ─────────────────────────────────────────────────────
    results = {
        "n_samples": N,
        "syntax_rate": syn_rate,
        "asr_mean": asr_mean,
        "asr_ci_low": asr_lo,
        "asr_ci_high": asr_hi,
        "asr_source": "real_waf" if args.waf_endpoint else "dev_proxy",
        "self_bleu_3": sb3,
        "relex_uniqueness": rlx_uniq,
        "type_entropy_bits": t_entropy,
        "novel_ngram_ratio": novel_ratio,
        "length_mean": float(np.mean(lengths)),
        "length_std": float(np.std(lengths)),
        "trivial_rate": trivial_rate,
        "per_type_breakdown": breakdown,
    }

    if args.out:
        with open(args.out, "w") as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.out}")

    return results


if __name__ == "__main__":
    main()
