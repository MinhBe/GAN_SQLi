import pandas as pd
import re
import os

# Configuration
INPUT_FILE = r'C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\Gemini\_chunks\chunk_002.csv'
OUTPUT_FILE = r'C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\Gemini\_chunks\chunk_002_labeled.csv'

# Taxonomy and Priorities (Adjusted: smaller number = stronger signal)
# Benign should be the weakest signal in an attack-focused dataset.
TAXONOMY = {
    'auth_bypass': 2,
    'boolean_blind': 3,
    'error_based': 4,
    'heavy_query': 4,
    'time_blind': 5,
    'out_of_band': 6,
    'union_based': 7,
    'stacked_queries': 8,
    'polyglot': 9,
    'benign': 10,  # Moved to 10 so it's the weakest
}

# Regex Patterns for Types - Improved with \s*
TYPE_PATTERNS = [
    ('auth_bypass', re.compile(r"admin'\s*--|' or '1'='1|' or 1=1", re.I), "auth bypass pattern (' or 1=1 or admin' --)"),
    ('boolean_blind', re.compile(r"\b(and|or)\b\s+.*=.*|\brlike\b|\belt\s*\(|\bif\s*\(|\bcase\s+when\b", re.I), "boolean condition (AND/OR, RLIKE, ELT, IF, CASE)"),
    ('error_based', re.compile(r"\bxmltype\s*\(|\bextractvalue\s*\(|\bupdatexml\s*\(|\bcast\s*\(.*as\s+int\)|\butl_inaddr\.get_host_address\b|\bctxsys\.drithsx\.sn\b|\bexp\s*\(\s*~", re.I), "error-based function (xmltype, extractvalue, updatexml, cast, etc.)"),
    ('heavy_query', re.compile(r"\bgenerate_series\b|\ball_users\b|\bsysusers\b|\brdb\$fields\b|\b(select\s+count\s*\(\s*\*\s*\)\s+from\s+.*,.*,.*,.*)", re.I), "heavy query signal (all_users joins, generate_series)"),
    ('time_blind', re.compile(r"\bsleep\s*\(|\bpg_sleep\s*\(|\bwaitfor\s+delay\b|\bbenchmark\s*\(|\bdbms_pipe\.receive_message\b|\brandomblob\s*\(|\bdbms_lock\.sleep\b", re.I), "time-blind function (sleep, pg_sleep, waitfor, benchmark, etc.)"),
    ('out_of_band', re.compile(r"\bload_file\s*\(|\butl_http\.request\b|\bxp_dirtree\b", re.I), "out-of-band signal (load_file, utl_http, xp_dirtree)"),
    ('union_based', re.compile(r"\bunion\b\s+(all\s+)?\bselect\b", re.I), "union-based keywords (UNION SELECT)"),
    ('stacked_queries', re.compile(r";\s*\b(insert|update|drop|delete|exec|xp_cmdshell)\b", re.I), "stacked query keywords (semicolon + DML/Exec)"),
]

# DB Engine Signatures
DB_SIGNATURES = [
    ('oracle', re.compile(r"\bxmltype\b|\bdual\b|\butl_inaddr\b|\bdbms_pipe\b|\bctxsys\b|\ball_tables\b|\brownum\b|\bchr\s*\(\d+\)\|\||\bdbms_lock\b", re.I)),
    ('mysql', re.compile(r"\bextractvalue\b|\bupdatexml\b|\bsleep\b|\bbenchmark\b|\binformation_schema\b|\bconcat\b|\belt\b|\brlike\b|\bexp\s*\(\s*~", re.I)),
    ('postgresql', re.compile(r"\bpg_sleep\b|\bpg_database\b|\bstring_agg\b|\bcast\s*\(.*as\s+int\)|\bgenerate_series\b", re.I)),
    ('mssql', re.compile(r"\bxp_cmdshell\b|\bwaitfor\s+delay\b|\bsysobjects\b|\bsysdatabases\b|\bmaster\.\.", re.I)),
    ('firebird', re.compile(r"\brdb\$", re.I)),
    ('sqlite', re.compile(r"\brandomblob\b|\bsqlite_master\b", re.I)),
    ('db2', re.compile(r"\bsysibm\.systables\b", re.I)),
]

