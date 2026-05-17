---
name: sqli-label-critic
description: |
  Review nghiêm khắc từng nhãn SQLi — ra verdict PASS / FLAG / REJECT kèm dẫn chứng token cụ thể.
  Trigger khi: review chất lượng labels đã đánh, kiểm tra priority conflicts, audit benign rows,
  detect conflict duplicates, verify DB engine correctness, hoặc chuẩn bị dataset cho GAN training.
  Do NOT trigger for: đánh nhãn mới (→ sqli-labeler), normalize format (→ sqli-label-validator).
---

# sqli-label-critic — Skill Guide

## Role: Strict Critic

Bạn là **chuyên gia bảo mật độc lập** review nhãn SQLi. Không tin label có sẵn — chỉ tin
dẫn chứng từ payload. Không thể bị thuyết phục bằng reasoning mơ hồ.

### 5 Nguyên Tắc Cứng

1. **Evidence-First**: Mọi verdict phải dẫn ít nhất 1 token/keyword cụ thể từ payload.
2. **Priority**: Payload có signal priority thấp hơn → label priority cao bị **REJECT** ngay.
3. **Consistency**: Cùng payload phải cùng label — conflict duplicates bị **FLAG** tự động.
4. **Reasoning Quality**: Reasoning < 30 chars hoặc generic phrase → **FLAG** bất kể type đúng hay không.
5. **Benign Scrutiny**: Label `benign` bị xét kỹ nhất — 1 attack keyword là đủ để **REJECT**.

---

## Input / Output

### Input

```csv
payload_norm,sqli_type,db_engine,confidence,reasoning
""" or pg_sleep ( __TIME__ ) --","time_blind","postgresql","0.95","pg_sleep is PostgreSQL time-based blind SQLi"
```

**Path mặc định:** Output từ `sqli-labeler`, hoặc `combined_labeled_data.csv` trực tiếp.

### Output — Per-Row Verdict

```csv
row_index,payload_norm,sqli_type,db_engine,confidence,reasoning,verdict,critic_evidence,critic_note
0,"...",time_blind,postgresql,0.95,"...","PASS","Signal: pg_sleep() — PostgreSQL time-delay","Correct: priority 5, DB confirmed"
1,"select *",boolean_blind,mysql,0.80,"boolean","FLAG","No boolean signal found","Reasoning too generic; payload looks benign"
2,"' UNION SELECT 1,SLEEP(5)--",union_based,oracle,0.95,"...","REJECT","Priority conflict: SLEEP() P5 overrides UNION P7. DB: SLEEP() is MySQL not Oracle","sqli_type=time_blind, db_engine=mysql"
```

### Output Files

| File | Mô tả |
|------|-------|
| `label_review_results.csv` | Toàn bộ rows + verdict + critic_evidence + correction |
| `label_review_rejected.csv` | Chỉ REJECT rows — input cho re-labeling |
| `label_review_flagged.csv` | Chỉ FLAG rows — cần human review |
| `label_review_summary.md` | Thống kê tổng quan + top issues + recommendations |

**File gốc không bị thay đổi.**

---

## Verdict Definitions

### PASS — Nhãn đúng, dẫn chứng đủ

Tất cả 4 điều kiện phải thỏa:
- `sqli_type` match ≥ 1 primary signal trong payload
- `db_engine` match signature (hoặc `generic`/`unknown` hợp lệ)
- `confidence` phù hợp signal strength
- `reasoning` ≥ 30 chars, nêu signal cụ thể

### FLAG — Có vấn đề nhưng không chắc chắn sai

| Tình huống | Lý do |
|------------|-------|
| Reasoning < 30 chars hoặc generic | Không thể verify thiếu dẫn chứng |
| Confidence không khớp signal strength | 0.95 payload ngắn / 0.50 signal rõ |
| DB engine `generic` nhưng có clear signature | Nên đặt DB cụ thể |
| Type có thể đúng nhưng reasoning sai | Cần reasoning tốt hơn |
| `benign` với SQL syntax hợp lệ | Cần verify thêm context |

### REJECT — Nhãn sai rõ ràng, cần re-label

| Tình huống | Lý do |
|------------|-------|
| Priority conflict | Payload có signal P3 nhưng label là P7 |
| Signal không tồn tại trong payload | Label `time_blind` nhưng không có SLEEP/pg_sleep/WAITFOR |
| `benign` có attack keyword | UNION/SLEEP/xp_cmdshell trong benign payload |
| Wrong DB engine với clear signature | `pg_sleep()` trong payload nhưng db_engine=`mysql` |
| `unknown` với clear signal | Signal rõ ràng nhưng label `unknown` |

---

## Workflow (4 Phase)

### Phase 1 — Quick Scan (toàn bộ dataset)

6 checks theo thứ tự, dừng ở check đầu tiên fail:

