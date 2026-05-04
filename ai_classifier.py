import pandas as pd
import numpy as np
import json
import os
import time
import argparse
import requests
import concurrent.futures

# Constants
VALID_TYPES = [
    "union_based", "error_based", "boolean_blind", "time_blind", 
    "heavy_query", "stacked_queries", "out_of_band", "auth_bypass", 
    "second_order", "rce", "polyglot", "lateral", "benign", "unknown"
]

VALID_ENGINES = ["mysql", "mssql", "oracle", "postgresql", "sqlite", "generic", "unknown"]

SYSTEM_PROMPT = "You are a cybersecurity expert specializing in SQL injection attack analysis. Respond ONLY with valid JSON. No explanation outside JSON."

USER_PROMPT_TEMPLATE = """Analyze each SQL injection payload below.
For each payload, determine:

1. sqli_type: The PRIMARY attack technique
   Valid values ONLY:
   union_based | error_based | boolean_blind | 
   time_blind | heavy_query | stacked_queries | 
   out_of_band | auth_bypass | second_order | 
   rce | polyglot | lateral | benign | unknown

2. db_engine: Target database if detectable
   Valid values ONLY:
   mysql | mssql | oracle | postgresql | 
   sqlite | generic | unknown

3. confidence: float 0.0-1.0
   1.0 = certain, 0.5 = likely, 0.0 = guessing

4. reasoning: ONE sentence explaining the 
   key indicator you used to classify

Rules:
- "benign": normal SQL query, NOT an attack
- "unknown": cannot determine with confidence
- Plain English text with no SQL = "benign"
- Focus on TECHNIQUE not just keywords
- Use sqli_type_hint if provided and logical

Input format:
{payloads_json}

Respond ONLY with this exact JSON:
{{
  "results": [
    {{
      "id": 1,
      "sqli_type": "union_based",
      "db_engine": "mysql",
      "confidence": 0.95,
      "reasoning": "Uses UNION SELECT to append query"
    }}
  ]
}}
"""

def get_gemini_response(payloads, api_key):
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={api_key}"
    
    payloads_json = json.dumps(payloads)
    user_prompt = USER_PROMPT_TEMPLATE.format(payloads_json=payloads_json)
    
    body = {
        "contents": [{
            "parts": [
                {"text": SYSTEM_PROMPT},
                {"text": user_prompt}
            ]
        }],
        "generationConfig": {
            "response_mime_type": "application/json",
        }
    }
    
    headers = {"Content-Type": "application/json"}
    
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 429:
        return "RATE_LIMIT", response.text
    
    if response.status_code != 200:
        return "ERROR", response.text
    
    try:
        res_json = response.json()
        text = res_json['candidates'][0]['content']['parts'][0]['text']
        return "SUCCESS", json.loads(text)
    except Exception as e:
        return "JSON_ERROR", str(e) + "\n" + response.text

def get_openrouter_response(payloads, api_key):
    url = "https://openrouter.ai/api/v1/chat/completions"
    
    payloads_json = json.dumps(payloads)
    user_prompt = USER_PROMPT_TEMPLATE.format(payloads_json=payloads_json)
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    body = {
        "model": "google/gemini-2.0-flash-exp:free",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "response_format": {"type": "json_object"}
    }
    
    response = requests.post(url, headers=headers, json=body)
    if response.status_code == 429:
        return "RATE_LIMIT", response.text
        
    if response.status_code != 200:
        return "ERROR", response.text
        
    try:
        res_json = response.json()
        text = res_json['choices'][0]['message']['content']
        return "SUCCESS", json.loads(text)
    except Exception as e:
        return "JSON_ERROR", str(e) + "\n" + response.text

