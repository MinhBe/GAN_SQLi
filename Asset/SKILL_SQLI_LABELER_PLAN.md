# Kế Hoạch Skill: `sqli-labeler`

> **Mục đích:** Skill chuyên đánh nhãn SQL Injection payloads — phân tích từng payload và gán `sqli_type`, `db_engine`, `confidence`, `reasoning` theo taxonomy chuẩn 14 categories của dự án GAN_SQLi.  
> **Trạng thái:** Bản kế hoạch — chưa build  
> **Ngày:** 2026-05-09

---

## 1. Bối Cảnh

### Tại sao cần skill này?

Dataset hiện tại (`combined_labeled_data.csv`, ~40,860 rows) đã được AI labeling bởi Gemini/Opencode. Tuy nhiên:

- **1,862 rows** có nhãn nằm ngoài taxonomy (boolean_based, generic, comment_based, inline_query, ldap_injection, command_injection, stacked_query)
- **2,373 rows** có confidence < 0.7 (AI không chắc chắn)
- **5,447 rows** (index 41,459–46,905 trong master_unlabeled.csv) chưa được đánh nhãn bao giờ

Skill labeler cần làm được 2 việc:
1. **Đánh nhãn mới** cho các rows chưa có nhãn
2. **Re-label** cho các rows có nhãn sai/kém chất lượng

---

## 2. Input / Output

### Input

```csv
payload_norm
""" or pg_sleep ( __TIME__ ) --"
"admin' OR '1'='1"
"' UNION SELECT 1, @@VERSION --"
```

Hoặc full CSV schema của dự án:
```csv
payload_norm,label,source,sqli_type_hint,is_obfuscated,payload_raw,payload_delex
```

Skill chỉ sử dụng cột `payload_norm` để phân tích. Các cột khác được pass-through.

**Path mặc định:** `C:\Projects\GAN_SQLi\Asset\LabelData\combined_labeled_data.csv`

### Output

```csv
payload_norm,sqli_type,db_engine,confidence,reasoning
""" or pg_sleep ( __TIME__ ) --","time_blind","postgresql","0.95","pg_sleep() is exclusive to PostgreSQL for time-based blind inference"
```

| Column | Kiểu | Mô tả |
|--------|------|-------|
| `sqli_type` | string | 1 trong 14 categories |
| `db_engine` | string | 1 trong 9 DB engines |
| `confidence` | float 0.0–1.0 | Độ chắc chắn của label |
| `reasoning` | string ≥ 30 chars | Dẫn chứng cụ thể — KHÔNG dùng generic phrases |

---

## 3. Taxonomy Chuẩn

### 3.1 SQLi Type (14 categories) — theo thứ tự ưu tiên

| Priority | Type | Primary Signal |
|----------|------|----------------|
| 1 | `rce` | `xp_cmdshell`, `certutil`, `powershell`, `/bin/bash` |
| 2 | `out_of_band` | `LOAD_FILE`, `UTL_HTTP`, `UTL_INADDR`, `xp_dirtree`, `OPENROWSET` |
| 3 | `stacked_queries` | `;` + new SQL statement (CREATE/DROP/INSERT) |
| 4 | `error_based` | `EXTRACTVALUE`, `UPDATEXML`, `utl_inaddr.get_host_address`, `ctxsys.drithsx` |
| 5 | `time_blind` | `SLEEP()`, `pg_sleep()`, `WAITFOR DELAY`, `BENCHMARK()`, `randomblob()` |
| 6 | `heavy_query` | `COUNT(*) FROM A, B, C, D` — cross-join ≥ 3 tables |
| 7 | `union_based` | `UNION SELECT`, `UNION ALL SELECT` |
| 8 | `boolean_blind` | `AND 1=1`, `OR 1=1`, `AND 'a'='a'`, `OR '1'='1'` |
| 9 | `auth_bypass` | `admin' OR`, `' OR '1'='1`, `admin'--`, `admin'#` |
| 10 | `second_order` | `INSERT INTO ... VALUES` với attack intent |
| 11 | `polyglot` | Hoạt động trên ≥ 2 DB engines đồng thời |
| 12 | `lateral` | `JOIN ... ON ... OR 1=1`, `LATERAL JOIN` |
| 13 | `benign` | Legitimate SQL, plain text |
| 14 | `unknown` | Không đủ thông tin để classify |

**Quy tắc priority:** Khi payload match nhiều categories → chọn category có priority số **thấp nhất**.

### 3.2 DB Engine (9 categories)

| DB | Primary Signatures |
|----|-------------------|
| `mysql` | `@@VERSION`, `SLEEP()`, `LOAD_FILE()`, `information_schema`, `/*!...*/` |
| `mssql` | `WAITFOR DELAY`, `sysobjects`, `xp_cmdshell`, `@@servername` |
| `oracle` | `utl_inaddr`, `ctxsys.drithsx`, `dual`, `all_tables`, `ROWNUM`, `v$version` |
| `postgresql` | `pg_sleep()`, `version()`, `::` cast, `pg_catalog` |
| `sqlite` | `sqlite_version()`, `sqlite_master`, `randomblob()` |
| `firebird` | `rdb$functions`, `rdb$relations` |
| `db2` | `sysibm.systables` |
| `generic` | Không có DB-specific signature |
| `unknown` | Payload quá ngắn / mơ hồ |

---

## 4. Workflow

### Step 1: Đọc input

