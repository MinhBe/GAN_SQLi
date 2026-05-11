import csv
import re

def detect_sqli(payload):
    p = payload.lower().strip()
    
    # ====== ENGINE DETECTION ======
    engine_scores = {'oracle': 0, 'mysql': 0, 'postgresql': 0, 'mssql': 0, 'sqlite': 0}
    
    # Oracle
    if re.search(r'xmltype\s*\(', p): engine_scores['oracle'] += 5
    if re.search(r'dbms_pipe\.', p): engine_scores['oracle'] += 4
    if re.search(r'dbms_utility\.', p): engine_scores['oracle'] += 4
    if re.search(r'utl_inaddr\.', p): engine_scores['oracle'] += 5
    if re.search(r'utl_http\.', p): engine_scores['oracle'] += 5
    if re.search(r'sys_context\s*\(', p): engine_scores['oracle'] += 4
    if re.search(r'ctxsys\.', p): engine_scores['oracle'] += 5
    if re.search(r'from\s+dual', p): engine_scores['oracle'] += 4
    if re.search(r'sys\.all_tables', p): engine_scores['oracle'] += 3
    if re.search(r'rownum', p): engine_scores['oracle'] += 2
    if re.search(r'chr\s*\(\d+\)\s*\|\|', p): engine_scores['oracle'] += 3
    chr_oracle_chain = re.findall(r'chr\s*\(\d+\)\s*\|\|', p)
    if len(chr_oracle_chain) >= 3: engine_scores['oracle'] += 1
    
    # MySQL
    if re.search(r'floor\s*\(\s*rand\s*\(', p): engine_scores['mysql'] += 5
    if re.search(r'extractvalue\s*\(', p): engine_scores['mysql'] += 5
    if re.search(r'updatexml\s*\(', p): engine_scores['mysql'] += 5
    if re.search(r'information_schema\.', p): engine_scores['mysql'] += 4
    if re.search(r'group_concat\s*\(', p): engine_scores['mysql'] += 3
    if re.search(r'load_file\s*\(', p): engine_scores['mysql'] += 3
    if re.search(r'into\s+outfile', p): engine_scores['mysql'] += 3
    if re.search(r'@@version', p): engine_scores['mysql'] += 2
    if re.search(r'@@datadir', p): engine_scores['mysql'] += 3
    if re.search(r'/\*!', p): engine_scores['mysql'] += 2
    if re.search(r"#$", p): engine_scores['mysql'] += 2
    if re.search(r'concat\s*\(0x[0-9a-f]', p): engine_scores['mysql'] += 2
    if re.search(r'benchmark\s*\(', p): engine_scores['mysql'] += 4
    # sleep without pg_ prefix
    if re.search(r'(?<!pg_)sleep\s*\(', p): engine_scores['mysql'] += 3
    
    # PostgreSQL
    if re.search(r'pg_sleep\s*\(', p): engine_scores['postgresql'] += 5
    if re.search(r'generate_series\s*\(', p): engine_scores['postgresql'] += 5
    if re.search(r'::text\b', p) or re.search(r'::int\b', p) or re.search(r'::numeric\b', p):
        engine_scores['postgresql'] += 5
    if re.search(r'\$\$', p): engine_scores['postgresql'] += 2
    if re.search(r'string_agg\s*\(', p): engine_scores['postgresql'] += 4
    if re.search(r'array_agg\s*\(', p): engine_scores['postgresql'] += 4
    if re.search(r'pg_read_file\s*\(', p): engine_scores['postgresql'] += 5
    if re.search(r'cast\s*\(.*::text\s+as\s+numeric', p) or re.search(r'cast\s*\(.*::text.*as\s+numeric', p):
        engine_scores['postgresql'] += 3
    
    # MSSQL
    if re.search(r'waitfor\s+delay', p): engine_scores['mssql'] += 5
    if re.search(r'master\.\.sysdatabases', p): engine_scores['mssql'] += 5
    if re.search(r'xp_cmdshell', p): engine_scores['mssql'] += 5
    if re.search(r'@@servername', p): engine_scores['mssql'] += 3
    if re.search(r'sysobjects', p): engine_scores['mssql'] += 4
    if re.search(r'syscolumns', p): engine_scores['mssql'] += 4
    if re.search(r'sysusers', p): engine_scores['mssql'] += 4
    if re.search(r'convert\s*\(\s*int\s*,', p): engine_scores['mssql'] += 4
    if re.search(r'top\s+\d+', p): engine_scores['mssql'] += 2
    
    # SQLite
    if re.search(r'randomblob\s*\(', p): engine_scores['sqlite'] += 5
    if re.search(r'sqlite_version\s*\(', p): engine_scores['sqlite'] += 5
    if re.search(r'sqlite_master', p): engine_scores['sqlite'] += 5
    
    # Determine engine
    best_engine = max(engine_scores, key=engine_scores.get)
    best_score = engine_scores[best_engine]
    
    if best_score >= 5:
        db_engine = best_engine
    elif best_score >= 3:
        db_engine = best_engine
    else:
        db_engine = 'generic'
    
    # char(N)+char(N)+ pattern (no ||) -> MSSQL/MySQL -> if no other markers, generic
    has_char_plus = re.search(r'char\s*\([^)]+\)\s*\+', p)
    has_chr_oracle = re.search(r'chr\s*\([^)]+\)\s*\|\|', p)
    
    # If only chr|| chain (no other oracle functions) and score < 5, check if we over-detected oracle
    if db_engine == 'oracle' and best_score < 5:
        # Check if only chr|| markers without real oracle functions
        has_oracle_func = re.search(r'xmltype|dbms_pipe|dbms_utility|utl_inaddr|utl_http|sys_context|ctxsys|from dual', p)
        if not has_oracle_func:
            # This is just chr|| chain - oracle but low confidence
            pass  # keep oracle with lower confidence
    
    # ====== ATTACK TYPE DETECTION ======
    
    # Check error markers
    has_error = False
    error_markers = 0
    if re.search(r'xmltype\s*\(', p):
        has_error = True
        error_markers += 1
    if re.search(r'extractvalue\s*\(', p):
        has_error = True
        error_markers += 1
    if re.search(r'updatexml\s*\(', p):
        has_error = True
        error_markers += 1
    if re.search(r'floor\s*\(\s*rand\s*\(', p) and re.search(r'group\s+by', p):
        has_error = True
        error_markers += 2
    if re.search(r'convert\s*\(\s*int\s*,', p):
        has_error = True
        error_markers += 1
    if re.search(r'cast\s*\(.*\s+as\s+int\)', p):
        has_error = True
        error_markers += 1
    if re.search(r'utl_inaddr\.get_host_address', p):
        has_error = True
        error_markers += 1
    if re.search(r'ctxsys\.drithsx\.sn', p):
        has_error = True
        error_markers += 2
    if re.search(r'dbms_utility\.sqlid_to_sqlhash', p):
        has_error = True
        error_markers += 1
    
    # Check time markers
    has_time = False
    time_markers = 0
    if re.search(r'(?<!pg_)sleep\s*\(\s*\d+\s*\)', p):
        has_time = True
        time_markers += 2
    if re.search(r'pg_sleep\s*\(', p):
        has_time = True
        time_markers += 2
    if re.search(r'waitfor\s+delay', p):
        has_time = True
        time_markers += 2
    if re.search(r'dbms_pipe\.receive_message\s*\(', p) and not re.search(r'xmltype\s*\(', p):
        has_time = True
        time_markers += 2
    if re.search(r'benchmark\s*\(', p):
        has_time = True
        time_markers += 2
    gs_match = re.search(r'generate_series\s*\(\s*1\s*,\s*(\d+)', p)
    if gs_match:
        count = int(gs_match.group(1))
        if count > 100000:
            has_time = True
            time_markers += 2
    if re.search(r'randomblob\s*\(\s*\d{6,}', p):
        has_time = True
        time_markers += 2
    if re.search(r'repeat\s*\(.*500000000', p) or re.search(r'repeat\s*\(.*50000000', p):
        has_time = True
        time_markers += 2
    
    # Check union markers
    has_union = bool(re.search(r'union\s+(?:all\s+)?select', p))
    
    # Check boolean markers
    has_boolean = bool(re.search(r'case\s+when\s*\(', p))
    has_boolean = has_boolean or bool(re.search(r"'\s+or\s+['\"]1['\"]\s*=\s*['\"]1['\"]", p))
    has_boolean = has_boolean or bool(re.search(r"'\s+or\s+['\"]\s*['\"]\s*=\s*['\"]", p))
    has_boolean = has_boolean or bool(re.search(r"'--", p))
    
    boolean_markers = 0
    if re.search(r'case\s+when\s*\(', p): boolean_markers += 2
    if re.search(r"'\s+or\s+['\"]1['\"]\s*=\s*['\"]1['\"]", p) or re.search(r"'\s+or\s+['\"]\s*['\"]\s*=\s*['\"]", p): boolean_markers += 2
    if re.search(r"'--", p): boolean_markers += 1
    if re.search(r"\band\s+\d+\s*=\s*\d+\b", p): boolean_markers += 1
    if re.search(r"\bor\s+\d+\s*=\s*\d+\b", p): boolean_markers += 1
    if re.search(r"admin\s*'--", p): boolean_markers += 1
    if re.search(r"'\s+or\s+''\s*=\s*'", p): boolean_markers += 2
    if re.search(r'::text\b', p) and re.search(r'case\s+when', p): boolean_markers += 1  # pg boolean
    
    # ====== DECIDE TYPE ======
    # Priority: error > time > union > boolean
    
    sqli_type = 'boolean_blind'
    
    if has_error:
        sqli_type = 'error_based'
    elif has_time:
        sqli_type = 'time_blind'
    elif has_union:
        sqli_type = 'union_based'
    elif has_boolean:
        sqli_type = 'boolean_blind'
    
    # ORDER BY alone -> union preparation
    if re.search(r'order\s+by\s+\d+', p) and not has_error and not has_time and not has_union:
        sqli_type = 'union_based'
    
    # ====== CONFIDENCE ======
    
    # Pattern-based confidence determination
    token_count = len(p.split())
    
    # 1. Very short payloads
    if token_count <= 4 and not re.search(r'case\s+when', p) and not has_union and not has_error and not has_time:
        sqli_type = 'boolean_blind'
        db_engine = 'generic'
        return sqli_type, db_engine, 0.70
    
    # 2. Simple numbers / non-SQL
    if re.match(r'^\d+$', p) or re.match(r'^[a-z]+$', p) or p in ["'", "--", "1", "1=1"]:
        return 'boolean_blind', 'generic', 0.70
    
    # 3. error_based + oracle (xmltype + from dual)
    if sqli_type == 'error_based' and db_engine == 'oracle':
        if re.search(r'xmltype\s*\(', p) and re.search(r'from\s+dual', p):
            return sqli_type, db_engine, 1.00
        if re.search(r'ctxsys\.', p):
            return sqli_type, db_engine, 1.00
        return sqli_type, db_engine, 0.85
    
    # 4. error_based + mysql
    if sqli_type == 'error_based' and db_engine == 'mysql':
        if error_markers >= 2:
            return sqli_type, db_engine, 1.00
        return sqli_type, db_engine, 0.85
    
    # 5. error_based + mssql
    if sqli_type == 'error_based' and db_engine == 'mssql':
        return sqli_type, db_engine, 0.85
    
    # 6. error_based + generic
    if sqli_type == 'error_based' and db_engine == 'generic':
        return sqli_type, db_engine, 0.85
    
    # 7. time_blind with clear engine
    if sqli_type == 'time_blind':
        if db_engine in ('mysql', 'postgresql', 'mssql', 'sqlite', 'oracle') and best_score >= 3:
            return sqli_type, db_engine, 1.00
        if db_engine == 'generic':
            return sqli_type, db_engine, 1.00
        return sqli_type, db_engine, 1.00
    
    # 8. union_based
    if sqli_type == 'union_based':
        if db_engine == 'mysql':
            return sqli_type, db_engine, 1.00
        if db_engine == 'generic':
            if has_union:
                return sqli_type, db_engine, 0.85
            # ORDER BY only
            return sqli_type, db_engine, 0.85
        return sqli_type, db_engine, 1.00
    
    # 9. boolean_blind
    if sqli_type == 'boolean_blind':
        # boolean + oracle
        if db_engine == 'oracle':
            if boolean_markers >= 2:
                return sqli_type, db_engine, 1.00
            return sqli_type, db_engine, 0.70
        
        # boolean + postgresql (:: cast + case when)
        if db_engine == 'postgresql' and best_score >= 3:
            return sqli_type, db_engine, 1.00
        
        # boolean + mssql (clear mssql markers)
        if db_engine == 'mssql' and best_score >= 4:
            return sqli_type, db_engine, 1.00
        
        # boolean + mysql
        if db_engine == 'mysql':
            if best_score >= 4:
                return sqli_type, db_engine, 1.00
            return sqli_type, db_engine, 0.70
        
        # boolean + generic
        if db_engine == 'generic':
            if boolean_markers >= 2 or token_count >= 10:
                return sqli_type, db_engine, 0.85
            return sqli_type, db_engine, 0.70
        
        # boolean + other
        return sqli_type, db_engine, 1.00
    
    return sqli_type, db_engine, 0.70


