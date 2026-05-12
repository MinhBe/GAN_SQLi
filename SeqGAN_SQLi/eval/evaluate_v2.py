"""
evaluate_v2.py — 5-metric evaluation cho generated payloads V2.

Metrics:
  1. OWASP bypass rate (w=0.30) — requires WAF Docker
  2. DB execution rate  (w=0.25)
  3. AST diversity entropy (w=0.20)
  4. ML-IDS evasion rate (w=0.15) — requires trained IDS classifier
  5. Re-lex uniqueness (w=0.10)

Composite score = weighted sum.
Bootstrap CI (n=10k) for metrics 1, 2, 4.
"""
import argparse
import json
import math
import random
import re
import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd
import yaml

sys.path.insert(0, str(Path(__file__).parent.parent))

from src.ast_tracker import ASTFingerprintTracker
from src.custom_rules import CustomRuleEngine
from src.db_sandbox import DBSandbox
from src.parser_gate import SQLParserGate


# ─── Bootstrap CI ─────────────────────────────────────────────────────────────

def bootstrap_ci(values, n_resamples=10000, ci=0.95):
    arr = np.array(values, dtype=float)
    means = np.array([
        np.mean(np.random.choice(arr, size=len(arr), replace=True))
        for _ in range(n_resamples)
    ])
    lo = np.percentile(means, (1 - ci) / 2 * 100)
    hi = np.percentile(means, (1 + ci) / 2 * 100)
    return float(np.mean(arr)), float(lo), float(hi)


# ─── Re-lex ───────────────────────────────────────────────────────────────────

def relex(payload: str, relex_dict: dict, seed: int = None) -> str:
    if seed is not None:
        random.seed(seed)

    def replace(match):
        key = match.group(0)
        choices = relex_dict.get(key)
        return random.choice(choices) if choices else key

    return re.sub(r"__\w+__", replace, payload)


# ─── Metric functions ─────────────────────────────────────────────────────────

def compute_owasp_bypass(payloads: list, waf_url: str) -> list:
    """Requires WAF Docker running. Returns list of 0/1."""
    try:
        from src.waf_oracle import WAFOracle
        waf = WAFOracle(url=waf_url, timeout=3.0)
        results = []
        for p in payloads:
            try:
                r = waf.evaluate(p)
                results.append(0 if r["blocked"] else 1)
            except Exception:
                results.append(0)
        waf.close()
        return results
    except Exception as e:
        print(f"  WAF unavailable ({e}) — skipping OWASP metric (score=0)")
        return [0] * len(payloads)


def compute_db_execution(payloads: list, db: DBSandbox) -> list:
    return [db.evaluate(p) for p in payloads]


def compute_ast_diversity_entropy(payloads: list, tracker: ASTFingerprintTracker) -> float:
    all_fps = []
    for p in payloads:
        fp = tracker.fingerprint(p)
        all_fps.extend(fp)
    if not all_fps:
        return 0.0
    counts = Counter(all_fps)
    total = sum(counts.values())
    entropy = -sum((c / total) * math.log(c / total) for c in counts.values())
    return entropy


def compute_ml_ids_evasion(payloads: list, ids_dir: str) -> list:
    """Returns 1 if IDS fails to detect (evasion success), 0 if caught."""
    ids_p = Path(ids_dir)
    if not (ids_p / "ids_xgb.pkl").exists():
        print(f"  IDS classifier not found at {ids_dir} — skipping (score=0)")
        return [0] * len(payloads)
    try:
        import joblib
        clf = joblib.load(ids_p / "ids_xgb.pkl")
        vec = joblib.load(ids_p / "ids_vectorizer.pkl")
        X = vec.transform(payloads)
        proba = clf.predict_proba(X)[:, 1]  # P(attack)
        return (proba < 0.5).astype(int).tolist()
    except Exception as e:
        print(f"  IDS eval failed ({e}) — skipping (score=0)")
        return [0] * len(payloads)


def compute_relex_uniqueness(payloads: list, relex_dict: dict, n_per: int = 3) -> float:
    relexed = []
    for p in payloads:
        for s in range(n_per):
            relexed.append(relex(p, relex_dict, seed=s))
    return len(set(relexed)) / max(len(relexed), 1)


# ─── Main evaluate ────────────────────────────────────────────────────────────

