from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable, Sequence

BOOLEAN_TOKENS = {
    "AND", "OR", "NOT", "IN", "LIKE", "ILIKE", "BETWEEN", "IS", "NULL",
    "TRUE", "FALSE", "ANY", "ALL", "EXISTS", "SIMILAR", "TO", "DISTINCT", "FROM",
    "=", "<>", "!=", ">", "<", ">=", "<=",
}
DANGEROUS_OUT_OF_SCOPE = {
    "UNION", "SELECT", "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "COPY",
    "CREATE", "TRUNCATE", "EXEC", "EXECUTE", "PG_SLEEP",
}
KEYWORD_RE = re.compile(r"[A-Za-z_]+|<>|!=|>=|<=|=|>|<")
STRING_RE = re.compile(r"'(?:''|[^'])*'")
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")


@dataclass
class StaticValidation:
    payload: str
    delimiter_valid: bool
    quote_valid: bool
    boolean_signal_valid: bool
    required_tokens_valid: bool
    dangerous_family_excluded: bool
    slot_sanity_valid: bool
    static_score: float
    final_accept: bool
    error_class: str


def strip_string_literals(s: str) -> str:
    return STRING_RE.sub("''", s)


def normalize_sqlish(s: str) -> str:
    s = re.sub(r"/\*.*?\*/", " ", s, flags=re.S)
    s = re.sub(r"--.*?$", " ", s, flags=re.M)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def tokens(s: str) -> list[str]:
    return [t.upper() for t in KEYWORD_RE.findall(strip_string_literals(s))]


def balanced_parentheses(s: str) -> bool:
    depth = 0
    in_str = False
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "'":
            if in_str and i + 1 < len(s) and s[i + 1] == "'":
                i += 2
                continue
            in_str = not in_str
        elif not in_str:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth < 0:
                    return False
        i += 1
    return depth == 0 and not in_str


def quote_valid(s: str) -> bool:
    in_str = False
    i = 0
    while i < len(s):
        if s[i] == "'":
            if in_str and i + 1 < len(s) and s[i + 1] == "'":
                i += 2
                continue
            in_str = not in_str
        i += 1
    return not in_str


def required_tokens_valid(s: str, required: str | Sequence[str] | None = None) -> bool:
    if required is None or required == "" or str(required).lower() == "nan":
        return True
    if isinstance(required, str):
        parts = [x.strip().upper() for x in re.split(r"[,| ]+", required) if x.strip()]
    else:
        parts = [str(x).upper() for x in required]
    tt = set(tokens(s))
    return all(p in tt or p in s.upper() for p in parts)


def boolean_signal_valid(s: str) -> bool:
    tt = set(tokens(s))
    # AND/OR/NOT alone is not enough; broken strings can contain connectors
    # while lacking an actual Boolean predicate. Require a predicate operator or
    # a PostgreSQL Boolean-returning construct.
    predicate_markers = {
        "=", "<>", "!=", ">", "<", ">=", "<=",
        "IN", "LIKE", "ILIKE", "BETWEEN", "IS", "EXISTS",
        "SIMILAR", "DISTINCT", "TRUE", "FALSE", "NULL", "ANY", "ALL",
    }
    return bool(tt & predicate_markers)


def dangerous_family_excluded(s: str) -> bool:
    tt = set(tokens(s))
    return not bool(tt & DANGEROUS_OUT_OF_SCOPE)


def slot_sanity_valid(s: str, max_digits: int = 9, max_length: int = 512) -> bool:
    if len(s) > max_length:
        return False
    for n in NUMBER_RE.findall(s):
        if len(n.replace(".", "")) > max_digits:
            return False
    return True


def static_validate(payload: str, required_tokens: str | Sequence[str] | None = None,
                    max_digits: int = 9, max_length: int = 512) -> StaticValidation:
    p = str(payload or "")
    checks = {
        "delimiter": balanced_parentheses(p),
        "quote": quote_valid(p),
        "boolean": boolean_signal_valid(p),
        "required": required_tokens_valid(p, required_tokens),
        "scope": dangerous_family_excluded(p),
        "slot": slot_sanity_valid(p, max_digits=max_digits, max_length=max_length),
    }
    weights = {
        "delimiter": 0.22,
        "quote": 0.12,
        "boolean": 0.18,
        "required": 0.20,
        "scope": 0.15,
        "slot": 0.13,
    }
    score = sum(weights[k] for k, ok in checks.items() if ok)
    final = score >= 0.80 and checks["delimiter"] and checks["quote"] and checks["boolean"] and checks["scope"]
    if final:
        error = "ok"
    else:
        error = "+".join(k for k, ok in checks.items() if not ok) or "low_score"
    return StaticValidation(
        payload=p,
        delimiter_valid=checks["delimiter"],
        quote_valid=checks["quote"],
        boolean_signal_valid=checks["boolean"],
        required_tokens_valid=checks["required"],
        dangerous_family_excluded=checks["scope"],
        slot_sanity_valid=checks["slot"],
        static_score=round(score, 4),
        final_accept=final,
        error_class=error,
    )


def validate_many(payloads: Iterable[str]) -> list[dict]:
    rows = []
    for i, p in enumerate(payloads):
        v = static_validate(p)
        rows.append({"index": i, **v.__dict__})
    return rows


def postgres_wrapper(payload: str) -> str:
    """Return a safe local parse/runtime wrapper for a predicate candidate.

    This string is for a private PostgreSQL sandbox only, never a live target.
    """
    return f"SELECT CASE WHEN ({payload}) THEN TRUE ELSE FALSE END;"
