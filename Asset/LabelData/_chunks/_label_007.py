"""Label chunk_007.csv per sqli-data-curator taxonomy.

Priority table (lower = stronger):
  1 benign, 2 auth_bypass, 3 boolean_blind, 4 error_based, 4 heavy_query,
  5 time_blind, 6 out_of_band, 7 union_based, 8 stacked_queries, 9 polyglot
"""
import csv
import re
import sys

IN = r"C:/Users/Admin/Documents/GAN_SQLi/Asset/LabelData/_chunks/chunk_007.csv"
OUT = r"C:/Users/Admin/Documents/GAN_SQLi/Asset/LabelData/_chunks/chunk_007_labeled.csv"

# --- Pattern catalog ---------------------------------------------------------
# Each tuple: (sqli_type, priority, db_hint, regex, token_label)
P = [
    # auth_bypass (P2)
    ("auth_bypass", 2, "generic",
     re.compile(r"(?i)('|\")\s*or\s+('|\"?)?1('|\"?)?\s*=\s*('|\"?)?1"), "OR 1=1 auth pattern"),
    ("auth_bypass", 2, "generic",
     re.compile(r"(?i)admin'\s*--"), "admin'-- auth bypass"),
    ("auth_bypass", 2, "generic",
     re.compile(r"(?i)'\s*or\s+'1'\s*=\s*'1"), "' OR '1'='1 classic auth bypass"),

    # error_based (P4) — DB-specific funcs
    ("error_based", 4, "oracle",
     re.compile(r"(?i)\bxmltype\s*\("), "xmltype("),
    ("error_based", 4, "oracle",
     re.compile(r"(?i)\butl_inaddr\.get_host_address"), "utl_inaddr.get_host_address"),
    ("error_based", 4, "oracle",
     re.compile(r"(?i)\bctxsys\."), "ctxsys.drithsx.sn"),
    ("error_based", 4, "mysql",
     re.compile(r"(?i)\bextractvalue\s*\("), "extractvalue("),
    ("error_based", 4, "mysql",
     re.compile(r"(?i)\bupdatexml\s*\("), "updatexml("),
    ("error_based", 4, "mysql",
     re.compile(r"(?i)\bexp\s*\(\s*~"), "exp(~N) overflow"),
    ("error_based", 4, "generic",
     re.compile(r"(?i)\bcast\s*\([^)]*\bas\s+int\b"), "cast(... as int)"),
    ("error_based", 4, "mysql",
     re.compile(r"(?i)\bprocedure\s+analyse\s*\("), "procedure analyse()"),
    ("error_based", 4, "mysql",
     re.compile(r"(?i)\bgeometrycollection\s*\("), "geometrycollection()"),
    ("error_based", 4, "mysql",
     re.compile(r"(?i)\bmultipoint\s*\("), "multipoint()"),
    ("error_based", 4, "mysql",
     re.compile(r"(?i)\bpolygon\s*\("), "polygon()"),
    ("error_based", 4, "mysql",
     re.compile(r"(?i)\bmultipolygon\s*\("), "multipolygon()"),
    ("error_based", 4, "mysql",
     re.compile(r"(?i)\blinestring\s*\("), "linestring()"),
    ("error_based", 4, "mysql",
     re.compile(r"(?i)\bmultilinestring\s*\("), "multilinestring()"),

    # time_blind (P5)
    ("time_blind", 5, "postgresql",
     re.compile(r"(?i)\bpg_sleep\s*\("), "pg_sleep("),
    ("time_blind", 5, "mysql",
     re.compile(r"(?i)\bsleep\s*\(\s*\d"), "sleep(N)"),
    ("time_blind", 5, "mssql",
     re.compile(r"(?i)\bwaitfor\s+delay\b"), "WAITFOR DELAY"),
    ("time_blind", 5, "mysql",
     re.compile(r"(?i)\bbenchmark\s*\(\s*\d"), "benchmark(N,...)"),
    ("time_blind", 5, "oracle",
     re.compile(r"(?i)\bdbms_pipe\.receive_message"), "dbms_pipe.receive_message"),
    ("time_blind", 5, "oracle",
     re.compile(r"(?i)\bdbms_lock\.sleep"), "dbms_lock.sleep"),
    ("time_blind", 5, "sqlite",
     re.compile(r"(?i)\brandomblob\s*\("), "randomblob("),
    ("time_blind", 5, "mysql",
     re.compile(r"(?i)\bif\s*\(\s*[^,]+,\s*sleep\s*\("), "IF(...,sleep,...)"),

    # out_of_band (P6)
    ("out_of_band", 6, "mysql",
     re.compile(r"(?i)\bload_file\s*\("), "load_file("),
    ("out_of_band", 6, "oracle",
     re.compile(r"(?i)\butl_http\.request"), "utl_http.request"),
    ("out_of_band", 6, "mssql",
     re.compile(r"(?i)\bxp_dirtree\b"), "xp_dirtree"),
    ("out_of_band", 6, "mssql",
     re.compile(r"(?i)\bxp_fileexist\b"), "xp_fileexist"),
    ("out_of_band", 6, "oracle",
     re.compile(r"(?i)\bdbms_ldap\."), "dbms_ldap"),

    # union_based (P7)
    ("union_based", 7, "generic",
     re.compile(r"(?i)\bunion\s+(all\s+)?select\b"), "UNION SELECT"),

    # stacked_queries (P8)
    ("stacked_queries", 8, "mssql",
     re.compile(r"(?i)\bxp_cmdshell\b"), "xp_cmdshell"),
    ("stacked_queries", 8, "generic",
     re.compile(r";\s*(insert|update|delete|drop|create|alter|exec)\b", re.I), "; INSERT/UPDATE/DROP"),

    # heavy_query (P4)
    ("heavy_query", 4, "postgresql",
     re.compile(r"(?i)\bgenerate_series\s*\("), "generate_series()"),
    ("heavy_query", 4, "oracle",
     re.compile(r"(?i)from\s+all_users\s+t1\s*,\s*all_users\s+t2"), "all_users t1,t2 cross-join"),
    ("heavy_query", 4, "oracle",
     re.compile(r"(?i)from\s+all_tables\s+t1\s*,\s*all_tables\s+t2"), "all_tables cross-join"),
    ("heavy_query", 4, "generic",
     re.compile(r"(?i)from\s+\w+\s+t1\s*,\s*\w+\s+t2\s*,\s*\w+\s+t3\s*,\s*\w+\s+t4\s*,\s*\w+\s+t5"), "5x cartesian join"),
    ("heavy_query", 4, "firebird",
     re.compile(r"(?i)from\s+rdb\$\w+\s+(as\s+)?t1\s*,\s*rdb\$"), "rdb$ cross-join (firebird)"),
    ("heavy_query", 4, "postgresql",
     re.compile(r"(?i)from\s+domain\.\w+\s+(as\s+)?t1\s*,\s*domain\."), "domain.* cross-join (postgresql)"),
    ("heavy_query", 4, "mssql",
     re.compile(r"(?i)from\s+sysusers\s+(as\s+)?\w*\s*,\s*sysusers"), "sysusers cross-join (mssql)"),
    ("heavy_query", 4, "generic",
     re.compile(r"(?i)\brepeat\s*\(\s*[^)]+,\s*\d{6,}\s*\)"), "repeat(...,LARGE_N) DoS"),
    ("heavy_query", 4, "mysql",
     re.compile(r"(?i)\bcrypt_key\s*\("), "crypt_key()"),

    # boolean_blind extras (P3)
    ("boolean_blind", 3, "generic",
     re.compile(r"(?i)\biif\s*\(\s*\d+\s*=\s*\d+"), "iif(N=N,...)"),
    ("boolean_blind", 3, "mysql",
     re.compile(r"(?i)\bin\s+boolean\s+mode\b"), "IN BOOLEAN MODE (mysql fulltext)"),
    ("boolean_blind", 3, "generic",
     re.compile(r"(?i)\bcase\s+when\s+\d+\s*=\s*\d+\s+then\b"), "CASE WHEN N=N THEN"),
    ("boolean_blind", 3, "generic",
     re.compile(r"(?i)\border\s+by\s+\d+\s*(--|#)"), "ORDER BY N -- probe"),

    # boolean_blind (P3) — RLIKE / ELT / AND N=N with extra context
    ("boolean_blind", 3, "mysql",
     re.compile(r"(?i)\brlike\s+\("), "RLIKE ("),
    ("boolean_blind", 3, "mysql",
     re.compile(r"(?i)\belt\s*\(\s*\d+\s*=\s*\d+"), "ELT(N=N,...)"),
    ("boolean_blind", 3, "mysql",
     re.compile(r"(?i)\bmake_set\s*\("), "make_set()"),
]

