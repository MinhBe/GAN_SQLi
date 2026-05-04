import pandas as pd
import json
import os
import time
import subprocess
import csv
from datetime import datetime
import re

# Config
INPUT_CSV = r"C:\Users\Admin\Documents\GAN\Asset\Guiding\master_unlabeled.csv"
OUTPUT_DIR = r"C:\Users\Admin\Documents\GAN\Asset\Gemini"
BATCH_SIZE = 30
QUOTA_LIMIT = 1500
STOP_THRESHOLD = int(QUOTA_LIMIT * 0.9) # 1350 requests

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

def save_progress(completed_batches, rows_completed, rows_total, request_count):
    progress = {
        "worker": "Gemini-CLI",
        "auth_type": "Terminal Auth (Google Account)",
        "completed_batches": completed_batches,
        "last_completed": max(completed_batches) if completed_batches else 0,
        "last_updated": datetime.now().isoformat(),
        "rows_completed": rows_completed,
        "rows_total": rows_total,
        "request_count": request_count,
        "quota_limit": QUOTA_LIMIT,
        "pct_done": round(rows_completed / rows_total * 100, 1),
        "status": "completed" if rows_completed >= rows_total else "in_progress"
    }
    with open(os.path.join(OUTPUT_DIR, "progress.json"), "w") as f:
        json.dump(progress, f, indent=2)

def save_batch_result(batch_id, ai_response_json):
    results = ai_response_json.get("results", [])
    fname = os.path.join(OUTPUT_DIR, f"result_batch_{batch_id:04d}.csv")
    
    with open(fname, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "row_index", "sqli_type", "db_engine", 
            "confidence", "reasoning"
        ])
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
    # Remove markdown code blocks if present
    s = re.sub(r"```json\s*", "", s)
    s = re.sub(r"```\s*", "", s)
    return s.strip()

def get_cli_response(batch_id, payloads):
    payloads_str = ""
    for p in payloads:
        payloads_str += f"Row {p['row']}: {p['payload']}, label={p['label']}, hint={p['hint']}\n"
        
    full_prompt = f"{SYSTEM_PROMPT}\n\n{USER_PROMPT_TEMPLATE.format(payloads_json=payloads_str, batch_id=f'{batch_id:04d}')}"
    
    try:
        # Sử dụng đường dẫn tuyệt đối để tránh lỗi [WinError 2]
        gemini_path = r"C:\Users\Admin\AppData\Roaming\npm\gemini.cmd"
        
        env = os.environ.copy()
        env["NO_COLOR"] = "1"
        
        result = subprocess.run(
            [gemini_path, "-o", "json", "-p", full_prompt],
            capture_output=True,
            text=True,
            encoding="utf-8",
            env=env
        )
        
        if result.returncode != 0:
            return "ERROR", f"CLI Error (Exit Code {result.returncode}): {result.stderr}"
        
        cli_json = json.loads(result.stdout)
        model_text = cli_json.get("response", "")
        
        if not model_text.strip():
            return "EMPTY_RESPONSE", "Model returned an empty response (possible safety filter)."
        
        # Parse the inner JSON
        clean_text = clean_json_string(model_text)
        try:
            return "SUCCESS", json.loads(clean_text)
        except json.JSONDecodeError:
            return "INVALID_INNER_JSON", f"Model returned invalid JSON format: {model_text[:100]}..."
        
    except json.JSONDecodeError as e:
        return "JSON_ERROR", f"Failed to parse JSON: {str(e)}\nRaw Output: {result.stdout if 'result' in locals() else 'N/A'}"
    except Exception as e:
        return "EXCEPTION", str(e)

def main():
    if not os.path.exists(INPUT_CSV):
        print(f"Error: {INPUT_CSV} not found.")
        return

    df = pd.read_csv(INPUT_CSV)
    df = df.fillna("")
    total_rows = len(df)
    
    progress_file = os.path.join(OUTPUT_DIR, "progress.json")
    completed_batches = []
    rows_completed = 0
    request_count = 0
    
    if os.path.exists(progress_file):
        with open(progress_file, 'r') as f:
            progress = json.load(f)
            completed_batches = progress.get('completed_batches', [])
            rows_completed = progress.get('rows_completed', 0)
            request_count = progress.get('request_count', 0)
            print(f"Resuming from batch {progress.get('last_completed', 0) + 1}, {rows_completed}/{total_rows} rows completed.")
            print(f"Current account request count: {request_count}/{STOP_THRESHOLD} (Threshold: 90% of {QUOTA_LIMIT})")

    for i in range(0, total_rows, BATCH_SIZE):
        if request_count >= STOP_THRESHOLD:
            print(f"\n[QUOTA ALERT] Đã đạt ngưỡng 90% ({request_count} requests).")
            print("Vui lòng đăng nhập tài khoản Google khác trong Gemini CLI và chạy lại kịch bản.")
            print("Lưu ý: Bạn có thể cần reset bộ đếm request_count trong progress.json nếu đổi tài khoản.")
            return

        batch_id = (i // BATCH_SIZE) + 1
        
        if batch_id in completed_batches:
            continue
            
        batch = df.iloc[i : i + BATCH_SIZE]
        payloads = []
        for idx, row in batch.iterrows():
            payloads.append({
                "row": int(idx), 
                "payload": row['payload_norm'], 
                "label": row['label'],
                "hint": row['sqli_type_hint']
            })
            
        success = False
        retries = 0
        
        while not success and retries <= 2:
            print(f"Processing Batch {batch_id:04d}...", end="\r")
            status, result = get_cli_response(batch_id, payloads)
            request_count += 1
            
            if status == "SUCCESS":
                save_batch_result(batch_id, result)
                
                completed_batches.append(batch_id)
                rows_completed += len(batch)
                save_progress(completed_batches, rows_completed, total_rows, request_count)
                
                print(f"Batch {batch_id:04d} done. Progress: {rows_completed}/{total_rows} | Req: {request_count}/{STOP_THRESHOLD}")
                success = True
                # Delay between CLI calls to respect quota (adjustable)
                time.sleep(2) 
                
            elif "429" in str(result) or "Resource has been exhausted" in str(result):
                print(f"\n[QUOTA EXHAUSTED] API báo hết hạn mức (429).")
                save_progress(completed_batches, rows_completed, total_rows, request_count)
                return
                
            else:
                print(f"\nBatch {batch_id:04d}: {status}. Retrying ({retries+1}/3)...")
                print(f"Details: {result}")
                retries += 1
                time.sleep(10)

    print("\nClassification completed.")

if __name__ == "__main__":
    main()
