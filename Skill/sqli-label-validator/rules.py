import re
from dataclasses import dataclass

from shared.taxonomy import NORMALIZE_MAP, VALID_TYPES
from shared.patterns import DB_SIGNATURES, GENERIC_REASONING, SIGNAL_PATTERNS


DB_CONFLICT_MAP = {
    "oracle": [re.compile(r"pg_sleep", re.I), re.compile(r"randomblob", re.I)],
    "mysql":  [re.compile(r"waitfor\s+delay", re.I), re.compile(r"pg_sleep", re.I)],
    "postgresql": [re.compile(r"waitfor\s+delay", re.I), re.compile(r"randomblob", re.I)],
    "mssql": [re.compile(r"pg_sleep", re.I), re.compile(r"randomblob", re.I)],
    "sqlite": [re.compile(r"waitfor\s+delay", re.I), re.compile(r"pg_sleep", re.I)],
}


@dataclass
class Correction:
    row_index: int
    field: str
    old_value: str
    new_value: str
    rule: str
    reason: str


def check_r1(row: dict) -> Correction | None:
    old = row.get("sqli_type", "").strip()
    new = NORMALIZE_MAP.get(old)
    if new and old != new:
        return Correction(
            row_index=int(row["row_index"]),
            field="sqli_type",
            old_value=old,
            new_value=new,
            rule="R1",
            reason=f"Normalize {old} -> {new}"
        )
    return None


def check_r2(row: dict) -> Correction | None:
    sqli_type = row.get("sqli_type", "").strip()
    if sqli_type not in {"generic", "comment_based", "inline_query"}:
        return None
    payload = row.get("payload_norm", "")
    for type_name, patterns in SIGNAL_PATTERNS.items():
        for pattern in patterns:
            if pattern.search(payload):
                return Correction(
                    row_index=int(row["row_index"]),
                    field="sqli_type",
                    old_value=sqli_type,
                    new_value=type_name,
                    rule="R2",
                    reason=f"Map out-of-taxonomy '{sqli_type}' -> '{type_name}' via signal match"
                )
    return None


def check_r3(row: dict) -> Correction | None:
    old = row.get("sqli_type", "").strip()
    new = NORMALIZE_MAP.get(old)
    if new and old != new and old != "boolean_based":
        return Correction(
            row_index=int(row["row_index"]),
            field="sqli_type",
            old_value=old,
            new_value=new,
            rule="R3",
            reason=f"Fix special type '{old}' -> '{new}'"
        )
    return None


def check_r4(row: dict) -> Correction | None:
    engine = row.get("db_engine", "").strip()
    payload = row.get("payload_norm", "")

    conflicts = DB_CONFLICT_MAP.get(engine, [])
    for pattern in conflicts:
        if pattern.search(payload):
            detected_db = _detect_db_from_payload(payload)
            target = detected_db if detected_db != "unknown" else "mysql"
            return Correction(
                row_index=int(row["row_index"]),
                field="db_engine",
                old_value=engine,
                new_value=target,
                rule="R4",
                reason=f"DB conflict: {pattern.pattern} detected but db_engine={engine}. Suggest {target}"
            )

    if engine == "oracle" and re.search(r"sleep\s*\(", payload, re.I):
        return Correction(
            row_index=int(row["row_index"]),
            field="db_engine",
            old_value=engine,
            new_value="mysql",
            rule="R4",
            reason="SLEEP() is MySQL function, not Oracle"
        )
    return None


def check_r5(row: dict) -> Correction | None:
    try:
        conf = float(row.get("confidence", 0))
    except (ValueError, TypeError):
        return Correction(
            row_index=int(row["row_index"]),
            field="confidence",
            old_value=row.get("confidence", ""),
            new_value="0.50",
            rule="R5",
            reason="Invalid confidence value, clamped to 0.50"
        )
    if conf < 0.0 or conf > 1.0:
        new_conf = max(0.0, min(1.0, conf))
        return Correction(
            row_index=int(row["row_index"]),
            field="confidence",
            old_value=str(conf),
            new_value=str(new_conf),
            rule="R5",
            reason=f"Confidence {conf} out of range [0.0, 1.0], clamped to {new_conf}"
        )
    return None


def check_r6(row: dict) -> Correction | None:
    reasoning = row.get("reasoning", "").strip()
    issues = []
    if len(reasoning) < 30:
        issues.append(f"Only {len(reasoning)} chars (need >= 30)")
    if reasoning.lower() in GENERIC_REASONING:
        issues.append(f"Generic phrase: '{reasoning}'")
    if issues:
        return Correction(
            row_index=int(row["row_index"]),
            field="reasoning",
            old_value=reasoning,
            new_value="",
            rule="R6",
            reason=f"Reasoning quality: {'; '.join(issues)}"
        )
    return None


ALL_RULES = [check_r1, check_r2, check_r3, check_r4, check_r5, check_r6]


def _detect_db_from_payload(payload: str) -> str:
    for db, signatures in DB_SIGNATURES.items():
        for sig in signatures:
            if sig.search(payload):
                return db
    return "unknown"
