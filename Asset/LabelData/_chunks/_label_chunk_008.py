# -*- coding: utf-8 -*-
"""Label chunk_008.csv -> chunk_008_labeled.csv with 7 columns."""
import pandas as pd
import re
import sys
import io

# Force stdout UTF-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

INPUT = r'C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks\chunk_008.csv'
OUTPUT = r'C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks\chunk_008_labeled.csv'

VALID_TYPES = {'benign', 'error_based', 'boolean_blind', 'time_blind', 'union_based',
               'auth_bypass', 'heavy_query', 'out_of_band', 'stacked_queries', 'polyglot'}
VALID_DBS = {'oracle', 'mysql', 'postgresql', 'mssql', 'firebird', 'sqlite', 'db2', 'generic'}

# Priority table (lower = stronger)
PRIORITY = {
    'benign': 1, 'auth_bypass': 2, 'boolean_blind': 3, 'error_based': 4,
    'heavy_query': 4, 'time_blind': 5, 'out_of_band': 6, 'union_based': 7,
    'stacked_queries': 8, 'polyglot': 9
}


def detect_db(p):
    """Detect DB engine and return (db, evidence_tokens)."""
    pl = p.lower()
    # Oracle
    oracle_tokens = []
    for t in ['xmltype', 'utl_inaddr', 'utl_http', 'dbms_pipe', 'dbms_lock',
              'ctxsys', 'all_tables', 'rdb$']:
        # rdb$ -> firebird, skip here
        if t == 'rdb$':
            continue
        if t in pl:
            oracle_tokens.append(t)
    if re.search(r'\bdual\b', pl):
        oracle_tokens.append('dual')
    if oracle_tokens:
        return 'oracle', oracle_tokens

    # Firebird
    fb_tokens = []
    for t in ['rdb$fields', 'rdb$types', 'rdb$collations', 'rdb$functions',
              'rdb$relations', 'rdb$', 'gen_id']:
        if t in pl:
            fb_tokens.append(t)
    if fb_tokens:
        return 'firebird', fb_tokens

    # SQLite
    sl_tokens = []
    for t in ['randomblob', 'sqlite_master', "like('a','a')", 'sqlite_version']:
        if t in pl:
            sl_tokens.append(t)
    if sl_tokens:
        return 'sqlite', sl_tokens

    # MSSQL
    ms_tokens = []
    for t in ['xp_cmdshell', 'xp_dirtree', 'sysobjects', 'sysdatabases',
              'master..', 'waitfor delay', 'waitfor']:
        if t in pl:
            ms_tokens.append(t)
    if ms_tokens:
        return 'mssql', ms_tokens

    # PostgreSQL
    pg_tokens = []
    for t in ['pg_sleep', 'pg_database', 'string_agg', 'generate_series',
              'pg_user', 'pg_catalog', 'pg_class']:
        if t in pl:
            pg_tokens.append(t)
    if re.search(r'cast\s*\([^)]*\bas\s+int', pl):
        pg_tokens.append('cast as int')
    if pg_tokens:
        return 'postgresql', pg_tokens

    # MySQL
    my_tokens = []
    for t in ['extractvalue', 'updatexml', 'benchmark', 'information_schema',
              'mysql.user', 'rlike', 'elt(', 'sleep(']:
        if t in pl:
            my_tokens.append(t.rstrip('('))
    if my_tokens:
        return 'mysql', my_tokens

    # DB2
    if 'sysibm.systables' in pl or 'current schema' in pl:
        return 'db2', ['sysibm']

    return 'generic', []