# DB hint regex — extra signals
DB_PATTERNS = [
    ("oracle", re.compile(r"(?i)\b(xmltype|utl_inaddr|dbms_pipe|dbms_lock|ctxsys|all_users|all_tables|dual|rownum|utl_http|dbms_ldap)\b")),
    ("mysql", re.compile(r"(?i)\b(extractvalue|updatexml|sleep|benchmark|elt|rlike|information_schema|procedure\s+analyse|load_file|geometrycollection|multipoint|polygon|linestring)\b")),
    ("postgresql", re.compile(r"(?i)\b(pg_sleep|pg_database|generate_series|string_agg|cast\s*\([^)]*as\s+int)\b")),
    ("mssql", re.compile(r"(?i)\b(xp_cmdshell|waitfor\s+delay|sysobjects|sysdatabases|xp_dirtree)\b")),
    ("sqlite", re.compile(r"(?i)\b(randomblob|sqlite_master)\b")),
    ("firebird", re.compile(r"(?i)\b(rdb\$fields|rdb\$types|gen_id)\b")),
    ("db2", re.compile(r"(?i)\b(sysibm\.systables)\b")),
]

# Boolean-blind weak signal (AND N=N / OR N=N near tail) — fallback only
RE_BOOL_NUM = re.compile(r"(?i)\b(and|or|where|when|then)\s+\(?\s*\d+\s*=\s*\d+")
RE_BOOL_STR = re.compile(r"(?i)\b(and|or|where|when)\s+['\"][^'\"]+['\"]\s*=\s*['\"][^'\"]+['\"]")
RE_COMMENT_TAIL = re.compile(r"(--|#|/\*)")
RE_PAREN_INJECT = re.compile(r"^[\s'\")0-9]*[)']")  # leading injection breakout
RE_QUOTE_BREAK = re.compile(r"^[-]?\d*\s*['\"]")  # 1' or 1" or -1' or just '
RE_CASE_WHEN = re.compile(r"(?i)\bcase\s+when\b")
RE_REGEXP = re.compile(r"(?i)\bregexp(_substring|_substr|_replace)?\b")
RE_ASCII = re.compile(r"(?i)\bascii\s*\(")
RE_REPEAT = re.compile(r"(?i)\brepeat\s*\(")
RE_SUBSELECT_COUNT = re.compile(r"(?i)select\s+count\s*\(\s*\*\s*\)")
RE_CROSS_JOIN = re.compile(r"(?i)\bfrom\s+\w+\s+\w*\s*,\s*\w+\s+\w*\s*,\s*\w+")


