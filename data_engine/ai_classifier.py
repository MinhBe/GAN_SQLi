import argparse
import csv
import json
import os
import time
import hashlib
from pathlib import Path

PROMPT_SYSTEM = """You are a cybersecurity expert specializing in SQL injection attack analysis. Respond ONLY with valid JSON. No explanation outside JSON."""

PROMPT_USER = """Analyze each SQL injection payload below. For each payload, determine:

1. sqli_type: The PRIMARY attack technique. Valid values ONLY: union_based | error_based | boolean_blind | time_blind | heavy_query | stacked_queries | out_of_band | auth_bypass | second_order | rce | polyglot | lateral | benign | unknown

2. db_engine: Target database if detectable. Valid values ONLY: mysql | mssql | oracle | postgresql | sqlite | generic | unknown

3. confidence: float 0.0-1.0. 1.0=certain, 0.5=likely, 0.0=guessing

4. reasoning: ONE sentence explaining the key indicator

Rules:
- "benign": normal SQL query, NOT an attack
- "unknown": cannot determine with confidence
- Plain English text with no SQL = "benign"
- Focus on TECHNIQUE not just keywords
- Use sqli_type_hint if provided and logical

Input format: [{"id": 1, "payload": "...", "hint": "..."},...]

Respond ONLY with this exact JSON:
{
  "results": [
    {
      "id": 1,
      "sqli_type": "union_based",
      "db_engine": "mysql",
      "confidence": 0.95,
      "reasoning": "Uses UNION SELECT to append query"
    }
  ]
}}"""

VALID_SQLI_TYPES = {
    'union_based', 'error_based', 'boolean_blind', 'time_blind',
    'heavy_query', 'stacked_queries', 'out_of_band', 'auth_bypass',
    'second_order', 'rce', 'polyglot', 'lateral', 'benign', 'unknown'
}
VALID_DB_ENGINES = {
    'mysql', 'mssql', 'oracle', 'postgresql', 'sqlite', 'generic', 'unknown'
}


def get_api_response(client, payload_batch, provider):
    import requests
    
    messages = [
        {"role": "system", "content": PROMPT_SYSTEM},
        {"role": "user", "content": PROMPT_USER + f"\n\nInput: {json.dumps(payload_batch)}"}
    ]
    
    if provider == 'gemini':
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={client}"
        parts = [{"text": m["content"]} for m in messages]
        data = {"contents": [{"parts": parts}]}
        resp = requests.post(url, json=data, timeout=60)
        if resp.status_code == 200:
            return resp.json()['candidates'][0]['content']['parts'][0]['text']
        return None
    
    elif provider == 'openrouter':
        url = "https://openrouter.ai/api/v1/chat/completions"
        headers = {"Authorization": f"Bearer {client}"}
        data = {
            "model": "google/gemini-2.0-flash-exp:free",
            "messages": messages
        }
        resp = requests.post(url, json=data, headers=headers, timeout=60)
        if resp.status_code == 200:
            return resp.json()['choices'][0]['message']['content']
        return None
    
    return None


def parse_response(text):
    try:
        text = text.strip()
        if '```json' in text:
            text = text.split('```json')[1].split('```')[0]
        elif '```' in text:
            text = text.split('```')[1].split('```')[0]
        
        data = json.loads(text)
        return data.get('results', [])
    except:
        return None


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def classify_chunk(chunk_id, provider, api_key):
    chunk_dir = os.path.join(BASE_DIR, 'chunks')
    chunk_path = os.path.join(chunk_dir, f'chunk_{chunk_id}.csv')
    output_dir = os.path.join(BASE_DIR, 'outputs')
    checkpoint_dir = os.path.join(BASE_DIR, 'checkpoints')
    
    output_path = os.path.join(output_dir, f'output_{chunk_id}.csv')
    checkpoint_path = os.path.join(checkpoint_dir, f'chunk_{chunk_id}_progress.json')
    
    os.makedirs(output_dir, exist_ok=True)
    os.makedirs(checkpoint_dir, exist_ok=True)
    
    rows = []
    if os.path.exists(chunk_path):
        with open(chunk_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                rows.append((i, row))
    
    if not rows:
        print(f"Chunk {chunk_id} is empty or not found")
        return True
    
    total_batches = (len(rows) + 29) // 30
    
    start_batch = 0
    if os.path.exists(checkpoint_path):
        with open(checkpoint_path, 'r') as f:
            ckpt = json.load(f)
            start_batch = ckpt.get('last_batch', -1) + 1
            print(f"Resuming chunk {chunk_id} from batch {start_batch}")
    
    results_map = {}
    
    if os.path.exists(output_path):
        with open(output_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                idx = int(row.get('row_idx', 0))
                results_map[idx] = row
    
    for batch_idx in range(start_batch, total_batches):
        batch_start = batch_idx * 30
        batch_end = min(batch_start + 30, len(rows))
        batch_rows = rows[batch_start:batch_end]
        
        payload_batch = []
        for idx, row in batch_rows:
            payload_batch.append({
                'id': idx,
                'payload': row.get('payload_norm', ''),
                'hint': row.get('sqli_type_hint', '')
            })
        
        results = None
        for attempt in range(4):
            try:
                response = get_api_response(api_key, payload_batch, provider)
                if response:
                    results = parse_response(response)
                    if results:
                        break
                
                if attempt < 3:
                    wait_time = [30, 60, 120][attempt]
                    print(f"Retry batch {batch_idx} after {wait_time}s...")
                    time.sleep(wait_time)
            except Exception as e:
                print(f"Batch {batch_idx} error: {e}")
                if attempt < 3:
                    time.sleep([30, 60, 120][attempt])
                continue
        
        if not results:
            results = [
                {'id': p['id'], 'sqli_type': 'unknown', 'db_engine': 'unknown', 
                 'confidence': 0.0, 'reasoning': 'API failed'}
                for p in payload_batch
            ]
        
        result_map_batch = {r['id']: r for r in results}
        
        batch_output = []
        for idx, row in batch_rows:
            result = result_map_batch.get(idx, {})
            row['sqli_type'] = result.get('sqli_type', 'unknown')
            row['db_engine'] = result.get('db_engine', 'unknown')
            row['confidence'] = result.get('confidence', 0.0)
            row['reasoning'] = result.get('reasoning', '')
            row['row_idx'] = str(idx)
            batch_output.append(row)
        
        mode = 'a' if os.path.exists(output_path) else 'w'
        with open(output_path, mode, encoding='utf-8', newline='') as f:
            writer = csv.DictWriter(f, fieldnames=batch_output[0].keys())
            if mode == 'w':
                writer.writeheader()
            writer.writerows(batch_output)
        
        with open(checkpoint_path, 'w') as f:
            json.dump({'last_batch': batch_idx, 'processed': batch_end}, f)
        
        delay = 4 if provider == 'gemini' else 6
        print(f"Chunk {chunk_id} batch {batch_idx+1}/{total_batches} done")
        time.sleep(delay)
    
    return True


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chunk', type=int, required=True)
    parser.add_argument('--provider', choices=['gemini', 'openrouter'], required=True)
    parser.add_argument('--key', type=str, required=True)
    args = parser.parse_args()
    
    classify_chunk(args.chunk, args.provider, args.key)


if __name__ == '__main__':
    main()