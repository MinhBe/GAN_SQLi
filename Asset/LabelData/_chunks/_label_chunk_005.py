#!/usr/bin/env python3
"""Label chunk_005.csv using priority-based rule matching with payload evidence.

Priority table (lower = stronger):
  1 benign, 2 auth_bypass, 3 boolean_blind, 4 error_based/heavy_query,
  5 time_blind, 6 out_of_band, 7 union_based, 8 stacked_queries, 9 polyglot
"""
import csv
import re
import sys
from pathlib import Path

IN_PATH = Path(r"C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks\chunk_005.csv")
OUT_PATH = Path(r"C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\_chunks\chunk_005_labeled.csv")

# ---- DB engine signatures ----
DB_PATTERNS = [
    ("oracle",     [r"\bxmltype\b", r"\bdual\b", r"\butl_inaddr\b", r"\bdbms_pipe\b",
                    r"\bdbms_lock\b", r"\bctxsys\b", r"\ball_tables\b", r"\brownum\b",
                    r"\butl_http\b", r"\bsys\.all_tables\b"]),
    ("mysql",      [r"\bextractvalue\b", r"\bupdatexml\b", r"\bbenchmark\b",
                    r"\binformation_schema\b", r"\belt\b", r"\brlike\b",
                    r"\bload_file\b", r"\bmysql\.user\b", r"\bunhex\b",
                    r"\bsleep\s*\(", r"\bexp\s*\(\s*~"]),
    ("postgresql", [r"\bpg_sleep\b", r"\bpg_database\b", r"\bstring_agg\b",
                    r"\bgenerate_series\b", r"::\s*int", r"\bcurrent_database\b"]),
    ("mssql",      [r"\bwaitfor\s+delay\b", r"\bxp_cmdshell\b", r"\bxp_dirtree\b",
                    r"\bsysobjects\b", r"\bsysdatabases\b", r"\bmaster\.\.",
                    r"\bconvert\s*\(", r"@@version"]),
    ("firebird",   [r"\brdb\$", r"\bgen_id\b"]),
    ("sqlite",     [r"\brandomblob\b", r"\bsqlite_master\b", r"\blike\s*\(\s*['\"]?\w"]),
    ("db2",        [r"\bsysibm\.systables\b", r"\bcurrent\s+schema\b"]),
]

