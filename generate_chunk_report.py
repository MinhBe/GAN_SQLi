#!/usr/bin/env python3
"""
Generate comprehensive report for chunks 071-080 labeling.
"""

import csv
from pathlib import Path
from collections import defaultdict

def analyze_chunk(chunk_num: int) -> dict:
    """Analyze a single labeled chunk."""
    chunk_path = Path(f'C:\\Users\\Admin\\Documents\\GAN_SQLi\\Asset\\LabelData\\_chunks\\chunk_{chunk_num:03d}_labeled.csv')

    if not chunk_path.exists():
        return None

    type_counts = defaultdict(int)
    db_counts = defaultdict(int)
    conf_buckets = defaultdict(int)
    low_conf = []
    short_reasoning = []
    sources_distribution = defaultdict(int)
    sample_rows = []

    try:
        with open(chunk_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            row_count = 0
            for row in reader:
                row_count += 1
                if row_count <= 3:
                    sample_rows.append(row)

                sqli_type = row.get('sqli_type', '').strip()
                db_engine = row.get('db_engine', '').strip()
                reasoning = row.get('reasoning', '').strip()
                sources = int(row.get('sources_agree', 0))

                type_counts[sqli_type] += 1
                db_counts[db_engine] += 1
                sources_distribution[sources] += 1

                try:
                    conf = float(row.get('confidence', 0.5))
                    if conf >= 0.95:
                        conf_buckets['0.95-1.00'] += 1
                    elif conf >= 0.80:
                        conf_buckets['0.80-0.94'] += 1
                    elif conf >= 0.70:
                        conf_buckets['0.70-0.79'] += 1
                    elif conf >= 0.60:
                        conf_buckets['0.60-0.69'] += 1
                    else:
                        conf_buckets['<0.60'] += 1
                        low_conf.append((row.get('id', ''), sqli_type, conf))
                except ValueError:
                    pass

                if len(reasoning) < 50:
                    short_reasoning.append((row.get('id', ''), len(reasoning)))

        return {
            'chunk_num': chunk_num,
            'total_rows': row_count,
            'type_counts': dict(type_counts),
            'db_counts': dict(db_counts),
            'conf_buckets': dict(conf_buckets),
            'sources_distribution': dict(sources_distribution),
            'low_conf': low_conf[:5],
            'short_reasoning': short_reasoning[:5],
            'sample_rows': sample_rows,
        }

    except Exception as e:
        return {'chunk_num': chunk_num, 'error': str(e)}


def main():
    print('\n' + '=' * 100)
    print('LABELING REPORT: CHUNKS 071-080')
    print('=' * 100)

    all_type_counts = defaultdict(int)
    all_db_counts = defaultdict(int)
    all_sources_distribution = defaultdict(int)
    total_rows = 0
    all_low_conf = []
    all_short_reasoning = []

    chunk_reports = []

    for chunk_num in range(71, 81):
        report = analyze_chunk(chunk_num)
        if report is None or 'error' in report:
            print(f'\nChunk {chunk_num:03d}: ERROR - {report.get("error", "File not found")}')
            continue

        chunk_reports.append(report)
        total_rows += report['total_rows']

        for t, c in report['type_counts'].items():
            all_type_counts[t] += c
        for d, c in report['db_counts'].items():
            all_db_counts[d] += c
        for s, c in report['sources_distribution'].items():
            all_sources_distribution[s] += c

        all_low_conf.extend(report['low_conf'])
        all_short_reasoning.extend(report['short_reasoning'])

    # Print per-chunk summary
    print('\n1. PER-CHUNK SUMMARY')
    print('-' * 100)
    for report in sorted(chunk_reports, key=lambda x: x['chunk_num']):
        print(f"\nChunk {report['chunk_num']:03d}: {report['total_rows']} rows")
        print(f"  Top 3 types: {sorted(report['type_counts'].items(), key=lambda x: x[1], reverse=True)[:3]}")
        print(f"  DB engines: {sorted(report['db_counts'].items(), key=lambda x: x[1], reverse=True)[:3]}")
        print(f"  Confidence distribution: {report['conf_buckets']}")
        print(f"  Sources agree: {report['sources_distribution']}")

    # Print aggregate statistics
    print('\n' + '=' * 100)
    print('2. AGGREGATE STATISTICS (ALL 10 CHUNKS)')
    print('-' * 100)

    print(f"\nTotal rows labeled: {total_rows}")

    print("\nSQLi Type Distribution (Top 10):")
    sorted_types = sorted(all_type_counts.items(), key=lambda x: x[1], reverse=True)
    for typ, count in sorted_types[:10]:
        pct = (count / total_rows) * 100
        print(f"  {typ:20s}: {count:4d} ({pct:5.1f}%)")

    print("\nDB Engine Distribution:")
    sorted_dbs = sorted(all_db_counts.items(), key=lambda x: x[1], reverse=True)
    for db, count in sorted_dbs:
        pct = (count / total_rows) * 100
        print(f"  {db:15s}: {count:4d} ({pct:5.1f}%)")

    print("\nSources Agreement Distribution:")
    print("  (how many sources agree with the label)")
    for sources in sorted(all_sources_distribution.keys()):
        count = all_sources_distribution[sources]
        pct = (count / total_rows) * 100
        print(f"  {sources} sources: {count:4d} ({pct:5.1f}%)")

    print(f"\nConfidence Quality (all chunks combined):")
    all_conf_buckets = defaultdict(int)
    for report in chunk_reports:
        for bucket, count in report['conf_buckets'].items():
            all_conf_buckets[bucket] += count
    for bucket in ['0.95-1.00', '0.80-0.94', '0.70-0.79', '0.60-0.69', '<0.60']:
        count = all_conf_buckets[bucket]
        pct = (count / total_rows) * 100
        print(f"  {bucket}: {count:4d} ({pct:5.1f}%)")

    # Print quality metrics
    print('\n' + '=' * 100)
    print('3. QUALITY METRICS')
    print('-' * 100)

    total_low_conf = sum(1 for report in chunk_reports for _ in report['low_conf'])
    total_short_reasoning = sum(1 for report in chunk_reports for _ in report['short_reasoning'])

    print(f"\nLow confidence rows (<0.60): {len(all_low_conf)}")
    print(f"  Percentage: {(len(all_low_conf) / total_rows) * 100:.1f}%")
    if all_low_conf:
        print(f"  Sample (first 5):")
        for row_id, typ, conf in all_low_conf[:5]:
            print(f"    - ID {row_id}: {typ} (conf={conf:.2f})")

    print(f"\nShort reasoning (<50 chars): {len(all_short_reasoning)}")
    print(f"  Percentage: {(len(all_short_reasoning) / total_rows) * 100:.1f}%")
    if all_short_reasoning:
        print(f"  Sample (first 5):")
        for row_id, length in all_short_reasoning[:5]:
            print(f"    - ID {row_id}: {length} chars")

    # Reasoning quality analysis
    reasoning_quality_pass = total_rows - len(all_short_reasoning)
    print(f"\nReasoning quality (>=50 chars): {reasoning_quality_pass}/{total_rows} ({(reasoning_quality_pass/total_rows)*100:.1f}%)")

    # Confidence quality
    high_conf = sum(1 for report in chunk_reports for c in report['conf_buckets'].get('0.95-1.00', 0) for _ in [c])
    med_conf = sum(1 for report in chunk_reports for c in report['conf_buckets'].get('0.80-0.94', 0) for _ in [c])
    acceptable_conf = high_conf + med_conf + sum(all_conf_buckets.get('0.70-0.79', 0) for _ in [1])

    print(f"Confidence >=0.70: {acceptable_conf}/{total_rows} ({(acceptable_conf/total_rows)*100:.1f}%)")

    # Sample output verification
    print('\n' + '=' * 100)
    print('4. SAMPLE LABELED ROWS (First row from each chunk)')
    print('-' * 100)
    for report in sorted(chunk_reports, key=lambda x: x['chunk_num']):
        if report['sample_rows']:
            row = report['sample_rows'][0]
            print(f"\nChunk {report['chunk_num']:03d}, ID {row.get('id', 'N/A')}:")
            print(f"  Payload: {row.get('payload_inner', '')[:50]}...")
            print(f"  Type: {row.get('sqli_type', '')}")
            print(f"  DB: {row.get('db_engine', '')}")
            print(f"  Confidence: {row.get('confidence', '')}")
            print(f"  Sources agree: {row.get('sources_agree', '')}")
            print(f"  Reasoning: {row.get('reasoning', '')[:70]}...")

    print('\n' + '=' * 100)
    print('OUTPUT FILES CREATED:')
    print('-' * 100)
    for i in range(71, 81):
        print(f"  chunk_{i:03d}_labeled.csv")

    print('\n' + '=' * 100)


if __name__ == '__main__':
    main()
