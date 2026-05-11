import csv
import re
import sys

def has_func(p, name):
    """Check if function name appears with optional space before ("""
    return bool(re.search(re.escape(name) + r'\s*\(', p))

def determine_label(payload):
    if not payload or len(payload.strip()) < 2:
        return "boolean_blind", "generic", 0.70

    p = payload.lower()

    # ========== DB ENGINE DETECTION ==========
    engine_scores = {"oracle": 0, "mysql": 0, "postgresql": 0, "mssql": 0, "sqlite": 0}

    # Oracle markers
    if re.search(r'chr\s*\(\s*\d+\s*\)\s*\|\|\s*chr\s*\(\s*\d+\s*\)', p):
        engine_scores["oracle"] += 3
    if has_func(p, 'xmltype'):
        engine_scores["oracle"] += 3
    if 'dbms_pipe.' in p:
        engine_scores["oracle"] += 3
    if 'utl_inaddr' in p or 'utl_http' in p:
        engine_scores["oracle"] += 3
    if has_func(p, 'sys_context'):
        engine_scores["oracle"] += 3
    if 'from dual' in p:
        engine_scores["oracle"] += 3
    if 'ctxsys.' in p:
        engine_scores["oracle"] += 3
    if 'dbms_utility.' in p:
        engine_scores["oracle"] += 3
    if 'sys.all_tables' in p or 'all_tables' in p or 'all_objects' in p:
        engine_scores["oracle"] += 3
    if has_func(p, 'raise_error'):
        engine_scores["oracle"] += 3
    if 'sysibm.sysdummy1' in p or 'sysibm.systables' in p:
        engine_scores["oracle"] += 3
    if 'rownum' in p:
        engine_scores["oracle"] += 2

    # MySQL markers
    if has_func(p, 'sleep'):
        engine_scores["mysql"] += 2
    if has_func(p, 'benchmark'):
        engine_scores["mysql"] += 2
    if 'group_concat' in p:
        engine_scores["mysql"] += 2
    if has_func(p, 'extractvalue'):
        engine_scores["mysql"] += 2
    if has_func(p, 'updatexml'):
        engine_scores["mysql"] += 2
    if 'information_schema.' in p:
        engine_scores["mysql"] += 2
    if 'load_file' in p:
        engine_scores["mysql"] += 2
    if 'into outfile' in p:
        engine_scores["mysql"] += 2
    if '@@version' in p or '@@datadir' in p:
        engine_scores["mysql"] += 2
    if has_func(p, 'elt'):
        engine_scores["mysql"] += 1
    if has_func(p, 'make_set'):
        engine_scores["mysql"] += 2
    if '0x7171706a71' in p or '0x717a767a71' in p:
        engine_scores["mysql"] += 2
    if has_func(p, 'regexp_substring') or has_func(p, 'regexp_substr'):
        engine_scores["mysql"] += 2
    if 'crypt_key' in p:
        engine_scores["mysql"] += 2
    if 'procedure analyse' in p:
        engine_scores["mysql"] += 2
    if ' in boolean mode' in p:
        engine_scores["mysql"] += 2
    if re.search(r'floor\s*\(\s*rand', p):
        engine_scores["mysql"] += 2
    if '# ' in p or p.rstrip().endswith('#'):
        engine_scores["mysql"] += 1

    # PostgreSQL markers
    if has_func(p, 'pg_sleep'):
        engine_scores["postgresql"] += 3
    if has_func(p, 'generate_series'):
        engine_scores["postgresql"] += 3
    if '::text' in p or '::int' in p or '::numeric' in p:
        engine_scores["postgresql"] += 3
    if 'string_agg' in p or 'array_agg' in p:
        engine_scores["postgresql"] += 3
    if 'pg_read_file' in p:
        engine_scores["postgresql"] += 3
    if 'from pg_' in p or 'pg_catalog' in p:
        engine_scores["postgresql"] += 3

    # MSSQL markers
    if re.search(r'waitfor\s+delay', p):
        engine_scores["mssql"] += 3
    if 'master..sysdatabases' in p:
        engine_scores["mssql"] += 3
    if 'xp_cmdshell' in p:
        engine_scores["mssql"] += 3
    if '@@servername' in p:
        engine_scores["mssql"] += 3
    if 'sysobjects' in p or 'syscolumns' in p or 'sysusers' in p:
        engine_scores["mssql"] += 3
    if has_func(p, 'convert') and 'int' in p:
        engine_scores["mssql"] += 3

    # SQLite markers
    if has_func(p, 'randomblob'):
        engine_scores["sqlite"] += 3
    if 'sqlite_version' in p or 'sqlite_master' in p:
        engine_scores["sqlite"] += 3

    # ========== TYPE DETECTION ==========
    has_union = bool(re.search(r'union\s+(all\s+)?select', p))
    has_error_marker = False
    has_time_marker = False
    has_boolean_marker = False

    # Error markers (handle optional space before parenthesis)
    if has_func(p, 'xmltype'):
        has_error_marker = True
    if has_func(p, 'extractvalue'):
        has_error_marker = True
    if has_func(p, 'updatexml'):
        has_error_marker = True
    if has_func(p, 'convert') and 'int' in p:
        has_error_marker = True
    if 'utl_inaddr.' in p:
        has_error_marker = True
    if has_func(p, 'ctxsys.drithsx.sn') or 'ctxsys.drithsx.sn' in p:
        has_error_marker = True
    if has_func(p, 'raise_error'):
        has_error_marker = True
    if re.search(r'exp\s*\(~', p) or re.search(r'exp\s*\(\s*~', p):
        has_error_marker = True
    if re.search(r'concat\s*\(\s*0x', p):
        has_error_marker = True
    if re.search(r'floor\s*\(\s*rand', p) and re.search(r'group\s+by', p):
        has_error_marker = True

    # Time markers
    if re.search(r'sleep\s*\(\s*\d+', p):
        has_time_marker = True
    if has_func(p, 'pg_sleep'):
        has_time_marker = True
    if re.search(r'waitfor\s+delay', p):
        has_time_marker = True
    if has_func(p, 'benchmark') and re.search(r'benchmark\s*\(\s*\d+', p):
        has_time_marker = True
    if re.search(r'dbms_pipe\.receive_message\s*\(', p):
        has_time_marker = True
    if has_func(p, 'generate_series') and re.search(r'generate_series\s*\(\s*1\s*,\s*[5-9]\d{5,}', p):
        has_time_marker = True
    if has_func(p, 'randomblob') and re.search(r'randomblob\s*\(\s*\d{6,}', p):
        has_time_marker = True
    if re.search(r'like\s*\(\s*[\'"]abcdefg[\'"]', p) and 'randomblob' in p:
        has_time_marker = True
    if re.search(r'regexp_substring\s*\(\s*repeat\s*\(', p):
        has_time_marker = True
    if '500000000' in p or '5000000000' in p:
        has_time_marker = True

    # Boolean markers
    if re.search(r'case\s+when', p):
        has_boolean_marker = True
    if has_func(p, 'if') and not has_func(p, 'sleep') and not has_func(p, 'benchmark'):
        has_boolean_marker = True
    if has_func(p, 'iif'):
        has_boolean_marker = True
    if has_func(p, 'elt'):
        has_boolean_marker = True
    if re.search(r'ord\s*\(\s*mid\s*\(', p):
        has_boolean_marker = True
    if re.search(r"""or\s+['""][\w'""]+['""]\s*=\s*['""][\w'""]+['""]""", p):
        has_boolean_marker = True
    if re.search(r"""or\s+['""]\s*=\s*['""]""", p):
        has_boolean_marker = True
    if re.search(r"""'\s+or\s+['""]""", p):
        has_boolean_marker = True
    if re.search(r'\band\s+\d+\s*=\s*\d+', p):
        has_boolean_marker = True
    if re.search(r'\bor\s+\d+\s*=\s*\d+', p) and not has_union:
        has_boolean_marker = True
    if re.search(r'=\s*\d+\s*\*\s*\d+', p):
        has_boolean_marker = True
    if re.search(r'select\s+\(?\s*case\s+when', p):
        has_boolean_marker = True
    if re.search(r'where\s+\d+\s*=\s*\d+', p):
        has_boolean_marker = True
    if 'rlike' in p:
        has_boolean_marker = True
    if re.search(r'cast\s*\(.*::text.*::numeric', p):
        has_boolean_marker = True
    if re.search(r'char\s*\(\s*\d+\s*\)\s*\+\s*char\s*\(\s*\d+\s*\)', p) and not has_union:
        has_boolean_marker = True

    # ========== TIEBREAKER LOGIC ==========
    if has_union and has_error_marker and not has_time_marker:
        sqli_type = "error_based"
        confidence = 0.85
    elif has_time_marker and has_boolean_marker:
        sqli_type = "time_blind"
        confidence = 1.00
    elif has_time_marker:
        sqli_type = "time_blind"
        confidence = 1.00
    elif has_error_marker:
        sqli_type = "error_based"
        confidence = 1.00
    elif has_union:
        sqli_type = "union_based"
        confidence = 1.00
    elif has_boolean_marker:
        sqli_type = "boolean_blind"
        confidence = 1.00
    else:
        if re.search(r'--', p) or re.search(r'#', p) or re.search(r'null', p):
            sqli_type = "boolean_blind"
            confidence = 0.70
        elif re.search(r'\b(and|or)\b', p) and re.search(r'\d+', p):
            sqli_type = "boolean_blind"
            confidence = 0.70
        else:
            sqli_type = "boolean_blind"
            confidence = 0.70

    # ========== DB ENGINE TIEBREAKER ==========
    max_score = max(engine_scores.values())
    if max_score >= 2:
        candidates = [k for k, v in engine_scores.items() if v == max_score]
        if len(candidates) > 1:
            if "oracle" in candidates:
                db_engine = "oracle"
            elif "mysql" in candidates:
                db_engine = "mysql"
            elif "postgresql" in candidates:
                db_engine = "postgresql"
            elif "mssql" in candidates:
                db_engine = "mssql"
            else:
                db_engine = candidates[0]
        else:
            db_engine = candidates[0]
    else:
        db_engine = "generic"

    # ========== CONFIDENCE ADJUSTMENT ==========
    tokens = len(p.split())
    if tokens < 5:
        if confidence == 1.00:
            confidence = 0.85
        elif confidence == 0.85:
            confidence = 0.70
        if tokens < 3:
            confidence = 0.70

    if sqli_type == "union_based" and "order by" in p and "union" not in p:
        confidence = min(confidence, 0.85)

    if db_engine == "oracle" and not has_func(p, 'xmltype') and 'dbms_pipe.' not in p and 'utl_' not in p and 'ctxsys.' not in p and 'sys_context' not in p and 'from dual' not in p and 'dbms_utility' not in p and 'sysibm.' not in p:
        if confidence > 0.85:
            confidence = 0.85

    if has_union and has_error_marker:
        confidence = min(confidence, 0.85)

    if 'case when' in p and '500000000' in p:
        confidence = min(confidence, 0.85)

    if db_engine == "generic" and confidence == 1.00:
        if sqli_type in ("boolean_blind",):
            if tokens < 10:
                confidence = 0.85

    return sqli_type, db_engine, confidence


# ========== MAIN ==========
start_id = 16001
count = 2000

rows = []
with open("C:\\Projects\\GAN_SQLi\\SeqGAN_SQLi\\data\\split_data.csv", "r", encoding="utf-8-sig") as f:
    reader = csv.DictReader(f)
    for row in reader:
        rid = int(row["id"])
        if start_id <= rid < start_id + count:
            rows.append(row)

print(f"Processing {len(rows)} rows from id={start_id}...", file=sys.stderr)

output_file = f"C:\\Projects\\GAN_SQLi\\SeqGAN_SQLi\\data\\split_data_labeled_batch_{start_id}_{start_id+count-1}.csv"
with open(output_file, "w", encoding="utf-8", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["id", "sqli_type", "db_engine", "confidence"])
    for row in rows:
        rid = int(row["id"])
        payload = row["payload_norm"]
        sqli_type, db_engine, confidence = determine_label(payload)
        conf_str = f"{confidence:.2f}"
        writer.writerow([rid, sqli_type, db_engine, conf_str])

print(f"Done! Written to {output_file}", file=sys.stderr)