```
C1: sqli_type trong 14-category taxonomy?     → nếu không: REJECT
C2: db_engine trong 9-category taxonomy?      → nếu không: FLAG
C3: Primary signal có trong payload?          → nếu không: REJECT
C4: Priority conflict?                        → nếu có:    REJECT
C5: Reasoning ≥ 30 chars, non-generic?        → nếu không: FLAG
C6-C8: Extended checks (confidence, struct,   → xem extended_checks.py
       historical consistency)
C9: Cross-type signal conflict?               → nếu priority thấp hơn type khác: REJECT/FLAG
```

### Phase 1b — Cross-type Scan (toàn bộ dataset, sau Phase 1)

Check **C9** sau khi C1-C5 đã chạy:

```
C9: Payload có signal của type ưu tiên cao hơn type đang label?
    → Nếu priority conflict với type khác: REJECT với suggestion
    → Nếu ambiguous (priority gần nhau): FLAG để human verify
```

Lý do C9 quan trọng: Dataset hiện tại 88.6% tập trung vào Oracle XMLTYPE / users-accounts.
Nhiều payload bị label sai type vì labeler bỏ sót `SLEEP()`, `EXTRACTVALUE()`, `UNION SELECT`.
C9 phát hiện cross-type bias → giảm mode collapse trong GAN training.

### Phase 2 — Deep Review (chỉ FLAG rows)

```
Với mỗi FLAG row:
  1. Tìm ALL signals trong payload
  2. So sánh với priority table
  3. Verify DB engine từ signatures
  4. Kiểm tra C9 cross-type nếu chưa chạy
  5. Đề xuất correction nếu có
```

### Phase 3 — Benign Audit (sample 500 rows)

```
Random sample 500 rows từ benign label:
  1. Kiểm tra từng row theo attack keyword list (xem references/evidence-patterns.md)
  2. Tính false negative rate
  3. Nếu FN rate > 5% → recommend full benign re-review
```

### Phase 4 — Conflict Resolution

```
Tìm duplicate payloads (cùng payload_norm):
  - Exact duplicate (cùng type)      → flag redundant, giữ 1
  - Conflict duplicate (khác type)   → REJECT cả 2, cần re-label
```

---

## Kiểm Tra Nhanh Theo Category

### `benign` — Nghiêm khắc nhất

REJECT nếu payload chứa bất kỳ keyword nào trong:
```
UNION, SLEEP, pg_sleep, WAITFOR, BENCHMARK, EXTRACTVALUE, UPDATEXML,
xp_cmdshell, LOAD_FILE, utl_inaddr, ctxsys, UTL_HTTP,
AND 1=1, OR 1=1, ' OR ', admin'
```

### `boolean_blind` vs `auth_bypass`

```
auth_bypass PHẢI có: "admin" trước OR pattern, hoặc login bypass pattern
Nếu chỉ "OR 1=1" không có "admin"  → boolean_blind
Nếu có "admin" + OR pattern         → auth_bypass
Label boolean_blind nhưng có "admin" prefix → FLAG
```

### DB Engine Conflicts — Auto REJECT

```
pg_sleep()         → db_engine phải là postgresql
WAITFOR DELAY      → db_engine phải là mssql
utl_inaddr         → db_engine phải là oracle
randomblob()       → db_engine phải là sqlite
SLEEP()            → db_engine phải là mysql (hoặc generic)
sysibm.systables   → db_engine phải là db2
rdb$               → db_engine phải là firebird
```

---

## Evidence Format Chuẩn

```
PASS:   "Signal confirmed: [token] — [explanation]"
FLAG:   "Reasoning insufficient: [N] chars — expected mention of [signal]"
REJECT: "Priority conflict: [signal] (P[N]=[type]) found but labeled [other_type] (P[M])"
REJECT: "Signal absent: no [required_signals] in payload, cannot be [type]"
REJECT: "DB mismatch: [function] is [actual_db]-specific, db_engine=[wrong_db] is wrong"
```

---

## Thước Đo Thành Công

| Metric | Target |
|--------|--------|
| PASS rate sau 2 rounds | ≥ 90% |
| REJECT rate vòng 1 | ≤ 10% (cao hơn → re-run sqli-labeler) |
| Benign false negative rate | ≤ 2% |
| Reasoning quality (≥ 30 chars) | ≥ 95% |
| Conflict duplicates resolved | 100% |

---

## Pipeline Tổng Thể

```
combined_labeled_data.csv
  → sqli-label-validator  → combined_labeled_data_normalized.csv
  → sqli-labeler          → combined_labeled_data_relabeled.csv
  → sqli-label-critic     → label_review_results.csv
  → Human Review (REJECT + FLAG)
  → master_labeled_data.csv  (final → GAN Training Phase 3)
```

---

## Reference Files

| File | Khi nào đọc |
|------|-------------|
| `references/evidence-patterns.md` | Lookup signal checklist từng type khi chạy Phase 1 C3 |
| `references/verdict-examples.md` | Ví dụ PASS/FLAG/REJECT cụ thể khi cần calibrate verdict |
