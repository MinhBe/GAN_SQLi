# Hệ Thống AI Classify — SQLi-GAN
> File này là hướng dẫn vận hành + prompt đầy đủ  
> Cập nhật tiến trình tại đây mỗi khi đổi tài khoản

---

## THÔNG TIN FILE INPUT

```
File: master_unlabeled.csv
Tổng rows: 41,460
Schema: payload_raw | payload_norm | payload_delex | 
        label | is_obfuscated | sqli_type_hint | source
Cần classify: sqli_type + db_engine + reasoning
```

---

## CẤU TRÚC THƯ MỤC

```
C:\Users\Admin\Documents\GAN\Asset\Data\
├── master_unlabeled.csv        ← INPUT (không sửa)
├── Gemini\                     ← Terminal 1 làm việc tại đây
│   ├── progress.json           ← Tiến trình Gemini
│   ├── batch_001.csv           ← Output từng batch
│   ├── batch_002.csv
│   └── ...
├── Opencode\                   ← Terminal 2 làm việc tại đây
│   ├── progress.json           ← Tiến trình Opencode
│   ├── batch_001.csv
│   ├── batch_002.csv
│   └── ...
└── master_sqli.csv             ← OUTPUT CUỐI (sau khi merge)
```

---

## PHÂN CHIA CÔNG VIỆC

```
Tổng: 41,460 rows
Trạng thái: Xử lý 100% dữ liệu (Không chia batch thủ công)
Mục tiêu: Hoàn thành toàn bộ dataset để đối chiếu chất lượng.
```

---

## TIẾN TRÌNH HIỆN TẠI

```
Tài khoản hiện tại: _______________
Rows đã xong: ___ / 41,460
Cập nhật lần cuối: _______________
```

---

## PROMPT GỬI CHO AI (COPY NGUYÊN)

### System Prompt (paste vào System hoặc đầu conversation)

```
You are a cybersecurity expert specializing in SQL injection analysis.
Your task: classify SQL injection payloads accurately.
Always respond with ONLY valid JSON. No text outside JSON.
No markdown code blocks. Raw JSON only.
```

### User Prompt Template

Thay `[PASTE_BATCH_HERE]` bằng 30 dòng CSV:

```
Classify each SQL injection payload below.

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
[PASTE_BATCH_HERE]

Respond with ONLY this JSON (no other text):
{
  "batch_id": "[BATCH_NUMBER]",
  "results": [
    {
      "row": 1,
      "sqli_type": "union_based",
      "db_engine": "mysql",
      "confidence": 0.95,
      "reasoning": "UNION SELECT used to append query and extract data"
    }
  ]
}
```

---

## QUY TRÌNH XỬ LÝ DỮ LIỆU

Hệ thống sẽ xử lý tuần tự toàn bộ 41,460 dòng từ `master_unlabeled.csv`. Dữ liệu được đưa vào AI theo từng đoạn (chunk) phù hợp với context window nhưng không chia thành các file batch vật lý riêng biệt như trước.

---

## CƠ CHẾ CHECKPOINT — ĐỌC KỸ

### File progress.json

Mỗi thư mục Gemini/ và Opencode/ có 1 file `progress.json`:

```json
{
  "worker": "Gemini",
  "account": "email@gmail.com",
  "total_batches": 691,
  "completed_batches": [1, 2, 3, 4, 5],
  "last_completed": 5,
  "last_updated": "2026-05-03T10:30:00",
  "rows_completed": 150,
  "rows_total": 20730,
  "status": "in_progress"
}
```

### Khi tài khoản đạt 90% quota

1. **DỪNG** — không gửi thêm prompt
2. **Ghi lại** batch cuối cùng đã xong vào `progress.json`
3. **Đăng nhập** tài khoản mới
4. **Tiếp tục** từ batch tiếp theo (last_completed + 1)
5. **Cập nhật** trường `account` trong `progress.json`

### Script save progress (chạy sau mỗi batch):

```python
import json
from datetime import datetime

def save_progress(worker, account, completed_batches, 
                  rows_completed, rows_total, output_dir):
    progress = {
        "worker": worker,
        "account": account,
        "completed_batches": completed_batches,
        "last_completed": max(completed_batches) if completed_batches else 0,
        "last_updated": datetime.now().isoformat(),
        "rows_completed": rows_completed,
        "rows_total": rows_total,
        "pct_done": round(rows_completed / rows_total * 100, 1),
        "status": "completed" if rows_completed >= rows_total else "in_progress"
    }
    with open(f"{output_dir}/progress.json", "w") as f:
        json.dump(progress, f, indent=2)
    print(f"[{worker}] Progress saved: {rows_completed}/{rows_total} "
          f"({progress['pct_done']}%)")
```

### Script lưu kết quả batch:

