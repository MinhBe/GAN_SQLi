import csv, sys, re

csv.field_size_limit(2**31-1)

# ---------- helpers ----------
def in_any(p, keywords):
    p_lower = p.lower()
    for k in keywords:
        if k.lower() in p_lower:
            return True
    return False

def find_func(payload, func_name):
    """Match func_name optionally followed by whitespace then ("""
    return re.search(rf'\b{func_name}\s*\(', payload, re.IGNORECASE)

# ---------- engine detection ----------
def detect_engine(payload):
    p_lower = payload.lower()

    has_mysql_end_hash = bool(re.search(r'#\s*$', payload)) or bool(re.search(r'#\s+', payload))
    has_mysql_info = 'information_schema.' in p_lower
    has_mysql_rlike = bool(re.search(r'\brlike\b', p_lower))
    has_mysql_elt = bool(re.search(r'\belt\s*\(', p_lower))
    has_mysql_make_set = bool(re.search(r'\bmake_set\s*\(', p_lower))
    has_mysql_procedure = 'procedure analyse' in p_lower
    has_mysql_floor = bool(re.search(r'\bfloor\s*\(\s*rand\s*\(', p_lower))
    has_mysql_exp = bool(re.search(r'\bexp\s*\(', p_lower))
    has_mysql_sleep = bool(re.search(r'\bsleep\s*\(', p_lower))
    has_mysql_benchmark = bool(re.search(r'\bbenchmark\s*\(', p_lower))

    has_oracle_xmltype = bool(find_func(payload, 'xmltype'))
    has_oracle_dbms_pipe = bool(re.search(r'dbms_pipe\.receive_message\s*\(', p_lower))
    has_oracle_utl_inaddr = bool(find_func(payload, 'utl_inaddr')) or bool(re.search(r'utl_inaddr\.', p_lower))
    has_oracle_ctxsys = bool(find_func(payload, 'ctxsys'))
    has_oracle_dbms_utility = bool(find_func(payload, 'dbms_utility'))
    has_oracle_dual = bool(re.search(r'\bfrom\s+dual\b', p_lower))
    has_oracle_all_tables = bool(re.search(r'\ball_tables\b', p_lower))
    has_oracle_all_users = bool(re.search(r'\ball_users\b', p_lower))
    has_oracle_rownum = bool(re.search(r'\brownum\b', p_lower))
    # chr chain with ||
    has_oracle_chr_chain = bool(re.search(r'chr\s*\([^)]*\)\s*\|\|', p_lower))

    has_postgres_cast = bool(re.search(r'::\s*(text|int(eger)?|numeric)', p_lower))
    has_pg_sleep = bool(find_func(payload, 'pg_sleep'))
    has_generate_series = bool(find_func(payload, 'generate_series'))
    has_pg_read = bool(find_func(payload, 'pg_read_file'))

    has_sqlite_rblob = bool(find_func(payload, 'randomblob'))
    has_sqlite_sqlite_version = bool(find_func(payload, 'sqlite_version'))
    has_sqlite_master = bool(re.search(r'\bsqlite_master\b', p_lower))

    has_mssql_waitfor = 'waitfor delay' in p_lower
    has_mssql_convert = bool(re.search(r'convert\s*\(\s*int', p_lower))
    has_mssql_master = bool(re.search(r'master\.\.', p_lower))
    has_mssql_sysobjects = bool(re.search(r'\bsysobjects\b', p_lower))

    # --- Decision ---
    # Strong Oracle
    if (has_oracle_xmltype or has_oracle_utl_inaddr or has_oracle_ctxsys or
        has_oracle_dbms_pipe or has_oracle_dbms_utility or has_oracle_all_users):
        return 'oracle'

    # Oracle with dual + chr chain
    if has_oracle_dual and has_oracle_chr_chain:
        return 'oracle'

    # Strong PostgreSQL
    if has_postgres_cast or has_pg_sleep or has_pg_read:
        return 'postgresql'

    # SQLite
    if has_sqlite_rblob or has_sqlite_sqlite_version or has_sqlite_master:
        return 'sqlite'

    # MSSQL
    if has_mssql_waitfor or has_mssql_convert or has_mssql_master or has_mssql_sysobjects:
        return 'mssql'

    # MySQL definite markers
    if has_mysql_floor or has_mysql_exp:
        return 'mysql'
    if has_mysql_rlike:
        return 'mysql'
    if has_mysql_elt:
        return 'mysql'
    if has_mysql_make_set:
        return 'mysql'
    if has_mysql_procedure:
        return 'mysql'
    if has_mysql_info and has_mysql_end_hash:
        return 'mysql'

    # has generate_series but no pg markers -> could be pg
    if has_generate_series:
        return 'postgresql'

    # sleep/benchmark without other engine markers -> likely mysql
    if has_mysql_sleep or has_mysql_benchmark:
        return 'mysql'

    # information_schema without oracle/pg -> mysql
    if has_mysql_info:
        return 'mysql'

    # char(..) + char(..) with + operator -> mssql or mysql
    if bool(re.search(r'char\s*\([^)]*\)\s*\+', p_lower)):
        return 'mssql'

    # oracle chr|| chain left
    if has_oracle_chr_chain:
        return 'oracle'

    # # hash at end
    if has_mysql_end_hash:
        return 'mysql'

    return 'generic'


