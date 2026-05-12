"""compare_results.py — Tổng hợp eval results thành bảng so sánh."""
import argparse
import json
from pathlib import Path

import pandas as pd


def compare(results_dir: str, out_csv: str, out_md: str):
    results_p = Path(results_dir)
    json_files = sorted(results_p.glob("*.json"))

    if not json_files:
        print(f"No JSON files found in {results_dir}")
        return

    rows = []
    for json_file in json_files:
        with open(json_file, encoding="utf-8") as f:
            r = json.load(f)
        m = r.get("metrics", {})
        rows.append({
            "model": json_file.stem,
            "n_samples": r.get("n_samples", 0),
            "owasp_bypass": round(m.get("owasp_bypass_rate", {}).get("mean", 0), 4),
            "owasp_ci": (
                f"[{m['owasp_bypass_rate']['ci_lo']:.3f},"
                f"{m['owasp_bypass_rate']['ci_hi']:.3f}]"
                if "owasp_bypass_rate" in m else "-"
            ),
            "db_execution": round(m.get("db_execution_rate", {}).get("mean", 0), 4),
            "ast_entropy": round(m.get("ast_diversity_entropy", {}).get("value", 0), 4),
            "ml_ids_evasion": round(m.get("ml_ids_evasion_rate", {}).get("mean", 0), 4),
            "relex_uniqueness": round(m.get("relex_uniqueness", {}).get("value", 0), 4),
            "composite": round(r.get("composite_score", 0), 4),
            "syntax_pass": round(r.get("quality", {}).get("syntax_pass_rate", 0), 4),
            "custom_pass": round(r.get("quality", {}).get("custom_rule_pass_mean", 0), 4),
        })

    df = pd.DataFrame(rows).sort_values("composite", ascending=False)
    df.to_csv(out_csv, index=False)

    # V2 vs V1 delta
    v2 = df[df["model"].str.contains("v2_refined", na=False)]
    v1 = df[df["model"].str.contains("v1_seqgan", na=False)]

    md_lines = ["# V2 Evaluation Comparison\n"]
    try:
        md_lines.append(df.to_markdown(index=False))
    except Exception:
        md_lines.append(df.to_string(index=False))

    if not v2.empty and not v1.empty:
        delta = v2["composite"].values[0] - v1["composite"].values[0]
        md_lines.append(f"\n## V2 vs V1 Delta\n")
        md_lines.append(f"Composite delta: {delta:+.4f}")
        if delta > 0.1:
            verdict = "V2 clearly better"
        elif delta > 0:
            verdict = "V2 marginally better — run ablations"
        else:
            verdict = "V2 did not improve — postmortem needed"
        md_lines.append(f"\nVerdict: **{verdict}**")

    Path(out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(out_md).write_text("\n".join(md_lines), encoding="utf-8")

    print(df.to_string(index=False))
    print(f"\nSaved: {out_csv}")
    print(f"Saved: {out_md}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--results_dir", default="SeqGAN_SQLi/eval/results")
    parser.add_argument("--out_csv", default="SeqGAN_SQLi/eval/comparison.csv")
    parser.add_argument("--out_md", default="SeqGAN_SQLi/eval/comparison.md")
    args = parser.parse_args()
    compare(args.results_dir, args.out_csv, args.out_md)


if __name__ == "__main__":
    main()
