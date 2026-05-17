#!/usr/bin/env python3
"""
Label chunks 031-040 with SQLi classification (v2).
Output: chunk_NNN_labeled.csv with columns:
  id, payload_inner, sqli_type, db_engine, confidence, reasoning, sources_agree

Rules:
- Trust ONLY the payload_inner field (delexicalized)
- DO NOT trust sqli_type/db_engine hints from original CSV
- Priority: check signals from P1 (RCE) down to P14 (unknown)
- If multiple types match, choose LOWEST priority number
- sources_agree: always 1 (single payload source of truth)
- confidence thresholds:
  - P1-2 (RCE, OOB): 0.95
  - P3-5 (stacked, error, time): 0.85
  - P6-9 (heavy, union, bool, auth): 0.75
  - P10+ (lower priority): 0.65
  - unknown: 0.50
"""

import csv
import re
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

# Priority mapping (lower = higher priority)
SQLI_TYPES = {
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

# Signal patterns (case-insensitive)
SIGNALS = {
    'rce': [
        r'xp_cmdshell\s*\(',
        r'xp_cmdshell\s+',
        r'exec\s+xp_cmdshell',
        r'certutil',
        r'powershell\s+-e',
        r'powershell\s+-enc',
        r'/bin/bash',
        r'/bin/sh',
        r'cmd\s+/c',
        r'cmd\.exe',
    ],
    'out_of_band': [
        r'load_file\s*\(',
        r'utl_http\.request',
        r'utl_http\.begin_request',
        r'utl_inaddr\.get_host_address',
        r'xp_dirtree',
        r'xp_fileexist',
        r'openrowset\s*\(',
        r'dns\s*\(',
    ],
    'stacked_queries': [
        r';\s*(create|drop|insert|update|delete|exec|select)\s',
    ],
    'error_based': [
        r'extractvalue\s*\(',
        r'updatexml\s*\(',
        r'utl_inaddr\.get_host_address\s*\(',
        r'ctxsys\.drithsx',
        r'ctxsys\.ctx_ddl',
        r'exp\s*\(~',
        r'geometrycollection\s*\(',
        r'multipoint\s*\(',
    ],
    'time_blind': [
        r'sleep\s*\(',
        r'pg_sleep\s*\(',
        r'waitfor\s+delay',
        r'benchmark\s*\(',
        r'randomblob\s*\(',
        r'dbms_pipe\.receive_message',
        r'dbms_lock\.sleep',
    ],
    'heavy_query': [
        r'count\s*\(\s*\*\s*\)\s+from\s+[^,]+,\s*[^,]+,\s*[^,]+',
    ],
    'union_based': [
        r'union\s+(all\s+)?select',
        r'union\s*\(',
    ],
    'boolean_blind': [
        r'and\s+(?:1\s*=\s*1|1\s*=\s*2|\'a\'\s*=\s*\'a\'|\'1\'\s*=\s*\'1\'|\'a\'\s*=\s*\'b\')',
        r'or\s+(?:1\s*=\s*1|1\s*=\s*0|\'a\'\s*=\s*\'a\'|\'1\'\s*=\s*\'1\')',
    ],
    'auth_bypass': [
        r'admin\s*[\'\"]\s*(?:or|--|#|;)',
        r'admin\s*[\'\"]\s*$',
    ],
    'lateral': [
        r'join\s+.*\s+on\s+.*\s+or\s+1\s*=\s*1',
        r'lateral\s+join',
    ],
}

DB_SIGNATURES = {
    'postgresql': [r'pg_sleep\s*\(', r'version\(\)::'],
    'mssql': [r'waitfor\s+delay', r'xp_cmdshell', r'sysobjects', r'@@servername', r'sys\.tables'],
    'oracle': [r'utl_inaddr', r'ctxsys', r'dual', r'all_tables', r'rownum', r'v\$version', r'xmltype'],
    'mysql': [r'@@version', r'sleep\s*\(', r'load_file\s*\(', r'information_schema'],
    'sqlite': [r'sqlite_version\s*\(', r'sqlite_master', r'randomblob\s*\(', r'sqlite_sequence'],
    'firebird': [r'rdb\$functions', r'rdb\$relations'],
    'db2': [r'sysibm\.systables', r'syscat\.tables'],
}

def has_signal(payload, signal_list):
    """Check if payload has any of the signals."""
    payload_lower = payload.lower()
    for signal in signal_list:
        if re.search(signal, payload_lower):
            return True
    return False

def get_all_matching_signals(payload, signal_pattern_list):
    """Get all signals that match in payload."""
    payload_lower = payload.lower()
    matches = []
    for signal in signal_pattern_list:
        if re.search(signal, payload_lower):
            matches.append(signal)
    return matches

def detect_db_engine(payload):
    """Detect DB engine from signatures."""
    payload_lower = payload.lower()
    scores = {}

    for db, sigs in DB_SIGNATURES.items():
        count = sum(1 for sig in sigs if re.search(sig, payload_lower))
        if count > 0:
            scores[db] = count

    if scores:
        return max(scores, key=scores.get)
    return 'generic'

def classify_sqli(payload_inner):
    """
    Classify payload according to priority order.
    Returns: (sqli_type, db_engine, confidence, reasoning, sources_agree=1)
    """
    if not payload_inner or len(payload_inner.strip()) == 0:
        return ('unknown', 'generic', 0.5, 'Empty payload', 1)

    payload_lower = payload_inner.lower()

    # Phase 1: Check each type by priority order
    detected = []

    for sqli_type in ['rce', 'out_of_band', 'stacked_queries', 'error_based', 'time_blind',
                      'heavy_query', 'union_based', 'boolean_blind', 'auth_bypass', 'lateral']:
        signals = SIGNALS.get(sqli_type, [])
        if has_signal(payload_inner, signals):
            priority = SQLI_TYPES[sqli_type]
            detected.append((priority, sqli_type, signals))

    # If we found attack patterns, use the highest priority (lowest number)
    if detected:
        detected.sort()
        priority, sqli_type, signal_list = detected[0]

        # Detect DB
        db_engine = detect_db_engine(payload_inner)

        # Set confidence based on priority
        if priority <= 2:
            confidence = 0.95
        elif priority <= 5:
            confidence = 0.85
        else:
            confidence = 0.75

        # Generate reasoning
        matching_signals = get_all_matching_signals(payload_inner, signal_list)
        if matching_signals:
            # Extract first matched signal name
            sig_str = matching_signals[0]
            # Clean up regex patterns
            sig_display = sig_str.replace(r'\s*\(', '').replace(r'\s+', ' ').replace('\\', '')[:30]

            reasoning = f"Signal match: {sig_display} → {sqli_type} (P{priority})"
        else:
            reasoning = f"Pattern detected: {sqli_type} (P{priority})"

        if len(reasoning) < 50:
            if db_engine != 'generic':
                reasoning += f"; DB signature: {db_engine}"
            else:
                reasoning += f"; confidence: {confidence:.2f}"

        return (sqli_type, db_engine, confidence, reasoning, 1)

    # Phase 2: No attack signals found - check if benign or unknown
    # Benign = legitimate SQL with common keywords but NO attack intent
    sql_keywords = ['select', 'from', 'where', 'and', 'or', 'insert', 'update', 'delete', 'create', 'drop']
    has_sql = any(kw in payload_lower for kw in sql_keywords)

    if has_sql and len(payload_inner) > 5:
        return ('benign', 'generic', 0.90, 'No attack signals detected; legitimate SQL structure', 1)

    # Unknown = too short or unclear
    return ('unknown', 'generic', 0.50, 'Insufficient information to classify', 1)

def label_chunk(chunk_num):
    """Label a single chunk."""
    input_path = Path(f'C:\\Users\\Admin\\Documents\\GAN_SQLi\\Asset\\LabelData\\_chunks\\chunk_{chunk_num:03d}.csv')
    output_path = Path(f'C:\\Users\\Admin\\Documents\\GAN_SQLi\\Asset\\LabelData\\_chunks\\chunk_{chunk_num:03d}_labeled.csv')

    if not input_path.exists():
        return {'chunk': chunk_num, 'status': 'NOT_FOUND', 'rows': 0}

    results = []
    low_conf_rows = []
    short_reasoning_rows = []
    type_counts = {}

    try:
        with open(input_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            if not reader.fieldnames:
                return {'chunk': chunk_num, 'status': 'EMPTY', 'rows': 0}

            for row in reader:
                # Use payload_inner if available, else fallback to payload_norm
                payload_inner = row.get('payload_inner', '')
                if not payload_inner:
                    payload_inner = row.get('payload_norm', '')

                if not payload_inner:
                    continue

                sqli_type, db_engine, confidence, reasoning, sources_agree = classify_sqli(payload_inner)

                results.append({
                    'id': row.get('id', ''),
                    'payload_inner': payload_inner,
                    'sqli_type': sqli_type,
                    'db_engine': db_engine,
                    'confidence': f"{confidence:.2f}",
                    'reasoning': reasoning,
                    'sources_agree': sources_agree,
                })

                # Track stats
                type_counts[sqli_type] = type_counts.get(sqli_type, 0) + 1

                if confidence < 0.7:
                    low_conf_rows.append({'id': row.get('id', ''), 'type': sqli_type, 'conf': confidence})

                if len(reasoning) < 50:
                    short_reasoning_rows.append({'id': row.get('id', ''), 'reasoning_len': len(reasoning)})

        # Write output
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=['id', 'payload_inner', 'sqli_type', 'db_engine', 'confidence', 'reasoning', 'sources_agree'])
            writer.writeheader()
            writer.writerows(results)

        # Get top 5 types
        top5 = sorted(type_counts.items(), key=lambda x: -x[1])[:5]

        return {
            'chunk': chunk_num,
            'status': 'SUCCESS',
            'rows': len(results),
            'top5_types': top5,
            'low_conf_count': len(low_conf_rows),
            'short_reasoning_count': len(short_reasoning_rows),
            'low_conf_samples': low_conf_rows[:3],
            'short_reasoning_samples': short_reasoning_rows[:3],
            'type_distribution': type_counts,
        }

    except Exception as e:
        return {'chunk': chunk_num, 'status': 'ERROR', 'error': str(e)}

def main():
    chunks = list(range(31, 41))

    print("Starting parallel labeling of chunks 031-040 (v2)...")
    results = {}

    with ProcessPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(label_chunk, c): c for c in chunks}

        for future in as_completed(futures):
            chunk_num = futures[future]
            try:
                result = future.result()
                results[chunk_num] = result

                status = result.get('status', 'UNKNOWN')
                if status == 'SUCCESS':
                    rows = result.get('rows', 0)
                    print(f"[OK] chunk_{chunk_num:03d}: {rows} rows labeled")
                else:
                    print(f"[ERR] chunk_{chunk_num:03d}: {status}")

            except Exception as e:
                print(f"[ERR] chunk_{chunk_num:03d}: Exception - {str(e)}")

    # Generate report
    print("\n" + "="*80)
    print("LABELING REPORT: Chunks 031-040 (v2)")
    print("="*80)

    total_rows = 0
    global_type_counts = {}

    for chunk_num in sorted(chunks):
        if chunk_num not in results:
            continue

        r = results[chunk_num]
        print(f"\nChunk {chunk_num:03d}:")
        print(f"  Status: {r.get('status', 'N/A')}")

        if r.get('status') == 'SUCCESS':
            rows = r.get('rows', 0)
            total_rows += rows
            print(f"  Rows labeled: {rows}")

            # Update global counts
            for sqli_type, count in r.get('type_distribution', {}).items():
                global_type_counts[sqli_type] = global_type_counts.get(sqli_type, 0) + count

            print(f"  Top 5 types:")
            for sqli_type, count in r.get('top5_types', []):
                pct = 100.0 * count / rows
                print(f"    - {sqli_type}: {count} ({pct:.1f}%)")

            low_conf = r.get('low_conf_count', 0)
            if low_conf > 0:
                print(f"  Low confidence rows (<0.7): {low_conf}")
                for sample in r.get('low_conf_samples', []):
                    print(f"    - ID {sample['id']}: {sample['type']} ({sample['conf']:.2f})")

            short_reasoning = r.get('short_reasoning_count', 0)
            if short_reasoning > 0:
                print(f"  Short reasoning rows (<50 chars): {short_reasoning}")
                for sample in r.get('short_reasoning_samples', []):
                    print(f"    - ID {sample['id']}: {sample['reasoning_len']} chars")

        elif r.get('status') == 'ERROR':
            print(f"  Error: {r.get('error', 'Unknown')}")

    # Summary
    print("\n" + "="*80)
    print("GLOBAL SUMMARY (All 10 chunks)")
    print("="*80)
    print(f"Total rows labeled: {total_rows}")
    print(f"Distribution:")
    for sqli_type in sorted(global_type_counts.keys()):
        count = global_type_counts[sqli_type]
        pct = 100.0 * count / total_rows
        print(f"  {sqli_type}: {count} ({pct:.1f}%)")

if __name__ == '__main__':
    main()
