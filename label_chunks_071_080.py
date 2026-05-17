#!/usr/bin/env python3
"""
Label chunks 071-080 using SQLi taxonomy and evidence patterns.
Output: chunk_NNN_labeled.csv with columns:
  id, payload_inner, sqli_type, db_engine, confidence, reasoning, sources_agree
"""

import re
import csv
from pathlib import Path
from typing import Dict, Tuple, List
from concurrent.futures import ThreadPoolExecutor, as_completed

# ============================================================================
# TAXONOMY
# ============================================================================

SQLI_TYPES = {
    'rce', 'out_of_band', 'stacked_queries', 'error_based', 'time_blind',
    'heavy_query', 'union_based', 'boolean_blind', 'auth_bypass',
    'second_order', 'polyglot', 'lateral', 'benign', 'unknown'
}

DB_ENGINES = {
    'mysql', 'postgresql', 'oracle', 'mssql', 'sqlite', 'db2', 'firebird',
    'mariadb', 'generic'
}

TYPE_PRIORITY = {
    'rce': 1, 'out_of_band': 2, 'stacked_queries': 3, 'error_based': 4,
    'time_blind': 5, 'heavy_query': 6, 'union_based': 7, 'boolean_blind': 8,
    'auth_bypass': 9, 'second_order': 10, 'polyglot': 11, 'lateral': 12,
    'benign': 13, 'unknown': 14
}

# ============================================================================
# SIGNAL PATTERNS
# ============================================================================

SIGNAL_PATTERNS = {
    'rce': [
        re.compile(r'\bxp_cmdshell\s*[(\'\"]', re.I),
        re.compile(r'\bEXEC\s+xp_cmdshell', re.I),
        re.compile(r'\bcertutil\b', re.I),
        re.compile(r'\bpowershell\s+-e', re.I),
        re.compile(r'\b/bin/(bash|sh)\b', re.I),
        re.compile(r'\bcmd\s*(/c|\.exe)', re.I),
    ],
    'out_of_band': [
        re.compile(r'\bLOAD_FILE\s*\(', re.I),
        re.compile(r'\bUTL_HTTP', re.I),
        re.compile(r'\butl_inaddr\b', re.I),
        re.compile(r'\bxp_dirtree\b', re.I),
        re.compile(r'\bxp_fileexist\b', re.I),
        re.compile(r'\bOPENROWSET\s*\(', re.I),
        re.compile(r'\bdns\s*\(', re.I),
    ],
    'stacked_queries': [
        re.compile(r';\s*(CREATE|DROP|INSERT|UPDATE|DELETE|EXEC|SELECT)\b', re.I),
        re.compile(r';\s*["\']?\s*(INSERT|UPDATE|DELETE|DROP|CREATE)', re.I),
    ],
    'error_based': [
        re.compile(r'\bEXTRACTVALUE\s*\(', re.I),
        re.compile(r'\bUPDATEXML\s*\(', re.I),
        re.compile(r'\butl_inaddr\.get_host_address\s*\(', re.I),
        re.compile(r'\bctxsys\.(drithsx|ctx_ddl)', re.I),
        re.compile(r'\bexp\s*\(\s*~', re.I),
        re.compile(r'\b(geometrycollection|multipoint|multilinestring|polygon)\s*\(', re.I),
    ],
    'time_blind': [
        re.compile(r'\bSLEEP\s*\(', re.I),
        re.compile(r'\bpg_sleep\s*\(', re.I),
        re.compile(r'\bWAITFOR\s+DELAY\b', re.I),
        re.compile(r'\bBENCHMARK\s*\(', re.I),
        re.compile(r'\bRANDOMBLOB\s*\(', re.I),
    ],
    'union_based': [
        re.compile(r'\bUNION\s+(ALL\s+)?SELECT\b', re.I),
        re.compile(r'\bUNION\s*\(\s*SELECT', re.I),
    ],
    'boolean_blind': [
        re.compile(r'\bAND\s+1\s*=\s*1\b', re.I),
        re.compile(r'\bAND\s+1\s*=\s*2\b', re.I),
        re.compile(r'\bOR\s+1\s*=\s*1\b', re.I),
        re.compile(r'\bOR\s+1\s*=\s*0\b', re.I),
        re.compile(r'\bAND\s+["\']a["\']\s*=\s*["\']a["\']', re.I),
        re.compile(r'\bOR\s+["\']1["\']\s*=\s*["\']1["\']', re.I),
        re.compile(r'\bAND\s*\(\s*SELECT', re.I),
        re.compile(r'\bAND\s+ASCII\s*\(\s*SUBSTR', re.I),
    ],
    'auth_bypass': [
        re.compile(r'\badmin\s*["\'"]?\s*--\b', re.I),
        re.compile(r'\badmin\s*["\'"]?\s*#\b', re.I),
        re.compile(r'\badmin\s*["\'"]?\s*OR\b', re.I),
        re.compile(r'\badmin\s*["\'"]?\s*AND\b', re.I),
    ],
    'heavy_query': [
        re.compile(r'FROM\s+\w+\s*,\s*\w+\s*,\s*\w+', re.I),
        re.compile(r'COUNT\s*\(\s*\*\s*\)\s+FROM\s+\w+.*,.*,', re.I),
    ],
    'second_order': [
        re.compile(r'\bINSERT\s+INTO.*VALUES', re.I),
        re.compile(r'\bUPDATE\s+\w+\s+SET', re.I),
    ],
    'lateral': [
        re.compile(r'\bJOIN.*ON.*OR\s+1\s*=\s*1', re.I),
        re.compile(r'\bLATERAL\s+JOIN\b', re.I),
    ],
}

