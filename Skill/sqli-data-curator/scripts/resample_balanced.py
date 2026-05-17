"""resample_balanced.py — Cap per-signature & per-(type,db) để chống bias dominance.

Input CSV phải có column payload_delex_v2 (đã chạy delex_v2.py trước).

Logic:
  1. Compute signature = SHA1(payload_delex_v2)[:8] (nếu chưa có)
  2. Cap mỗi signature ≤ cap_signature rows (default 30) — chống pattern dominance
  3. Cap mỗi (sqli_type, db_engine) ≤ cap_type_db rows (default 300) — chống type bias

Mục tiêu: từ ~40,000 rows → ~12,000-15,000 rows balanced.
"""
import argparse
import hashlib

import pandas as pd
import numpy as np


def compute_signatures(df: pd.DataFrame, col: str = "payload_delex_v2") -> pd.DataFrame:
    """Add 'signature' column from SHA1 hash."""
    if "signature" in df.columns and df["signature"].notna().all():
        return df  # already computed
    if col not in df.columns:
        raise ValueError(f"Column '{col}' missing — run delex_v2.py first")
    df = df.copy()
    df["signature"] = df[col].fillna("").astype(str).map(
        lambda x: hashlib.sha1(x.encode("utf-8")).hexdigest()[:8]
    )
    return df


def cap_per_signature(df: pd.DataFrame, cap: int, seed: int = 42) -> pd.DataFrame:
    """For each signature with >cap rows, randomly sample down to cap."""
    rng = np.random.RandomState(seed)
    out_parts = []
    for sig, group in df.groupby("signature"):
        if len(group) <= cap:
            out_parts.append(group)
        else:
            sampled = group.sample(n=cap, random_state=rng.randint(0, 2**31 - 1))
            out_parts.append(sampled)
    return pd.concat(out_parts, ignore_index=True)


def cap_per_type_db(df: pd.DataFrame, cap: int, seed: int = 42) -> pd.DataFrame:
    """For each (sqli_type, db_engine) with >cap rows, sample down to cap."""
    rng = np.random.RandomState(seed)
    out_parts = []
    if "sqli_type" not in df.columns or "db_engine" not in df.columns:
        print("WARN: sqli_type/db_engine missing — skipping type-db cap")
        return df
    for (t, d), group in df.groupby(["sqli_type", "db_engine"]):
        if len(group) <= cap:
            out_parts.append(group)
        else:
            sampled = group.sample(n=cap, random_state=rng.randint(0, 2**31 - 1))
            out_parts.append(sampled)
    return pd.concat(out_parts, ignore_index=True)


def report_stats(label: str, df: pd.DataFrame):
    print(f"\n=== {label} ===")
    print(f"Total rows: {len(df)}")
    if "signature" in df.columns:
        n_sig = df["signature"].nunique()
        print(f"Unique signatures: {n_sig} (mean {len(df)/n_sig:.2f} rows/sig)")
        top = df["signature"].value_counts().head(5)
        print(f"Top 5 signatures:")
        for sig, cnt in top.items():
            print(f"  {sig:>9}  {cnt:5d}")
    if "sqli_type" in df.columns:
        print(f"Type distribution:")
        for t, c in df["sqli_type"].value_counts().items():
            print(f"  {c:6d} ({c/len(df):6.2%})  {t}")


def main():
    parser = argparse.ArgumentParser(description="Resample balanced dataset")
    parser.add_argument("--input", required=True, help="Input CSV")
    parser.add_argument("--output", required=True, help="Output CSV (balanced)")
    parser.add_argument("--cap_signature", type=int, default=30,
                        help="Max rows per signature (default 30)")
    parser.add_argument("--cap_type_db", type=int, default=300,
                        help="Max rows per (sqli_type, db_engine) cell (default 300)")
    parser.add_argument("--col", default="payload_delex_v2",
                        help="Column to hash for signature")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--limit", type=int, default=None, help="Limit rows for testing")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    if args.limit:
        df = df.head(args.limit).copy()

    report_stats("BEFORE", df)

    # Step 1: compute signatures
    df = compute_signatures(df, args.col)
    print(f"\nComputed signatures from column '{args.col}'")

    # Step 2: cap per signature (most aggressive)
    df = cap_per_signature(df, args.cap_signature, args.seed)
    report_stats(f"AFTER cap_signature={args.cap_signature}", df)

    # Step 3: cap per (type, db)
    df = cap_per_type_db(df, args.cap_type_db, args.seed)
    report_stats(f"AFTER cap_type_db={args.cap_type_db}", df)

    df.to_csv(args.output, index=False)
    print(f"\nWrote {len(df)} rows to {args.output}")


if __name__ == "__main__":
    main()
