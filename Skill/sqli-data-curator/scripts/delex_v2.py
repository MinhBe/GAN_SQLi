"""delex_v2.py — De-lexicalize SQL payloads with function whitelist.

Original delex replaced ALL identifiers with __IDENT__, destroying signal:
  xmltype()       → __IDENT__   (Oracle error signal lost)
  pg_sleep()      → __IDENT__   (PostgreSQL time signal lost)
  extractvalue()  → __IDENT__   (MySQL error signal lost)

delex_v2 preserves ~30 SQLi-significant functions while still collapsing literals.

Reference: references/function_whitelist.md
"""
import re
from typing import Iterable

# Functions/identifiers preserved during delex (case-insensitive match)
WHITELIST = frozenset([
    # Time-blind
    "sleep", "pg_sleep", "waitfor", "benchmark", "dbms_pipe", "dbms_lock", "randomblob",
    # Error-based
    "xmltype", "extractvalue", "updatexml", "exp", "utl_inaddr", "ctxsys",
    # Out-of-band
    "load_file", "utl_http", "xp_dirtree", "xp_cmdshell",
    # Encoding / structural
    "chr", "char", "ord", "ascii", "hex", "unhex", "concat", "substring", "substr",
    # Boolean
    "elt", "rlike", "if", "case", "when", "then", "else", "end",
    # Casting
    "cast", "convert",
    # DB-specific identifiers
    "dual", "information_schema", "sysobjects", "sysdatabases", "sqlite_master",
    "all_tables", "rdb$fields", "rdb$types", "rdb$collations", "rdb$functions",
    "mysql.user",
])

# SQL keywords preserved (case-insensitive)
SQL_KEYWORDS = frozenset([
    "select", "from", "where", "and", "or", "not", "union", "all", "null", "is",
    "in", "exists", "between", "like", "as", "on", "join", "inner", "left", "right",
    "outer", "group", "by", "having", "order", "asc", "desc", "limit", "offset",
    "insert", "into", "values", "update", "set", "delete", "create", "table",
    "index", "drop", "alter", "add", "column", "primary", "key", "foreign",
    "references", "exec", "execute", "call", "true", "false",
])

# Regex patterns (order matters: more specific first)
RE_QUOTED_STR = re.compile(r"'((?:[^'\\]|\\.)*)'|\"((?:[^\"\\]|\\.)*)\"")
RE_HEX = re.compile(r"\b0x[0-9a-fA-F]+\b")
RE_FLOAT = re.compile(r"\b\d+\.\d+\b")
RE_TIME_INTERVAL = re.compile(r"'?\d+:\d+(?::\d+)?'?")  # WAITFOR DELAY format
RE_INT = re.compile(r"\b\d+\b")
RE_IDENT = re.compile(r"\b[A-Za-z_][A-Za-z_0-9]*\b")
RE_DOLLAR_IDENT = re.compile(r"\b[A-Za-z_][A-Za-z_0-9]*\$[A-Za-z_0-9]*\b")  # rdb$fields
RE_DOT_IDENT = re.compile(r"\b([A-Za-z_]\w*)\.([A-Za-z_]\w*)\b")  # sys.all_tables
RE_WS = re.compile(r"\s+")


_SQL_SIGNAL_PAT = re.compile(
    r"\b(" + "|".join(re.escape(w) for w in WHITELIST) + r")\b", re.IGNORECASE
)


def _replace_strings(text: str) -> str:
    """Replace 'foo' or "foo" with __STR__.

    Exception: if the string CONTENT contains a whitelisted SQL function
    (xmltype, pg_sleep, etc.), unwrap the string instead of replacing.
    Many SQLi payloads embed attacks inside outer quotes — those quotes are
    not SQL strings, they're injection scaffolding.
    """
    def repl(match):
        content = match.group(1) if match.group(1) is not None else match.group(2)
        if content and _SQL_SIGNAL_PAT.search(content):
            # Content has SQL signal → unwrap (let later passes delex inside)
            return f" {content} "
        return "__STR__"
    return RE_QUOTED_STR.sub(repl, text)


def _replace_time_intervals(text: str) -> str:
    """Replace MSSQL-style WAITFOR time intervals like '0:0:5' with __TIME__."""
    # Only match in WAITFOR context to avoid false positives
    return re.sub(
        r"(waitfor\s+delay\s+)'?\d+:\d+(?::\d+)?'?",
        r"\1__TIME__",
        text,
        flags=re.IGNORECASE,
    )


def _replace_hex(text: str) -> str:
    return RE_HEX.sub("__HEX__", text)


def _replace_float(text: str) -> str:
    return RE_FLOAT.sub("__FLOAT__", text)


