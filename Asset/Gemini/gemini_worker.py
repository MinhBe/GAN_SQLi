import pandas as pd
import json
import os
import time
import subprocess
import csv
from datetime import datetime
import re
import argparse

# Config
INPUT_CSV = r"C:\Users\Admin\Documents\GAN\Asset\Guiding\master_unlabeled.csv"
OUTPUT_DIR = r"C:\Users\Admin\Documents\GAN\Asset\Gemini"
BATCH_SIZE = 30
GEMINI_PATH = r"C:\Users\Admin\AppData\Roaming\npm\gemini.cmd"

os.makedirs(OUTPUT_DIR, exist_ok=True)

SYSTEM_PROMPT = "You are a cybersecurity expert specializing in SQL injection analysis. Your task: classify SQL injection payloads accurately. Always respond with ONLY valid JSON. No text outside JSON. No markdown code blocks. Raw JSON only."

USER_PROMPT_TEMPLATE = """Classify each SQL injection payload below.

For each payload determine:
1. sqli_type — PRIMARY attack technique:
   union_based | error_based | boolean_blind | time_blind |
   heavy_query | stacked_queries | out_of_band | auth_bypass |
   second_order | rce | polyglot | lateral | benign | unknown

2. db_engine — target database if detectable:
   mysql | mssql | oracle | postgresql | sqlite | generic | unknown

3. confidence — float 0.0 to 1.0:
   1.0 = certain | 0.7 = likely | 0.5 = unsure | 0.3 = guessing

4. reasoning — ONE short sentence explaining key indicator used

Classification rules:
- Focus on TECHNIQUE, not just keywords
- "benign": normal SQL query, not an attack
- "unknown": genuinely cannot determine
- Plain English text with no SQL structure = "benign"
- Use sqli_type_hint if provided and makes sense
- label=0 rows may still need sqli_type="benign" confirmed

Input (CSV rows — columns: payload_norm, label, sqli_type_hint):
{payloads_json}

Respond with ONLY this JSON (no other text):
{{
  "batch_id": "{batch_id}",
  "results": [
    {{
      "row": 1,
      "sqli_type": "union_based",
      "db_engine": "mysql",
      "confidence": 0.95,
      "reasoning": "UNION SELECT used to append query and extract data"
    }}
  ]
}}
"""

def save_progress(worker_name, completed_batches, rows_completed, total_rows):
    progress = {
        "worker": worker_name,
        "completed_batches": completed_batches,
        "last_completed": max(completed_batches) if completed_batches else 0,
        "last_updated": datetime.now().isoformat(),
        "rows_completed": rows_completed,
        "rows_total": total_rows,
        "status": "in_progress"
    }
    prog_file = os.path.join(OUTPUT_DIR, f"progress_{worker_name}.json")
    with open(prog_file, "w") as f:
        json.dump(progress, f, indent=2)

def save_batch_result(batch_id, ai_response_json):
    results = ai_response_json.get("results", [])
    fname = os.path.join(OUTPUT_DIR, f"result_batch_{batch_id:04d}.csv")
    
    with open(fname, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["row_index", "sqli_type", "db_engine", "confidence", "reasoning"])
        writer.writeheader()
        for r in results:
            writer.writerow({
                "row_index": r.get("row"),
                "sqli_type": r.get("sqli_type", "unknown"),
                "db_engine": r.get("db_engine", "unknown"),
                "confidence": r.get("confidence", 0.0),
                "reasoning": r.get("reasoning", "")
            })

def clean_json_string(s):
    s = re.sub(r"```json\s*", "", s)
    s = re.sub(r"```\s*", "", s)
    return s.strip()

def get_cli_response(batch_id, payloads):
    payloads_str = ""
    for p in payloads:
        payloads_str += f"Row {p['row']}: {p['payload']}, label={p['label']}, hint={p['hint']}\n"
    
    full_prompt = f"{SYSTEM_PROMPT}\n\n{USER_PROMPT_TEMPLATE.format(payloads_json=payloads_str, batch_id=f'{batch_id:04d}')}"
    
    try:
        env = os.environ.copy()
        env["NO_COLOR"] = "1"
        result = subprocess.run([GEMINI_PATH, "-o", "json", "-p", full_prompt], capture_output=True, text=True, encoding="utf-8", env=env)
        
        if result.returncode != 0:
            return "ERROR", result.stderr
        
        cli_json = json.loads(result.stdout)
        model_text = cli_json.get("response", "")
        if not model_text.strip():
            return "EMPTY", "Empty response"
            
        clean_text = clean_json_string(model_text)
        return "SUCCESS", json.loads(clean_text)
    except Exception as e:
        return "EXCEPTION", str(e)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=int, required=True)
    parser.add_argument("--end", type=int, required=True)
    parser.add_argument("--delay", type=int, default=60) # Tăng delay mặc định để chạy song song an toàn
    args = parser.parse_args()

    worker_name = f"worker_{args.start}_{args.end}"
    print(f"[{worker_name}] Started.")

    df = pd.read_csv(INPUT_CSV).fillna("")
    total_rows = len(df)
    
    completed_batches = []
    prog_file = os.path.join(OUTPUT_DIR, f"progress_{worker_name}.json")
    if os.path.exists(prog_file):
        with open(prog_file, 'r') as f:
            completed_batches = json.load(f).get('completed_batches', [])

    for batch_id in range(args.start, args.end + 1):
        if batch_id in completed_batches: continue
            
        start_idx = (batch_id - 1) * BATCH_SIZE
        if start_idx >= total_rows: break
        
        batch = df.iloc[start_idx : start_idx + BATCH_SIZE]
        payloads = [{"row": int(idx), "payload": row['payload_norm'], "label": row['label'], "hint": row['sqli_type_hint']} for idx, row in batch.iterrows()]
        
        success = False
        retries = 0
        while not success and retries <= 2:
            status, result = get_cli_response(batch_id, payloads)
            if status == "SUCCESS":
                save_batch_result(batch_id, result)
                completed_batches.append(batch_id)
                save_progress(worker_name, completed_batches, len(completed_batches)*BATCH_SIZE, total_rows)
                print(f"[{worker_name}] Batch {batch_id:04d} done.")
                success = True
                time.sleep(args.delay)
            elif "429" in str(result) or "exhausted" in str(result):
                print(f"[{worker_name}] 429 Error. Sleeping 120s...")
                time.sleep(120)
                retries += 1
            else:
                print(f"[{worker_name}] {status}. Retrying...")
                retries += 1
                time.sleep(10)

    print(f"[{worker_name}] Completed.")

if __name__ == "__main__":
    main()
