#!/usr/bin/env python3
"""
Generate comprehensive labeling report for chunks 061-070.
"""

import csv
from pathlib import Path
from collections import Counter
import sys

def analyze_chunk(chunk_num):
    """Analyze a single labeled chunk."""
    path = Path(f"C:\\Users\\Admin\\Documents\\GAN_SQLi\\Asset\\LabelData\\_chunks\\chunk_{chunk_num:03d}_labeled.csv")

    if not path.exists():
        return None

    data = {
        'chunk': chunk_num,
        'rows': [],
        'type_dist': Counter(),
        'engine_dist': Counter(),
        'conf_dist': Counter(),
        'low_conf': [],
        'short_reasoning': [],
    }

    with open(path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            data['rows'].append(row)

            sqli_type = row['sqli_type']
            db_engine = row['db_engine']
            confidence = float(row['confidence'])
            reasoning = row['reasoning']
            payload = row['payload_inner']

            data['type_dist'][sqli_type] += 1
            data['engine_dist'][db_engine] += 1

            # Confidence bucketing
            if confidence >= 0.95:
                data['conf_dist']['0.95+'] += 1
            elif confidence >= 0.80:
                data['conf_dist']['0.80-0.94'] += 1
            elif confidence >= 0.70:
                data['conf_dist']['0.70-0.79'] += 1
            else:
                data['conf_dist']['< 0.70'] += 1

            # Track issues
            if confidence < 0.70:
                data['low_conf'].append({
                    'id': row['id'],
                    'type': sqli_type,
                    'conf': confidence,
                    'payload': payload[:40]
                })

            if len(reasoning) < 50:
                data['short_reasoning'].append({
                    'id': row['id'],
                    'len': len(reasoning),
                    'reason': reasoning[:60]
                })

    return data

def main():
    chunk_analyses = []
    for i in range(61, 71):
        result = analyze_chunk(i)
        if result:
            chunk_analyses.append(result)

    # Generate report
    report_lines = []
    report_lines.append("=" * 100)
    report_lines.append("LABELING REPORT: Chunks 061-070 (2000 payloads)")
    report_lines.append("=" * 100)
    report_lines.append("")

    # Overall statistics
    total_rows = sum(len(c['rows']) for c in chunk_analyses)
    all_types = Counter()
    all_engines = Counter()
    all_confs = Counter()
    all_low_conf = []
    all_short_reason = []

    for chunk in chunk_analyses:
        all_types.update(chunk['type_dist'])
        all_engines.update(chunk['engine_dist'])
        all_confs.update(chunk['conf_dist'])
        all_low_conf.extend(chunk['low_conf'])
        all_short_reason.extend(chunk['short_reasoning'])

    report_lines.append(f"Total Payloads Labeled: {total_rows}")
    report_lines.append("")

    # Top 5 Types
    report_lines.append("TOP 5 SQLi TYPES:")
    report_lines.append("-" * 50)
    for sqli_type, count in all_types.most_common(5):
        pct = (count / total_rows * 100)
        report_lines.append(f"  {sqli_type:20s} {count:5d} ({pct:5.1f}%)")
    report_lines.append("")

    # DB Engine distribution
    report_lines.append("DATABASE ENGINE DISTRIBUTION:")
    report_lines.append("-" * 50)
    for db_engine, count in all_engines.most_common():
        pct = (count / total_rows * 100)
        report_lines.append(f"  {db_engine:20s} {count:5d} ({pct:5.1f}%)")
    report_lines.append("")

    # Confidence distribution
    report_lines.append("CONFIDENCE DISTRIBUTION:")
    report_lines.append("-" * 50)
    conf_order = ['0.95+', '0.80-0.94', '0.70-0.79', '< 0.70']
    for conf_level in conf_order:
        count = all_confs.get(conf_level, 0)
        pct = (count / total_rows * 100) if total_rows > 0 else 0
        report_lines.append(f"  {conf_level:15s} {count:5d} ({pct:5.1f}%)")
    report_lines.append("")

    # Quality issues summary
    report_lines.append("QUALITY ISSUES:")
    report_lines.append("-" * 50)
    report_lines.append(f"  Low confidence rows (< 0.70):     {len(all_low_conf)} ({len(all_low_conf)/total_rows*100:.1f}%)")
    report_lines.append(f"  Short reasoning (< 50 chars):     {len(all_short_reason)} ({len(all_short_reason)/total_rows*100:.1f}%)")
    report_lines.append("")

    # Per-chunk breakdown
    report_lines.append("")
    report_lines.append("=" * 100)
    report_lines.append("PER-CHUNK BREAKDOWN")
    report_lines.append("=" * 100)
    report_lines.append("")

    for chunk in chunk_analyses:
        chunk_num = chunk['chunk']
        rows = len(chunk['rows'])
        report_lines.append(f"CHUNK {chunk_num:03d} ({rows} rows)")
        report_lines.append("-" * 80)

        # Top types for this chunk
        report_lines.append("  Top 3 Types:")
        for sqli_type, count in chunk['type_dist'].most_common(3):
            pct = (count / rows * 100)
            report_lines.append(f"    {sqli_type:18s} {count:3d} ({pct:5.1f}%)")

        # DB engines
        report_lines.append("  DB Engines:")
        for db_engine, count in chunk['engine_dist'].most_common(3):
            pct = (count / rows * 100)
            report_lines.append(f"    {db_engine:18s} {count:3d} ({pct:5.1f}%)")

        # Issues
        report_lines.append("  Issues:")
        low_conf_count = len(chunk['low_conf'])
        short_reason_count = len(chunk['short_reasoning'])
        report_lines.append(f"    Low confidence:   {low_conf_count:3d} ({low_conf_count/rows*100:5.1f}%)")
        report_lines.append(f"    Short reasoning:  {short_reason_count:3d} ({short_reason_count/rows*100:5.1f}%)")

        report_lines.append("")

    # Sample low confidence rows
    if all_low_conf:
        report_lines.append("")
        report_lines.append("=" * 100)
        report_lines.append(f"SAMPLE LOW CONFIDENCE ROWS (showing first 10 of {len(all_low_conf)})")
        report_lines.append("=" * 100)
        report_lines.append("")
        for row in all_low_conf[:10]:
            report_lines.append(f"  ID: {row['id']:6s} | Type: {row['type']:15s} | Conf: {row['conf']:.2f} | Payload: {row['payload']}")
        report_lines.append("")

    # Sample short reasoning rows
    if all_short_reason:
        report_lines.append("")
        report_lines.append("=" * 100)
        report_lines.append(f"SAMPLE SHORT REASONING ROWS (< 50 chars, showing first 10 of {len(all_short_reason)})")
        report_lines.append("=" * 100)
        report_lines.append("")
        for row in all_short_reason[:10]:
            report_lines.append(f"  ID: {row['id']:6s} | Len: {row['len']:2d} | {row['reason']}")
        report_lines.append("")

    report_lines.append("")
    report_lines.append("=" * 100)
    report_lines.append("LABELING RULES APPLIED")
    report_lines.append("=" * 100)
    report_lines.append("""
1. PRIORITY CHAIN: Matched SQLi type to lowest priority number (1-14)
2. CONFIDENCE LEVELS:
   - 0.95: Clear primary signal, unambiguous
   - 0.85-0.90: Strong signal with minor uncertainty
   - 0.70-0.79: Weak signal or short payload
   - 0.50: Ambiguous/insufficient data (benign or unknown)
3. DATABASE ENGINE: Detected from DB-specific keywords
4. REASONING: Minimum 50 characters, cites specific signals
5. SOURCES_AGREE: Always 1 (single labeler consensus model)

TAXONOMY APPLIED:
  Priority 1 (rce): xp_cmdshell, certutil, powershell, cmd.exe, /bin/bash
  Priority 2 (out_of_band): load_file, utl_http, utl_inaddr, xp_dirtree, openrowset
  Priority 3 (stacked_queries): ; followed by CREATE/DROP/INSERT/EXEC
  Priority 4 (error_based): extractvalue, updatexml, ctxsys, xmltype
  Priority 5 (time_blind): sleep, pg_sleep, waitfor, benchmark, randomblob
  Priority 6 (heavy_query): COUNT(*) with 3+ table cross-join
  Priority 7 (union_based): UNION SELECT, UNION ALL SELECT
  Priority 8 (boolean_blind): AND 1=1, OR 1=1, AND 'a'='a', OR '1'='1'
  Priority 9 (auth_bypass): admin' OR, admin'--, admin'#
  Priority 10 (second_order): INSERT INTO with attack intent
  Priority 11 (polyglot): Works on 2+ DB engines simultaneously
  Priority 12 (lateral): JOIN with OR 1=1
  Priority 13 (benign): Legitimate SQL, no attack signals
  Priority 14 (unknown): Insufficient data to classify
""")
    report_lines.append("=" * 100)

    # Write report
    report_text = "\n".join(report_lines)
    report_path = Path("C:\\Users\\Admin\\Documents\\GAN_SQLi\\Asset\\LabelData\\_chunks\\LABELING_REPORT_061_070.txt")
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write(report_text)

    print(report_text)
    print(f"\nReport saved to: {report_path}")

if __name__ == '__main__':
    main()
