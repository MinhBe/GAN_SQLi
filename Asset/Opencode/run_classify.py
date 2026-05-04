import pandas as pd
import json
import os
import time
import requests
import sys

BATCH_DIR = r"C:\Users\Admin\Documents\GAN\Asset\Data\batches"
RESULTS_DIR = r"C:\Users\Admin\Documents\GAN\Asset\Data\results"
PROGRESS_FILE = r"C:\Users\Admin\Documents\GAN\Asset\Opencode\progress.json"

SYSTEM_PROMPT = """You are a cybersecurity expert specializing in SQL injection analysis.
Your task: classify SQL injection payloads accurately.
Always respond with ONLY valid JSON. No text outside JSON.
No markdown code blocks. Raw JSON only."""

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
- label=0 rows should be sqli_type="benign" confirmed
- label=1 rows cannot be "benign"

Input (CSV rows — columns: payload_norm, label, row_index):
{csv_content}

Respond with ONLY this JSON (no other text):
{{
  "batch_id": "{batch_id}",
  "total_rows": {total_rows},
  "results": [
    {{
      "row": 0,
      "sqli_type": "union_based",
      "db_engine": "mysql",
      "confidence": 0.95,
      "reasoning": "UNION SELECT used"
    }}
  ]
}}"""

os.makedirs(RESULTS_DIR, exist_ok=True)

def load_progress():
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, "r") as f:
            return json.load(f)
    return {
        "total_batches": 1000,
        "completed_batches": [],
        "failed_batches": [],
        "last_completed": 0,
        "status": "pending"
    }

def save_progress(progress):
    progress["last_updated"] = time.strftime("%Y-%m-%d %H:%M:%S")
    with open(PROGRESS_FILE, "w") as f:
        json.dump(progress, f, indent=2, ensure_ascii=False)

def classify_batch(batch_num, api_key):
    batch_file = os.path.join(BATCH_DIR, f"batch_{batch_num:04d}.csv")
    if not os.path.exists(batch_file):
        return None, f"Batch file not found"
    
    df = pd.read_csv(batch_file)
    csv_content = df.to_csv(index=False)
    
    total_rows = len(df)
    prompt = USER_PROMPT_TEMPLATE.format(
        csv_content=csv_content,
        batch_id=f"{batch_num:04d}",
        total_rows=total_rows
    )
    
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        "response_format": {"type": "json_object"},
        "max_tokens": 4096
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=90
        )
        
        if response.status_code != 200:
            return None, f"API Error {response.status_code}"
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return json.loads(content), None
        
    except Exception as e:
        return None, str(e)

def save_result(batch_num, result_data):
    if not result_data or "results" not in result_data:
        return False
    
    results = result_data["results"]
    output_file = os.path.join(RESULTS_DIR, f"result_batch_{batch_num:04d}.csv")
    
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("row_index,sqli_type,db_engine,confidence,reasoning\n")
        for r in results:
            row_idx = r.get("row", 0)
            sqli_type = r.get("sqli_type", "unknown")
            db_engine = r.get("db_engine", "unknown")
            confidence = r.get("confidence", 0.0)
            reasoning = r.get("reasoning", "").replace('"', '""')
            f.write(f"{row_idx},{sqli_type},{db_engine},{confidence},{reasoning}\n")
    
    return True

def main():
    print("=" * 60)
    print("SQLi CLASSIFIER - 1000 BATCHES")
    print("=" * 60)
    
    # Nhap API key
    api_key = input("\n[Nhap API key (sk-...)]: ").strip()
    if not api_key.startswith("sk-"):
        print("ERROR: Key phai bat dau 'sk-'")
        sys.exit(1)
    
    # Load progress
    progress = load_progress()
    start_from = progress["last_completed"] + 1
    
    print(f"\nBat dau tu batch: {start_from}")
    print(f"Muc tieu: 1000 batches")
    print(f"Tien trinh: {PROGRESS_FILE}")
    print("\nBat dau... (Ctrl+C de dung)")
    
    for batch_num in range(start_from, 1001):
        print(f"\n[{batch_num}/1000]", end=" ", flush=True)
        
        # Retry 3 lan
        for retry in range(3):
            result, error = classify_batch(batch_num, api_key)
            if result:
                break
            print(f"Retry {retry+1}...", end=" ", flush=True)
            time.sleep(3)
        
        if error:
            print(f"LOI: {error[:50]}")
            progress["failed_batches"].append(batch_num)
            save_progress(progress)
            break
        
        if save_result(batch_num, result):
            progress["completed_batches"].append(batch_num)
            progress["last_completed"] = batch_num
            save_progress(progress)
            print(f"OK", end="", flush=True)
        else:
            print(f"LOI save", end="", flush=True)
            progress["failed_batches"].append(batch_num)
            save_progress(progress)
            break
        
        time.sleep(0.5)
    
    print(f"\n\nDONE! Hoan thanh: {progress['last_completed']}/1000")
    print(f"Tien trinh luu tai: {PROGRESS_FILE}")

if __name__ == "__main__":
    main()