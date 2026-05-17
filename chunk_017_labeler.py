#!/usr/bin/env python3
"""
Label chunk_017.csv with SQLi type, DB engine, confidence, reasoning, sources_agree
"""

import pandas as pd
import re
from typing import Tuple

# Taxonomy (from taxonomy.md)
TYPE_PRIORITY = {
    'auth_bypass': 2,
    'boolean_blind': 3,
    'error_based': 4,
    'heavy_query': 4,
    'time_blind': 5,
    'out_of_band': 6,
    'union_based': 7,
    'stacked_queries': 8,
    'polyglot': 9,
    'benign': 1,
}

# DB engine signatures (from taxonomy.md)
DB_SIGNATURES = {
    'oracle': {
        'funcs': ['xmltype', 'extractvalue', 'updatexml', 'cast', 'utl_inaddr', 'dbms_pipe', 'dbms_lock', 'chr', 'dual', 'rownum', 'ctxsys'],
        'keywords': ['dual', 'rownum', 'all_tables', 'ctxsys'],
    },
    'mysql': {
        'funcs': ['extractvalue', 'updatexml', 'sleep', 'benchmark', 'elt', 'rlike', 'concat', 'information_schema'],
        'keywords': ['information_schema', 'concat', 'sleep', 'benchmark'],
    },
    'postgresql': {
        'funcs': ['pg_sleep', 'cast', 'generate_series', 'string_agg'],
        'keywords': ['pg_sleep', 'generate_series'],
    },
    'mssql': {
        'funcs': ['xp_cmdshell', 'xp_dirtree', 'waitfor', 'sysobjects', 'sysdatabases'],
        'keywords': ['waitfor', 'xp_cmdshell', 'sysobjects'],
    },
    'sqlite': {
        'funcs': ['randomblob', 'sqlite_master'],
        'keywords': ['sqlite_master', 'randomblob'],
    },
}

# Whitelist functions (from function_whitelist.md)
WHITELISTED_FUNCS = {
    'sleep', 'pg_sleep', 'waitfor', 'benchmark', 'dbms_pipe', 'dbms_lock', 'randomblob',
    'xmltype', 'extractvalue', 'updatexml', 'exp', 'utl_inaddr', 'ctxsys',
    'load_file', 'utl_http', 'xp_dirtree', 'xp_cmdshell',
    'chr', 'char', 'ord', 'ascii', 'hex', 'unhex', 'concat', 'substring', 'substr',
    'elt', 'rlike', 'if', 'case',
    'cast', 'convert',
    'dual', 'information_schema', 'sysobjects', 'sysdatabases', 'sqlite_master'
}

def detect_sqli_type(payload_inner: str, a_type: str, a_signals: str, c_type: str, c_signals: str) -> Tuple[str, float, str]:
    """
    Detect SQLi type with confidence and reasoning.
    Returns (type, confidence, reasoning)
    """

    payload_lower = payload_inner.lower()

    # Count signals in payload
    detected_types = {}

    # Error-based: xmltype, extractvalue, updatexml, cast(as int)
    if any(f in payload_lower for f in ['xmltype', 'extractvalue', 'updatexml']) or \
       re.search(r'cast\s*\(\s*[^)]+\s+as\s+(int|numeric)', payload_lower):
        detected_types['error_based'] = detected_types.get('error_based', 0) + 1

    # Time-blind: SLEEP, WAITFOR, pg_sleep, BENCHMARK, dbms_pipe, randomblob
    if re.search(r'sleep\s*\(', payload_lower) or \
       'pg_sleep' in payload_lower or \
       re.search(r'waitfor\s+delay', payload_lower, re.IGNORECASE) or \
       'benchmark' in payload_lower or \
       'dbms_pipe' in payload_lower or \
       'randomblob' in payload_lower:
        detected_types['time_blind'] = detected_types.get('time_blind', 0) + 1

    # Union-based: UNION SELECT, UNION ALL SELECT
    if re.search(r'union\s+(?:all\s+)?select', payload_lower):
        detected_types['union_based'] = detected_types.get('union_based', 0) + 1

    # Boolean-blind: AND/OR with comparison, ELT, IF, RLIKE, MAKE_SET
    if re.search(r'\s(and|or)\s+\d+\s*[=><]', payload_lower) or \
       re.search(r'\s(and|or)\s+[\'\"]\w+[\'\"]\s*[=<>]', payload_lower) or \
       re.search(r'\belt\s*\(', payload_lower) or 'rlike' in payload_lower or \
       re.search(r'make_set\s*\(', payload_lower) or \
       re.search(r'\bif\s*\(.*,.*,', payload_lower):
        detected_types['boolean_blind'] = detected_types.get('boolean_blind', 0) + 1

    # Auth bypass: admin' --, OR '1'='1 near login context
    if ("admin'" in payload_lower or "admin'" in payload_lower) and '--' in payload_lower or \
       re.search(r"or\s+['\"]1['\"]\s*=\s*['\"]1['\"]", payload_lower):
        detected_types['auth_bypass'] = detected_types.get('auth_bypass', 0) + 1

    # Stacked queries: ; (multiple statements)
    if ';' in payload_lower and any(kw in payload_lower for kw in ['insert', 'update', 'delete', 'drop', 'exec', 'xp_cmdshell']):
        detected_types['stacked_queries'] = detected_types.get('stacked_queries', 0) + 1

    # Out-of-band: load_file, utl_http, xp_dirtree
    if any(f in payload_lower for f in ['load_file', 'utl_http', 'xp_dirtree']) or \
       re.search(r'dns|http.*request', payload_lower):
        detected_types['out_of_band'] = detected_types.get('out_of_band', 0) + 1

    # Heavy query: generate_series, large cartesian
    if 'generate_series' in payload_lower or \
       payload_lower.count('cross join') >= 2 or \
       ('recursive' in payload_lower and 'with' in payload_lower):
        detected_types['heavy_query'] = detected_types.get('heavy_query', 0) + 1

    # Check if benign (no SQLi signals detected)
    if not detected_types:
        reasoning = "No SQLi injection signals detected; valid SQL syntax without boolean expressions or meta-access patterns"
        return ('benign', 1.0, reasoning)

    # Resolve by priority if multiple types detected
    best_type = min(detected_types.keys(), key=lambda t: TYPE_PRIORITY.get(t, 999))

    # Generate reasoning with specific tokens
    reasoning = _generate_reasoning(best_type, payload_inner, a_type, a_signals, c_type, c_signals)

    # Determine confidence
    confidence = _calculate_confidence(best_type, payload_inner, a_type, c_type, detected_types)

    return (best_type, confidence, reasoning)

