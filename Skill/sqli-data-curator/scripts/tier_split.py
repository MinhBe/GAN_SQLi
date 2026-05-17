"""tier_split.py — Chia dataset thành Gold / Silver / Bronze theo confidence + sources_agree.

Tier definition:
  - gold:   confidence >= 0.90 AND sources_agree == 3   → MLE pretrain + RL real
  - silver: confidence >= 0.70 AND sources_agree >= 2   → RL augment
  - bronze: rest (low conf hoặc sources_agree <= 1)     → D-only negative

Output: gold.csv, silver.csv, bronze.csv trong output_dir.
"""
import argparse
import os

import pandas as pd


def assign_tier(row: dict) -> str:
    try:
        conf = float(row.get("confidence", 0.0))
    except (TypeError, ValueError):
        conf = 0.0
    try:
        agree = int(row.get("sources_agree", 0))
    except (TypeError, ValueError):
        agree = 0

    if conf >= 0.90 and agree == 3:
        return "gold"
    if conf >= 0.70 and agree >= 2:
        return "silver"
    return "bronze"


def split_and_save(df: pd.DataFrame, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    df = df.copy()
    df["tier"] = df.apply(lambda r: assign_tier(r.to_dict()), axis=1)

    counts = df["tier"].value_counts()
    print(f"\n=== TIER DISTRIBUTION ===")
    for tier in ("gold", "silver", "bronze"):
        c = int(counts.get(tier, 0))
        print(f"  {tier:<8} {c:6d} ({c/len(df):6.2%})")

    for tier in ("gold", "silver", "bronze"):
        subset = df[df["tier"] == tier].copy()
        out_path = os.path.join(output_dir, f"{tier}.csv")
        subset.to_csv(out_path, index=False)
        print(f"  Wrote {len(subset)} rows -> {out_path}")

    # Quality report on gold (most important tier)
    gold = df[df["tier"] == "gold"]
    if len(gold) > 0:
        print(f"\n=== GOLD QUALITY ===")
        print(f"Type distribution (top 10):")
        for t, c in gold["sqli_type"].value_counts().head(10).items():
            print(f"  {c:6d} ({c/len(gold):6.2%})  {t}")
        if "signature" in gold.columns:
            n_sig = gold["signature"].nunique()
            print(f"Unique signatures: {n_sig} (mean {len(gold)/n_sig:.2f} rows/sig)")


def main():
    parser = argparse.ArgumentParser(description="Tier split Gold/Silver/Bronze")
    parser.add_argument("--input", required=True, help="Input CSV (must have confidence, sources_agree)")
    parser.add_argument("--output_dir", required=True, help="Output dir for gold/silver/bronze.csv")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    if "confidence" not in df.columns or "sources_agree" not in df.columns:
        raise SystemExit("ERROR: input must have 'confidence' and 'sources_agree' columns")

    split_and_save(df, args.output_dir)


if __name__ == "__main__":
    main()
