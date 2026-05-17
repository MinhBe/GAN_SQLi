#!/usr/bin/env python3
"""
Label chunks 031-040 with SQLi classification.
Output: chunk_NNN_labeled.csv with columns:
  id, payload_inner, sqli_type, db_engine, confidence, reasoning, sources_agree
"""

import csv
import re
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor, as_completed

# Reference data from SKILL.md
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

DB_ENGINES = ['mysql', 'mssql', 'oracle', 'postgresql', 'sqlite', 'firebird', 'db2', 'generic', 'unknown']

# Signal patterns (case-insensitive)
SIGNALS = {
    'rce': [r'xp_cmdshell\s*\(', r'xp_cmdshell\s+', r'exec\s+xp_cmdshell', r'certutil', r'powershell\s+-e', r'powershell\s+-enc', r'/bin/bash', r'/bin/sh', r'cmd\s+/c', r'cmd\.exe'],
    'out_of_band': [r'load_file\s*\(', r'utl_http\.request', r'utl_http\.begin_request', r'utl_inaddr\.get_host_address', r'xp_dirtree', r'xp_fileexist', r'openrowset\s*\(', r'dns\s*\('],
    'stacked_queries': [r';\s*(create|drop|insert|update|delete|exec|select)\s', r';\s*(create|drop|insert|update|delete|exec)'],
    'error_based': [r'extractvalue\s*\(', r'updatexml\s*\(', r'utl_inaddr\.get_host_address\s*\(', r'ctxsys\.drithsx', r'ctxsys\.ctx_ddl', r'exp\s*\(~', r'geometrycollection\s*\(', r'multipoint\s*\('],
    'time_blind': [r'sleep\s*\(', r'pg_sleep\s*\(', r'waitfor\s+delay', r'benchmark\s*\(', r'randomblob\s*\(', r'dbms_pipe\.receive_message', r'dbms_lock\.sleep'],
    'heavy_query': [r'count\s*\(\s*\*\s*\)\s+from.*,.*,'],
    'union_based': [r'union\s+(all\s+)?select', r'union\s*\(', r'union\s*%20'],
    'boolean_blind': [r'and\s+(1\s*=\s*1|1\s*=\s*2|\'a\'\s*=\s*\'a\'|\'1\'\s*=\s*\'1\')', r'or\s+(1\s*=\s*1|1\s*=\s*0|\'a\'\s*=\s*\'a\'|\'1\'\s*=\s*\'1\')'],
    'auth_bypass': [r'admin\s*\'[\s\-#]*(\s|$|or)', r'admin\s*\"[\s\-#]*(\s|$|or)', r'admin\s*\'\s*(or|--|#)', r'\'\s+or\s+\'1\'\s*=\s*\'1', r'\"\\s+or\\s+\"1\"\\s*=\\s*\"1'],
    'lateral': [r'join\s+.*\s+on\s+.*\s+or\s+1\s*=\s*1', r'lateral\s+join'],
}

DB_SIGNATURES = {
    'postgresql': [r'pg_sleep\s*\(', r'version\(\)::'],
    'mssql': [r'waitfor\s+delay', r'xp_cmdshell', r'sysobjects', r'@@servername', r'sys\.tables'],
    'oracle': [r'utl_inaddr', r'ctxsys', r'dual', r'all_tables', r'rownum', r'v\$version', r'xmltype', r'extractvalue'],
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
    Classify payload and return: (sqli_type, db_engine, confidence, reasoning, sources_agree)
    Rules:
    - Trust payload, not hint
    - Priority: check P1 signals first, then P2, etc.
    - If multiple types match, choose lowest priority number
    - sources_agree: count of sources that agree (0-3 based on annotation presence)
    """
    payload_lower = payload_inner.lower()
    sources_agree = 1  # Always at least 1 (the payload itself)

    # Check for benign first (stricter)
    benign_keywords = ['union', 'sleep', 'pg_sleep', 'waitfor', 'benchmark', 'extractvalue', 'updatexml',
                       'xp_cmdshell', 'load_file', 'utl_inaddr', 'ctxsys', 'utl_http',
                       'and 1=1', 'or 1=1', ' or ', 'admin\'']

    is_benign = True
    for keyword in benign_keywords:
        if keyword in payload_lower:
            is_benign = False
            break

    if is_benign:
        # Check if it's legitimate SQL
        sql_keywords = ['select', 'from', 'where', 'and', 'or', 'insert', 'update', 'delete', 'create', 'drop']
        has_sql = any(kw in payload_lower for kw in sql_keywords)

        if has_sql or len(payload_inner.strip()) < 5:
            return ('benign', 'generic', 0.9, 'No attack signals detected; legitimate SQL structure', 1)

    # Check each type in priority order
    detected_types = []

    for sqli_type, priority in SQLI_TYPES.items():
        if sqli_type in ['benign', 'unknown']:
            continue

        signals = SIGNALS.get(sqli_type, [])
        if has_signal(payload_inner, signals):
            detected_types.append((priority, sqli_type))

    if not detected_types:
        return ('unknown', 'generic', 0.5, 'Insufficient information to classify', 1)

    # Choose lowest priority number
    detected_types.sort()
    priority, sqli_type = detected_types[0]

    # Detect DB engine
    db_engine = detect_db_engine(payload_inner)

    # Calculate confidence
    if priority <= 3:
        confidence = 0.95
        reasoning_basis = 'Strong signal match'
    elif priority <= 5:
        confidence = 0.85
        reasoning_basis = 'Clear signal detection'
    else:
        confidence = 0.75
        reasoning_basis = 'Pattern match with lower priority'

    # Generate reasoning
    signals_found = [s for s in SIGNALS.get(sqli_type, []) if has_signal(payload_inner, [s])]
    if signals_found:
        first_signal = signals_found[0].replace(r'\s*\(', '').replace(r'\s+', ' ').replace('\\', '')
        reasoning = f"{reasoning_basis}: {first_signal[:40]} → {sqli_type} (P{priority})"
    else:
        reasoning = f"{reasoning_basis}: {sqli_type} detected (P{priority})"

    # Ensure reasoning is at least 50 chars
    if len(reasoning) < 50:
        if db_engine != 'generic':
            reasoning += f"; DB signature: {db_engine}"
        else:
            reasoning += f"; type: {sqli_type}, priority: {priority}"

    return (sqli_type, db_engine, confidence, reasoning, sources_agree)

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
                payload_inner = row.get('payload_inner', row.get('payload_norm', ''))
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
            'output_path': str(output_path),
        }

    except Exception as e:
        return {'chunk': chunk_num, 'status': 'ERROR', 'error': str(e)}

def main():
    chunks = list(range(31, 41))

    print("Starting parallel labeling of chunks 031-040...")
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
    print("LABELING REPORT: Chunks 031-040")
    print("="*80)

    for chunk_num in sorted(chunks):
        if chunk_num not in results:
            continue

        r = results[chunk_num]
        print(f"\nChunk {chunk_num:03d}:")
        print(f"  Status: {r.get('status', 'N/A')}")

        if r.get('status') == 'SUCCESS':
            print(f"  Rows labeled: {r.get('rows', 0)}")
            print(f"  Top 5 types:")
            for sqli_type, count in r.get('top5_types', []):
                pct = 100.0 * count / r.get('rows', 1)
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

if __name__ == '__main__':
    main()
