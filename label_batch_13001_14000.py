import re
import csv
import sys

def determine_db_engine(payload):
    payload_l = payload.lower()
    
    # === Oracle markers (highest priority per guide: Oracle markers ưu tiên cao nhất) ===
    if re.search(r'\bxmltype\s*\(', payload_l):
        return 'oracle'
    if re.search(r'\bctxsys\.drithsx\.sn\s*\(', payload_l):
        return 'oracle'
    if re.search(r'\bdbms_utility\.sqlid_to_sqlhash\s*\(', payload_l):
        return 'oracle'
    if re.search(r'\butl_inaddr', payload_l):
        return 'oracle'
    if re.search(r'\butl_http', payload_l):
        return 'oracle'
    if re.search(r'\bsys_context\s*\(', payload_l):
        return 'oracle'
    if re.search(r'\bfrom\s+dual\b', payload_l):
        return 'oracle'
    if re.search(r'\bsys\.all_tables\b', payload_l):
        return 'oracle'
    if re.search(r'\brownum\b', payload_l):
        return 'oracle'
    if re.search(r'\bdbms_pipe\.', payload_l):
        return 'oracle'
    if re.search(r'\bdbms_lock\.sleep\s*\(', payload_l):
        return 'oracle'
    if re.search(r'\buser_lock\.sleep\s*\(', payload_l):
        return 'oracle'
    
    # === PostgreSQL markers ===
    if re.search(r'::text\b|::int\b|::numeric\b', payload_l):
        return 'postgresql'
    if re.search(r'\bpg_sleep\s*\(', payload_l):
        return 'postgresql'
    if re.search(r'\bgenerate_series\s*\(', payload_l):
        return 'postgresql'
    if re.search(r'\bstring_agg\s*\(', payload_l):
        return 'postgresql'
    
    # chr(X)||chr(Y) pattern → Oracle (guide: chr(X)||chr(Y) chain = oracle)
    if re.search(r'chr\s*\(\s*\d+\s*\)\s*\|\|', payload_l):
        return 'oracle'
    
    # === MSSQL markers ===
    if re.search(r'\bwaitfor\s+delay\b', payload_l):
        return 'mssql'
    if re.search(r'\bmaster\.\.sysdatabases\b', payload_l):
        return 'mssql'
    if re.search(r'\bsysobjects\b', payload_l):
        return 'mssql'
    if re.search(r'\bsyscolumns\b', payload_l):
        return 'mssql'
    if re.search(r'\bsysusers\b', payload_l):
        return 'mssql'
    if re.search(r'\bxp_cmdshell\b', payload_l):
        return 'mssql'
    if re.search(r'@@servername\b', payload_l):
        return 'mssql'
    
    # char(X)+char(Y)+char(Z) pattern = MSSQL concatenation
    # Check for multiple char()+char() connected
    if re.search(r'char\s*\(\s*\d+\s*\)\s*\+', payload_l):
        # Only if there's no Oracle/PG marker
        if not re.search(r'xmltype|from dual|ctxsys|::text|::int|::numeric', payload_l):
            return 'mssql'
    
    # convert(int, / convert(varchar, pattern = MSSQL
    if re.search(r'convert\s*\(\s*(int|varchar|nvarchar)\s*,', payload_l):
        return 'mssql'
    
    # === MySQL markers ===
    if re.search(r'\bbenchmark\s*\(', payload_l):
        return 'mysql'
    if re.search(r'\bfloor\s*\(\s*rand\s*\(', payload_l):
        return 'mysql'
    if re.search(r'\bextractvalue\s*\(', payload_l):
        return 'mysql'
    if re.search(r'\bupdatexml\s*\(', payload_l):
        return 'mysql'
    if re.search(r'\binformation_schema\.', payload_l):
        return 'mysql'
    if re.search(r'\bconcat\s*\(', payload_l) and not re.search(r'xmltype|from dual|ctxsys', payload_l):
        return 'mysql'
    if re.search(r'\bgroup_concat\s*\(', payload_l):
        return 'mysql'
    if re.search(r'@@version\b', payload_l) and not re.search(r'xmltype|from dual', payload_l):
        return 'mysql'
    if re.search(r'@@datadir\b', payload_l):
        return 'mysql'
    if re.search(r'\bload_file\s*\(', payload_l):
        return 'mysql'
    if re.search(r'\binto\s+outfile\b', payload_l):
        return 'mysql'
    if re.search(r'\bexp\s*\(', payload_l):
        return 'mysql'
    if re.search(r'#\s*$', payload):
        return 'mysql'
    if re.search(r'\brlike\b', payload_l):
        return 'mysql'
    if re.search(r'\bgtid_subset\s*\(', payload_l):
        return 'mysql'
    if re.search(r'\bmake_set\s*\(', payload_l):
        return 'mysql'
    if re.search(r'\bprocedure\s+analyse\b', payload_l):
        return 'mysql'
    if re.search(r'\belt\s*\(', payload_l) and not re.search(r'xmltype|from dual|ctxsys', payload_l):
        return 'mysql'
    if re.search(r'\bif\s*\(', payload_l) and not re.search(r'xmltype|from dual|ctxsys', payload_l):
        return 'mysql'
    if re.search(r'\bcrypt_key\s*\(', payload_l):
        return 'mysql'
    if re.search(r'\bregexp_substring\s*\(', payload_l):
        return 'mysql'
    # 0x hex literals are MySQL
    if re.search(r'\b0x[0-9a-f]+\b', payload_l):
        return 'mysql'
    
    # === SQLite markers ===
    if re.search(r'\brandomblob\s*\(', payload_l):
        return 'sqlite'
    if re.search(r'\bsqlite_version\s*\(', payload_l):
        return 'sqlite'
    if re.search(r'\bsqlite_master\b', payload_l):
        return 'sqlite'
    
    # === Default: generic ===
    return 'generic'