# ---------- type detection ----------
def detect_type(payload, engine):
    p_lower = payload.lower()

    # Function matching helpers
    def has_func(name):
        return bool(find_func(payload, name))

    # ---- Priority 1: UNION ----
    has_union = bool(re.search(r'\bunion\s+(all\s+)?select\b', p_lower))
    if has_union:
        # Check for error function in the main context (not just subquery)
        # If UNION is inside a subquery (nested), treat as the outer technique
        has_error_outer = (
            has_func('convert') and int_conv and False or
            has_func('xmltype') or has_func('extractvalue') or
            has_func('updatexml') or
            (has_func('floor') and bool(re.search(r'\bgroup\s+by\b', p_lower)))
        )
        # Simple: just check if these exist anywhere
        has_any_error = (
            has_func('xmltype') or has_func('extractvalue') or has_func('updatexml') or
            has_func('utl_inaddr') or has_func('ctxsys') or
            has_func('exp') or
            (has_func('floor') and bool(re.search(r'\bgroup\s+by\b', p_lower)))
        )
        # If error marker present alongside UNION, check if UNION is top-level or nested
        # Count UNION depth
        if has_any_error:
            return 'error_based', 0.85
        return 'union_based', 1.00

    # ---- Priority 2: ORDER BY (union prep) ----
    if re.search(r'\border\s+by\s+\d+', p_lower):
        # Could be union column probe or legitimate order by
        if re.search(r'order\s+by\s+\d+\s*(#|--)', payload, re.IGNORECASE):
            return 'union_based', 0.85
        return 'boolean_blind', 0.85

    # ---- Priority 3: Time-based ----
    has_time = False

    # Generic sleep(pattern) - also match templates like [VALUE]
    if re.search(r'(?:sleep|pg_sleep)\s*\(\s*(?:\d+|\[)', p_lower):
        has_time = True
    # WAITFOR DELAY
    if 'waitfor delay' in p_lower:
        has_time = True
    # dbms_pipe.receive_message (standalone, not with error functions)
    if has_func('dbms_pipe.receive_message') and not has_func('xmltype'):
        has_time = True
    # benchmark(heavy, ...)
    if has_func('benchmark'):
        has_time = True
    # generate_series with large number
    if has_func('generate_series') and ('500000' in p_lower or '1000000' in p_lower or '50000' in p_lower):
        has_time = True
    # randomblob heavy
    if has_func('randomblob') and ('500000' in p_lower or '1000000' in p_lower):
        has_time = True
    # regexp_substring heavy computation
    if has_func('regexp_substring') or has_func('regexp_substr'):
        if '500000000' in p_lower or '50000000' in p_lower:
            has_time = True
        elif '5000000000' in p_lower:
            has_time = True
    # like('abcdefg', upper(hex(randomblob(...)))) - SQLite time
    if has_func('like') and 'randomblob' in p_lower:
        has_time = True
    # like('abcdefg', upper(...)) heavy pattern
    if has_func('like') and ("'abcdefg'" in p_lower or '"abcdefg"' in p_lower):
        if 'randomblob' in p_lower or '500000000' in p_lower:
            has_time = True

    # Heavy cartesian join of Oracle system tables (all_users x N, all_tables x N)
    if re.search(r'from\s+all_users\s+\w+,\s*all_users', p_lower) or re.search(r'from\s+all_tables\s+\w+,\s*all_tables', p_lower):
        # Multiple joins of same system table = heavy cartesian
        count_matches = len(re.findall(r'\ball_users\b', p_lower))
        if count_matches >= 4:
            has_time = True

    if has_time:
        return 'time_blind', 1.00

    # ---- Priority 4: Error-based ----
    has_error = False

    # floor(rand()) + group by
    if has_func('floor') and re.search(r'rand\s*\(', p_lower) and re.search(r'group\s+by', p_lower):
        has_error = True
    # extractvalue
    if has_func('extractvalue'):
        has_error = True
    # updatexml
    if has_func('updatexml'):
        has_error = True
    # xmltype (Oracle error)
    if has_func('xmltype'):
        has_error = True
    # utl_inaddr (can be utl_inaddr.get_host_address(...))
    if bool(re.search(r'utl_inaddr', p_lower)):
        has_error = True
    # ctxsys
    if has_func('ctxsys'):
        has_error = True
    # exp(~(...)) - MySQL double-query error
    if has_func('exp') and re.search(r'~\s*\(', p_lower):
        has_error = True
    # convert(int, ...) - MSSQL conversion error
    if has_func('convert') and re.search(r'convert\s*\(\s*int', p_lower):
        has_error = True

    if has_error:
        if has_func('xmltype') or bool(re.search(r'utl_inaddr', p_lower)) or has_func('ctxsys'):
            return 'error_based', 1.00
        if has_func('floor') and re.search(r'group\s+by', p_lower):
            return 'error_based', 1.00
        if has_func('extractvalue') or has_func('updatexml'):
            return 'error_based', 1.00
        if has_func('exp') and re.search(r'~\s*\(', p_lower):
            return 'error_based', 1.00
        if has_func('convert') and re.search(r'convert\s*\(\s*int', p_lower):
            return 'error_based', 0.85
        return 'error_based', 0.85

    # ---- Priority 5: Boolean-based ----
    has_boolean = False
    if re.search(r'\bcase\s+when\b', p_lower):
        has_boolean = True
    if re.search(r'\bif\s*\(', p_lower) and not has_func('benchmark'):
        has_boolean = True
    if re.search(r'\biif\s*\(', p_lower):
        has_boolean = True
    if re.search(r'\brlike\b', p_lower):
        has_boolean = True
    if re.search(r'\belt\s*\(', p_lower):
        has_boolean = True
    if re.search(r'\bconvert\s*\(', p_lower):
        has_boolean = True

    if has_boolean:
        return 'boolean_blind', 1.00

    # Simple conditions (AND X=Y, OR X=Y)
    if re.search(r'\d+\s*=\s*\d+', p_lower):
        return 'boolean_blind', 0.70

    # Auth bypass
    if re.search(r"'\s*or\s*'", payload) or re.search(r"'\s*or\s*1\s*=\s*1", payload):
        return 'boolean_blind', 0.85

    # Comment injection
    if '--' in payload or '#' in payload:
        return 'boolean_blind', 0.70

    return 'boolean_blind', 0.70


