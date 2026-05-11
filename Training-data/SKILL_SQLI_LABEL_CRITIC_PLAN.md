# Kế Hoạch Skill: `sqli-label-critic`

> **Mục đích:** Skill đóng vai "hà khắc kỹ tính" — review từng nhãn đã đánh trong dataset, tra cứu detection signals cụ thể, và ra verdict **PASS / FLAG / REJECT** kèm dẫn chứng rõ ràng. Không thể bị thuyết phục bằng reasoning mơ hồ.  
> **Trạng thái:** Bản kế hoạch — chưa build  
> **Ngày:** 2026-05-09

---

## 1. Bối Cảnh

### Tại sao cần skill này?

Skill `sqli-labeler` có thể labeling tốt nhưng không hoàn hảo. Cần một lớp review độc lập với tiêu chí nghiêm khắc:

- **AI labeling có rate lỗi cao**: 1,862 rows out-of-taxonomy, 2,373 rows confidence thấp
- **Reasoning kém chất lượng**: 68.5% rows (27,997) có reasoning < 30 chars hoặc generic
- **False negatives nguy hiểm**: `benign` + SQL keywords mạnh (19,669 rows cần verify)
- **Conflict duplicates**: Cùng payload, khác label — AI không nhất quán

Critic đóng vai một chuyên gia bảo mật độc lập — **không tin label có sẵn**, chỉ tin dẫn chứng từ payload.

---

## 2. Triết Lý Của Critic

> **"Không có dẫn chứng = không PASS."**

Critic tuân theo 5 nguyên tắc cứng:

1. **Nguyên tắc Evidence-First**: Mọi verdict đều phải dẫn ra ít nhất 1 token/keyword cụ thể từ payload để chứng minh.

2. **Nguyên tắc Priority**: Nếu payload có signal ở priority thấp hơn (nguy hiểm hơn), label priority cao (ít nguy hiểm) bị **REJECT** ngay.

3. **Nguyên tắc Consistency**: Cùng payload phải có cùng label. Conflict duplicates bị **FLAG** tự động.

4. **Nguyên tắc Reasoning Quality**: Reasoning < 30 chars hoặc generic phrase → **FLAG** bất kể type có đúng không.

5. **Nguyên tắc Benign Scrutiny**: Label `benign` bị xét kỹ nhất. Một keyword tấn công đủ để **REJECT**.

---

## 3. Input / Output

### Input

```csv
payload_norm,sqli_type,db_engine,confidence,reasoning
""" or pg_sleep ( __TIME__ ) --","time_blind","postgresql","0.95","pg_sleep is PostgreSQL time-based blind SQLi"
"admin' or 1 = 1#","auth_bypass","generic","0.95","admin' or 1=1# is classic auth bypass"
"distinct","benign","unknown","0.70","Plain keyword 'distinct' is not an attack"
```

**Path mặc định:** Output từ `sqli-labeler`, hoặc `combined_labeled_data.csv` trực tiếp.

### Output: Per-Row Verdict

```csv
row_index,payload_norm,sqli_type,db_engine,confidence,reasoning,verdict,critic_evidence,critic_note
0,""" or pg_sleep ( __TIME__ ) --","time_blind","postgresql","0.95","...","PASS","Signal found: pg_sleep() — PostgreSQL-specific time delay","Correct: priority 5, DB confirmed"
1,"select *","boolean_blind","mysql","0.80","boolean","FLAG","No boolean signal found in payload","Reasoning too generic; payload looks benign"
2,"admin' or 1=1#","boolean_blind","generic","0.90","or 1=1 is boolean","REJECT","Priority conflict: auth_bypass (P9) < boolean_blind (P8) for payload with admin prefix","Should be auth_bypass"
```

### Output: Summary Report

```markdown
# Label Review Report
Generated: 2026-05-09

## Verdict Distribution
| Verdict | Count | % |
|---------|-------|---|
| PASS    | 32,100 | 78.6% |
| FLAG    | 6,240  | 15.3% |
| REJECT  | 2,520  | 6.1%  |

## Top Rejection Reasons
1. Priority conflict (1,100 rows)
2. Signal not found in payload (820 rows)
3. Benign with attack signal (600 rows)
...
```

---

## 4. Verdict Definitions

### PASS — Nhãn đúng, dẫn chứng đủ

**Tiêu chí:**
- `sqli_type` match ít nhất 1 primary signal trong payload
- `db_engine` match signature trong payload (hoặc `generic`/`unknown` nếu không có signature)
- `confidence` phù hợp với số lượng và chất lượng signals
- `reasoning` ≥ 30 chars, nêu signal cụ thể, không generic