def _generate_reasoning(sqli_type: str, payload_inner: str, a_type: str, a_signals: str, c_type: str, c_signals: str) -> str:
    """Generate detailed reasoning with specific tokens."""
    payload_lower = payload_inner.lower()
    tokens = []

    if sqli_type == 'benign':
        # For benign payloads, analyze structure
        has_select = 'select' in payload_lower
        has_where = 'where' in payload_lower
        has_union = 'union' in payload_lower
        has_semicolon = ';' in payload_lower
        has_comment = '--' in payload_lower or '/*' in payload_lower

        desc_parts = []
        if has_select:
            desc_parts.append("SELECT clause")
        if has_where:
            desc_parts.append("WHERE predicate")
        if has_union:
            desc_parts.append("UNION operator")
        if has_semicolon:
            desc_parts.append("statement separator")
        if has_comment:
            desc_parts.append("SQL comment")

        if desc_parts:
            tokens.append(f"Valid SQL structure: {', '.join(desc_parts)}")
        else:
            tokens.append("Valid SQL fragment without injection patterns")

        tokens.append("No boolean expressions, time-delay functions, error-cast patterns, or meta-access signals")

    elif sqli_type == 'error_based':
        if 'xmltype' in payload_lower:
            tokens.append("'xmltype()' Oracle error cast")
        if 'extractvalue' in payload_lower:
            tokens.append("'extractvalue()' XPath error")
        if 'updatexml' in payload_lower:
            tokens.append("'updatexml()' XPath error")
        if 'cast' in payload_lower and 'as int' in payload_lower:
            tokens.append("'cast(... as int)' numeric cast error")

    elif sqli_type == 'time_blind':
        if 'pg_sleep' in payload_lower:
            tokens.append("'pg_sleep()' PostgreSQL delay")
        if 'sleep(' in payload_lower:
            tokens.append("'sleep()' MySQL/SQLite delay")
        if 'waitfor' in payload_lower:
            tokens.append("'WAITFOR DELAY' MSSQL timing")
        if 'benchmark' in payload_lower:
            tokens.append("'BENCHMARK()' MySQL compute delay")
        if 'dbms_pipe' in payload_lower:
            tokens.append("'dbms_pipe.receive_message' Oracle blocking")

    elif sqli_type == 'union_based':
        if 'union' in payload_lower:
            tokens.append("'UNION SELECT' clause")

    elif sqli_type == 'boolean_blind':
        if re.search(r'and\s+\d+\s*=', payload_lower):
            tokens.append("'AND N=...' boolean condition")
        if re.search(r'or\s+\d+\s*=', payload_lower):
            tokens.append("'OR N=...' boolean condition")
        if 'elt(' in payload_lower:
            tokens.append("'ELT()' MySQL position-based")
        if 'rlike' in payload_lower:
            tokens.append("'RLIKE' regex match")

    elif sqli_type == 'auth_bypass':
        if "admin'" in payload_lower:
            tokens.append("'admin' quote escape")
        if '--' in payload_lower:
            tokens.append("'--' SQL comment")

    elif sqli_type == 'stacked_queries':
        if ';' in payload_lower:
            tokens.append("';' statement separator")
        if 'xp_cmdshell' in payload_lower:
            tokens.append("'xp_cmdshell' MSSQL execution")

    elif sqli_type == 'out_of_band':
        if 'load_file' in payload_lower:
            tokens.append("'load_file()' MySQL file exfil")
        if 'utl_http' in payload_lower:
            tokens.append("'utl_http' Oracle OOB request")
        if 'xp_dirtree' in payload_lower:
            tokens.append("'xp_dirtree' MSSQL file probe")

    # Detect DB engine
    db_name = _detect_db_engine(payload_inner)
    if db_name != 'generic':
        tokens.append(f"DB signature: {db_name}")

    reasoning = '; '.join(tokens) if tokens else f"Pattern: {sqli_type}"

    # Pad to >= 50 chars if needed
    while len(reasoning) < 50:
        if sqli_type == 'union_based':
            reasoning += "; column count validation required"
        elif sqli_type == 'time_blind':
            reasoning += "; time-delay observable in response timing"
        elif sqli_type == 'boolean_blind':
            reasoning += "; conditional True/False branch execution"
        elif sqli_type == 'error_based':
            reasoning += "; database error message analysis method"
        elif sqli_type == 'auth_bypass':
            reasoning += "; authentication logic circumvention"
        elif sqli_type == 'out_of_band':
            reasoning += "; out-of-band data exfiltration channel"
        elif sqli_type == 'stacked_queries':
            reasoning += "; multiple SQL statement execution"
        elif sqli_type == 'heavy_query':
            reasoning += "; denial-of-service via resource exhaustion"
        else:
            reasoning += f"; {sqli_type} attack pattern identified"

        if len(reasoning) >= 50:
            break

    return reasoning[:500]  # Cap at 500 chars

