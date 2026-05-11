import csv
import re
import io

def normalize_payload(p):
    """Normalize payload: lowercase, collapse spaces around parens for function detection."""
    p = p.lower()
    # Remove spaces between function name and opening paren
    p = re.sub(r'(\w)\s+\(', r'\1(', p)
    # Collapse multiple spaces
    p = re.sub(r'\s+', ' ', p)
    return p

def classify_sqli(payload):
    p_lower = payload.lower()
    p_norm = normalize_payload(payload)
    
    # ============ DETECT MARKERS (use normalized for func calls, original for others) ============
    
    # --- Oracle markers ---
    has_xmltype = 'xmltype(' in p_norm
    has_dual = 'from dual' in p_lower
    has_dbms_pipe = 'dbms_pipe' in p_lower
    has_utl_inaddr = 'utl_inaddr' in p_lower
    has_sys_context = 'sys_context(' in p_norm
    has_ctxsys = 'ctxsys.' in p_lower
    has_all_tables = 'all_tables' in p_lower
    has_rownum = 'rownum' in p_lower
    has_dbms_utility = 'dbms_utility' in p_lower
    chr_chain = bool(re.search(r"chr\s*\(\s*\d+\s*\)\s*\|\|\s*chr\s*\(\s*\d+\s*\)", p_lower))
    has_regexp_substr = 'regexp_substr(' in p_norm
    
    # --- MySQL markers ---
    has_sleep = bool(re.search(r'(?<![a-z_])sleep\s*\(', p_lower))
    has_benchmark = 'benchmark(' in p_norm
    has_group_concat = 'group_concat(' in p_norm
    has_floor_rand = 'floor(rand(' in p_norm
    has_extractvalue = 'extractvalue(' in p_norm
    has_updatexml = 'updatexml(' in p_norm
    has_information_schema = 'information_schema' in p_lower
    has_load_file = 'load_file(' in p_norm
    has_into_outfile = 'into outfile' in p_lower
    has_at_at_version = '@@version' in p_lower
    has_at_at_datadir = '@@datadir' in p_lower
    has_elt = 'elt(' in p_norm
    has_concat = 'concat(' in p_norm
    has_if_mysql = bool(re.search(r'(?<![a-z_])if\s*\(', p_lower))
    has_make_set = 'make_set(' in p_norm
    has_mysql_comment_hash = payload.rstrip().endswith('#')
    
    # PostgreSQL markers
    has_pg_sleep = 'pg_sleep(' in p_norm
    has_generate_series = 'generate_series(' in p_norm
    has_cast_text = bool(re.search(r'::\s*text', p_lower))
    has_cast_numeric = bool(re.search(r'::\s*numeric', p_lower)) or bool(re.search(r'::\s*int', p_lower))
    
    # MSSQL markers
    has_waitfor = 'waitfor delay' in p_lower
    has_master_sysdatabases = 'master..sysdatabases' in p_lower
    has_xp_cmdshell = 'xp_cmdshell' in p_lower
    has_at_at_servername = '@@servername' in p_lower
    has_sysobjects = bool(re.search(r'sysobjects|syscolumns|sysusers', p_lower))
    has_convert_int = bool(re.search(r'convert\s*\(\s*int', p_lower))
    has_char_plus = bool(re.search(r"char\s*\(\s*\d+\s*\)\s*\+", p_lower))
    has_iif = bool(re.search(r'(?<![a-z_])iif\s*\(', p_lower))
    
    # SQLite markers
    has_randomblob = 'randomblob' in p_lower
    has_sqlite_version = 'sqlite_version' in p_norm
    has_sqlite_master = 'sqlite_master' in p_lower
    has_sqlite_like_abcdefg = bool(re.search(r"like\s*\(\s*['\"]abcdefg['\"]", p_lower))
    
    # Type markers
    has_union = bool(re.search(r'union(\s+all)?\s+select', p_lower))
    has_order_by = bool(re.search(r'order\s+by\s+\d+', p_lower))
    has_case_when = bool(re.search(r'case\s+when', p_lower))
    has_rlike = 'rlike' in p_lower
    and_1_1 = bool(re.search(r'and\s+1\s*=\s*1', p_lower))
    
    # ============ ENGINE DETECTION ============
    
    score_oracle = score_mysql = score_postgres = score_mssql = score_sqlite = 0
    
    if has_xmltype: score_oracle += 3
    if has_dual: score_oracle += 2
    if has_ctxsys: score_oracle += 3
    if has_dbms_utility: score_oracle += 2
    if has_utl_inaddr: score_oracle += 3
    if has_sys_context: score_oracle += 2
    if has_all_tables: score_oracle += 1
    if has_rownum: score_oracle += 1
    if chr_chain: score_oracle += 2
    if has_dbms_pipe: score_oracle += 1
    
    if has_sleep: score_mysql += 2
    if has_benchmark: score_mysql += 2
    if has_group_concat: score_mysql += 2
    if has_floor_rand: score_mysql += 2
    if has_information_schema: score_mysql += 1
    if has_at_at_version: score_mysql += 1
    if has_elt: score_mysql += 1
    if has_mysql_comment_hash: score_mysql += 1
    if has_if_mysql: score_mysql += 1
    if has_make_set: score_mysql += 1
    
    if has_pg_sleep: score_postgres += 3
    if has_generate_series: score_postgres += 2
    if has_cast_text: score_postgres += 2
    if has_cast_numeric: score_postgres += 2
    
    if has_waitfor: score_mssql += 3
    if has_master_sysdatabases: score_mssql += 2
    if has_xp_cmdshell: score_mssql += 3
    if has_at_at_servername: score_mssql += 1
    if has_sysobjects: score_mssql += 2
    if has_convert_int: score_mssql += 2
    if has_char_plus: score_mssql += 2
    if has_iif: score_mssql += 1
    
    if has_randomblob: score_sqlite += 3
    if has_sqlite_version: score_sqlite += 2
    if has_sqlite_master: score_sqlite += 2
    if has_sqlite_like_abcdefg: score_sqlite += 2
    
    scores = {'oracle': score_oracle, 'mysql': score_mysql, 'postgresql': score_postgres,
              'mssql': score_mssql, 'sqlite': score_sqlite}
    
    max_score = max(scores.values())
    if max_score >= 3:
        top = [e for e, s in scores.items() if s == max_score]
        db_engine = 'oracle' if 'oracle' in top and score_oracle >= 2 else top[0]
    elif max_score >= 1:
        top = [e for e, s in scores.items() if s == max_score]
        db_engine = top[0]
    else:
        db_engine = 'generic'
    
    # ============ TYPE DETECTION ============
    
    # error_based markers
    is_error = False
    error_markers = []
    if has_xmltype: is_error = True; error_markers.append('xmltype')
    if has_ctxsys: is_error = True; error_markers.append('ctxsys')
    if has_extractvalue and not has_sleep: is_error = True; error_markers.append('extractvalue')
    if has_updatexml: is_error = True; error_markers.append('updatexml')
    if has_floor_rand: is_error = True; error_markers.append('floor_rand')
    if has_convert_int: is_error = True; error_markers.append('convert_int')
    if has_utl_inaddr: is_error = True; error_markers.append('utl_inaddr')
    
    # time_based markers
    is_time = False
    time_markers = []
    if has_sleep: is_time = True; time_markers.append('sleep')
    if has_pg_sleep: is_time = True; time_markers.append('pg_sleep')
    if has_waitfor: is_time = True; time_markers.append('waitfor')
    if has_benchmark: is_time = True; time_markers.append('benchmark')
    if has_dbms_pipe and not has_xmltype: is_time = True; time_markers.append('dbms_pipe')
    if has_randomblob: is_time = True; time_markers.append('randomblob')
    if has_sqlite_like_abcdefg: is_time = True; time_markers.append('sqlite_heavy_like')
    
    # generate_series heavy check
    if has_generate_series:
        m = re.search(r'generate_series\s*\(\s*(\d+)\s*,?\s*(\d+)', p_norm)
        if m:
            try:
                if int(m.group(2)) > 100000:
                    is_time = True; time_markers.append('gen_series_heavy')
            except: pass
        # Also check for template-like large numbers e.g. [SLEEPTIME]000000
        if bool(re.search(r'generate_series\s*\(\s*\d+\s*,\s*\[\w+\]\d+', p_lower)):
            is_time = True; time_markers.append('gen_series_template')
    
    # Heavy repeat
    if 'repeat(' in p_norm:
        m = re.search(r'repeat\s*\([^,]+,\s*(\d+)', p_lower)
        if m:
            try:
                if int(m.group(1)) > 100000:
                    is_time = True; time_markers.append('repeat_heavy')
            except: pass
    
    # union markers
    is_union = has_union or (has_order_by and not has_case_when and not is_time and not is_error)
    
    # ============ CLASSIFICATION ============
    
    # dbms_pipe + xmltype = error_based (not time)
    if has_dbms_pipe and has_xmltype and 'dbms_pipe' in time_markers:
        time_markers.remove('dbms_pipe')
        if not time_markers: is_time = False
    
    # UNION + error = error_based
    if has_union and is_error:
        is_union = False
    
    if is_error:
        sqli_type = 'error_based'
    elif is_time:
        sqli_type = 'time_blind'
    elif is_union:
        sqli_type = 'union_based'
    elif has_case_when:
        sqli_type = 'boolean_blind'
    elif has_rlike:
        sqli_type = 'boolean_blind'
    elif has_char_plus:
        sqli_type = 'boolean_blind'
    elif has_iif:
        sqli_type = 'boolean_blind'
    else:
        sqli_type = 'boolean_blind'
    
    # ============ CONFIDENCE ============
    token_count = len(payload.split())
    
    confidence = 0.70
    if is_error:
        if len(error_markers) >= 2 or (has_xmltype and has_dual):
            confidence = 1.00
        elif has_union:
            confidence = 0.85
        else:
            confidence = 0.85 if len(error_markers) >= 1 else 0.70
    elif is_time:
        if len(time_markers) >= 2:
            confidence = 1.00
        elif has_case_when:
            confidence = 0.85
        else:
            confidence = 1.00 if len(time_markers) >= 1 else 0.85
    elif is_union:
        if has_union and bool(re.search(r'union\s+all\s+select', p_lower)):
            confidence = 1.00
        elif has_union:
            confidence = 1.00
        elif has_order_by:
            confidence = 0.85
        else:
            confidence = 0.85
    else:
        if has_case_when and (has_dual or chr_chain or has_char_plus or has_cast_text or has_cast_numeric):
            confidence = 1.00
        elif has_case_when:
            confidence = 0.85
        elif token_count <= 4 and db_engine == 'generic':
            confidence = 0.70
        else:
            confidence = 0.85
    
    # Oracle + dual + chr chain = high confidence
    if db_engine == 'oracle' and has_dual and chr_chain and confidence < 0.85:
        confidence = 0.85
    
    # Polyglot detection: multiple DB-specific markers present
    db_markers = 0
    if has_xmltype or has_dual or has_ctxsys or has_dbms_utility: db_markers += 1
    if has_sleep or has_benchmark or has_floor_rand or has_at_at_version or has_mysql_comment_hash: db_markers += 1
    if has_pg_sleep or has_cast_text or has_cast_numeric: db_markers += 1
    if has_waitfor or has_master_sysdatabases or has_xp_cmdshell or has_sysobjects or has_convert_int: db_markers += 1
    if has_randomblob or has_sqlite_master: db_markers += 1
    
    if db_markers >= 2 and confidence == 1.00:
        confidence = 0.85
    
    return sqli_type, db_engine, confidence


