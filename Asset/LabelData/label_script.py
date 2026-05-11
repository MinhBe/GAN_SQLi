import csv
import re

def token_count(payload):
    return len(payload.strip().split())

def normalize(text):
    # Remove extra whitespace, lowercase for matching
    text = re.sub(r'\s+', ' ', text).strip()
    return text

def classify_sqli(payload_norm):
    pl = normalize(payload_norm).lower()
    
    # === ENGINE DETECTION (Oracle has highest priority) ===
    oracle_markers = [
        'xmltype(', 'dbms_pipe.receive_message', 'utl_inaddr', 'utl_http',
        'sys_context(', 'from dual', 'ctxsys.drithsx.sn', 'dbms_utility',
        'rownum'
    ]
    # Check for chr()||chr() chain pattern (Oracle concatenation)
    oracle_chr_chain = bool(re.search(r'chr\s*\(\s*\d+\s*\)\s*\|\|\s*chr\s*\(\s*\d+\s*\)', pl))
    
    mysql_markers = [
        'sleep(', 'benchmark(', 'group_concat(', 'floor(rand(', 'extractvalue(',
        'updatexml(', 'information_schema.', 'load_file(', 'into outfile',
        '@@version', '@@datadir', 'mysql.db', 'make_set(', 'elt(', 'rlike'
    ]
    mysql_hash_comment = pl.rstrip().endswith('#')
    
    postgresql_markers = [
        'pg_sleep(', 'generate_series(', '::text', '::int', '::numeric',
        'string_agg(', 'array_agg(', 'pg_read_file('
    ]
    
    mssql_markers = [
        'waitfor delay', 'master..sysdatabases', 'xp_cmdshell',
        '@@servername', 'sysobjects', 'syscolumns', 'sysusers'
    ]
    # MSSQL char()+char()+ pattern
    mssql_char_chain = bool(re.search(r'char\s*\(\s*\d+\s*\)\s*\+\s*char\s*\(\s*\d+\s*\)', pl))
    
    sqlite_markers = [
        'randomblob(', 'sqlite_version(', 'sqlite_master'
    ]
    
    # === TYPE DETECTION ===
    has_xmltype = 'xmltype(' in pl
    has_extractvalue = 'extractvalue(' in pl
    has_updatexml = 'updatexml(' in pl
    has_floor_rand_group = 'floor(rand(' in pl and 'group by' in pl
    has_convert_int = bool(re.search(r'convert\s*\(\s*int', pl)) and bool(re.search(r'cast\s*\(.*\s+as\s+int', pl))
    has_utl_inaddr = 'utl_inaddr.get_host_address(' in pl
    has_ctxsys = 'ctxsys.drithsx.sn(' in pl
    has_dbms_utility = 'dbms_utility' in pl
    
    # Also treat standalone xmltype (without sleep/pg_sleep/WAITFOR/UNION) as error_based trigger
    has_error_trigger = has_xmltype or has_extractvalue or has_updatexml or has_floor_rand_group or has_utl_inaddr or has_ctxsys or has_dbms_utility
    
    has_sleep = 'sleep(' in pl
    has_pg_sleep = 'pg_sleep(' in pl
    has_waitfor = 'waitfor delay' in pl
    has_benchmark = 'benchmark(' in pl
    has_dbms_pipe_time = 'dbms_pipe.receive_message' in pl
    has_generate_series_large = bool(re.search(r'generate_series\s*\(\s*1\s*,\s*[5-9]\d{4,}', pl))
    
    has_union = bool(re.search(r'union\s+(all\s+)?select', pl))
    has_order_by = 'order by' in pl
    
    has_case_when = 'case when' in pl
    has_if_func = bool(re.search(r'\bif\s*\(', pl))
    has_iif = 'iif(' in pl
    has_boolean_eq = bool(re.search(r'\band\s+\d+\s*=\s*\d+', pl)) or bool(re.search(r'\bor\s+\d+\s*=\s*\d+', pl))
    has_boolean_bypass = bool(re.search(r"'\s+or\s+'1'\s*=\s*'1", pl)) or bool(re.search(r"'\s+or\s+''\s*=\s*'", pl))
    has_elt = 'elt(' in pl
    has_rlike = 'rlike' in pl
    has_ord_mid = bool(re.search(r'ord\s*\(\s*mid\s*\(', pl))
    has_where_eq = bool(re.search(r'where\s+\d+\s*=\s*\d+', pl))
    has_if_bool = bool(re.search(r'if\s*\(\s*\(?\s*select\s+\*\s*from', pl)) or has_if_func
    
    # === ENGINE DETERMINATION ===
    # Oracle markers have highest priority
    oracle_score = 0
    for m in oracle_markers:
        if m in pl:
            oracle_score += 1
    if oracle_chr_chain:
        oracle_score += 1
    
    mysql_score = 0
    for m in mysql_markers:
        if m in pl:
            mysql_score += 1
    if mysql_hash_comment:
        mysql_score += 1
    
    postgresql_score = 0
    for m in postgresql_markers:
        if m in pl:
            postgresql_score += 1
    
    mssql_score = 0
    for m in mssql_markers:
        if m in pl:
            mssql_score += 1
    if mssql_char_chain:
        mssql_score += 1
    
    sqlite_score = 0
    for m in sqlite_markers:
        if m in pl:
            sqlite_score += 1
    
    # Determine engine
    if oracle_score > 0:
        # Check if ::text is the ONLY postgresql marker and it's from cast(... ::text as numeric)
        # This is a hybrid pattern where Oracle payload uses pg syntax for casting
        # Oracle markers take priority
        db_engine = 'oracle'
    elif mysql_score > 0 and mssql_score == 0 and postgresql_score == 0 and sqlite_score == 0:
        db_engine = 'mysql'
    elif postgresql_score > 0 and mysql_score == 0 and mssql_score == 0 and sqlite_score == 0:
        db_engine = 'postgresql'
    elif mssql_score > 0 and mysql_score == 0 and postgresql_score == 0 and sqlite_score == 0:
        db_engine = 'mssql'
    elif sqlite_score > 0 and mysql_score == 0 and postgresql_score == 0 and mssql_score == 0:
        db_engine = 'sqlite'
    elif postgresql_score > 0 and mysql_score > 0:
        # Check which is stronger
        if re.search(r'generate_series', pl) and re.search(r'information_schema|sleep|benchmark', pl):
            # generate_series appears in both, check context
            if has_sleep or has_benchmark:
                db_engine = 'mysql'
            elif 'pg_sleep' in pl:
                db_engine = 'postgresql'
            else:
                db_engine = 'generic'
        else:
            db_engine = 'generic'
    elif mysql_score > 0 and mssql_score > 0:
        db_engine = 'generic'
    else:
        # Check for specific patterns
        if has_waitfor or mssql_char_chain:
            db_engine = 'mssql'
        elif has_pg_sleep or 'generate_series' in pl:
            db_engine = 'postgresql'
        elif has_benchmark or has_sleep or has_rlike or has_elt or information_schema in pl:
            db_engine = 'mysql'
        else:
            db_engine = 'generic'
    
    # === TYPE DETERMINATION ===
    # Rule: dbms_pipe.receive_message combined with xmltype() => error_based
    has_dbms_pipe_combined_xmltype = has_dbms_pipe_time and has_xmltype
    
    # Rule: dbms_pipe.receive_message standalone with timeout => time_blind
    has_dbms_pipe_standalone = has_dbms_pipe_time and not has_xmltype and not has_ctxsys
    
    # Check for error markers
    is_error = has_error_trigger and not has_dbms_pipe_standalone
    
    # Check for time markers  (sleep, pg_sleep, WAITFOR, benchmark, dbms_pipe standalone)
    is_time = (has_sleep or has_pg_sleep or has_waitfor or has_benchmark or 
               has_dbms_pipe_standalone or has_generate_series_large)
    
    # Check for union
    is_union = has_union
    
    # Edge case: Both UNION and error marker => error_based (error is the goal), confidence=0.85
    if is_error and is_union:
        sqli_type = 'error_based'
        # Will set confidence later
    # Edge case: CASE WHEN + sleep() together => time_blind (sleep() has higher priority)
    elif is_time and has_case_when and not is_error:
        sqli_type = 'time_based'
    # Edge case: dbms_pipe standalone => time_blind (already handled)
    elif is_error:
        sqli_type = 'error_based'
    elif is_time:
        sqli_type = 'time_based'
    elif is_union:
        sqli_type = 'union_based'
    else:
        # Check boolean markers
        has_boolean = (has_case_when or has_if_func or has_iif or 
                       has_boolean_eq or has_boolean_bypass or 
                       has_elt or has_rlike or has_ord_mid or has_where_eq)
        if has_boolean:
            sqli_type = 'boolean_blind'
        else:
            # Additional detection for short boolean-like patterns
            # Check for where X = X patterns
            if re.search(r'where\s+\d+\s*=\s*\d+', pl):
                sqli_type = 'boolean_blind'
            elif re.search(r"'\s*--", pl) or pl.strip() in ["'", "--", "1", "1=1", "1'", "1\""]:
                sqli_type = 'boolean_blind'
            elif re.search(r"\band\s+\d+\s*=\s*\d+", pl) or re.search(r"\bor\s+\d+\s*=\s*\d+", pl):
                sqli_type = 'boolean_blind'
            else:
                sqli_type = 'boolean_blind'  # default
    
    # === CONFIDENCE CALCULATION ===
    tcount = token_count(payload_norm)
    
    # Count type markers
    type_marker_count = 0
    if has_sleep: type_marker_count += 1
    if has_pg_sleep: type_marker_count += 1
    if has_waitfor: type_marker_count += 1
    if has_benchmark: type_marker_count += 1
    if has_dbms_pipe_time: type_marker_count += 1
    if has_generate_series_large: type_marker_count += 1
    if has_xmltype: type_marker_count += 1
    if has_extractvalue: type_marker_count += 1
    if has_updatexml: type_marker_count += 1
    if has_floor_rand_group: type_marker_count += 1
    if has_ctxsys: type_marker_count += 1
    if has_dbms_utility: type_marker_count += 1
    if has_utl_inaddr: type_marker_count += 1
    if has_union: type_marker_count += 1
    if has_order_by: type_marker_count += 1
    if has_case_when: type_marker_count += 1
    if has_if_func: type_marker_count += 1
    if has_boolean_eq: type_marker_count += 1
    if has_boolean_bypass: type_marker_count += 1
    if has_elt: type_marker_count += 1
    if has_rlike: type_marker_count += 1
    if has_where_eq: type_marker_count += 1
    
    # Count engine markers
    engine_marker_count = oracle_score + mysql_score + postgresql_score + mssql_score + sqlite_score
    
    # Determine base confidence
    if sqli_type == 'error_based' and has_union:
        # Both UNION and error marker -> error_based, confidence=0.85
        confidence = 0.85
    elif type_marker_count >= 2 and engine_marker_count >= 1:
        confidence = 1.00
    elif type_marker_count >= 1 and engine_marker_count >= 1:
        # Check for short payload
        if tcount < 8:
            confidence = 0.85
        else:
            confidence = 1.00
    elif type_marker_count >= 1:
        confidence = 0.85
    else:
        # Very few markers
        if tcount < 8:
            confidence = 0.70
        else:
            confidence = 0.85
    
    # Length adjustment
    if tcount < 8:
        if confidence == 1.00:
            confidence = 0.85
        elif confidence == 0.85:
            confidence = 0.70
    
    # === OVERRIDES FOR SPECIAL CASES ===
    
    # Simple auth bypass: ' OR '1'='1 -> boolean_blind, confidence=0.85
    if bool(re.search(r"'\s+or\s+'1'\s*=\s*'1", pl)):
        sqli_type = 'boolean_blind'
        confidence = 0.85
    
    # dbms_pipe standalone with timeout -> time_blind
    if has_dbms_pipe_standalone:
        sqli_type = 'time_based'
        if tcount < 8:
            confidence = 0.85
        else:
            confidence = 1.00
    
    # dbms_pipe + xmltype -> error_based
    if has_dbms_pipe_combined_xmltype:
        sqli_type = 'error_based'
    
    # Short payloads (< 8 tokens) without clear markers
    if tcount < 5 and type_marker_count == 0:
        confidence = 0.70
    
    # Very short: "1", "1=1", "'", "--"
    very_short = pl.strip() in ['1', '1=1', "'", '--', "''", "1'", '1"', "' --", "'--"]
    if very_short:
        sqli_type = 'boolean_blind'
        confidence = 0.70
    
    # "end# thjv" pattern - incomplete/injected garbage
    if pl.startswith('end#') or pl == 'end# thjv':
        sqli_type = 'boolean_blind'
        db_engine = 'generic'
        confidence = 0.70
    
    # Heavy Cartesian joins -> time_blind
    has_heavy_cross_join = bool(re.search(r'(?:cross\s+join|from\s+\w+\s+\w+,\s*\w+\s+\w+\s*,\s*\w+\s+\w+)', pl))
    if has_heavy_cross_join and 'generate_series' not in pl:
        if has_error_trigger:
            sqli_type = 'error_based'
        elif has_union:
            sqli_type = 'union_based'
        else:
            sqli_type = 'time_based'
    
    # Ensure 'time_based' -> 'time_blind' in output
    if sqli_type == 'time_based':
        sqli_type = 'time_blind'
    
    # Override confidence for specific very clear cases
    # xmltype + from dual = 2 clear oracle markers
    if 'xmltype(' in pl and 'from dual' in pl and not has_union:
        sqli_type = 'error_based'
        db_engine = 'oracle'
        confidence = 1.00
    
    # ctxsys.drithsx.sn + from dual -> error_based, oracle, 1.00
    if 'ctxsys.drithsx.sn(' in pl and 'from dual' in pl:
        sqli_type = 'error_based'
        db_engine = 'oracle'
        confidence = 1.00
    
    # sleep(5) standalone -> time_blind, mysql, 1.00
    if has_sleep and tcount < 10 and not has_union and not has_error_trigger and not has_case_when:
        sqli_type = 'time_blind'
        db_engine = 'mysql'
        confidence = 1.00
    
    # elt(..., sleep(5)) -> sleep has higher priority -> time_blind, mysql
    if 'elt(' in pl and has_sleep:
        sqli_type = 'time_blind'
        if db_engine == 'generic' or mysql_score > 0:
            db_engine = 'mysql'
        confidence = 1.00
    
    # UNION ALL SELECT with # -> union_based, mysql
    if has_union and mysql_hash_comment and not has_error_trigger:
        sqli_type = 'union_based'
        db_engine = 'mysql'
        confidence = 1.00
    
    # WAITFOR DELAY -> time_blind, mssql
    if has_waitfor:
        sqli_type = 'time_blind'
        db_engine = 'mssql'
        confidence = 1.00
    
    # benchmark(5000000, ...) -> time_blind, mysql
    if has_benchmark and not has_error_trigger:
        sqli_type = 'time_blind'
        db_engine = 'mysql'
        confidence = 1.00
    
    # information_schema.character_sets + floor(rand + group by -> error_based, mysql
    if 'floor(rand(' in pl and 'group by' in pl and 'information_schema' in pl:
        sqli_type = 'error_based'
        db_engine = 'mysql'
        confidence = 1.00
    
    # CASE WHEN + mysql.db + # -> boolean_blind, mysql, 1.00
    if 'case when' in pl and 'mysql.db' in pl and mysql_hash_comment:
        sqli_type = 'boolean_blind'
        db_engine = 'mysql'
        confidence = 1.00
    
    # dbms_utility + from dual -> error_based, oracle
    if 'dbms_utility' in pl and 'from dual' in pl:
        sqli_type = 'error_based'
        db_engine = 'oracle'
        confidence = 1.00
    
    # chr()||chr() chain with from dual -> oracle
    if oracle_chr_chain and ('from dual' in pl or 'xmltype(' in pl or 'ctxsys' in pl):
        db_engine = 'oracle'
    
    # ::text cast -> PostgreSQL marker, but if oracle markers present too, oracle wins
    if '::text' in pl and oracle_score == 0 and postgresql_score > 0:
        db_engine = 'postgresql'
    
    return sqli_type, db_engine, confidence


