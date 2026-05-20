"""
consistency_rules.py -- DB x Type consistency rules.

Rules:
1. Impossible combinations → adjust sqli_type or engine
2. Oracle-specific type inference
3. Confidence adjustment for weakly-supported combinations
"""

# (sqli_type, db_engine) → impossible (confidence * penalty or forced type change)
# penalty=0.0 means "impossible, change engine to unknown"
# penalty=0.5 means "very unlikely, halve confidence"
_IMPOSSIBLE = {
    ('time_blind',   'sqlite'):   ('time_blind',   'unknown', 0.0),  # SQLite has no SLEEP()
    ('error_based',  'sqlite'):   ('error_based',  'unknown', 0.5),  # SQLite error injection limited
    ('time_blind',   'oracle'):   ('time_blind',   'oracle',  0.5),  # Oracle time-blind via dbms_pipe only
}

# Oracle-specific: if db=oracle and type is ambiguous → prefer error_based
_ORACLE_TYPE_INFER = {
    None:         'error_based',   # unknown type + oracle → error_based
    'union_based': 'union_based',  # oracle can do union, keep it
    'boolean_blind': 'boolean_blind',  # oracle can do boolean, keep it
    'time_blind': 'time_blind',    # keep but flag (rare in Oracle, needs dbms_pipe)
    'error_based': 'error_based',  # keep
}


def apply_consistency(sqli_type: str, db_engine: str, confidence: float) -> tuple:
    """
    Apply DB×Type consistency rules.

    Returns:
        (sqli_type, db_engine, confidence) — possibly adjusted
    """
    if sqli_type is None or db_engine is None:
        # Oracle inference: if engine is oracle and type is unknown
        if db_engine == 'oracle' and sqli_type is None:
            return ('error_based', 'oracle', round(confidence * 0.65, 4))
        return (sqli_type, db_engine, confidence)

    key = (sqli_type, db_engine)
    if key in _IMPOSSIBLE:
        new_type, new_engine, penalty = _IMPOSSIBLE[key]
        if penalty == 0.0:
            return (new_type, new_engine, 0.0)
        return (new_type, new_engine, round(confidence * penalty, 4))

    return (sqli_type, db_engine, confidence)


def infer_type_from_engine(db_engine: str, current_type: str, confidence: float) -> tuple:
    """
    If db_engine is strongly detected but sqli_type is weak/None, infer type.

    Returns:
        (sqli_type, confidence) — inferred or unchanged
    """
    if db_engine == 'oracle' and (current_type is None or confidence < 0.60):
        return ('error_based', round(max(confidence, 0.55), 4))

    if db_engine == 'mssql' and current_type is None:
        return ('time_blind', round(max(confidence, 0.52), 4))  # MSSQL → likely waitfor

    if db_engine == 'postgres' and current_type is None:
        return ('time_blind', round(max(confidence, 0.52), 4))  # Postgres → likely pg_sleep

    return (current_type, confidence)


def needs_ai_by_cell(sqli_type: str, db_engine: str, cell_counts: dict,
                     sparse_threshold: int = 20) -> bool:
    """
    True if this type×engine cell is sparse and needs AI enrichment.

    Args:
        cell_counts: {(sqli_type, db_engine): count}
        sparse_threshold: route to AI if cell count below this
    """
    count = cell_counts.get((sqli_type, db_engine), 0)
    return count < sparse_threshold
