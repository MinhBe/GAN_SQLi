import re
import csv
import os
import hashlib
import html
from urllib.parse import unquote
from xml.etree import ElementTree as ET

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SOURCES = {
    'sqli_dataset': os.path.join(BASE_DIR, '../Asset/Data/data/raw/sqli_dataset.csv'),
    'sqliv3': os.path.join(BASE_DIR, '../Asset/Data/sqliv5_dataset/SQLiV3.csv'),
    'sqliv2': os.path.join(BASE_DIR, '../Asset/Data/sqliv5_dataset/sqliv2.csv'),
    'sqli': os.path.join(BASE_DIR, '../Asset/Data/sqliv5_dataset/sqli.csv'),
    'bccc': os.path.join(BASE_DIR, '../Asset/Data/BCCC-SFU-SQLInj-2023.csv'),
    'sqlmap': os.path.join(BASE_DIR, '../Asset/Data/sqlmap_payloads/data/xml/payloads'),
    'seclists': os.path.join(BASE_DIR, '../Asset/Data/seclists_sqli/Fuzzing/Databases/SQLi'),
    'advanced': os.path.join(BASE_DIR, '../Asset/Data/data/raw/advanced_sqli.csv'),
}

SQL_KEYWORDS = re.compile(r'\b(SELECT|INSERT|UPDATE|DELETE|FROM|WHERE|JOIN|ORDER|GROUP|HAVING|UNION|CREATE|DROP)\b', re.IGNORECASE)
ORACLE_FILES = ['Oracle.fuzzdb.txt', 'OracleDB-SID.txt']

EVASION_PATTERNS = {
    'url_encoding': r'%[0-9a-fA-F]{2}',
    'whitespace_subst': r'%09|%0a|%0d|\+',
    'mysql_versioned': r'/\*![0-9]{5}',
    'comment_obfus': r'/\*.*?\*/',
    'hex_encoding': r'0x[0-9a-fA-F]+',
    'case_mixing': r'(?:(?:[A-Z][a-z])|(?:[a-z][A-Z])){2,}',
}