def process_all():
    input_path = r"C:\Projects\GAN_SQLi\Asset\LabelData\unlabeled_10001_12000.csv"
    output_path = r"C:\Projects\GAN_SQLi\Asset\LabelData\labeled_10001_12000.csv"
    
    rows = []
    with open(input_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:
                rows.append((row[0], row[1]))
    
    print(f"Total rows to process: {len(rows)}")
    
    results = []
    for id_val, payload in rows:
        sqli_type, db_engine, confidence = classify_sqli(payload)
        results.append((id_val, sqli_type, db_engine, confidence))
    
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['id', 'sqli_type', 'db_engine', 'confidence'])
        for row in results:
            writer.writerow([row[0], row[1], row[2], f"{row[3]:.2f}"])
    
    # Summary
    type_counts = {}
    engine_counts = {}
    confidence_counts = {}
    
    print("\n=== SUMMARY ===")
    for id_val, sqli_type, db_engine, confidence in results:
        type_counts[sqli_type] = type_counts.get(sqli_type, 0) + 1
        engine_counts[db_engine] = engine_counts.get(db_engine, 0) + 1
        conf_key = f"{confidence:.2f}"
        confidence_counts[conf_key] = confidence_counts.get(conf_key, 0) + 1
    
    print("\nCount per sqli_type:")
    for t, c in sorted(type_counts.items()):
        print(f"  {t}: {c}")
    
    print("\nCount per db_engine:")
    for e, c in sorted(engine_counts.items()):
        print(f"  {e}: {c}")
    
    print("\nCount per confidence:")
    for c_val, cnt in sorted(confidence_counts.items()):
        print(f"  {c_val}: {cnt}")
    
    # Sample verification
    print("\n=== SAMPLE VERIFICATION (first 20) ===")
    for id_val, sqli_type, db_engine, confidence in results[:20]:
        print(f"  {id_val}: {sqli_type}, {db_engine}, {confidence:.2f}")
    
    # Also show some diverse samples
    print("\n=== DIVERSE SAMPLES ===")
    seen_types = set()
    for id_val, sqli_type, db_engine, confidence in results:
        key = f"{sqli_type}_{db_engine}"
        if key not in seen_types:
            seen_types.add(key)
            print(f"  {id_val}: type={sqli_type}, engine={db_engine}, conf={confidence:.2f}")
            print(f"    Payload: {rows[int(id_val)-10001][1][:100]}...")

process_all()