```
Đọc file CSV → validate schema → xác định mode:
  - Mode A: Đánh nhãn mới (payload_norm có, sqli_type trống)
  - Mode B: Re-label (sqli_type đã có nhưng cần xem xét lại)
```

### Step 2: Phân tích từng payload theo priority chain

```
Với mỗi payload_norm:
  1. Lowercase, strip whitespace
  2. Kiểm tra rce signals           → if found: sqli_type = rce, priority 1
  3. Kiểm tra out_of_band signals   → if found: sqli_type = out_of_band, priority 2
  4. Kiểm tra stacked_queries       → if found: sqli_type = stacked_queries, priority 3
  [... tiếp tục theo priority table]
  14. Nếu không match gì → sqli_type = unknown
```

### Step 3: Xác định DB engine

```
Song song với Step 2:
  1. Tìm DB-specific keywords (pg_sleep → postgresql, WAITFOR → mssql, ...)
  2. Nếu không có DB signature → generic
  3. Nếu payload quá ngắn → unknown
```

### Step 4: Gán confidence

```
confidence = 0.95  → Có ≥ 1 primary signal rõ ràng, không ambiguous
confidence = 0.80  → Có signal nhưng payload ngắn hoặc bị obfuscated nhẹ
confidence = 0.70  → Signal yếu, có thể là false positive
confidence = 0.50  → Ambiguous, không chắc giữa 2 categories
```

### Step 5: Viết reasoning

**Yêu cầu bắt buộc:**
- Độ dài ≥ 30 characters
- Nêu signal cụ thể (function name, keyword, pattern)
- Nêu lý do chọn category này thay vì category khác (nếu ambiguous)

**Ví dụ tốt:**
```
"pg_sleep() is PostgreSQL-specific time-delay function — time-based blind inference"
"utl_inaddr.get_host_address with subquery is Oracle error-based exfiltration"
"UNION SELECT with @@VERSION confirms MySQL union-based data extraction"
```

**Ví dụ kém (không chấp nhận):**
```
"sql_injection"                 ← generic, không nói gì
"boolean"                       ← 1 từ
"not_sql_injection"             ← không giải thích
"boolean_blind"                 ← chỉ lặp lại type
```

---

## 5. Batch Mode (cho re-labeling combined_labeled_data.csv)

Vì dataset có ~40k rows, skill cần hỗ trợ batch processing:

```
Input:  combined_labeled_data.csv (40,860 rows)
        --target-mode: all | low-confidence | out-of-taxonomy | unlabeled
        --batch-size: 30 (default)

Output:
  combined_labeled_data_relabeled.csv   ← dataset đã re-label
  relabeling_diff.csv                   ← chỉ các rows bị thay đổi
  relabeling_summary.md                 ← thống kê trước/sau
```

**Target modes:**
| Mode | Mô tả | Số rows dự kiến |
|------|-------|----------------|
| `all` | Re-label toàn bộ | 40,860 |
| `low-confidence` | Chỉ rows confidence < 0.7 | ~2,373 |
| `out-of-taxonomy` | Chỉ rows type ngoài taxonomy | ~1,862 |
| `unlabeled` | Rows chưa có sqli_type | ~5,447 (từ master) |

---

## 6. Output Files

| File | Mô tả |
|------|-------|
| `combined_labeled_data_relabeled.csv` | Dataset hoàn chỉnh sau re-label |
| `relabeling_diff.csv` | Chỉ rows bị thay đổi — dùng cho audit |
| `relabeling_summary.md` | Distribution trước/sau, tỷ lệ thay đổi |

**File gốc `combined_labeled_data.csv` KHÔNG BAO GIỜ bị ghi đè.**

---

## 7. Cấu Trúc Thư Mục Skill

```
Skill/sqli-labeler/
├── SKILL.md                          ← Entry point, workflow chính
└── references/
    ├── taxonomy.md                   ← 14 SQLi types + detection signals + examples
    └── labeling-guidelines.md        ← Hướng dẫn edge cases, ambiguous payloads
```

---

## 8. Edge Cases Quan Trọng

| Tình huống | Cách xử lý |
|------------|------------|
| Payload chỉ là 1 từ (e.g., `insert`, `distinct`) | `benign`, db=`unknown`, confidence=0.70 |
| `OR 1=1` không có context | `boolean_blind`, db=`generic`, confidence=0.85 |
| `admin' OR '1'='1` | `auth_bypass` (không phải `boolean_blind`) — có `admin` prefix |
| `UNION SELECT` + `SLEEP()` | `time_blind` (priority 5 < priority 7) |
| `@@VERSION` không có context | db=`generic` (tồn tại ở cả MySQL và MSSQL) |
| Payload bị heavy obfuscation | Cố gắng decode, nếu không được → confidence 0.60-0.70 |
| `SELECT COUNT(*) FROM A, B` (2 tables) | `boolean_blind` hoặc `union_based` — KHÔNG phải `heavy_query` |

---

## 9. Liên Kết Với Skill sqli-label-critic

Sau khi skill `sqli-labeler` chạy xong và tạo ra `combined_labeled_data_relabeled.csv`, skill `sqli-label-critic` sẽ:

1. Đọc output của labeler
2. Review từng nhãn bằng cách tra cứu detection signals
3. Output PASS / FLAG / REJECT cho từng row kèm evidence

**Pipeline đề xuất:**
```
combined_labeled_data.csv
  → sqli-labeler → combined_labeled_data_relabeled.csv
  → sqli-label-critic → label_review_report.csv + summary.md
  → human review → master_labeled_data.csv (final)
```