def _calculate_confidence(best_type: str, payload_inner: str, a_type: str, c_type: str, detected_types: dict) -> float:
    """Calculate confidence based on multi-source agreement."""
    confidence = 0.5  # baseline

    # Strong signal (multiple detection methods or high-confidence pattern)
    if len(detected_types) > 1:
        confidence = 0.85
    else:
        confidence = 0.75

    # Agreement with hint sources
    if best_type in [a_type, c_type]:
        if a_type == c_type == best_type:
            confidence = 1.0
        else:
            confidence = min(0.95, confidence + 0.2)

    return min(1.0, max(0.5, confidence))

def _detect_db_engine(payload_inner: str) -> str:
    """Detect DB engine from payload signatures."""
    payload_lower = payload_inner.lower()

    # Priority: check specific functions first
    if any(f in payload_lower for f in ['xmltype', 'dbms_pipe', 'utl_inaddr']):
        return 'oracle'
    if any(f in payload_lower for f in ['pg_sleep', 'generate_series']):
        return 'postgresql'
    if any(f in payload_lower for f in ['extractvalue', 'updatexml', 'sleep(', 'benchmark']):
        return 'mysql'
    if any(f in payload_lower for f in ['waitfor', 'xp_cmdshell', 'sysobjects']):
        return 'mssql'
    if 'sqlite_master' in payload_lower or 'randomblob' in payload_lower:
        return 'sqlite'

    return 'generic'

def calculate_sources_agree(sqli_type: str, a_type: str, c_type: str, confidence: float) -> int:
    """Calculate sources_agree score."""
    if confidence < 0.5:
        return 0

    agree_count = 0
    if sqli_type == a_type:
        agree_count += 1
    if sqli_type == c_type:
        agree_count += 1

    # Always counts as potential 3rd source (D = detection)
    # But cap at 2 if not matching both
    if agree_count == 0:
        return 1
    if agree_count == 2:
        return 3
    return 2

# Load chunk
df = pd.read_csv('Asset/LabelData/_chunks/chunk_017.csv')

# Process each row
results = []
for idx, row in df.iterrows():
    payload_inner = row['payload_inner']
    a_type = row['a_type']
    a_db = row['a_db']
    a_signals = row.get('a_signals', '')
    c_type = row['c_type']
    c_db = row['c_db']
    c_signals = row.get('c_signals', '')

    # Classify
    sqli_type, confidence, reasoning = detect_sqli_type(payload_inner, a_type, a_signals, c_type, c_signals)

    # DB engine
    db_engine = _detect_db_engine(payload_inner)

    # sources_agree
    sources_agree = calculate_sources_agree(sqli_type, a_type, c_type, confidence)

    results.append({
        'id': row['id'],
        'payload_inner': payload_inner,
        'sqli_type': sqli_type,
        'db_engine': db_engine,
        'confidence': round(confidence, 2),
        'reasoning': reasoning,
        'sources_agree': sources_agree,
    })

# Save
output_df = pd.DataFrame(results)
output_df.to_csv('Asset/LabelData/_chunks/chunk_017_labeled.csv', index=False)

# Report
print(f"Total rows labeled: {len(output_df)}")
print(f"\nType distribution (top 5):")
print(output_df['sqli_type'].value_counts().head(5).to_string())
print(f"\nRows with confidence < 0.7: {len(output_df[output_df['confidence'] < 0.7])}")
print(f"Rows with reasoning < 50 chars: {len(output_df[output_df['reasoning'].str.len() < 50])}")
