"""Label chunk_001.csv with sqli_type, db_engine, confidence, reasoning, sources_agree.

Strategy:
- Use payload text as ground truth; reference a_type/c_type for confidence.
- Priority table (lower wins): auth_bypass=2, boolean_blind=3, error_based=4,
  heavy_query=4, time_blind=5, out_of_band=6, union_based=7, stacked_queries=8, polyglot=9.
- benign only if no attack tokens; reasoning must quote tokens and >= 50 chars.
"""
import pandas as pd
import re
import csv

IN_PATH = r"C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks\chunk_001.csv"
OUT_PATH = r"C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks\chunk_001_labeled.csv"

df = pd.read_csv(IN_PATH)


def detect_db(p: str):
    """Detect DB engine from lowercased payload."""
    sigs = []
    if re.search(r"\bxmltype\b", p):
        return "oracle", "xmltype"
    if re.search(r"\bdbms_pipe\b|\bdbms_lock\b|\bdbms_utility\b|\butl_inaddr\b|\butl_http\b|\bctxsys\b", p):
        return "oracle", "dbms_/utl_/ctxsys"
    if re.search(r"\bpg_sleep\b|\bpg_database\b|\bstring_agg\b|\bgenerate_series\b", p):
        return "postgresql", "pg_sleep/generate_series"
    if re.search(r"\bextractvalue\b|\bupdatexml\b", p):
        return "mysql", "extractvalue/updatexml"
    if re.search(r"\binformation_schema\b|\bmysql\.user\b", p):
        return "mysql", "information_schema/mysql.user"
    if re.search(r"\bbenchmark\s*\(|\belt\s*\(|\brlike\b|\bunhex\b", p):
        return "mysql", "benchmark/elt/rlike"
    if re.search(r"\bsleep\s*\(", p):
        return "mysql", "sleep()"
    if re.search(r"\bwaitfor\s+delay\b|\bxp_cmdshell\b|\bxp_dirtree\b|\bsysobjects\b|\bsyscolumns\b|\bsysdatabases\b|\bmaster\.\.", p):
        return "mssql", "waitfor/xp_/sysobjects/syscolumns"
    if re.search(r"\brandomblob\b|\bsqlite_master\b", p):
        return "sqlite", "randomblob/sqlite_master"
    if re.search(r"\brdb\$", p):
        return "firebird", "rdb$"
    if re.search(r"\bsysibm\.systables\b|\bcurrent\s+schema\b", p):
        return "db2", "sysibm.systables"
    if re.search(r"\bdual\b", p):
        return "oracle", "dual"
    return "generic", ""