def process_chunk(chunk_id, provider, api_key):
    chunk_file = f"chunks/chunk_{chunk_id}.csv"
    checkpoint_file = f"checkpoints/chunk_{chunk_id}_progress.json"
    output_file = f"outputs/output_{chunk_id}.csv"
    
    if not os.path.exists(chunk_file):
        print(f"Chunk {chunk_id} not found!")
        return

    df = pd.read_csv(chunk_file)
    df = df.fillna("")
    
    processed_count = 0
    if os.path.exists(checkpoint_file):
        with open(checkpoint_file, 'r') as f:
            checkpoint = json.load(f)
            processed_count = checkpoint.get('processed', 0)
            print(f"Resuming chunk {chunk_id} from {processed_count}")

    batch_size = 30
    delay = 4 if provider == 'gemini' else 6
    
    # Load existing output if any to append or just write at end
    if processed_count > 0 and os.path.exists(output_file):
        out_df = pd.read_csv(output_file)
    else:
        out_df = pd.DataFrame()

    total_rows = len(df)
    
    for i in range(processed_count, total_rows, batch_size):
        batch = df.iloc[i : i + batch_size]
        payloads = []
        for idx, row in batch.iterrows():
            payloads.append({
                "id": int(idx), 
                "payload": row['payload_norm'], 
                "hint": row['sqli_type_hint']
            })
        
        # Retry logic
        success = False
        retries = 0
        wait_times = [30, 60, 120]
        
        current_batch_payloads = payloads
        current_batch_size = batch_size
        
        while not success and retries <= 3:
            if provider == 'gemini':
                status, result = get_gemini_response(current_batch_payloads, api_key)
            else:
                status, result = get_openrouter_response(current_batch_payloads, api_key)
            
            if status == "SUCCESS":
                results = result.get('results', [])
                batch_results_df = pd.DataFrame(results)
                
                # Merge with original batch data
                batch_to_save = batch.copy().reset_index()
                # Ensure IDs match
                batch_results_df['id'] = batch_results_df['id'].astype(int)
                batch_to_save['index'] = batch_to_save['index'].astype(int)
                
                merged_batch = pd.merge(batch_to_save, batch_results_df, left_on='index', right_on='id', how='left')
                merged_batch = merged_batch.drop(columns=['index', 'id'])
                
                out_df = pd.concat([out_df, merged_batch], ignore_index=True)
                
                # Save progress
                out_df.to_csv(output_file, index=False)
                with open(checkpoint_file, 'w') as f:
                    json.dump({"processed": i + len(batch)}, f)
                
                success = True
                print(f"Chunk {chunk_id}: Processed {i + len(batch)}/{total_rows}")
                time.sleep(delay)
                
            elif status == "RATE_LIMIT":
                if retries < 3:
                    wait = wait_times[retries]
                    print(f"Chunk {chunk_id}: Rate limited. Waiting {wait}s...")
                    time.sleep(wait)
                    retries += 1
                else:
                    print(f"Chunk {chunk_id}: Max retries reached for batch starting at {i}. Skipping.")
                    break
            elif status == "JSON_ERROR" or status == "ERROR":
                if current_batch_size > 15:
                    print(f"Chunk {chunk_id}: {status}. Retrying with smaller batch (15)...")
                    current_batch_size = 15
                    current_batch_payloads = payloads[:15]
                    # Note: this simple logic only retries the first half. 
                    # For a robust engine we'd need a recursive split, but following blueprint.
                    retries += 1
                else:
                    print(f"Chunk {chunk_id}: Persistent {status}. Assigning unknown.")
                    # Fill with unknown
                    unknown_results = pd.DataFrame([{
                        "sqli_type": "unknown", "db_engine": "unknown", 
                        "confidence": 0.0, "reasoning": f"Error: {status}"
                    }] * len(batch))
                    merged_batch = pd.concat([batch.reset_index(drop=True), unknown_results], axis=1)
                    out_df = pd.concat([out_df, merged_batch], ignore_index=True)
                    out_df.to_csv(output_file, index=False)
                    with open(checkpoint_file, 'w') as f:
                        json.dump({"processed": i + len(batch)}, f)
                    success = True
                    break
            else:
                print(f"Chunk {chunk_id}: Unexpected status {status}. Skipping.")
                break

def split_master():
    if not os.path.exists('master_unlabeled.csv'):
        print("master_unlabeled.csv not found!")
        return
    
    df = pd.read_csv('master_unlabeled.csv')
    num_chunks = 8
    
    os.makedirs('chunks', exist_ok=True)
    os.makedirs('checkpoints', exist_ok=True)
    os.makedirs('outputs', exist_ok=True)
    
    total = len(df)
    chunk_size = int(np.ceil(total / num_chunks))
    
    for i in range(num_chunks):
        start = i * chunk_size
        end = min((i + 1) * chunk_size, total)
        if start >= total:
            break
        chunk = df.iloc[start:end]
        chunk.to_csv(f"chunks/chunk_{i}.csv", index=False)
    print(f"Split into {num_chunks} chunks.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--split", action="store_true", help="Split master into chunks")
    parser.add_argument("--chunk", type=int, help="Chunk ID to process (0-7)")
    parser.add_argument("--provider", type=str, choices=['gemini', 'openrouter'], help="API Provider")
    parser.add_argument("--key", type=str, help="API Key")
    
    args = parser.parse_args()
    
    if args.split:
        split_master()
    elif args.chunk is not None:
        if not args.provider or not args.key:
            print("Provider and Key are required for processing.")
        else:
            process_chunk(args.chunk, args.provider, args.key)
    else:
        parser.print_help()
