import pandas as pd
import re
from hashlib import sha1

# Taxonomy priority (lower = stronger)
TYPE_PRIORITY = {
    'auth_bypass': 2,
    'boolean_blind': 3,
    'error_based': 4,
    'heavy_query': 4,
    'time_blind': 5,
    'out_of_band': 6,
    'union_based': 7,
    'stacked_queries': 8,
    'polyglot': 9,
    'benign': 1,
    'unknown': 10,
}

# Function whitelist for delex
WHITELIST = {
    'sleep', 'pg_sleep', 'waitfor', 'benchmark', 'dbms_pipe', 'dbms_lock', 'randomblob',
    'xmltype', 'extractvalue', 'updatexml', 'exp', 'utl_inaddr', 'ctxsys',
    'load_file', 'utl_http', 'xp_dirtree', 'xp_cmdshell',
    'chr', 'char', 'ord', 'ascii', 'hex', 'unhex', 'concat', 'substring', 'substr',
    'elt', 'rlike', 'if', 'case', 'cast', 'convert',
    'dual', 'information_schema', 'sysobjects', 'sysdatabases', 'sqlite_master',
    'sys', 'all_tables', 'rdb', 'sysibm'
}

def extract_signals(payload):
    """Extract SQLi signal keywords from payload"""
    signals = []
    payload_lower = payload.lower()

    # Time-blind signals
    if re.search(r'\b(sleep|pg_sleep|waitfor|benchmark|dbms_pipe|randomblob)\s*\(', payload_lower):
        signals.append('time_function')

    # Error-based signals
    if re.search(r'\b(xmltype|extractvalue|updatexml|exp|utl_inaddr|ctxsys)\s*\(', payload_lower):
        signals.append('error_function')

    # Union-based
    if re.search(r'\bunion\s+all\s+select\b', payload_lower):
        signals.append('union_select')

    # Boolean-blind
    if re.search(r'\b(and|or)\s+\d+\s*=\s*\d+\b', payload_lower) or re.search(r'\b(and|or)\s+\d+\s*!=\s*\d+\b', payload_lower):
        signals.append('boolean_condition')
    if re.search(r'\brlike\s*\(', payload_lower):
        signals.append('rlike_condition')
    if re.search(r'\belt\s*\(', payload_lower):
        signals.append('elt_condition')

    # Stacked queries
    if re.search(r';\s*(insert|update|delete|drop|exec|create)\b', payload_lower):
        signals.append('stacked_statement')
    if re.search(r'\bxp_cmdshell\b', payload_lower):
        signals.append('xp_cmdshell')

    # Out-of-band
    if re.search(r'\b(load_file|utl_http|xp_dirtree|utl_inaddr|dbms_utility)\b', payload_lower):
        signals.append('oob_function')

    # Heavy query (DoS)
    if re.search(r'\b(generate_series|regexp_substring)\s*\(\s*[^,]*,\s*\d{7,}\b', payload_lower):
        signals.append('heavy_dos')
    if re.search(r'randomblob\s*\(\s*\d{7,}', payload_lower):
        signals.append('heavy_dos')

    return signals

def determine_sqli_type(a_type, c_type, signals, current_type):
    """Determine best sqli_type based on 3 sources + signals"""

    # If both agree
    if a_type == c_type:
        return a_type

    # If A agrees with current
    if a_type == current_type:
        confidence_boost = 0.75
        return a_type

    # If C agrees with current
    if c_type == current_type:
        confidence_boost = 0.70
        return c_type

    # Use signal to break tie
    if 'time_function' in signals and a_type == 'time_blind':
        return a_type
    if 'error_function' in signals and a_type == 'error_based':
        return a_type
    if 'union_select' in signals and a_type == 'union_based':
        return a_type
    if 'boolean_condition' in signals or 'rlike_condition' in signals or 'elt_condition' in signals:
        if a_type == 'boolean_blind':
            return a_type

    # Default to A (rule engine) priority
    return a_type

def calculate_sources_agree(type_val, a_type, c_type):
    """Calculate sources_agree: how many sources match the final label"""
    sources_count = 0
    if a_type == type_val:
        sources_count += 1
    if c_type == type_val:
        sources_count += 1
    return sources_count

def determine_confidence(type_val, a_type, c_type, signals, current_conf):
    """Calculate confidence score [0.5, 1.0]"""

    sources_agree = calculate_sources_agree(type_val, a_type, c_type)

    # 2/2 sources agree
    if sources_agree == 2:
        return 0.95

    # 1/2 sources agree but signals strong
    if sources_agree == 1:
        signal_strength = len(signals)
        if signal_strength >= 2:
            return 0.85
        else:
            return 0.75

    # No sources agree - use signals to infer
    if sources_agree == 0:
        signal_strength = len(signals)
        if signal_strength >= 2:
            return 0.65
        else:
            return 0.50

    return 0.70

