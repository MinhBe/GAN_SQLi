"""label_payload.py — 3-source SQLi labeling.

For each payload, vote from 3 independent sources:
  (a) Rule-based pattern matching (sqlmap-style signatures)
  (b) Claude Haiku 4.5 (anthropic API)
  (c) Heuristic structure analysis (priority + DB signature)

Final label = majority vote (≥ 2/3 agree). Confidence reflects agreement:
  3/3 agree → 1.00
  2/3 agree → 0.85
  1/3 agree → 0.50 (FLAG for human review)
  0/3 agree → 0.30 (DROP candidate)

Output schema (per row):
  sqli_type, db_engine, confidence, reasoning, sources_agree,
  source_a_type, source_b_type, source_c_type
"""
import os
import re
import json
import time
from dataclasses import dataclass, field
from typing import Optional

# ── Taxonomy ──────────────────────────────────────────────────────────────────
SQLI_TYPES = [
    "union_based", "time_blind", "error_based", "out_of_band",
    "stacked_queries", "boolean_blind", "auth_bypass", "heavy_query",
    "polyglot", "benign",
]

DB_ENGINES = [
    "oracle", "mysql", "postgresql", "mssql", "firebird", "sqlite",
    "db2", "generic",
]

# Priority (lower = stronger signal in conflict resolution)
TYPE_PRIORITY = {
    "auth_bypass": 2, "boolean_blind": 3, "error_based": 4, "heavy_query": 4,
    "time_blind": 5, "out_of_band": 6, "union_based": 7, "stacked_queries": 8,
    "polyglot": 9, "benign": 99,
}

# ── Source A: Rule-based ──────────────────────────────────────────────────────
RULE_PATTERNS: dict[str, list] = {
    "time_blind": [
        re.compile(r"\bsleep\s*\(", re.I),
        re.compile(r"\bpg_sleep\s*\(", re.I),
        re.compile(r"\bwaitfor\s+delay\b", re.I),
        re.compile(r"\bbenchmark\s*\(", re.I),
        re.compile(r"\bdbms_pipe\.receive_message", re.I),
        re.compile(r"\bdbms_lock\.sleep", re.I),
        re.compile(r"\brandomblob\s*\(", re.I),
    ],
    "error_based": [
        re.compile(r"\bxmltype\s*\(", re.I),
        re.compile(r"\bextractvalue\s*\(", re.I),
        re.compile(r"\bupdatexml\s*\(", re.I),
        re.compile(r"\butl_inaddr\.get_host_address", re.I),
        re.compile(r"\bctxsys\.drithsx", re.I),
        re.compile(r"\bexp\s*\(\s*~", re.I),
    ],
    "out_of_band": [
        re.compile(r"\bload_file\s*\(", re.I),
        re.compile(r"\butl_http\b", re.I),
        re.compile(r"\bxp_dirtree\b", re.I),
    ],
    "stacked_queries": [
        re.compile(r";\s*(insert|update|delete|drop|create|alter|exec)\b", re.I),
        re.compile(r"\bxp_cmdshell\b", re.I),
    ],
    "union_based": [
        re.compile(r"\bunion\s+(all\s+)?select\b", re.I),
    ],
    "boolean_blind": [
        re.compile(r"\b(or|and)\s+\d+\s*=\s*\d+\b", re.I),
        re.compile(r"\belt\s*\(", re.I),
        re.compile(r"\brlike\s*\(", re.I),
    ],
    "auth_bypass": [
        re.compile(r"\badmin'\s*--", re.I),
        re.compile(r"\badmin'\s*#", re.I),
        re.compile(r"admin'\s*(or|and)\s+'?\d+'?\s*=\s*'?\d+", re.I),
    ],
    "heavy_query": [
        re.compile(r"\bgenerate_series\s*\(\s*\d+\s*,\s*\d{6,}\s*\)", re.I),
        re.compile(r"\brepeat\s*\([^,]+,\s*\d{6,}", re.I),
    ],
    "polyglot": [
        re.compile(r"<script[^>]*>", re.I),
        re.compile(r"javascript:", re.I),
    ],
}

DB_SIGNATURES = {
    "oracle": [r"\bxmltype\b", r"\bdual\b", r"\butl_inaddr\b", r"\bdbms_pipe\b",
               r"\bctxsys\b", r"\ball_tables\b", r"\brownum\b"],
    "mysql": [r"\bextractvalue\b", r"\bupdatexml\b", r"\bsleep\s*\(", r"\bbenchmark\b",
              r"\binformation_schema\b", r"\belt\b", r"\brlike\b"],
    "postgresql": [r"\bpg_sleep\b", r"\bpg_database\b", r"\bstring_agg\b",
                   r"\bgenerate_series\b"],
    "mssql": [r"\bxp_cmdshell\b", r"\bwaitfor\s+delay\b", r"\bsysobjects\b",
              r"\bsysdatabases\b"],
    "firebird": [r"\brdb\$", r"\bgen_id\b"],
    "sqlite": [r"\brandomblob\b", r"\bsqlite_master\b"],
    "db2": [r"\bsysibm\.systables\b"],
}