def detect(payload: str, a_type: str, c_type: str):
    """Return (sqli_type, db_engine, confidence, reasoning)."""
    if not isinstance(payload, str):
        payload = ""
    p = payload.lower()
    db, db_sig = detect_db(p)

    candidates = []  # (priority, type, signal_token)

    # --- error_based (priority 4) ---
    if "xmltype" in p:
        candidates.append((4, "error_based", "xmltype()"))
    if "extractvalue" in p:
        candidates.append((4, "error_based", "extractvalue()"))
    if "updatexml" in p:
        candidates.append((4, "error_based", "updatexml()"))
    if "ctxsys" in p:
        candidates.append((4, "error_based", "ctxsys"))
    if re.search(r"\butl_inaddr\b", p):
        candidates.append((4, "error_based", "utl_inaddr"))
    if re.search(r"dbms_utility\.sqlid_to_sqlhash", p):
        candidates.append((4, "error_based", "dbms_utility.sqlid_to_sqlhash"))
    if re.search(r"\bexp\s*\(\s*~", p):
        candidates.append((4, "error_based", "exp(~N)"))

    # --- time_blind (priority 5) ---
    if re.search(r"\bsleep\s*\(", p):
        candidates.append((5, "time_blind", "sleep()"))
    if re.search(r"\bpg_sleep\s*\(", p):
        candidates.append((5, "time_blind", "pg_sleep()"))
    if re.search(r"\bwaitfor\s+delay\b", p):
        candidates.append((5, "time_blind", "WAITFOR DELAY"))
    if re.search(r"\bbenchmark\s*\(", p):
        candidates.append((5, "time_blind", "benchmark()"))
    if re.search(r"\bdbms_pipe\.receive_message\b|\bdbms_lock\.sleep\b", p):
        candidates.append((5, "time_blind", "dbms_pipe/dbms_lock"))
    if re.search(r"\brandomblob\s*\(", p):
        candidates.append((5, "time_blind", "randomblob()"))

    # --- out_of_band (priority 6) ---
    if re.search(r"\bload_file\s*\(|\butl_http\.request\b|\bxp_dirtree\b", p):
        candidates.append((6, "out_of_band", "load_file/utl_http/xp_dirtree"))

    # --- union_based (priority 7) ---
    if re.search(r"\bunion\s+(all\s+)?select\b", p):
        candidates.append((7, "union_based", "UNION SELECT"))
    if re.search(r"%27union\s+select|\\x27union\s+select|union\s+select", p):
        candidates.append((7, "union_based", "UNION SELECT (encoded)"))

    # --- stacked_queries (priority 8) ---
    if re.search(r";\s*(insert|update|delete|drop|exec|create|alter|select|desc)\b", p):
        candidates.append((8, "stacked_queries", "; INSERT/UPDATE/DROP/EXEC/SELECT"))
    if re.search(r"\bxp_cmdshell\b", p):
        candidates.append((8, "stacked_queries", "xp_cmdshell"))
    if re.search(r"\binsert\s+into\s+mysql\.user\b", p):
        candidates.append((8, "stacked_queries", "INSERT INTO mysql.user"))

    # --- heavy_query (priority 4) ---
    if re.search(r"\bgenerate_series\b", p):
        candidates.append((4, "heavy_query", "generate_series"))
    # cartesian self-joins
    if re.search(r"\bsysibm\.systables\b.*\bas\s+t\d+", p) and p.count("sysibm.systables") >= 2:
        candidates.append((4, "heavy_query", "sysibm.systables x N (cartesian)"))
    if re.search(r"\brdb\$.*\bas\s+t\d+", p) and len(re.findall(r"\bas\s+t\d+", p)) >= 2:
        candidates.append((4, "heavy_query", "rdb$ tables x N (cartesian)"))
    if re.search(r"\bfrom\s+\w+\s+as\s+t1\s*,\s*\w+(\.\w+)?\s+as\s+t2", p) and "select count" in p:
        candidates.append((4, "heavy_query", "SELECT COUNT cartesian join"))
    if re.search(r"call\s+regexp_substring\s*\(\s*repeat\s*\(", p):
        candidates.append((4, "heavy_query", "regexp_substring(repeat(...))"))
    if re.search(r"\brepeat\s*\([^,)]+,\s*\d{6,}\s*\)", p):
        candidates.append((4, "heavy_query", "repeat(.., LARGE_N)"))

    # --- auth_bypass (priority 2) ---
    if re.search(r"['\"]?admin['\"]?\s*['\"]?\s*(--|#|/\*)", p):
        candidates.append((2, "auth_bypass", "admin'--"))
    if re.search(r"\bor\s+['\"]?1['\"]?\s*=\s*['\"]?1['\"]?", p) and ("admin" in p or "login" in p or "user" in p):
        candidates.append((2, "auth_bypass", "OR 1=1 + admin/login/user context"))

    # --- boolean_blind (priority 3) ---
    if re.search(r"\b(and|or)\s+\d+\s*=\s*\d+\b", p):
        candidates.append((3, "boolean_blind", "AND/OR N=N"))
    if re.search(r"\b(and|or)\s+['\"]\w+['\"]?\s*(like|=)\s*['\"]\w+", p):
        candidates.append((3, "boolean_blind", "AND/OR 'x'='x' or LIKE"))
    if re.search(r"\b(and|or)\s+\(\s*['\"]\w+['\"]?\s*(like|=)\s*['\"]\w+", p):
        candidates.append((3, "boolean_blind", "AND/OR ('x'='x')"))
    if re.search(r"\brlike\b|\belt\s*\(", p):
        candidates.append((3, "boolean_blind", "rlike/elt()"))
    if re.search(r"\bif\s*\(.*=.*,", p):
        candidates.append((3, "boolean_blind", "IF(cond, ..)"))
    if re.search(r"\bcase\s+when\s+.*\s+then\s+", p):
        candidates.append((3, "boolean_blind", "CASE WHEN .. THEN"))
    # order by / group by / having patterns for blind
    if re.search(r"\border\s+by\s+\d+(\s|#|--|$)", p):
        candidates.append((3, "boolean_blind", "ORDER BY N"))
    if re.search(r"\bgroup\s+by\s+.*having\s+", p):
        candidates.append((3, "boolean_blind", "GROUP BY .. HAVING"))
    if re.search(r"\bwhere\s+\d+\s*=\s*\d+\b", p):
        candidates.append((3, "boolean_blind", "WHERE N=N"))
    # short standalone blind closures
    if re.search(r"^['\"\s\-\d\)]*(end|where|order)\b.*\b\d+\s*=\s*\d+", p):
        candidates.append((3, "boolean_blind", "blind closure end/where N=N"))
    if re.search(r"['\"]\s*\)\s*\)?\s*as\s+\w+\s+where\s+\d+\s*=\s*\d+", p):
        candidates.append((3, "boolean_blind", "subquery alias WHERE N=N"))

    # --- polyglot (priority 9) ---
    if re.search(r"<script|onerror=|javascript:", p) and re.search(r"\bunion\b|\bselect\b|\bor\b\s+1", p):
        candidates.append((9, "polyglot", "XSS + SQLi mix"))

    # Decide type
    if not candidates:
        # Check if obviously benign or unsure
        # Detect any SQL keyword/metachar
        has_sql_token = bool(re.search(r"['\"\(\)]|--|#|union|select|sleep|or\s+1|and\s+1|drop|insert|order|where|/\*", p))
        if not has_sql_token:
            return ("benign", db, 0.80, f"No injection tokens (no quotes/SQL keywords) in payload. Snippet: {payload[:80]!r}")
        # has tokens but no rule matched - fallback
        if a_type and a_type == c_type and a_type != "":
            return (a_type, db, 0.65,
                    f"UNCERTAIN: no strong rule match. Sources A=C={a_type} agree. Payload tokens: {payload[:80]!r}")
        return ("benign", db, 0.55,
                f"UNCERTAIN: weak/no signals detected; fragment without clear SQLi pattern. Snippet: {payload[:80]!r}")

    # Sort by priority asc, pick lowest (strongest)
    candidates.sort(key=lambda x: x[0])
    pri, chosen_type, chosen_signal = candidates[0]

    db_part = f"; DB={db}" + (f" ({db_sig})" if db_sig else "")
    reasoning = f"Token '{chosen_signal}' in payload → {chosen_type} (priority {pri}){db_part}. Payload: {payload[:90]!r}"

    # Confidence based on source agreement
    src_match_a = (a_type == chosen_type)
    src_match_c = (c_type == chosen_type)
    src_match = int(src_match_a) + int(src_match_c)

    if src_match == 2:
        conf = 0.95
    elif src_match == 1:
        conf = 0.85
    else:
        conf = 0.75

    # boost if DB-specific signal makes type unambiguous
    if chosen_type in {"error_based", "time_blind", "out_of_band"} and db != "generic":
        conf = min(1.0, conf + 0.05)

    if len(reasoning) < 50:
        reasoning = reasoning + " | Priority-based decision from sqlmap-style ruleset."

    return (chosen_type, db, conf, reasoning)