def build_reasoning(type_val, signals, db_engine, a_type, c_type, payload):
    """Build detailed reasoning ≥50 chars"""

    reasoning_parts = []

    # Add signal evidence
    if 'time_function' in signals:
        # Find which time function
        match = re.search(r'\b(sleep|pg_sleep|waitfor|benchmark|dbms_pipe|randomblob)\s*\(', payload.lower())
        if match:
            func = match.group(1)
            reasoning_parts.append(f"Time function '{func}' detected → {type_val}")

    if 'error_function' in signals:
        match = re.search(r'\b(xmltype|extractvalue|updatexml|exp|utl_inaddr|ctxsys)\s*\(', payload.lower())
        if match:
            func = match.group(1)
            reasoning_parts.append(f"Error function '{func}' detected → {type_val}")

    if 'union_select' in signals:
        reasoning_parts.append("UNION SELECT pattern detected → union_based SQLi")

    if 'boolean_condition' in signals or 'rlike_condition' in signals or 'elt_condition' in signals:
        reasoning_parts.append("Boolean condition (AND/OR equality checks) → boolean_blind")

    # Add DB engine if specific
    if db_engine != 'generic':
        reasoning_parts.append(f"DB signature: {db_engine}")

    # Add source agreement
    sources_agree = calculate_sources_agree(type_val, a_type, c_type)
    if sources_agree == 2:
        reasoning_parts.append("Both Rule & Heuristic sources agree")
    elif sources_agree == 1:
        if a_type == type_val:
            reasoning_parts.append("Rule engine match (A)")
        if c_type == type_val:
            reasoning_parts.append("Heuristic engine match (C)")

    reasoning = "; ".join(reasoning_parts)
    if len(reasoning) < 50:
        reasoning = f"{reasoning}; confidence based on signal strength and source agreement"

    return reasoning[:500]  # Cap at 500 chars

def relabel_row(row):
    """Relabel single row"""

    payload = str(row['payload_inner'])
    a_type = row['a_type']
    c_type = row['c_type']
    current_type = row['sqli_type']
    current_db = row['db_engine']

    signals = extract_signals(payload)

    # Determine best type
    best_type = determine_sqli_type(a_type, c_type, signals, current_type)

    # Calculate confidence
    confidence = determine_confidence(best_type, a_type, c_type, signals, row['confidence'])

    # Calculate sources_agree
    sources_agree = calculate_sources_agree(best_type, a_type, c_type)

    # Build reasoning
    reasoning = build_reasoning(best_type, signals, current_db, a_type, c_type, payload)

    return {
        'sqli_type': best_type,
        'db_engine': current_db,  # Keep as-is from existing label
        'confidence': confidence,
        'reasoning': reasoning,
        'sources_agree': sources_agree
    }

def main():
    # Read chunk
    df = pd.read_csv("Asset/LabelData/_chunks/chunk_030.csv")

    print(f"Processing {len(df)} rows from chunk_030...")

    # Process each row
    results = []
    for idx, row in df.iterrows():
        result = relabel_row(row)
        results.append(result)
        if (idx + 1) % 50 == 0:
            print(f"  Processed {idx + 1}/{len(df)}")

    # Create output dataframe
    output_df = pd.DataFrame(results)

    # Combine with original data
    for col in output_df.columns:
        df[col] = output_df[col]

    # Select output columns
    output_cols = ['id', 'payload_inner', 'sqli_type', 'db_engine', 'confidence', 'reasoning', 'sources_agree']
    output_df_final = df[output_cols].copy()

    # Write output
    output_df_final.to_csv("Asset/LabelData/_chunks/chunk_030_labeled.csv", index=False)

    # Print stats
    print(f"\n=== LABELING STATS ===")
    print(f"Total rows: {len(output_df_final)}")
    print(f"\nTop 5 sqli_type:")
    print(output_df_final['sqli_type'].value_counts().head(5).to_string())

    print(f"\nLow confidence rows (< 0.75):")
    low_conf = output_df_final[output_df_final['confidence'] < 0.75]
    print(f"  Count: {len(low_conf)}")
    if len(low_conf) > 0:
        print(low_conf[['id', 'sqli_type', 'confidence']].head(5).to_string())

    print(f"\nShort reasoning rows (< 50 chars):")
    short_reason = output_df_final[output_df_final['reasoning'].str.len() < 50]
    print(f"  Count: {len(short_reason)}")
    if len(short_reason) > 0:
        print(short_reason[['id', 'sqli_type', 'reasoning']].head(3).to_string())

    print(f"\nsources_agree distribution:")
    print(output_df_final['sources_agree'].value_counts().sort_index().to_string())

    print(f"\nOutput written to: Asset/LabelData/_chunks/chunk_030_labeled.csv")

if __name__ == '__main__':
    main()