@dataclass
class LabelResult:
    sqli_type: str
    db_engine: str
    signals: list = field(default_factory=list)
    reasoning: str = ""


def detect_db(payload: str) -> str:
    """Detect DB engine by signature. Returns 'generic' if no match."""
    pl = payload.lower()
    for db, patterns in DB_SIGNATURES.items():
        for pat in patterns:
            if re.search(pat, pl, re.IGNORECASE):
                return db
    return "generic"


def source_a_rule_based(payload: str) -> LabelResult:
    """Source A: Sqlmap-style pattern matching."""
    if not payload or not payload.strip():
        return LabelResult("benign", "generic", reasoning="empty payload")

    pl = payload.lower()
    matches = {}
    for sqli_type, patterns in RULE_PATTERNS.items():
        for pat in patterns:
            m = pat.search(pl)
            if m:
                matches.setdefault(sqli_type, []).append(m.group(0))

    if not matches:
        # Check if has any SQL keyword at all
        if re.search(r"\b(select|insert|update|delete|union|or|and)\b", pl, re.I):
            # Has SQL but no specific signal → boolean_blind low-confidence
            return LabelResult(
                "boolean_blind", detect_db(payload),
                reasoning="generic SQL keywords without specific signal",
            )
        return LabelResult("benign", "generic", reasoning="no attack signal detected")

    # Pick type with lowest priority number (strongest signal)
    chosen = min(matches.keys(), key=lambda t: TYPE_PRIORITY.get(t, 99))
    signals_found = matches[chosen]
    db = detect_db(payload)
    reasoning = (
        f"Pattern match: '{signals_found[0]}' → {chosen} (P{TYPE_PRIORITY[chosen]})"
        f"; DB signature: {db}"
    )
    return LabelResult(chosen, db, signals_found, reasoning)


# ── Source B: Claude Haiku via Anthropic API ─────────────────────────────────
def source_b_haiku(payload: str, client=None) -> LabelResult:
    """Source B: Claude Haiku 4.5 verification.

    Returns LabelResult. If API fails, falls back to 'unknown' with low confidence.
    """
    if client is None:
        return LabelResult("unknown", "generic", reasoning="haiku client unavailable")

    system_prompt = (
        "You are a SQL injection classifier. Given a payload, return JSON: "
        '{"type": "<one of: ' + ", ".join(SQLI_TYPES) + '>", '
        '"db": "<one of: ' + ", ".join(DB_ENGINES) + '>", '
        '"reasoning": "<≥50 chars explaining the specific token/function evidence>"}. '
        "If no injection signal, type='benign'. Be precise — quote tokens from the payload."
    )
    user_prompt = f"Payload:\n```\n{payload[:1500]}\n```\nReturn JSON only."

    try:
        resp = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=300,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        text = resp.content[0].text.strip()
        # Strip markdown code fence if present
        text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
        data = json.loads(text)

        t = data.get("type", "unknown")
        if t not in SQLI_TYPES:
            t = "unknown"
        db = data.get("db", "generic")
        if db not in DB_ENGINES:
            db = "generic"
        reasoning = str(data.get("reasoning", ""))[:500]
        return LabelResult(t, db, reasoning=reasoning)
    except Exception as e:
        return LabelResult("unknown", "generic", reasoning=f"haiku error: {e}")


