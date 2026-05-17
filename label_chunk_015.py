#!/usr/bin/env python3
"""
Label chunk_015.csv dựa trên taxonomy
"""

import pandas as pd
import re
from collections import defaultdict

# Đọc chunk
df = pd.read_csv('Asset/LabelData/_chunks/chunk_015.csv')

# Priority table từ taxonomy
PRIORITY = {
    'auth_bypass': 2,
    'boolean_blind': 3,
    'error_based': 4,
    'heavy_query': 4,
    'time_blind': 5,
    'out_of_band': 6,
    'union_based': 7,
    'stacked_queries': 8,
    'polyglot': 9,
    'benign': 10,
}

# Signal patterns từ whitelist
TIME_BLIND_FUNCS = ['sleep', 'pg_sleep', 'waitfor', 'benchmark', 'dbms_pipe', 'dbms_lock', 'randomblob']
ERROR_BASED_FUNCS = ['xmltype', 'extractvalue', 'updatexml', 'exp', 'utl_inaddr', 'ctxsys']
UNION_PATTERN = r'\bunion\s+(all\s+)?select\b'
OUT_OF_BAND_FUNCS = ['load_file', 'utl_http', 'xp_dirtree', 'xp_cmdshell']
BOOLEAN_FUNCS = ['elt', 'rlike', 'if(', 'case when']

def classify_sqli_type(payload_str):
    """Phân loại SQLi type dựa trên payload"""
    if not isinstance(payload_str, str) or len(payload_str) == 0:
        return 'benign', {}

    payload = payload_str.lower()
    signals = defaultdict(list)

    # Time-blind signals
    for func in TIME_BLIND_FUNCS:
        if func in payload:
            signals['time_blind'].append(func)

    # Error-based signals
    for func in ERROR_BASED_FUNCS:
        if func in payload:
            signals['error_based'].append(func)

    # Union signals
    if re.search(UNION_PATTERN, payload, re.IGNORECASE):
        signals['union_based'].append('union select')

    # Out-of-band signals
    for func in OUT_OF_BAND_FUNCS:
        if func in payload:
            signals['out_of_band'].append(func)

    # Boolean signals
    for func in BOOLEAN_FUNCS:
        if func in payload:
            signals['boolean_blind'].append(func)

    # Heavy query signals
    if re.search(r'\d{7,}', payload) or 'generate_series' in payload:
        signals['heavy_query'].append('large_number')

    # Cartesian join
    if re.search(r'from\s+\w+\s+as\s+t\d+,\s*\w+\s+as\s+t\d+,\s*\w+\s+as\s+t\d+', payload):
        signals['heavy_query'].append('cartesian_join')

    # Find best type (lowest priority)
    best_type = 'benign'
    best_priority = 999

    for sqli_type, sigs in signals.items():
        if sigs:
            priority = PRIORITY.get(sqli_type, 999)
            if priority < best_priority:
                best_priority = priority
                best_type = sqli_type

    return best_type, dict(signals)

def detect_db_engine(payload_str, sqli_type):
    """Detect DB engine"""
    if not isinstance(payload_str, str):
        return 'generic'

    payload = payload_str.lower()

    # Oracle
    if any(x in payload for x in ['xmltype', 'utl_inaddr', 'ctxsys', 'dbms_pipe', 'dual', '||']):
        return 'oracle'

    # PostgreSQL
    if any(x in payload for x in ['pg_sleep', 'pg_database', 'generate_series', '::text', '::int']):
        return 'postgresql'

    # MSSQL
    if any(x in payload for x in ['xp_cmdshell', 'waitfor', 'master..', 'sysobjects', 'convert(int,']):
        return 'mssql'

    # MySQL
    if any(x in payload for x in ['extractvalue', 'updatexml', 'sleep(', 'benchmark', 'information_schema', 'elt(']):
        return 'mysql'

    # SQLite
    if any(x in payload for x in ['randomblob', 'sqlite_master']):
        return 'sqlite'

    # Firebird
    if 'rdb$' in payload:
        return 'firebird'

    # DB2
    if 'sysibm.systables' in payload:
        return 'db2'

    return 'generic'

def compute_confidence(sqli_type, signals):
    """Tính confidence"""
    if sqli_type == 'benign':
        return 0.5

    signal_count = sum(len(v) for v in signals.values())
    confidence = min(0.95, 0.5 + signal_count * 0.15)
    return max(0.5, round(confidence, 2))

def generate_reasoning(payload_str, sqli_type, db_engine, signals):
    """Tạo reasoning ≥ 50 chars"""
    if sqli_type == 'benign':
        reason = f"No SQLi signals detected. Payload appears to be valid SQL without injection context."
    else:
        signal_list = signals.get(sqli_type, [])
        if signal_list:
            first_signal = signal_list[0]
            reason = f"SQLi type '{sqli_type}': '{first_signal}' detected; DB engine: {db_engine}. Payload structure indicates {sqli_type} attack pattern."
        else:
            reason = f"Classified as {sqli_type} based on payload pattern analysis and DB signature."

    if len(reason) < 50:
        reason += f" Pattern consistent with SQL injection payload."

    return reason[:200]

def sources_agree(sqli_type, a_type, c_type):
    """Tính sources_agree"""
    if pd.isna(a_type) or pd.isna(c_type):
        return 0

    a_type = str(a_type).strip() if pd.notna(a_type) else None
    c_type = str(c_type).strip() if pd.notna(c_type) else None

    agree = 0
    if a_type == sqli_type:
        agree += 1
    if c_type == sqli_type:
        agree += 1

    return agree

# Label từng row
results = []

for idx, row in df.iterrows():
    payload_inner = row.get('payload_inner', '')
    a_type = row.get('a_type')
    c_type = row.get('c_type')
    row_id = row.get('id')

    # Classify
    sqli_type, signals = classify_sqli_type(payload_inner)
    db_engine = detect_db_engine(payload_inner, sqli_type)
    confidence = compute_confidence(sqli_type, signals)
    reasoning = generate_reasoning(payload_inner, sqli_type, db_engine, signals)
    sources_agree_val = sources_agree(sqli_type, a_type, c_type)

    results.append({
        'id': row_id,
        'payload_inner': payload_inner,
        'sqli_type': sqli_type,
        'db_engine': db_engine,
        'confidence': confidence,
        'reasoning': reasoning,
        'sources_agree': sources_agree_val
    })

# Create output DataFrame
output_df = pd.DataFrame(results)

# Write output
output_df.to_csv('Asset/LabelData/_chunks/chunk_015_labeled.csv', index=False)

# Statistics
print(f"Rows labeled: {len(output_df)}")
print(f"\nType distribution (top 5):")
print(output_df['sqli_type'].value_counts().head())
print(f"\nConfidence < 0.7: {(output_df['confidence'] < 0.7).sum()}")
print(f"\nReasoning < 50 chars: {(output_df['reasoning'].str.len() < 50).sum()}")

print(f"\nOutput saved to: Asset/LabelData/_chunks/chunk_015_labeled.csv")