def _replace_int(text: str) -> str:
    return RE_INT.sub("__INT__", text)


def _replace_dot_ident(text: str) -> str:
    """Handle `sys.all_tables`, `mysql.user`: keep if EITHER part in whitelist."""
    def repl(m):
        a, b = m.group(1).lower(), m.group(2).lower()
        full = f"{a}.{b}"
        if full in WHITELIST:
            return full
        if a in WHITELIST and b in WHITELIST:
            return f"{a} . {b}"
        if a in WHITELIST:
            return f"{a} . __IDENT__"
        if b in WHITELIST:
            return f"__IDENT__ . {b}"
        return "__IDENT__"
    return RE_DOT_IDENT.sub(repl, text)


def _replace_dollar_ident(text: str) -> str:
    """Handle Firebird-style `rdb$fields`."""
    def repl(m):
        token = m.group(0).lower()
        return token if token in WHITELIST else "__IDENT__"
    return RE_DOLLAR_IDENT.sub(repl, text)


def _replace_idents(text: str) -> str:
    """Replace plain identifiers with __IDENT__ unless in whitelist/keywords."""
    def repl(m):
        token = m.group(0).lower()
        if token in WHITELIST:
            return token
        if token in SQL_KEYWORDS:
            return token
        # Preserve special tokens already inserted
        if m.group(0).startswith("__") and m.group(0).endswith("__"):
            return m.group(0)
        return "__IDENT__"
    return RE_IDENT.sub(repl, text)


def _tokenize_separators(text: str) -> str:
    """Add spaces around operators/punctuation for clean tokenization."""
    text = re.sub(r"([()=,;])", r" \1 ", text)
    text = re.sub(r"(--|/\*|\*/|\|\||&&|!=|<=|>=|<>)", r" \1 ", text)
    # Single < > * / + - (but careful with -- comment which is already split)
    text = re.sub(r"(?<![\-])([<>*+/%])", r" \1 ", text)
    return text


def delex_v2(payload: str) -> str:
    """Apply delex with function whitelist.

    Pipeline:
      1. Tokenize separators (spaces around ops)
      2. Replace quoted strings → __STR__
      3. Replace WAITFOR time intervals → __TIME__
      4. Replace hex literals → __HEX__
      5. Replace float literals → __FLOAT__
      6. Replace integer literals → __INT__
      7. Handle dot identifiers (sys.all_tables, mysql.user)
      8. Handle dollar identifiers (rdb$fields)
      9. Replace plain identifiers → __IDENT__ (keeping whitelist + keywords)
     10. Normalize whitespace
    """
    if not isinstance(payload, str) or not payload.strip():
        return ""

    text = payload.lower().strip()
    text = _tokenize_separators(text)
    text = _replace_strings(text)
    text = _replace_time_intervals(text)
    text = _replace_hex(text)
    text = _replace_float(text)
    text = _replace_int(text)
    text = _replace_dot_ident(text)
    text = _replace_dollar_ident(text)
    text = _replace_idents(text)
    text = RE_WS.sub(" ", text).strip()
    return text


def delex_v2_batch(payloads: Iterable[str]) -> list[str]:
    return [delex_v2(p) for p in payloads]


def compute_vocab(payloads: Iterable[str]) -> dict:
    """Return token frequency dict from delexed payloads."""
    from collections import Counter
    counter: Counter = Counter()
    for p in payloads:
        counter.update(p.split())
    return dict(counter)


# ── CLI ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    import pandas as pd

    parser = argparse.ArgumentParser(description="Apply delex_v2 to CSV")
    parser.add_argument("--input", required=True, help="Input CSV with payload_norm column")
    parser.add_argument("--output", required=True, help="Output CSV")
    parser.add_argument("--col_in", default="payload_norm", help="Input column name")
    parser.add_argument("--col_out", default="payload_delex_v2", help="Output column name")
    parser.add_argument("--stats", action="store_true", help="Print vocab & collision stats")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    df[args.col_out] = df[args.col_in].fillna("").astype(str).map(delex_v2)
    df.to_csv(args.output, index=False)
    print(f"Wrote {len(df)} rows to {args.output}")

    if args.stats:
        vocab = compute_vocab(df[args.col_out])
        unique_delex = df[args.col_out].nunique()
        collision = 1 - unique_delex / len(df)
        print(f"\n=== STATS ===")
        print(f"Vocab size: {len(vocab)}")
        print(f"Unique delex_v2: {unique_delex}/{len(df)}")
        print(f"Collision rate: {collision:.2%}")
        print(f"\nTop 10 tokens:")
        for tok, cnt in sorted(vocab.items(), key=lambda x: -x[1])[:10]:
            print(f"  {tok:<25} {cnt:6d}")
