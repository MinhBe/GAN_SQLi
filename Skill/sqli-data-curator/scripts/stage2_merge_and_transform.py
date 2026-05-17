#!/usr/bin/env python3
"""
Stage 2 + 3 consolidated: Merge chunks → Strip wrapper → Delex v2 → Tier split

Usage:
  python stage2_merge_and_transform.py \
    --chunks_dir Asset/LabelData/_chunks \
    --keep_csv Asset/LabelData/keep.csv \
    --output_dir Asset/LabelData

Outputs:
  - relabeled_chat.csv (merged from chunks)
  - merged_final.csv (keep + relabeled)
  - stripped.csv (wrapper removed)
  - dataset_v3_raw.csv (delex v2 applied)
  - tiers/gold.csv, silver.csv, bronze.csv
"""
import argparse
import glob
import os
import sys
import re
import hashlib
from collections import Counter
from pathlib import Path

import pandas as pd
import numpy as np

# Tier thresholds
TIER_CONFIG = {
    'gold': {'confidence': 0.90, 'min_sources_agree': 3},
    'silver': {'confidence': 0.70, 'min_sources_agree': 2},
    'bronze': {'confidence': 0.50, 'min_sources_agree': 1},
}

WRAPPER_PATTERNS = [
    r"^['\"]?\s*(select|SELECT).*?WHERE\s+(username|login|email)\s*=\s*['\"]([^'\"]*)['\"]",
    r"^['\"]?\s*(select|SELECT).*?WHERE\s+(id|user_id)\s*=\s*(\d+)",
    r"^['\"]?\s*(insert|INSERT).*?VALUES\s*\(",
]

FUNCTION_WHITELIST = {
    # Oracle
    'xmltype': 'oracle', 'extractvalue': 'mysql', 'updatexml': 'mysql',
    'pg_sleep': 'postgresql', 'dbms_pipe': 'oracle', 'dbms_lock': 'oracle',
    'randomblob': 'sqlite', 'elt': 'mysql', 'chr': 'oracle',
    'sleep': 'mysql', 'waitfor': 'mssql', 'benchmark': 'mysql',
    'information_schema': 'mysql', 'sys': 'mssql', 'pg_catalog': 'postgresql',
}

def strip_wrapper(payload: str) -> str:
    """Remove outer wrapper pattern (select ... WHERE username = '...')."""
    for pattern in WRAPPER_PATTERNS:
        match = re.search(pattern, payload, re.IGNORECASE)
        if match:
            # Extract inner payload from group 3 or last group
            groups = match.groups()
            for i in range(len(groups) - 1, -1, -1):
                if groups[i] and not groups[i].upper() in ['SELECT', 'INSERT']:
                    return groups[i].strip().strip('\'"')
    return payload

def delex_v2(payload: str, function_whitelist: dict) -> str:
    """Delex v2: replace literals but preserve function names in whitelist."""
    # Replace string literals with __STR__
    result = re.sub(r"'[^']*'", '__STR__', payload)
    result = re.sub(r'"[^"]*"', '__STR__', result)

    # Replace numbers with __NUM__
    result = re.sub(r'\b\d+\b', '__NUM__', result)

    # Replace identifiers NOT in whitelist with __IDENT__
    # Keep function names from whitelist intact
    def replace_ident(match):
        word = match.group(0)
        if word.lower() in function_whitelist:
            return word
        if word.isupper():  # SQL keywords
            return word
        return '__IDENT__'

    result = re.sub(r'\b[a-zA-Z_][a-zA-Z0-9_]*\b', replace_ident, result)

    return result.strip()

def compute_signature(payload_delex: str) -> str:
    """SHA1 hash of delex payload, first 8 chars."""
    h = hashlib.sha1(payload_delex.encode()).hexdigest()
    return h[:8]

def assign_tier(row: dict) -> str:
    """Assign Gold/Silver/Bronze based on confidence + sources_agree."""
    conf = float(row.get('confidence', 0.5))
    sources = int(row.get('sources_agree', 0))

    if conf >= TIER_CONFIG['gold']['confidence'] and sources >= TIER_CONFIG['gold']['min_sources_agree']:
        return 'gold'
    elif conf >= TIER_CONFIG['silver']['confidence'] and sources >= TIER_CONFIG['silver']['min_sources_agree']:
        return 'silver'
    else:
        return 'bronze'

