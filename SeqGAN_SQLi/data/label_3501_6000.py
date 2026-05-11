import csv, sys, re

csv.field_size_limit(2**31-1)

# ---------- helpers ----------
def lower_payload(p):
    """lowercase but preserve hex literals"""
    return p.lower()

def contains_any(p, keywords):
    p_lower = p.lower()
    for k in keywords:
        if k.lower() in p_lower:
            return True
    return False

# ---------- engine detection ----------
oracle_markers = [
    'xmltype(', 'dbms_pipe.', 'utl_inaddr.', 'utl_http.', 'sys_context(',
    'from dual', 'sys.all_tables', 'rownum', 'ctxsys.', 'dbms_utility.',
    'all_tables', 'all_users', 'all_views',
]
# chr(X)||chr(Y) chain is Oracle pattern — multiple || with chr()
# But also check for :: casts which are postgres

mysql_markers = [
    'information_schema.', 'group_concat(', 'floor(rand(',
    'extractvalue(', 'updatexml(', 'load_file(', 'into outfile',
    '@@version', '@@datadir',
]
mysql_comment_hash = lambda p: p.strip().endswith('#') or '# ' in p or '#\n' in p

postgresql_markers = [
    'pg_sleep(', 'generate_series(', '::text', '::int', '::numeric',
    'string_agg(', 'array_agg(', 'pg_read_file(', '$$',
]
# ::text and ::numeric are strong postgres indicators

mssql_markers = [
    'waitfor delay', 'master..', 'xp_cmdshell', '@@servername',
    'sysobjects', 'syscolumns', 'sysusers', 'convert(int,',
    'convert(varchar,',
]

sqlite_markers = [
    'randomblob(', 'sqlite_version(', 'sqlite_master',
]

def detect_engine(payload):
    p_lower = payload.lower()
    
    # Check specific markers in priority
    # ::text or ::numeric or ::int = postgres (but not :: in general, specific ::text etc)
    has_postgres_cast = bool(re.search(r'::(text|int|integer|numeric)', p_lower))
    
    # chr chain with || (Oracle) vs char() with + (MSSQL) vs concat() (MySQL)
    # Oracle: chr(X)||chr(Y) pattern
    has_oracle_chr_chain = bool(re.search(r'chr\s*\([^)]+\)\s*\|\|', p_lower))
    # PostgreSQL: chr(X)||chr(Y) sometimes also works in PG, but ::cast is definitive
    has_postgres_strong = bool(re.search(r'::\s*(text|int|integer|numeric)', p_lower)) or contains_any(payload, ['pg_sleep(', 'generate_series(', 'pg_read_file('])
    has_oracle_strong = contains_any(payload, ['xmltype(', 'dbms_pipe.', 'utl_inaddr.', 'ctxsys.', 'from dual', 'utl_http.']) or has_oracle_chr_chain
    
    # MySQL markers
    has_mysql_comment = p_lower.strip().endswith('#') or ' #' in p_lower or '# ' in p_lower
    has_mysql_error = contains_any(payload, ['extractvalue(', 'updatexml(', 'floor(rand(', 'exp(~('])
    has_mysql_info = 'information_schema.' in p_lower
    has_mysql_sleep = contains_any(payload, ['sleep(', 'benchmark('])
    has_mysql_elt = bool(re.search(r'\belt\b', p_lower))
    has_mysql_rlike = 'rlike' in p_lower
    
    # MSSQL
    has_mssql_waitfor = 'waitfor delay' in p_lower
    has_mssql_convert = bool(re.search(r'convert\s*\(\s*int', p_lower))
    has_mssql_sys = contains_any(payload, ['master..', 'sysobjects', 'syscolumns', 'sysusers'])
    
    # SQLite
    has_sqlite_rblob = 'randomblob(' in p_lower
    has_sqlite_like_hex = bool(re.search(r'like\s*\(\s*[\'\"](abcdefg|abcdef)', p_lower))
    
    # --- Decision logic ---
    
    # Oracle: xmltype or dbms_pipe or utl_inaddr or ctxsys or from dual + chr|| chain
    if has_oracle_strong and not has_postgres_strong:
        if has_oracle_chr_chain or contains_any(payload, ['xmltype(', 'dbms_pipe.', 'utl_inaddr.', 'ctxsys.', 'from dual']):
            return 'oracle'
    
    # PostgreSQL: ::cast or pg_sleep or generate_series
    if has_postgres_strong:
        return 'postgresql'
    
    # SQLite
    if has_sqlite_rblob or has_sqlite_like_hex:
        return 'sqlite'
    
    # MSSQL
    if has_mssql_waitfor or has_mssql_convert or has_mssql_sys:
        return 'mssql'
    
    # MySQL: various markers
    if has_mysql_comment and (has_mysql_error or has_mysql_info or has_mysql_sleep or has_mysql_elt or has_mysql_rlike):
        return 'mysql'
    
    # More MySQL checks
    if contains_any(payload, ['sleep(', 'benchmark(']) and not has_postgres_strong:
        return 'mysql'
    
    if has_mysql_error:
        return 'mysql'
    
    if 'information_schema.' in p_lower and not has_postgres_strong:
        return 'mysql'
    
    # elt() with sleep is MySQL
    if has_mysql_elt:
        return 'mysql'
    
    # rlike is MySQL
    if has_mysql_rlike:
        return 'mysql'
    
    # make_set is MySQL
    if 'make_set(' in p_lower:
        return 'mysql'
    
    # procedure analyse is MySQL
    if 'procedure analyse' in p_lower:
        return 'mysql'
    
    # Oracle by default if has || chains
    if has_oracle_chr_chain:
        return 'oracle'
    
    # char()+char() with + operator is MSSQL/MySQL
    if bool(re.search(r'char\s*\([^)]+\)\s*\+', p_lower)):
        # Could be MSSQL or MySQL, check for int conversion
        if has_mssql_convert:
            return 'mssql'
        return 'mysql'  # MySQL sometimes uses + too, but MSSQL uses + for concat more
    
    # elt() is MySQL
    if has_mysql_elt:
        return 'mysql'
    
    # # ending is MySQL
    if has_mysql_comment:
        return 'mysql'
    
    # waitfor
    if has_mssql_waitfor:
        return 'mssql'
    
    return 'generic'


