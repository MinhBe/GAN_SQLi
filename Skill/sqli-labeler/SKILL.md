---
name: sqli-labeler
description: |
  Label SQL injection payloads với sqli_type, db_engine, confidence, reasoning
  theo taxonomy chuẩn 14 categories của dự án GAN_SQLi.
  Trigger khi: đánh nhãn payload mới, re-label rows có nhãn sai/kém chất lượng,
  xử lý batch combined_labeled_data.csv, classify payload theo priority chain,
  hoặc cần gán confidence + reasoning có dẫn chứng cụ thể.
  Do NOT trigger for: validate/normalize labels đã có (→ sqli-label-validator),
  review chất lượng nhãn sau khi label (→ sqli-label-critic).
---

# sqli-labeler — Skill Guide

## Role

Phân tích từng `payload_norm` và gán **4 fields**: `sqli_type`, `db_engine`, `confidence`,
`reasoning` theo taxonomy chuẩn của dự án. Chỉ sử dụng `payload_norm` để phân tích — các
cột khác được pass-through.

**File gốc `combined_labeled_data.csv` KHÔNG BAO GIỜ bị ghi đè.**

---

## Input / Output

### Input

```csv
payload_norm
""" or pg_sleep ( __TIME__ ) --"
"admin' OR '1'='1"
"' UNION SELECT 1, @@VERSION --"
```

Hoặc full CSV schema:
```csv
payload_norm,label,source,sqli_type_hint,is_obfuscated,payload_raw,payload_delex
```

**Path mặc định:** `C:\Projects\GAN_SQLi\Asset\LabelData\combined_labeled_data.csv`

### Output

```csv
payload_norm,sqli_type,db_engine,confidence,reasoning
""" or pg_sleep ( __TIME__ ) --","time_blind","postgresql","0.95","pg_sleep() is PostgreSQL-specific time-delay function — time-based blind inference"
```

| Column | Kiểu | Yêu cầu |
|--------|------|---------|
| `sqli_type` | string | 1 trong 14 categories |
| `db_engine` | string | 1 trong 9 DB engines |
| `confidence` | float 0.0–1.0 | Theo thang 4 mức bên dưới |
| `reasoning` | string ≥ 30 chars | Nêu signal cụ thể, KHÔNG dùng generic phrases |

---

## Workflow (5 bước)

### Bước 1 — Đọc input và xác định mode

```
Đọc file CSV → validate schema → xác định mode:
  Mode A: sqli_type trống  → Đánh nhãn mới
  Mode B: sqli_type đã có  → Re-label (xem xét lại)
```

### Bước 2 — Phân tích payload theo priority chain

```
Với mỗi payload_norm:
  1. Lowercase, strip whitespace
  2. Kiểm tra rce signals (priority 1)           → xp_cmdshell, certutil, powershell
  3. Kiểm tra out_of_band signals (priority 2)   → LOAD_FILE, UTL_HTTP, xp_dirtree
  4. Kiểm tra stacked_queries (priority 3)       → ; + new SQL statement
  5. Kiểm tra error_based (priority 4)           → EXTRACTVALUE, UPDATEXML
  6. Kiểm tra time_blind (priority 5)            → SLEEP, pg_sleep, WAITFOR DELAY
  7. Kiểm tra heavy_query (priority 6)           → COUNT(*) cross-join ≥ 3 tables
  8. Kiểm tra union_based (priority 7)           → UNION SELECT
  9. Kiểm tra boolean_blind (priority 8)         → AND/OR 1=1, 'a'='a'
  10. Kiểm tra auth_bypass (priority 9)          → admin' OR, admin'--
  11. Kiểm tra second_order (priority 10)        → INSERT INTO với attack intent
  12. Kiểm tra polyglot (priority 11)            → works on ≥ 2 DB engines
  13. Kiểm tra lateral (priority 12)             → JOIN ... OR 1=1
  14. benign hoặc unknown
```

**Quy tắc priority:** payload match nhiều categories → chọn priority số **thấp nhất**.

Xem `references/taxonomy.md` cho detection signals đầy đủ từng type.

### Bước 3 — Xác định DB engine

Song song với Bước 2:
- Tìm DB-specific keywords → gán đúng engine
- Không có DB signature → `generic`
- Payload quá ngắn/mơ hồ → `unknown`

Xem `references/taxonomy.md` §DB Engine cho signatures từng engine.

### Bước 4 — Gán confidence

| Mức | Giá trị | Điều kiện |
|-----|---------|-----------|
| High | 0.95 | Có ≥ 1 primary signal rõ ràng, không ambiguous |
| Medium-high | 0.80 | Có signal nhưng payload ngắn hoặc obfuscated nhẹ |
| Medium | 0.70 | Signal yếu, có thể false positive |
| Low | 0.50 | Ambiguous, không chắc giữa 2 categories |

### Bước 5 — Viết reasoning

**Yêu cầu**: ≥ 30 characters, nêu signal cụ thể, giải thích lý do chọn category này.

**Tốt:**
```
"pg_sleep() is PostgreSQL-specific time-delay function — time-based blind inference"
"UNION SELECT with @@VERSION confirms MySQL union-based data extraction"
"utl_inaddr.get_host_address with subquery is Oracle error-based exfiltration"
```

**Không chấp nhận:**
```
"sql_injection"    "boolean"    "boolean_blind"    "not_sql_injection"
```

---

## Batch Mode

```
Input:  combined_labeled_data.csv
        --target-mode: all | low-confidence | out-of-taxonomy | unlabeled
        --batch-size: 30 (default)
```

| Mode | Mô tả | Rows dự kiến |
|------|-------|-------------|
| `all` | Re-label toàn bộ | 40,860 |
| `low-confidence` | confidence < 0.7 | ~2,373 |
| `out-of-taxonomy` | type ngoài taxonomy chuẩn | ~1,862 |
| `unlabeled` | chưa có sqli_type | ~5,447 (từ master) |

**Output files** (cùng thư mục với input):

| File | Mô tả |
|------|-------|
| `combined_labeled_data_relabeled.csv` | Dataset hoàn chỉnh sau re-label |
| `relabeling_diff.csv` | Chỉ rows bị thay đổi — dùng cho audit |
| `relabeling_summary.md` | Distribution trước/sau, tỷ lệ thay đổi |

---

## Pipeline với các Skill khác

```
combined_labeled_data.csv
  → sqli-labeler       → combined_labeled_data_relabeled.csv
  → sqli-label-critic  → label_review_report.csv + summary.md
  → human review       → master_labeled_data.csv (final)
```

---

## Reference Files

| File | Khi nào đọc |
|------|-------------|
| `references/taxonomy.md` | Lookup signals cụ thể từng sqli_type và db_engine |
| `references/labeling-guidelines.md` | Edge cases, ambiguous payloads, reasoning examples |
