"""Label chunk_004.csv based on payload tokens + priority table."""
import pandas as pd
import re
import csv

IN = r'C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks\chunk_004.csv'
OUT = r'C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks\chunk_004_labeled.csv'

df = pd.read_csv(IN)

# Priority table (lower priority = stronger signal)
# benign=1, auth_bypass=2, boolean_blind=3, error_based=4/heavy_query=4,
# time_blind=5, out_of_band=6, union_based=7, stacked_queries=8, polyglot=9

def detect(payload, a_type, a_db, c_type, c_db):
    """Return (sqli_type, db_engine, confidence, reasoning, found_tokens)."""
    if not isinstance(payload, str):
        return ('benign', 'generic', 0.5, 'UNCERTAIN: empty/NaN payload', [])
    p = payload.lower()
    tokens = []  # collected (priority, type, db_hint, token, why)

    # ---- Time-blind signals (priority 5) ----
    if re.search(r'\bpg_sleep\s*\(', p):
        tokens.append((5, 'time_blind', 'postgresql', 'pg_sleep(',
                       "pg_sleep() is PostgreSQL time-based blind function"))
    if re.search(r'\bsleep\s*\(', p):
        tokens.append((5, 'time_blind', 'mysql', 'sleep(',
                       "sleep() is MySQL time-based blind function"))
    if re.search(r'\bwaitfor\s+delay\b', p):
        tokens.append((5, 'time_blind', 'mssql', 'waitfor delay',
                       "WAITFOR DELAY is MSSQL time-based blind"))
    if re.search(r'\bbenchmark\s*\(', p):
        tokens.append((5, 'time_blind', 'mysql', 'benchmark(',
                       "benchmark() is MySQL CPU-burn time-based blind"))
    if re.search(r'\bdbms_pipe\.receive_message\b', p):
        tokens.append((5, 'time_blind', 'oracle', 'dbms_pipe.receive_message',
                       "dbms_pipe.receive_message is Oracle time-based blind"))
    if re.search(r'\bdbms_lock\.sleep\b', p):
        tokens.append((5, 'time_blind', 'oracle', 'dbms_lock.sleep',
                       "dbms_lock.sleep is Oracle time-based blind"))
    if re.search(r'\brandomblob\s*\(', p):
        tokens.append((5, 'time_blind', 'sqlite', 'randomblob(',
                       "randomblob() is SQLite time-based blind via large blob"))

    # ---- Error-based signals (priority 4) ----
    if re.search(r'\bxmltype\s*\(', p):
        tokens.append((4, 'error_based', 'oracle', 'xmltype(',
                       "xmltype() triggers Oracle XML cast error"))
    if re.search(r'\bextractvalue\s*\(', p):
        tokens.append((4, 'error_based', 'mysql', 'extractvalue(',
                       "extractvalue() triggers MySQL XPath error"))
    if re.search(r'\bupdatexml\s*\(', p):
        tokens.append((4, 'error_based', 'mysql', 'updatexml(',
                       "updatexml() triggers MySQL XPath error"))
    if re.search(r'\butl_inaddr\b', p):
        tokens.append((4, 'error_based', 'oracle', 'utl_inaddr',
                       "utl_inaddr.get_host_address is Oracle error/OOB"))
    if re.search(r'\bctxsys\.', p):
        tokens.append((4, 'error_based', 'oracle', 'ctxsys.',
                       "ctxsys.drithsx.sn is Oracle error-based"))

    # ---- Heavy query (priority 4) ----
    # Big numbers (5000000+) inside repeat/generate_series/all_users joins
    if re.search(r'\brepeat\s*\([^()]*,\s*\d{7,}', p) or re.search(r',\s*5\d{8,}\s*\)', p):
        tokens.append((4, 'heavy_query', 'generic', 'repeat(...,500000000)',
                       "repeat() with huge count (>=10^7) creates DoS-style heavy query"))
    if re.search(r'\bgenerate_series\s*\(', p):
        tokens.append((4, 'heavy_query', 'postgresql', 'generate_series(',
                       "generate_series() in PostgreSQL builds heavy query"))
    # Multiple all_users joins
    if re.search(r'all_users\s+t1.*all_users\s+t5', p):
        tokens.append((4, 'heavy_query', 'oracle', 'all_users t1..t5',
                       "Cartesian join over all_users t1..t5 is Oracle heavy query"))
    if len(re.findall(r'\ball_users\b', p)) >= 4:
        tokens.append((4, 'heavy_query', 'oracle', 'all_users x N',
                       "Multiple all_users self-joins for Oracle heavy query"))
    # rdb$fields,rdb$types,... cartesian (firebird heavy)
    if re.search(r'rdb\$fields.*rdb\$types', p) and 'count' in p:
        tokens.append((4, 'heavy_query', 'firebird', 'rdb$fields,rdb$types',
                       "Firebird heavy query joining rdb$fields and rdb$types"))
    # Cartesian joins with 3+ tables and count(*) -> heavy query
    if re.search(r'select\s+count\s*\(\s*\*\s*\)\s+from\b', p):
        # check for >=3 table aliases t1,t2,t3 etc.
        if re.search(r'\bt1\b.*\bt2\b.*\bt3\b', p) or re.search(r'(\w+\.\w+\s+as\s+t\d+\s*,\s*){2,}', p):
            tokens.append((4, 'heavy_query', 'generic', 'count(*) from T t1,T t2,T t3',
                           "count(*) over 3+ self-joined tables creates cartesian heavy query"))
    # sysibm.systables joins (DB2 heavy)
    if len(re.findall(r'sysibm\.systables', p)) >= 2:
        tokens.append((4, 'heavy_query', 'db2', 'sysibm.systables x N',
                       "Multiple sysibm.systables joins for DB2 heavy query"))
    # sysusers cartesian joins (MSSQL heavy)
    if len(re.findall(r'\bsysusers\b', p)) >= 3:
        tokens.append((4, 'heavy_query', 'mssql', 'sysusers x N',
                       "Cartesian join of sysusers aliases for MSSQL heavy query"))
    # domain.domains/columns/tables joins (Firebird-ish heavy)
    if re.search(r'domain\.domains', p) and re.search(r'domain\.(columns|tables)', p):
        tokens.append((4, 'heavy_query', 'firebird', 'domain.domains,domain.columns',
                       "domain.domains/columns/tables cartesian for heavy query"))
    # master..sysdatabases (MSSQL signal)
    if re.search(r'master\.\.sysdatabases', p):
        tokens.append((3, 'boolean_blind', 'mssql', 'master..sysdatabases',
                       "master..sysdatabases used in CASE WHEN for MSSQL boolean blind"))
    # regexp_substring repeat big number => heavy_query SQLite-ish
    if 'regexp_substring' in p and 'repeat' in p:
        tokens.append((4, 'heavy_query', 'generic', 'regexp_substring(repeat(...))',
                       "regexp_substring over repeat() creates compute-heavy query"))
    # crypt_key + large literal
    if 'crypt_key' in p:
        tokens.append((4, 'heavy_query', 'generic', 'crypt_key(',
                       "crypt_key() with huge repeat() count is heavy query DoS"))

    # ---- Out-of-band (priority 6) ----
    if re.search(r'\bload_file\s*\(', p):
        tokens.append((6, 'out_of_band', 'mysql', 'load_file(',
                       "load_file() is MySQL OOB file-read"))
    if re.search(r'\butl_http\b', p):
        tokens.append((6, 'out_of_band', 'oracle', 'utl_http',
                       "utl_http.request is Oracle OOB HTTP"))
    if re.search(r'\bxp_dirtree\b', p):
        tokens.append((6, 'out_of_band', 'mssql', 'xp_dirtree',
                       "xp_dirtree is MSSQL OOB file listing"))

    # ---- Stacked queries (priority 8) ----
    if re.search(r'\bxp_cmdshell\b', p):
        tokens.append((8, 'stacked_queries', 'mssql', 'xp_cmdshell',
                       "xp_cmdshell is MSSQL stacked shell exec"))
    if re.search(r';\s*(insert|update|delete|drop|exec|create)\b', p):
        tokens.append((8, 'stacked_queries', 'generic', '; <DML>',
                       "Semicolon-separated DML/DDL after primary query is stacked"))
    if re.search(r'\bdrop\s+function\b', p):
        tokens.append((8, 'stacked_queries', 'generic', 'drop function',
                       "DROP FUNCTION inside ELSE branch is stacked DDL"))

    # ---- Union-based (priority 7) ----
    if re.search(r'\bunion\s+(all\s+)?select\b', p):
        # count selects to distinguish from heavy
        u_count = len(re.findall(r'\bunion\s+(?:all\s+)?select\b', p))
        # If union is part of a heavy query construct, heavy_query overrides
        tokens.append((7, 'union_based', 'generic', f'UNION SELECT (x{u_count})',
                       f"Detected {u_count} UNION SELECT clause(s) for data extraction"))

    # ---- Boolean blind (priority 3) ----
    if re.search(r'\bif\s*\(.*,.*,.*\)', p):
        tokens.append((3, 'boolean_blind', 'mysql', 'IF(cond,a,b)',
                       "IF(cond,a,b) is MySQL boolean conditional"))
    if re.search(r'\belt\s*\(', p):
        tokens.append((3, 'boolean_blind', 'mysql', 'elt(',
                       "ELT() is MySQL boolean conditional select"))
    if re.search(r'\brlike\b', p):
        tokens.append((3, 'boolean_blind', 'mysql', 'rlike',
                       "RLIKE is MySQL regex boolean"))
    # Loose AND/OR N=N (allow parentheses between)
    if re.search(r'\b(and|or)\s*\(?\s*\(?\s*\d+\s*=\s*\d+', p):
        tokens.append((3, 'boolean_blind', 'generic', 'AND/OR N=N',
                       "AND/OR N=N numeric tautology for boolean blind"))
    if re.search(r"\b(and|or)\s*\(?\s*'[^']+'\s*=\s*'", p):
        tokens.append((3, 'boolean_blind', 'generic', "AND/OR 'x'='x'",
                       "AND/OR string equality tautology for boolean blind"))
    if re.search(r"\b(and|or)\s+\w+\s+like\s+", p):
        tokens.append((3, 'boolean_blind', 'generic', "AND/OR ... LIKE ...",
                       "LIKE comparison in AND/OR clause for boolean blind"))
    if re.search(r"'[a-z0-9]+'\s+like\s+'[a-z0-9]+", p):
        tokens.append((3, 'boolean_blind', 'generic', "'x' LIKE 'x'",
                       "Quoted-string LIKE tautology for boolean blind"))
    if re.search(r'"[a-z0-9]+"\s+like\s+"[a-z0-9]+', p):
        tokens.append((3, 'boolean_blind', 'generic', '"x" LIKE "x"',
                       "Double-quoted-string LIKE tautology for boolean blind"))
    if re.search(r'"[a-z0-9%]+"\s*=\s*"[a-z0-9%]*', p):
        tokens.append((3, 'boolean_blind', 'generic', '"x"="x"',
                       "Double-quoted string equality tautology for boolean blind"))
    if re.search(r'\bcase\s+when\b', p):
        tokens.append((3, 'boolean_blind', 'generic', 'case when',
                       "CASE WHEN conditional select for boolean blind"))
    if re.search(r'\bsubstring\s*\(.*\)\s*=\s*', p):
        tokens.append((3, 'boolean_blind', 'generic', 'substring()=...',
                       "substring() char-extract comparison for boolean blind"))
    if re.search(r'\bdbms_utility\.', p):
        tokens.append((3, 'boolean_blind', 'oracle', 'dbms_utility.',
                       "dbms_utility.sqlid_to_sqlhash used as side-channel for Oracle boolean blind"))
    # order by N (--/#) probing column count
    if re.search(r'\border\s+by\s+\d+\s*(--|#)', p):
        tokens.append((3, 'boolean_blind', 'generic', 'order by N --/#',
                       "ORDER BY N with comment terminator is column-count probing for boolean blind"))

    # ---- Auth bypass (priority 2) ----
    if re.search(r"(admin|administrator)['\"]?\s*--", p) or re.search(r"admin\s*'\s*--", p):
        tokens.append((2, 'auth_bypass', 'generic', "admin'--",
                       "admin'-- pattern bypasses login by truncating password check"))
    if re.search(r"'\s*or\s*'1'\s*=\s*'1", p):
        tokens.append((2, 'auth_bypass', 'generic', "' or '1'='1",
                       "' OR '1'='1 classic auth bypass tautology"))

    # ---- Polyglot (priority 9) ----
    if '<script' in p or 'onerror' in p or 'javascript:' in p:
        tokens.append((9, 'polyglot', 'generic', '<script/onerror',
                       "Contains XSS payload combined with SQLi = polyglot"))

    # ---- DB engine inference (independent) ----
    db = None
    if re.search(r'\bdual\b|\butl_inaddr\b|\bxmltype\b|\bctxsys\b|\ball_users\b|\ball_tables\b|\bdbms_pipe\b|\bdbms_lock\b', p):
        db = 'oracle'
    elif re.search(r'\bpg_sleep\b|\bgenerate_series\b|\bpg_database\b|\bstring_agg\b', p):
        db = 'postgresql'
    elif re.search(r'\bextractvalue\b|\bupdatexml\b|\bbenchmark\b|\belt\s*\(|\brlike\b|\binformation_schema\b|\bload_file\b', p):
        db = 'mysql'
    elif re.search(r'\bwaitfor\s+delay\b|\bxp_cmdshell\b|\bxp_dirtree\b|\bsysobjects\b|\bsysdatabases\b', p):
        db = 'mssql'
    elif re.search(r'\brandomblob\b|\bsqlite_master\b', p):
        db = 'sqlite'
    elif re.search(r'\brdb\$', p):
        db = 'firebird'
    elif re.search(r'\bsysibm\.', p):
        db = 'db2'
    elif re.search(r'\bdomain\.(domains|columns|tables)\b', p):
        db = 'firebird'

    if not tokens:
        # Maybe benign or trivial
        # If payload looks like simple SQL without injection markers
        return ('benign', db or 'generic', 0.6,
                f"No SQLi signal tokens detected in payload (length={len(payload)} chars); treated as benign baseline",
                [])

    # Pick lowest-priority token's type as primary
    tokens.sort(key=lambda t: t[0])
    # Special override: if heavy_query and boolean_blind both present and payload has huge repeat()/regexp -> heavy_query wins
    types_present = {t[1] for t in tokens}
    if 'heavy_query' in types_present and 'boolean_blind' in types_present:
        # Choose heavy_query when DoS markers present (huge int)
        if re.search(r'\b\d{7,}\b', p) or 'crypt_key' in p or 'regexp_substring' in p or 'generate_series' in p or re.search(r'all_users.*all_users.*all_users', p):
            best = next(t for t in tokens if t[1] == 'heavy_query')
        else:
            best = tokens[0]
    else:
        best = tokens[0]

    sqli_type = best[1]
    # DB: prefer inferred from payload tokens
    db_engine = db or best[2]
    if db_engine is None:
        db_engine = 'generic'

    # Build reasoning: combine top 1-2 matches plus DB rationale
    reasons = []
    seen_types = set()
    for t in tokens:
        if t[1] not in seen_types:
            reasons.append(f"'{t[3]}' -> {t[1]} (P{t[0]}): {t[4]}")
            seen_types.add(t[1])
        if len(reasons) >= 2:
            break
    reasoning = ' | '.join(reasons) + f" | db_engine={db_engine}"

    # Confidence based on signal strength
    if len(tokens) >= 2 and best[0] <= 5:
        conf = 0.9
    elif best[0] <= 5:
        conf = 0.85
    else:
        conf = 0.8

    # Lower confidence if conflicts with both a_type and c_type
    if a_type and c_type and sqli_type != a_type and sqli_type != c_type:
        conf = max(0.7, conf - 0.1)

    return (sqli_type, db_engine, conf, reasoning, tokens)