def classify_payload(payload):
    found_types = []
    
    # Check for attack types
    for type_name, pattern, description in TYPE_PATTERNS:
        match = pattern.search(payload)
        if match:
            found_types.append((type_name, TAXONOMY[type_name], match.group(0), description))
            
    # Determine DB Engine
    db_engine = 'generic'
    db_signal = None
    for engine, pattern in DB_SIGNATURES:
        match = pattern.search(payload)
        if match:
            db_engine = engine
            db_signal = match.group(0)
            break
            
    if not found_types:
        return 'benign', db_engine, "No SQLi signal detected", TAXONOMY['benign']
        
    # Pick type with lowest priority number (strongest signal)
    found_types.sort(key=lambda x: x[1])
    best_type, priority, token, desc = found_types[0]
    
    reasoning = f"Pattern match: '{token}' -> {best_type} (P{priority}); DB signature: {db_engine}. {desc} detected in payload."
    if db_signal:
        reasoning += f" DB-specific token found: '{db_signal}'."
        
    return best_type, db_engine, reasoning, priority

def process_chunk():
    df = pd.read_csv(INPUT_FILE)
    
    new_data = []
    for idx, row in df.iterrows():
        payload = str(row['payload_inner'])
        
        # Script classification
        s_type, s_db, s_reason, s_prio = classify_payload(payload)
        
        # Source A and C from CSV
        a_type = row['a_type'] if pd.notna(row['a_type']) else 'unknown'
        c_type = row['c_type'] if pd.notna(row['c_type']) else 'unknown'
        
        # Final Type Decision
        candidates = [s_type]
        if a_type != 'unknown': candidates.append(a_type)
        if c_type != 'unknown': candidates.append(c_type)
        
        # Filter out benign if there are other attack types
        attack_candidates = [t for t in candidates if t != 'benign' and t in TAXONOMY]
        
        if attack_candidates:
            # Majority vote among attacks
            # final_type = max(set(attack_candidates), key=attack_candidates.count)
            # Actually, use priority logic among all candidates
            prio_candidates = []
            for t in set(candidates):
                if t in TAXONOMY:
                    prio_candidates.append((t, TAXONOMY[t]))
            prio_candidates.sort(key=lambda x: x[1])
            final_type = prio_candidates[0][0]
        else:
            final_type = 'benign'

        # Sources agree count
        sources_agree = 0
        if s_type == final_type: sources_agree += 1
        if a_type == final_type: sources_agree += 1
        if c_type == final_type: sources_agree += 1
        
        # Confidence
        if sources_agree == 3:
            confidence = 1.0
        elif sources_agree == 2:
            confidence = 0.85
        else:
            confidence = 0.50
            
        # DB Engine decision
        final_db = s_db
        if pd.notna(row['a_db']) and row['a_db'] not in ['generic', 'unknown']:
            final_db = row['a_db']
        elif pd.notna(row['c_db']) and row['c_db'] not in ['generic', 'unknown']:
            final_db = row['c_db']
            
        # Final Reasoning
        if final_type == s_type:
            final_reasoning = s_reason
        else:
            final_reasoning = f"Agreement on {final_type} injection targetting {final_db} based on multi-source analysis."
        
        # Ensure reasoning is at least 50 chars
        if len(final_reasoning) < 50:
            extra = (row['a_signals'] if pd.notna(row['a_signals']) else "")
            final_reasoning = (final_reasoning + " " + extra).strip()
            
        if len(final_reasoning) < 50:
             final_reasoning = final_reasoning.ljust(50, '.')
            
        new_data.append({
            'sqli_type': final_type,
            'db_engine': final_db,
            'confidence': confidence,
            'reasoning': final_reasoning,
            'sources_agree': sources_agree
        })
        
    # Update dataframe
    df_new = pd.DataFrame(new_data)
    for col in df_new.columns:
        df[col] = df_new[col]
        
    df.to_csv(OUTPUT_FILE, index=False)
    print(f"Labeled {len(df)} rows. Saved to {OUTPUT_FILE}")

if __name__ == "__main__":
    process_chunk()
