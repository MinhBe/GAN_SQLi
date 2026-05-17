"""Label chunk_003.csv with sqli_type, db_engine, confidence, reasoning, sources_agree.

Rules follow taxonomy.md priority table (lower = stronger):
  auth_bypass(2) < boolean_blind(3) < error_based(4) < heavy_query(4) <
  time_blind(5) < out_of_band(6) < union_based(7) < stacked_queries(8) <
  polyglot(9) < benign(1 special)

Reasoning must quote specific tokens (>= 50 chars).
"""

import csv
import os
import re
import sys

IN_PATH = r"C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks\chunk_003.csv"
OUT_PATH = r"C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks\chunk_003_labeled.csv"

# ---------------------------------------------------------------------------
# DB engine detection
# ---------------------------------------------------------------------------

DB_PATTERNS = [
    # oracle
    ("oracle", re.compile(
        r"\b(xmltype|dbms_pipe|dbms_lock|utl_inaddr|utl_http|ctxsys|"
        r"all_users|all_tables|sys\.all_tables|dual|rownum)\b", re.I)),
    # mysql
    ("mysql", re.compile(
        r"\b(extractvalue|updatexml|benchmark|elt|rlike|information_schema|"
        r"mysql\.user|load_file|unhex|sleep\s*\()\b", re.I)),
    # postgresql
    ("postgresql", re.compile(
        r"\b(pg_sleep|pg_database|generate_series|string_agg|pg_catalog|"
        r"pg_user)\b", re.I)),
    # mssql
    ("mssql", re.compile(
        r"\b(waitfor\s+delay|xp_cmdshell|xp_dirtree|sysobjects|sysdatabases|"
        r"master\.\.)\b", re.I)),
    # sqlite
    ("sqlite", re.compile(r"\b(randomblob|sqlite_master)\b", re.I)),
    # firebird
    ("firebird", re.compile(r"(rdb\$|\bgen_id\b)", re.I)),
    # db2
    ("db2", re.compile(r"\b(sysibm\.systables|current\s+schema)\b", re.I)),
]


def detect_db(payload: str, hint_a: str, hint_c: str) -> str:
    for db, pat in DB_PATTERNS:
        if pat.search(payload):
            return db
    # fallback: trust hints if they agree
    if hint_a and hint_a == hint_c and hint_a not in ("", "unknown"):
        return hint_a
    if hint_a and hint_a not in ("", "unknown", "generic"):
        return hint_a
    if hint_c and hint_c not in ("", "unknown", "generic"):
        return hint_c
    return "generic"


# ---------------------------------------------------------------------------
# Pattern matchers per type (return matched token or None)
# ---------------------------------------------------------------------------

def find(pattern: str, text: str, flags=re.I):
    m = re.search(pattern, text, flags)
    return m.group(0) if m else None


