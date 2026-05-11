import csv
import re

def normalize(p):
    return p.lower().strip()

def has_error_based(p):
    if re.search(r'xmltype\s*\(', p): return True
    if re.search(r'extractvalue\s*\(', p): return True
    if re.search(r'updatexml\s*\(', p): return True
    if re.search(r'floor\s*\(\s*rand\s*\(', p): return True
    if re.search(r'convert\s*\(\s*int\s*,', p): return True
    if re.search(r'cast\s*\(\s*.+?\s+as\s+int\b', p): return True
    if re.search(r'utl_inaddr\.get_host_address\s*\(', p): return True
    if re.search(r'ctxsys\.drithsx\.sn\s*\(', p): return True
    return False

def has_time_based(p):
    if re.search(r'(?<!\w)sleep\s*\(', p): return True
    if re.search(r'pg_sleep\s*\(', p): return True
    if re.search(r'waitfor\s+delay', p): return True
    if re.search(r'benchmark\s*\(', p): return True
    if re.search(r'randomblob\s*\(', p): return True
    if re.search(r'sqlite_version\s*\(', p): return True
    if re.search(r'dbms_pipe\.receive_message\s*\(', p): return True
    if re.search(r'generate_series\s*\(\s*1\s*,\s*\d{5,}', p): return True
    if re.search(r'regexp_substring\s*\(\s*repeat\s*\(', p): return True
    if re.search(r'like\s*\(\s*[\'\"](?:abcdefg|abcdef)[\'"]', p): return True
    return False

def has_union(p):
    if re.search(r'union\s+(?:all\s+)?select', p): return True
    if re.search(r'uni\s+on\s+select', p): return True
    if re.search(r'order\s+by\s+\d+', p) and not re.search(r'case\s+when|sleep|union|xmltype|extractvalue', p):
        return 'order_by'
    return False

def detect_db_engine(p):
    # Oracle
    if re.search(r'xmltype\s*\(', p): return 'oracle'
    if re.search(r'dbms_pipe\.', p): return 'oracle'
    if re.search(r'utl_inaddr\.', p): return 'oracle'
    if re.search(r'utl_http\.', p): return 'oracle'
    if re.search(r'ctxsys\.', p): return 'oracle'
    if re.search(r'dbms_utility\.', p): return 'oracle'
    if re.search(r'from\s+dual', p): return 'oracle'
    if re.search(r'sys_context\s*\(', p): return 'oracle'
    if re.search(r'sys\.all_tables', p): return 'oracle'
    if re.search(r'rownum', p) and re.search(r'from\s+dual', p): return 'oracle'
    if re.search(r'regexp_substr\s*\(', p): return 'oracle'
    # MySQL
    if re.search(r'sleep\s*\(', p) and not re.search(r'dbms_pipe', p): return 'mysql'
    if re.search(r'benchmark\s*\(', p): return 'mysql'
    if re.search(r'floor\s*\(\s*rand', p): return 'mysql'
    if re.search(r'extractvalue\s*\(', p): return 'mysql'
    if re.search(r'updatexml\s*\(', p): return 'mysql'
    if re.search(r'group_concat\s*\(', p): return 'mysql'
    if re.search(r'load_file\s*\(', p): return 'mysql'
    if re.search(r'into\s+outfile', p): return 'mysql'
    if re.search(r'@@version|@@datadir', p): return 'mysql'
    if re.search(r'#\s*$', p) and not re.search(r'rdb\$database', p): return 'mysql'
    if re.search(r'information_schema\.character_sets', p): return 'mysql'
    if re.search(r'information_schema\.system_users', p): return 'mysql'
    if re.search(r'in\s+boolean\s+mode', p): return 'mysql'
    if re.search(r'make_set\s*\(', p): return 'mysql'
    # PostgreSQL
    if re.search(r'pg_sleep\s*\(', p): return 'postgresql'
    if re.search(r'::text|::int\b|::numeric', p): return 'postgresql'
    if re.search(r'generate_series\s*\(', p): return 'postgresql'
    if re.search(r'string_agg\s*\(', p): return 'postgresql'
    if re.search(r'array_agg\s*\(', p): return 'postgresql'
    if re.search(r'pg_read_file\s*\(', p): return 'postgresql'
    # MSSQL
    if re.search(r'waitfor\s+delay', p): return 'mssql'
    if re.search(r'master\.\.sysdatabases', p): return 'mssql'
    if re.search(r'xp_cmdshell', p): return 'mssql'
    if re.search(r'@@servername', p): return 'mssql'
    if re.search(r'sysobjects', p): return 'mssql'
    if re.search(r'syscolumns', p): return 'mssql'
    if re.search(r'sysusers', p): return 'mssql'
    if re.search(r'char\s*\(\s*\d+\s*\)\s*\+', p): return 'mssql'
    if re.search(r'\bconvert\s*\(\s*int', p): return 'mssql'
    # SQLite
    if re.search(r'randomblob\s*\(', p): return 'sqlite'
    if re.search(r'sqlite_version\s*\(', p): return 'sqlite'
    if re.search(r'sqlite_master', p): return 'sqlite'
    # Check for double-pipe Oracle-style
    if re.search(r'chr\s*\(\s*\d+\s*\)\s*\|\|', p): return 'oracle'
    # RLIKE = MySQL
    if re.search(r'\brlike\b', p): return 'mysql'
    # ELT = MySQL
    if re.search(r'\belt\s*\(', p): return 'mysql'
    return 'generic'


