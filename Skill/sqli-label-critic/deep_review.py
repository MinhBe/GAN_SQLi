import logging
from shared.taxonomy import SQLI_TYPES, TYPE_PRIORITY
from shared.patterns import SIGNAL_PATTERNS, DB_SIGNATURES
from reviewer import VerdictResult


logger = logging.getLogger("deep_review")


def deep_review(row: dict) -> list[dict]:
    payload = row.get("payload_norm", "")
    current_type = row.get("sqli_type", "").strip()

    findings = []

    all_signals_found = []
    for sqli_type in SQLI_TYPES:
        patterns = SIGNAL_PATTERNS.get(sqli_type.name, [])
        for pattern in patterns:
            m = pattern.search(payload)
            if m:
                all_signals_found.append({
                    "type": sqli_type.name,
                    "priority": sqli_type.priority,
                    "signal": m.group(),
                    "pattern": pattern.pattern,
                })

    if all_signals_found:
        findings.append(f"All signals: {', '.join(f['signal'] for f in all_signals_found[:5])}")
        min_priority = min(f["priority"] for f in all_signals_found)
        best_match = next(f for f in all_signals_found if f["priority"] == min_priority)
        findings.append(f"Highest priority signal: {best_match['type']} (P{best_match['priority']})")
        if current_type and min_priority < TYPE_PRIORITY.get(current_type, 99):
            findings.append(f"Priority conflict: {best_match['type']} overrides {current_type}")

    db_signals = []
    for db, signatures in DB_SIGNATURES.items():
        for sig in signatures:
            if sig.search(payload):
                db_signals.append(db)
                break
    if db_signals:
        findings.append(f"DB signatures detected: {', '.join(set(db_signals))}")

    full_analysis = "; ".join(findings) if findings else "No additional signals found"
    return [{
        "check": "DEEP_REVIEW",
        "verdict": "FLAG",
        "evidence": full_analysis,
        "correction": None,
    }]
