import pandas as pd
import numpy as np
import re
import os
import glob
import xml.etree.ElementTree as ET
from urllib.parse import unquote
import html
import hashlib

def flag_evasion(payload):
    """PHẢI chạy TRƯỚC normalize"""
    if not isinstance(payload, str):
        return False
    
    rules = {
        'url_encoding': r"%[0-9a-fA-F]{2}",
        'whitespace_subst': r"%09|%0a|%0d|\+",
        'mysql_versioned': r"/\*![0-9]{5}",
        'comment_obfus': r"/\*.*?\*/",
        'hex_encoding': r"0x[0-9a-fA-F]+",
        'case_mixing': r"(?:(?:[A-Z][a-z])|(?:[a-z][A-Z])){2,}"
    }
    
    # Check case_mixing specifically to NOT match "SELECT"
    # The regex r"(?:(?:[A-Z][a-z])|(?:[a-z][A-Z])){2,}" matches things like "SeLeCt"
    
    for name, pattern in rules.items():
        if re.search(pattern, payload):
            return True
    return False

def normalize(payload):
    """Chạy SAU flag_evasion"""
    if not isinstance(payload, str):
        return ""
    
    s = payload
    # a. URL decode (vòng lặp an toàn)
    prev = None
    while "%" in s and s != prev:
        prev = s
        s = unquote(s)
    
    # b. HTML decode
    s = html.unescape(s)
    
    # c. Collapse comments
    s = re.sub(r'/\*.*?\*/', ' ', s)
    
    # d. Normalize whitespace
    s = re.sub(r'\s+', ' ', s).strip()
    
    return s

def delexicalize(payload):
    if not isinstance(payload, str):
        return ""
    
    s = payload
    s = re.sub(r"'[^']*'", '<STR>', s)
    s = re.sub(r'"[^"]*"', '<STR>', s)
    s = re.sub(r'\b\d+\.?\d*\b', '<NUM>', s)
    
    # Table names
    s = re.sub(r'\b(users|admin|accounts|members|login)\b', '<TABLE>', s, flags=re.IGNORECASE)
    # Column names
    s = re.sub(r'\b(username|password|email|id|name)\b', '<COL>', s, flags=re.IGNORECASE)
    
    return s

def load_source_1():
    path = 'Asset/Data/data/raw/sqli_dataset.csv'
    df = pd.read_csv(path)
    if 'Sentence' not in df.columns:
        df = pd.read_csv(path, header=None, names=['payload_raw', 'label'])
    else:
        df = df[['Sentence', 'Label']].rename(columns={'Sentence': 'payload_raw', 'Label': 'label'})
    df['source'] = 'sqli_dataset.csv'
    df['sqli_type_hint'] = ""
    return df

def load_source_2():
    path = 'Asset/Data/sqliv5_dataset/SQLiV3.csv'
    # Source 2: No header based on inspection
    df = pd.read_csv(path, usecols=[0, 1], header=None)
    df.columns = ['payload_raw', 'label']
    df['source'] = 'SQLiV3.csv'
    df['sqli_type_hint'] = ""
    return df

def load_source_3():
    path = 'Asset/Data/sqliv5_dataset/sqliv2.csv'
    try:
        df = pd.read_csv(path, encoding='utf-16', header=None)
    except:
        df = pd.read_csv(path, encoding='utf-8', errors='ignore', header=None)
    
    df = df.iloc[:, [0, 1]]
    df.columns = ['payload_raw', 'label']
    
    # Lọc label=0 — CHỈ GIỮ dòng label=0 có ít nhất 1 SQL keyword
    keywords = r"SELECT|INSERT|UPDATE|DELETE|FROM|WHERE|JOIN|ORDER|GROUP|HAVING|UNION|CREATE|DROP"
    
    # Ensure label is numeric for filtering
    df['label'] = pd.to_numeric(df['label'], errors='coerce')
    df = df.dropna(subset=['label'])
    
    mask_benign = df['label'] == 0
    mask_has_keyword = df['payload_raw'].str.contains(keywords, case=False, na=False, regex=True)
    
    df_benign = df[mask_benign & mask_has_keyword]
    df_malicious = df[df['label'] == 1]
    
    df = pd.concat([df_benign, df_malicious])
    df['source'] = 'sqliv2.csv'
    df['sqli_type_hint'] = ""
    return df

def load_source_4():
    path = 'Asset/Data/sqliv5_dataset/sqli.csv'
    try:
        df = pd.read_csv(path, encoding='utf-16', header=None)
    except:
        df = pd.read_csv(path, encoding='utf-8', errors='ignore', header=None)
    
    df = df.iloc[:, [0, 1]]
    df.columns = ['payload_raw', 'label']
    df['source'] = 'sqli.csv'
    df['sqli_type_hint'] = ""
    return df

def load_source_5():
    path = 'Asset/Data/BCCC-SFU-SQLInj-2023.csv'
    df = pd.read_csv(path)
    
    def extract_payload(text):
        if not isinstance(text, str): return text
        pattern = r'WHERE username = ""(.+?)""'
        match = re.search(pattern, text)
        if match:
            return match.group(1)
        return text

    df['payload_raw'] = df['Data'].apply(extract_payload)
    df['label'] = 1
    df['source'] = 'BCCC-SFU-SQLInj-2023.csv'
    df['sqli_type_hint'] = ""
    return df[['payload_raw', 'label', 'source', 'sqli_type_hint']]