def determine_sqli_type(payload, db_engine):
    payload_l = payload.lower()
    
    # Detecting markers
    has_union = bool(re.search(r'\bunion\s+(all\s+)?select\b', payload_l, re.IGNORECASE))
    has_order_by = bool(re.search(r'\border\s+by\s+\d+', payload_l))
    
    # Time markers
    has_sleep = bool(re.search(r'(?:^|\W)sleep\s*\(\s*\d+\s*\)', payload_l))
    has_pg_sleep = bool(re.search(r'\bpg_sleep\s*\(\s*\d+\s*\)', payload_l))
    has_waitfor = bool(re.search(r'\bwaitfor\s+delay\b', payload_l))
    has_benchmark = bool(re.search(r'\bbenchmark\s*\(', payload_l))
    has_dbms_pipe = bool(re.search(r'\bdbms_pipe\.receive_message\s*\(', payload_l))
    has_dbms_lock = bool(re.search(r'\bdbms_lock\.sleep\s*\(', payload_l))
    has_user_lock = bool(re.search(r'\buser_lock\.sleep\s*\(', payload_l))
    has_generate_large = bool(re.search(r'generate_series\s*\(\s*1\s*,\s*\d{6,}', payload_l))
    has_repeat_large = bool(re.search(r'repeat\s*\(.*\d{6,}', payload_l))
    has_randomblob_large = bool(re.search(r'randomblob\s*\(\s*\d{6,}', payload_l))
    
    # Error markers
    has_xmltype = bool(re.search(r'\bxmltype\s*\(', payload_l))
    has_ctxsys_error = bool(re.search(r'\bctxsys\.drithsx\.sn\s*\(', payload_l))
    has_extractvalue = bool(re.search(r'\bextractvalue\s*\(', payload_l))
    has_updatexml = bool(re.search(r'\bupdatexml\s*\(', payload_l))
    has_floor_rand_group = bool(re.search(r'floor\s*\(\s*rand\s*\(.*\).*group\s+by', payload_l))
    has_convert_int = bool(re.search(r'convert\s*\(\s*int\s*,', payload_l))
    has_utl_inaddr = bool(re.search(r'\butl_inaddr\.', payload_l))
    has_exp_error = bool(re.search(r'\bexp\s*\(\s*~\s*\(', payload_l))
    has_gtid_error = bool(re.search(r'\bgtid_subset\s*\(', payload_l))
    
    # Boolean markers
    has_case_when = bool(re.search(r'\bcase\s+when\b', payload_l))
    has_if_func = bool(re.search(r'(?:^|\W)if\s*\(', payload_l))
    has_elt_bool = bool(re.search(r'\belt\s*\(\s*\d+\s*=\s*\d+', payload_l))
    has_make_set = bool(re.search(r'\bmake_set\s*\(', payload_l))
    has_rlike = bool(re.search(r'\brlike\b', payload_l))
    has_and_or = bool(re.search(r'(?:^|\W)and\s+\d+\s*=\s*\d+|(?:^|\W)or\s+\d+\s*=\s*\d+', payload_l))
    has_gtid = bool(re.search(r'\bgtid_subset\s*\(', payload_l))
    has_row_greater = bool(re.search(r'\brow\s*\(.*\).*>', payload_l))
    
    # Boolean bypass
    has_or_1_1 = bool(re.search(r"'\s+or\s+'\d+'\s*=\s*'\d+", payload_l))
    has_or_true = bool(re.search(r"or\s+1\s*=\s*1", payload_l))
    has_and_1_1 = bool(re.search(r"and\s+1\s*=\s*1", payload_l))
    
    # === Priority-based classification ===
    
    # Rule Case 1: UNION + error marker → error_based
    if has_union:
        if has_xmltype or has_ctxsys_error or has_convert_int or has_utl_inaddr or has_extractvalue or has_updatexml:
            return 'error_based'
    
    # Rule Case 2: sleep + CASE WHEN → time_blind (sleep ưu tiên)
    if has_sleep or has_pg_sleep or has_waitfor or has_dbms_lock or has_user_lock:
        return 'time_blind'
    
    # Rule Case 6: dbms_pipe standalone → time_blind
    if has_dbms_pipe:
        return 'time_blind'
    
    # benchmark with large number → time_blind
    if has_benchmark:
        return 'time_blind'
    
    # generate_series(1, large) → time_blind
    if has_generate_large:
        return 'time_blind'
    
    # repeat with large number → time_blind (heavy computation)
    if has_repeat_large:
        return 'time_blind'
    
    # randomblob large → time_blind
    if has_randomblob_large:
        return 'time_blind'
    
    # Error-based markers (highest priority technique)
    if has_xmltype or has_ctxsys_error:
        return 'error_based'
    if has_extractvalue or has_updatexml:
        return 'error_based'
    if has_floor_rand_group:
        return 'error_based'
    if has_convert_int and has_case_when:
        return 'error_based'
    if has_utl_inaddr:
        return 'error_based'
    if has_exp_error:
        return 'error_based'
    if has_gtid_error:
        return 'error_based'
    
    # UNION-based
    if has_union:
        return 'union_based'
    if has_order_by:
        # order by with # or -- comment → union probe
        return 'union_based'
    
    # Boolean-based
    if has_case_when or has_if_func or has_elt_bool or has_make_set or has_rlike or has_gtid or has_row_greater:
        return 'boolean_blind'
    if has_or_1_1 or has_or_true or has_and_1_1 or has_and_or:
        return 'boolean_blind'
    
    # Short/comparison-based
    if re.search(r'\d+\s*=\s*\d+', payload_l):
        return 'boolean_blind'
    
    # Default
    return 'boolean_blind'


