"""merge_chunks.py — Concat tất cả chunk_*_labeled.csv thành relabeled_chat.csv.

Validates schema, dedup theo id, sort, print quality report.

Expected chunk schema (do subagent ghi):
  id, payload_inner, sqli_type, db_engine, confidence, reasoning, sources_agree
"""
import argparse
import glob
import os
import sys
from collections import Counter

import pandas as pd

VALID_TYPES = {
    "benign", "error_based", "boolean_blind", "time_blind", "union_based",
    "auth_bypass", "heavy_query", "out_of_band", "stacked_queries", "polyglot",
}
VALID_DBS = {
    "oracle", "mysql", "postgresql", "mssql", "firebird", "sqlite",
    "db2", "generic",
}

REQUIRED_COLS = ["id", "payload_inner", "sqli_type", "db_engine",
                 "confidence", "reasoning", "sources_agree"]


def validate_row(row: dict, row_idx: int, chunk_name: str) -> tuple[bool, str]:
    """Return (is_valid, error_msg). Logs issues but allows processing."""
    if row.get("sqli_type") not in VALID_TYPES:
        return False, f"invalid sqli_type='{row.get('sqli_type')}'"
    if row.get("db_engine") not in VALID_DBS:
        return False, f"invalid db_engine='{row.get('db_engine')}'"
    try:
        conf = float(row.get("confidence", 0))
        if not (0 <= conf <= 1):
            return False, f"confidence out of range: {conf}"
    except (ValueError, TypeError):
        return False, f"confidence not float: {row.get('confidence')!r}"
    reasoning = str(row.get("reasoning", ""))
    if len(reasoning) < 10:
        return False, f"reasoning too short ({len(reasoning)} chars)"
    return True, ""


def merge_chunks(temp_dir: str, output_csv: str, strict: bool = False):
    """Read all chunk_*_labeled.csv, validate, merge, save."""
    pattern = os.path.join(temp_dir, "chunk_*_labeled.csv")
    chunk_files = sorted(glob.glob(pattern))
    if not chunk_files:
        print(f"ERROR: no files matched {pattern}")
        sys.exit(1)

    print(f"Found {len(chunk_files)} chunk files")
    dfs = []
    n_invalid_total = 0
    error_examples = []

    for chunk_path in chunk_files:
        chunk_name = os.path.basename(chunk_path)
        try:
            df = pd.read_csv(chunk_path)
        except Exception as e:
            print(f"  ERROR reading {chunk_name}: {e}")
            continue

        # Validate columns
        missing = [c for c in REQUIRED_COLS if c not in df.columns]
        if missing:
            print(f"  {chunk_name}: missing columns {missing} — SKIP")
            continue

        # Validate rows
        valid_rows = []
        for idx, row in df.iterrows():
            ok, err = validate_row(row.to_dict(), idx, chunk_name)
            if ok:
                valid_rows.append(row)
            else:
                n_invalid_total += 1
                if len(error_examples) < 5:
                    error_examples.append((chunk_name, idx, err))
                if strict:
                    print(f"  STRICT mode: stopping at {chunk_name} row {idx}: {err}")
                    sys.exit(2)

        if valid_rows:
            valid_df = pd.DataFrame(valid_rows)
            dfs.append(valid_df)
            print(f"  {chunk_name}: {len(valid_df)}/{len(df)} valid rows")

    if not dfs:
        print("ERROR: no valid rows collected")
        sys.exit(1)

    merged = pd.concat(dfs, ignore_index=True)

    # Dedup by id (keep first)
    n_before = len(merged)
    merged = merged.drop_duplicates(subset="id", keep="first").reset_index(drop=True)
    n_dups = n_before - len(merged)
    if n_dups > 0:
        print(f"  Dropped {n_dups} duplicate ids")

    # Sort by id
    merged = merged.sort_values("id").reset_index(drop=True)

    merged.to_csv(output_csv, index=False)
    print(f"\nWrote {len(merged)} rows to {output_csv}")

    if n_invalid_total > 0:
        print(f"\nWARNING: {n_invalid_total} invalid rows skipped")
        print("First 5 errors:")
        for chunk_name, idx, err in error_examples:
            print(f"  {chunk_name} row {idx}: {err}")

    print_quality_report(merged)
    return merged


def print_quality_report(df: pd.DataFrame):
    print("\n" + "=" * 50)
    print("QUALITY REPORT")
    print("=" * 50)

    print(f"\nTotal rows: {len(df)}")

    print(f"\nType distribution:")
    for t, c in df["sqli_type"].value_counts().items():
        print(f"  {c:6d} ({c/len(df):6.2%})  {t}")

    print(f"\nDB distribution (top 8):")
    for d, c in df["db_engine"].value_counts().head(8).items():
        print(f"  {c:6d} ({c/len(df):6.2%})  {d}")

    print(f"\nConfidence stats:")
    print(f"  mean : {df['confidence'].mean():.3f}")
    print(f"  >=0.90: {(df['confidence']>=0.90).sum():6d} ({(df['confidence']>=0.90).mean():.2%})")
    print(f"  0.70-0.89: {((df['confidence']>=0.70) & (df['confidence']<0.90)).sum():6d}")
    print(f"  <0.70: {(df['confidence']<0.70).sum():6d}")

    print(f"\nSources agreement distribution:")
    for n, c in df["sources_agree"].value_counts().sort_index().items():
        print(f"  {c:6d} ({c/len(df):6.2%})  {n}/3 agree")

    df_len = df["reasoning"].fillna("").astype(str).str.len()
    print(f"\nReasoning length:")
    print(f"  mean : {df_len.mean():.1f} chars")
    print(f"  <50  : {(df_len<50).sum():6d} ({(df_len<50).mean():.2%})")
    print(f"  >=50 : {(df_len>=50).sum():6d} ({(df_len>=50).mean():.2%})")

    # Detect duplicate reasoning (red flag from V1 dataset)
    top_reasons = df["reasoning"].value_counts().head(5)
    print(f"\nTop 5 reasoning (duplicates = bad sign):")
    for r, c in top_reasons.items():
        marker = " !!" if c >= 50 else ("  ?" if c >= 20 else "")
        print(f"  [{c:4d}x{marker}] {str(r)[:80]}")


def main():
    parser = argparse.ArgumentParser(description="Merge labeled chunks → final CSV")
    parser.add_argument("--temp_dir", required=True, help="Dir containing chunk_*_labeled.csv")
    parser.add_argument("--output", required=True, help="Output merged CSV")
    parser.add_argument("--strict", action="store_true",
                        help="Stop on first invalid row (default: skip invalid rows)")
    args = parser.parse_args()

    merge_chunks(args.temp_dir, args.output, strict=args.strict)


if __name__ == "__main__":
    main()