**Ví dụ PASS:**
```
payload:   "AND 1 = utl_inaddr.get_host_address((SELECT name FROM users))"
sqli_type: error_based ✓   (utl_inaddr = Oracle error-based signal)
db_engine: oracle ✓        (utl_inaddr là Oracle-specific)
confidence: 0.95 ✓         (primary signal rõ ràng)
reasoning: "utl_inaddr.get_host_address with subquery is Oracle error-based exfiltration" ✓
verdict:   PASS
evidence:  "Signal: utl_inaddr.get_host_address — Oracle error-based primary signal"
```

---

### FLAG — Có vấn đề nhưng không chắc chắn sai

**Khi nào FLAG:**

| Tình huống | Lý do |
|------------|-------|
| Reasoning < 30 chars hoặc generic | Không thể verify label thiếu dẫn chứng |
| Confidence không khớp signal strength | 0.95 nhưng payload ngắn, 0.50 nhưng signal rõ ràng |
| DB engine `generic` nhưng có signature | Có thể đặt DB cụ thể |
| Label có thể đúng nhưng reasoning sai | Type đúng, nhưng cần reasoning tốt hơn |
| `benign` với SQL syntax hợp lệ | Cần verify thêm context |

**Ví dụ FLAG:**
```
payload:   "or 1 = 1 --"
sqli_type: boolean_blind  (có thể đúng)
reasoning: "boolean"      ← FLAG: chỉ 7 chars, không nêu signal cụ thể
verdict:   FLAG
note:      "Reasoning too short. Expected: nêu cụ thể 'OR 1=1 -- pattern with comparison'"
```

---

### REJECT — Nhãn sai rõ ràng, cần re-label

**Khi nào REJECT:**

| Tình huống | Lý do |
|------------|-------|
| Priority conflict | Payload có signal P3 nhưng label là P7 |
| Signal không tồn tại trong payload | Label `time_blind` nhưng không có SLEEP/pg_sleep/WAITFOR |
| `benign` có attack keyword | UNION/SLEEP/xp_cmdshell trong payload benign |
| Wrong DB engine với clear signature | `pg_sleep()` trong payload nhưng db_engine=`mysql` |
| `unknown` với clear signal | Signal rõ ràng nhưng label `unknown` |

**Ví dụ REJECT:**
```
payload:   "' UNION SELECT 1, SLEEP(5) --"
sqli_type: union_based     ← REJECT: SLEEP() = time_blind (priority 5) < union_based (priority 7)
db_engine: oracle          ← REJECT: SLEEP() là MySQL, không phải Oracle
confidence: 0.95
verdict:   REJECT
evidence:  "Priority conflict: SLEEP() at P5 overrides UNION SELECT at P7. DB: SLEEP() is MySQL-specific, not Oracle"
correction: sqli_type=time_blind, db_engine=mysql
```

---

## 5. Kiểm Tra Cụ Thể Theo Từng Category

### 5.1 Kiểm tra `benign` — Nghiêm khắc nhất

```
Benign REJECT nếu payload chứa BẤT KỲ:
  UNION, SLEEP, pg_sleep, WAITFOR, BENCHMARK
  EXTRACTVALUE, UPDATEXML, xp_cmdshell, LOAD_FILE
  utl_inaddr, ctxsys, UTL_HTTP
  AND 1=1, OR 1=1, ' OR ', " OR "
  OR '1'='1', admin'
```

### 5.2 Kiểm tra `boolean_blind` vs `auth_bypass`

```
auth_bypass PHẢI có ít nhất 1 trong:
  - "admin" trước OR pattern
  - login bypass pattern: ' OR '1'='1', admin'--

Nếu chỉ có "OR 1=1" không có "admin" → boolean_blind
Nếu có "admin" + OR pattern → auth_bypass
Nếu label là boolean_blind nhưng có "admin" prefix → FLAG
```

### 5.3 Kiểm tra `time_blind` vs `heavy_query`

```
time_blind CẦN: SLEEP(), pg_sleep(), WAITFOR DELAY, BENCHMARK(), randomblob()
heavy_query CẦN: COUNT(*) với cross-join ≥ 3 tables

Nếu không có các functions trên → không được label time_blind
Nếu chỉ có 2-table join → không phải heavy_query
```

### 5.4 Kiểm tra DB engine conflicts

```
Conflict tự động REJECT nếu:
  pg_sleep()   → db_engine != postgresql
  WAITFOR DELAY → db_engine != mssql
  utl_inaddr   → db_engine != oracle
  randomblob() → db_engine != sqlite
  SLEEP()      → db_engine không phải mysql hoặc generic
  sysibm.systables → db_engine != db2
  rdb$         → db_engine != firebird
```

---

## 6. Workflow

### Phase 1: Quick Scan (toàn bộ dataset)

```
Đọc CSV → chạy 5 checks nhanh:
  C1: sqli_type trong taxonomy?          (nếu không → REJECT)
  C2: db_engine trong taxonomy?          (nếu không → FLAG)
  C3: Primary signal có trong payload?   (nếu không → REJECT)
  C4: Priority conflict?                 (nếu có → REJECT)
  C5: Reasoning ≥ 30 chars, non-generic? (nếu không → FLAG)
```

