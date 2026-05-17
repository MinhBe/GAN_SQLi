import pandas as pd
import re
import os

input_path = r'C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\Gemini\_chunks\chunk_010.csv'
output_path = r'C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\Gemini\_chunks\chunk_010_labeled.csv'

df = pd.read_csv(input_path)

def label_payload(row):
    p = str(row['payload_inner'])
    a_type = str(row['a_type'])
    c_type = str(row['c_type'])
    
    sqli_type = 'unknown'
    db_engine = 'generic'
    confidence = 0.9
    reasoning = ''
    
    # Priority check based on tokens
    if 'union all select' in p.lower() or 'union select' in p.lower():
        sqli_type = 'union_based'
        reasoning = "'union all select' structure detected, typical for extracting data via UNION-based injection."
        if '#' in p: db_engine = 'mysql'
        elif '--' in p: db_engine = 'generic'
    elif 'sleep (' in p.lower() or 'sleep(' in p.lower():
        sqli_type = 'time_blind'
        db_engine = 'mysql'
        reasoning = "'sleep(N)' function call detected; this is a standard MySQL time-based blind injection signal."
    elif 'pg_sleep' in p.lower():
        sqli_type = 'time_blind'
        db_engine = 'postgresql'
        reasoning = "'pg_sleep(N)' is a PostgreSQL-specific function used for time-based blind SQL injection."
    elif 'waitfor delay' in p.lower():
        sqli_type = 'time_blind'
        db_engine = 'mssql'
        reasoning = "'WAITFOR DELAY' detected, which is the standard method for time-based blind SQLi in MSSQL."
    elif 'dbms_pipe.receive_message' in p.lower():
        sqli_type = 'time_blind'
        db_engine = 'oracle'
        reasoning = "'dbms_pipe.receive_message' is an Oracle-specific function often used for time-based blind injection."
    elif 'benchmark (' in p.lower():
        sqli_type = 'time_blind'
        db_engine = 'mysql'
        reasoning = "'benchmark()' function detected; used in MySQL to create time delays for blind injection."
    elif 'xmltype (' in p.lower() or 'xmltype(' in p.lower():
        sqli_type = 'error_based'
        db_engine = 'oracle'
        reasoning = "'xmltype()' constructor used with malformed XML to trigger Oracle error-based SQL injection."
    elif 'extractvalue (' in p.lower() or 'extractvalue(' in p.lower():
        sqli_type = 'error_based'
        db_engine = 'mysql'
        reasoning = "'extractvalue()' is a MySQL function used to trigger XPath errors in error-based SQLi."
    elif 'updatexml (' in p.lower() or 'updatexml(' in p.lower():
        sqli_type = 'error_based'
        db_engine = 'mysql'
        reasoning = "'updatexml()' used to trigger intentional XPath errors for error-based SQL injection in MySQL."
    elif 'convert ( int' in p.lower() or ('cast (' in p.lower() and 'as int' in p.lower()):
        sqli_type = 'error_based'
        reasoning = "Type conversion error (e.g., 'convert(int, ...)') used to leak data in error-based SQLi."
        if 'char (' in p.lower(): db_engine = 'mssql'
    elif 'regexp_substring' in p.lower() and '500000000' in p:
        sqli_type = 'heavy_query'
        reasoning = "'regexp_substring' with a very large 'repeat' multiplier (500,000,000) is a DoS-style heavy query attack."
    elif 'generate_series' in p.lower() and '5000000' in p:
        sqli_type = 'heavy_query'
        db_engine = 'postgresql'
        reasoning = "'generate_series' with a large range (5,000,000) creates a massive result set for heavy query DoS."
    elif 'randomblob' in p.lower():
        sqli_type = 'time_blind'
        db_engine = 'sqlite'
        reasoning = "'randomblob(N)' with a large N creates a processing delay in SQLite, used for time-based blind SQLi."
    elif 'utl_inaddr.get_host_address' in p.lower():
        sqli_type = 'error_based'
        db_engine = 'oracle'
        reasoning = "'utl_inaddr.get_host_address' used in Oracle for error-based or out-of-band data exfiltration."
    elif 'rlike' in p.lower() or 'elt (' in p.lower() or 'make_set' in p.lower():
        sqli_type = 'boolean_blind'
        db_engine = 'mysql'
        reasoning = f"MySQL specific boolean operator used for boolean-based blind injection: {p[:20]}..."
    elif 'iif (' in p.lower() and '1/0' in p:
        sqli_type = 'boolean_blind'
        db_engine = 'mssql'
        reasoning = "'iif()' with a division by zero ('1/0') used to trigger conditional errors in boolean-blind SQLi."
    elif 'all_users' in p.lower() or 'all_tables' in p.lower():
        sqli_type = 'boolean_blind'
        db_engine = 'oracle'
        reasoning = "Oracle metadata table 'all_users' or 'all_tables' access attempted in a boolean context for blind injection."
    elif 'rdb$database' in p.lower() or 'rdb$fields' in p.lower():
        sqli_type = 'boolean_blind'
        db_engine = 'firebird'
        reasoning = "Firebird metadata table 'rdb$database' or 'rdb$fields' used in boolean-based blind injection."
    elif 'sysibm.systables' in p.lower():
        sqli_type = 'boolean_blind'
        db_engine = 'db2'
        reasoning = "DB2 metadata table 'sysibm.systables' used for schema discovery in boolean-blind injection."
    elif 'and ' in p.lower() or 'or ' in p.lower():
        sqli_type = 'boolean_blind'
        reasoning = "Standard boolean logic ('AND'/'OR' with equality) used for boolean-based blind SQL injection."
    else:
        sqli_type = 'benign'
        confidence = 0.7
        reasoning = "No clear SQL injection attack signals (UNION, SLEEP, XML error, etc.) detected in the payload."

    if sqli_type == 'unknown' or len(reasoning) < 50:
        confidence = 0.5
        reasoning = 'UNCERTAIN: ' + (reasoning if reasoning else 'Could not determine type from payload tokens.')

    # sources_agree
    sources_agree = 1
    if sqli_type == a_type and sqli_type == c_type: sources_agree = 3
    elif sqli_type == a_type or sqli_type == c_type: sources_agree = 2
    if confidence < 0.5: sources_agree = 0
    
    return pd.Series([sqli_type, db_engine, confidence, reasoning, sources_agree])

df[['sqli_type', 'db_engine', 'confidence', 'reasoning', 'sources_agree']] = df.apply(label_payload, axis=1)
df['id'] = range(1, len(df) + 1)

output_df = df[['id', 'payload_inner', 'sqli_type', 'db_engine', 'confidence', 'reasoning', 'sources_agree']]
output_df.to_csv(output_path, index=False)
print(output_df['sqli_type'].value_counts())
