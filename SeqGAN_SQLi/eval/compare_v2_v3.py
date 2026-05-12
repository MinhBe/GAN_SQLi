"""compare_v2_v3.py — So sánh V2 vs V3 trên các metrics chính."""
import json
from pathlib import Path
import sys

V2_RESULTS = Path("SeqGAN_SQLi/eval/results")
V3_RESULTS = Path("SeqGAN_SQLi/eval/results_v3")

KEY_MODELS = {
    "v2_mle":        ("V2 MLE baseline",       V2_RESULTS / "v2_mle.json"),
    "v2_step1000":   ("V2 step1000 (best V2)", V2_RESULTS / "v2_step1000.json"),
    "v2_refined":    ("V2 final (refined)",    V2_RESULTS / "v2_refined.json"),
    "v3_adv_step1000":  ("V3 step1000",           V3_RESULTS / "v3_adv_step1000.json"),
    "v3_adv_step2000":  ("V3 step2000",           V3_RESULTS / "v3_adv_step2000.json"),
    "v3_adv_step12000": ("V3 step12000",          V3_RESULTS / "v3_adv_step12000.json"),
    "v3_adv_final":     ("V3 final",              V3_RESULTS / "v3_adv_final.json"),
}

HEADER = f"{'Model':<26} {'DB%':>6} {'AST-H':>7} {'IDS%':>6} {'Uniq':>6} {'Comp':>7} {'SynPas':>7} {'CustPas':>8}"
SEP = "-" * 80


def load(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return None


def main():
    print("\n" + "=" * 80)
    print("  V2 vs V3 Comparison — key checkpoints (no WAF)")
    print("=" * 80)
    print(HEADER)
    print(SEP)

    rows = []
    for key, (label, path) in KEY_MODELS.items():
        d = load(path)
        if d is None:
            print(f"  {label:<24}  [not found: {path}]")
            continue
        m = d.get("metrics", {})
        row = {
            "label": label,
            "db":    m.get("db_execution_rate", {}).get("mean", 0),
            "ast":   m.get("ast_diversity_entropy", {}).get("value", 0),
            "ids":   m.get("ml_ids_evasion_rate", {}).get("mean", 0),
            "uniq":  m.get("relex_uniqueness", {}).get("value", 0),
            "comp":  d.get("composite_score", 0),
            "syn":   d.get("quality", {}).get("syntax_pass_rate", 0),
            "cust":  d.get("quality", {}).get("custom_rule_pass_mean", 0),
        }
        rows.append(row)
        print(
            f"  {label:<24} {row['db']:>6.1%} {row['ast']:>7.3f} {row['ids']:>6.1%}"
            f" {row['uniq']:>6.3f} {row['comp']:>7.4f} {row['syn']:>7.1%} {row['cust']:>8.1%}"
        )

    print(SEP)

    # Delta: V3 final vs V2 step1000 (best V2)
    v2_best = next((r for r in rows if "V2 step1000" in r["label"]), None)
    v3_final = next((r for r in rows if "V3 final" in r["label"]), None)
    if v2_best and v3_final:
        print(f"\n  V3 final vs V2 best (step1000):")
        delta_comp = v3_final["comp"] - v2_best["comp"]
        delta_uniq = v3_final["uniq"] - v2_best["uniq"]
        delta_db   = v3_final["db"]   - v2_best["db"]
        print(f"    composite:       {delta_comp:+.4f}")
        print(f"    relex_unique:    {delta_uniq:+.4f}")
        print(f"    db_execution:    {delta_db:+.1%}")
        verdict = "V3 BETTER" if delta_comp > 0.02 else "V3 MARGINAL" if delta_comp > 0 else "V3 DID NOT IMPROVE"
        print(f"    Verdict: {verdict}")

    print()


if __name__ == "__main__":
    main()