def evaluate(samples_csv: str, out_json: str, config_path: str,
             ids_dir: str, use_waf: bool = True):
    with open(config_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    relex_dict_path = cfg.get("relex_dict_path", "SeqGAN_SQLi/data/relex_dictionary.json")
    with open(relex_dict_path, encoding="utf-8") as f:
        relex_dict = json.load(f)

    df = pd.read_csv(samples_csv)
    payload_col = next(
        (c for c in ["payload_delex", "payload", "payload_norm"] if c in df.columns),
        df.columns[0],
    )
    raw_payloads = df[payload_col].fillna("").astype(str).tolist()

    # Re-lex de-lexed payloads for actual SQL scoring
    payloads = [relex(p, relex_dict) for p in raw_payloads]
    print(f"\nEvaluating {len(payloads)} payloads from {samples_csv}")
    print(f"Sample (re-lexed): {payloads[0][:80]}")

    db = DBSandbox()
    parser = SQLParserGate()
    custom = CustomRuleEngine()
    tracker = ASTFingerprintTracker()

    # Metric 1: OWASP bypass
    print("\n[1/5] OWASP bypass rate...")
    if use_waf:
        owasp_vals = compute_owasp_bypass(payloads, cfg.get("waf_url", "http://localhost:8080"))
    else:
        owasp_vals = [0] * len(payloads)
        print("  Skipped (--no_waf)")
    m1, m1_lo, m1_hi = bootstrap_ci(owasp_vals)
    print(f"  {m1:.4f} [{m1_lo:.4f}, {m1_hi:.4f}]")

    # Metric 2: DB execution
    print("[2/5] DB execution rate...")
    db_vals = compute_db_execution(payloads, db)
    m2, m2_lo, m2_hi = bootstrap_ci(db_vals)
    print(f"  {m2:.4f} [{m2_lo:.4f}, {m2_hi:.4f}]")

    # Metric 3: AST diversity entropy
    print("[3/5] AST diversity entropy...")
    ast_entropy = compute_ast_diversity_entropy(payloads, tracker)
    ast_normalized = min(ast_entropy / 5.0, 1.0)
    print(f"  entropy={ast_entropy:.4f} (normalized={ast_normalized:.4f})")
    print(f"  AST stats: {tracker.get_stats()}")

    # Metric 4: ML-IDS evasion
    print("[4/5] ML-IDS evasion rate...")
    ids_vals = compute_ml_ids_evasion(payloads, ids_dir)
    m4, m4_lo, m4_hi = bootstrap_ci(ids_vals)
    print(f"  {m4:.4f} [{m4_lo:.4f}, {m4_hi:.4f}]")

    # Metric 5: Re-lex uniqueness
    print("[5/5] Re-lex uniqueness...")
    relex_uniq = compute_relex_uniqueness(raw_payloads, relex_dict)
    print(f"  {relex_uniq:.4f}")

    # Composite score
    composite = (
        0.30 * m1
        + 0.25 * m2
        + 0.20 * ast_normalized
        + 0.15 * m4
        + 0.10 * relex_uniq
    )

    # Quality stats
    syntax_vals = [parser.evaluate(p) for p in payloads]
    custom_vals = [custom.score(p) for p in payloads]

    report = {
        "samples_file": str(samples_csv),
        "n_samples": len(payloads),
        "metrics": {
            "owasp_bypass_rate": {
                "mean": m1, "ci_lo": m1_lo, "ci_hi": m1_hi, "weight": 0.30,
                "note": "0.0 if WAF not available",
            },
            "db_execution_rate": {
                "mean": m2, "ci_lo": m2_lo, "ci_hi": m2_hi, "weight": 0.25,
            },
            "ast_diversity_entropy": {
                "value": ast_entropy, "normalized": ast_normalized, "weight": 0.20,
            },
            "ml_ids_evasion_rate": {
                "mean": m4, "ci_lo": m4_lo, "ci_hi": m4_hi, "weight": 0.15,
                "note": "0.0 if IDS not trained",
            },
            "relex_uniqueness": {"value": relex_uniq, "weight": 0.10},
        },
        "composite_score": composite,
        "quality": {
            "syntax_pass_rate": float(np.mean(syntax_vals)),
            "custom_rule_pass_mean": float(np.mean(custom_vals)),
        },
        "ast_stats": tracker.get_stats(),
    }

    Path(out_json).parent.mkdir(parents=True, exist_ok=True)
    with open(out_json, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print(f"\n=== Composite Score: {composite:.4f} ===")
    print(f"  OWASP bypass:  {m1:.4f}")
    print(f"  DB execution:  {m2:.4f}")
    print(f"  AST diversity: {ast_entropy:.4f}")
    print(f"  ML-IDS evasion:{m4:.4f}")
    print(f"  Re-lex unique: {relex_uniq:.4f}")
    print(f"\nSaved: {out_json}")

    db.close()
    return report


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--samples_csv", required=True)
    parser.add_argument("--out_json", required=True)
    parser.add_argument("--config", default="SeqGAN_SQLi/configs/seqgan_v2.yaml")
    parser.add_argument("--ids_dir", default="SeqGAN_SQLi/eval/ids_classifier")
    parser.add_argument("--no_waf", action="store_true", help="Skip WAF evaluation")
    args = parser.parse_args()

    cfg_path = args.config
    if not Path(cfg_path).exists():
        cfg_path = str(Path(__file__).parent.parent / args.config)

    evaluate(args.samples_csv, args.out_json, cfg_path, args.ids_dir,
             use_waf=not args.no_waf)


if __name__ == "__main__":
    main()
