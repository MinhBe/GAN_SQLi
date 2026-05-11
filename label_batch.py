import csv
import re

def classify(payload):
    p = payload.lower()
    
    # --- DB Engine detection ---
    
    # Oracle markers
    oracle_markers = []
    if re.search(r'xmltype\s*\(', p): oracle_markers.append('xmltype')
    if re.search(r'dbms_pipe\.', p): oracle_markers.append('dbms_pipe')
    if re.search(r'utl_inaddr\.', p): oracle_markers.append('utl_inaddr')
    if re.search(r'utl_http\.', p): oracle_markers.append('utl_http')
    if re.search(r'sys_context\s*\(', p): oracle_markers.append('sys_context')
    if re.search(r'from\s+dual\b', p): oracle_markers.append('from_dual')
    if re.search(r'sys\.all_tables', p): oracle_markers.append('sys.all_tables')
    if re.search(r'\brownum\b', p): oracle_markers.append('rownum')
    if re.search(r'ctxsys\.', p): oracle_markers.append('ctxsys')
    if re.search(r'regexp_substr\s*\(', p): oracle_markers.append('regexp_substr')
    if re.search(r'dbms_utility\.', p): oracle_markers.append('dbms_utility')
    
    # PostgreSQL markers
    pg_markers = []
    if re.search(r'pg_sleep\s*\(', p): pg_markers.append('pg_sleep')
    if re.search(r'generate_series\s*\(', p): pg_markers.append('generate_series')
    if re.search(r'::text\b', p): pg_markers.append('::text')
    if re.search(r'::int\b', p): pg_markers.append('::int')
    if re.search(r'::numeric\b', p): pg_markers.append('::numeric')
    if re.search(r'\$\$', p): pg_markers.append('$$')
    if re.search(r'string_agg\s*\(', p): pg_markers.append('string_agg')
    if re.search(r'array_agg\s*\(', p): pg_markers.append('array_agg')
    if re.search(r'\blimit\s+\d+', p) and re.search(r'generate_series', p): pg_markers.append('limit')
    
    # MSSQL markers
    mssql_markers = []
    if re.search(r'waitfor\s+delay', p): mssql_markers.append('waitfor_delay')
    if re.search(r'master\.\.sysdatabases', p): mssql_markers.append('master..sysdatabases')
    if re.search(r'xp_cmdshell', p): mssql_markers.append('xp_cmdshell')
    if re.search(r'@@servername', p): mssql_markers.append('@@servername')
    if re.search(r'\bsysobjects\b', p): mssql_markers.append('sysobjects')
    if re.search(r'\bsyscolumns\b', p): mssql_markers.append('syscolumns')
    if re.search(r'\bsysusers\b', p): mssql_markers.append('sysusers')
    if re.search(r'convert\s*\(\s*int', p): mssql_markers.append('convert(int')
    if re.search(r'\biif\s*\(', p): mssql_markers.append('iif')
    
    # MySQL markers
    mysql_markers = []
    if re.search(r'\bsleep\s*\(', p): mysql_markers.append('sleep')
    if re.search(r'benchmark\s*\(', p): mysql_markers.append('benchmark')
    if re.search(r'group_concat\s*\(', p): mysql_markers.append('group_concat')
    if re.search(r'floor\s*\(\s*rand\s*\(', p): mysql_markers.append('floor_rand')
    if re.search(r'extractvalue\s*\(', p): mysql_markers.append('extractvalue')
    if re.search(r'updatexml\s*\(', p): mysql_markers.append('updatexml')
    if re.search(r'information_schema\.', p): mysql_markers.append('information_schema')
    if re.search(r'information_schema\.system_users', p): mysql_markers.append('system_users')
    if re.search(r'load_file\s*\(', p): mysql_markers.append('load_file')
    if re.search(r'into\s+outfile', p): mysql_markers.append('into_outfile')
    if re.search(r'@@version', p): mysql_markers.append('@@version')
    if re.search(r'@@datadir', p): mysql_markers.append('@@datadir')
    if re.search(r'#\s*$', p.strip()) or re.search(r'#[a-z]{4}$', p.strip()): mysql_markers.append('hash_comment')
    if re.search(r'\bconcat\s*\(', p) and not re.search(r'from\s+dual', p): mysql_markers.append('concat')
    if re.search(r'\bif\s*\(', p) and not re.search(r'from\s+dual', p): mysql_markers.append('if(')
    if re.search(r'\belt\s*\(', p): mysql_markers.append('elt')
    if re.search(r'make_set\s*\(', p): mysql_markers.append('make_set')
    if re.search(r'crypt_key\s*\(', p): mysql_markers.append('crypt_key')
    if re.search(r'\brlike\b', p): mysql_markers.append('rlike')
    if re.search(r'procedure\s+analyse', p): mysql_markers.append('procedure_analyse')
    if re.search(r'\bexp\s*\(\s*~', p): mysql_markers.append('exp')
    
    # SQLite markers
    sqlite_markers = []
    if re.search(r'randomblob\s*\(', p): sqlite_markers.append('randomblob')
    if re.search(r'sqlite_version\s*\(', p): sqlite_markers.append('sqlite_version')
    if re.search(r'sqlite_master', p): sqlite_markers.append('sqlite_master')
    if re.search(r'\blike\s*\(\s*\'abcdefg\'', p): sqlite_markers.append('like_abcdefg')
    
    # --- Determine db_engine ---
    # Tiebreaker: Oracle > PostgreSQL > MSSQL > MySQL > SQLite > generic
    if oracle_markers:
        db_engine = 'oracle'
        engine_markers = oracle_markers
    elif pg_markers:
        db_engine = 'postgresql'
        engine_markers = pg_markers
    elif mssql_markers:
        db_engine = 'mssql'
        engine_markers = mssql_markers
    elif mysql_markers:
        db_engine = 'mysql'
        engine_markers = mysql_markers
    elif sqlite_markers:
        db_engine = 'sqlite'
        engine_markers = sqlite_markers
    else:
        db_engine = 'generic'
        engine_markers = []
    
    # --- sqli_type detection ---
    has_union = bool(re.search(r'union\s+(all\s+)?select', p))
    has_error_marker = bool(re.search(r'xmltype\s*\(', p)) or bool(re.search(r'extractvalue\s*\(', p)) or bool(re.search(r'updatexml\s*\(', p)) or bool(re.search(r'floor\s*\(\s*rand\s*\(', p)) or bool(re.search(r'convert\s*\(\s*int', p)) or bool(re.search(r'utl_inaddr\.', p)) or bool(re.search(r'ctxsys\.drithsx\.sn\s*\(', p)) or bool(re.search(r"exp\s*\(\s*~", p))
    has_time_marker = bool(re.search(r'\bsleep\s*\(', p)) or bool(re.search(r'pg_sleep\s*\(', p)) or bool(re.search(r'waitfor\s+delay', p)) or bool(re.search(r'dbms_pipe\.receive_message', p)) or bool(re.search(r'benchmark\s*\(', p)) or bool(re.search(r'randomblob\s*\(', p))
    
    # Heavy computation
    has_heavy_computation = bool(re.search(r'generate_series\s*\(\s*1\s*,\s*[56789]\d{5,}', p)) or bool(re.search(r'500000000', p)) or bool(re.search(r'5000000000', p))
    has_case_when = bool(re.search(r'case\s+when', p))
    has_order_by = bool(re.search(r'order\s+by\s+\d+', p))
    
    # Boolean markers (excluding those already in time/error)
    has_rlike_boolean = bool(re.search(r'\brlike\s*\(', p)) or bool(re.search(r'rlike\s+select', p)) or bool(re.search(r'rlike\s+sleep', p))
    has_elt_boolean = bool(re.search(r'elt\s*\(', p))
    has_if_boolean = bool(re.search(r'\bif\s*\(', p)) or bool(re.search(r'\biif\s*\(', p))
    has_simple_boolean = bool(re.search(r"'\s+or\s+'\d+'\s*=\s*'\d+'", p)) or bool(re.search(r"'\s+or\s+''\s*=\s*'", p)) or bool(re.search(r"or\s+'\d+'\s*=\s*'\d+'", p))
    has_char_compare = bool(re.search(r"and\s+chr\s*\(|or\s+chr\s*\(", p))
    has_make_set_boolean = bool(re.search(r'make_set\s*\(', p))
    
    # --- Classification with priority ---
    
    # Error-based: highest priority
    if has_error_marker:
        sqli_type = 'error_based'
    elif has_time_marker:
        sqli_type = 'time_blind'
    elif has_heavy_computation:
        sqli_type = 'time_blind'
    elif has_union:
        sqli_type = 'union_based'
    elif has_case_when:
        sqli_type = 'boolean_blind'
    elif has_order_by:
        sqli_type = 'union_based'  # ORDER BY is union column probing
    elif has_rlike_boolean or has_elt_boolean or has_if_boolean or has_make_set_boolean:
        sqli_type = 'boolean_blind'
    elif has_simple_boolean or has_char_compare:
        sqli_type = 'boolean_blind'
    else:
        # Check for common boolean patterns
        if re.search(r'\b(and|or)\s+\d+\s*=\s*\d+', p) or re.search(r"--\s*$", p.strip()):
            sqli_type = 'boolean_blind'
        elif re.search(r"or\s+'1'\s*=\s*'1", p) or re.search(r"or\s+\"1\"\s*=\s*\"1", p):
            sqli_type = 'boolean_blind'
        elif re.search(r"'\s*--", p) or re.search(r"admin'", p):
            sqli_type = 'boolean_blind'
        elif re.search(r'or\s+.+=\s*', p) and len(p.strip()) > 3:
            sqli_type = 'boolean_blind'
        elif re.search(r'\bwhere\s+\d+\s*=\s*\d+', p):
            sqli_type = 'boolean_blind'
        elif re.search(r'\b(as\s+\w+\s+where|procedure\s+analyse)', p):
            sqli_type = 'boolean_blind'
        else:
            sqli_type = 'boolean_blind'  # safest default for SQL payloads
    
    # --- Edge case overrides ---
    
    # Union + error marker: purpose is error
    if has_union and has_error_marker:
        sqli_type = 'error_based'
    
    # CASE WHEN + sleep/time: time_blind (sleep overrides)
    if has_case_when and has_time_marker:
        sqli_type = 'time_blind'
    
    # CASE WHEN + heavy computation: time_blind
    if has_case_when and has_heavy_computation:
        sqli_type = 'time_blind'
    
    # dbms_pipe standalone (no xmltype/ctxsys) = time_blind
    if re.search(r'dbms_pipe\.receive_message', p) and not re.search(r'xmltype|ctxsys|upper\s*\(\s*xmltype', p):
        sqli_type = 'time_blind'
    
    # --- Confidence scoring ---
    type_markers_count = 0
    if has_error_marker: type_markers_count += 1
    if has_time_marker: type_markers_count += 1
    if has_union: type_markers_count += 1
    if has_case_when: type_markers_count += 1
    if has_rlike_boolean or has_elt_boolean or has_if_boolean or has_make_set_boolean: type_markers_count += 1
    
    payload_len = len(p.strip())
    engine_count = len(engine_markers)
    
    # 1.00 rules
    if sqli_type == 'error_based' and db_engine != 'generic' and engine_count >= 2:
        confidence = 1.00
    elif sqli_type == 'time_blind' and db_engine != 'generic' and (has_time_marker or has_heavy_computation) and engine_count >= 2:
        confidence = 1.00
    elif sqli_type == 'union_based' and has_union and engine_count >= 2:
        confidence = 1.00
    elif sqli_type == 'boolean_blind' and db_engine != 'generic' and engine_count >= 2 and has_case_when:
        confidence = 1.00
    elif sqli_type == 'boolean_blind' and db_engine != 'generic' and engine_count >= 2 and has_rlike_boolean:
        confidence = 1.00
    elif sqli_type == 'boolean_blind' and db_engine != 'generic' and payload_len >= 30 and engine_count >= 2 and type_markers_count >= 2:
        confidence = 1.00
    elif sqli_type == 'time_blind' and db_engine != 'generic' and payload_len >= 30 and (has_time_marker or has_heavy_computation) and engine_count >= 1:
        confidence = 1.00
    elif sqli_type == 'union_based' and has_union and payload_len >= 20:
        if db_engine != 'generic':
            confidence = 1.00
        else:
            confidence = 0.85
    # 0.70 rules
    elif payload_len < 5:
        confidence = 0.70
    elif payload_len < 10 and db_engine == 'generic':
        confidence = 0.70
    elif payload_len < 15 and engine_count == 0 and type_markers_count <= 1:
        confidence = 0.70
    # 0.85 rules (everything else)
    else:
        confidence = 0.85
    
    # Override: if db_engine is generic and payload is very short/non-specific
    if db_engine == 'generic' and engine_count == 0:
        if payload_len < 10:
            confidence = 0.70
        elif not has_case_when and not has_union and not has_time_marker and not has_error_marker and not has_rlike_boolean:
            if payload_len < 20:
                confidence = 0.70
    
    # Format confidence
    if confidence >= 1.0:
        conf_str = '1.00'
    elif confidence >= 0.85:
        conf_str = '0.85'
    else:
        conf_str = '0.70'
    
    return sqli_type, db_engine, conf_str


# Read the CSV data
rows = []
with open(r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\split_data.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        rows.append(row)

# Process rows 1501 to 2000
output = []
for row in rows:
    row_id = int(row[0])
    if 1501 <= row_id <= 2000:
        payload = row[1]
        sqli_type, db_engine, conf_str = classify(payload)
        output.append([row_id, sqli_type, db_engine, conf_str])

# Write output
with open(r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\split_data_labeled_batch_1501_2000.csv', 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'sqli_type', 'db_engine', 'confidence'])
    writer.writerows(output)

# Print summary
from collections import Counter
types = Counter(o[1] for o in output)
engines = Counter(o[2] for o in output)
confs = Counter(o[3] for o in output)
print(f"Total: {len(output)} rows")
print(f"sqli_type: {dict(types)}")
print(f"db_engine: {dict(engines)}")
print(f"confidence: {dict(confs)}")
