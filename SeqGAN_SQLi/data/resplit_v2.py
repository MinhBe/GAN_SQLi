"""
resplit_v2.py — Stratified split by (sqli_type, source).
Output: data/v2/{train,val,test}.csv
"""
import argparse
from pathlib import Path

import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit


def resplit(csv_path: str, out_dir: str, seed: int = 42):
    df = pd.read_csv(csv_path)
    out_dir_p = Path(out_dir)
    out_dir_p.mkdir(parents=True, exist_ok=True)

    type_col = next((c for c in ["sqli_type", "type", "label"] if c in df.columns), None)
    if type_col is None:
        df["sqli_type"] = "unknown"
        type_col = "sqli_type"

    if "source" not in df.columns:
        df["source"] = "original"

    # Compound stratification
    df["_strat"] = df[type_col].astype(str) + "|" + df["source"].astype(str)

    # Filter rare combinations (< 2 samples)
    strat_counts = df["_strat"].value_counts()
    valid_strat = strat_counts[strat_counts >= 2].index
    df_strat = df[df["_strat"].isin(valid_strat)].copy()
    df_rare = df[~df["_strat"].isin(valid_strat)].copy()
    print(f"Stratifiable rows: {len(df_strat)} / Rare: {len(df_rare)} (put in train)")

    # First split: 70% train, 30% temp
    sss1 = StratifiedShuffleSplit(n_splits=1, test_size=0.30, random_state=seed)
    train_idx, temp_idx = next(sss1.split(df_strat, df_strat["_strat"]))
    df_train = df_strat.iloc[train_idx].copy()
    df_temp = df_strat.iloc[temp_idx].copy()

    # Second split: 50% val, 50% test of temp = 15% each total
    # Handle rare classes in temp (< 2 members) — put them in val
    temp_strat_counts = df_temp["_strat"].value_counts()
    valid_temp_strat = temp_strat_counts[temp_strat_counts >= 2].index
    df_temp_strat = df_temp[df_temp["_strat"].isin(valid_temp_strat)].copy()
    df_temp_rare = df_temp[~df_temp["_strat"].isin(valid_temp_strat)].copy()
    print(f"Temp stratifiable: {len(df_temp_strat)} / Rare: {len(df_temp_rare)} (put in val)")

    sss2 = StratifiedShuffleSplit(n_splits=1, test_size=0.50, random_state=seed)
    val_idx, test_idx = next(sss2.split(df_temp_strat, df_temp_strat["_strat"]))
    df_val = pd.concat([df_temp_strat.iloc[val_idx], df_temp_rare], ignore_index=True)
    df_test = df_temp_strat.iloc[test_idx].copy()

    # Add rare samples to train
    df_train = pd.concat([df_train, df_rare], ignore_index=True)

    # Drop helper column
    for d in [df_train, df_val, df_test]:
        d.drop(columns=["_strat"], inplace=True, errors="ignore")

    df_train.to_csv(out_dir_p / "train.csv", index=False)
    df_val.to_csv(out_dir_p / "val.csv", index=False)
    df_test.to_csv(out_dir_p / "test.csv", index=False)

    print(f"Train: {len(df_train)}")
    print(f"Val:   {len(df_val)}")
    print(f"Test:  {len(df_test)}")

    # Write stratify report
    report_lines = [
        f"Split: train={len(df_train)} val={len(df_val)} test={len(df_test)}",
        f"\nPer-type distribution:",
    ]
    for split_name, split_df in [("train", df_train), ("val", df_val), ("test", df_test)]:
        report_lines.append(f"\n  {split_name}:")
        for t, c in split_df[type_col].value_counts().items():
            report_lines.append(f"    {t}: {c}")

    (out_dir_p / "stratify_report.txt").write_text("\n".join(report_lines), encoding="utf-8")
    print(f"Stratify report: {out_dir_p / 'stratify_report.txt'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True)
    parser.add_argument("--out_dir", required=True)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    resplit(args.csv, args.out_dir, args.seed)