def detect_type(payload: str):
    """Return list of (priority, type, token, signal_desc) sorted by priority."""
    hits = []
    p = payload

    # --- polyglot (P9): XSS + SQLi mix
    tok = find(r"<\s*script|javascript:|onerror=|onload=", p)
    if tok:
        # only polyglot if there's also a SQL token
        if re.search(r"(union|select|sleep|extractvalue|--|or\s+1=1|;)", p, re.I):
            hits.append((9, "polyglot", tok,
                         f"XSS marker '{tok}' combined with SQL keywords (polyglot)"))

    # --- stacked_queries (P8): ; INSERT/UPDATE/DROP/EXEC
    tok = find(r";\s*(insert|update|delete|drop|exec|create|alter|truncate)\b", p)
    if tok:
        hits.append((8, "stacked_queries", tok,
                     f"semicolon-stacked statement '{tok}' indicates stacked queries"))
    tok2 = find(r"\bxp_cmdshell\b", p)
    if tok2:
        hits.append((8, "stacked_queries", tok2,
                     f"'xp_cmdshell' MSSQL shell exec via stacked query"))

    # --- union_based (P7): UNION SELECT / UNION ALL SELECT
    tok = find(r"\bunion\s+(all\s+)?select\b", p)
    if tok:
        hits.append((7, "union_based", tok,
                     f"'{tok}' is the classic UNION-based extraction pattern"))

    # --- out_of_band (P6)
    tok = find(r"\b(utl_http\.request|utl_inaddr\.get_host_address|"
               r"xp_dirtree|load_file)\b", p)
    if tok:
        hits.append((6, "out_of_band", tok,
                     f"OOB exfil primitive '{tok}' performs external data egress"))
    # DNS-style: domain || ... in chr concat (cheap heuristic)
    tok = find(r"\.(burpcollab|oast|interact\.sh|requestbin|ngrok)\.", p)
    if tok:
        hits.append((6, "out_of_band", tok,
                     f"OOB callback domain '{tok}' used for DNS exfiltration"))

    # --- time_blind (P5): SLEEP/pg_sleep/WAITFOR/BENCHMARK/dbms_pipe/randomblob
    tok = find(r"\b(pg_sleep|sleep|benchmark|waitfor\s+delay|"
               r"dbms_pipe\.receive_message|dbms_lock\.sleep|randomblob)\s*\(?", p)
    if tok:
        hits.append((5, "time_blind", tok.strip(),
                     f"time-delay primitive '{tok.strip()}' causes blind timing oracle"))

    # --- heavy_query (P4): generate_series, large cartesian joins, recursive CTE
    tok = find(r"\bgenerate_series\b", p)
    if tok:
        hits.append((4, "heavy_query", tok,
                     f"'generate_series' produces large row counts for heavy_query DoS"))
    # cartesian join: many table aliases t1..tN OR repeated joins of metadata tables
    m = re.findall(
        r"(all_users|all_tables|information_schema\.\w+|sysibm\.systables|"
        r"rdb\$\w+|sqlite_master|sysobjects|sysdatabases|"
        r"domain\.\w+|pg_\w+)\s+(as\s+)?t\d", p, re.I)
    if len(m) >= 3:
        first = m[0][0] if isinstance(m[0], tuple) else m[0]
        hits.append((4, "heavy_query", first,
                     f"{len(m)} cartesian aliases of '{first}' produce row explosion (heavy_query DoS)"))
    # WITH RECURSIVE
    tok = find(r"\bwith\s+recursive\b", p)
    if tok:
        hits.append((4, "heavy_query", tok,
                     f"'WITH RECURSIVE' CTE used as compute-heavy oracle"))

    # --- error_based (P4): xmltype, extractvalue, updatexml, cast(... as int) error
    tok = find(r"\b(xmltype|extractvalue|updatexml|ctxsys\.drithsx\.sn|exp)\s*\(", p)
    if tok:
        hits.append((4, "error_based", tok,
                     f"error-induction call '{tok}' leaks data through DB error message"))
    # cast(... as int) over non-numeric → error
    tok = find(r"\bcast\s*\([^)]+as\s+(int|integer|signed)\)", p)
    if tok:
        hits.append((4, "error_based", tok,
                     f"'{tok}' cast-to-int forces conversion error for error_based leak"))
    # convert(int, ...)
    tok = find(r"\bconvert\s*\(\s*int\b", p)
    if tok:
        hits.append((4, "error_based", tok,
                     f"'{tok}' MSSQL convert-to-int forces type error for error_based"))

    # --- auth_bypass (P2): admin' --, OR '1'='1 near login-ish
    tok = find(r"(admin'\s*--|admin\"\s*--|'\s*or\s*'1'='1|'\s*or\s+1\s*=\s*1\s*--|"
               r"'\s*or\s+''\s*=\s*'|'\s*=\s*'|admin'\s*#)", p)
    if tok:
        # only treat as auth_bypass if short and looks like login bypass
        if len(p) < 80 or re.search(r"admin", p, re.I):
            hits.append((2, "auth_bypass", tok,
                         f"login-bypass tautology '{tok}' typical of auth_bypass"))

    # --- boolean_blind (P3): AND 1=1, OR 1=2, RLIKE, ELT, IF()
    tok = find(r"\b(and|or)\s+\d+\s*=\s*\d+", p)
    if tok:
        hits.append((3, "boolean_blind", tok,
                     f"boolean comparison '{tok}' is classic AND/OR true/false oracle"))
    else:
        # Bare numeric tautology like '1557 = 1557' inside an injected WHERE
        tok = find(r"\bwhere\s+\d+\s*=\s*\d+", p)
        if tok:
            hits.append((3, "boolean_blind", tok,
                         f"injected WHERE-tautology '{tok}' is boolean true oracle"))
        else:
            # standalone equal-number tautology with surrounding paren / quote injection
            tok = find(r"\d+\s*=\s*\d+", p)
            if tok and re.search(r"(\b(select|where)\b|[)('\"\|])", p, re.I):
                hits.append((3, "boolean_blind", tok,
                             f"numeric tautology '{tok}' acts as boolean true branch"))
    tok = find(r"\belt\s*\(", p)
    if tok:
        hits.append((3, "boolean_blind", tok,
                     f"'ELT(' MySQL conditional return used as boolean oracle"))
    tok = find(r"\brlike\b", p)
    if tok:
        hits.append((3, "boolean_blind", tok,
                     f"'RLIKE' MySQL regex used for boolean inference"))
    tok = find(r"\bif\s*\(\s*\w+\s*[=<>]", p)
    if tok:
        hits.append((3, "boolean_blind", tok,
                     f"'{tok}' conditional IF() returns 1/0 for boolean inference"))
    # like comparisons of equal strings
    tok = find(r"'[a-z]+'\s+like\s+'[a-z]+", p, re.I)
    if tok:
        hits.append((3, "boolean_blind", tok,
                     f"LIKE tautology '{tok}' yields boolean true/false"))
    # case when ... then 1 else 0
    tok = find(r"\bcase\s+when\b", p)
    if tok:
        hits.append((3, "boolean_blind", tok,
                     f"'CASE WHEN' conditional branches used as boolean oracle"))

    return sorted(hits, key=lambda h: h[0])


