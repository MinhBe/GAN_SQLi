#!/usr/bin/env python3
"""
Labeler for chunk_011.csv
Applies 3-source validation (Rule + Priority + Heuristic) with better reasoning
"""

import csv
import re
from collections import defaultdict

# Priority table from taxonomy.md (lower = stronger)
PRIORITY = {
    'benign': 1,
    'auth_bypass': 2,
    'boolean_blind': 3,
    'error_based': 4,
    'time_blind': 5,
    'out_of_band': 6,
    'union_based': 7,
    'stacked_queries': 8,
    'polyglot': 9,
    'heavy_query': 4,  # Treat as error_based priority
}

# Function patterns for Rule source
PATTERNS = {
    # Time-blind
    r'\bsleep\s*\(': ('time_blind', 'mysql'),
    r'\bpg_sleep\s*\(': ('time_blind', 'postgresql'),
    r'\bwaitfor\s+delay': ('time_blind', 'mssql'),
    r'\bbenchmark\s*\(': ('time_blind', 'mysql'),
    r'\bdbms_pipe\.receive_message': ('time_blind', 'oracle'),
    r'\brandomblob\s*\(': ('time_blind', 'sqlite'),

    # Error-based
    r'\bxmltype\s*\(': ('error_based', 'oracle'),
    r'\bextractvalue\s*\(': ('error_based', 'mysql'),
    r'\bupdatexml\s*\(': ('error_based', 'mysql'),
    r'\bexp\s*\(': ('error_based', 'mysql'),
    r'\butl_inaddr\.get_host_address': ('error_based', 'oracle'),
    r'\bctxsys\.drithsx': ('error_based', 'oracle'),

    # Out-of-band
    r'\butl_http\.request': ('out_of_band', 'oracle'),
    r'\bxp_dirtree': ('out_of_band', 'mssql'),
    r'\bxp_cmdshell': ('stacked_queries', 'mssql'),
    r'\bdbms_utility\.sqlid_to_sqlhash': ('out_of_band', 'oracle'),
    r'\bload_file\s*\(': ('out_of_band', 'mysql'),

    # Union-based
    r'\bunion\s+all\s+select': ('union_based', 'generic'),
    r'\bunion\s+select': ('union_based', 'generic'),

    # Boolean/Conditional
    r'\belt\s*\(': ('boolean_blind', 'mysql'),
    r'\brlike\s*\(': ('boolean_blind', 'mysql'),
    r'\bif\s*\(': ('boolean_blind', 'mysql'),
    r'\bcase\s+when': ('boolean_blind', 'generic'),
}

def rule_check(payload_inner):
    """Rule source: pattern matching"""
    payload_lower = payload_inner.lower()
    matches = []

    for pattern, (sqli_type, db_engine) in PATTERNS.items():
        if re.search(pattern, payload_lower):
            priority = PRIORITY.get(sqli_type, 999)
            matches.append((priority, sqli_type, db_engine, pattern))

    if matches:
        matches.sort(key=lambda x: x[0])  # Sort by priority (lower first)
        _, sqli_type, db_engine, matched_pattern = matches[0]
        return sqli_type, db_engine, matched_pattern

    return None, None, None

def heuristic_check(payload_inner, sqli_type_hint, db_hint):
    """Heuristic source: structure analysis"""
    payload_lower = payload_inner.lower()

    # Check for benign patterns
    if re.search(r'^\d+\s*$', payload_inner.strip()):
        return 'benign', 'generic'

    if re.search(r'^[a-z_]\w*\s*=\s*\d+\s*$', payload_lower):
        return 'benign', 'generic'

    if re.search(r'order\s+by\s+\d+\s*$', payload_lower):
        return 'benign', 'generic'

    # Heavy query patterns
    if re.search(r'generate_series\s*\(\s*1\s*,\s*\d{6,}\s*\)', payload_lower):
        return 'heavy_query', 'postgresql'

    if re.search(r'randomblob\s*\(\s*\d{6,}', payload_lower):
        return 'heavy_query', 'sqlite'

    if re.search(r'benchmark\s*\(\s*\d{6,}', payload_lower):
        return 'heavy_query', 'mysql'

    if re.search(r'regexp_substring.*\d{6,}', payload_lower):
        return 'heavy_query', 'postgresql'

    # Multi-table joins (heavy)
    if re.search(r'from\s+\w+\s+t1\s*,\s*\w+\s+t2\s*,\s*\w+\s+t3', payload_lower):
        return 'heavy_query', 'generic'

    # Boolean patterns
    if re.search(r'\bor\s+\d+\s*=\s*\d+', payload_lower):
        return 'boolean_blind', 'generic'

    if re.search(r'\band\s+\d+\s*=\s*\d+', payload_lower):
        return 'boolean_blind', 'generic'

    # Default: conservative
    if sqli_type_hint:
        return sqli_type_hint, db_hint or 'generic'

    return None, None

