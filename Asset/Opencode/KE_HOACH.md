# KẾ HOẠCH SQLi CLASSIFICATION 100%

## TỔNG QUAN

- **MỤC TIÊU**: Classify 41,459 rows → ground truth cho GAN training
- **AI**: Opencode Agent (chạy trực tiếp trong conversation)
- **RESULT**: master_sqli.csv + Conflict Report + Distribution Stats
- **LƯU TRỮ**: C:\Users\Admin\Documents\GAN\Asset\Opencode

---

## KIẾN TRÚC THƯ MỤC

```
C:\Users\Admin\Documents\GAN\Asset\
├── Guiding/
│   └── master_unlabeled.csv     [INPUT - 41,459 rows]
├── Data/
│   ├── batches/                 [1,382 batch files]
│   └── results/                [1,382 result files]
├── Opencode/
│   ├── KE_HOACH.md              [KẾ HOẠCH NÀY]
│   └── progress.json            [TIẾN TRÌNH]
└── master_sqli.csv              [OUTPUT - SAU KHI XONG]
```

---

## PHƯƠNG PHÁP

### Classify trực tiếp trong conversation:
1. Mỗi batch = 30 rows
2. User paste 30 payloads
3. Tôi reply JSON classification
4. Tự động lưu progress + result

### Prompts:

**System Prompt:**
```
You are a cybersecurity expert specializing in SQL injection analysis.
Your task: classify SQL injection payloads accurately.
Always respond with ONLY valid JSON.
```

**User Prompt Template:**
```
Classify each SQL injection payload below.

For each payload determine:
1. sqli_type: union_based | error_based | boolean_blind | time_blind |
   heavy_query | stacked_queries | out_of_band | auth_bypass |
   second_order | rce | polyglot | lateral | benign | unknown

2. db_engine: mysql | mssql | oracle | postgresql | sqlite | generic | unknown

3. confidence: 0.0-1.0

4. reasoning: ONE short sentence

Rules:
- label=1 → sqli_type KHÔNG phải "benign"
- label=0 → sqli_type = "benign"

Input (30 rows):
[PASTE_30_ROWS]

Respond with ONLY JSON:
{"batch_id": "0001", "results": [...]
```

---

## TIẾN TRÌNH THỰC TẾ

### Phase 1: Chuẩn bị (ĐÃ XONG)
- [x] Đọc master_unlabeled.csv (41,459 rows)
- [x] Label distribution: 22,630 (label=1), 18,829 (label=0)
- [x] Tạo thư mục batches/results
- [x] Tạo 1,382 batch files

### Phase 2: Classify (ĐANG CHẠY)
- [ ] Batch 001-1000 (30,000 rows) - User theo dõi quota
- [ ] Batch 1001-1382 (11,459 rows) - Còn lại

### Phase 3: Merge & Report (PENDING)
- [ ] Merge → master_sqli.csv
- [ ] Conflict Report
- [ ] Distribution Stats

---

## PROGRESS TRACKING

File: `C:\Users\Admin\Documents\GAN\Asset\Opencode\progress.json`

```json
{
  "worker": "Opencode",
  "total_batches": 1382,
  "completed_batches": [],
  "failed_batches": [],
  "last_completed": 0,
  "status": "in_progress",
  "last_updated": "2026-05-03 HH:MM:SS"
}
```

---

## ƯỚC TÍNH THỜI GIAN

- Batch 001-1000: ~50-100 phút (tùy quota)
- Batch 1001-1382: ~20-40 phút
- **Tổng**: ~1-2 giờ

---

## KẾT QUẢ CUỐI

### master_sqli.csv Schema:
```csv
payload_raw,payload_norm,payload_delex,label,is_obfuscated,sqli_type_hint,source,
sqli_type,db_engine,confidence,reasoning
```

### Conflict Report:
- **False Negative**: label=1 + sqli_type=benign
- **False Positive**: label=0 + sqli_type≠benign

### Distribution Stats:
- sqli_type % (union, blind, error...)
- db_engine % (mysql, postgresql, mssql...)
- Confidence mean/std

---

## TIẾP TỤC

**Bắt đầu classify Batch 001?**

[OK] - Bắt đầu ngay
[WAIT] - Chờ user xác nhận