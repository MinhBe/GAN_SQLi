# Phase 2 — Rebuild Labeling System

> Mục tiêu: xây lại labeler từ đầu cho dữ liệu chỉ có `payload_norm`, tạo bộ nhãn có confidence, có taxonomy đúng, và có thể dùng cho training/evaluation.

---

## 1. Câu hỏi chính

Bạn hỏi:

> Nếu labeler lại thì sẽ gồm những gì?

Câu trả lời ngắn gọn:

```text
Labeler V5 không phải một script rule-based đơn giản.
Labeler V5 là một hệ thống weak supervision nhiều tầng:
  source-free heuristics
  SQL lexical parser
  attack technique detector
  intent detector
  db engine detector
  syntax validity checker
  conflict resolver
  confidence calibrator
  review priority ranker
```

Output không chỉ là `is_sqli`, mà là một schema nhiều chiều.

---

# 2. Vấn đề hiện tại

Hiện tại dữ liệu chỉ có:

```csv
payload_norm
```

Do đó labeler phải tái tạo tối thiểu các nhãn:

```text
is_sqli
technique_primary
intent_secondary
db_engine
syntax_validity
confidence_score
review_priority
```

Nếu chỉ làm:

```python
if "union select" in payload:
    label = "union_based"
```

thì sẽ gặp lại lỗi V1–V4:

```text
labeler bias
+ false confidence
+ gold set nhỏ
+ rare type bị drop
+ obfuscated payload không được học
```

---

# 3. Taxonomy label V5

## 3.1. Không dùng lại `primary_sqli_type` cũ theo dạng trộn

Không nên để chung:

```text
boolean_blind
time_blind
union_based
error_based
metadata_enumeration
db_fingerprint
```

vì đây không cùng cấp khái niệm.

## 3.2. Schema label mới

### A. Binary label

```text
is_sqli:
  0 = benign / non-SQLi
  1 = SQLi
  unknown = chưa đủ bằng chứng
```

### B. Technique primary

```text
technique_primary:
  benign
  boolean_blind
  time_blind
  union_based
  error_based
  stacked_queries
  out_of_band
  generic_injection
  unknown
```

### C. Intent secondary

```text
intent_secondary:
  none
  auth_bypass
  metadata_enumeration
  db_fingerprint
  data_exfiltration
  privilege_probe
  destructive_action
  obfuscation_only
  unknown
```

### D. DB engine

```text
db_engine:
  mysql
  postgresql
  mssql
  oracle
  sqlite
  multi
  generic_sql
  unknown
```

### E. Syntax validity

```text
syntax_validity:
  valid_query
  valid_fragment
  http_param
  encoded_payload
  malformed
  non_sql
  unknown
```

### F. Confidence

```text
confidence_score: 0.0 → 1.0

confidence_band:
  high    >= 0.90
  medium  >= 0.70 and < 0.90
  low     >= 0.40 and < 0.70
  reject  < 0.40
```

---

# 4. Labeler V5 gồm những module nào?

## 4.1. Module 1 — Lexical SQL signal detector

### Vai trò

Bắt tín hiệu SQL tổng quát:

```text
select
union
where
and/or
sleep
benchmark
waitfor
extractvalue
information_schema
--
#
/*
';
```

### Output

```csv
sql_keyword_score,
sql_operator_score,
comment_score,
literal_pattern_score
```

### Không dùng để kết luận cuối cùng

Module này chỉ tạo feature. Không được tự quyết định toàn bộ label.

---

## 4.2. Module 2 — SQLi technique detector

### Vai trò

Detect technique chính.

| Technique | Nhóm tín hiệu |
|---|---|
| `boolean_blind` | OR/AND condition, tautology, comparison logic |
| `time_blind` | sleep/benchmark/pg_sleep/waitfor/dbms_pipe/randomblob |
| `union_based` | union select, column count probing, null sequence |
| `error_based` | extractvalue/updatexml/xmltype/cast/convert error triggers |
| `stacked_queries` | semicolon + second statement |
| `out_of_band` | dns/http/external callback functions or patterns |
| `generic_injection` | SQLi-like nhưng chưa đủ phân loại |