def determine_confidence(payload, sqli_type, db_engine):
    payload_l = payload.lower()
    tokens = payload.split()
    token_count = len(tokens)
    
    # Very short / obfuscated / no SQL keywords
    if token_count <= 3:
        return 0.70
    
    # Count clear markers
    marker_count = 0
    
    # DB engine markers
    strong_db_markers = [
        'xmltype', 'from dual', 'ctxsys.drithsx.sn', 'dbms_utility',
        'dbms_pipe', 'utl_inaddr', 'pg_sleep', '::text', '::int', '::numeric',
        'generate_series', 'waitfor delay', 'sysobjects', 'syscolumns',
        'benchmark(', 'floor(rand()', 'extractvalue(', 'updatexml(',
        'information_schema.', 'randomblob(', 'sqlite_version(',
        'concat(', 'elt(', 'make_set(', 'exp(', 'rlike',
        'rdb$database', 'master..sysdatabases'
    ]
    for m in strong_db_markers:
        if m in payload_l:
            marker_count += 1
    
    # Technique markers
    technique_markers = ['union select', 'union all select', 'case when',
                         'sleep(', 'waitfor delay', 'benchmark(', 'pg_sleep(',
                         'extractvalue(', 'updatexml(']
    for m in technique_markers:
        if m in payload_l:
            marker_count += 1
    
    # Payloads with clear markers
    if marker_count >= 2:
        # Check for ambiguity
        if db_engine == 'generic' and sqli_type == 'boolean_blind':
            return 0.85
        return 1.00
    
    if marker_count == 1:
        if db_engine == 'generic':
            return 0.85
        return 0.85
    
    # Payloads with no clear markers
    if token_count <= 5:
        return 0.70
    
    return 0.85


def label_row(payload):
    db_engine = determine_db_engine(payload)
    sqli_type = determine_sqli_type(payload, db_engine)
    confidence = determine_confidence(payload, sqli_type, db_engine)
    return sqli_type, db_engine, confidence


# Main processing
input_file = r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\split_data.csv'
output_file = r'C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\temp_batch_13001_14000.csv'

# Read all rows from CSV
all_rows = []
with open(input_file, 'r', encoding='utf-8') as f:
    reader = csv.reader(f)
    header = next(reader)
    for row in reader:
        all_rows.append(row)

print(f"Total rows in file: {len(all_rows)}")

# Filter for ids 13001 to 14000
target_rows = []
for row in all_rows:
    try:
        row_id = int(row[0])
        if 13001 <= row_id <= 14000:
            target_rows.append(row)
    except (ValueError, IndexError):
        continue

print(f"Target rows: {len(target_rows)} (ids 13001-14000)")

# Label each row
results = []
for i, row in enumerate(target_rows):
    row_id = row[0]
    payload_norm = row[1]  # payload_norm column
    sqli_type, db_engine, confidence = label_row(payload_norm)
    results.append([row_id, sqli_type, db_engine, str(confidence)])
    
    if (i + 1) % 100 == 0:
        print(f"  Labeled {i+1}/{len(target_rows)} rows...")

# Write output
with open(output_file, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'sqli_type', 'db_engine', 'confidence'])
    writer.writerows(results)

print(f"\nDone! Output written to {output_file}")
print(f"Total labeled: {len(results)} rows")
