import csv
import json
import os
import re

BATCHES_DIR = r"C:\Users\Admin\Documents\GAN\Asset\Data\batches"
RESULTS_DIR = r"C:\Users\Admin\Documents\GAN\Asset\Data\results"
PROGRESS_FILE = r"C:\Users\Admin\Documents\GAN\Asset\Opencode\progress.json"

def classify_payload(payload, label, sqli_type_hint):
    """Classify a single SQL injection payload"""
    payload_lower = payload.lower()
    
    # Oracle XML type - error based
    if 'xmltype' in payload_lower:
        return {
            'sqli_type': 'error_based',
            'db_engine': 'oracle',
            'confidence': 0.95,
            'reasoning': 'xmltype Oracle error extraction'
        }
    
    # Oracle dbms_utility - out of band
    if 'dbms_utility.sqlid_to_sqlhash' in payload_lower:
        return {
            'sqli_type': 'out_of_band',
            'db_engine': 'oracle',
            'confidence': 0.95,
            'reasoning': 'dbms_utility Oracle DNS exfiltration'
        }
    
    # Oracle ctxsys - error based
    if 'ctxsys.drithsx.sn' in payload_lower:
        return {
            'sqli_type': 'error_based',
            'db_engine': 'oracle',
            'confidence': 0.95,
            'reasoning': 'ctxsys Oracle error extraction'
        }
    
    # Oracle utl_inaddr - out of band
    if 'utl_inaddr.get_host_address' in payload_lower:
        return {
            'sqli_type': 'out_of_band',
            'db_engine': 'oracle',
            'confidence': 0.95,
            'reasoning': 'utl_inaddr Oracle DNS exfiltration'
        }
    
    # PostgreSQL generate_series - boolean blind
    if 'generate_series' in payload_lower:
        return {
            'sqli_type': 'boolean_blind',
            'db_engine': 'postgresql',
            'confidence': 0.9,
            'reasoning': 'generate_series PostgreSQL blind'
        }
    
    # PostgreSQL cast ::text with case
    if '::text' in payload_lower and 'case when' in payload_lower:
        return {
            'sqli_type': 'boolean_blind',
            'db_engine': 'postgresql',
            'confidence': 0.9,
            'reasoning': 'PostgreSQL cast boolean blind'
        }
    
    # SQL Server convert(int,...)
    if 'convert(int' in payload_lower:
        return {
            'sqli_type': 'boolean_blind',
            'db_engine': 'mssql',
            'confidence': 0.9,
            'reasoning': 'convert int SQL Server blind'
        }
    
    # SQL Server char() with case
    if 'char(' in payload_lower and 'case when' in payload_lower:
        return {
            'sqli_type': 'boolean_blind',
            'db_engine': 'mssql',
            'confidence': 0.9,
            'reasoning': 'char case SQL Server blind'
        }
    
    # MySQL heavy query with if
    if 'select 2* ( if' in payload_lower or 'select 2* (if' in payload_lower:
        return {
            'sqli_type': 'heavy_query',
            'db_engine': 'mysql',
            'confidence': 0.9,
            'reasoning': 'MySQL heavy query with if'
        }
    
    # MySQL elt function
    if 'elt(' in payload_lower:
        return {
            'sqli_type': 'boolean_blind',
            'db_engine': 'mysql',
            'confidence': 0.85,
            'reasoning': 'elt function MySQL blind'
        }
    
    # Generic case when (boolean blind)
    if 'case when' in payload_lower:
        return {
            'sqli_type': 'boolean_blind',
            'db_engine': 'generic',
            'confidence': 0.8,
            'reasoning': 'case when boolean blind'
        }
    
    # If label=0, it's benign
    if label == 0:
        return {
            'sqli_type': 'benign',
            'db_engine': 'generic',
            'confidence': 1.0,
            'reasoning': 'Normal SQL query'
        }
    
    # Default
    return {
        'sqli_type': 'unknown',
        'db_engine': 'unknown',
        'confidence': 0.5,
        'reasoning': 'Unable to determine technique'
    }

def process_batch(batch_num):
    """Process a single batch file"""
    batch_file = os.path.join(BATCHES_DIR, f"batch_{batch_num:04d}.csv")
    result_file = os.path.join(RESULTS_DIR, f"result_batch_{batch_num:04d}.csv")
    
    if not os.path.exists(batch_file):
        print(f"Batch {batch_num} not found, skipping...")
        return False
    
    results = []
    with open(batch_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            row_index = int(row['row_index'])
            payload = row['payload_norm']
            label = int(row['label'])
            sqli_type_hint = row.get('sqli_type_hint', '')
            
            classification = classify_payload(payload, label, sqli_type_hint)
            
            results.append({
                'row_index': row_index,
                'sqli_type': classification['sqli_type'],
                'db_engine': classification['db_engine'],
                'confidence': classification['confidence'],
                'reasoning': classification['reasoning']
            })
    
    # Write results
    with open(result_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=['row_index', 'sqli_type', 'db_engine', 'confidence', 'reasoning'])
        writer.writeheader()
        writer.writerows(results)
    
    print(f"Processed batch {batch_num}: {len(results)} rows -> {result_file}")
    return True

def update_progress(start_batch, end_batch):
    """Update progress.json"""
    with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
        progress = json.load(f)
    
    # Add completed batches
    for b in range(start_batch, end_batch + 1):
        if b not in progress['completed_batches']:
            progress['completed_batches'].append(b)
    
    progress['last_completed'] = end_batch
    progress['rows_completed'] = end_batch * 30
    progress['status'] = 'in_progress'
    progress['last_updated'] = '2026-05-04T11:00:00'
    
    with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
        json.dump(progress, f, indent=4)
    
    print(f"Updated progress.json: last_completed={end_batch}, rows_completed={end_batch * 30}")

if __name__ == "__main__":
    # Process batches 1046 to 1055
    start = 1046
    end = 1055
    
    print(f"Processing batches {start} to {end}...")
    for batch_num in range(start, end + 1):
        process_batch(batch_num)
    
    update_progress(start, end)
    print("Done!")
