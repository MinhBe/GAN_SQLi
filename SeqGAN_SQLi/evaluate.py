"""Sprint 5: Evaluation — ASR (dev proxy), Syntax, Self-BLEU-3."""
import os
import sys
import argparse
import json
import numpy as np
import pandas as pd
import sqlparse

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from src.reward import RewardOracle


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


def self_bleu_3(payloads, max_samples=500):
    """Self-BLEU-3 on a subsample for speed."""
    try:
        from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
    except ImportError:
        print("nltk not installed, skipping Self-BLEU")
        return float('nan')

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
    return float(np.mean(scores)) if scores else float('nan')


def bootstrap_ci(values, n_resamples=10000, confidence=0.95):
    arr = np.array(values)
    means = [arr[np.random.randint(0, len(arr), len(arr))].mean()
             for _ in range(n_resamples)]
    lo = np.percentile(means, (1 - confidence) / 2 * 100)
    hi = np.percentile(means, (1 + confidence) / 2 * 100)
    return float(arr.mean()), float(lo), float(hi)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='CSV with "payload" column')
    parser.add_argument('--n_samples', type=int, default=1000)
    parser.add_argument('--out', default=None, help='JSON output for report')
    args = parser.parse_args()

    input_path = args.input if os.path.isabs(args.input) else os.path.join(ROOT, '..', args.input)
    df = pd.read_csv(input_path)
    payloads = df['payload'].fillna('').tolist()[:args.n_samples]
    N = len(payloads)
    print(f"Evaluating {N} samples from {input_path}")

    if N < 100:
        print(f"WARNING: N={N} < 100. Insufficient data for reliable evaluation.")

    # Syntax
    syn_rate = syntax_validity(payloads)
    print(f"\nSyntax Validity: {syn_rate:.1%}  ({'PASS' if syn_rate >= 0.9 else 'FAIL (< 90%)'})")
    if syn_rate < 0.9:
        print("  -> Fix Generator before reading ASR (invalid payloads can't attack WAF).")

    # ASR
    bypass_arr = asr_proxy(payloads)
    asr_mean, asr_lo, asr_hi = bootstrap_ci(bypass_arr)
    print(f"ASR (dev proxy):  {asr_mean:.1%}  [CI: {asr_lo:.1%}–{asr_hi:.1%}, N={N}]")

    # Self-BLEU-3
    print("Computing Self-BLEU-3 (may be slow)...")
    sb3 = self_bleu_3(payloads)
    if not np.isnan(sb3):
        print(f"Self-BLEU-3:      {sb3:.4f}  ({'PASS' if sb3 < 0.6 else 'WARN >= 0.6'})")

    # Length distribution
    lengths = [len(p.split()) for p in payloads]
    print(f"Length:  mean={np.mean(lengths):.1f}  std={np.std(lengths):.1f}  "
          f"min={min(lengths)}  max={max(lengths)}")

    trivial = sum(1 for p in payloads if len(p.split()) < 3 or p.strip() in {'--', ';', ''})
    trivial_rate = trivial / N
    print(f"Trivial seqs:     {trivial_rate:.1%}  ({'OK' if trivial_rate <= 0.01 else 'RF-5 TRIGGERED'})")

    results = {
        'n_samples': N,
        'syntax_rate': syn_rate,
        'asr_mean': asr_mean,
        'asr_ci_low': asr_lo,
        'asr_ci_high': asr_hi,
        'self_bleu_3': sb3,
        'length_mean': float(np.mean(lengths)),
        'length_std': float(np.std(lengths)),
        'trivial_rate': trivial_rate,
    }

    if args.out:
        with open(args.out, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to {args.out}")

    return results


if __name__ == '__main__':
    main()
