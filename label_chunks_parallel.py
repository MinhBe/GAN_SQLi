#!/usr/bin/env python3
"""
SQLi Labeler — Label chunks 041-050 in parallel
Follows sqli-labeler SKILL.md + taxonomy.md guidelines
"""

import csv
import re
import sys
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Dict, List, Tuple
from dataclasses import dataclass

CHUNK_DIR = Path("C:/Users/Admin/Documents/GAN_SQLi/Asset/LabelData/_chunks")
CHUNKS = list(range(41, 51))  # 041 to 050

# Taxonomy definitions
SQLI_TYPES_PRIORITY = {
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

DB_ENGINES = {
    'mysql', 'mssql', 'oracle', 'postgresql', 'sqlite',
    'firebird', 'db2', 'generic', 'unknown'
}

# Signal definitions by type
SIGNALS = {
    'rce': {
        'keywords': ['xp_cmdshell', 'certutil', 'powershell', '/bin/bash', 'cmd.exe'],
        'patterns': [r'xp_cmdshell\s*\(', r'certutil\s', r'powershell\s*-e', r'/bin/bash\s*-c', r'cmd\s*/c']
    },
    'out_of_band': {
        'keywords': ['load_file', 'utl_http', 'utl_inaddr', 'xp_dirtree', 'openrowset', 'dns'],
        'patterns': [r'load_file\s*\(', r'utl_http', r'utl_inaddr', r'xp_dirtree', r'openrowset']
    },
    'stacked_queries': {
        'keywords': [';'],
        'patterns': [r';\s*(create|drop|insert|update|delete|exec|select)',]
    },
    'error_based': {
        'keywords': ['extractvalue', 'updatexml', 'utl_inaddr.get_host_address', 'ctxsys.drithsx'],
        'patterns': [r'extractvalue\s*\(', r'updatexml\s*\(', r'utl_inaddr\.get_host_address', r'ctxsys\.drithsx']
    },
    'time_blind': {
        'keywords': ['sleep(', 'pg_sleep(', 'waitfor delay', 'benchmark(', 'randomblob('],
        'patterns': [r'sleep\s*\(\d+', r'pg_sleep\s*\(', r'waitfor\s+delay', r'benchmark\s*\(', r'randomblob\s*\(']
    },
    'heavy_query': {
        'keywords': ['count(*)', 'cross', 'from', 'where'],
        'patterns': [r'count\s*\(\s*\*\s*\)\s+from\s+\w+\s*,\s*\w+\s*,\s*\w+']
    },
    'union_based': {
        'keywords': ['union', 'select'],
        'patterns': [r'union\s+(all\s+)?select']
    },
    'boolean_blind': {
        'keywords': ['and 1=1', 'or 1=1', "and 'a'='a'", "or '1'='1'"],
        'patterns': [r"(and|or)\s+1\s*=\s*1", r"(and|or)\s+'[^']*'\s*=\s*'[^']*'"]
    },
    'auth_bypass': {
        'keywords': ["admin'", "' or '", "'--", "'#"],
        'patterns': [r"admin\s*'", r"' or '", r"'--", r"'#"]
    },
    'benign': {
        'keywords': [],
        'patterns': []
    },
    'unknown': {
        'keywords': [],
        'patterns': []
    }
}

# DB Engine signatures
DB_SIGNATURES = {
    'mysql': ['@@version', 'sleep(', 'load_file(', 'information_schema', '/*!'],
    'mssql': ['waitfor delay', 'sysobjects', 'xp_cmdshell', '@@servername', 'sys.tables'],
    'oracle': ['utl_inaddr', 'ctxsys.drithsx', 'dual', 'all_tables', 'rownum', 'v$version'],
    'postgresql': ['pg_sleep(', 'version()::', '::', 'pg_catalog', 'pg_tables'],
    'sqlite': ['sqlite_version(', 'sqlite_master', 'randomblob(', 'sqlite_sequence'],
    'firebird': ['rdb$functions', 'rdb$relations'],
    'db2': ['sysibm.systables', 'syscat.tables'],
}

@dataclass
class LabelResult:
    sqli_type: str
    db_engine: str
    confidence: float
    reasoning: str
    sources_agree: int

def has_signal(payload: str, signals: Dict) -> Tuple[bool, List[str]]:
    """Check if payload matches any signal pattern. Returns (match, matched_signals)."""
    payload_lower = payload.lower()
    matched = []

    # Check keywords
    for keyword in signals.get('keywords', []):
        if keyword.lower() in payload_lower:
            matched.append(keyword)

    # Check regex patterns
    for pattern in signals.get('patterns', []):
        if re.search(pattern, payload_lower):
            matched.append(pattern)

    return len(matched) > 0, matched

def count_comma_separated(payload: str) -> int:
    """Count comma-separated tables in FROM clause for heavy_query detection."""
    match = re.search(r'from\s+([^;]+?)(?:where|$)', payload, re.IGNORECASE)
    if match:
        tables = match.group(1).split(',')
        return len([t for t in tables if t.strip()])
    return 0

def classify_payload(payload_norm: str) -> LabelResult:
    """Classify payload according to priority chain."""

    if not payload_norm or not isinstance(payload_norm, str):
        return LabelResult('unknown', 'unknown', 0.50, 'Empty or non-string payload', 0)

    payload = payload_norm.strip()
    payload_lower = payload.lower()

    # Check for benign first
    attack_keywords = [
        'union', 'select', 'sleep(', 'pg_sleep', 'waitfor', 'extractvalue',
        'updatexml', 'xp_cmdshell', 'load_file', 'utl_inaddr', 'and', 'or',
        'admin', ';', 'drop', 'insert', 'delete', 'update', 'exec'
    ]

    has_attack = any(kw in payload_lower for kw in attack_keywords)

    if not has_attack and len(payload) > 2:
        return LabelResult(
            'benign', 'generic', 0.85,
            'Plain text without SQL injection keywords or patterns detected',
            1
        )

    # Priority chain (1-12)
    for sqli_type in ['rce', 'out_of_band', 'stacked_queries', 'error_based',
                      'time_blind', 'heavy_query', 'union_based', 'boolean_blind',
                      'auth_bypass', 'second_order', 'polyglot', 'lateral']:

        has_match, matched_signals = has_signal(payload, SIGNALS[sqli_type])

        if not has_match:
            continue

        # Special case: heavy_query requires ≥3 tables
        if sqli_type == 'heavy_query':
            table_count = count_comma_separated(payload)
            if table_count < 3:
                continue

        # Special case: auth_bypass requires admin prefix or context
        if sqli_type == 'auth_bypass':
            if 'admin' not in payload_lower and 'login' not in payload_lower:
                continue

        # Detect DB engine
        db_engine = 'generic'
        confidence = 0.95

        for db, sigs in DB_SIGNATURES.items():
            for sig in sigs:
                if sig.lower() in payload_lower:
                    db_engine = db
                    break
            if db_engine != 'generic':
                break

        # Adjust confidence based on payload length and obfuscation
        if len(payload) < 20:
            confidence = 0.80
        elif re.search(r'0x[0-9a-f]+|/\*+\*/', payload_lower):
            confidence = 0.70

        # Build reasoning
        signal_str = ', '.join(matched_signals[:2]) if matched_signals else sqli_type
        reasoning = f"{signal_str} → {sqli_type} detection"

        if len(reasoning) < 50:
            reasoning += f" with {db_engine} database signature" if db_engine != 'generic' else ""

        return LabelResult(
            sqli_type=sqli_type,
            db_engine=db_engine,
            confidence=confidence,
            reasoning=reasoning,
            sources_agree=2
        )

    # Default to benign or unknown
    if has_attack:
        return LabelResult(
            'unknown', 'unknown', 0.50,
            'Potential injection pattern detected but insufficient signal for categorization',
            1
        )

    return LabelResult(
        'benign', 'unknown', 0.70,
        'Insufficient context for classification — single token or ambiguous payload',
        0
    )

def label_chunk(chunk_num: int) -> Tuple[int, str, int, int, Dict]:
    """Label a single chunk and return stats."""
    chunk_file = CHUNK_DIR / f"chunk_{chunk_num:03d}.csv"

    if not chunk_file.exists():
        return chunk_num, f"chunk_{chunk_num:03d}_labeled.csv", 0, 0, {}

    rows = []
    stats = {
        'total': 0,
        'by_type': {},
        'low_conf': [],
        'short_reasoning': [],
    }

    with open(chunk_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        headers = reader.fieldnames

        for row_idx, row in enumerate(reader):
            stats['total'] += 1
            payload = row.get('payload_inner', row.get('payload_norm', ''))

            result = classify_payload(payload)

            # Update stats
            stats['by_type'][result.sqli_type] = stats['by_type'].get(result.sqli_type, 0) + 1

            if result.confidence < 0.7:
                stats['low_conf'].append((row_idx, payload[:50], result.confidence))

            if len(result.reasoning) < 50:
                stats['short_reasoning'].append((row_idx, result.reasoning))

            # Build output row
            output_row = {
                'id': row.get('id', ''),
                'payload_inner': payload,
                'sqli_type': result.sqli_type,
                'db_engine': result.db_engine,
                'confidence': f"{result.confidence:.2f}",
                'reasoning': result.reasoning,
                'sources_agree': result.sources_agree,
            }
            rows.append(output_row)

    # Write labeled chunk
    output_file = CHUNK_DIR / f"chunk_{chunk_num:03d}_labeled.csv"
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'payload_inner', 'sqli_type', 'db_engine', 'confidence', 'reasoning', 'sources_agree'])
        writer.writeheader()
        writer.writerows(rows)

    return chunk_num, f"chunk_{chunk_num:03d}_labeled.csv", stats['total'], len(stats['low_conf']), stats