def hash_payload(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()

output_rows = []
source_stats = {}


def load_sqli_dataset(filepath):
    rows = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sentence = row.get('Sentence', '').strip()
            label = int(row.get('Label', 0))
            if sentence:
                rows.append({'payload_raw': sentence, 'label': label, 'source': 'sqli_dataset'})
    source_stats['sqli_dataset'] = len(rows)
    return rows


def load_sqliv3(filepath):
    rows = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:
                sentence = row[0].strip()
                label = int(row[1]) if row[1].strip().isdigit() else 0
                if sentence:
                    rows.append({'payload_raw': sentence, 'label': label, 'source': 'sqliv3'})
    source_stats['sqliv3'] = len(rows)
    return rows


def load_sqliv2(filepath):
    rows = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sentence = row.get('Sentence', '').strip()
            label = int(row.get('Label', 0))
            if not sentence:
                continue
            if label == 0:
                if not SQL_KEYWORDS.search(sentence):
                    continue
            rows.append({'payload_raw': sentence, 'label': label, 'source': 'sqliv2'})
    source_stats['sqliv2'] = len(rows)
    return rows


def load_sqli_simple(filepath):
    rows = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sentence = row.get('Sentence', '').strip()
            label = int(row.get('Label', 0))
            if sentence:
                rows.append({'payload_raw': sentence, 'label': label, 'source': 'sqli'})
    source_stats['sqli'] = len(rows)
    return rows


def load_bccc(filepath):
    rows = []
    pattern = re.compile(r'WHERE username = ""(.+?)""')
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if len(row) >= 2:
                data = row[1].strip() if len(row) > 1 else ''
                if not data:
                    continue
                match = pattern.search(data)
                payload = match.group(1) if match else data
                rows.append({'payload_raw': payload, 'label': 1, 'source': 'bccc'})
    source_stats['bccc'] = len(rows)
    return rows


def load_sqlmap(xml_dir):
    rows = []
    type_hints = {
        'boolean_blind.xml': 'boolean_blind',
        'error_based.xml': 'error_based',
        'time_blind.xml': 'time_blind',
        'union_query.xml': 'union_based',
        'stacked_queries.xml': 'stacked_queries',
        'inline_query.xml': 'inline_query',
    }
    for xml_file in os.listdir(xml_dir):
        if not xml_file.endswith('.xml'):
            continue
        filepath = os.path.join(xml_dir, xml_file)
        sqli_hint = type_hints.get(xml_file, '')
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            for test in root.findall('.//test'):
                vector_elem = test.find('vector')
                payload_elem = test.find('request/payload')
                vector = vector_elem.text if vector_elem is not None and vector_elem.text else ''
                payload = payload_elem.text if payload_elem is not None and payload_elem.text else ''
                if payload or vector:
                    combined = (payload + ' ' + vector).strip()
                    rows.append({
                        'payload_raw': combined,
                        'label': 1,
                        'sqli_type_hint': sqli_hint,
                        'source': 'sqlmap'
                    })
        except ET.ParseError:
            continue
    source_stats['sqlmap'] = len(rows)
    return rows


def load_seclists(txt_dir):
    rows = []
    for filename in os.listdir(txt_dir):
        if filename not in ORACLE_FILES:
            continue
        filepath = os.path.join(txt_dir, filename)
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                rows.append({'payload_raw': line, 'label': 1, 'source': 'seclists'})
    source_stats['seclists'] = len(rows)
    return rows


def load_advanced(filepath):
    rows = []
    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
        reader = csv.DictReader(f)
        for row in reader:
            sentence = row.get('Sentence', '').strip()
            label = int(row.get('Label', 0))
            sqli_type = row.get('Type', '').strip()
            if sentence:
                rows.append({
                    'payload_raw': sentence,
                    'label': label,
                    'sqli_type_hint': sqli_type,
                    'source': 'advanced'
                })
    source_stats['advanced'] = len(rows)
    return rows


def split_chunks(processed, num_chunks=8):
    chunk_size = len(processed) // num_chunks
    chunks = []
    for i in range(num_chunks):
        start = i * chunk_size
        end = start + chunk_size if i < num_chunks - 1 else len(processed)
        chunks.append(processed[start:end])
    return chunks


def flag_evasion(payload):
    for name, pattern in EVASION_PATTERNS.items():
        if name == 'case_mixing':
            test_payload = re.sub(r'\bSELECT\b', '', payload)
            if re.search(pattern, test_payload):
                return True
        elif re.search(pattern, payload):
            return True
    return False


def normalize(payload):
    s = payload
    prev = None
    while '%' in s and s != prev:
        prev = s
        try:
            s = unquote(s)
        except:
            break
    s = html.unescape(s)
    s = re.sub(r'/\*.*?\*/', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip()
    return s


def delexicalize(payload):
    s = re.sub(r"'[^']*'", '<STR>', payload)
    s = re.sub(r'"[^"]*"', '<STR>', s)
    s = re.sub(r'\b\d+\.?\d*\b', '<NUM>', s)
    s = re.sub(r'\b(users|admin|accounts|members|login)\b', '<TABLE>', s, flags=re.IGNORECASE)
    s = re.sub(r'\b(username|password|email|id|name)\b', '<COL>', s, flags=re.IGNORECASE)
    return s


def hash_payload(s):
    return hashlib.sha256(s.encode('utf-8')).hexdigest()


def process():
    import json
    
    all_rows = []
    
    print("Loading sources...")
    all_rows.extend(load_sqli_dataset(SOURCES['sqli_dataset']))
    all_rows.extend(load_sqliv3(SOURCES['sqliv3']))
    all_rows.extend(load_sqliv2(SOURCES['sqliv2']))
    all_rows.extend(load_sqli_simple(SOURCES['sqli']))
    all_rows.extend(load_bccc(SOURCES['bccc']))
    all_rows.extend(load_sqlmap(SOURCES['sqlmap']))
    all_rows.extend(load_seclists(SOURCES['seclists']))
    all_rows.extend(load_advanced(SOURCES['advanced']))
    
    print(f"Total loaded: {len(all_rows)} rows")
    for src, count in source_stats.items():
        print(f"  {src}: {count}")
    
    checkpoint_path = os.path.join(BASE_DIR, 'output/prepare_checkpoint.json')
    start_idx = 0
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, 'r') as f:
            ckpt = json.load(f)
            start_idx = ckpt.get('processed', 0)
            print(f"Resuming from row {start_idx}")
    
    processed = []
    seen_raw = set()
    seen_norm = set()
    
    for i, row in enumerate(all_rows):
        if i < start_idx:
            continue
        
        raw = row.get('payload_raw', '')
        if len(raw) < 3:
            continue
        if re.match(r'^[\d\*\?\@]+$', raw):
            continue
        
        h_raw = hash_payload(raw.lower().strip())
        if h_raw in seen_raw:
            continue
        seen_raw.add(h_raw)
        
        norm = normalize(raw)
        h_norm = hash_payload(norm.lower().strip())
        if h_norm in seen_norm:
            continue
        seen_norm.add(h_norm)
        
        is_obf = flag_evasion(raw)
        delex = delexicalize(norm)
        
        processed.append({
            'payload_raw': raw,
            'payload_norm': norm,
            'payload_delex': delex,
            'label': row.get('label', 1),
            'is_obfuscated': is_obf,
            'sqli_type_hint': row.get('sqli_type_hint', ''),
            'source': row.get('source', '')
        })
        
        if i > 0 and i % 10000 == 0:
            with open(checkpoint_path, 'w') as f:
                json.dump({'processed': i}, f)
            print(f"Processed {i} rows...")
    
    print(f"After processing: {len(processed)} rows")
    
    label_0 = sum(1 for r in processed if r['label'] == 0)
    label_1 = sum(1 for r in processed if r['label'] == 1)
    is_obf = sum(1 for r in processed if r['is_obfuscated'])
    has_hint = sum(1 for r in processed if r.get('sqli_type_hint'))
    
    print(f"label=0: {label_0}, label=1: {label_1}")
    print(f"is_obfuscated: {is_obf}")
    print(f"has sqli_type_hint: {has_hint}")
    
    chunks = split_chunks(processed, 8)
    os.makedirs(os.path.join(BASE_DIR, 'output'), exist_ok=True)
    os.makedirs(os.path.join(BASE_DIR, 'chunks'), exist_ok=True)
    
    chunks_dir = os.path.join(BASE_DIR, 'chunks')
    output_dir = os.path.join(BASE_DIR, 'output')
    
    for i, chunk in enumerate(chunks):
        with open(os.path.join(chunks_dir, f'chunk_{i}.csv'), 'w', encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=[
                'payload_raw', 'payload_norm', 'payload_delex',
                'label', 'is_obfuscated', 'sqli_type_hint', 'source'
            ])
            writer.writeheader()
            writer.writerows(chunk)
        print(f"Chunk {i}: {len(chunk)} rows")
    
    with open(os.path.join(output_dir, 'master_unlabeled.csv'), 'w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=[
            'payload_raw', 'payload_norm', 'payload_delex',
            'label', 'is_obfuscated', 'sqli_type_hint', 'source'
        ])
        writer.writeheader()
        writer.writerows(processed)
    
    print("Output: output/master_unlabeled.csv")
    return processed


if __name__ == '__main__':
    process()