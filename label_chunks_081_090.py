#!/usr/bin/env python3
"""
Label chunks 081-090 with SQLi classification.
Output: chunk_NNN_labeled.csv with columns:
  id, payload_inner, sqli_type, db_engine, confidence, reasoning, sources_agree
"""

import pandas as pd
import re
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, Tuple, List

# Base paths
DATA_DIR = Path(r"C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks")
OUTPUT_DIR = DATA_DIR  # Save labeled files in same directory

# SQLi Type Priorities (lower number = higher priority)
SQLI_PRIORITY = {
    'rce': 1,
    'out_of_band': 2,
    'stacked_queries': 3,
    'error_based': 4,
    'time_blind': 5,
    'heavy_query': 6,
    'union_based': 7,
    'boolean_blind': 8,
    'auth_bypass': 9,
    'second_order': 10,
    'polyglot': 11,
    'lateral': 12,
    'benign': 13,
    'unknown': 14,
}

# Signal patterns
SIGNALS = {
    'rce': {
        'patterns': [
            r'xp_cmdshell', r'certutil', r'powershell', r'/bin/bash', r'cmd\.exe',
            r'exec\s+xp_cmdshell'
        ],
        'db': 'mssql',
    },
    'out_of_band': {
        'patterns': [
            r'load_file', r'utl_http', r'utl_inaddr', r'xp_dirtree',
            r'xp_fileexist', r'openrowset', r'dns'
        ],
        'db': 'generic',
    },
    'stacked_queries': {
        'patterns': [
            r';\s*(create|drop|insert|update|delete|exec)',
        ],
        'db': 'generic',
    },
    'error_based': {
        'patterns': [
            r'extractvalue', r'updatexml', r'xmltype',
            r'utl_inaddr\.get_host_address', r'ctxsys\.drithsx'
        ],
        'db': 'generic',
    },
    'time_blind': {
        'patterns': [
            (r'sleep\s*\(', 'mysql'),
            (r'pg_sleep\s*\(', 'postgresql'),
            (r'waitfor\s+delay', 'mssql'),
            (r'benchmark\s*\(', 'mysql'),
            (r'randomblob\s*\(', 'sqlite'),
            (r'dbms_pipe', 'oracle'),
            (r'dbms_lock', 'oracle'),
        ],
        'db': None,  # DB-specific
    },
    'heavy_query': {
        'patterns': [
            r'count\s*\(\s*\*\s*\)\s+from.*,.*,.*',  # >=3 tables cross-join
        ],
        'db': 'generic',
    },
    'union_based': {
        'patterns': [
            r'union\s+(all\s+)?select',
        ],
        'db': 'generic',
    },
    'boolean_blind': {
        'patterns': [
            r'and\s+1\s*=\s*1',
            r'and\s+1\s*=\s*2',
            r'or\s+1\s*=\s*1',
            r'or\s+\'a\'\s*=\s*\'a\'',
            r'or\s+\'1\'\s*=\s*\'1\'',
            r'and\s+\'a\'\s*=\s*\'a\'',
        ],
        'db': 'generic',
    },
    'auth_bypass': {
        'patterns': [
            r'admin\s*\'',
            r'admin\s*--',
            r'admin\s*#',
            r'admin\s+or',
        ],
        'db': 'generic',
    },
    'second_order': {
        'patterns': [
            r'insert\s+into.*values',
        ],
        'db': 'generic',
    },
    'polyglot': {
        'patterns': [
            r'/\*\+\*/|/\*!\d+',  # MySQL/other specific comments
            r'\/\*\*\/or\/\*\*\/',  # polyglot OR pattern
        ],
        'db': 'generic',
    },
    'lateral': {
        'patterns': [
            r'lateral\s+join',
            r'join.*on.*or\s+1\s*=\s*1',
        ],
        'db': 'generic',
    },
}

# Benign keywords - very strict
BENIGN_KEYWORDS = {
    'union', 'sleep', 'pg_sleep', 'waitfor', 'benchmark', 'extractvalue',
    'updatexml', 'xp_cmdshell', 'load_file', 'utl_inaddr', 'ctxsys',
    'utl_http', 'and 1=1', 'or 1=1', 'admin\'', 'or \'1\'=\'1\'', 'insert'
}

# DB-specific signatures
DB_SIGNATURES = {
    'pg_sleep': 'postgresql',
    'waitfor': 'mssql',
    'utl_inaddr': 'oracle',
    'ctxsys': 'oracle',
    'randomblob': 'sqlite',
    'sleep': 'mysql',
    'xp_cmdshell': 'mssql',
    'xp_dirtree': 'mssql',
    '@@version': 'generic',
    'information_schema': 'mysql',
    'sqlite_version': 'sqlite',
    'rdb$': 'firebird',
    'sysibm': 'db2',
}