def load_source_6():
    xml_dir = 'Asset/Data/sqlmap_payloads/data/xml/payloads/'
    xml_files = glob.glob(os.path.join(xml_dir, "*.xml"))
    data = []
    
    for file_path in xml_files:
        hint = os.path.basename(file_path).replace('.xml', '')
        tree = ET.parse(file_path)
        root = tree.getroot()
        
        # In sqlmap XML, payloads are often inside <test><request><payload> or similar
        # Based on instructions, extract <payload> and <vector>
        for test in root.findall('.//test'):
            payload_tag = test.find('.//payload')
            vector_tag = test.find('.//vector')
            
            if payload_tag is not None and payload_tag.text:
                data.append({
                    'payload_raw': payload_tag.text,
                    'label': 1,
                    'source': f'sqlmap_{os.path.basename(file_path)}',
                    'sqli_type_hint': hint
                })
            
            if vector_tag is not None and vector_tag.text:
                data.append({
                    'payload_raw': vector_tag.text,
                    'label': 1,
                    'source': f'sqlmap_{os.path.basename(file_path)}',
                    'sqli_type_hint': hint
                })
                
    return pd.DataFrame(data)

def load_source_7():
    # Only take Oracle*.txt files
    base_dir = 'Asset/Data/seclists_sqli/Fuzzing/Databases/'
    oracle_files = glob.glob(os.path.join(base_dir, "**/Oracle*.txt"), recursive=True)
    data = []
    
    for file_path in oracle_files:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    data.append({
                        'payload_raw': line,
                        'label': 1,
                        'source': f'seclists_{os.path.basename(file_path)}',
                        'sqli_type_hint': ""
                    })
    return pd.DataFrame(data)

def load_source_8():
    path = 'Asset/Data/data/raw/advanced_sqli.csv'
    df = pd.read_csv(path)
    # Cột: Sentence, Label, Source, Type
    df = df.rename(columns={'Sentence': 'payload_raw', 'Label': 'label', 'Type': 'sqli_type_hint'})
    df['source'] = 'advanced_sqli.csv'
    return df[['payload_raw', 'label', 'source', 'sqli_type_hint']]

def main():
    print("--- Loading Sources ---")
    sources = [
        load_source_1(), load_source_2(), load_source_3(), load_source_4(),
        load_source_5(), load_source_6(), load_source_7(), load_source_8()
    ]
    
    for i, df in enumerate(sources, 1):
        print(f"Source {i}: {len(df)} rows")
        
    master_df = pd.concat(sources, ignore_index=True)
    print(f"Total raw rows: {len(master_df)}")
    
    # Ensure label is numeric 0/1
    master_df['label'] = pd.to_numeric(master_df['label'], errors='coerce')
    master_df = master_df.dropna(subset=['label'])
    master_df['label'] = master_df['label'].astype(int)
    master_df = master_df[master_df['label'].isin([0, 1])]
    
    # Bước 2: flag_evasion
    print("Flagging evasion...")
    master_df['is_obfuscated'] = master_df['payload_raw'].apply(flag_evasion)
    
    # Bước 3: normalize
    print("Normalizing...")
    master_df['payload_norm'] = master_df['payload_raw'].apply(normalize)
    
    # Bước 4: delexicalize
    print("Delexicalizing...")
    master_df['payload_delex'] = master_df['payload_norm'].apply(delexicalize)
    
    # Bước 5: Deduplication
    print("Deduplicating...")
    # Level 1: exact raw
    master_df = master_df.drop_duplicates(subset=['payload_raw'])
    # Level 2: norm.lower().strip()
    master_df['norm_hash'] = master_df['payload_norm'].str.lower().str.strip()
    master_df = master_df.drop_duplicates(subset=['norm_hash'])
    master_df = master_df.drop(columns=['norm_hash'])
    
    # Bước 6: Filter rác
    print("Filtering junk...")
    # Bỏ len < 3
    master_df = master_df[master_df['payload_raw'].str.len() >= 3]
    # Bỏ chỉ có số hoặc ký tự đặc biệt đơn lẻ
    master_df = master_df[~master_df['payload_raw'].str.match(r'^[\d\W]$', na=False)]
    
    # Save output
    output_path = 'master_unlabeled.csv'
    master_df.to_csv(output_path, index=False)
    print(f"Final rows: {len(master_df)}")
    
    # Report
    print("\n--- FINAL REPORT ---")
    print(f"Total rows: {len(master_df)}")
    print("\nLabel Distribution:")
    print(master_df['label'].value_counts(normalize=True) * 100)
    print("\nObfuscation Distribution:")
    print(master_df['is_obfuscated'].value_counts(normalize=True) * 100)
    print(f"\nRows with sqli_type_hint: {master_df['sqli_type_hint'].replace('', np.nan).notna().sum()}")
    
    # Source distribution
    print("\nSource Distribution:")
    print(master_df['source'].value_counts())

if __name__ == "__main__":
    main()