### Phase 2: Deep Review (chỉ FLAG rows)

```
Với mỗi FLAG row:
  - Tìm ALL signals trong payload
  - So sánh với taxonomy priority table
  - Verify DB engine từ signatures
  - Đề xuất correction nếu có
```

### Phase 3: Benign Audit (sample)

```
Random sample 500 rows từ benign label:
  - Kiểm tra từng row theo danh sách attack keywords
  - Tính false negative rate
  - Nếu FN rate > 5% → recommend full benign re-review
```

### Phase 4: Conflict Resolution

```
Tìm duplicate payloads (cùng payload_norm):
  - Exact duplicate: cùng type → flag redundant, giữ 1
  - Conflict duplicate: khác type → REJECT cả 2, cần re-label
```

---

## 7. Evidence Format Chuẩn

Mọi verdict phải kèm `critic_evidence` theo format:

```
Format: "[Verdict reason] — Signal: [exact token] — [explanation]"
```

**Ví dụ:**
```
PASS:   "Signal confirmed: pg_sleep() at char 5 — PostgreSQL time-delay function"
FLAG:   "Reasoning insufficient: 7 chars, no signal cited — expected mention of [exact signal]"
REJECT: "Priority conflict: xp_cmdshell (P1=rce) found but labeled union_based (P7)"
REJECT: "Signal absent: no SLEEP/WAITFOR/pg_sleep in payload, cannot be time_blind"
REJECT: "DB mismatch: pg_sleep() is PostgreSQL-specific, db_engine=mysql is wrong"
```

---

## 8. Output Files

| File | Mô tả |
|------|-------|
| `label_review_results.csv` | Toàn bộ rows + verdict + critic_evidence + correction |
| `label_review_rejected.csv` | Chỉ REJECT rows — input cho re-labeling |
| `label_review_flagged.csv` | Chỉ FLAG rows — cần human review |
| `label_review_summary.md` | Thống kê tổng quan + top issues + recommendations |

**File gốc không bị thay đổi.**

---

## 9. Cấu Trúc Thư Mục Skill

```
Skill/sqli-label-critic/
├── SKILL.md                          ← Entry point + verdict logic
└── references/
    ├── taxonomy.md                   ← 14 types + signals (dùng chung với labeler)
    ├── evidence-patterns.md          ← Signal checklist cho từng type (mới)
    └── verdict-examples.md           ← 50+ ví dụ PASS/FLAG/REJECT có dẫn chứng (mới)
```

### evidence-patterns.md sẽ chứa gì?

```
# Evidence Pattern Checklist

## time_blind — Required Signals (ít nhất 1)
  ✓ SLEEP(       ← MySQL
  ✓ pg_sleep(    ← PostgreSQL
  ✓ WAITFOR DELAY ← MSSQL
  ✓ BENCHMARK(   ← MySQL
  ✓ randomblob(  ← SQLite

## union_based — Required Signals
  ✓ UNION SELECT
  ✓ UNION ALL SELECT
  ✓ UNION (SELECT
  ✓ UN/**/ION/**/SEL   (obfuscated)
...
```

---

## 10. Phân Biệt Với `sqli-label-validator`

| Đặc điểm | `sqli-label-validator` (đã có) | `sqli-label-critic` (sẽ build) |
|-----------|-------------------------------|-------------------------------|
| Mục tiêu | Normalize format, check schema | Review correctness từng nhãn |
| Input | CSV schema check | Payload + label analysis |
| Output | Corrections report, normalized CSV | PASS/FLAG/REJECT + evidence |
| Cần AI? | Không (rule-based) | Có (signal matching + reasoning) |
| Granularity | Dataset level | Row level + token level |
| Benign check | Flag + SQL keywords | Deep audit với evidence |
| Priority check | Không | Có — core feature |

---

## 11. Pipeline Tổng Thể (3 Skills)

```
combined_labeled_data.csv
        │
        ▼
[sqli-label-validator]         ← Normalize format, fix typos
        │ combined_labeled_data_normalized.csv
        ▼
[sqli-labeler]                 ← Re-label low-confidence, out-of-taxonomy, unlabeled
        │ combined_labeled_data_relabeled.csv
        ▼
[sqli-label-critic]            ← Strict review, evidence-based
        │ label_review_results.csv
        ▼
Human Review (REJECT + FLAG)
        │
        ▼
master_labeled_data.csv        ← Final dataset → GAN Training Phase 3
```

---

## 12. Thước Đo Thành Công

| Metric | Target |
|--------|--------|
| PASS rate sau 2 rounds | ≥ 90% |
| REJECT rate vòng 1 | ≤ 10% (nếu cao hơn → re-run labeler) |
| Benign false negative rate | ≤ 2% |
| Reasoning quality (≥ 30 chars) | ≥ 95% |
| Conflict duplicates resolved | 100% |
