import csv, re, sys

with open('C:/Projects/GAN_SQLi/SeqGAN_SQLi/data/temp_batch_extracted.csv', 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    next(reader)
    rows = list(reader)

payloads = {r[0]: r[1] for r in rows}

def classify(pid, pay):
    pl = pay.lower()
    orig = pay
    tokens = len(pl.split())

    # === DB ENGINE DETECTION ===
    is_oracle = bool(re.search(r'xmltype\s*\(', pl))
    is_oracle |= bool(re.search(r'dbms_pipe', pl))
    is_oracle |= bool(re.search(r'utl_inaddr', pl))
    is_oracle |= bool(re.search(r'utl_http', pl))
    is_oracle |= bool(re.search(r'sys_context\s*\(', pl))
    is_oracle |= bool(re.search(r'from dual', pl))
    is_oracle |= bool(re.search(r'sys\.all_tables', pl))
    is_oracle |= bool(re.search(r'rownum', pl))
    is_oracle |= bool(re.search(r'ctxsys', pl))
    is_oracle |= bool(re.search(r'regexp_substr\s*\(', pl))
    is_oracle |= bool(re.search(r'chr\s*\(.*?\)\s*\|\|', pl))

    is_mysql = bool(re.search(r'sleep\s*\(', pl) and 'pg_sleep' not in pl)
    is_mysql |= bool(re.search(r'benchmark\s*\(', pl))
    is_mysql |= bool(re.search(r'floor\s*\(\s*rand\s*\(', pl))
    is_mysql |= bool(re.search(r'extractvalue\s*\(', pl))
    is_mysql |= bool(re.search(r'updatexml\s*\(', pl))
    is_mysql |= bool(re.search(r'information_schema', pl))
    is_mysql |= bool(re.search(r'load_file\s*\(', pl))
    is_mysql |= bool(re.search(r'into\s+outfile', pl))
    is_mysql |= bool(re.search(r'@@version', pl))
    is_mysql |= bool(re.search(r'@@datadir', pl))
    is_mysql |= bool(re.search(r'group_concat\s*\(', pl))
    is_mysql |= orig.strip().endswith('#')
    is_mysql |= bool(re.search(r'elt\s*\(', pl))
    is_mysql |= bool(re.search(r'regexp_substring\s*\(', pl))
    is_mysql |= bool(re.search(r'\brlike\s*\(', pl))
    is_mysql |= bool(re.search(r'concat\s*\(.*?0x[0-9a-f]', pl))
    is_mysql |= bool(re.search(r'procedure\s+analyse', pl))
    is_mysql |= bool(re.search(r'\bmake_set\s*\(', pl))

    is_postgres = bool(re.search(r'pg_sleep\s*\(', pl))
    is_postgres |= bool(re.search(r'generate_series\s*\(', pl))
    is_postgres |= bool(re.search(r'::text\b', pl))
    is_postgres |= bool(re.search(r'::int\b', pl))
    is_postgres |= bool(re.search(r'::numeric\b', pl))
    is_postgres |= bool(re.search(r'\$\$', pl))
    is_postgres |= bool(re.search(r'string_agg\s*\(', pl))
    is_postgres |= bool(re.search(r'array_agg\s*\(', pl))
    is_postgres |= bool(re.search(r'pg_read_file\s*\(', pl))

    is_mssql = bool(re.search(r'waitfor\s+delay', pl))
    is_mssql |= bool(re.search(r'master\.\.sysdatabases', pl))
    is_mssql |= bool(re.search(r'xp_cmdshell', pl))
    is_mssql |= bool(re.search(r'@@servername', pl))
    is_mssql |= bool(re.search(r'sysobjects', pl))
    is_mssql |= bool(re.search(r'syscolumns', pl))
    is_mssql |= bool(re.search(r'sysusers', pl))
    is_mssql |= bool(re.search(r'convert\s*\(\s*int', pl))
    is_mssql |= bool(re.search(r'char\s*\(.*?\)\s*\+', pl))
    is_mssql |= bool(re.search(r'@@rowcount', pl))
    is_mssql |= bool(re.search(r'@@error', pl))
    is_mssql |= bool(re.search(r'\btop\s+\d+', pl))

    is_sqlite = bool(re.search(r'randomblob\s*\(', pl))
    is_sqlite |= bool(re.search(r'sqlite_version\s*\(', pl))
    is_sqlite |= bool(re.search(r'sqlite_master', pl))
    is_sqlite |= bool(re.search(r'like\s*\(\s*[\"\']abcdefg', pl))

    # === SQLI TYPE DETECTION ===
    has_union = bool(re.search(r'union\s+(all\s+)?select', pl))

    has_error_marker = bool(re.search(r'xmltype\s*\(', pl))
    has_error_marker |= bool(re.search(r'extractvalue\s*\(', pl))
    has_error_marker |= bool(re.search(r'updatexml\s*\(', pl))
    has_error_marker |= bool(re.search(r'floor\s*\(\s*rand\s*\(', pl))
    has_error_marker |= bool(re.search(r'convert\s*\(\s*int\s*,', pl))
    has_error_marker |= bool(re.search(r'utl_inaddr\.get_host_address', pl))

    has_time_marker = bool(re.search(r'sleep\s*\(', pl))
    has_time_marker |= bool(re.search(r'pg_sleep\s*\(', pl))
    has_time_marker |= bool(re.search(r'waitfor\s+delay', pl))
    has_time_marker |= bool(re.search(r'dbms_pipe\.receive_message\s*\(', pl))
    has_time_marker |= bool(re.search(r'benchmark\s*\(', pl))
    has_time_marker |= bool(re.search(r'repeat\s*\(.*?,\s*(\d{6,})', pl))
    has_time_marker |= bool(re.search(r'randomblob\s*\(\s*\d{6,}', pl))
    has_time_marker |= bool(re.search(r'generate_series\s*\(\s*1\s*,\s*(\d{6,})', pl))

    has_boolean_marker = bool(re.search(r'case\s+when', pl))
    has_boolean_marker |= bool(re.search(r'\bif\s*\(', pl)) and not bool(re.search(r'sleep', pl))
    has_boolean_marker |= bool(re.search(r'\biif\s*\(', pl))
    has_boolean_marker |= bool(re.search(r'\band\s+1\s*=\s*1\b', pl))
    has_boolean_marker |= bool(re.search(r'\band\s+1\s*=\s*2\b', pl))
    has_boolean_marker |= bool(re.search(r'\bor\s+1\s*=\s*1\b', pl))
    has_boolean_marker |= bool(re.search(r'\brlike\s*\(', pl))
    has_boolean_marker |= bool(re.search(r'\belt\s*\(', pl))
    has_boolean_marker |= bool(re.search(r'\bor\s+.*?=\s*.*?--', pl))
    has_boolean_marker |= bool(re.search(r'ord\s*\(\s*mid\s*\(', pl))
    has_boolean_marker |= bool(re.search(r'0x313d31', pl))

    # === DETERMINE sqli_type ===
    if has_error_marker:
        sqli_type = 'error_based'
    elif has_time_marker:
        sqli_type = 'time_blind'
    elif has_union:
        sqli_type = 'union_based'
    elif has_boolean_marker:
        sqli_type = 'boolean_blind'
    else:
        sqli_type = 'boolean_blind'

    # === DETERMINE db_engine ===
    if is_oracle:
        db = 'oracle'
    elif is_mysql:
        db = 'mysql'
    elif is_postgres:
        db = 'postgresql'
    elif is_mssql:
        db = 'mssql'
    elif is_sqlite:
        db = 'sqlite'
    else:
        db = 'generic'

    # === DETERMINE confidence ===
    db_markers = sum([is_oracle, is_mysql, is_postgres, is_mssql, is_sqlite])

    # Short payloads
    if tokens <= 2:
        confidence = 0.70
    elif db == 'generic' and tokens <= 5:
        confidence = 0.70
    elif sqli_type == 'error_based' and db_markers >= 2:
        confidence = 1.00
    elif sqli_type == 'error_based' and db_markers >= 1:
        confidence = 0.85
    elif sqli_type == 'time_blind' and db_markers >= 2:
        confidence = 1.00
    elif sqli_type == 'time_blind' and db_markers >= 1:
        confidence = 0.85
    elif sqli_type == 'union_based' and db != 'generic' and tokens > 5:
        confidence = 1.00
    elif sqli_type == 'union_based' and db == 'generic' and tokens > 5:
        confidence = 0.85
    elif sqli_type == 'boolean_blind' and db_markers >= 2:
        confidence = 1.00
    elif sqli_type == 'boolean_blind' and db_markers >= 1 and tokens > 10:
        confidence = 1.00
    elif sqli_type == 'boolean_blind' and db_markers >= 1:
        confidence = 0.85
    elif sqli_type == 'boolean_blind' and db == 'generic' and tokens > 8:
        confidence = 0.85
    elif sqli_type == 'boolean_blind' and db == 'generic':
        confidence = 0.70
    else:
        confidence = 0.85

    # Clamp
    if confidence < 0.70:
        confidence = 0.70
    if confidence > 1.00:
        confidence = 1.00

    return pid, sqli_type, db, confidence

# Classify all
results = []
for pid, pay in sorted(payloads.items(), key=lambda x: int(x[0])):
    result = classify(pid, pay)
    results.append(result)

# Output
print('id,sqli_type,db_engine,confidence')
for r in results:
    print(f'{r[0]},{r[1]},{r[2]},{r[3]:.2f}')