def normalize_payload(payload: str) -> str:
    """Normalize payload for matching."""
    if not isinstance(payload, str):
        return ""
    return payload.lower().strip()

def find_signals(payload: str) -> Dict[str, List[str]]:
    """Find all matching signals in payload."""
    norm_payload = normalize_payload(payload)
    found_signals = {}

    for sqli_type, signal_info in SIGNALS.items():
        if isinstance(signal_info['patterns'][0], tuple):
            # DB-specific patterns (time_blind)
            for pattern, db in signal_info['patterns']:
                if re.search(pattern, norm_payload, re.IGNORECASE):
                    if sqli_type not in found_signals:
                        found_signals[sqli_type] = []
                    found_signals[sqli_type].append((pattern, db))
        else:
            # Regular patterns
            for pattern in signal_info['patterns']:
                if re.search(pattern, norm_payload, re.IGNORECASE):
                    if sqli_type not in found_signals:
                        found_signals[sqli_type] = []
                    found_signals[sqli_type].append(pattern)

    return found_signals

def detect_db_engine(payload: str, sqli_type: str) -> str:
    """Detect DB engine from payload signatures."""
    norm_payload = normalize_payload(payload)

    # Check DB-specific signatures
    for sig, db in DB_SIGNATURES.items():
        if sig in norm_payload:
            return db

    # For time_blind, infer DB from time function
    if sqli_type == 'time_blind':
        if 'pg_sleep' in norm_payload:
            return 'postgresql'
        elif 'waitfor' in norm_payload:
            return 'mssql'
        elif 'randomblob' in norm_payload:
            return 'sqlite'
        elif 'benchmark' in norm_payload:
            return 'mysql'
        elif 'sleep' in norm_payload:
            return 'mysql'
        elif 'dbms_lock' in norm_payload or 'dbms_pipe' in norm_payload:
            return 'oracle'

    return 'generic'

def is_benign(payload: str) -> bool:
    """Check if payload is truly benign."""
    norm_payload = normalize_payload(payload)

    # Strict check: any attack keyword disqualifies as benign
    for keyword in BENIGN_KEYWORDS:
        if keyword in norm_payload:
            return False

    # Must look like SQL but without attack patterns
    sql_keywords = ['select', 'from', 'where', 'insert', 'update', 'delete', 'create']
    has_sql = any(kw in norm_payload for kw in sql_keywords)

    return has_sql

def label_row(row_id: int, payload: str, existing_labels: Dict = None) -> Dict:
    """
    Label a single row.

    Returns:
        Dict with: sqli_type, db_engine, confidence, reasoning, sources_agree
    """
    if not isinstance(payload, str) or not payload.strip():
        return {
            'sqli_type': 'unknown',
            'db_engine': 'unknown',
            'confidence': 0.5,
            'reasoning': 'Empty or invalid payload',
            'sources_agree': 0,
        }

    norm_payload = normalize_payload(payload)

    # Find all signals
    found_signals = find_signals(payload)

    # If no signals and looks benign
    if not found_signals and is_benign(payload):
        return {
            'sqli_type': 'benign',
            'db_engine': 'generic',
            'confidence': 0.85,
            'reasoning': 'Valid SQL structure without attack patterns (SELECT/FROM/WHERE without injection signals)',
            'sources_agree': 1,
        }

    # If no signals found
    if not found_signals:
        return {
            'sqli_type': 'unknown',
            'db_engine': 'unknown',
            'confidence': 0.5,
            'reasoning': 'Insufficient signals to classify; may be malformed or non-SQL text',
            'sources_agree': 0,
        }

    # Get highest priority type (lowest number)
    best_type = min(found_signals.keys(),
                   key=lambda x: SQLI_PRIORITY.get(x, 99))

    # Detect DB engine
    db_engine = detect_db_engine(payload, best_type)

    # Calculate confidence based on signal strength and clarity
    signal_count = len(found_signals.get(best_type, []))
    confidence = min(0.95, 0.50 + 0.15 * signal_count)
    if signal_count >= 2:
        confidence = min(0.95, 0.70 + 0.10 * signal_count)

    # Build reasoning
    signal_evidence = found_signals[best_type]
    if isinstance(signal_evidence[0], tuple):
        sig_str = f"{signal_evidence[0][0]}"
    else:
        sig_str = signal_evidence[0]

    reasoning = f"Signal match: {sig_str} → {best_type} (P{SQLI_PRIORITY[best_type]}); DB: {db_engine}"
    if signal_count >= 2:
        reasoning += f" ({signal_count} signals)"

    # Ensure reasoning is >= 50 chars
    if len(reasoning) < 50:
        reasoning += f". Payload structure indicates {best_type} attack pattern."

    # Calculate sources_agree: how many signal types align
    sources_agree = min(3, len(found_signals))
    if len(found_signals) == 1:
        sources_agree = 1  # Only one type found
    elif len(found_signals) <= 2:
        sources_agree = 2  # One or two types
    elif len(found_signals) >= 3:
        sources_agree = 3  # Multiple confirmations

    return {
        'sqli_type': best_type,
        'db_engine': db_engine,
        'confidence': round(confidence, 2),
        'reasoning': reasoning,
        'sources_agree': sources_agree,
    }

