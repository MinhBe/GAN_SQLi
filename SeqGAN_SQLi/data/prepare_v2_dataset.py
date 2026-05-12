"""
prepare_v2_dataset.py — Chuẩn bị dataset V2 từ latest_relabel_data.csv.

Bước:
1. Load SQLi data từ latest_relabel_data.csv
2. Thêm source column = 'manual'
3. Tiered confidence (gold/silver/bronze)
4. Stratified split train/val/test (70/15/15)
5. Lưu vào data/v2/{train,val,test}.csv + stratify_report.txt

Không dùng combined_labeled_data.csv ở đây — dùng riêng cho IDS eval.
"""
import argparse
from pathlib import Path

import pandas as pd
from sklearn.model_selection import StratifiedShuffleSplit


SQLI_TYPES_V2 = ["error_based", "boolean_blind", "time_blind", "union_based"]
TYPE_TO_ID = {t: i for i, t in enumerate(SQLI_TYPES_V2)}


def tier(c: float) -> str:
    if c >= 0.95:
        return "gold"
    elif c >= 0.80:
        return "silver"
    return "bronze"


def prepare(csv_path: str, out_dir: str, seed: int = 42):
    out_dir_p = Path(out_dir)
    out_dir_p.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} rows from {csv_path}")
    print(f"Columns: {list(df.columns)}")

    # Normalize columns
    if "payload_delex" not in df.columns:
        raise ValueError("Expected 'payload_delex' column for de-lexed payloads")
    if "sqli_type" not in df.columns:
        raise ValueError("Expected 'sqli_type' column")

    # Filter to known 4 types only
    before = len(df)
    df = df[df["sqli_type"].isin(SQLI_TYPES_V2)].copy()
    print(f"Filtered to 4 known types: {before} -> {len(df)} rows")

    # Add source column
    if "source" not in df.columns:
        df["source"] = "manual"

    # Add tier
    if "confidence" not in df.columns:
        df["confidence"] = 0.85
    df["confidence"] = pd.to_numeric(df["confidence"], errors="coerce").fillna(0.5)
    df["tier"] = df["confidence"].apply(tier)

    # Add type_id for model
    df["type_id"] = df["sqli_type"].map(TYPE_TO_ID)

    print("\nTier distribution:")
    for t in ["gold", "silver", "bronze"]:
        c = (df["tier"] == t).sum()
        print(f"  {t}: {c} ({c/len(df)*100:.1f}%)")

    print("\nType distribution:")
    for t, c in df["sqli_type"].value_counts().items():
        print(f"  {t}: {c}")

    # Stratified split by sqli_type (no source column variation since all=manual)
    df["_strat"] = df["sqli_type"].astype(str)
    strat_counts = df["_strat"].value_counts()
    valid_strat = strat_counts[strat_counts >= 2].index
    df_strat = df[df["_strat"].isin(valid_strat)].copy()
    df_rare = df[~df["_strat"].isin(valid_strat)].copy()

    sss1 = StratifiedShuffleSplit(n_splits=1, test_size=0.30, random_state=seed)
    train_idx, temp_idx = next(sss1.split(df_strat, df_strat["_strat"]))
    df_train = df_strat.iloc[train_idx].copy()
    df_temp = df_strat.iloc[temp_idx].copy()

    sss2 = StratifiedShuffleSplit(n_splits=1, test_size=0.50, random_state=seed)
    val_idx, test_idx = next(sss2.split(df_temp, df_temp["_strat"]))
    df_val = df_temp.iloc[val_idx].copy()
    df_test = df_temp.iloc[test_idx].copy()

    if len(df_rare) > 0:
        df_train = pd.concat([df_train, df_rare], ignore_index=True)

    for d in [df_train, df_val, df_test]:
        d.drop(columns=["_strat"], inplace=True, errors="ignore")

    # Save only gold+silver for training (bronze stays in train for reference)
    # But mark them — training loop will filter by tier
    df_train.to_csv(out_dir_p / "train.csv", index=False)
    df_val.to_csv(out_dir_p / "val.csv", index=False)
    df_test.to_csv(out_dir_p / "test.csv", index=False)

    print(f"\nTrain: {len(df_train)}")
    print(f"Val:   {len(df_val)}")
    print(f"Test:  {len(df_test)}")

    # Stratify report
    lines = [
        f"Dataset prepared: {csv_path}",
        f"Total: {len(df)}  Train: {len(df_train)}  Val: {len(df_val)}  Test: {len(df_test)}",
        f"\nType mapping: {TYPE_TO_ID}",
        "\nPer-type distribution:",
    ]
    for split_name, split_df in [("train", df_train), ("val", df_val), ("test", df_test)]:
        lines.append(f"\n  {split_name}:")
        for t, c in split_df["sqli_type"].value_counts().items():
            lines.append(f"    {t}: {c} ({c/len(split_df)*100:.1f}%)")

    (out_dir_p / "stratify_report.txt").write_text("\n".join(lines), encoding="utf-8")
    print(f"Stratify report: {out_dir_p / 'stratify_report.txt'}")

    # Save type mapping
    import json
    with open(out_dir_p / "type_mapping.json", "w") as f:
        json.dump({"type_to_id": TYPE_TO_ID, "id_to_type": {v: k for k, v in TYPE_TO_ID.items()}}, f, indent=2)
    print(f"Type mapping: {out_dir_p / 'type_mapping.json'}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", default=r"C:\Projects\GAN_SQLi\Asset\LabelData\latest_relabel_data.csv")
    parser.add_argument("--out_dir", default="SeqGAN_SQLi/data/v2")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    prepare(args.csv, args.out_dir, args.seed)