DB_EXCLUSIVE_FUNCTIONS = {
    'pg_sleep': 'postgresql',
    'WAITFOR DELAY': 'mssql',
    'utl_inaddr': 'oracle',
    'ctxsys': 'oracle',
    'randomblob': 'sqlite',
    'sqlite_master': 'sqlite',
    'rdb$': 'firebird',
    'sysibm.systables': 'db2',
}

BENIGN_KEYWORDS = {
    'UNION', 'SLEEP', 'pg_sleep', 'WAITFOR', 'BENCHMARK', 'EXTRACTVALUE',
    'UPDATEXML', 'xp_cmdshell', 'LOAD_FILE', 'utl_inaddr', 'ctxsys',
    'UTL_HTTP', 'AND 1=1', 'OR 1=1', "' OR '", "admin'", 'EXEC'
}

# ============================================================================
# LABELING LOGIC
# ============================================================================

def estimate_signal_strength(payload: str, sqli_type: str) -> str:
    """Estimate if signal is strong, medium, or none."""
    patterns = SIGNAL_PATTERNS.get(sqli_type, [])
    if not patterns:
        return 'NO_SIGNAL'
    match_count = sum(1 for p in patterns if p.search(payload))
    if match_count >= 2:
        return 'HIGH_SIGNAL'
    if match_count == 1:
        if len(payload) < 20:
            return 'MEDIUM_SIGNAL'
        return 'HIGH_SIGNAL'
    return 'NO_SIGNAL'


def check_db_exclusive_match(payload: str) -> Tuple[str, str]:
    """Check if payload contains DB-exclusive functions.
    Returns (db_engine, function_found) or ('generic', '').
    """
    payload_lower = payload.lower()
    for func, db in DB_EXCLUSIVE_FUNCTIONS.items():
        if func.lower() in payload_lower:
            return db, func
    return 'generic', ''


def detect_sqli_type(payload: str) -> Tuple[str, float, str]:
    """
    Detect SQLi type with evidence.
    Returns (sqli_type, confidence, reasoning)
    """
    payload_lower = payload.lower()

    # Check benign first
    if not re.search(r"[';\"()\-+*/=><!&|*()\]]", payload):
        if not any(kw.lower() in payload_lower for kw in BENIGN_KEYWORDS):
            return 'benign', 0.95, 'Plain text payload without SQL syntax, special chars, or SQLi keywords. Not SQL-injectable.'

    # Check each type by priority
    detected_types = []
    for sqli_type in sorted(TYPE_PRIORITY.keys(), key=lambda x: TYPE_PRIORITY[x]):
        if sqli_type in ('benign', 'unknown'):
            continue
        patterns = SIGNAL_PATTERNS.get(sqli_type, [])
        for pattern in patterns:
            if pattern.search(payload):
                strength = estimate_signal_strength(payload, sqli_type)
                if strength == 'HIGH_SIGNAL':
                    conf = 0.95
                elif strength == 'MEDIUM_SIGNAL':
                    conf = 0.80
                else:
                    conf = 0.70
                detected_types.append((TYPE_PRIORITY[sqli_type], sqli_type, conf, pattern.pattern))
                break

    if detected_types:
        # Take highest priority (lowest number)
        detected_types.sort()
        priority, sqli_type, conf, pattern = detected_types[0]
        # Make reasoning more descriptive
        signal_name = pattern.split(r'\b')[0] if '\\b' in pattern else pattern[:30]
        return sqli_type, conf, f'Signal confirmed: {pattern[:40]} — specific indicator of {sqli_type} SQLi vulnerability'

    # Check for benign with SQL-like structure
    sql_keywords = ['select', 'insert', 'update', 'delete', 'drop', 'create',
                    'from', 'where', 'and', 'or', 'join', 'union']
    if any(kw in payload_lower for kw in sql_keywords):
        return 'boolean_blind', 0.60, 'SQL statement structure detected with generic boolean logic pattern; suggests conditional injection'

    return 'unknown', 0.50, 'Payload structure ambiguous; insufficient markers to classify as specific SQLi type with confidence'


def determine_db_engine(payload: str, sqli_type: str) -> str:
    """Determine DB engine from signals."""
    db, func = check_db_exclusive_match(payload)
    if db != 'generic':
        return db

    # If no exclusive function, check time_blind functions
    payload_lower = payload.lower()
    if sqli_type == 'time_blind':
        if 'pg_sleep' in payload_lower:
            return 'postgresql'
        if 'waitfor delay' in payload_lower:
            return 'mssql'
        if 'randomblob' in payload_lower:
            return 'sqlite'
        if 'sleep' in payload_lower or 'benchmark' in payload_lower:
            return 'mysql'

    return 'generic'