def main():
    input_file = r"C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\split_data.csv"
    output_file = r"C:\Projects\GAN_SQLi\SeqGAN_SQLi\data\split_data_labeled_batch_6001_8000.csv"
    
    rows = []
    with open(input_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.DictReader(f)
        for row in reader:
            rid = int(row['id'])
            if 6001 <= rid <= 8000:
                payload = row['payload_norm']
                sqli_type, db_engine, confidence = detect_sqli(payload)
                rows.append({
                    'id': rid,
                    'sqli_type': sqli_type,
                    'db_engine': db_engine,
                    'confidence': confidence
                })
    
    print(f"Total rows labeled: {len(rows)}")
    
    with open(output_file, 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['id', 'sqli_type', 'db_engine', 'confidence'])
        writer.writeheader()
        writer.writerows(rows)
    
    # Print summary
    type_counts = {}
    engine_counts = {}
    conf_counts = {}
    for r in rows:
        type_counts[r['sqli_type']] = type_counts.get(r['sqli_type'], 0) + 1
        engine_counts[r['db_engine']] = engine_counts.get(r['db_engine'], 0) + 1
        conf_counts[r['confidence']] = conf_counts.get(r['confidence'], 0) + 1
    
    print(f"Output written to: {output_file}")
    print("\n=== Summary ===")
    print(f"sqli_type: {type_counts}")
    print(f"db_engine: {engine_counts}")
    print(f"confidence: {conf_counts}")


if __name__ == '__main__':
    main()
