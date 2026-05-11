"""
tier_filter.py — Assign tier confidence: gold/silver/bronze.
"""
import argparse
from pathlib import Path

import pandas as pd


def tier_dataset(csv_path: str, out_path: str):
    df = pd.read_csv(csv_path)

    if "confidence" not in df.columns:
        print("WARNING: No 'confidence' column - assign default 0.85 (silver)")
        df["confidence"] = 0.85

    df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0.5)

    def tier(c):
        if c >= 0.95:
            return "gold"
        elif c >= 0.80:
            return "silver"
        else:
            return "bronze"

    df["tier"] = df["confidence"].apply(tier)

    counts = df["tier"].value_counts().to_dict()
    print(f"Tier distribution:")
    for t in ["gold", "silver", "bronze"]:
        c = counts.get(t, 0)
        print(f"  {t}: {c} ({c/len(df)*100:.1f}%)")

    df.to_csv(out_path, index=False)
    print(f"Saved: {out_path}")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out", required=True)
    args = parser.parse_args()
    tier_dataset(args.csv, args.out)
