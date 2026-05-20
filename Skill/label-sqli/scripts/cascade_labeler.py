"""
cascade_labeler.py -- 4-Tier cascade labeler (v2).

Architecture:
  PRE  → detect payload state (raw/normalized/delex)
  T1   → exact function match           → conf 0.90-1.00  (script, ~45% of rows)
  T2   → structural patterns + sqlparse → conf 0.70-0.89  (script, ~30% of rows)
  T3   → contextual inference + rules   → conf 0.50-0.69  (script, ~10% of rows)
  T4   → benign classifier or AI route  → conf from AI    (~15-25% of rows)

Each tier returns immediately if confidence meets its threshold.
All tiers are pure Python/regex. sqlparse is used in T2 if available.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from state_detector import detect_state
from detectors_v2 import (
    tier1_score, tier2_score, detect_db_engine,
    score_benign, has_injection_context,
    detect_comment_injection, detect_case_variation, detect_encoding_obfuscation,
    is_complex_payload, normalize_payload, get_sqli_types,
)
from consistency_rules import apply_consistency, infer_type_from_engine

try:
    import sqlparse
    _HAS_SQLPARSE = True
except ImportError:
    _HAS_SQLPARSE = False

# Confidence thresholds for each tier
_THRESH_T1  = 0.85   # Tier 1: accept if >= 0.85
_THRESH_T2  = 0.70   # Tier 2: accept if >= 0.70
_THRESH_T3  = 0.50   # Tier 3: accept if >= 0.50
_THRESH_BEN = 0.60   # Benign: accept if >= 0.60

# Rows at or below this confidence are flagged low_confidence → needs_ai
_LOW_CONF_THRESHOLD = 0.69

VALID_TYPES   = {'time_blind', 'boolean_blind', 'union_based', 'error_based', 'benign'}
VALID_ENGINES = {'mysql', 'postgres', 'oracle', 'mssql', 'sqlite', 'unknown'}


# ===========================================================================
# SQLPARSE STRUCTURAL ANALYSIS (Tier 2 enhancement)
# ===========================================================================

def _sqlparse_hints(payload: str) -> dict:
    """
    Parse payload with sqlparse and return structural hints.
    Returns empty dict if sqlparse not available or parse fails.
    """
    if not _HAS_SQLPARSE:
        return {}
    try:
        import sqlparse as sp
        from sqlparse.sql import Where
        from sqlparse.tokens import Keyword, DML

        parsed = sp.parse(payload)
        if not parsed:
            return {}

        tokens = list(parsed[0].flatten())
        tvals  = [t.value.upper() for t in tokens]
        ttypes = [t.ttype for t in tokens]

        hints = {}

        # UNION SELECT → union_based
        if 'UNION' in tvals and 'SELECT' in tvals:
            ui = tvals.index('UNION')
            si = next((i for i, v in enumerate(tvals[ui:]) if v == 'SELECT'), None)
            if si is not None:
                hints['union_select'] = True

        # ORDER BY N → union probing
        for i, v in enumerate(tvals[:-1]):
            if v == 'BY' and i > 0 and tvals[i-1] == 'ORDER':
                if i+1 < len(tvals) and tvals[i+1].isdigit():
                    hints['order_by_n'] = True

        # ROWNUM → Oracle
        if 'ROWNUM' in tvals:
            hints['rownum'] = True

        # Multiple SELECTs → nested/union
        if tvals.count('SELECT') >= 2:
            hints['nested_select'] = True

        # HAVING without GROUP BY → boolean
        if 'HAVING' in tvals and 'GROUP' not in tvals:
            hints['having_no_group'] = True

        return hints
    except Exception:
        return {}


# ===========================================================================
# TIER 2 — STRUCTURAL (with optional sqlparse hints)
# ===========================================================================

def _tier2_with_sqlparse(payload: str, t2_base: dict) -> dict:
    """Enhance Tier 2 result with sqlparse hints."""
    hints = _sqlparse_hints(payload)
    if not hints:
        return t2_base

    result = dict(t2_base)
    conf   = result.get('confidence', 0.0)

    if hints.get('union_select') and result.get('sqli_type') != 'union_based':
        result['sqli_type']  = 'union_based'
        result['confidence'] = max(conf, 0.78)

    if hints.get('rownum') and result.get('sqli_type') is None:
        result['sqli_type']  = 'error_based'
        result['confidence'] = max(conf, 0.72)

    if hints.get('order_by_n') and result.get('sqli_type') is None:
        result['sqli_type']  = 'union_based'
        result['confidence'] = max(conf, 0.70)

    if hints.get('having_no_group') and result.get('sqli_type') is None:
        result['sqli_type']  = 'boolean_blind'
        result['confidence'] = max(conf, 0.70)

    if hints.get('nested_select') and conf > 0:
        result['confidence'] = min(0.89, conf + 0.03)

    return result


# ===========================================================================
# MAIN CASCADE FUNCTION
# ===========================================================================

def label_payload(payload: str) -> dict:
    """
    Run the 4-tier cascade on a single payload.

    Returns:
        {
            'sqli_type':    str | None    — attack type or 'benign'
            'db_engine':    str           — 'mysql' | 'postgres' | 'oracle' |
                                           'mssql' | 'sqlite' | 'unknown'
            'confidence':   float         — 0.0 – 1.0
            'tier':         str           — 'gold' | 'silver' | 'bronze'
            'label_source': str           — which tier labeled it
            'is_complex':   bool          — scored high in 2+ attack dimensions
            'low_confidence': bool        — True if confidence < 0.70
            'needs_ai':     bool          — True if should be sent for AI review
            'payload_state': str          — 'raw' | 'normalized' | 'delex'
            'obf_comment':  float
            'obf_case':     float
            'obf_encoding': float
        }
    """
    orig_payload = str(payload)
    payload      = normalize_payload(orig_payload)
    state   = detect_state(payload)
    db, dbc = detect_db_engine(payload)

    # --- TIER 1: Exact function match ---
    t1 = tier1_score(payload)

    # Always run Tier 2 so multi-label sqli_types captures all detected types
    t2_raw = tier2_score(payload)
    t2     = _tier2_with_sqlparse(payload, t2_raw)

    if t1['confidence'] >= _THRESH_T1 and t1['sqli_type']:
        # Prefer t1 db_hint if detector found no engine or lower confidence
        engine = t1['db_hint'] or (db if dbc > 0 else 'unknown')
        stype, engine, conf = apply_consistency(t1['sqli_type'], engine, t1['confidence'])
        return _build_result(stype, engine, conf, 'tier1_exact',
                             t1, t2, payload, state, db, dbc,
                             orig_payload=orig_payload)

    # Use best between T1 and T2 if T2 doesn't clear threshold alone
    best_t2_conf = t2.get('confidence', 0.0)
    best_t2_type = t2.get('sqli_type')

    # Also check if T1 partial + T2 partial together clear T2 threshold
    if t1['confidence'] > 0 and t1['sqli_type'] and best_t2_type == t1['sqli_type']:
        best_t2_conf = min(0.89, max(best_t2_conf, t1['confidence']))

    if best_t2_conf >= _THRESH_T2 and best_t2_type:
        engine = db if dbc > 0.30 else 'unknown'
        if not engine or engine == 'unknown':
            engine = t1.get('db_hint') or 'unknown'
        stype, engine, conf = apply_consistency(best_t2_type, engine, best_t2_conf)
        return _build_result(stype, engine, conf, 'tier2_structural',
                             t1, t2, payload, state, db, dbc,
                             orig_payload=orig_payload)

    # --- TIER 3: Contextual inference ---
    # Use highest confidence across T1+T2
    t3_type = t1['sqli_type'] or best_t2_type
    t3_conf = max(t1['confidence'], best_t2_conf)

    # Engine inference from DB detector
    engine = db if dbc > 0.40 else 'unknown'
    if not engine or engine == 'unknown':
        engine = t1.get('db_hint') or 'unknown'

    # Infer type from engine if still no type
    if t3_type is None and engine != 'unknown':
        t3_type, t3_conf = infer_type_from_engine(engine, t3_type, t3_conf)

    if t3_conf >= _THRESH_T3 and t3_type:
        stype, engine, conf = apply_consistency(t3_type, engine, t3_conf)
        return _build_result(stype, engine, conf, 'tier3_contextual',
                             t1, t2, payload, state, db, dbc,
                             needs_ai=True, orig_payload=orig_payload)

    # --- BENIGN CLASSIFIER ---
    benign_conf = score_benign(payload)
    if benign_conf >= _THRESH_BEN:
        return _build_result('benign', 'unknown', benign_conf, 'benign_classifier',
                             t1, t2, payload, state, db, dbc,
                             needs_ai=False, orig_payload=orig_payload)

    # --- TIER 4: Route to AI ---
    return _build_result(None, engine or 'unknown', 0.0, 'tier4_ai_needed',
                         t1, t2, payload, state, db, dbc,
                         needs_ai=True, orig_payload=orig_payload)


def _build_result(sqli_type, db_engine, confidence, label_source,
                  t1, t2, payload, state, db, dbc,
                  needs_ai=False, orig_payload=None) -> dict:
    """Assemble final result dict."""
    if db_engine not in VALID_ENGINES:
        db_engine = 'unknown'
    if sqli_type is not None and sqli_type not in VALID_TYPES:
        sqli_type = None

    tier = 'gold' if confidence >= 0.85 else ('silver' if confidence >= 0.70 else 'bronze')
    low_confidence = confidence < _LOW_CONF_THRESHOLD

    # Run obfuscation on ORIGINAL (pre-normalization) payload to detect encoding bypass
    obf_src      = orig_payload if orig_payload is not None else payload
    obf_comment  = detect_comment_injection(obf_src)
    obf_case     = detect_case_variation(obf_src)
    obf_encoding = detect_encoding_obfuscation(obf_src)
    max_obf      = max(obf_comment, obf_case, obf_encoding)
    is_sqli_pos  = bool(sqli_type and sqli_type != 'benign')
    complex_flag = is_complex_payload(t1, t2) or (is_sqli_pos and max_obf >= 0.60)

    return {
        'is_sqli':           1 if is_sqli_pos else 0,
        'sqli_type':         sqli_type,
        'sqli_types':        get_sqli_types(t1, t2),   # multi-label pipe-separated
        'script_sqli_type':  sqli_type,                 # preserved for AI agreement check
        'script_confidence': round(confidence, 4),      # preserved for AI agreement check
        'db_engine':         db_engine,
        'confidence':        round(confidence, 4),
        'tier':              tier,
        'label_source':      label_source,
        'is_complex':        complex_flag,
        'low_confidence':    low_confidence,
        'needs_ai':          needs_ai or (label_source == 'tier4_ai_needed'),
        'payload_state':     state,
        'db_confidence':     round(dbc, 4),
        'obf_comment':       obf_comment,
        'obf_case':          obf_case,
        'obf_encoding':      obf_encoding,
    }


# ===========================================================================
# BATCH LABELER
# ===========================================================================

def label_batch(payloads: list, progress_every: int = 50_000) -> list:
    """
    Label a list of payloads. Returns list of result dicts.
    """
    results = []
    for i, payload in enumerate(payloads):
        results.append(label_payload(str(payload)))
        if (i + 1) % progress_every == 0:
            print(f"[INFO] cascade: {i+1:,}/{len(payloads):,} rows labeled")
    return results


# ===========================================================================
# QUICK TEST
# ===========================================================================

if __name__ == '__main__':
    import io
    if hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

    tests = [
        ("admin' AND sleep(5)--",                          "time_blind+mysql"),
        ("admin ' and sleep ( __TIME__ ) --",              "time_blind delex"),
        ("' UNION SELECT NULL,NULL,NULL--",                "union_based"),
        ("' and extractvalue(1,concat(0x7e,version()))--", "error_based+mysql"),
        ("' OR '1'='1",                                    "boolean_blind"),
        ("'; WAITFOR DELAY '0:0:5'--",                     "time_blind+mssql"),
        ("' AND xmltype((select version from v$instance))--", "error_based+oracle"),
        ("' AND utl_inaddr.get_host_address('x')--",       "error_based+oracle"),
        ("__STR__ or __INT__ = __INT__ --",                "boolean_blind delex"),
        ("admin",                                           "benign"),
        ("1",                                              "benign"),
        ("__STR__",                                        "benign delex"),
        ("' ORDER BY 1--",                                 "union_based probing"),
    ]

    header = f"{'Payload':<55} {'Expected':<22} {'Type':<15} {'Eng':<10} {'Conf':<6} {'Src':<20} {'State'}"
    print(header)
    print("-" * 145)
    for payload, expected in tests:
        r = label_payload(payload)
        ai_flag = " [AI]" if r['needs_ai'] else ""
        print(f"{payload:<55} {expected:<22} {str(r['sqli_type']):<15} "
              f"{r['db_engine']:<10} {r['confidence']:<6.2f} "
              f"{r['label_source']:<20} {r['payload_state']}{ai_flag}")