### Output

```csv
technique_votes,
technique_primary_candidate,
technique_confidence
```

---

## 4.3. Module 3 — Intent detector

### Vai trò

Tách intent khỏi technique.

| Intent | Tín hiệu |
|---|---|
| `metadata_enumeration` | information_schema, table_name, column_name, sys tables |
| `db_fingerprint` | version(), @@version, banner, user(), database() |
| `auth_bypass` | login-style tautology |
| `data_exfiltration` | select columns, concat, group_concat |
| `destructive_action` | drop/delete/update/insert risky statements |
| `obfuscation_only` | comment/case/encoding noise nhưng không rõ attack |

### Output

```csv
intent_votes,
intent_secondary,
intent_confidence
```

---

## 4.4. Module 4 — DB engine detector

### Vai trò

Detect engine dựa trên function, system table, operator, syntax.

| Engine | Tín hiệu ví dụ |
|---|---|
| MySQL | `sleep`, `benchmark`, `extractvalue`, `updatexml`, `information_schema`, `@@version` |
| PostgreSQL | `pg_sleep`, `version()`, `current_database`, `pg_catalog` |
| MSSQL | `waitfor delay`, `@@version`, `xp_`, `sysobjects`, `char()` style |
| Oracle | `dbms_pipe`, `xmltype`, `dual`, `v$`, `utl_http` |
| SQLite | `sqlite_master`, `randomblob`, `sqlite_version` |

### Output

```csv
db_engine_votes,
db_engine,
db_engine_confidence
```

### Quy tắc quan trọng

Nếu có nhiều engine signal mâu thuẫn:

```text
db_engine = multi
confidence giảm
review_priority tăng
```

Nếu không có signal:

```text
db_engine = unknown
```

Không ép đoán.

---

## 4.5. Module 5 — Syntax/context validity checker

### Vai trò

Phân biệt:

```text
SQL query đầy đủ
SQL fragment
HTTP param chứa SQLi
encoded payload
malformed payload
non-SQL
```

### Vì sao cần?

GAN sinh token theo sequence. Nếu training lẫn:

```text
full query
+ fragment
+ HTTP URL
+ encoded text
+ JavaScript/XSS
```

model sẽ học distribution hỗn tạp.

### Output

```csv
syntax_validity,
context_type,
parse_error_type
```

---

## 4.6. Module 6 — Conflict resolver

### Vai trò

Hợp nhất kết quả từ nhiều detector.

Ví dụ conflict:

```text
technique detector: time_blind
intent detector: db_fingerprint
db detector: mysql
syntax checker: valid_fragment
```

Kết quả hợp lệ:

```text
is_sqli = 1
technique_primary = time_blind
intent_secondary = db_fingerprint
db_engine = mysql
```

Ví dụ conflict mạnh:

```text
technique detector: union_based
db detector: oracle + mysql
syntax checker: malformed
```

Kết quả:

```text
is_sqli = 1
technique_primary = union_based
db_engine = multi
confidence giảm
review_priority tăng
```

---

## 4.7. Module 7 — Confidence calibrator

### Vai trò

Không để rule agreement tạo false confidence.

Confidence nên dựa trên:

| Tín hiệu | Ảnh hưởng |
|---|---|
| nhiều detector độc lập cùng kết luận | tăng |
| SQL syntax/context rõ | tăng |
| db_engine rõ | tăng |
| duplicate cluster có label đồng nhất | tăng |
| technique và intent không mâu thuẫn | tăng |
| malformed/encoded quá nặng | giảm |
| engine conflict | giảm |
| duplicate cluster label conflict | giảm |
| rare class nhưng rule yếu | không drop ngay, đưa review |

### Công thức minh họa

```text
confidence =
  0.25 * sql_signal_score
+ 0.25 * technique_confidence
+ 0.20 * syntax_confidence
+ 0.15 * db_engine_confidence
+ 0.10 * cluster_consistency
+ 0.05 * intent_confidence
- conflict_penalty
```