def main():
    print("SQLi Chunk Labeler — Processing chunks 041-050 in parallel")
    print(f"Target directory: {CHUNK_DIR}")
    print(f"Chunks: {CHUNKS}")
    print()

    all_stats = {}

    with ThreadPoolExecutor(max_workers=10) as executor:
        futures = {executor.submit(label_chunk, c): c for c in CHUNKS}

        for future in as_completed(futures):
            chunk_num, output_file, total, low_conf, stats = future.result()
            all_stats[chunk_num] = stats

            # Top-5 types
            top5 = sorted(stats['by_type'].items(), key=lambda x: -x[1])[:5]
            top5_str = ', '.join([f"{t[0]}({t[1]})" for t in top5])

            print(f"[chunk_{chunk_num:03d}] {total} rows | Low-conf: {low_conf} | Top-5: {top5_str}")
            if stats['short_reasoning']:
                print(f"  └─ Short reasoning: {len(stats['short_reasoning'])} rows")

    # Summary
    print("\n" + "="*80)
    print("SUMMARY — All chunks labeled")
    print("="*80)

    overall_type_dist = {}
    total_rows = 0
    total_low_conf = 0
    total_short = 0

    for chunk_num in sorted(all_stats.keys()):
        stats = all_stats[chunk_num]
        total_rows += stats['total']
        total_low_conf += len(stats['low_conf'])
        total_short += len(stats['short_reasoning'])

        for sqli_type, count in stats['by_type'].items():
            overall_type_dist[sqli_type] = overall_type_dist.get(sqli_type, 0) + count

    print(f"\nTotal rows labeled: {total_rows}")
    print(f"Low-confidence rows (< 0.7): {total_low_conf} ({100*total_low_conf/total_rows:.1f}%)")
    print(f"Short reasoning (< 50 chars): {total_short} ({100*total_short/total_rows:.1f}%)")

    print(f"\nOverall distribution (top 10):")
    for sqli_type, count in sorted(overall_type_dist.items(), key=lambda x: -x[1])[:10]:
        pct = 100 * count / total_rows
        print(f"  {sqli_type:20s}: {count:6d} ({pct:5.1f}%)")

    print(f"\nOutput files: {CHUNK_DIR}/chunk_0NN_labeled.csv")

if __name__ == '__main__':
    main()