# ---------------------------------------------------------------------------
# Main labeling logic
# ---------------------------------------------------------------------------

BENIGN_RE = re.compile(
    r"^\s*select\s+\w[\w\s,*().]*\s+from\s+\w+(\s+where\s+\w+\s*=\s*[\w'\"%]+)?\s*;?\s*$",
    re.I,
)


def label_row(payload: str, a_type: str, a_db: str, c_type: str, c_db: str):
    p = payload or ""
    p_low = p.lower()

    # benign check: minimal length & no injection signals at all
    has_sigi = bool(re.search(
        r"(union|sleep|pg_sleep|waitfor|extractvalue|updatexml|xmltype|"
        r"benchmark|\belt\b|rlike|xp_cmdshell|generate_series|all_users|"
        r"all_tables|sysobjects|sysdatabases|information_schema|dual|"
        r"--|/\*|#|;\s*(insert|drop|update|delete|exec)|"
        r"\bor\b\s+\d+\s*=\s*\d+|\band\b\s+\d+\s*=\s*\d+|"
        r"\d+\s*=\s*\d+|"  # bare tautology like 1557=1557
        r"'\s*or\s*'|admin'|case\s+when|cast\s*\(|convert\s*\(\s*int|"
        r"\|\||\bchr\s*\(|\bord\s*\(|\bhex\s*\(|\bunhex\s*\(|"
        r"^\s*['\"\d]+\s*['\"\)]|"   # starts with broken-quote payload prefix like 1' or 1"
        r"\)\s*(and|or)\s*\(|"       # paren-stacked AND/OR
        r"like\s+['\"]|0x[0-9a-f]{4,})",
        p_low,
    ))
    if not has_sigi and len(p) > 0:
        # treat as benign
        db = detect_db(p, a_db, c_db)
        reason = (f"No SQLi tokens found in payload (no UNION/SLEEP/extractvalue/"
                  f"OR 1=1/--/;EXEC etc.); payload appears as benign SQL fragment "
                  f"'{p[:40]}'")
        return "benign", db, 0.85, reason

    hits = detect_type(p)
    db = detect_db(p, a_db, c_db)

    if not hits:
        # unsure — try to lean on hints if both agree
        if a_type and a_type == c_type and a_type not in ("", "unknown"):
            reason = (f"UNCERTAIN: no rule-pattern match; both sources A and C "
                      f"agree on '{a_type}'. Payload fragment: '{p[:60]}'")
            return a_type, db, 0.5, reason
        reason = (f"UNCERTAIN: no specific SQLi signal token matched in payload "
                  f"'{p[:80]}'; cannot determine type confidently.")
        return "boolean_blind", db, 0.5, reason

    # Take strongest (lowest priority) hit
    prio, ttype, tok, signal_desc = hits[0]

    # Aggregate evidence from up to 2 distinct types for richer reasoning
    other_toks = []
    for h in hits[1:3]:
        if h[1] != ttype:
            other_toks.append(f"'{h[2]}' ({h[1]})")

    reason = signal_desc
    if other_toks:
        reason += " ; secondary signals: " + ", ".join(other_toks)
    reason += f" ; db_engine={db}"

    # confidence
    if a_type == ttype and c_type == ttype:
        conf = 0.95
    elif a_type == ttype or c_type == ttype:
        conf = 0.85
    else:
        conf = 0.75

    # ensure reasoning length
    if len(reason) < 50:
        reason += f" ; payload prefix: '{p[:40]}'"

    return ttype, db, conf, reason