def detect_db(payload, default="generic"):
    for db, pat in DB_PATTERNS:
        if pat.search(payload):
            return db
    return default


def label(payload):
    """Return (sqli_type, db_engine, confidence, reasoning_tokens)."""
    if not payload or not payload.strip():
        return ("benign", "generic", 0.6, "empty/whitespace payload — no SQL injection signal present")

    matches = []  # list of (priority, sqli_type, db_hint, token_label)
    for sqli_type, pri, db_hint, regex, token in P:
        m = regex.search(payload)
        if m:
            matches.append((pri, sqli_type, db_hint, token, m.group(0)))

    db_engine = detect_db(payload)

    if matches:
        # lowest priority wins
        matches.sort(key=lambda x: x[0])
        best_pri = matches[0][0]
        top = [m for m in matches if m[0] == best_pri]
        sqli_type = top[0][1]
        # use db hint from rule if it's specific, else detected db
        rule_db = top[0][2]
        if rule_db != "generic":
            db_engine = rule_db
        # build reasoning with quoted tokens
        token_strs = [f"'{m[4]}' ({m[3]})" for m in top[:3]]
        reasoning = f"Token match {', '.join(token_strs)} → {sqli_type} (P{best_pri}); db={db_engine}"
        # confidence
        if len(matches) >= 2 and matches[0][0] != matches[1][0]:
            conf = 0.9  # clear winner over weaker match
        elif len(top) >= 2:
            conf = 0.85  # multiple confirming tokens at same priority
        else:
            conf = 0.85
        # Boost for very specific funcs
        if any(tk in top[0][3] for tk in ["xmltype", "pg_sleep", "extractvalue", "updatexml",
                                           "WAITFOR", "dbms_pipe", "xp_cmdshell", "load_file",
                                           "utl_inaddr", "randomblob", "benchmark", "procedure analyse"]):
            conf = 0.95
        return (sqli_type, db_engine, conf, reasoning)

    # No strong signal — check boolean_blind weak signals
    bn = RE_BOOL_NUM.search(payload)
    bs = RE_BOOL_STR.search(payload)
    has_comment = bool(RE_COMMENT_TAIL.search(payload))
    has_break = bool(RE_QUOTE_BREAK.search(payload)) or payload.lstrip().startswith(("'", '"', "(", ")"))
    has_case_when = bool(RE_CASE_WHEN.search(payload))
    has_regexp = bool(RE_REGEXP.search(payload))
    has_ascii = bool(RE_ASCII.search(payload))
    has_subcount = bool(RE_SUBSELECT_COUNT.search(payload))
    has_cross_join = bool(RE_CROSS_JOIN.search(payload))

    # Heavy-query: cross join + subselect-count
    if has_subcount and has_cross_join:
        m = RE_CROSS_JOIN.search(payload)
        reasoning = (f"Cross-join pattern '{m.group(0)[:50]}' + count(*) subselect — "
                     f"heavy_query DoS-style payload (P4); db={db_engine}")
        return ("heavy_query", db_engine, 0.9, reasoning)

    # Strong boolean_blind: CASE WHEN, ASCII, REGEXP_SUBSTR — common blind tricks
    if has_case_when and (has_ascii or has_regexp or has_subcount):
        reasoning = (f"CASE WHEN construct + "
                     f"{'ASCII()' if has_ascii else 'REGEXP' if has_regexp else 'subselect count'} "
                     f"— inferential boolean_blind (P3); db={db_engine}")
        return ("boolean_blind", db_engine, 0.9, reasoning)

    if has_case_when and (bn or bs):
        token = bn.group(0) if bn else bs.group(0)
        reasoning = (f"CASE WHEN + tautology '{token}' — boolean_blind inferential (P3); db={db_engine}")
        return ("boolean_blind", db_engine, 0.9, reasoning)

    if (bn or bs) and (has_comment or has_break):
        token = bn.group(0) if bn else bs.group(0)
        reasoning = (f"Boolean tautology '{token}' + injection break "
                     f"({'comment tail' if has_comment else 'quote/paren break'}) → boolean_blind (P3); db={db_engine}")
        return ("boolean_blind", db_engine, 0.85, reasoning)

    if (bn or bs):
        token = bn.group(0) if bn else bs.group(0)
        reasoning = (f"Boolean equality '{token}' tautology pattern — boolean_blind (P3); db={db_engine}")
        return ("boolean_blind", db_engine, 0.75, reasoning)

    # Possibly benign — check if payload looks like plain text/SQL fragment
    if has_break and has_comment:
        reasoning = (f"Quote/paren break + comment '--/#' detected but no tautology/function — "
                     f"likely probe payload; boolean_blind low-conf (P3); db={db_engine}")
        return ("boolean_blind", db_engine, 0.6, reasoning)

    if has_break or has_comment:
        reasoning = (f"Only {'quote/paren break' if has_break else 'comment tail'} detected, no tautology/function — "
                     f"likely simple probe; boolean_blind low-conf (P3); db={db_engine}")
        return ("boolean_blind", db_engine, 0.55, reasoning)

    return ("benign", "generic", 0.6,
            f"No SQL injection signal (no tautology, no function, no break) — payload appears benign; db=generic")


