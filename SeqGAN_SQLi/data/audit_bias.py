"""
audit_bias.py — Phát hiện bias trong dataset SQLi.
Output: report ở stdout + JSON ở data/v2/audit/bias_report.json
"""
import argparse
import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd


def normalize_skeleton(payload: str) -> str:
    """Strip placeholders và whitespace để có structural skeleton."""
    s = re.sub(r"__\w+__", "_", str(payload))
    s = re.sub(r"\s+", " ", s).strip().lower()
    return s


def audit(csv_path: str, out_dir: str):
    df = pd.read_csv(csv_path)
    print(f"\n=== DATASET BIAS AUDIT ===")
    print(f"Total rows: {len(df)}")
    print(f"Columns: {list(df.columns)}")

    payload_col = next(
        (c for c in ["payload_norm", "payload", "payload_delex", "query"] if c in df.columns),
        None,
    )
    if not payload_col:
        raise ValueError("No payload column found in CSV")

    type_col = next(
        (c for c in ["sqli_type", "type", "attack_type", "label"] if c in df.columns),
        None,
    )

    report = {
        "total_rows": len(df),
        "payload_col": payload_col,
        "type_col": type_col,
    }

    # Test 1: Source diversity
    if "source" in df.columns:
        source_counts = df["source"].value_counts().to_dict()
        report["source_diversity"] = source_counts
        print(f"\n[Test 1] Source diversity:")
        for src, cnt in source_counts.items():
            print(f"  {src}: {cnt} ({cnt/len(df)*100:.1f}%)")
        max_source_pct = max(source_counts.values()) / len(df) * 100
        report["max_source_pct"] = max_source_pct
        if max_source_pct > 60:
            print(f"  WARNING: {max_source_pct:.1f}% from 1 source - heavy bias")
    else:
        print(f"\n[Test 1] NO source column - cannot audit source diversity")
        report["source_diversity"] = None

    # Test 2: Skeleton diversity
    df["skeleton"] = df[payload_col].apply(normalize_skeleton)
    unique_skels = df["skeleton"].nunique()
    skeleton_ratio = unique_skels / len(df)
    report["skeleton_uniqueness"] = {
        "unique": unique_skels,
        "total": len(df),
        "ratio": skeleton_ratio,
    }
    print(f"\n[Test 2] Unique skeletons: {unique_skels} / {len(df)} = {skeleton_ratio*100:.2f}%")
    if skeleton_ratio < 0.05:
        print(f"  CRITICAL: <5% uniqueness - heavy structural bias")
    elif skeleton_ratio < 0.20:
        print(f"  WARNING: <20% uniqueness - significant structural bias")

    # Test 3: Per-type skeleton diversity
    if type_col:
        per_type = {}
        print(f"\n[Test 3] Per-type skeleton uniqueness:")
        for sqli_type, group in df.groupby(type_col):
            ratio = group["skeleton"].nunique() / max(len(group), 1)
            per_type[str(sqli_type)] = {
                "count": int(len(group)),
                "unique_skeletons": int(group["skeleton"].nunique()),
                "ratio": ratio,
            }
            warn = "  [BIAS]" if ratio < 0.10 else ""
            print(f"  {sqli_type}: {len(group)} rows, {group['skeleton'].nunique()} skeletons ({ratio*100:.1f}%){warn}")
        report["per_type"] = per_type

    # Test 4: Top frequent tokens (xem dataset có dominated bởi 1 pattern không)
    all_tokens = []
    for p in df[payload_col].astype(str):
        all_tokens.extend(p.lower().split())
    token_counts = Counter(all_tokens)
    top_20 = token_counts.most_common(20)
    report["top_tokens"] = [{"token": t, "count": c} for t, c in top_20]
    print(f"\n[Test 4] Top 20 tokens:")
    for t, c in top_20:
        pct = c / len(all_tokens) * 100
        flag = "  [DOMINANT]" if pct > 5 else ""
        print(f"  '{t}': {c} ({pct:.2f}%){flag}")

    # Test 5: Target table check (G4 specific concern)
    table_patterns = re.compile(r"from\s+(\w+)|insert\s+into\s+(\w+)|update\s+(\w+)", re.IGNORECASE)
    target_tables = []
    for p in df[payload_col].astype(str):
        for match in table_patterns.finditer(p):
            for g in match.groups():
                if g:
                    target_tables.append(g.lower())
    if target_tables:
        table_counts = Counter(target_tables).most_common(10)
        report["top_target_tables"] = [{"table": t, "count": c} for t, c in table_counts]
        print(f"\n[Test 5] Top target tables:")
        total_table_refs = len(target_tables)
        for t, c in table_counts:
            pct = c / total_table_refs * 100
            flag = "  [BIAS]" if pct > 20 else ""
            print(f"  {t}: {c} ({pct:.1f}%){flag}")

    # Write report
    out_path = Path(out_dir) / "bias_report.json"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)
    print(f"\nReport saved: {out_path}")

    return report


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--csv", required=True, help="Path to dataset CSV")
    parser.add_argument("--out_dir", default="SeqGAN_SQLi/data/v2/audit")
    args = parser.parse_args()
    audit(args.csv, args.out_dir)
