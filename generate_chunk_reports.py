#!/usr/bin/env python3
"""
Generate detailed reports for labeled chunks 081-090.
"""

import pandas as pd
from pathlib import Path

DATA_DIR = Path(r"C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks")
REPORT_DIR = DATA_DIR / "reports"
REPORT_DIR.mkdir(exist_ok=True)

def generate_chunk_report(chunk_num: int):
    """Generate detailed report for a single chunk."""
    csv_file = DATA_DIR / f"chunk_{chunk_num:03d}_labeled.csv"

    if not csv_file.exists():
        return None

    df = pd.read_csv(csv_file)

    # Statistics
    total = len(df)
    type_dist = df['sqli_type'].value_counts().to_dict()
    db_dist = df['db_engine'].value_counts().to_dict()
    conf_avg = df['confidence'].mean()
    conf_min = df['confidence'].min()
    conf_max = df['confidence'].max()

    low_conf = df[df['confidence'] < 0.7]
    short_reasoning = df[df['reasoning'].str.len() < 50]

    # Report content
    report = f"""
CHUNK {chunk_num:03d} LABELING REPORT
{'='*80}

BASIC STATISTICS
----------------
Total Rows: {total}
Average Confidence: {conf_avg:.3f}
Min/Max Confidence: {conf_min:.2f} - {conf_max:.2f}

TOP-5 SQLI TYPES
----------------
"""
    for sqli_type, count in sorted(type_dist.items(), key=lambda x: x[1], reverse=True)[:5]:
        pct = 100 * count / total
        report += f"{sqli_type:20s}: {count:4d} ({pct:5.1f}%)\n"

    report += f"\nDB ENGINE DISTRIBUTION\n{'-'*40}\n"
    for db, count in sorted(db_dist.items(), key=lambda x: x[1], reverse=True):
        pct = 100 * count / total
        report += f"{db:20s}: {count:4d} ({pct:5.1f}%)\n"

    report += f"\nQUALITY ASSESSMENT\n{'-'*40}\n"
    report += f"Low-confidence rows (<0.7): {len(low_conf)} ({100*len(low_conf)/total:.1f}%)\n"
    report += f"Short-reasoning rows (<50 chars): {len(short_reasoning)} ({100*len(short_reasoning)/total:.1f}%)\n"

    report += f"\nSOURCES_AGREE DISTRIBUTION\n{'-'*40}\n"
    sources_dist = df['sources_agree'].value_counts().sort_index()
    for sources, count in sources_dist.items():
        pct = 100 * count / total
        report += f"sources_agree={sources}: {count:4d} ({pct:5.1f}%)\n"

    # Sample of each type
    report += f"\nSAMPLE ROWS BY TYPE (first 2 of each)\n{'-'*40}\n"
    for sqli_type in sorted(type_dist.keys()):
        type_df = df[df['sqli_type'] == sqli_type].head(2)
        report += f"\n{sqli_type.upper()}\n"
        for idx, row in type_df.iterrows():
            report += f"  ID {row['id']}: confidence={row['confidence']:.2f}, sources_agree={row['sources_agree']}\n"
            report += f"    Payload: {row['payload_inner'][:80]}...\n"
            report += f"    Reasoning: {row['reasoning'][:100]}...\n"

    # Problem rows
    if len(low_conf) > 0:
        report += f"\nLOW-CONFIDENCE ROWS (first 5)\n{'-'*40}\n"
        for idx, row in low_conf.head(5).iterrows():
            report += f"ID {row['id']}: {row['sqli_type']} ({row['confidence']:.2f})\n"
            report += f"  {row['reasoning'][:120]}\n\n"

    return report

def main():
    """Generate all reports."""
    print("Generating detailed reports for chunks 081-090...\n")

    summary_lines = []

    for chunk_num in range(81, 91):
        report = generate_chunk_report(chunk_num)
        if report:
            # Save to file
            report_file = REPORT_DIR / f"chunk_{chunk_num:03d}_report.txt"
            with open(report_file, 'w', encoding='utf-8') as f:
                f.write(report)

            # Extract key stats for summary
            csv_file = DATA_DIR / f"chunk_{chunk_num:03d}_labeled.csv"
            df = pd.read_csv(csv_file)
            top_type = df['sqli_type'].value_counts().index[0]
            top_count = df['sqli_type'].value_counts().iloc[0]
            low_conf_pct = 100 * len(df[df['confidence'] < 0.7]) / len(df)

            summary_lines.append(
                f"chunk_{chunk_num:03d}: {len(df)} rows, top={top_type} ({top_count}), low_conf={low_conf_pct:.1f}%"
            )
            print(f"[OK] chunk_{chunk_num:03d}_report.txt")

    # Write master summary
    summary_file = REPORT_DIR / "SUMMARY_081-090.txt"
    with open(summary_file, 'w', encoding='utf-8') as f:
        f.write("LABELING SUMMARY: CHUNKS 081-090\n")
        f.write("="*80 + "\n\n")
        for line in summary_lines:
            f.write(line + "\n")

    print(f"\nAll reports saved to: {REPORT_DIR}")
    print(f"Master summary: {summary_file}")

if __name__ == '__main__':
    main()
