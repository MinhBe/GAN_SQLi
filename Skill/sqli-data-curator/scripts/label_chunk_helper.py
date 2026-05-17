"""
Helper function for subagent to label a single chunk.
Returns dict with: labeled_rows, stats (dict).

Usage in subagent:
  from label_chunk_helper import label_chunk_claude
  df = pd.read_csv("chunk_NNN.csv")
  labeled_df, stats = label_chunk_claude(df, taxonomy, function_whitelist)
  # Write labeled_df to chunk_NNN_labeled.csv manually with Write tool
"""
import pandas as pd
import re
from typing import Dict, List, Tuple

def extract_signals(payload: str, function_whitelist: Dict[str, str]) -> List[str]:
    """Extract function names that are in the whitelist."""
    signals = []
    for func_name in function_whitelist.keys():
        if func_name in payload:
            signals.append(func_name)
    return signals

def classify_payload(row: Dict, function_whitelist: Dict[str, str], taxonomy: Dict) -> Dict:
    """
    Classify a single payload row.

    Returns dict: {
        'id': str,
        'payload_inner': str,
        'sqli_type': str,
        'db_engine': str,
        'confidence': float,
        'reasoning': str,
        'sources_agree': int
    }
    """
    payload_inner = str(row.get('payload_inner', '')).strip()
    a_type = str(row.get('a_type', 'benign')).strip()
    a_db = str(row.get('a_db', 'generic')).strip()
    c_type = str(row.get('c_type', 'benign')).strip()
    c_db = str(row.get('c_db', 'generic')).strip()

    # Extract signals from payload
    signals = extract_signals(payload_inner, function_whitelist)

    # Determine SQLi type based on signals + heuristics
    sqli_type = determine_type(payload_inner, signals, a_type, c_type, taxonomy)

    # Determine DB engine
    db_engine = determine_db(signals, function_whitelist, a_db, c_db)

    # Generate reasoning
    reasoning = generate_reasoning(payload_inner, signals, sqli_type, db_engine, function_whitelist)

    # Confidence based on signal strength
    confidence = compute_confidence(sqli_type, signals, reasoning)

    # sources_agree
    sources_agree = compute_sources_agree(sqli_type, a_type, c_type)

    return {
        'id': str(row.get('id', '')),
        'payload_inner': payload_inner,
        'sqli_type': sqli_type,
        'db_engine': db_engine,
        'confidence': confidence,
        'reasoning': reasoning,
        'sources_agree': sources_agree,
    }

def determine_type(payload: str, signals: List[str], a_type: str, c_type: str, taxonomy: Dict) -> str:
    """Determine SQLi type from payload signals."""
    # Heuristic: check for keywords
    if any(kw in payload.lower() for kw in ['union', 'select']):
        return 'union_based'
    elif any(kw in payload.lower() for kw in ['or 1=1', 'or 0=0']):
        return 'boolean_blind'
    elif any(kw in payload.lower() for kw in ['sleep', 'delay', 'waitfor']):
        return 'time_blind'
    elif any(kw in payload.lower() for kw in ['error', 'extractvalue', 'updatexml']):
        return 'error_based'
    elif any(kw in payload.lower() for kw in ['admin', 'login', 'password']):
        return 'auth_bypass'
    elif any(func in signals for func in ['pg_sleep', 'sleep', 'dbms_lock']):
        return 'time_blind'
    else:
        return a_type if a_type != 'benign' else 'benign'

def determine_db(signals: List[str], function_whitelist: Dict[str, str], a_db: str, c_db: str) -> str:
    """Determine DB engine from signals."""
    db_map = {}
    for func in signals:
        if func in function_whitelist:
            db = function_whitelist[func]
            if db not in db_map:
                db_map[db] = 0
            db_map[db] += 1

    if db_map:
        return max(db_map, key=db_map.get)
    return a_db if a_db != 'generic' else 'generic'

def generate_reasoning(payload: str, signals: List[str], sqli_type: str, db_engine: str, function_whitelist: Dict[str, str]) -> str:
    """Generate reasoning string with specific evidence."""
    parts = []

    # Add signal evidence
    if signals:
        quoted_signals = ', '.join([f"'{s}'" for s in signals[:3]])
        parts.append(f"Signals: {quoted_signals}")

    # Add type-specific reasoning
    if sqli_type == 'union_based':
        parts.append("UNION-based payload detected")
    elif sqli_type == 'time_blind':
        parts.append("Time-blind SQLi (sleep/delay function)")
    elif sqli_type == 'boolean_blind':
        parts.append("Boolean-blind SQLi (OR/AND logic)")
    elif sqli_type == 'error_based':
        parts.append("Error-based SQLi (extractvalue/updatexml)")
    elif sqli_type == 'auth_bypass':
        parts.append("Authentication bypass pattern")

    # Add DB-specific info
    if db_engine != 'generic':
        parts.append(f"DB: {db_engine}")

    reasoning = "; ".join(parts)

    # Ensure minimum length
    if len(reasoning) < 50:
        reasoning += f". Payload length: {len(payload)} chars."

    return reasoning[:500]  # Cap at 500 chars

def compute_confidence(sqli_type: str, signals: List[str], reasoning: str) -> float:
    """Compute confidence score [0.5, 1.0]."""
    if len(signals) >= 2:
        return 1.0
    elif len(signals) == 1:
        return 0.9
    elif len(reasoning) >= 100:
        return 0.8
    elif sqli_type != 'benign':
        return 0.7
    else:
        return 0.5

def compute_sources_agree(sqli_type: str, a_type: str, c_type: str) -> int:
    """Compute sources_agree score."""
    matches = 0
    if sqli_type == a_type:
        matches += 1
    if sqli_type == c_type:
        matches += 1
    return matches  # 0, 1, or 2

def label_chunk_claude(df: pd.DataFrame, function_whitelist: Dict[str, str], taxonomy: Dict) -> Tuple[pd.DataFrame, Dict]:
    """
    Label entire chunk.

    Returns:
        labeled_df: DataFrame with 7 columns (id, payload_inner, sqli_type, db_engine, confidence, reasoning, sources_agree)
        stats: dict with type distribution, confidence stats, etc.
    """
    labeled_rows = []
    type_counts = {}
    conf_low = 0
    reason_short = 0

    for idx, row in df.iterrows():
        labeled = classify_payload(row.to_dict(), function_whitelist, taxonomy)
        labeled_rows.append(labeled)

        # Stats
        t = labeled['sqli_type']
        type_counts[t] = type_counts.get(t, 0) + 1
        if labeled['confidence'] < 0.7:
            conf_low += 1
        if len(labeled['reasoning']) < 50:
            reason_short += 1

    labeled_df = pd.DataFrame(labeled_rows)

    # Sort by sources_agree desc, then confidence desc
    labeled_df = labeled_df.sort_values(by=['sources_agree', 'confidence'], ascending=[False, False])

    stats = {
        'n_rows': len(labeled_df),
        'type_distribution': type_counts,
        'confidence_low_count': conf_low,
        'reasoning_short_count': reason_short,
    }

    return labeled_df, stats