# ---- Type signatures with priority ----
# Each: (type, priority, regex_list, description)
TYPE_RULES = [
    # P8 stacked queries
    ("stacked_queries", 8, [r";\s*(insert|update|delete|drop|exec|create|alter)\b",
                            r"\bxp_cmdshell\b"], "stacked statement separator ';' + DDL/DML"),
    # P9 polyglot
    ("polyglot",        9, [r"<script", r"javascript:", r"</?\w+>\s*['\"`]"], "HTML/JS tags mixed with SQL"),
    # P6 OOB
    ("out_of_band",     6, [r"\butl_http\b", r"\butl_inaddr\b", r"\bxp_dirtree\b",
                            r"\bload_file\b", r"\bdbms_ldap\b",
                            r"\\\\[a-z0-9.]+\\", r"\bmaster\.\.xp_dirtree\b"], "OOB exfil function"),
    # P5 time_blind
    ("time_blind",      5, [r"\bsleep\s*\(", r"\bpg_sleep\b", r"\bwaitfor\s+delay\b",
                            r"\bbenchmark\s*\(", r"\bdbms_pipe\.receive_message\b",
                            r"\bdbms_lock\.sleep\b", r"\brandomblob\s*\("], "time delay function"),
    # P4 heavy_query
    ("heavy_query",     4, [r"\bgenerate_series\b", r"\bwith\s+recursive\b",
                            r"\bcross\s+join\b.*\bcross\s+join\b",
                            # Triple+ cartesian: t1,t2,t3 of same/metadata table (allow rdb$, sys.,...)
                            r"\bfrom\s+[\w\$\.]+\s+(as\s+)?\w+\s*,\s*[\w\$\.]+\s+(as\s+)?\w+\s*,\s*[\w\$\.]+\s+(as\s+)?\w+\s*,",
                            r"\bselect\s+count\s*\(\s*\*\s*\)\s+from\s+[\w\$\.]+\s+(as\s+)?\w+\s*,\s*[\w\$\.]+"],
     "heavy compute / cartesian join"),
    # P4 error_based
    ("error_based",     4, [r"\bxmltype\b", r"\bextractvalue\b", r"\bupdatexml\b",
                            r"\bexp\s*\(\s*~", r"\butl_inaddr\.get_host_address\b",
                            r"\bctxsys\.drithsx\b", r"\bcast\s*\([^)]*\bas\s+int\b",
                            r"\bconvert\s*\([^)]*,"], "error-based XML/cast function"),
    # P7 union_based
    ("union_based",     7, [r"\bunion\s+(all\s+)?select\b", r"\bunion\s+select\b"], "UNION SELECT"),
    # P3 boolean_blind
    ("boolean_blind",   3, [r"\brlike\s*\(", r"\belt\s*\(",
                            r"\b(and|or)\s+\d+\s*=\s*\d+\b",
                            r"\b(and|or)\s+'[^']*'\s*=\s*'[^']*'",
                            r"\b(and|or)\s+\d+\s*<\s*\d+\b",
                            r"\bif\s*\([^)]+,[^)]+,[^)]+\)",
                            r"\bcase\s+when\b.*\bthen\b.*\belse\b",
                            r"\b(and|or)\s+\(\s*\d+\s*=\s*\d+\s*\)",
                            r"\bwhere\s+\d+\s*=\s*\d+\b",
                            r"\bregexp_like\b", r"\bdbms_utility\.sqlid_to_sqlhash\b",
                            # 'X'='X' string tautology anywhere
                            r"\(\s*'[\w%]+'\s*=\s*'[\w%]+",
                            # make_set boolean signal (MySQL)
                            r"\bmake_set\s*\(",
                            # regexp_substring / regexp_replace used as boolean compare
                            r"\bregexp_substring\b", r"\bregexp_replace\b",
                            # OR/AND followed by '... = ...' string compare
                            r"=\s*'[a-z0-9]{3,6}'\s*--",
                            # case <num> when <num> then 1 else 0
                            r"\bcase\s+\d+\s+when\s+\d+\s+then\b"],
     "boolean tautology / RLIKE/ELT/IF/CASE/make_set/regexp"),
    # P2 auth_bypass
    ("auth_bypass",     2, [r"admin'\s*(--|#|/\*)", r"'\s*or\s*'1'\s*=\s*'1",
                            r"'\s*or\s*1\s*=\s*1\s*(--|#)",
                            r"'\s*or\s*''\s*=\s*'"], "auth bypass tautology"),
]

PRIORITY_ORDER = {  # lower wins
    "benign": 1, "auth_bypass": 2, "boolean_blind": 3, "error_based": 4,
    "heavy_query": 4, "time_blind": 5, "out_of_band": 6, "union_based": 7,
    "stacked_queries": 8, "polyglot": 9,
}


def detect_db(payload: str) -> tuple[str, str]:
    """Return (db_engine, matched_token)."""
    p = payload.lower()
    for db, patterns in DB_PATTERNS:
        for pat in patterns:
            m = re.search(pat, p, re.IGNORECASE)
            if m:
                return db, m.group(0)
    return "generic", ""


def detect_types(payload: str) -> list[tuple[str, int, str, str]]:
    """Return list of (type, priority, matched_token, description)."""
    p = payload.lower()
    hits = []
    for tname, prio, patterns, desc in TYPE_RULES:
        for pat in patterns:
            m = re.search(pat, p, re.IGNORECASE)
            if m:
                hits.append((tname, prio, m.group(0), desc))
                break
    return hits


def is_likely_benign(payload: str) -> bool:
    """Very simple benign check: no SQL injection markers."""
    p = payload.lower().strip()
    if len(p) < 5:
        return True
    # Has SQL but no injection markers
    inj_markers = ["'", '"', "--", "#", "/*", " or ", " and ", " union ", " sleep",
                   "waitfor", "xmltype", "extractvalue", "updatexml", "pg_sleep",
                   "rlike", "elt(", "benchmark", "convert(", "cast(", " || ",
                   "char(", "chr(", "xp_", "load_file", "randomblob"]
    return not any(m in p for m in inj_markers)