# ---------- main ----------
def classify(payload, pid):
    engine = detect_engine(payload)
    sqli_type, confidence = detect_type(payload, engine)

    # ---- confidence adjustments ----
    p_lower = payload.lower()
    tokens = payload.split()
    clean = payload.strip().strip("'\"")

    # Very short payloads
    if len(tokens) <= 2:
        if re.match(r'^-?\d+\'?$', clean):
            return pid, 'boolean_blind', 'generic', 0.70
        if re.match(r'^[-\d\s\'\"=<>!]+$', clean) and len(clean) < 10:
            return pid, 'boolean_blind', 'generic', 0.70

    # Generic engine, short -> 0.70
    if engine == 'generic':
        if len(tokens) <= 3:
            return pid, sqli_type, 'generic', 0.70

    # Generic engine with boolean and few tokens
    if engine == 'generic' and sqli_type == 'boolean_blind':
        if len(tokens) <= 5:
            confidence = 0.70

    # Generic union -> 0.85
    if engine == 'generic' and sqli_type == 'union_based':
        confidence = 0.85

    # Engine mismatch adjustments
    if engine == 'oracle' and sqli_type in ('time_blind',):
        if not re.search(r'dbms_pipe\.receive_message', p_lower):
            confidence = 0.85

    # postgresql with ::cast and case when = boolean_blind 1.00
    if engine == 'postgresql' and sqli_type == 'boolean_blind':
        if re.search(r'::\s*(text|int(eger)?|numeric)', p_lower) and re.search(r'case\s+when', p_lower):
            confidence = 1.00

    # mssql with convert(int and case when
    if engine == 'mssql' and 'convert(int,' in p_lower.replace(' ', '') and 'case when' in p_lower:
        confidence = 0.85

    # time_blind with mysql markers -> 1.00
    if sqli_type == 'time_blind' and engine == 'mysql':
        confidence = 1.00

    # time_blind with generate_series -> 1.00
    if sqli_type == 'time_blind' and 'generate_series' in p_lower:
        confidence = 1.00

    # error_based with oracle strong markers -> 1.00
    if sqli_type == 'error_based' and engine == 'oracle':
        if re.search(r'xmltype|utl_inaddr|ctxsys', p_lower):
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
