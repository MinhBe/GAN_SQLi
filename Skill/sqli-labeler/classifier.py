import re
from dataclasses import dataclass

from shared.taxonomy import SQLI_TYPES, TYPE_PRIORITY
from shared.patterns import DB_SIGNATURES, SIGNAL_PATTERNS


@dataclass
class ClassifyResult:
    sqli_type: str
    db_engine: str
    confidence: float
    reasoning: str


def detect_db(payload: str) -> str:
    for db, signatures in DB_SIGNATURES.items():
        for sig in signatures:
            if sig.search(payload):
                return db
    return "generic"


def _count_signals(payload: str, sqli_type: str) -> int:
    patterns = SIGNAL_PATTERNS.get(sqli_type, [])
    return sum(1 for p in patterns if p.search(payload))


def assign_confidence(payload: str, sqli_type: str, db_engine: str) -> float:
    signal_count = _count_signals(payload, sqli_type)
    payload_len = len(payload)

    if signal_count >= 2:
        return 0.95
    if signal_count == 1:
        if payload_len < 20:
            return 0.85
        return 0.95
    if sqli_type == "benign":
        if payload_len < 10:
            return 0.70
        if any(kw in payload.lower() for kw in ["select", "insert", "update", "delete", "from", "where"]):
            return 0.80
        return 0.75
    if sqli_type == "unknown":
        return 0.50
    return 0.70


def generate_reasoning(payload: str, sqli_type: str, db_engine: str) -> str:
    patterns = SIGNAL_PATTERNS.get(sqli_type, [])
    signals_found = []
    for p in patterns:
        m = p.search(payload)
        if m:
            signals_found.append(m.group())

    if signals_found:
        signals_str = ", ".join(signals_found[:3])
        if sqli_type == "time_blind":
            return (f"{signals_str} is {'PostgreSQL' if 'pg_sleep' in payload.lower() else 'MySQL' if 'sleep' in payload.lower() else 'MSSQL' if 'waitfor' in payload.lower() else 'SQLite' if 'randomblob' in payload.lower() else 'database'}-specific time-delay function — time-based blind inference (priority {TYPE_PRIORITY.get(sqli_type, '?')})")
        if sqli_type == "auth_bypass":
            return f"{signals_str} with admin prefix — auth bypass pattern (priority {TYPE_PRIORITY.get(sqli_type, '?')})"
        return f"{signals_str} detected — {sqli_type} injection (priority {TYPE_PRIORITY.get(sqli_type, '?')}) on {db_engine}"

    if sqli_type == "benign":
        return f"No attack signals detected in payload — classified as benign"
    if sqli_type == "unknown":
        return f"Insufficient information to classify payload"
    return f"Classified as {sqli_type} based on payload analysis"


def is_likely_sql(payload: str) -> bool:
    sql_keywords = [
        "select", "insert", "update", "delete", "drop", "create", "alter",
        "exec", "execute", "union", "from", "where", "having", "group",
        "order by", "join", "into", "values", "set", "and", "or", "not",
        "null", "like", "in", "between", "exists", "as", "on", "union",
        "sleep", "waitfor", "benchmark", "extractvalue", "updatexml",
    ]
    payload_lower = payload.lower()
    return any(kw in payload_lower for kw in sql_keywords)


def classify(payload_norm: str) -> ClassifyResult | None:
    for sqli_type in SQLI_TYPES:
        patterns = SIGNAL_PATTERNS.get(sqli_type.name, [])
        for pattern in patterns:
            if pattern.search(payload_norm):
                db_engine = detect_db(payload_norm)
                confidence = assign_confidence(payload_norm, sqli_type.name, db_engine)
                reasoning = generate_reasoning(payload_norm, sqli_type.name, db_engine)
                return ClassifyResult(sqli_type.name, db_engine, confidence, reasoning)

    if is_likely_sql(payload_norm):
        return ClassifyResult("benign", "generic", 0.80,
                              "No attack signals detected in payload")

    return ClassifyResult("unknown", "unknown", 0.50,
                          "Insufficient information to classify")