def label_payload(payload: str, a_type: str, c_type: str,
                  a_db: str, c_db: str) -> tuple[str, str, float, str]:
    """Return (sqli_type, db_engine, confidence, reasoning)."""
    if not payload or not payload.strip():
        return "benign", "generic", 0.5, "UNCERTAIN: empty payload, no tokens to analyze for SQLi signature."

    type_hits = detect_types(payload)
    db_engine, db_token = detect_db(payload)

    # Show payload snippet for evidence (cap 80)
    snippet = payload[:80].replace("\n", " ")

    if not type_hits:
        if is_likely_benign(payload):
            reason = (f"No SQLi tokens found in payload '{snippet}'; "
                      f"no UNION/SLEEP/XMLTYPE/RLIKE/OR-tautology/comment markers. "
                      f"Classified benign per priority P1.")
            return "benign", db_engine, 0.85, reason
        # has some SQL markers but no clear signal
        reason = (f"UNCERTAIN: payload '{snippet}' has SQL syntax but no priority-tagged "
                  f"signal (no UNION/SLEEP/XMLTYPE/ELT/RLIKE/WAITFOR matched). "
                  f"a_type={a_type}, c_type={c_type}.")
        # tiebreaker via a_type if non-benign
        if a_type and a_type not in ("benign", "unknown", ""):
            return a_type, a_db or db_engine, 0.5, reason
        return "benign", db_engine, 0.5, reason

    # Pick lowest priority hit
    type_hits.sort(key=lambda x: x[1])
    chosen_type, chosen_prio, chosen_tok, chosen_desc = type_hits[0]

    # Build reasoning
    parts = []
    parts.append(f"Token '{chosen_tok}' matched in payload '{snippet}' → "
                 f"{chosen_type} (P{chosen_prio}, {chosen_desc})")
    if db_token:
        parts.append(f"DB signature token '{db_token}' → {db_engine}")
    else:
        parts.append(f"No exclusive DB signature → {db_engine}")
    # mention secondary if any
    if len(type_hits) > 1:
        sec = type_hits[1]
        parts.append(f"secondary signal '{sec[2]}' ({sec[0]} P{sec[1]}) overridden by priority")

    reasoning = "; ".join(parts)
    if len(reasoning) < 50:
        reasoning += f"; full context: {snippet}"

    # Confidence: 0.9 if both type tokens and db_token, 0.8 if just type
    if db_token and len(type_hits) >= 2:
        conf = 0.95
    elif db_token:
        conf = 0.9
    elif len(type_hits) >= 2:
        conf = 0.85
    else:
        conf = 0.8

    return chosen_type, db_engine, conf, reasoning


def main():
    rows_in = []
    with IN_PATH.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for r in reader:
            rows_in.append(r)

    out_rows = []
    type_counts = {}
    low_conf = 0
    short_reason = 0
    sources_agree_dist = {0: 0, 1: 0, 2: 0, 3: 0}

    for idx, r in enumerate(rows_in):
        rid = r.get("id") or str(idx)
        payload = r.get("payload_inner") or r.get("payload_norm") or ""
        a_type = (r.get("a_type") or "").strip()
        a_db = (r.get("a_db") or "").strip()
        c_type = (r.get("c_type") or "").strip()
        c_db = (r.get("c_db") or "").strip()

        sqli_type, db_engine, conf, reasoning = label_payload(
            payload, a_type, c_type, a_db, c_db
        )

        # sources_agree
        if conf < 0.5:
            sa = 0
        else:
            matches = 0
            if a_type == sqli_type:
                matches += 1
            if c_type == sqli_type:
                matches += 1
            if matches == 2:
                sa = 3
            elif matches == 1:
                sa = 2
            else:
                sa = 1

        type_counts[sqli_type] = type_counts.get(sqli_type, 0) + 1
        if conf < 0.7:
            low_conf += 1
        if len(reasoning) < 50:
            short_reason += 1
        sources_agree_dist[sa] = sources_agree_dist.get(sa, 0) + 1

        out_rows.append({
            "id": rid,
            "payload_inner": payload,
            "sqli_type": sqli_type,
            "db_engine": db_engine,
            "confidence": f"{conf:.2f}",
            "reasoning": reasoning,
            "sources_agree": sa,
        })

    cols = ["id", "payload_inner", "sqli_type", "db_engine",
            "confidence", "reasoning", "sources_agree"]
    with OUT_PATH.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=cols)
        w.writeheader()
        w.writerows(out_rows)

    # Print report
    print(f"Rows labeled: {len(out_rows)}")
    print("Type distribution (top 5):")
    for t, c in sorted(type_counts.items(), key=lambda x: -x[1])[:5]:
        print(f"  {t}: {c}")
    print(f"Rows confidence<0.7: {low_conf}")
    print(f"Rows reasoning<50 chars: {short_reason}")
    print(f"sources_agree dist: {sources_agree_dist}")


if __name__ == "__main__":
    main()
