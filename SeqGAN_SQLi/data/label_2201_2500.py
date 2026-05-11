import csv
import re

def classify_sqli(payload):
    p = payload.lower().strip()

    # ===== DB ENGINE DETECTION =====
    db_scores = {'oracle': 0, 'mysql': 0, 'postgresql': 0, 'mssql': 0, 'sqlite': 0}

    # Oracle (very specific)
    if re.search(r'xmltype\s*\(', p): db_scores['oracle'] += 3
    if re.search(r'from\s+dual', p): db_scores['oracle'] += 1.5
    if re.search(r'ctxsys\.', p): db_scores['oracle'] += 3
    if re.search(r'dbms_pipe\.', p): db_scores['oracle'] += 2
    if re.search(r'dbms_utility\.', p): db_scores['oracle'] += 2
    if re.search(r'utl_inaddr\.', p): db_scores['oracle'] += 3
    if re.search(r'utl_http\.', p): db_scores['oracle'] += 3
    if re.search(r'sys_context\s*\(', p): db_scores['oracle'] += 2
    if re.search(r'rownum\b', p): db_scores['oracle'] += 1
    if re.search(r'all_tables', p): db_scores['oracle'] += 1
    if re.search(r'regexp_substr\s*\(', p): db_scores['oracle'] += 1

    # PostgreSQL (very specific)
    if re.search(r'pg_sleep\s*\(', p): db_scores['postgresql'] += 3
    if re.search(r'::text\b', p): db_scores['postgresql'] += 2
    if re.search(r'::int\b', p): db_scores['postgresql'] += 2
    if re.search(r'::numeric\b', p): db_scores['postgresql'] += 2
    if re.search(r'generate_series\s*\(', p): db_scores['postgresql'] += 2
    if re.search(r'\$\$', p): db_scores['postgresql'] += 2
    if re.search(r'string_agg\s*\(', p): db_scores['postgresql'] += 2
    if re.search(r'array_agg\s*\(', p): db_scores['postgresql'] += 1

    # MySQL
    if re.search(r'benchmark\s*\(', p): db_scores['mysql'] += 2
    if re.search(r'group_concat\s*\(', p): db_scores['mysql'] += 2
    if re.search(r'floor\s*\(\s*rand\s*\(', p): db_scores['mysql'] += 2
    if re.search(r'extractvalue\s*\(', p): db_scores['mysql'] += 2
    if re.search(r'updatexml\s*\(', p): db_scores['mysql'] += 2
    if re.search(r'information_schema\.', p): db_scores['mysql'] += 1.5
    if re.search(r'make_set\s*\(', p): db_scores['mysql'] += 1.5
    if re.search(r'procedure\s+analyse', p): db_scores['mysql'] += 2
    if re.search(r'crypt_key\s*\(', p): db_scores['mysql'] += 2
    if re.search(r'md5\s*\(', p): db_scores['mysql'] += 1
    if re.search(r'regexp_substring\s*\(', p): db_scores['mysql'] += 1
    if re.search(r'#', p): db_scores['mysql'] += 0.5
    # sleep() is MySQL but check not pg_sleep
    if re.search(r'(?<!pg_)sleep\s*\(', p): db_scores['mysql'] += 1.5

    # MSSQL
    if re.search(r'waitfor\s+delay', p): db_scores['mssql'] += 2
    if re.search(r'master\.\.sysdatabases', p): db_scores['mssql'] += 3
    if re.search(r'sysobjects', p): db_scores['mssql'] += 2
    if re.search(r'syscolumns', p): db_scores['mssql'] += 1
    if re.search(r'sysusers', p): db_scores['mssql'] += 1
    if re.search(r'convert\s*\(\s*int\s*,', p): db_scores['mssql'] += 2
    if re.search(r'@@servername', p): db_scores['mssql'] += 2
    if re.search(r'xp_cmdshell', p): db_scores['mssql'] += 3
    # char(N)+char(N)+ pattern (MSSQL, not Oracle ||)
    if re.search(r'char\s*\(\s*\d+\s*\)\s*\+', p): db_scores['mssql'] += 1.5

    # SQLite
    if re.search(r'randomblob\s*\(', p): db_scores['sqlite'] += 2
    if re.search(r'sqlite_version\s*\(', p): db_scores['sqlite'] += 2
    if re.search(r'sqlite_master', p): db_scores['sqlite'] += 2
    if re.search(r'like\s*\(\s*\'abcdefg\'', p): db_scores['sqlite'] += 2

    # Determine db_engine
    active = {k: v for k, v in db_scores.items() if v > 0}
    if not active:
        db_engine = 'generic'
    else:
        max_engine = max(active, key=active.get)
        max_score = active[max_engine]
        # Check for ties or near-ties
        sorted_engines = sorted(active.items(), key=lambda x: -x[1])
        if len(sorted_engines) > 1 and sorted_engines[0][1] - sorted_engines[1][1] <= 1:
            # Tiebreaker: Oracle markers ưu tiên cao nhất
            if 'oracle' in active:
                # Only if oracle has meaningful score
                if active['oracle'] >= 1.5:
                    max_engine = 'oracle'
                elif 'postgresql' in active and active['postgresql'] >= 2:
                    max_engine = 'postgresql'
            elif 'postgresql' in active and active['postgresql'] >= 2:
                max_engine = 'postgresql'
        db_engine = max_engine

    # ===== SQLI TYPE DETECTION =====
    has_union = bool(re.search(r'union\s+(all\s+)?select', p))
    has_order_by = bool(re.search(r'order\s+by\s+\d+', p))
    has_case_when = bool(re.search(r'case\s+when', p))
    has_pg_sleep = bool(re.search(r'pg_sleep\s*\(', p))
    has_mysql_sleep = bool(re.search(r'(?<!pg_)sleep\s*\(', p))
    has_benchmark = bool(re.search(r'benchmark\s*\(', p))
    has_waitfor = bool(re.search(r'waitfor\s+delay', p))
    has_dbms_pipe = bool(re.search(r'dbms_pipe\.receive_message\s*\(', p))
    has_generate_series = bool(re.search(r'generate_series\s*\(', p))
    has_randomblob = bool(re.search(r'randomblob\s*\(', p))
    has_regexp_repeat = bool(re.search(r'regexp_substring\s*\(\s*repeat\s*\(', p))
    has_like_abcdefg = bool(re.search(r'like\s*\(\s*\'abcdefg\'', p))

    # Error-based markers
    has_xmltype = bool(re.search(r'xmltype\s*\(', p))
    has_ctxsys = bool(re.search(r'ctxsys\.', p))
    has_floor_rand = bool(re.search(r'floor\s*\(\s*rand\s*\(', p))
    has_extractvalue = bool(re.search(r'extractvalue\s*\(', p))
    has_updatexml = bool(re.search(r'updatexml\s*\(', p))
    has_convert_int = bool(re.search(r'convert\s*\(\s*int\s*,', p))
    has_exp_tilde = bool(re.search(r'exp\s*\(\s*~', p))
    # cast( ... as numeric/int) with CASE WHEN for error-based PG
    has_cast_as_numeric = bool(re.search(r'cast\s*\(.*::text.*as\s+(numeric|int)', p))
    has_utl_inaddr = bool(re.search(r'utl_inaddr\.', p))

    error_score = sum([has_xmltype, has_ctxsys, has_floor_rand,
                       has_extractvalue, has_updatexml,
                       has_convert_int, has_exp_tilde,
                       has_utl_inaddr])

    # Time markers
    time_score = sum([has_pg_sleep, has_mysql_sleep, has_benchmark,
                      has_waitfor, has_dbms_pipe, has_randomblob,
                      has_regexp_repeat, has_like_abcdefg])

    # generate_series with large number = time
    has_large_generate_series = bool(re.search(r'generate_series\s*\(\s*1\s*,\s*[5-9]\d{5,}', p))
    if has_large_generate_series:
        time_score += 1

    # Boolean markers
    has_and_eq = bool(re.search(r'\band\s+\d+=\d+', p))
    has_or_eq = bool(re.search(r'\bor\s+\d+=\d+', p))
    has_rlike = bool(re.search(r'rlike\s*\(', p))
    has_elt = bool(re.search(r'elt\s*\(', p))
    has_if_func = bool(re.search(r'\bif\s*\(', p))
    has_iif = bool(re.search(r'\biif\s*\(', p))
    has_or_quote = bool(re.search(r"or\s+'.*?='", p))

    boolean_score = sum([has_case_when, has_and_eq, has_or_eq,
                         has_rlike, has_elt, has_if_func,
                         has_iif, has_or_quote])

    # ---- Decision Logic ----
    sqli_type = 'boolean_blind'
    conf = 0.70

    # PRIORITY 1: time_blind (time markers take precedence when clear)
    if has_pg_sleep or has_waitfor or has_randomblob or has_like_abcdefg:
        sqli_type = 'time_blind'
        conf = 1.00
        if db_engine == 'generic':
            if has_pg_sleep: db_engine = 'postgresql'
            elif has_waitfor: db_engine = 'mssql'
            elif has_randomblob or has_like_abcdefg: db_engine = 'sqlite'
    elif has_mysql_sleep and not has_error_function_override(p):
        sqli_type = 'time_blind'
        conf = 1.00
        if db_engine == 'generic':
            db_engine = 'mysql'
    elif has_dbms_pipe:
        # dbms_pipe.receive_message standalone = time_blind
        if not has_xmltype:
            sqli_type = 'time_blind'
            conf = 1.00
            if db_engine == 'generic': db_engine = 'oracle'
    elif has_benchmark:
        sqli_type = 'time_blind'
        conf = 1.00
        if db_engine == 'generic': db_engine = 'mysql'
    elif has_large_generate_series:
        sqli_type = 'time_blind'
        conf = 1.00
        if db_engine == 'generic': db_engine = 'postgresql'
    elif has_regexp_repeat:
        sqli_type = 'time_blind'
        conf = 0.85
        if db_engine == 'generic': db_engine = 'mysql'

    # PRIORITY 2: error_based (strong error markers)
    elif error_score >= 1:
        sqli_type = 'error_based'

        if has_xmltype and db_engine == 'oracle':
            conf = 1.00
        elif has_ctxsys:
            conf = 1.00
        elif has_floor_rand:
            conf = 1.00
        elif has_convert_int and db_engine == 'mssql':
            conf = 1.00
        elif has_extractvalue or has_updatexml:
            conf = 1.00
        elif has_cast_as_numeric and has_case_when:
            # PostgreSQL error-based via cast
            conf = 0.85 if has_union else 1.00
        elif has_exp_tilde:
            conf = 0.85  # exp(~...) can be error or just heavy
        elif has_union:
            conf = 0.85  # UNION + error marker
        else:
            conf = 0.85

    # PRIORITY 3: union_based
    elif has_union:
        sqli_type = 'union_based'
        conf = 1.00
        if has_order_by and not has_union:
            conf = 0.85
        if len(re.findall(r'\S+', p)) < 5:
            conf = 0.85

    # PRIORITY 4: boolean_blind
    elif boolean_score >= 1:
        sqli_type = 'boolean_blind'
        if db_engine != 'generic' and boolean_score >= 2:
            conf = 1.00
        elif db_engine != 'generic':
            conf = 0.85
        else:
            conf = 0.70

        # ORDER BY without UNION = union probe
        if has_order_by and not has_union:
            sqli_type = 'union_based'
            conf = 0.85

    # ORDER BY standalone
    elif has_order_by:
        sqli_type = 'union_based'
        conf = 0.85

    # Fallback
    else:
        sqli_type = 'boolean_blind'
        db_engine = 'generic'
        conf = 0.70

    # ---- Adjustments ----
    # Template payloads
    if re.search(r'\[RANDNUM\]|\[INFERENCE\]|\[SLEEPTIME\]|\[DELIMITER', p):
        conf = min(conf, 0.85)

    # Very short payload adjustment
    tokens = len(re.findall(r'\S+', p))
    if tokens <= 2:
        sqli_type = 'boolean_blind'
        db_engine = 'generic'
        conf = 0.70
    elif tokens <= 3 and conf > 0.85:
        conf = 0.85

    # db_engine tiebreaker: if oracle has dual but pg has ::text, prefer pg
    if db_engine == 'oracle':
        has_strong_pg = bool(re.search(r'::text|::numeric|::int', p))
        # If pg has very specific markers, re-evaluate
        if has_strong_pg and not has_xmltype and not has_ctxsys:
            db_engine = 'postgresql'

    # Ensure confidence is correct format
    if conf >= 1.0:
        conf = 1.00
    elif conf >= 0.85:
        conf = 0.85
    else:
        conf = 0.70

    return sqli_type, db_engine, f"{conf:.2f}"


