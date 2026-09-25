#!/usr/bin/env python3
"""PostgreSQL Boolean predicate sandbox validator for V5.1.
Defensive/offline use only. Validates predicate-only payloads by wrapping them in SELECT CASE WHEN.
Requires psycopg or psycopg2 and a sandbox DSN, for example:
  PG_DSN=postgresql://postgres:postgres@localhost:5432/postgres \
  python postgres_boolean_probe_validator.py input.csv output.csv --auto-payload-column

Column policy:
- Y1/Y2: validate payload_raw or payload_stripped.
- Y3: validate payload_decoded where available.
- Y4: validate payload_normalized where available.
This prevents raw encoding/comment obfuscation from being confused with canonical predicate validation.
"""
import os, csv, sys, re, argparse
try:
    import psycopg
except Exception:
    psycopg = None
try:
    import psycopg2
except Exception:
    psycopg2 = None
DANGEROUS = re.compile(r"(;|--|\b(SELECT|UNION|INSERT|UPDATE|DELETE|DROP|ALTER|CREATE|COPY|GRANT|REVOKE|TRUNCATE|pg_sleep|dblink|lo_import|pg_read_file)\b)", re.I)
COMMENT = re.compile(r"(/\*)")
def wrap(payload):
    return f"SELECT CASE WHEN ({payload}) THEN TRUE ELSE FALSE END AS observed_truth"
def pos(payload): return f"SELECT CASE WHEN (({payload}) OR TRUE) THEN TRUE ELSE FALSE END AS observed_truth"
def neg(payload): return f"SELECT CASE WHEN (({payload}) AND FALSE) THEN TRUE ELSE FALSE END AS observed_truth"
def connect(dsn):
    if psycopg:
        return psycopg.connect(dsn, connect_timeout=3)
    if psycopg2:
        return psycopg2.connect(dsn, connect_timeout=3)
    raise RuntimeError('Install psycopg or psycopg2')
def run_one(cur, sql):
    cur.execute('SET statement_timeout = 500')
    cur.execute(sql)
    row = cur.fetchone()
    return bool(row[0]) if row else None
def choose_payload(row, args):
    if args.payload_column:
        return row.get(args.payload_column, '') or ''
    if args.auto_payload_column:
        mod = row.get('target_module_id') or row.get('module_id') or ''
        if mod == 'Y3_encoded_boolean':
            return row.get('payload_decoded') or row.get('payload_normalized') or row.get('payload_raw') or row.get('payload_stripped') or ''
        if mod == 'Y4_obfuscated_boolean':
            return row.get('payload_normalized') or row.get('payload_decoded') or row.get('payload_raw') or row.get('payload_stripped') or ''
    return row.get('payload_raw') or row.get('payload_stripped') or row.get('payload_normalized') or row.get('payload_decoded') or ''
def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('input_csv')
    ap.add_argument('output_csv')
    ap.add_argument('--payload-column', default='', help='Explicit payload column to validate, e.g. payload_raw, payload_decoded, payload_normalized')
    ap.add_argument('--auto-payload-column', action='store_true', help='Choose payload column by module: Y3 decoded, Y4 normalized, Y1/Y2 raw')
    ap.add_argument('--allow-comments', action='store_true', help='Allow SQL comments in chosen payload column. Prefer validating normalized Y4 instead.')
    args=ap.parse_args()
    dsn=os.environ.get('PG_DSN')
    if not dsn: raise RuntimeError('PG_DSN env var is required')
    with connect(dsn) as conn, open(args.input_csv, newline='', encoding='utf-8') as f, open(args.output_csv,'w',newline='',encoding='utf-8') as g:
        reader=csv.DictReader(f)
        add=['payload_validation_column','payload_validation_value','postgres_parse_valid','postgres_runtime_valid','positive_observed_truth','negative_observed_truth','truth_match','runtime_error_class','runtime_error_message_normalized']
        fields=list(reader.fieldnames or [])+[x for x in add if x not in (reader.fieldnames or [])]
        w=csv.DictWriter(g, fieldnames=fields); w.writeheader()
        cur=conn.cursor()
        for r in reader:
            payload=choose_payload(r,args)
            col=args.payload_column or ('auto' if args.auto_payload_column else 'default')
            forbidden = DANGEROUS.search(payload) or ((not args.allow_comments) and COMMENT.search(payload))
            if forbidden:
                r.update(payload_validation_column=col,payload_validation_value=payload,postgres_parse_valid='false',postgres_runtime_valid='false',positive_observed_truth='',negative_observed_truth='',truth_match='false',runtime_error_class='forbidden_construct',runtime_error_message_normalized='forbidden construct in predicate-only validator')
            else:
                try:
                    _=run_one(cur, wrap(payload))
                    po=run_one(cur, pos(payload)); ne=run_one(cur, neg(payload))
                    r.update(payload_validation_column=col,payload_validation_value=payload,postgres_parse_valid='true',postgres_runtime_valid='true',positive_observed_truth=str(po).lower(),negative_observed_truth=str(ne).lower(),truth_match=str(po is True and ne is False).lower(),runtime_error_class='ok',runtime_error_message_normalized='')
                except Exception as e:
                    try: conn.rollback()
                    except Exception: pass
                    r.update(payload_validation_column=col,payload_validation_value=payload,postgres_parse_valid='false',postgres_runtime_valid='false',positive_observed_truth='',negative_observed_truth='',truth_match='false',runtime_error_class=e.__class__.__name__,runtime_error_message_normalized=str(e).split('\n')[0][:240])
            w.writerow(r)
if __name__ == '__main__': main()