def label_row(p):
    p_lower = p.lower().strip()
    
    has_err = has_error_based(p_lower)
    has_time = has_time_based(p_lower)
    union_result = has_union(p_lower)
    has_union_flag = union_result == True
    has_order_by = union_result == 'order_by'
    
    # Detect boolean blind markers
    has_case_when = bool(re.search(r'case\s+when', p_lower))
    has_rlike_case = bool(re.search(r'rlike\s*\(\s*select\s+case\s+when', p_lower))
    has_if = bool(re.search(r'\bif\s*\(', p_lower))
    has_iif = bool(re.search(r'\biif\s*\(', p_lower))
    has_elt = bool(re.search(r'\belt\s*\(', p_lower))
    has_simple_bool = bool(re.search(r'\d+\s*=\s*\d+', p_lower))
    has_where_cond = bool(re.search(r'where\s+\d+\s*=', p_lower))
    has_in_select = bool(re.search(r'in\s*\(\s*select', p_lower))
    has_like_compare = bool(re.search(r"'[^']+'\s+like\s+'[^']+'", p_lower))
    has_str_compare = bool(re.search(r"'[^']+'\s*=\s*'[^']*'", p_lower))
    
    # Engine
    engine = detect_db_engine(p_lower)
    
    # --- POLYGLOT DETECTION: Find FIRST technique in payload ---
    # Per rules: when multiple techniques exist, pick the one appearing FIRST
    
    def first_match(pattern_list):
        earliest = None
        earliest_key = None
        for key, pat in pattern_list:
            m = re.search(pat, p_lower)
            if m:
                pos = m.start()
                if earliest is None or pos < earliest:
                    earliest = pos
                    earliest_key = key
        return earliest_key, earliest
    
    # Check error markers
    error_pats = [
        ('error_based', r'xmltype\s*\('),
        ('error_based', r'extractvalue\s*\('),
        ('error_based', r'updatexml\s*\('),
        ('error_based', r'floor\s*\(\s*rand\s*\('),
        ('error_based', r'convert\s*\(\s*int\s*,'),
        ('error_based', r'utl_inaddr\.get_host_address\s*\('),
        ('error_based', r'ctxsys\.drithsx\.sn\s*\('),
    ]
    
    # Check time markers
    time_pats = [
        ('time_blind', r'(?<!\w)sleep\s*\('),
        ('time_blind', r'pg_sleep\s*\('),
        ('time_blind', r'waitfor\s+delay'),
        ('time_blind', r'benchmark\s*\('),
        ('time_blind', r'randomblob\s*\('),
        ('time_blind', r'sqlite_version\s*\('),
        ('time_blind', r'dbms_pipe\.receive_message\s*\('),
        ('time_blind', r'generate_series\s*\(\s*1\s*,\s*\d{4,}'),
        ('time_blind', r'regexp_substring\s*\(\s*repeat\s*\('),
        ('time_blind', r'like\s*\(\s*[\'\"](?:abcdefg|abcdef)[\'"]'),
    ]
    
    # Check union markers
    union_pats = [
        ('union_based', r'union\s+(?:all\s+)?select'),
        ('union_based', r'uni\s+on\s+sel[^t]*ect'),
    ]
    
    # Check boolean markers  
    bool_pats = [
        ('boolean_blind', r'case\s+when'),
        ('boolean_blind', r'\bif\s*\('),
        ('boolean_blind', r'\biif\s*\('),
        ('boolean_blind', r'\belt\s*\('),
        ('boolean_blind', r'rlike\s*\(\s*select'),
        ('boolean_blind', r"'[^']+'\s+like\s+'[^']+'"),
        ('boolean_blind', r"'[^']+'\s*=\s*'[^']*'"),
    ]
    
    all_pats = error_pats + time_pats + union_pats + bool_pats
    
    first_type, first_pos = first_match(all_pats)
    
    # Also check ORDER BY as union preparation
    m_order = re.search(r'order\s+by\s+\d+', p_lower) if not re.search(r'case\s+when|sleep|union|xmltype|extractvalue', p_lower) else None
    if m_order:
        order_pos = m_order.start()
        if first_pos is None or order_pos < first_pos:
            first_type = 'union_based'
            first_pos = order_pos
    
    # If no technique found, fall through
    if first_type is None:
        is_boolean = has_simple_bool or has_where_cond or has_in_select
        is_boolean = is_boolean or bool(re.search(r'1\s*=\s*1', p_lower))
        is_boolean = is_boolean or bool(re.search(r"or\s+['\"]", p_lower))
        is_boolean = is_boolean or bool(re.search(r'select\s+.+?\s+where\s+\d+\s*=', p_lower))
        
        if is_boolean:
            first_type = 'boolean_blind'
    
    # No technique found at all
    if first_type is None:
        if len(p_lower) < 10:
            sqli_type = 'boolean_blind'
            engine = 'generic'
            conf = 0.70
            return sqli_type, engine, conf
        has_sql_keywords = bool(re.search(r'\bselect\b|\bwhere\b|\band\b|\bor\b|\bfrom\b|\blike\b|\bin\b', p_lower))
        if has_sql_keywords:
            sqli_type = 'boolean_blind'
            conf = 0.85
            return sqli_type, engine, conf
        sqli_type = 'boolean_blind'
        engine = 'generic'
        conf = 0.70
        return sqli_type, engine, conf
    
    # --- Now determine confidence based on the first technique ---
    if first_type == 'error_based':
        sqli_type = 'error_based'
        oracle_markers = sum(1 for m in ['xmltype', 'ctxsys', 'utl_inaddr', 'from dual'] if m in p_lower)
        if oracle_markers >= 2 or (has_err and re.search(r'from\s+dual', p_lower)):
            conf = 1.00
        elif has_union_flag:
            conf = 0.85
        else:
            conf = 1.00
        return sqli_type, engine, conf
    
    if first_type == 'time_blind':
        sqli_type = 'time_blind'
        conf = 1.00
        if has_case_when and (re.search(r'regexp_substring\s*\(\s*repeat', p_lower) or re.search(r'generate_series\s*\(\s*1\s*,\s*\d{5,}', p_lower)):
            conf = 0.85
        return sqli_type, engine, conf
    
    if first_type == 'union_based':
        sqli_type = 'union_based'
        conf = 1.00
        if re.search(r'#\s*$', p_lower):
            engine = 'mysql'
        elif engine == 'generic' and re.search(r'from\s+dual', p_lower):
            engine = 'oracle'
        elif len(p_lower) < 40:
            conf = 0.85
        if has_case_when or has_if:
            conf = 0.85  # polyglot
        return sqli_type, engine, conf
    
    if first_type == 'boolean_blind':
        sqli_type = 'boolean_blind'
        has_strong_marker = has_case_when or has_if or has_iif
        
        if has_strong_marker and engine not in ('generic',):
            conf = 1.00
        elif has_strong_marker:
            if re.search(r'select\s+case\s+when', p_lower) and re.search(r'end\s*--', p_lower):
                conf = 0.85
            elif re.search(r'select\s+case\s+when', p_lower):
                conf = 0.85
            else:
                conf = 1.00
        elif has_rlike_case:
            conf = 1.00
        elif has_elt:
            conf = 0.85
        elif has_simple_bool and len(p_lower) < 30:
            if re.search(r'1\s*or\s*1\s*=\s*1', p_lower):
                conf = 0.85
            else:
                conf = 0.70
        elif has_simple_bool:
            conf = 0.85
        else:
            conf = 0.85
        
        if len(p_lower) < 15:
            conf = 0.70
        
        # Polyglot: if union also present but boolean appears first
        if has_union_flag or has_order_by:
            conf = 0.85
        
        return sqli_type, engine, conf
    
    # Fallback
    if len(p_lower) < 10:
        sqli_type = 'boolean_blind'
        engine = 'generic'
        conf = 0.70
        return sqli_type, engine, conf
    
    # Obfuscated union (e.g., "uni on select" instead of "union select")
    if re.search(r'uni\s+on\s+sel[^t]*ect', p_lower):
        sqli_type = 'union_based'
        conf = 0.85
        return sqli_type, engine, conf
    
    # Generic SQL keywords
    has_sql_keywords = bool(re.search(r'\bselect\b|\bwhere\b|\band\b|\bor\b|\bfrom\b|\blike\b|\bin\b', p_lower))
    if has_sql_keywords:
        sqli_type = 'boolean_blind'
        conf = 0.85
        return sqli_type, engine, conf
    
    sqli_type = 'boolean_blind'
    engine = 'generic'
    conf = 0.70
    return sqli_type, engine, conf


# Main processing
rows = []
with open(r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\split_data.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        rows.append(row)

target_rows = [r for r in rows if 8001 <= int(r['id']) <= 10000]
print(f"Found {len(target_rows)} rows to label")

results = []
for r in target_rows:
    sid = r['id']
    payload = r['payload_norm']
    sqli_type, db_engine, confidence = label_row(payload)
    results.append((sid, sqli_type, db_engine, f"{confidence:.2f}"))

# Write output
output_path = r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\split_data_labeled_8001_10000.csv'
with open(output_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'sqli_type', 'db_engine', 'confidence'])
    writer.writerows(results)

print(f"Written {len(results)} labeled rows to {output_path}")

# Print distribution
from collections import Counter
types = Counter(r[1] for r in results)
engines = Counter(r[2] for r in results)
confs = Counter(r[3] for r in results)
print(f"\nDistribution by type:")
for k, v in types.most_common():
    print(f"  {k}: {v}")
print(f"\nDistribution by engine:")
for k, v in engines.most_common():
    print(f"  {k}: {v}")
print(f"\nDistribution by confidence:")
for k, v in confs.most_common():
    print(f"  {k}: {v}")
