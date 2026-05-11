import csv
import re

def norm(p):
    return re.sub(r'\s+', ' ', p.lower().strip())

rows = []
with open('data/split_data.csv', 'r', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for r in reader:
        rid = int(r['id'])
        if 3001 <= rid <= 3500:
            rows.append((rid, r['payload_norm']))

def has_func(p, name):
    return re.search(r'\b' + re.escape(name) + r'\s*\(', p) is not None

def label_row(rid, payload):
    p = norm(payload)

    # --- error_based ---

    # Oracle: xmltype
    if has_func(p, 'xmltype') and 'from dual' in p:
        return ('error_based', 'oracle', 1.00)

    # Oracle: ctxsys.drithsx.sn
    if 'ctxsys.drithsx.sn' in p:
        return ('error_based', 'oracle', 1.00)

    # Oracle: utl_inaddr.get_host_address
    if 'utl_inaddr.get_host_address' in p:
        return ('error_based', 'oracle', 1.00)

    # MySQL: floor(rand with group by
    if re.search(r'floor\s*\(\s*rand\s*\(', p) and 'group by' in p:
        return ('error_based', 'mysql', 1.00)

    # MySQL: extractvalue
    if has_func(p, 'extractvalue') and (has_func(p, 'concat') or '0x' in p):
        return ('error_based', 'mysql', 1.00)

    # MySQL: updatexml
    if has_func(p, 'updatexml'):
        return ('error_based', 'mysql', 1.00)

    # MySQL: exp(~(select...concat))
    if re.search(r'exp\s*\(~\s*\(select', p) and has_func(p, 'concat'):
        return ('error_based', 'mysql', 1.00)

    # MSSQL: convert(int, ...)
    if re.search(r'convert\s*\(\s*int\s*,', p):
        return ('error_based', 'mssql', 0.85)

    # Oracle: dbms_utility.sqlid_to_sqlhash
    if 'dbms_utility.sqlid_to_sqlhash' in p:
        return ('error_based', 'oracle', 1.00)

    # Oracle: procedure analyse with extractvalue (MySQL)
    if 'procedure analyse' in p and has_func(p, 'extractvalue'):
        return ('error_based', 'mysql', 1.00)

    # Oracle: row(...) > (select count(*),concat(...floor(rand...)))
    if re.search(r'row\s*\(', p) and re.search(r'floor\s*\(\s*rand\s*\(', p):
        return ('error_based', 'mysql', 1.00)

    # Oracle error: cast(1 as int) / (select 0 from dual)
    if re.search(r'cast\s*\(\s*1\s+as\s+int\s*\)\s*/\s*\(', p) and 'from dual' in p:
        return ('error_based', 'oracle', 1.00)

    # --- union_based ---
    if re.search(r'union\s+all\s+select', p) or re.search(r'union\s+select', p):
        de = 'generic'
        if '#' in p:
            de = 'mysql'
        elif re.search(r'@@version', p):
            de = 'mysql'
        return ('union_based', de, 1.00)

    # --- time_blind ---

    # MySQL: sleep(N) without pg_sleep
    if has_func(p, 'sleep') and 'pg_sleep' not in p:
        return ('time_blind', 'mysql', 1.00)

    # PostgreSQL: pg_sleep
    if has_func(p, 'pg_sleep'):
        return ('time_blind', 'postgresql', 1.00)

    # MSSQL: WAITFOR DELAY
    if 'waitfor delay' in p:
        return ('time_blind', 'mssql', 1.00)

    # Oracle: dbms_pipe.receive_message
    if 'dbms_pipe.receive_message' in p:
        return ('time_blind', 'oracle', 1.00)

    # MySQL: benchmark with md5
    if has_func(p, 'benchmark') and 'md5' in p:
        return ('time_blind', 'mysql', 1.00)

    # PostgreSQL: generate_series large (range, not row-generator)
    if has_func(p, 'generate_series') and '5000000' in str([m for m in re.findall(r'\d+', p)]):
        return ('time_blind', 'postgresql', 1.00)

    # SQLite: randomblob with large number
    if has_func(p, 'randomblob') and ('500000000' in p):
        return ('time_blind', 'sqlite', 1.00)

    # MySQL: rlike sleep
    if re.search(r'rlike\s+sleep\s*\(', p):
        return ('time_blind', 'mysql', 1.00)

    # Heavy repeat/regexp_substring with large constants
    if (has_func(p, 'regexp_substring') or has_func(p, 'regexp_substr')) and ('500000000' in p or '5000000000' in p):
        if has_func(p, 'sleep'):
            return ('time_blind', 'mysql', 1.00)
        return ('time_blind', 'mysql', 0.85)

    # CALL REGEXP_SUBSTRING / CALL CASE WHEN template
    if p.startswith('call regexp_substring') or p.startswith(';call regexp_substring'):
        return ('time_blind', 'mysql', 0.85)

    # OR SLEEP template
    if 'or sleep(' in p:
        return ('time_blind', 'mysql', 0.85)

    # elt(...sleep(5)...)
    if re.search(r'elt\s*\([^)]*sleep\s*\(', p):
        return ('time_blind', 'mysql', 1.00)

    # Cartesian join heavy
    if 'all_users' in p and re.search(r't\d+,all_users t\d+,all_users t\d+,all_users', p):
        return ('time_blind', 'oracle', 0.85)

    # --- boolean_blind ---

    # PostgreSQL: generate_series with case when (boolean inference, no large number)
    if has_func(p, 'generate_series') and 'case when' in p:
        return ('boolean_blind', 'postgresql', 1.00)

    # PostgreSQL: ::text or ::int or ::numeric with CASE WHEN
    if ('::text' in p or '::int' in p or '::numeric' in p) and 'case when' in p:
        return ('boolean_blind', 'postgresql', 1.00)

    # MySQL: rlike (select case when)  
    if re.search(r'rlike\s*\(select', p) and 'case when' in p:
        return ('boolean_blind', 'mysql', 1.00)

    # MySQL: case when ... 1/(select 0) conditional division-by-zero boolean
    if 'case when' in p and re.search(r'1/\s*\(\s*select\s+0\s*\)', p):
        return ('boolean_blind', 'mysql', 1.00)

    # MSSQL: iif(cond,1,1/0) division by zero boolean
    if has_func(p, 'iif') and '1/0' in p:
        return ('boolean_blind', 'mssql', 1.00)

    # CASE WHEN with master..sysdatabases (MSSQL)
    if 'case when' in p and 'master..sysdatabases' in p:
        return ('boolean_blind', 'mssql', 1.00)

    # char()+ char()+ chain (MSSQL pattern - uses + not ||)
    if re.search(r"char\s*\(\s*\d+\s*\)\s*\+\s*char\s*\(\s*\d+\s*\)", p):
        return ('boolean_blind', 'mssql', 0.85)

    # make_set (MySQL)
    if has_func(p, 'make_set'):
        return ('boolean_blind', 'mysql', 0.85)

    # elt(cond, val1, val2) without sleep
    if has_func(p, 'elt') and 'sleep' not in p:
        return ('boolean_blind', 'mysql', 0.85)

    # rdb$database (Firebird) 
    if 'rdb$database' in p:
        return ('boolean_blind', 'generic', 0.85)

    # CASE WHEN with from dual (Oracle)
    if 'case when' in p and 'from dual' in p:
        return ('boolean_blind', 'oracle', 0.85)

    # CASE WHEN with information_schema (MySQL)
    if 'case when' in p and 'information_schema' in p:
        return ('boolean_blind', 'mysql', 0.85)

    # CASE WHEN generic
    if 'case when' in p:
        return ('boolean_blind', 'generic', 0.85)

    # rlike + case when (fallback)
    if 'rlike' in p and 'case when' in p:
        return ('boolean_blind', 'mysql', 0.85)

    # IIF (MSSQL)
    if has_func(p, 'iif'):
        return ('boolean_blind', 'mssql', 0.85)

    # IF(cond, val1, val2) - MySQL
    if re.search(r'\bif\s*\([^)]+,[^)]+,[^)]+\)', p):
        return ('boolean_blind', 'mysql', 0.85)

    # chr()||chr() chain (Oracle)
    if re.search(r"chr\s*\(\s*\d+\s*\)\s*\|\|\s*chr\s*\(\s*\d+\s*\)", p):
        return ('boolean_blind', 'oracle', 0.85)

    # Simple 1=1 pattern (boolean)
    if re.search(r'\d+\s*=\s*\d+', p):
        return ('boolean_blind', 'generic', 0.70)

    # Simple OR/AND auth bypass
    if "or 1=1" in p or "and 1=1" in p or "or '1'='1" in p or "or '1'='1" in p:
        return ('boolean_blind', 'generic', 0.85)

    # Simple quote bypass
    if re.search(r"""['"]\s+or\s+['"]""", p) or re.search(r"""or\s+['"]\s*=\s*['"]""", p):
        return ('boolean_blind', 'generic', 0.70)

    # Very short / obfuscated
    if len(p) < 10:
        return ('boolean_blind', 'generic', 0.70)

    # Has like/and/or patterns
    if "like" in p or "and" in p or "or" in p:
        return ('boolean_blind', 'generic', 0.70)

    return ('boolean_blind', 'generic', 0.70)

results = []
for rid, payload in rows:
    sqli_type, db_engine, conf = label_row(rid, payload)
    results.append((rid, sqli_type, db_engine, f'{conf:.2f}'))

outpath = 'data/split_data_labeled_batch_3001_3500.csv'
with open(outpath, 'w', newline='', encoding='utf-8') as f:
    writer = csv.writer(f)
    writer.writerow(['id', 'sqli_type', 'db_engine', 'confidence'])
    writer.writerows(results)

# Print summary
from collections import Counter
types = Counter(r[1] for r in results)
engines = Counter(r[2] for r in results)
print(f'Written {len(results)} rows')
print(f'sqli_type distribution: {dict(types)}')
print(f'db_engine distribution: {dict(engines)}')
print()
print('Sample rows (first 20):')
for r in results[:20]:
    print(f'{r[0]},{r[1]},{r[2]},{r[3]}')
