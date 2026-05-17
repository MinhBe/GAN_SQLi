import re
from reviewer import VerdictResult
from shared.taxonomy import SQLI_TYPES, TYPE_PRIORITY
from shared.patterns import SIGNAL_PATTERNS, HISTORICAL_FINGERPRINTS, DB_EXCLUSIVE_FUNCTIONS


def estimate_signal_strength(payload: str, sqli_type: str) -> str:
    patterns = SIGNAL_PATTERNS.get(sqli_type, [])
    if not patterns:
        return "NO_SIGNAL"
    match_count = sum(1 for p in patterns if p.search(payload))
    if match_count >= 2:
        return "HIGH_SIGNAL"
    if match_count == 1:
        if len(payload) < 20:
            return "MEDIUM_SIGNAL"
        return "HIGH_SIGNAL"
    return "NO_SIGNAL"


def check_c6_confidence_calibration(row: dict) -> VerdictResult | None:
    payload = row.get("payload_norm", "")
    sqli_type = row.get("sqli_type", "").strip()
    try:
        confidence = float(row.get("confidence", 0))
    except (ValueError, TypeError):
        return None

    strength = estimate_signal_strength(payload, sqli_type)

    if strength == "HIGH_SIGNAL" and confidence < 0.70:
        return VerdictResult("C6", "FLAG",
            f"Confidence {confidence} too low. Signal {sqli_type} is clear -> should be 0.90-0.95")
    if strength == "NO_SIGNAL" and confidence > 0.80 and sqli_type not in {"benign", "unknown"}:
        return VerdictResult("C6", "REJECT",
            f"Confidence {confidence} too high. Payload has no {sqli_type} signal",
            correction={"action": "re-label or reduce confidence"})

    if sqli_type in {"auth_bypass", "boolean_blind"}:
        has_admin = bool(re.search(r"admin", payload, re.I))
        has_or_and = bool(re.search(r"(and|or)\s+['\"]?1['\"]?\s*=", payload, re.I))
        if has_admin and has_or_and and confidence > 0.85:
            return VerdictResult("C6", "FLAG",
                f"Ambiguous case: admin prefix + bool pattern. Confidence {confidence} may be too high; "
                f"should be 0.70-0.80 unless context confirmed")

    if sqli_type == "benign" and confidence > 0.90:
        payload_lower = payload.lower()
        has_any_keyword = any(
            kw in payload_lower for kw in
            ["select", "union", "insert", "drop", "exec", "or 1=1", "and 1=1"]
        )
        if has_any_keyword:
            return VerdictResult("C6", "FLAG",
                f"Confidence {confidence} high but payload contains SQL keywords. "
                f"Verify benign label")

    return None


def _is_sql_like(payload: str) -> bool:
    lower = payload.lower()
    sql_keywords = ["select", "insert", "update", "delete", "drop", "create",
                    "alter", "exec", "union", "from", "where", "having",
                    "group", "order", "join", "into", "values", "set",
                    "and ", "or ", "not ", "null", "like", "in(", "between",
                    "exists", "as ", "on ", "sleep", "waitfor", "benchmark",
                    "admin", "--", "/*", "1=1", "1=2", "'a'='a'"]
    return any(kw in lower for kw in sql_keywords)


def check_c7_structural_integrity(row: dict) -> VerdictResult | None:
    payload = row.get("payload_norm", "")
    sqli_type = row.get("sqli_type", "").strip()
    issues = []

    single_quotes = sum(1 for c in payload if c == "'")
    double_quotes = sum(1 for c in payload if c == '"')
    open_paren = payload.count("(")
    close_paren = payload.count(")")

    if single_quotes % 2 != 0:
        issues.append(f"unbalanced single quotes ({single_quotes})")
    if double_quotes % 2 != 0:
        issues.append(f"unbalanced double quotes ({double_quotes})")
    if open_paren != close_paren:
        issues.append(f"parentheses mismatch ({open_paren} open, {close_paren} close)")

    double_encoding = re.search(r"(%25)+[0-9a-fA-F]{2}", payload)
    if double_encoding:
        issues.append(f"double URL-encoding detected ({double_encoding.group()})")

    if not issues:
        return None

    # Benign text with apostrophes (names, addresses) -> skip structural check
    if sqli_type == "benign" and not _is_sql_like(payload):
        return None

    if sqli_type == "benign":
        has_attack = any(kw in payload.lower() for kw in
                        ["or 1=1", "and 1=1", "union", "admin'", "sleep",
                         "drop ", "exec ", "insert ", "--", "/*",
                         "xp_", "pg_sleep", "waitfor", "benchmark",
                         "extractvalue", "updatexml"])
        if has_attack:
            return VerdictResult("C7", "REJECT",
                f"Structural issue: {'; '.join(issues)}. "
                f"Plus attack signal detected -> benign label wrong")

    return VerdictResult("C7", "FLAG",
        f"Structural issue: {'; '.join(issues)}. "
        f"Payload syntax not complete, confidence may need adjustment")