def detect_type(p, db, db_tokens):
    """Return (type, evidence_tokens, priority)."""
    pl = p.lower()
    found = []  # list of (type, token, priority)

    # polyglot — multi-context (xss + sqli)
    if re.search(r'<script|javascript:|onerror\s*=', pl) and \
       re.search(r'(union\s+select|sleep|or\s+\d+\s*=\s*\d+|--)', pl):
        found.append(('polyglot', 'xss+sqli mix', 9))

    # stacked_queries
    if re.search(r';\s*(insert|update|drop|exec|delete|create|alter)\b', pl):
        m = re.search(r';\s*(insert|update|drop|exec|delete|create|alter)\b', pl)
        found.append(('stacked_queries', ';' + m.group(1), 8))
    if 'xp_cmdshell' in pl:
        found.append(('stacked_queries', 'xp_cmdshell', 8))

    # union_based
    if re.search(r'\bunion\s+(all\s+)?select\b', pl):
        m = re.search(r'\bunion\s+(all\s+)?select\b', pl)
        found.append(('union_based', m.group(0), 7))

    # out_of_band
    for t in ['load_file', 'utl_http', 'xp_dirtree', 'utl_inaddr', 'dnslookup',
              'into outfile', 'into dumpfile']:
        if t in pl:
            found.append(('out_of_band', t, 6))
            break

    # time_blind
    time_tokens = []
    for t in ['pg_sleep', 'waitfor delay', 'benchmark(', 'dbms_pipe.receive_message',
              'dbms_lock.sleep', 'randomblob']:
        if t in pl:
            time_tokens.append(t.rstrip('('))
    if re.search(r'\bsleep\s*\(', pl):
        time_tokens.append('sleep(')
    if time_tokens:
        found.append(('time_blind', time_tokens[0], 5))

    # heavy_query
    if 'generate_series' in pl and re.search(r'generate_series\s*\(\s*\d+\s*,\s*\d{5,}', pl):
        found.append(('heavy_query', 'generate_series(large)', 4))
    elif re.search(r'count\s*\(\s*\*\s*\)\s+from\s+\w+\s*,\s*\w+\s*,\s*\w+\s*,\s*\w+', pl):
        # cartesian heavy join (4+ tables)
        found.append(('heavy_query', 'cartesian count(*) from N tables', 4))

    # error_based
    err_tokens = []
    for t in ['xmltype', 'extractvalue', 'updatexml', 'ctxsys.drithsx',
              'utl_inaddr.get_host_address']:
        if t in pl:
            err_tokens.append(t)
    if re.search(r'\bexp\s*\(\s*~', pl):
        err_tokens.append('exp(~)')
    if re.search(r'cast\s*\([^)]*\bas\s+int', pl) and not re.search(r'union', pl):
        # cast error is weaker but common in pg error
        pass  # do not auto-flag — likely structural
    if err_tokens:
        found.append(('error_based', err_tokens[0], 4))

    # boolean_blind
    bool_tokens = []
    if re.search(r'\b(and|or)\s+\d+\s*=\s*\d+', pl):
        m = re.search(r'\b(and|or)\s+\d+\s*=\s*\d+', pl)
        bool_tokens.append(m.group(0))
    if re.search(r'\b(and|or)\s+\(?\s*\d+\s*[<>]=?\s*\d+', pl):
        m = re.search(r'\b(and|or)\s+\(?\s*\d+\s*[<>]=?\s*\d+', pl)
        bool_tokens.append(m.group(0))
    if re.search(r"\brlike\b", pl) or re.search(r"\belt\s*\(", pl):
        bool_tokens.append('rlike/elt')
    if re.search(r"\biif\s*\(\s*\d+\s*=\s*\d+", pl):
        bool_tokens.append('iif(N=N,...)')
    if re.search(r"\bif\s*\(\s*\w+\s*=", pl):
        bool_tokens.append('if(...)')
    if re.search(r"\bcase\s+when\b", pl):
        bool_tokens.append('case when')
    if bool_tokens:
        found.append(('boolean_blind', bool_tokens[0], 3))

    # auth_bypass — only if specifically login style: admin'-- or '1'='1
    if re.search(r"(admin|root)['\"]?\s*(--|#)", pl) or \
       re.search(r"['\"]?1['\"]?\s*=\s*['\"]?1['\"]?\s*(--|#|/\*)", pl) or \
       re.search(r"\bor\s+['\"]?1['\"]?\s*=\s*['\"]?1['\"]?($|\s|--)", pl):
        # also requires context of being a login bypass — usually short payloads
        if len(p) < 80 or 'union' not in pl:
            found.append(('auth_bypass', "admin'-- or '1'='1", 2))

    if not found:
        # benign-ish: still might be valid SQL test (NULLs, etc.)
        # Check if there are ANY attack signs
        if re.search(r'(union|sleep|waitfor|benchmark|xmltype|extractvalue|updatexml|'
                     r'pg_sleep|randomblob|;\s*drop|;\s*insert|--|#|/\*|or\s+\d|and\s+\d|'
                     r'concat|cast|chr\s*\()', pl):
            # likely something — fall to boolean default
            return 'boolean_blind', ['weak signal'], 3
        return 'benign', [], 1

    # Pick lowest priority
    found.sort(key=lambda x: x[2])
    best = found[0]
    return best[0], [best[1]], best[2]


