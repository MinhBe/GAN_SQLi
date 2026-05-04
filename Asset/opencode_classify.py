import pandas as pd
import json
import os
import time

OPENAI_API_KEYS = [
    "sk-uvW6c8AdpzYR3zXqWFeLv3qddvvJvbziPCaop8KsE7kdrLqBm7YEJQce3F14Olde",
    "sk-jDMXAXlhvToZOZMJeDkn8M1q235AXWqdHE8ak1U2fkNzPCRZZIkeCvsklbcWC6Aj",
    "sk-9EOoJ6DfA9tYYl7JcPSywMhIIF5CuXtAq7DI8DO5weDVSPSZOqGGFzjDzV9MGsrV",
    "sk-Pb9jA4sca4kvlXsN1dD34vaB45lLtqj2FT9URMa6Bctfb0FyuaxFC89ZwVhRFa8f",
    "sk-967k9TpCLAg8aXWZBexFTbhGV9qMhtfv2Qzr1KaAaul5WTmQK2ht1iXLuYy8LV9B",
    "sk-v4y1lDpnN2ze2Fs63qhWZVC6JwJo1tZXRIUqiA1bSXMC4mdRngt5y5LB39cEd8QS",
    "sk-dAkHNFgEq2awYDndezU2QXc0LoZIwfrCi5B2eYBzvzUznJJCodgbrBjzH70GA3Ov"
]

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
      "reasoning": "UNION SELECT used to append query and extract data"
    }}
  ]
}}"""

BATCH_DIR = r"C:\Users\Admin\Documents\GAN\Asset\Data\batches"
RESULTS_DIR = r"C:\Users\Admin\Documents\GAN\Asset\Data\results"
BATCH_SIZE = 30

def classify_batch(batch_num, api_key):
    """Classify a single batch using OpenAI API"""
    import requests
    
    batch_file = os.path.join(BATCH_DIR, f"batch_{batch_num:04d}.csv")
    if not os.path.exists(batch_file):
        return None, f"Batch file not found: {batch_file}"
    
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
        "response_format": {"type": "json_object"}
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=payload,
            timeout=60
        )
        
        if response.status_code != 200:
            return None, f"API Error: {response.status_code} - {response.text}"
        
        result = response.json()
        content = result["choices"][0]["message"]["content"]
        return json.loads(content), None
        
    except Exception as e:
        return None, str(e)

def save_result(batch_num, result_data):
    """Save result to CSV"""
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

# Test với batch 001
print("=" * 50)
print("TESTING: Batch 001")
print("=" * 50)

result, error = classify_batch(1, OPENAI_API_KEYS[0])

if error:
    print(f"ERROR: {error}")
else:
    print(f"SUCCESS! Batch 001 result:")
    print(json.dumps(result, indent=2)[:500])
    
    # Save result
    save_result(1, result)
    print(f"\nResult saved to: result_batch_0001.csv")