def main():
    with open(IN_PATH, "r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    out_rows = []
    type_counts = {}
    low_conf = 0
    short_reason = 0

    for idx, row in enumerate(rows):
        payload = row.get("payload_inner") or row.get("payload_norm") or ""
        a_type = (row.get("a_type") or "").strip().lower()
        a_db = (row.get("a_db") or "").strip().lower()
        c_type = (row.get("c_type") or "").strip().lower()
        c_db = (row.get("c_db") or "").strip().lower()

        ttype, db, conf, reason = label_row(payload, a_type, a_db, c_type, c_db)

        # sources_agree
        if conf < 0.5 + 1e-9 and reason.startswith("UNCERTAIN"):
            sa = 0
        else:
            sa_match = sum([ttype == a_type, ttype == c_type])
            if ttype == a_type and ttype == c_type:
                sa = 3
            elif sa_match == 1:
                sa = 2
            else:
                sa = 1
        # clamp confidence
        conf = max(0.5, min(1.0, conf))

        row_id = row.get("id") or str(idx)

        out_rows.append({
            "id": row_id,
            "payload_inner": payload,
            "sqli_type": ttype,
            "db_engine": db,
            "confidence": f"{conf:.2f}",
            "reasoning": reason,
            "sources_agree": sa,
        })

        type_counts[ttype] = type_counts.get(ttype, 0) + 1
        if conf < 0.7:
            low_conf += 1
        if len(reason) < 50:
            short_reason += 1

    # Write
    fieldnames = ["id", "payload_inner", "sqli_type", "db_engine",
                  "confidence", "reasoning", "sources_agree"]
    with open(OUT_PATH, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(out_rows)

    # Report to stdout
    print(f"LABELED_ROWS={len(out_rows)}")
    top = sorted(type_counts.items(), key=lambda x: -x[1])[:5]
    print("TOP5=" + ";".join(f"{t}:{c}" for t, c in top))
    print(f"LOW_CONF_LT_0.7={low_conf}")
    print(f"SHORT_REASON_LT_50={short_reason}")


if __name__ == "__main__":
    main()