```python
import json
import csv
import os

def save_batch_result(batch_id, ai_response_json, output_dir):
    """
    ai_response_json: dict từ AI response
    """
    results = ai_response_json.get("results", [])
    fname = os.path.join(output_dir, f"result_batch_{batch_id:04d}.csv")
    
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
    print(f"Saved batch {batch_id:04d} → {fname}")
```

---

## SCRIPT MERGE CUỐI CÙNG

Chạy sau khi cả Gemini và Opencode hoàn thành:

```python
import pandas as pd
import os
import glob

BASE = r"C:\Users\Admin\Documents\GAN\Asset\Data"
INPUT = os.path.join(BASE, "master_unlabeled.csv")
GEMINI_DIR = os.path.join(BASE, "Gemini")
OPENCODE_DIR = os.path.join(BASE, "Opencode")
OUTPUT = os.path.join(BASE, "master_sqli.csv")

# Load input
df = pd.read_csv(INPUT)
df["sqli_type"] = "unknown"
df["db_engine"] = "unknown"
df["confidence"] = 0.0
df["reasoning"] = ""

# Load tất cả result files
for result_dir in [GEMINI_DIR, OPENCODE_DIR]:
    files = sorted(glob.glob(os.path.join(result_dir, "result_batch_*.csv")))
    print(f"Loading {len(files)} files from {result_dir}")
    for f in files:
        batch_df = pd.read_csv(f)
        for _, row in batch_df.iterrows():
            idx = int(row["row_index"])
            if idx < len(df):
                df.at[idx, "sqli_type"] = row["sqli_type"]
                df.at[idx, "db_engine"] = row["db_engine"]
                df.at[idx, "confidence"] = row["confidence"]
                df.at[idx, "reasoning"] = row["reasoning"]

# Validate
flags = []
for i, row in df.iterrows():
    if row["label"] == 1 and row["sqli_type"] == "benign":
        flags.append(f"Row {i}: label=1 but sqli_type=benign")
    if row["label"] == 0 and row["sqli_type"] not in ["benign", "unknown"]:
        flags.append(f"Row {i}: label=0 but sqli_type={row['sqli_type']}")

print(f"\nValidation: {len(flags)} conflicts found")
for f in flags[:10]:
    print(" ", f)

# Save
df.to_csv(OUTPUT, index=False)
print(f"\nSaved: {OUTPUT}")
print(f"Total rows: {len(df)}")
print("\nDistribution:")
print(df["sqli_type"].value_counts())
```

---

## CHECKLIST KHI ĐỔI TÀI KHOẢN

```
[ ] Ghi lại batch cuối cùng đã hoàn thành
[ ] Cập nhật progress.json (last_completed)
[ ] Kiểm tra result_batch_XXXX.csv đã lưu đủ
[ ] Đăng nhập tài khoản mới
[ ] Tiếp tục từ batch (last_completed + 1)
[ ] Cập nhật trường "account" trong progress.json
[ ] KHÔNG chạy lại batch đã có result file
```

---

## THEO DÕI TỔNG TIẾN TRÌNH

Cập nhật bảng này mỗi khi đổi tài khoản:

| Worker | Tài khoản | Batch xong | Rows xong | % |
|--------|-----------|-----------|-----------|---|
| Gemini | | | | |
| Opencode | | | | |
| **TỔNG** | | | **/ 41,460** | |

---

*Cập nhật lần cuối: 2026-05-03*   if row["label"] == 0 and row["sqli_type"] not in ["benign", "unknown"]:
        flags.append(f"Row {i}: label=0 but sqli_type={row['sqli_type']}")

print(f"\nValidation: {len(flags)} conflicts found")
for f in flags[:10]:
    print(" ", f)

# Save
df.to_csv(OUTPUT, index=False)
print(f"\nSaved: {OUTPUT}")
print(f"Total rows: {len(df)}")
print("\nDistribution:")
print(df["sqli_type"].value_counts())
```

---

## CHECKLIST KHI ĐỔI TÀI KHOẢN

```
[ ] Ghi lại batch cuối cùng đã hoàn thành
[ ] Cập nhật progress.json (last_completed)
[ ] Kiểm tra result_batch_XXXX.csv đã lưu đủ
[ ] Đăng nhập tài khoản mới
[ ] Tiếp tục từ batch (last_completed + 1)
[ ] Cập nhật trường "account" trong progress.json
[ ] KHÔNG chạy lại batch đã có result file
```

---

## THEO DÕI TỔNG TIẾN TRÌNH

Cập nhật bảng này mỗi khi đổi tài khoản:

| Worker | Tài khoản | Batch xong | Rows xong | % |
|--------|-----------|-----------|-----------|---|
| Gemini | | | | |
| Opencode | | | | |
| **TỔNG** | | | **/ 41,460** | |

---

*Cập nhật lần cuối: 2026-05-03*