def merge_chunks(chunks_dir: str) -> pd.DataFrame:
    """Merge all chunk_*_labeled.csv files."""
    pattern = os.path.join(chunks_dir, "chunk_*_labeled.csv")
    files = sorted(glob.glob(pattern))
    print(f"Found {len(files)} chunk files")

    dfs = []
    for f in files:
        try:
            df = pd.read_csv(f)
            dfs.append(df)
        except Exception as e:
            print(f"  Error reading {os.path.basename(f)}: {e}")

    if not dfs:
        print("ERROR: No valid chunk files found")
        sys.exit(1)

    result = pd.concat(dfs, ignore_index=True)
    result = result.drop_duplicates(subset='id')
    print(f"Merged {len(result)} rows from chunks")
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chunks_dir', default='Asset/LabelData/_chunks', help='Directory with chunk_*_labeled.csv')
    parser.add_argument('--keep_csv', default='Asset/LabelData/keep.csv', help='KEEP verdicts')
    parser.add_argument('--output_dir', default='Asset/LabelData', help='Output directory')
    args = parser.parse_args()

    os.makedirs(args.output_dir, exist_ok=True)
    os.makedirs(os.path.join(args.output_dir, 'tiers'), exist_ok=True)

    print("\n=== STAGE 2: Merge chunks ===")
    relabeled_df = merge_chunks(args.chunks_dir)
    relabeled_df.to_csv(os.path.join(args.output_dir, 'relabeled_chat.csv'), index=False)

    print("\n=== Concat KEEP + RELABELED ===")
    try:
        keep_df = pd.read_csv(args.keep_csv)
        print(f"Loaded {len(keep_df)} KEEP rows")
    except:
        print("Warning: KEEP CSV not found, using relabeled only")
        keep_df = pd.DataFrame()

    merged_df = pd.concat([keep_df, relabeled_df], ignore_index=True).drop_duplicates(subset='id')
    print(f"Total merged: {len(merged_df)} rows")
    merged_df.to_csv(os.path.join(args.output_dir, 'merged_final.csv'), index=False)

    print("\n=== STAGE 3a: Strip wrapper ===")
    merged_df['payload_inner'] = merged_df['payload_norm'].apply(strip_wrapper)
    merged_df.to_csv(os.path.join(args.output_dir, 'stripped.csv'), index=False)

    print("\n=== STAGE 3b: Delex v2 ===")
    merged_df['payload_delex'] = merged_df['payload_inner'].apply(lambda x: delex_v2(str(x), FUNCTION_WHITELIST))
    merged_df['signature'] = merged_df['payload_delex'].apply(compute_signature)

    print("\n=== STAGE 4: Tier split ===")
    merged_df['tier'] = merged_df.apply(assign_tier, axis=1)

    tier_counts = merged_df['tier'].value_counts()
    print(f"Tier distribution:\n{tier_counts}")

    for tier in ['gold', 'silver', 'bronze']:
        tier_df = merged_df[merged_df['tier'] == tier].copy()

        # Cap signatures at 30 rows each
        if tier == 'gold':
            sig_counts = tier_df['signature'].value_counts()
            to_drop = []
            for sig, count in sig_counts.items():
                if count > 30:
                    rows = tier_df[tier_df['signature'] == sig].index.tolist()
                    to_drop.extend(rows[30:])  # Keep first 30, drop rest
            tier_df = tier_df.drop(to_drop)
            print(f"{tier}: {len(tier_df)} rows after capping signatures")

        output_path = os.path.join(args.output_dir, 'tiers', f'{tier}.csv')
        tier_df.to_csv(output_path, index=False)

    print("\n=== Final dataset_v3_raw.csv ===")
    final_df = merged_df[['id', 'payload_inner', 'payload_delex', 'sqli_type', 'db_engine', 'confidence', 'reasoning', 'sources_agree', 'signature', 'tier']]
    final_df.to_csv(os.path.join(args.output_dir, 'dataset_v3_raw.csv'), index=False)
    print(f"Saved {len(final_df)} rows to dataset_v3_raw.csv")

if __name__ == '__main__':
    main()