# ---------- type detection ----------
def detect_type(payload, engine):
    p_lower = payload.lower()
    
    # Priority 1: UNION
    if 'union select' in p_lower or 'union all select' in p_lower:
        # Check if also has error marker -> error_based per guide
        has_error = contains_any(payload, [
            'convert(int,', 'convert(varchar,', 'xmltype(', 'extractvalue(', 'updatexml(',
            'floor(rand(', 'exp(~(', 'utl_inaddr.', 'ctxsys.',
        ])
        if has_error and ('convert(int,' in p_lower or 'convert(varchar,' in p_lower):
            return 'error_based', 0.85
        # ORDER BY with union prep
        if 'order by' in p_lower and 'union' not in p_lower.split('order by')[0]:
            # ORDER BY is preparation, but UNION is in payload
            pass
        # Check if error marker in same payload
        if has_error:
            return 'error_based', 0.85
        return 'union_based', 1.00
    
    # Priority 2: ORDER BY alone (union prep)
    if 'order by ' in p_lower and 'union' not in p_lower:
        # Could be union preparation
        # Only label as union_based if it's clearly probing column count
        if re.search(r'order by \s*\d+\s*#', p_lower) or re.search(r'order by \s*\d+\s*--', p_lower):
            return 'union_based', 0.85
        # Otherwise just boolean_blind with order by
        return 'boolean_blind', 0.85
    
    # Priority 3: Time-based markers
    has_time = False
    # sleep() - MySQL
    if re.search(r'sleep\s*\(\s*\d+\s*\)', p_lower):
        has_time = True
    elif 'pg_sleep(' in p_lower:
        has_time = True
    elif 'waitfor delay' in p_lower:
        has_time = True
    elif 'dbms_pipe.receive_message' in p_lower and not contains_any(payload, ['xmltype(', 'extractvalue(', 'updatexml(']):
        has_time = True
    elif 'benchmark(' in p_lower:
        has_time = True
    elif 'generate_series' in p_lower and '50000' in p_lower:
        has_time = True
    # randomblob heavy computation
    elif 'randomblob(' in p_lower and ('500000' in p_lower or '1000000' in p_lower):
        has_time = True
    # regexp_substring with heavy repeat
    elif 'regexp_substring' in p_lower and ('500000000' in p_lower or '50000000' in p_lower):
        has_time = True
    
    if has_time:
        # If it has CASE WHEN but sleep is the primary purpose
        if 'case when' in p_lower and 'then' in p_lower:
            # Check if sleep is inside the THEN clause
            if re.search(r'then\s+.*sleep', p_lower) or re.search(r'then\s+.*benchmark', p_lower):
                return 'time_blind', 1.00
            # dbms_pipe with CASE WHEN is still time_blind if dbms_pipe is there  
            if 'dbms_pipe.receive_message' in p_lower:
                return 'time_blind', 1.00
        return 'time_blind', 1.00
    
    # Priority 4: Error-based markers
    has_error = False
    # floor(rand) + group by
    if 'floor(rand(' in p_lower and 'group by' in p_lower:
        has_error = True
    if 'extractvalue(' in p_lower:
        has_error = True
    if 'updatexml(' in p_lower:
        has_error = True
    if 'xmltype(' in p_lower:
        has_error = True
    if 'utl_inaddr.' in p_lower:
        has_error = True
    if 'ctxsys.' in p_lower:
        has_error = True
    if 'exp(~(' in p_lower:
        has_error = True
    if 'convert(int,' in p_lower:
        has_error = True
    
    if has_error:
        # Check if it also has CASE WHEN but error marker dominates
        if contains_any(payload, ['xmltype(', 'utl_inaddr.', 'ctxsys.']) and engine == 'oracle':
            return 'error_based', 1.00
        if 'floor(rand(' in p_lower and 'group by' in p_lower:
            return 'error_based', 1.00
        if 'extractvalue(' in p_lower or 'updatexml(' in p_lower:
            return 'error_based', 1.00
        if 'exp(~(' in p_lower:
            return 'error_based', 1.00
        if 'convert(int,' in p_lower:
            return 'error_based', 0.85  # Could be ambiguous with union
        return 'error_based', 0.85
    
    # Priority 5: Boolean-based (CASE WHEN, IF, IIF, simple OR/AND)
    has_boolean = False
    if re.search(r'case\s+when', p_lower):
        has_boolean = True
    if re.search(r'\bif\s*\(', p_lower):
        has_boolean = True
    if 'iif(' in p_lower:
        has_boolean = True
    if 'rlike' in p_lower:
        has_boolean = True
    if bool(re.search(r'\belt\b', p_lower)):
        has_boolean = True
    
    # Simple boolean comparisons
    if re.search(r'\d+\s*=\s*\d+', p_lower) and not has_boolean:
        # Very short payload with just number comparison
        tokens = p_lower.split()
        if len(tokens) <= 4:
            payload_clean = payload.strip()
            # Generic simple test
            if re.match(r'^[\d\s\'\"()=<>!]+\s*--?\s*$', payload_clean, re.IGNORECASE):
                pass  # Will be boolean_blind
            has_boolean = True  # Still boolean in nature
            return 'boolean_blind', 0.70
    
    if has_boolean:
        return 'boolean_blind', 1.00
    
    # Fallback: check for simple AND/OR conditions
    if re.search(r'\d+\s*=\s*\d+', p_lower):
        return 'boolean_blind', 0.70
    
    # Check for classic auth bypass
    if re.search(r"'\s*or\s*'", p_lower) or re.search(r"'\s*or\s+1\s*=\s*1", p_lower) or re.search(r"or\s+['\"]\d+['\"]\s*=\s*['\"]", p_lower):
        return 'boolean_blind', 0.85
    
    # Check for comment injection (--, #)
    if '--' in payload or '#' in payload:
        return 'boolean_blind', 0.70
    
    return 'boolean_blind', 0.70