rows_out = []
for idx, row in df.iterrows():
    payload = row["payload_inner"] if pd.notna(row["payload_inner"]) else (
        row["payload_norm"] if pd.notna(row["payload_norm"]) else "")
    a_type = str(row.get("a_type", "") or "")
    c_type = str(row.get("c_type", "") or "")

    sqli_type, db_engine, confidence, reasoning = detect(payload, a_type, c_type)

    # sources_agree
    if confidence < 0.5:
        sa = 0
    else:
        m_a = (sqli_type == a_type)
        m_c = (sqli_type == c_type)
        if m_a and m_c:
            sa = 3
        elif m_a or m_c:
            sa = 2
        else:
            sa = 1

    if len(reasoning) < 50:
        reasoning = reasoning + f" | a_type={a_type}, c_type={c_type}, db={db_engine}"

    confidence = max(0.5, min(1.0, confidence))

    rows_out.append({
        "id": row["id"],
        "payload_inner": payload,
        "sqli_type": sqli_type,
        "db_engine": db_engine,
        "confidence": round(confidence, 2),
        "reasoning": reasoning,
        "sources_agree": sa,
    })

out_df = pd.DataFrame(rows_out, columns=["id", "payload_inner", "sqli_type", "db_engine", "confidence", "reasoning", "sources_agree"])
out_df.to_csv(OUT_PATH, index=False, quoting=csv.QUOTE_MINIMAL)

# Report
print(f"Labeled: {len(out_df)} rows")
print("\nType distribution (top 5):")
print(out_df["sqli_type"].value_counts().head(5))
print(f"\nRows with confidence < 0.7: {(out_df['confidence'] < 0.7).sum()}")
print(f"Rows with reasoning < 50 chars: {(out_df['reasoning'].str.len() < 50).sum()}")
print(f"\nsources_agree distribution:")
print(out_df["sources_agree"].value_counts())
print(f"\ndb_engine distribution:")
print(out_df["db_engine"].value_counts())
print(f"\nMean confidence: {out_df['confidence'].mean():.3f}")