# Read the input file - handle both with and without header
with open(r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\temp_batch_12001_13000.csv', 'r', encoding='utf-8-sig') as f:
    content = f.read()

lines = content.strip().split('\n')
has_header = lines[0].startswith('"id"') or lines[0].startswith('id')

with io.StringIO(content) as f:
    reader = csv.reader(f)
    if has_header:
        header = next(reader)
        print(f"Header found: {header}")
    else:
        print("No header found, processing all rows as data")
        # Seek back
        f.seek(0)
        reader = csv.reader(f)
    
    results = []
    for row in reader:
        if len(row) < 2:
            continue
        id_str = row[0].strip('"')
        if not id_str.isdigit():
            if not has_header:
                continue  # skip non-digit first col
        payload = row[1].strip('"')
        
        sqli_type, db_engine, confidence = classify_sqli(payload)
        results.append((id_str, sqli_type, db_engine, f"{confidence:.2f}"))

output_file = r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\split_data_labeled_batch_12001_13000.csv'
with open(output_file, 'w', encoding='utf-8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'sqli_type', 'db_engine', 'confidence'])
    writer.writerows(results)

print(f"Done! Processed {len(results)} rows.")
print(f"Output: {output_file}")

# Summary
type_counts = {}
engine_counts = {}
for _, t, e, c in results:
    type_counts[t] = type_counts.get(t, 0) + 1
    engine_counts[e] = engine_counts.get(e, 0) + 1

print("\n=== Type Distribution ===")
for t, c in sorted(type_counts.items()):
    print(f"  {t}: {c}")
print("\n=== Engine Distribution ===")
for e, c in sorted(engine_counts.items()):
    print(f"  {e}: {c}")

# Check first/last
print(f"\nFirst: id={results[0][0]}, {results[0][1]}, {results[0][2]}, {results[0][3]}")
print(f"Last:  id={results[-1][0]}, {results[-1][1]}, {results[-1][2]}, {results[-1][3]}")