# ---------- main ----------
def classify(payload, pid):
    engine = detect_engine(payload)
    sqli_type, confidence = detect_type(payload, engine)
    
    # ---- confidence adjustments ----
    
    # If payload is very short and generic, lower confidence
    tokens = payload.split()
    clean = payload.strip().strip("'\"")
    
    # Very short payloads
    if len(tokens) <= 2:
        # Just a number or a simple comparison
        if re.match(r'^-?\d+\'?$', clean):
            return pid, 'boolean_blind', 'generic', 0.70
        if re.match(r'^[-\d\s\'\"=<>!]+$', clean) and len(clean) < 10:
            return pid, 'boolean_blind', 'generic', 0.70
    
    # If engine is generic but payload has some structure
    if engine == 'generic':
        if len(tokens) <= 3:
            return pid, sqli_type, 'generic', 0.70
    
    # Oracle with just chr||chain without specific Oracle function
    if engine == 'oracle' and not contains_any(payload, ['xmltype(', 'dbms_pipe.', 'utl_inaddr.', 'ctxsys.', 'dbms_utility.', 'from dual']):
        # Has chr|| but no specific Oracle function
        if not re.search(r'from\s+dual', payload.lower()):
            confidence = min(confidence, 0.85)
    
    # Generic engine with boolean type, short payload
    if engine == 'generic' and sqli_type == 'boolean_blind':
        if len(tokens) <= 5:
            confidence = 0.70
    
    # If engine is generic but we're very sure about type
    if engine == 'generic' and sqli_type == 'union_based':
        confidence = 0.85  # UNION is always union_based, but without engine markers
    
    # If engine is oracle with xmltype + dual + chr chain
    if engine == 'oracle' and contains_any(payload, ['xmltype(']) and 'from dual' in payload.lower():
        if sqli_type == 'error_based':
            confidence = 1.00
    
    # If engine is mysql with floor(rand)+group by
    if engine == 'mysql' and 'floor(rand(' in payload.lower() and 'group by' in payload.lower():
        if sqli_type == 'error_based':
            confidence = 1.00
    
    # postgresql with ::cast and case when = boolean_blind
    if engine == 'postgresql' and sqli_type == 'boolean_blind' and re.search(r'::\s*(text|int|integer|numeric)', payload.lower()):
        if 'case when' in payload.lower():
            confidence = 1.00
    
    # mssql with convert(int and case when
    if engine == 'mssql' and 'convert(int,' in payload.lower() and 'case when' in payload.lower():
        confidence = 0.85  # Could be ambiguous
    
    # time_blind with mysql markers → 1.00
    if sqli_type == 'time_blind' and engine == 'mysql' and re.search(r'sleep\s*\(\s*\d+\s*\)', payload.lower()):
        confidence = 1.00
    
    # time_blind with generate_series and large number
    if sqli_type == 'time_blind' and 'generate_series' in payload.lower():
        confidence = 1.00
    
    return pid, sqli_type, engine, confidence


# ---------- process ----------
with open('SeqGAN_SQLi/data/split_data.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    results = []
    for row in reader:
        pid = int(row['id'])
        if 3501 <= pid <= 6000:
            payload = row['payload_norm']
            pid_out, stype, engine, conf = classify(payload, pid)
            results.append((pid_out, stype, engine, conf))

# Write output
output_path = 'SeqGAN_SQLi/data/split_data_labeled_batch_3501_6000.csv'
with open(output_path, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'sqli_type', 'db_engine', 'confidence'])
    writer.writerows(results)

# Summary
from collections import Counter
type_counts = Counter(r[1] for r in results)
engine_counts = Counter(r[2] for r in results)
conf_counts = Counter(r[3] for r in results)

print(f"Total labeled: {len(results)} rows")
print(f"\nType distribution:")
for t, c in type_counts.most_common():
    print(f"  {t}: {c}")
print(f"\nEngine distribution:")
for e, c in engine_counts.most_common():
    print(f"  {e}: {c}")
print(f"\nConfidence distribution:")
for c_val, cnt in conf_counts.most_common():
    print(f"  {c_val}: {cnt}")

print(f"\nOutput saved to: {output_path}")