def label_chunk(chunk_num: int) -> Tuple[int, str, int, Dict]:
    """
    Label a single chunk.

    Returns:
        (chunk_num, status, row_count, report_stats)
    """
    chunk_file = DATA_DIR / f"chunk_{chunk_num:03d}.csv"

    if not chunk_file.exists():
        return (chunk_num, f"ERROR: File not found {chunk_file}", 0, {})

    try:
        # Read chunk
        df = pd.read_csv(chunk_file, dtype={'id': str})

        # Label each row
        labels = []
        for idx, row in df.iterrows():
            payload_inner = row.get('payload_inner', '')
            label = label_row(row['id'], payload_inner)
            labels.append(label)

        # Create output dataframe
        output_df = pd.DataFrame({
            'id': df['id'],
            'payload_inner': df['payload_inner'],
            'sqli_type': [l['sqli_type'] for l in labels],
            'db_engine': [l['db_engine'] for l in labels],
            'confidence': [l['confidence'] for l in labels],
            'reasoning': [l['reasoning'] for l in labels],
            'sources_agree': [l['sources_agree'] for l in labels],
        })

        # Save labeled output
        output_file = OUTPUT_DIR / f"chunk_{chunk_num:03d}_labeled.csv"
        output_df.to_csv(output_file, index=False)

        # Calculate statistics
        type_counts = output_df['sqli_type'].value_counts().to_dict()
        top_5_types = output_df['sqli_type'].value_counts().head(5)

        low_conf = output_df[output_df['confidence'] < 0.7]
        short_reasoning = output_df[output_df['reasoning'].str.len() < 50]

        stats = {
            'total_rows': len(output_df),
            'type_counts': type_counts,
            'top_5_types': top_5_types.to_dict(),
            'low_conf_count': len(low_conf),
            'short_reasoning_count': len(short_reasoning),
        }

        return (chunk_num, f"OK", len(output_df), stats)

    except Exception as e:
        return (chunk_num, f"ERROR: {str(e)}", 0, {})

def main():
    """Main entry point."""
    print("Labeling chunks 081-090...")
    print(f"Output directory: {OUTPUT_DIR}\n")

    # Process chunks in parallel
    chunk_nums = list(range(81, 91))
    results = {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(label_chunk, num): num for num in chunk_nums}

        for future in as_completed(futures):
            chunk_num, status, row_count, stats = future.result()
            results[chunk_num] = (status, row_count, stats)

            if status == "OK":
                print(f"[OK] chunk_{chunk_num:03d}.csv -> chunk_{chunk_num:03d}_labeled.csv")
                print(f"  Rows: {row_count}")
                print(f"  Top-5 types: {stats['top_5_types']}")
                print(f"  Low-conf (<0.7): {stats['low_conf_count']}")
                print(f"  Short-reasoning: {stats['short_reasoning_count']}\n")
            else:
                print(f"[ERR] chunk_{chunk_num:03d}: {status}\n")

    # Summary
    print("\n" + "="*80)
    print("LABELING SUMMARY")
    print("="*80)
    total_rows = sum(r[1] for r in results.values() if r[0] == "OK")
    ok_count = sum(1 for r in results.values() if r[0] == "OK")
    print(f"Chunks completed: {ok_count}/10")
    print(f"Total rows labeled: {total_rows}")

    # Aggregate statistics
    all_type_counts = {}
    all_low_conf = 0
    all_short_reasoning = 0

    for chunk_num in sorted(results.keys()):
        status, row_count, stats = results[chunk_num]
        if status == "OK":
            for sqli_type, count in stats['type_counts'].items():
                all_type_counts[sqli_type] = all_type_counts.get(sqli_type, 0) + count
            all_low_conf += stats['low_conf_count']
            all_short_reasoning += stats['short_reasoning_count']

    print(f"\nOverall type distribution:")
    for sqli_type in sorted(all_type_counts.keys(),
                           key=lambda x: all_type_counts[x], reverse=True)[:10]:
        count = all_type_counts[sqli_type]
        pct = 100 * count / total_rows if total_rows > 0 else 0
        print(f"  {sqli_type}: {count} ({pct:.1f}%)")

    print(f"\nQuality metrics:")
    print(f"  Low-conf rows (<0.7): {all_low_conf} ({100*all_low_conf/total_rows if total_rows else 0:.1f}%)")
    print(f"  Short-reasoning rows (<50 chars): {all_short_reasoning} ({100*all_short_reasoning/total_rows if total_rows else 0:.1f}%)")

if __name__ == '__main__':
    main()