def main():
    with open(IN, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    out_rows = []
    for i, row in enumerate(rows):
        rid = row.get("id") or str(i)
        payload = row.get("payload_inner") or row.get("payload_norm") or ""
        a_type = (row.get("a_type") or "").strip().lower()
        c_type = (row.get("c_type") or "").strip().lower()

        sqli_type, db_engine, conf, reasoning = label(payload)

        # sources_agree
        if conf < 0.5:
            sources_agree = 0
        else:
            m_a = (sqli_type == a_type)
            m_c = (sqli_type == c_type)
            if m_a and m_c and a_type == c_type:
                sources_agree = 3
            elif m_a or m_c:
                sources_agree = 2
            else:
                sources_agree = 1

        # Ensure reasoning >= 50 chars
        if len(reasoning) < 50:
            reasoning = reasoning + f" — payload snippet: '{payload[:40]}'"

        # Clamp confidence
        if conf < 0.5:
            conf = 0.5
        if conf > 1.0:
            conf = 1.0

        out_rows.append({
            "id": rid,
            "payload_inner": payload,
            "sqli_type": sqli_type,
            "db_engine": db_engine,
            "confidence": round(conf, 2),
            "reasoning": reasoning,
            "sources_agree": sources_agree,
        })

    with open(OUT, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "id", "payload_inner", "sqli_type", "db_engine",
            "confidence", "reasoning", "sources_agree"
        ])
        writer.writeheader()
        writer.writerows(out_rows)

    # Report
    from collections import Counter
    types = Counter(r["sqli_type"] for r in out_rows)
    low_conf = sum(1 for r in out_rows if r["confidence"] < 0.7)
    short_reason = sum(1 for r in out_rows if len(r["reasoning"]) < 50)
    print(f"Labeled rows: {len(out_rows)}")
    print(f"Top 5 types: {types.most_common(5)}")
    print(f"Rows confidence<0.7: {low_conf}")
    print(f"Rows reasoning<50chars: {short_reason}")
    print(f"sources_agree dist: {Counter(r['sources_agree'] for r in out_rows)}")


if __name__ == "__main__":
    main()