# ── Source C: Heuristic structure analysis ───────────────────────────────────
def source_c_heuristic(payload: str) -> LabelResult:
    """Source C: Structure-based heuristic using priority + DB signature.

    Different logic from rule-based:
      - Count occurrences (signal density)
      - Length-based discrimination
      - Special-case detection
    """
    if not payload or not payload.strip():
        return LabelResult("benign", "generic", reasoning="empty payload")

    pl = payload.lower()
    n_chars = len(pl)

    # Special case: pure comment / trivial
    if pl.strip() in ("--", ";", "/*", "*/", "#", ""):
        return LabelResult("benign", "generic", reasoning="trivial token only")

    # Polyglot detection (HTML/JS mixed in)
    if re.search(r"<\w+[^>]*>|javascript:", pl):
        return LabelResult("polyglot", "generic",
                           reasoning="contains HTML tag or javascript: scheme")

    # Heavy query: very long numbers (likely DoS pattern)
    if re.search(r"\d{7,}", pl):
        # ≥7-digit number suggests heavy_query (generate_series, repeat, etc.)
        return LabelResult("heavy_query", detect_db(payload),
                           reasoning="contains 7+ digit number (DoS-style payload)")

    # Auth bypass: admin' near OR/AND
    if re.search(r"admin'\s*(or|and|--|#)", pl):
        return LabelResult("auth_bypass", detect_db(payload),
                           reasoning="admin' prefix near boolean/comment context")

    # Stacked queries: semicolon followed by another statement
    if re.search(r";\s*(insert|update|delete|drop|create|alter|exec|xp_cmdshell)\b", pl):
        return LabelResult("stacked_queries", detect_db(payload),
                           reasoning="semicolon followed by DDL/DML/exec")

    # Time-blind: any time function
    time_funcs = ["sleep(", "pg_sleep(", "waitfor delay", "benchmark(",
                  "dbms_pipe", "dbms_lock.sleep", "randomblob("]
    for f in time_funcs:
        if f in pl:
            return LabelResult("time_blind", detect_db(payload),
                               reasoning=f"time function '{f}' detected")

    # Error-based: error functions
    error_funcs = ["xmltype(", "extractvalue(", "updatexml(", "utl_inaddr",
                   "ctxsys.drithsx", "exp(~"]
    for f in error_funcs:
        if f in pl:
            return LabelResult("error_based", detect_db(payload),
                               reasoning=f"error function '{f}' detected")

    # Union-based
    if re.search(r"\bunion\s+(all\s+)?select\b", pl):
        return LabelResult("union_based", detect_db(payload),
                           reasoning="UNION SELECT structure")

    # Out-of-band
    if re.search(r"\b(load_file|utl_http|xp_dirtree)\b", pl):
        return LabelResult("out_of_band", detect_db(payload),
                           reasoning="OOB file/network function")

    # Boolean blind: AND/OR 1=1 or RLIKE
    if re.search(r"\b(or|and)\s+\d+\s*=\s*\d+\b", pl) or "rlike" in pl or "elt(" in pl:
        return LabelResult("boolean_blind", detect_db(payload),
                           reasoning="boolean condition (1=1, RLIKE, or ELT)")

    # Has SQL keywords but no specific signal
    if re.search(r"\b(select|from|where|insert|update|delete)\b", pl):
        return LabelResult("boolean_blind", detect_db(payload),
                           reasoning="generic SQL structure without strong signal")

    return LabelResult("benign", "generic", reasoning="no SQLi signal in heuristic check")


# ── Voting & aggregation ─────────────────────────────────────────────────────
def vote(results: list[LabelResult]) -> tuple:
    """Majority vote across 3 sources. Returns (type, db, confidence, n_agree)."""
    types = [r.sqli_type for r in results]
    dbs = [r.db_engine for r in results]

    # Type vote
    from collections import Counter
    type_counts = Counter(types)
    top_type, top_n = type_counts.most_common(1)[0]

    # DB vote (separate; allow tie-break by majority)
    db_counts = Counter([d for d in dbs if d != "generic"])
    if db_counts:
        top_db, _ = db_counts.most_common(1)[0]
    else:
        top_db = "generic"

    # Confidence based on agreement
    if top_n == 3:
        confidence = 1.00
    elif top_n == 2:
        confidence = 0.85
    elif top_n == 1:
        # All disagree → use priority-based tiebreaker
        top_type = min(types, key=lambda t: TYPE_PRIORITY.get(t, 99))
        confidence = 0.50
    else:
        confidence = 0.30

    return top_type, top_db, confidence, top_n


def label_payload(payload: str, haiku_client=None) -> dict:
    """Run all 3 sources and aggregate."""
    a = source_a_rule_based(payload)
    b = source_b_haiku(payload, haiku_client) if haiku_client else \
        LabelResult("unknown", "generic", reasoning="haiku skipped")
    c = source_c_heuristic(payload)

    chosen_type, chosen_db, conf, n_agree = vote([a, b, c])

    # Compose reasoning from agreeing sources
    agreeing_reasonings = [r.reasoning for r in (a, b, c) if r.sqli_type == chosen_type]
    final_reasoning = " | ".join(agreeing_reasonings[:2])[:500]
    if len(final_reasoning) < 50:
        final_reasoning = (final_reasoning + " | " +
                           f"sources={n_agree}/3; chosen={chosen_type}@P{TYPE_PRIORITY.get(chosen_type, 99)}")[:500]

    return {
        "sqli_type": chosen_type,
        "db_engine": chosen_db,
        "confidence": conf,
        "reasoning": final_reasoning,
        "sources_agree": n_agree,
        "source_a_type": a.sqli_type,
        "source_b_type": b.sqli_type,
        "source_c_type": c.sqli_type,
    }


