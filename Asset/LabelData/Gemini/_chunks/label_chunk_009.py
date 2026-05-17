
import pandas as pd
import re

def get_db(payload):
    p = payload.lower()
    if 'waitfor delay' in p or 'master..sysdatabases' in p or 'sysobjects' in p:
        return 'mssql'
    if 'pg_sleep' in p or 'generate_series' in p or '::text' in p or 'pg_database' in p:
        return 'postgresql'
    if 'sleep(' in p or 'benchmark(' in p or 'extractvalue' in p or 'updatexml' in p or 'rlike' in p or 'elt(' in p or 'make_set' in p or '0x717' in p:
        return 'mysql'
    if 'xmltype' in p or 'dbms_pipe' in p or 'dbms_utility' in p or 'from dual' in p or 'utl_inaddr' in p or 'ctxsys' in p:
        return 'oracle'
    if 'randomblob' in p or 'sqlite_master' in p:
        return 'sqlite'
    if 'rdb$fields' in p or 'rdb$database' in p or 'rdb$types' in p:
        return 'firebird'
    if 'sysibm.systables' in p:
        return 'db2'
    return 'generic'

def label_payload(row, idx):
    payload = str(row['payload_inner'])
    p = payload.lower()
    a_type = str(row['a_type'])
    c_type = str(row['c_type'])
    
    sqli_type = 'unknown'
    db_engine = get_db(payload)
    confidence = 1.0
    reasoning = ""

    # Priority rules
    if 'waitfor delay' in p:
        sqli_type = 'time_blind'
        db_engine = 'mssql'
        reasoning = f"Uses 'waitfor delay' which is an exclusive T-SQL signature for time-based blind injection in MSSQL."
    elif 'pg_sleep' in p:
        sqli_type = 'time_blind'
        db_engine = 'postgresql'
        reasoning = f"The 'pg_sleep' function is a clear PostgreSQL signature for time-based blind SQL injection."
    elif 'dbms_pipe.receive_message' in p:
        sqli_type = 'time_blind'
        db_engine = 'oracle'
        reasoning = f"Uses 'dbms_pipe.receive_message', an Oracle-specific function often leveraged for time-based blind SQLi."
    elif 'benchmark(' in p:
        sqli_type = 'time_blind'
        db_engine = 'mysql'
        reasoning = f"The 'benchmark()' function is used in MySQL to induce artificial delays for time-based blind injection."
    elif 'sleep(' in p:
        sqli_type = 'time_blind'
        db_engine = 'mysql'
        reasoning = f"Detected the 'sleep()' function, which is the standard MySQL signal for time-based blind SQL injection."
    elif 'randomblob(5000000' in p:
        sqli_type = 'time_blind' # or heavy_query? Taxonomy says time_blind
        db_engine = 'sqlite'
        reasoning = f"Uses a large 'randomblob' generation to induce processing delays in SQLite, characteristic of time-based blind SQLi."
    elif 'xmltype' in p:
        sqli_type = 'error_based'
        db_engine = 'oracle'
        reasoning = f"The 'xmltype' function call with invalid syntax is a classic Oracle error-based SQL injection technique."
    elif 'extractvalue' in p or 'updatexml' in p:
        sqli_type = 'error_based'
        db_engine = 'mysql'
        reasoning = f"Uses MySQL XPath functions like 'extractvalue' or 'updatexml' to trigger verbose error messages containing data."
    elif 'utl_inaddr' in p or 'ctxsys.drithsx' in p or 'dbms_utility' in p:
        sqli_type = 'out_of_band' # SKILL says P6
        db_engine = 'oracle'
        reasoning = f"Oracle package functions like 'utl_inaddr' or 'ctxsys' are used for out-of-band data exfiltration or error-based extraction."
    elif 'generate_series' in p and ('5000000' in p or '1000000' in p):
        sqli_type = 'heavy_query'
        db_engine = 'postgresql'
        reasoning = f"The 'generate_series(1, 5000000)' token creates a massive result set to exhaust CPU resources, typical of a heavy query."
    elif 'regexp_substring' in p and '5000000' in p:
        sqli_type = 'heavy_query'
        db_engine = 'generic'
        reasoning = f"High iteration counts like '5000000' within 'regexp_substring' or 'repeat' are used for CPU-intensive heavy query attacks."
    elif 'union' in p and 'select' in p:
        sqli_type = 'union_based'
        reasoning = f"Contains the 'union all select' pattern used to append results from an attacker-controlled query to the original output."
    elif 'drop function' in p or '; insert' in p or '; delete' in p:
        sqli_type = 'stacked_queries'
        reasoning = f"Uses ';' to stack multiple SQL statements, such as 'drop function' or 'insert', allowing for arbitrary command execution."
    elif 'rlike' in p or 'elt(' in p or 'make_set' in p:
        sqli_type = 'boolean_blind'
        db_engine = 'mysql'
        reasoning = f"Uses MySQL-specific boolean functions like 'rlike' or 'elt' to perform data exfiltration via boolean-based blind injection."
    elif re.search(r'\d+\s*=\s*\d+', p) or 'where' in p or 'and' in p or 'or' in p:
        sqli_type = 'boolean_blind'
        reasoning = f"The use of boolean tautologies like '4008 = 4008' or logical operators 'AND'/'OR' indicates a boolean-based blind SQLi attempt."
    else:
        sqli_type = 'benign'
        confidence = 0.8
        reasoning = f"No specific SQL injection signals (union, error, time, etc.) were identified in this payload structure."

    # Final adjustments based on taxonomy priorities if needed, but the if-elif above mostly covers it
    
    # Calculate sources_agree
    sources_agree = 1
    if sqli_type == a_type and sqli_type == c_type:
        sources_agree = 3
    elif sqli_type == a_type or sqli_type == c_type:
        sources_agree = 2
    
    if confidence < 0.5:
        sources_agree = 0
        
df = pd.read_csv(r'C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\Gemini\_chunks\chunk_009.csv')
df_out = df.apply(lambda row: label_payload(row, row.name), axis=1)
df_out.columns = ['id', 'payload_inner', 'sqli_type', 'db_engine', 'confidence', 'reasoning', 'sources_agree']

df_out.to_csv(r'C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\Gemini\_chunks\chunk_009_labeled.csv', index=False)
print("Labeling complete. Distribution:")
print(df_out['sqli_type'].value_counts())
