"""
gold_set_creator.py -- Stratified sampling to build a human-labeled gold set.

Samples N payloads from a labeled CSV, stratified by sqli_type x tier.
Outputs a CSV for manual human review and annotation.

Usage:
    python Skill/label-sqli/scripts/gold_set_creator.py \
        --input  Asset/LabelData/Testing/Testing_labeled.csv \
        --output Asset/LabelData/gold_200.csv \
        --n 200 \
        [--seed 42]

After running: open gold_200.csv, verify/correct 'sqli_type' column manually,
then use --gold_set with run_labeling.py to compute Precision@Gold.
"""

import argparse
import sys
from pathlib import Path

import pandas as pd


def stratified_sample(df: pd.DataFrame, n: int, seed: int = 42) -> pd.DataFrame:
    """
    Stratified sample by (sqli_type, tier). Each stratum gets proportional quota.
    Falls back to uniform sample if strata are too small.
    """
    strata_col = 'sqli_type'
    tier_col   = 'tier'

    # Build strata: (sqli_type, tier) combinations with actual rows
    if strata_col not in df.columns:
        print(f"[WARN] No '{strata_col}' column — using uniform sample")
        return df.sample(n=min(n, len(df)), random_state=seed)

    df = df.copy()
    if tier_col not in df.columns:
        df[tier_col] = 'unknown'

    df['_stratum'] = df[strata_col].fillna('none').astype(str) + '|' + df[tier_col].astype(str)
    strata_counts  = df['_stratum'].value_counts()
    total          = len(df)

    # Proportional quota per stratum, min 1 if stratum exists
    samples = []
    budget  = n
    strata_order = strata_counts.index.tolist()

    for i, stratum in enumerate(strata_order):
        stratum_df = df[df['_stratum'] == stratum]
        remaining_strata = len(strata_order) - i
        quota = max(1, round(budget / remaining_strata))
        quota = min(quota, len(stratum_df), budget)
        sampled = stratum_df.sample(n=quota, random_state=seed)
        samples.append(sampled)
        budget -= quota
        if budget <= 0:
            break

    result = pd.concat(samples).drop(columns=['_stratum'])
    result = result.sample(frac=1, random_state=seed).reset_index(drop=True)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Build a stratified gold set for Precision@Gold evaluation"
    )
    parser.add_argument('--input',  required=True, help='Labeled CSV (cascade output)')
    parser.add_argument('--output', required=True, help='Output gold set CSV')
    parser.add_argument('--n',      type=int, default=200, help='Number of samples (default 200)')
    parser.add_argument('--seed',   type=int, default=42,  help='Random seed')
    args = parser.parse_args()

    input_path  = Path(args.input)
    output_path = Path(args.output)

    if not input_path.exists():
        print(f"[FAIL] Input not found: {input_path}")
        sys.exit(1)

    print(f"[INFO] Loading {input_path.name}...")
    df = pd.read_csv(input_path, encoding='utf-8-sig')
    print(f"[INFO] Loaded {len(df):,} rows")

    # Prefer gold-tier rows (higher confidence) for gold set quality
    gold_tier = df[df.get('tier', pd.Series()) == 'gold']
    if len(gold_tier) >= args.n:
        pool = gold_tier
        print(f"[INFO] Pool: {len(pool):,} gold-tier rows (conf >= 0.85)")
    else:
        pool = df
        print(f"[INFO] Pool: all {len(pool):,} rows (not enough gold-tier rows)")

    sampled = stratified_sample(pool, n=args.n, seed=args.seed)
    print(f"[INFO] Sampled {len(sampled):,} rows across "
          f"{sampled['sqli_type'].nunique()} sqli_types")

    # Keep only the columns needed for human review
    keep_cols = ['payload'] if 'payload' in sampled.columns else []
    for col in ('payload_norm', 'sqli_type', 'db_engine', 'confidence', 'tier',
                'label_source', 'is_complex', 'payload_state'):
        if col in sampled.columns:
            keep_cols.append(col)

    output_df = sampled[keep_cols].copy()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_df.to_csv(output_path, encoding='utf-8-sig', index=False)

    print(f"\n[OK] Gold set written to: {output_path}")
    print(f"     → Open CSV, verify 'sqli_type' column, correct any wrong labels")
    print(f"     → Then run with: --gold_set {output_path}")
    print(f"\nType distribution in gold set:")
    if 'sqli_type' in output_df.columns:
        for t, c in output_df['sqli_type'].value_counts().items():
            print(f"  {str(t):<22} {c:>5,}")


if __name__ == '__main__':
    main()