out_rows = []
type_counts = {}
low_conf = 0
short_reason = 0

for _, r in df.iterrows():
    rid = r['id'] if 'id' in r and pd.notna(r['id']) else _
    payload = r['payload_inner'] if pd.notna(r['payload_inner']) else r.get('payload_norm', '')
    a_type = r.get('a_type', '')
    a_db = r.get('a_db', '')
    c_type = r.get('c_type', '')
    c_db = r.get('c_db', '')

    sqli_type, db_engine, conf, reasoning, _toks = detect(payload, a_type, a_db, c_type, c_db)

    # Pad reasoning if short
    if len(reasoning) < 50:
        reasoning = reasoning + f" | payload starts: {repr(str(payload)[:40])}"
    if len(reasoning) < 50:
        reasoning = "UNCERTAIN: " + reasoning
        conf = 0.5

    # sources_agree
    if conf < 0.5:
        sa = 0
    else:
        match_a = (sqli_type == a_type)
        match_c = (sqli_type == c_type)
        if match_a and match_c:
            sa = 3
        elif match_a or match_c:
            sa = 2
        else:
            sa = 1

    out_rows.append({
        'id': int(rid),
        'payload_inner': payload,
        'sqli_type': sqli_type,
        'db_engine': db_engine,
        'confidence': round(conf, 2),
        'reasoning': reasoning,
        'sources_agree': sa,
    })

    type_counts[sqli_type] = type_counts.get(sqli_type, 0) + 1
    if conf < 0.7:
        low_conf += 1
    if len(reasoning) < 50:
        short_reason += 1

# Write CSV with exact column order
with open(OUT, 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=['id','payload_inner','sqli_type','db_engine','confidence','reasoning','sources_agree'], quoting=csv.QUOTE_MINIMAL)
    w.writeheader()
    for row in out_rows:
        w.writerow(row)

print(f'Total labeled: {len(out_rows)}')
print('Top types:', sorted(type_counts.items(), key=lambda x: -x[1])[:5])
print(f'confidence<0.7: {low_conf}')
print(f'reasoning<50chars: {short_reason}')