def count_sources_agree(row: Dict) -> int:
    """
    Count how many sources agree with the label.
    Based on suggested_type, a_type, c_type if available.
    """
    sources_agree = 0
    detected_type = row.get('detected_type', '')

    if row.get('suggested_type', '').strip() == detected_type and detected_type:
        sources_agree += 1
    if row.get('a_type', '').strip() == detected_type and detected_type:
        sources_agree += 1
    if row.get('c_type', '').strip() == detected_type and detected_type:
        sources_agree += 1

    return sources_agree


def label_row(row: Dict) -> Dict:
    """Label a single row."""
    payload_inner = row.get('payload_inner', row.get('payload_norm', ''))

    sqli_type, confidence, reasoning = detect_sqli_type(payload_inner)
    db_engine = determine_db_engine(payload_inner, sqli_type)

    # Store detected type for sources_agree calculation
    row['detected_type'] = sqli_type
    sources_agree = count_sources_agree(row)

    return {
        'id': row.get('id', ''),
        'payload_inner': payload_inner,
        'sqli_type': sqli_type,
        'db_engine': db_engine,
        'confidence': f'{confidence:.2f}',
        'reasoning': reasoning,
        'sources_agree': sources_agree
    }


def process_chunk(chunk_num: int) -> Tuple[int, int, dict]:
    """Process a single chunk file."""
    chunk_path = Path(f'C:\\Users\\Admin\\Documents\\GAN_SQLi\\Asset\\LabelData\\_chunks\\chunk_{chunk_num:03d}.csv')
    output_path = Path(f'C:\\Users\\Admin\\Documents\\GAN_SQLi\\Asset\\LabelData\\_chunks\\chunk_{chunk_num:03d}_labeled.csv')

    if not chunk_path.exists():
        return chunk_num, 0, {'error': 'File not found'}

    rows = []
    labeled_rows = []
    low_conf_rows = []
    short_reasoning_rows = []
    type_counts = {}

    try:
        with open(chunk_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row_idx, row in enumerate(reader):
                rows.append(row)
                labeled_row = label_row(row)
                labeled_rows.append(labeled_row)

                # Track metrics
                sqli_type = labeled_row['sqli_type']
                type_counts[sqli_type] = type_counts.get(sqli_type, 0) + 1

                conf = float(labeled_row['confidence'])
                if conf < 0.70:
                    low_conf_rows.append((row.get('id', ''), sqli_type, conf))

                if len(labeled_row['reasoning']) < 50:
                    short_reasoning_rows.append((row.get('id', ''), labeled_row['reasoning']))

        # Write labeled output
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'id', 'payload_inner', 'sqli_type', 'db_engine', 'confidence', 'reasoning', 'sources_agree'
            ])
            writer.writeheader()
            writer.writerows(labeled_rows)

        # Generate statistics
        top5_types = sorted(type_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        stats = {
            'chunk_num': chunk_num,
            'total_rows': len(rows),
            'top5_types': top5_types,
            'low_conf_count': len(low_conf_rows),
            'low_conf_samples': low_conf_rows[:3],
            'short_reasoning_count': len(short_reasoning_rows),
            'short_reasoning_samples': short_reasoning_rows[:3],
        }

        return chunk_num, len(rows), stats

    except Exception as e:
        return chunk_num, 0, {'error': str(e)}


# ============================================================================
# MAIN
# ============================================================================

def main():
    print('Starting parallel labeling of chunks 071-080...')
    print('=' * 80)

    all_stats = {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(process_chunk, i): i for i in range(71, 81)}

        for future in as_completed(futures):
            chunk_num, rows_count, stats = future.result()
            all_stats[chunk_num] = stats

            print(f'\nChunk {chunk_num:03d}:')
            if 'error' in stats:
                print(f'  ERROR: {stats["error"]}')
            else:
                print(f'  Total rows: {stats["total_rows"]}')
                print(f'  Top 5 types: {stats["top5_types"]}')
                print(f'  Low confidence rows: {stats["low_conf_count"]}')
                if stats['low_conf_samples']:
                    for row_id, typ, conf in stats['low_conf_samples']:
                        print(f'    - ID {row_id}: {typ} (conf={conf:.2f})')
                print(f'  Short reasoning rows: {stats["short_reasoning_count"]}')
                if stats['short_reasoning_samples']:
                    for row_id, reason in stats['short_reasoning_samples']:
                        print(f'    - ID {row_id}: {reason[:40]}...')

    print('\n' + '=' * 80)
    print('Labeling complete. Output files:')
    for i in range(71, 81):
        print(f'  C:\\Users\\Admin\\Documents\\GAN_SQLi\\Asset\\LabelData\\_chunks\\chunk_{i:03d}_labeled.csv')


if __name__ == '__main__':
    main()
