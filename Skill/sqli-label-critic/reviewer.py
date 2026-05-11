from dataclasses import dataclass

from shared.taxonomy import SQLI_TYPES, VALID_TYPES, VALID_DB, TYPE_PRIORITY, NORMALIZE_MAP, REQUIRED_REVIEW
from shared.patterns import SIGNAL_PATTERNS, GENERIC_REASONING


@dataclass
class VerdictResult:
    check: str
    verdict: str
    evidence: str
    correction: dict | None = None


def check_c1_type_in_taxonomy(row: dict) -> VerdictResult:
    sqli_type = row.get("sqli_type", "").strip()
    if sqli_type in REQUIRED_REVIEW:
        return VerdictResult("C1", "FLAG",
            f"Out-of-taxonomy type '{sqli_type}' needs review to map to correct type")
    if sqli_type in NORMALIZE_MAP:
        return VerdictResult("C1", "REJECT",
            f"Type '{sqli_type}' needs normalize -> '{NORMALIZE_MAP[sqli_type]}'",
            correction={"sqli_type": NORMALIZE_MAP[sqli_type]})
    if sqli_type not in VALID_TYPES:
        return VerdictResult("C1", "REJECT",
            f"Unknown type '{sqli_type}' — not in 14-category taxonomy")
    return VerdictResult("C1", "PASS", f"Type '{sqli_type}' is valid")


def check_c2_db_in_taxonomy(row: dict) -> VerdictResult:
    db = row.get("db_engine", "").strip()
    if db not in VALID_DB:
        return VerdictResult("C2", "FLAG",
            f"Unknown DB engine '{db}' — not in 9-category taxonomy")
    return VerdictResult("C2", "PASS", f"DB engine '{db}' is valid")


def check_c3_signal_in_payload(row: dict) -> VerdictResult:
    sqli_type = row.get("sqli_type", "").strip()
    payload = row.get("payload_norm", "")
    patterns = SIGNAL_PATTERNS.get(sqli_type, [])
    if not patterns:
        return VerdictResult("C3", "PASS",
            f"Type '{sqli_type}' has no specific signal requirement")
    for pattern in patterns:
        if pattern.search(payload):
            return VerdictResult("C3", "PASS",
                f"Signal confirmed: {pattern.pattern}")
    return VerdictResult("C3", "REJECT",
        f"Signal absent: no {sqli_type} signal found in payload",
        correction={"action": "re-label"})


def check_c4_priority_conflict(row: dict) -> VerdictResult:
    current_type = row.get("sqli_type", "").strip()
    current = TYPE_PRIORITY.get(current_type, 99)
    payload = row.get("payload_norm", "")
    for sqli_type in SQLI_TYPES:
        if sqli_type.priority >= current:
            continue
        for pattern in SIGNAL_PATTERNS.get(sqli_type.name, []):
            if pattern.search(payload):
                return VerdictResult("C4", "REJECT",
                    f"Priority conflict: {sqli_type.name} (P{sqli_type.priority}) "
                    f"found but labeled {current_type} (P{current})",
                    correction={"sqli_type": sqli_type.name})
    return VerdictResult("C4", "PASS", "No priority conflict detected")


def check_c5_reasoning_quality(row: dict) -> VerdictResult:
    reasoning = row.get("reasoning", "").strip()
    issues = []
    if len(reasoning) < 30:
        issues.append(f"Only {len(reasoning)} chars (need >= 30)")
    if reasoning.lower() in GENERIC_REASONING:
        issues.append(f"Generic phrase: '{reasoning}'")
    if not reasoning:
        issues.append("Empty reasoning")
    if issues:
        return VerdictResult("C5", "FLAG",
            f"Reasoning quality: {'; '.join(issues)}")
    return VerdictResult("C5", "PASS", f"Reasoning OK ({len(reasoning)} chars)")


BASIC_CHECKS = [check_c1_type_in_taxonomy, check_c2_db_in_taxonomy,
                check_c3_signal_in_payload, check_c4_priority_conflict,
                check_c5_reasoning_quality]


def run_basic_checks(row: dict) -> tuple[str, list[VerdictResult]]:
    results = []
    for check_fn in BASIC_CHECKS:
        result = check_fn(row)
        results.append(result)
        if result.verdict == "REJECT":
            return "REJECT", results
    if any(r.verdict == "FLAG" for r in results):
        return "FLAG", results
    return "PASS", results
