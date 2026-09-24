#!/usr/bin/env python3
"""PostgreSQL Boolean predicate sandbox validator.
Run only against a disposable local PostgreSQL database.
This script validates predicate executability, not exploitability against an application.
"""
import csv, sys, subprocess, tempfile, os, shlex, json, re
from pathlib import Path

FORBIDDEN = re.compile(r"\b(SELECT|UNION|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|COPY|TRUNCATE|GRANT|REVOKE|EXEC|EXECUTE|CALL|DO|PG_SLEEP)\b|;|--|/\*.*?\*/", re.I|re.S)

def validate_payload(payload: str, psql_cmd='psql'):
    if FORBIDDEN.search(payload):
        return {'postgres_parse_valid': False, 'postgres_runtime_valid': False, 'runtime_error_class': 'forbidden_construct'}
    sql = "SET statement_timeout='200ms'; SET lock_timeout='100ms'; SET search_path=pg_temp; SELECT CASE WHEN (" + payload + ") THEN TRUE ELSE FALSE END;"
    try:
        cp = subprocess.run([psql_cmd, '-X', '-q', '-v', 'ON_ERROR_STOP=1', '-c', sql], text=True, capture_output=True, timeout=1.0)
        ok = cp.returncode == 0
        return {'postgres_parse_valid': ok, 'postgres_runtime_valid': ok, 'runtime_error_class': '' if ok else (cp.stderr.strip().split('\n')[-1][:120] if cp.stderr else 'psql_error')}
    except subprocess.TimeoutExpired:
        return {'postgres_parse_valid': False, 'postgres_runtime_valid': False, 'runtime_error_class': 'timeout'}

if __name__ == '__main__':
    if len(sys.argv) < 3:
        print('usage: postgres_sandbox_validator.py input.csv output.csv [payload_column]', file=sys.stderr); sys.exit(2)
    inp, out = Path(sys.argv[1]), Path(sys.argv[2])
    col = sys.argv[3] if len(sys.argv) > 3 else 'validation_payload_v4'
    with inp.open(newline='', encoding='utf-8') as f, out.open('w', newline='', encoding='utf-8') as g:
        r = csv.DictReader(f)
        fields = r.fieldnames + ['postgres_parse_valid_runtime','postgres_runtime_valid_runtime','runtime_error_class_runtime']
        w = csv.DictWriter(g, fieldnames=fields); w.writeheader()
        for row in r:
            res = validate_payload(row.get(col,'') or '')
            row.update({'postgres_parse_valid_runtime': res['postgres_parse_valid'], 'postgres_runtime_valid_runtime': res['postgres_runtime_valid'], 'runtime_error_class_runtime': res['runtime_error_class']})
            w.writerow(row)