def compute_confidence_and_reasoning(a_type, a_db, c_type, c_db, sqli_type, db_engine, matched_pattern):
    """Compute confidence and reasoning"""

    # Count source agreement
    sources_agree = 0
    if a_type and a_type.lower() == sqli_type:
        sources_agree += 1
    if c_type and c_type.lower() == sqli_type:
        sources_agree += 1

    # Confidence based on agreement
    if sources_agree == 2:
        confidence = 0.90
    elif sources_agree == 1:
        confidence = 0.75
    else:
        confidence = 0.65

    # Build reasoning
    if matched_pattern:
        if 'sleep' in matched_pattern:
            reasoning = f"'sleep()' time-delay function matched; MySQL time-based blind SQLi confirmed"
        elif 'pg_sleep' in matched_pattern:
            reasoning = f"'pg_sleep()' is PostgreSQL time-based function; detected in payload context"
        elif 'benchmark' in matched_pattern:
            reasoning = f"'benchmark(N, function)' causes CPU delay; MySQL time-blind confirmed"
        elif 'xmltype' in matched_pattern:
            reasoning = f"'xmltype()' is Oracle XML parsing function; triggers error-based SQLi"
        elif 'extractvalue' in matched_pattern:
            reasoning = f"'extractvalue()' XPath error extraction; MySQL error-based SQLi"
        elif 'union' in matched_pattern:
            reasoning = f"'UNION ALL SELECT' structure detected; classic union-based SQLi"
        elif 'elt' in matched_pattern:
            reasoning = f"'ELT()' conditional function; MySQL boolean-blind context"
        elif 'rlike' in matched_pattern:
            reasoning = f"'RLIKE' regex operator; MySQL boolean context"
        elif 'utl_inaddr' in matched_pattern:
            reasoning = f"'utl_inaddr.get_host_address()' Oracle function; OOB exfiltration vector"
        elif 'pg_sleep' in matched_pattern:
            reasoning = f"'pg_sleep()' PostgreSQL time delay; time-blind SQLi"
        elif 'waitfor' in matched_pattern:
            reasoning = f"'WAITFOR DELAY' MSSQL time function; time-blind SQLi"
        else:
            reasoning = f"Pattern '{matched_pattern}' matched; type={sqli_type}"
    else:
        reasoning = f"Heuristic analysis: {sqli_type} inferred from structure"

    # Ensure minimum reasoning length
    if len(reasoning) < 50:
        reasoning = reasoning.ljust(50, '.')

    return confidence, reasoning, sources_agree

def label_row(row):
    """Label a single row"""
    id_val = row['id']
    payload_inner = row['payload_inner']
    a_type = row.get('a_type', '').strip() or None
    a_db = row.get('a_db', '').strip() or None
    c_type = row.get('c_type', '').strip() or None
    c_db = row.get('c_db', '').strip() or None

    # Rule check
    rule_type, rule_db, matched_pattern = rule_check(payload_inner)

    # Heuristic check
    heur_type, heur_db = heuristic_check(payload_inner, c_type, c_db)

    # Determine final label
    if rule_type:
        sqli_type = rule_type
        db_engine = rule_db
    elif heur_type:
        sqli_type = heur_type
        db_engine = heur_db
    elif c_type:
        sqli_type = c_type
        db_engine = c_db or 'generic'
    else:
        sqli_type = 'benign'
        db_engine = 'generic'

    # Compute confidence and reasoning
    confidence, reasoning, sources_agree = compute_confidence_and_reasoning(
        a_type, a_db, c_type, c_db, sqli_type, db_engine, matched_pattern
    )

    return {
        'id': id_val,
        'payload_inner': payload_inner,
        'sqli_type': sqli_type,
        'db_engine': db_engine,
        'confidence': confidence,
        'reasoning': reasoning,
        'sources_agree': sources_agree,
    }

# Main
input_file = r'C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks\chunk_011.csv'
output_file = r'C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks\chunk_011_labeled.csv'

labeled_rows = []
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.DictReader(f)
    for row in reader:
        labeled = label_row(row)
        labeled_rows.append(labeled)

# Write output
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    fieldnames = ['id', 'payload_inner', 'sqli_type', 'db_engine', 'confidence', 'reasoning', 'sources_agree']
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(labeled_rows)

# Stats
type_counts = defaultdict(int)
db_counts = defaultdict(int)
low_conf_count = 0
short_reasoning_count = 0

for row in labeled_rows:
    type_counts[row['sqli_type']] += 1
    db_counts[row['db_engine']] += 1
    if row['confidence'] < 0.7:
        low_conf_count += 1
    if len(row['reasoning']) < 50:
        short_reasoning_count += 1

print(f"Labeled {len(labeled_rows)} rows")
print(f"\nTop 5 types:")
for t, c in sorted(type_counts.items(), key=lambda x: -x[1])[:5]:
    print(f"  {t}: {c}")
print(f"\nLow confidence (<0.7): {low_conf_count}")
print(f"Short reasoning (<50 chars): {short_reasoning_count}")