def check_c9_cross_type_consistency(row: dict) -> VerdictResult | None:
    """C9: Nếu payload có signals của type khác mạnh hơn type đang label → FLAG/REJECT.

    Mục tiêu: giảm dataset bias (88.6% Oracle XMLTYPE/users-accounts table) bằng cách
    phát hiện các payload bị gán sai type do labeler bỏ sót signal ưu tiên cao hơn.
    """
    payload = row.get("payload_norm", "").lower()
    sqli_type = row.get("sqli_type", "").strip()
    current_priority = TYPE_PRIORITY.get(sqli_type, 99)

    # Map type → detector patterns (cụ thể, ít false positive)
    CROSS_TYPE_SIGNALS: dict[str, list] = {
        "time_blind": [
            re.compile(r"\bsleep\s*\(", re.I),
            re.compile(r"\bpg_sleep\s*\(", re.I),
            re.compile(r"\bwaitfor\s+delay\b", re.I),
            re.compile(r"\bbenchmark\s*\(", re.I),
        ],
        "error_based": [
            re.compile(r"\bextractvalue\s*\(", re.I),
            re.compile(r"\bupdatexml\s*\(", re.I),
            re.compile(r"\bexp\s*\(\s*~", re.I),
        ],
        "out_of_band": [
            re.compile(r"\bload_file\s*\(", re.I),
            re.compile(r"\butl_http\b", re.I),
            re.compile(r"\butl_inaddr\b", re.I),
            re.compile(r"\bxp_dirtree\b", re.I),
        ],
        "stacked_queries": [
            re.compile(r"\bxp_cmdshell\b", re.I),
            re.compile(r";\s*(drop|insert|update|exec)\b", re.I),
        ],
        "union_based": [
            re.compile(r"\bunion\s+(all\s+)?select\b", re.I),
        ],
    }

    conflicts = []
    for other_type, patterns in CROSS_TYPE_SIGNALS.items():
        if other_type == sqli_type:
            continue
        other_priority = TYPE_PRIORITY.get(other_type, 99)
        if other_priority >= current_priority:
            continue  # other type bằng hoặc thấp hơn priority → không conflict
        for pat in patterns:
            if pat.search(payload):
                conflicts.append((other_type, other_priority, pat.pattern))
                break  # 1 pattern đủ để flag type này

    if not conflicts:
        return None

    best_conflict = min(conflicts, key=lambda x: x[1])
    other_type, other_priority, evidence = best_conflict

    if other_priority < current_priority - 1:
        return VerdictResult(
            "C9", "REJECT",
            f"Cross-type conflict: signal '{evidence}' matches {other_type} "
            f"(P{other_priority}) which overrides labeled {sqli_type} (P{current_priority})",
            correction={"sqli_type": other_type},
        )
    return VerdictResult(
        "C9", "FLAG",
        f"Cross-type ambiguity: signal '{evidence}' matches {other_type} "
        f"(P{other_priority}) — verify whether {sqli_type} (P{current_priority}) is correct",
    )


def check_c8_historical_consistency(row: dict) -> VerdictResult | None:
    payload = row.get("payload_norm", "").lower()
    sqli_type = row.get("sqli_type", "").strip()
    db_engine = row.get("db_engine", "").strip()

    for func, expected_db in DB_EXCLUSIVE_FUNCTIONS.items():
        if func in payload and db_engine != expected_db:
            return VerdictResult("C8", "REJECT",
                f"Historical DB mismatch: '{func}' is {expected_db}-exclusive, "
                f"but db_engine={db_engine}",
                correction={"db_engine": expected_db})

    for fp_name, patterns in HISTORICAL_FINGERPRINTS.items():
        for pattern in patterns:
            if pattern.search(payload):
                fp_type, fp_db = fp_name.rsplit("_", 1)
                if fp_type != sqli_type:
                    fp_priority = TYPE_PRIORITY.get(fp_type, 99)
                    current_priority = TYPE_PRIORITY.get(sqli_type, 99)
                    if fp_priority < current_priority:
                        return VerdictResult("C8", "REJECT",
                            f"Historical pattern match: {fp_name} fingerprint detected. "
                            f"Priority conflict: {fp_type} (P{fp_priority}) overrides "
                            f"{sqli_type} (P{current_priority})",
                            correction={"sqli_type": fp_type, "db_engine": fp_db})

    return None
