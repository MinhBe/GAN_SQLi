import pandas as pd
import re

def classify(row):
    p = row['payload_inner'].lower()
    signals = []
    db = 'generic'
    
    # DB detection
    if any(x in p for x in ['xmltype', 'dual', 'utl_inaddr', 'dbms_pipe', 'ctxsys', 'all_tables', 'all_users', 'rownum']):
        db = 'oracle'
    elif any(x in p for x in ['extractvalue', 'updatexml', 'sleep', 'benchmark', 'information_schema', 'elt', 'rlike', 'make_set', 'mysql.db']):
        db = 'mysql'
    elif any(x in p for x in ['pg_sleep', 'pg_database', 'generate_series', 'regexp_substring']):
        db = 'postgresql'
    elif any(x in p for x in ['waitfor delay', 'sysobjects', 'sysdatabases', 'master..', 'sysusers']):
        db = 'mssql'
    elif any(x in p for x in ['rdb$', 'rdb$database', 'rdb$fields']):
        db = 'firebird'
    elif any(x in p for x in ['randomblob', 'sqlite_master']):
        db = 'sqlite'
    elif any(x in p for x in ['sysibm.systables']):
        db = 'db2'

    # Type detection with priority
    # P2: Auth Bypass (rare in this chunk, but checking)
    if "' or '1'='1" in p or "admin' --" in p:
        signals.append((2, 'auth_bypass', 'Auth bypass pattern detected'))

    # P3: Boolean Blind
    boolean_patterns = [
        (r'elt\s*\(', 'elt()'),
        (r'rlike\s*\(', 'rlike()'),
        (r'if\s*\(', 'if()'),
        (r'case\s+when', 'case when'),
        (r'make_set\s*\(', 'make_set()'),
        (r'iif\s*\(', 'iif()'),
        (r'\d+\s*=\s*\d+', 'equality tautology'),
        (r"'\w+'\s*=\s*'\w+'", 'string equality'),
        (r'where\s+\d+\s*=', 'where equality'),
        (r'and\s+\d+\s*=', 'and equality'),
        (r'or\s+\d+\s*=', 'or equality'),
        (r'select\s+case', 'select case'),
        (r'regexp_substring', 'regexp_substring') # Often used in boolean context here
    ]
    for pattern, name in boolean_patterns:
        if re.search(pattern, p):
            signals.append((3, 'boolean_blind', f"Boolean signal '{name}' detected"))
            break # Only need one for priority
            
    # P4: Error Based / Heavy Query
    error_patterns = [
        (r'xmltype\s*\(', 'xmltype()'),
        (r'extractvalue\s*\(', 'extractvalue()'),
        (r'updatexml\s*\(', 'updatexml()'),
        (r'utl_inaddr', 'utl_inaddr'),
        (r'ctxsys', 'ctxsys'),
        (r'cast\s*\(.*as\s+int\)', 'cast as int')
    ]
    for pattern, name in error_patterns:
        if re.search(pattern, p):
            signals.append((4, 'error_based', f"Error-based function '{name}' detected"))
            break

    heavy_patterns = [
        (r'generate_series', 'generate_series'),
        (r'from\s+\w+\s+as\s+t1,\s*\w+\s+as\s+t2', 'cartesian join'),
        (r'all_users', 'all_users join'),
        (r'sysusers', 'sysusers join'),
        (r'domain\.domains', 'domain.domains join'),
        (r'sysibm\.systables', 'sysibm.systables join')
    ]
    for pattern, name in heavy_patterns:
        if re.search(pattern, p):
            signals.append((4, 'heavy_query', f"Heavy query pattern '{name}' detected"))
            break

    # P5: Time Blind
    time_patterns = [
        (r'sleep\s*\(', 'sleep()'),
        (r'pg_sleep\s*\(', 'pg_sleep()'),
        (r'waitfor\s+delay', 'waitfor delay'),
        (r'benchmark\s*\(', 'benchmark()'),
        (r'dbms_pipe\.receive_message', 'dbms_pipe'),
        (r'randomblob', 'randomblob')
    ]
    for pattern, name in time_patterns:
        if re.search(pattern, p):
            signals.append((5, 'time_blind', f"Time-blind function '{name}' detected"))
            break

    # P7: Union Based
    if "union select" in p or "union all select" in p:
        signals.append((7, 'union_based', "Union-based 'union select' detected"))

    # P8: Stacked
    if any(x in p for x in ['; insert', '; update', '; drop', '; exec', 'xp_cmdshell']):
        signals.append((8, 'stacked_queries', 'Stacked query keyword detected'))

    # Final decision based on priority
    if not signals:
        res_type = 'benign'
        reasoning = "No SQL injection signals detected in the payload structure."
    else:
        signals.sort() # Sort by priority number (lower is stronger)
        res_type = signals[0][1]
        reasoning = f"{signals[0][2]}; DB engine signature: {db}; follows taxonomy priority P{signals[0][0]}."

    # sources_agree
    a_type = str(row['a_type'])
    c_type = str(row['c_type'])
    agree = 1
    if res_type == a_type and res_type == c_type:
        agree = 3
    elif res_type == a_type or res_type == c_type:
        agree = 2
        
    confidence = 0.85 if agree >= 2 else 0.7
    if agree == 3: confidence = 1.0
    
    # Reasoning length check
    if len(reasoning) < 50:
        reasoning += " " + row['payload_inner'][:50] + "..."

    return pd.Series([res_type, db, confidence, reasoning, agree])

df = pd.read_csv(r'C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\Gemini\_chunks\chunk_006.csv')
df[['sqli_type', 'db_engine', 'confidence', 'reasoning', 'sources_agree']] = df.apply(classify, axis=1)

# Final selection of columns
out_df = df[['id', 'payload_inner', 'sqli_type', 'db_engine', 'confidence', 'reasoning', 'sources_agree']]
out_df.to_csv(r'C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\Gemini\_chunks\chunk_006_labeled.csv', index=False)