---

## 4.8. Module 8 — Review priority ranker

### Vai trò

Chọn dòng đáng review bằng người hoặc LLM.

Priority cao nếu:

```text
rare technique
rare db_engine
high-impact conflict
unknown db_engine nhưng có function đặc trưng
duplicate cluster label conflict
benign giống SQLi
SQLi bị obfuscate mạnh
confidence medium nhưng sample có giá trị học cao
```

### Output

```csv
review_priority: 1 → 5
review_reason
```

---

# 5. Output schema Phase 2

Tạo file:

```text
data/labeled/phase2_labeled_payloads.parquet
```

Schema:

```csv
v5_row_id,
payload_raw,
payload_core,
payload_canonical,
payload_delex,

is_sqli,
technique_primary,
intent_secondary,
db_engine,
syntax_validity,

sql_signal_score,
technique_confidence,
intent_confidence,
db_engine_confidence,
syntax_confidence,
confidence_score,
confidence_band,

label_votes_json,
conflict_flags,
review_priority,
review_reason,

dedup_hash,
near_dup_cluster_id,
split_eligible
```

---

# 6. Gold/Silver/Bronze mới

## 6.1. Không dùng high-confidence quá hẹp

Nếu chỉ lấy `confidence >= 0.90`, gold có thể quá nhỏ và lệch về pattern dễ detect.

V5 nên chia:

| Tier | Điều kiện | Cách dùng |
|---|---|---|
| Gold | confidence cao + conflict thấp + cluster sạch | train/eval chính |
| Silver | confidence vừa + useful diversity | train phụ, semi-supervised |
| Bronze | confidence thấp hoặc conflict | không train generator trực tiếp |
| Review | rare/conflict/high-value | manual/LLM review |

## 6.2. Gold không chỉ dựa trên confidence

Một sample gold cần:

```text
confidence_score cao
+ cluster consistency cao
+ technique rõ
+ syntax/context rõ
+ không leak sang val/test
```

## 6.3. Balanced gold

Gold nên cân bằng theo:

```text
technique_primary
db_engine
syntax_validity
source-like cluster
```

Không để time_blind hoặc boolean_blind áp đảo.

---

# 7. Dataset split sau labeling

Không split ngẫu nhiên theo row.

Split theo:

```text
near_dup_cluster_id
```

Quy tắc:

```text
toàn bộ cluster vào train hoặc val hoặc test
không chia cluster sang nhiều split
```

Output:

```csv
split:
  train
  val
  test
  holdout_rare
```

---

# 8. Quality gates Phase 2

Phase 2 chỉ pass nếu có báo cáo:

| Metric | Target |
|---|---:|
| Gold size | tối thiểu 10k nếu có thể |
| Technique entropy | > 2.0 bits |
| Top-10 delex coverage trong gold | < 10% |
| Delex collision trong gold | < 10% |
| Unknown db_engine trong engine-specific train | không dùng |
| Label conflict rate | report rõ |
| Cluster leakage | 0 |
| Rare class count | report từng class |

---

# 9. Folder output đề xuất

```text
data/
├── labeled/
│   ├── phase2_labeled_payloads.parquet
│   ├── gold.parquet
│   ├── silver.parquet
│   ├── bronze.parquet
│   ├── review_queue.parquet
│   └── label_taxonomy.json
└── reports/
    ├── phase2_label_distribution.md
    ├── phase2_conflict_report.md
    └── phase2_gold_quality_report.md
```

---

# 10. Kết luận Phase 2

Labeler V5 không chỉ trả lời:

```text
Payload này có phải SQLi không?
```

Mà phải trả lời:

```text
Nó có phải SQLi không?
Nó thuộc technique nào?
Intent phụ là gì?
Nó nghiêng về DB engine nào?
Nó là full query, fragment, HTTP param hay malformed?
Mức tin cậy bao nhiêu?
Có đáng review không?
Có nên đưa vào gold/silver/bronze không?
```

Nếu Phase 2 làm tốt, GAN sẽ học từ signal sạch hơn rất nhiều.