def label_payload_chat_queue(payload: str) -> dict:
    """Chat-queue mode: run A + C only, output as HINTS for subagent.

    No voting — subagent will make final decision based on payload + these hints.
    """
    a = source_a_rule_based(payload)
    c = source_c_heuristic(payload)
    return {
        "a_type": a.sqli_type,
        "a_db": a.db_engine,
        "a_signals": a.reasoning[:200],
        "c_type": c.sqli_type,
        "c_db": c.db_engine,
        "c_signals": c.reasoning[:200],
    }


def get_haiku_client():
    """Initialize Anthropic client. Returns None if not configured."""
    try:
        import anthropic
        api_key = os.environ.get("ANTHROPIC_API_KEY")
        if not api_key:
            print("WARNING: ANTHROPIC_API_KEY not set — source B will be skipped")
            return None
        return anthropic.Anthropic(api_key=api_key)
    except ImportError:
        print("WARNING: anthropic package not installed — source B skipped")
        return None


# ── CLI ────────────────────────────────────────────────────────────────────────
def _main():
    import argparse
    import pandas as pd

    parser = argparse.ArgumentParser(description="3-source SQLi labeling")
    parser.add_argument("--input", required=True, help="Input CSV")
    parser.add_argument("--output", required=True, help="Output CSV")
    parser.add_argument("--col", default="payload_inner",
                        help="Column to label (default: payload_inner). For chat_queue "
                             "mode, fallback to payload_norm if payload_inner missing.")
    parser.add_argument("--mode", default="api",
                        choices=["api", "chat_queue"],
                        help="api=full 3-source with Haiku; "
                             "chat_queue=A+C only, output hints for subagent labeling")
    parser.add_argument("--no_haiku", action="store_true",
                        help="(api mode) Skip Claude Haiku, use only A+C")
    parser.add_argument("--limit", type=int, default=None, help="Limit N rows for testing")
    parser.add_argument("--sleep", type=float, default=0.1,
                        help="Sleep between Haiku calls to avoid rate limit")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    if args.limit:
        df = df.head(args.limit).copy()

    # Resolve column: prefer payload_inner, fallback to payload_norm
    if args.col not in df.columns:
        if "payload_norm" in df.columns:
            print(f"WARN: '{args.col}' not in CSV; falling back to 'payload_norm'")
            args.col = "payload_norm"
        else:
            raise SystemExit(f"ERROR: neither '{args.col}' nor 'payload_norm' in CSV")

    if args.mode == "chat_queue":
        # Chat-queue mode: A + C as hints; subagent decides
        results = []
        for i, row in df.iterrows():
            payload = str(row.get(args.col, ""))
            r = label_payload_chat_queue(payload)
            results.append(r)
            if (i + 1) % 1000 == 0:
                print(f"  Pre-labeled {i+1}/{len(df)}")
        for key in ["a_type", "a_db", "a_signals", "c_type", "c_db", "c_signals"]:
            df[key] = [r[key] for r in results]
        df.to_csv(args.output, index=False)
        print(f"\nWrote {len(df)} rows to {args.output} (chat_queue mode)")
        print(f"\n=== A SOURCE TYPE DISTRIBUTION ===")
        print(df["a_type"].value_counts())
        print(f"\n=== C SOURCE TYPE DISTRIBUTION ===")
        print(df["c_type"].value_counts())
        ac_disagree = (df["a_type"] != df["c_type"]).sum()
        print(f"\nA != C: {ac_disagree}/{len(df)} ({ac_disagree/len(df):.1%}) "
              f"(these rows benefit most from chat verification)")
        return

    # api mode (full 3-source with Haiku)
    client = None if args.no_haiku else get_haiku_client()
    results = []
    for i, row in df.iterrows():
        payload = str(row.get(args.col, ""))
        r = label_payload(payload, haiku_client=client)
        results.append(r)
        if client and args.sleep > 0:
            time.sleep(args.sleep)
        if (i + 1) % 50 == 0:
            print(f"  Labeled {i+1}/{len(df)}")

    for key in ["sqli_type", "db_engine", "confidence", "reasoning",
                "sources_agree", "source_a_type", "source_b_type", "source_c_type"]:
        df[f"new_{key}"] = [r[key] for r in results]

    df.to_csv(args.output, index=False)
    print(f"\nWrote {len(df)} rows to {args.output}")
    print(f"\n=== AGREEMENT STATS ===")
    print(df["new_sources_agree"].value_counts().sort_index())
    print(f"\n=== NEW TYPE DISTRIBUTION ===")
    print(df["new_sqli_type"].value_counts())


if __name__ == "__main__":
    _main()
