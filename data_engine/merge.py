import csv
import json
import os
import re
import hashlib
from pathlib import Path

VALID_SQLI_TYPES = {
    'union_based', 'error_based', 'boolean_blind', 'time_blind',
    'heavy_query', 'stacked_queries', 'out_of_band', 'auth_bypass',
    'second_order', 'rce', 'polyglot', 'lateral', 'benign', 'unknown'
}
VALID_DB_ENGINES = {
    'mysql', 'mssql', 'oracle', 'postgresql', 'sqlite', 'generic', 'unknown'
}


def delexicalize(payload):
    s = re.sub(r"'[^']*'", '<STR>', payload)
    s = re.sub(r'"[^"]*"', '<STR>', s)
    s = re.sub(r'\b\d+\.?\d*\b', '<NUM>', s)
    s = re.sub(r'\b(users|admin|accounts|members|login)\b', '<TABLE>', s, flags=re.IGNORECASE)
    s = re.sub(r'\b(username|password|email|id|name)\b', '<COL>', s, flags=re.IGNORECASE)
    return s


def validate_row(row):
    issues = []
    
    required_cols = ['payload_raw', 'payload_norm', 'payload_delex', 'label', 
                   'is_obfuscated', 'sqli_type', 'db_engine', 'confidence', 'reasoning']
    for col in required_cols:
        if col not in row or not row[col]:
            issues.append(f"missing {col}")
    
    label = row.get('label', '')
    if label not in ['0', '1']:
        issues.append(f"invalid label: {label}")
    
    is_obf = row.get('is_obfuscated', '')
    if is_obf not in ['True', 'False', True, False]:
        issues.append(f"invalid is_obfuscated: {is_obf}")
    
    sqli_type = row.get('sqli_type', '').lower()
    if sqli_type not in VALID_SQLI_TYPES:
        issues.append(f"invalid sqli_type: {sqli_type}")
    
    db_engine = row.get('db_engine', '').lower()
    if db_engine not in VALID_DB_ENGINES:
        issues.append(f"invalid db_engine: {db_engine}")
    
    try:
        conf = float(row.get('confidence', 0))
        if not (0.0 <= conf <= 1.0):
            issues.append(f"invalid confidence: {conf}")
    except:
        issues.append("confidence not float")
    
    if not row.get('payload_raw', '').strip():
        issues.append("empty payload_raw")
    
    is_label_1_but_benign = (label == '1' and sqli_type == 'benign')
    is_label_0_not_benign = (label == '0' and sqli_type != 'benign')
    if is_label_1_but_benign:
        issues.append("label=1 but sqli_type=benign")
    if is_label_0_not_benign:
        issues.append("label=0 but sqli_type!=benign")
    
    return issues


def merge():
    all_rows = []
    
    output_dir = Path('outputs')
    for i in range(8):
        output_file = output_dir / f'output_{i}.csv'
        if not output_file.exists():
            print(f"Warning: {output_file} not found")
            continue
        
        with open(output_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                all_rows.append(row)
    
    print(f"Loaded {len(all_rows)} rows from 8 outputs")
    
    seen_norm = set()
    deduped = []
    for row in all_rows:
        norm = row.get('payload_norm', '').lower().strip()
        h = hashlib.sha256(norm.encode()).hexdigest()
        if h in seen_norm:
            continue
        seen_norm.add(h)
        deduped.append(row)
    
    print(f"After dedup: {len(deduped)} rows")
    
    for row in deduped:
        if 'payload_delex' not in row or not row['payload_delex']:
            row['payload_delex'] = delexicalize(row.get('payload_norm', ''))
    
    flagged = []
    for row in deduped:
        issues = validate_row(row)
        if issues:
            row['validation_issues'] = '; '.join(issues)
            flagged.append(row)
    
    if flagged:
        print(f"Flagged {len(flagged)} rows with validation issues")
        with open('output/flagged_rows.csv', 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=flagged[0].keys())
            writer.writeheader()
            writer.writerows(flagged)
    
    sqli_type_dist = {}
    db_engine_dist = {}
    label_dist = {'0': 0, '1': 0}
    is_obf_dist = {'True': 0, 'False': 0}
    confidence_sum = 0.0
    unknown_count = 0
    
    for row in deduped:
        st = row.get('sqli_type', 'unknown').lower()
        sqli_type_dist[st] = sqli_type_dist.get(st, 0) + 1
        
        db = row.get('db_engine', 'unknown').lower()
        db_engine_dist[db] = db_engine_dist.get(db, 0) + 1
        
        label_dist[row.get('label', '0')] = label_dist.get(row.get('label', '0'), 0) + 1
        
        is_obf = str(row.get('is_obfuscated', False))
        is_obf_dist[is_obf] = is_obf_dist.get(is_obf, 0) + 1
        
        try:
            confidence_sum += float(row.get('confidence', 0))
        except:
            pass
        
        if st == 'unknown':
            unknown_count += 1
    
    total = len(deduped)
    avg_conf = confidence_sum / total if total > 0 else 0
    
    print("\n=== FINAL REPORT ===")
    print(f"Total rows: {total}")
    print(f"\nsqli_type distribution (%):")
    for st, cnt in sorted(sqli_type_dist.items(), key=lambda x: -x[1]):
        print(f"  {st}: {cnt} ({cnt*100/total:.1f}%)")
    
    print(f"\ndb_engine distribution (%):")
    for db, cnt in sorted(db_engine_dist.items(), key=lambda x: -x[1]):
        print(f"  {db}: {cnt} ({cnt*100/total:.1f}%)")
    
    print(f"\nlabel distribution:")
    print(f"  label=0: {label_dist['0']} ({label_dist['0']*100/total:.1f}%)")
    print(f"  label=1: {label_dist['1']} ({label_dist['1']*100/total:.1f}%)")
    
    print(f"\nis_obfuscated distribution:")
    print(f"  True: {is_obf_dist['True']} ({is_obf_dist['True']*100/total:.1f}%)")
    print(f"  False: {is_obf_dist['False']} ({is_obf_dist['False']*100/total:.1f}%)")
    
    print(f"\naverage confidence: {avg_conf:.2f}")
    print(f"unknown sqli_type count: {unknown_count} ({unknown_count*100/total:.1f}%)")
    print(f"flagged rows: {len(flagged)}")
    
    os.makedirs('output', exist_ok=True)
    output_path = 'output/master_sqli.csv'
    with open(output_path, 'w', encoding='utf-8', newline='') as f:
        fieldnames = ['payload_raw', 'payload_norm', 'payload_delex', 'label',
                    'sqli_type', 'db_engine', 'is_obfuscated', 'confidence', 'reasoning']
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in deduped:
            writer.writerow({k: row.get(k, '') for k in fieldnames})
    
    print(f"\nOutput: {output_path}")
    return deduped


if __name__ == '__main__':
    merge()