def has_error_function_override(p):
    """Check if payload has error functions alongside sleep for ambiguous cases"""
    p_lower = p.lower()
    error_funcs = ['xmltype', 'extractvalue', 'updatexml', 'ctxsys.',
                   'floor(rand(', 'convert(int,']
    sleep_funcs = ['sleep(', 'pg_sleep(']
    has_error = any(f in p_lower for f in error_funcs)
    has_sleep = any(f in p_lower for f in sleep_funcs)
    # If error + sleep, check which comes first
    if has_error and has_sleep:
        first_error = min((p_lower.find(f) for f in error_funcs if f in p_lower), default=9999)
        first_sleep = min((p_lower.find(f) for f in sleep_funcs if f in p_lower), default=9999)
        # If error comes before sleep, error_based
        return first_error < first_sleep
    return False


def main():
    input_file = "split_data.csv"
    rows = []
    start_id = 2501
    end_id = 2800
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = int(row['id'])
            if start_id <= rid <= end_id:
                payload = row['payload_norm']
                sqli_type, db_engine, confidence = classify_sqli(payload)
                rows.append((rid, sqli_type, db_engine, confidence))

    output_file = f"split_data_labeled_batch_{start_id}_{end_id}.csv"
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'sqli_type', 'db_engine', 'confidence'])
        for rid, st, de, cf in rows:
            writer.writerow([rid, st, de, cf])

    print(f"Done! {len(rows)} rows written to {output_file}")
    # Show distribution
    types = {}
    engines = {}
    for _, st, de, _ in rows:
        types[st] = types.get(st, 0) + 1
        engines[de] = engines.get(de, 0) + 1
    print("\nType distribution:", dict(sorted(types.items())))
    print("Engine distribution:", dict(sorted(engines.items())))


if __name__ == '__main__':
    main()
