"""
Phase 02 — Script 3: Rule-based Minimal Labeler
Input : Guiding/Phase 2/slice_payloads.parquet
Output: Guiding/Phase 2/slice_labeled.parquet
Labels: is_sqli, technique_primary, db_hint, syntax_validity, confidence_basic
"""

import re
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
SRC  = HERE / "slice_payloads.parquet"
OUT  = HERE / "slice_labeled.parquet"

# ── Detection patterns ─────────────────────────────────────────────────────────

RE_TIME_BLIND = re.compile(
    r"\b(pg_sleep|sleep\s*\(|waitfor\s+delay|benchmark\s*\(|dbms_pipe\.receive_message)\b",
    re.IGNORECASE,
)
RE_UNION = re.compile(r"\bUNION\s+(ALL\s+)?SELECT\b", re.IGNORECASE)
RE_BOOLEAN = re.compile(
    r"(\bOR\b|\bAND\b)\s+[\w'\"(].*?(=|LIKE|IS\s+NULL|<>|!=)",
    re.IGNORECASE,
)
RE_TAUTOLOGY = re.compile(
    r"(\bOR\b|\bAND\b)\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?",
    re.IGNORECASE,
)
RE_ERROR_BASED = re.compile(
    r"\b(extractvalue|updatexml|exp\s*\(|floor\s*\(|rand\s*\(|convert\s*\(|"
    r"utl_inaddr|dbms_utility|xmltype|ctxsys|ordsys)\b",
    re.IGNORECASE,
)
RE_SQL_ANY = re.compile(
    r"\b(SELECT|UNION|FROM|WHERE|INSERT|UPDATE|DELETE|DROP|EXEC|ALTER|CREATE)\b",
    re.IGNORECASE,
)
RE_COMMENT = re.compile(r"(--|#\s*$|/\*)", re.MULTILINE)
RE_QUOTE = re.compile(r"['\"]")

# DB hint patterns
RE_DB_MYSQL     = re.compile(r"\b(sleep\s*\(|information_schema|@@version|mysql\.|load_file|into\s+outfile)\b", re.IGNORECASE)
RE_DB_POSTGRES  = re.compile(r"\b(pg_sleep|pg_|::text|::int|array_to_string|current_setting)\b", re.IGNORECASE)
RE_DB_MSSQL     = re.compile(r"\b(waitfor\s+delay|xp_cmdshell|sysobjects|syscolumns|@@servername|nchar)\b", re.IGNORECASE)
RE_DB_ORACLE    = re.compile(r"\b(utl_inaddr|dbms_pipe|sys\.all_tables|dual|rownum|substr)\b", re.IGNORECASE)
RE_DB_SQLITE    = re.compile(r"\b(sqlite_master|sqlite_version|randomblob)\b", re.IGNORECASE)

# Syntax validity hints
RE_UNMATCHED_QUOTE = re.compile(r"(?<!')'(?!')|(?<!\\)\"")

PLACEHOLDER_RE = re.compile(r"__[A-Z_]+__")


def detect_technique(payload: str) -> tuple[str, str]:
    """Returns (technique_primary, confidence_basic)."""
    if not payload or not isinstance(payload, str):
        return "unknown", "low"

    p = payload

    if RE_TIME_BLIND.search(p):
        return "time_blind", "high"
    if RE_UNION.search(p):
        return "union_based", "high"
    if RE_ERROR_BASED.search(p):
        return "error_based", "high"

    # boolean blind: tautology patterns
    if RE_TAUTOLOGY.search(p):
        confidence = "high" if RE_COMMENT.search(p) else "medium"
        return "boolean_blind", confidence

    if RE_BOOLEAN.search(p) and RE_SQL_ANY.search(p):
        return "boolean_blind", "medium"

    if RE_SQL_ANY.search(p):
        return "generic_sqli", "medium"

    # Check for placeholder-only (delex input from D lane)
    if PLACEHOLDER_RE.search(p) and not RE_SQL_ANY.search(p):
        return "generic_sqli", "low"

    return "benign", "low"


def detect_db_hint(payload: str) -> str:
    if not isinstance(payload, str):
        return "unknown"
    hints = []
    if RE_DB_MYSQL.search(payload):    hints.append("mysql")
    if RE_DB_POSTGRES.search(payload): hints.append("postgres")
    if RE_DB_MSSQL.search(payload):    hints.append("mssql")
    if RE_DB_ORACLE.search(payload):   hints.append("oracle")
    if RE_DB_SQLITE.search(payload):   hints.append("sqlite")

    if len(hints) == 1:
        return hints[0]
    if len(hints) > 1:
        return hints[0]  # most specific hit (first match wins)
    return "unknown"


def detect_syntax_validity(payload: str) -> str:
    if not isinstance(payload, str) or len(payload) < 2:
        return "invalid"

    # Use working payload; if has SQL structure and balanced quotes → valid
    has_sql = bool(RE_SQL_ANY.search(payload))

    # Count unescaped quotes
    single_q = payload.count("'")
    double_q = payload.count('"')

    # Balanced quotes (even count) + SQL keyword → valid
    if has_sql and (single_q % 2 == 0) and (double_q % 2 == 0):
        return "valid"
    # Has SQL but unbalanced quotes → partial (intentional for injection)
    if has_sql:
        return "partial"
    # No SQL at all
    if len(payload.strip()) < 3:
        return "invalid"
    return "partial"


def label_row(row: pd.Series) -> dict:
    payload = row.get("payload_working", row.get("payload_input", ""))
    if not isinstance(payload, str):
        payload = ""

    technique, confidence = detect_technique(payload)
    is_sqli = technique != "benign"
    db_hint = detect_db_hint(payload)
    syntax_validity = detect_syntax_validity(payload)

    return {
        "is_sqli": is_sqli,
        "technique_primary": technique,
        "db_hint": db_hint,
        "syntax_validity": syntax_validity,
        "confidence_basic": confidence,
    }


def main():
    print("Phase 02 — Labeling")
    print(f"Source: {SRC}")

    df = pd.read_parquet(SRC)
    print(f"Loaded: {len(df):,} rows")

    print("Applying rule-based labels...")
    labels = df.apply(label_row, axis=1, result_type="expand")
    df = pd.concat([df, labels], axis=1)

    df.to_parquet(OUT, index=False)
    print(f"Saved: {OUT}")

    print("\n-- technique_primary distribution --")
    print(df["technique_primary"].value_counts().to_string())
    print("\n-- db_hint distribution --")
    print(df["db_hint"].value_counts().to_string())
    print("\n-- syntax_validity distribution --")
    print(df["syntax_validity"].value_counts().to_string())
    print("\n-- is_sqli --")
    print(df["is_sqli"].value_counts().to_string())


if __name__ == "__main__":
    main()