def label_row(payload, a_type, a_db, c_type, c_db):
    """Return (sqli_type, db_engine, confidence, reasoning, sources_agree)."""
    p = str(payload) if payload is not None else ''
    if not p or p.strip() == '' or p.lower() == 'nan':
        return ('benign', 'generic', 0.5,
                "UNCERTAIN: empty/null payload, defaulting to benign with low confidence",
                0)

    db, db_evidence = detect_db(p)
    sqli_type, type_evidence, prio = detect_type(p, db, db_evidence)

    # Build reasoning >= 50 chars, with quoted tokens
    tok_quotes = []
    for t in type_evidence:
        if t:
            tok_quotes.append(f"'{t}'")
    for t in db_evidence[:2]:
        tok_quotes.append(f"'{t}'")

    if sqli_type == 'benign':
        reasoning = (f"No SQLi signal in payload (no union/sleep/error funcs/comments); "
                     f"payload normalized: '{p[:60]}'; "
                     f"db_evidence={db_evidence or 'none'}; classified benign/generic")
    else:
        reasoning = (f"Token match: {','.join(tok_quotes) if tok_quotes else 'pattern'} -> "
                     f"{sqli_type} (priority P{prio}); db_engine={db} from evidence "
                     f"{db_evidence or 'generic'}; payload snippet: '{p[:50]}'")

    # Pad reasoning if short
    if len(reasoning) < 50:
        reasoning = reasoning + f"; full classification: type={sqli_type}, db={db}"

    # Confidence
    a_match = (str(a_type).lower() == sqli_type)
    c_match = (str(c_type).lower() == sqli_type)
    if a_match and c_match:
        confidence = 0.95
        sources_agree = 3
    elif a_match or c_match:
        confidence = 0.80
        sources_agree = 2
    else:
        confidence = 0.65
        sources_agree = 1

    # Bump for very strong evidence
    if sqli_type != 'benign' and len(type_evidence) > 0 and type_evidence[0]:
        if any(t in str(type_evidence[0]) for t in [
            'xmltype', 'extractvalue', 'updatexml', 'pg_sleep',
            'waitfor delay', 'randomblob', 'xp_cmdshell',
            'utl_inaddr', 'union select', 'union all select']):
            if confidence < 0.90:
                confidence = min(0.95, confidence + 0.10)

    # If benign and both agree benign
    if sqli_type == 'benign' and a_match and c_match:
        confidence = 0.90

    return (sqli_type, db, round(confidence, 2), reasoning, sources_agree)


def main():
    df = pd.read_csv(INPUT)
    print(f"Loaded {len(df)} rows from {INPUT}", flush=True)

    rows = []
    for idx, r in df.iterrows():
        rid = r['id'] if 'id' in df.columns and pd.notna(r.get('id')) else idx
        pi = r.get('payload_inner', '')
        if pd.isna(pi):
            pi = r.get('payload_norm', '')
        a_t = r.get('a_type', '')
        a_d = r.get('a_db', '')
        c_t = r.get('c_type', '')
        c_d = r.get('c_db', '')
        sqli_type, db_engine, confidence, reasoning, sa = label_row(
            pi, a_t, a_d, c_t, c_d)
        # Validate
        if sqli_type not in VALID_TYPES:
            sqli_type = 'benign'
        if db_engine not in VALID_DBS:
            db_engine = 'generic'
        if confidence < 0.5:
            confidence = 0.5
            sa = 0
        rows.append({
            'id': rid,
            'payload_inner': pi,
            'sqli_type': sqli_type,
            'db_engine': db_engine,
            'confidence': confidence,
            'reasoning': reasoning,
            'sources_agree': sa
        })

    out = pd.DataFrame(rows, columns=['id', 'payload_inner', 'sqli_type', 'db_engine',
                                       'confidence', 'reasoning', 'sources_agree'])
    out.to_csv(OUTPUT, index=False, encoding='utf-8')
    print(f"Wrote {len(out)} rows -> {OUTPUT}", flush=True)

    # Report
    print("\n=== REPORT ===", flush=True)
    print(f"Rows labeled: {len(out)}", flush=True)
    print("\nTop 5 type distribution:", flush=True)
    print(out['sqli_type'].value_counts().head(5).to_string(), flush=True)
    print(f"\nRows with confidence<0.7: {(out['confidence']<0.7).sum()}", flush=True)
    short = out['reasoning'].astype(str).str.len() < 50
    print(f"Rows with reasoning<50 chars: {short.sum()}", flush=True)
    print(f"\nDB distribution:", flush=True)
    print(out['db_engine'].value_counts().to_string(), flush=True)
    print(f"\nSources_agree distribution:", flush=True)
    print(out['sources_agree'].value_counts().to_string(), flush=True)


if __name__ == '__main__':
    main()
