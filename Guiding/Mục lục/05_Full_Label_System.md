# 05 — Full Label System

> Mục tiêu: xây hệ thống gán nhãn nhiều tầng cho SQLi, không chỉ binary label, có confidence calibration, conflict handling, review queue và provenance.

---

## 1. Vấn đề cần giải quyết

Dữ liệu sau foundation vẫn chưa có ý nghĩa bảo mật đầy đủ.

Cần biết:

```text
payload có phải SQLi không?
thuộc technique nào?
intent phụ là gì?
nghiêng về DB engine nào?
syntax/context là gì?
confidence bao nhiêu?
có cần review không?
```

Không được lặp lại lỗi cũ:

```text
rule + heuristic cùng keyword matching
→ false confidence
→ gold set lệch về pattern dễ detect
```

---

## 2. Tính chất của phase này

| Tính chất | Diễn giải |
|---|---|
| Weak supervision | Nhiều detector yếu kết hợp |
| Taxonomy-aware | Tách technique, intent, db, syntax |
| Confidence-calibrated | Confidence phải có ý nghĩa xác suất tương đối |
| Conflict-aware | Không ép nhãn khi bằng chứng mâu thuẫn |
| Review-driven | Ưu tiên review sample có giá trị cao |

---

## 3. Taxonomy chính

### 3.1. is_sqli

```text
0 = benign / non-SQLi
1 = SQLi
unknown = chưa đủ bằng chứng
```

### 3.2. technique_primary

```text
benign
boolean_blind
time_blind
union_based
error_based
stacked_queries
out_of_band
generic_sqli
unknown
```

### 3.3. intent_secondary

Nên hỗ trợ multi-label:

```text
auth_bypass
metadata_enumeration
db_fingerprint
data_exfiltration
privilege_probe
destructive_action
obfuscation_only
none
unknown
```

### 3.4. db_engine / db_family

```text
mysql
postgresql
mssql
oracle
sqlite
generic_sql
multi
unknown
```

Có thể thêm `db_family` để giảm sparse:

```text
mysql_like
postgresql
mssql
oracle
sqlite_or_generic
unknown
```

### 3.5. syntax_validity

```text
valid_query
valid_fragment
http_param
encoded_payload
malformed
non_sql
unknown
```

---

## 4. Các module labeler

### 4.1. Lexical SQL signal detector

Detect:

```text
SQL keywords
operators
comments
quotes
functions
boolean operators
union markers
time functions
error functions
```

Output:

```text
sql_signal_score
```

### 4.2. Technique detector

Detect:

```text
boolean_blind
time_blind
union_based
error_based
stacked_queries
out_of_band
generic_sqli
```

Output:

```text
technique_votes
technique_primary_candidate
technique_confidence
```

### 4.3. Intent detector

Detect:

```text
metadata_enumeration
db_fingerprint
auth_bypass
data_exfiltration
destructive_action
```

Output multi-label:

```text
intent_votes
intent_secondary_multilabel
intent_confidence
```

### 4.4. DB detector

Detect engine từ:

```text
function
system table
syntax
operator
keyword
```

Ví dụ:

| Engine | Signals |
|---|---|
| MySQL | sleep, benchmark, extractvalue, updatexml, information_schema |
| PostgreSQL | pg_sleep, pg_catalog, current_database |
| MSSQL | waitfor delay, @@version, sysobjects, xp_ |
| Oracle | dbms_pipe, xmltype, dual, v$ |
| SQLite | sqlite_master, randomblob, sqlite_version |

Output:

```text
db_engine_votes
db_engine
db_confidence
```

### 4.5. Syntax/context checker

Classify:

```text
valid SQL query
SQL fragment
HTTP param
encoded payload
malformed
non-SQL
```

---

## 5. Conflict resolver

Conflict examples:

```text
union_based + malformed
mysql + oracle signals
time_blind + no time function
SQLi signal high + syntax non_sql
```

Resolver output:

```text
final labels
conflict_flags
confidence_adjustment
review_reason
```

Không ép đoán nếu conflict quá mạnh.

---

## 6. Confidence calibrator

Confidence không chỉ là rule score.

Nó nên dựa trên:

```text
detector agreement
syntax clarity
db clarity
cluster consistency
lane reliability
conflict severity
manual/LLM verification nếu có
```

Pseudo-score:

```text
confidence =
  sql_signal
+ technique_confidence
+ syntax_confidence
+ db_confidence
+ cluster_consistency
- conflict_penalty
- lane_uncertainty_penalty
```

Sau đó cần calibration bằng verified/review set.

---

## 7. Review queue

Không chỉ review low confidence.

Priority cao nếu:

```text
rare technique
rare db engine
large duplicate cluster representative
high conflict
boundary benign/SQLi
engine-specific syntax
Lane X/D nhưng pattern quan trọng
medium confidence nhưng high value
```

Output:

```text
review_priority
review_reason
```

---

## 8. Gold / Silver / Bronze

### 8.1. Gold

Không chỉ high-confidence obvious.

Gold nên gồm:

```text
high-confidence clean samples
reviewed rare samples
verified engine-specific samples
hard benign samples
```

### 8.2. Silver

```text
medium confidence
low conflict
useful diversity
```

### 8.3. Bronze

```text
low confidence
conflict
uncertain lane
not used for main generator training
```

---

## 9. Label provenance

Mỗi label cần biết đến từ đâu:

```text
rule_detector
syntax_checker
db_detector
classifier
LLM
human
DB_execution
source_cluster
```

Schema:

```text
label_sources_json
verified_label_flag
verified_by
```

---

## 10. Kết quả đầu ra

```text
data/phase05/phase05_labeled.parquet
data/phase05/gold.parquet
data/phase05/silver.parquet
data/phase05/bronze.parquet
data/phase05/review_queue.parquet
reports/05_label_distribution.md
reports/05_conflict_report.md
reports/05_gold_quality_report.md
```

Schema:

```csv
row_id,
payload_delex_v5,
payload_working,
lane,
is_sqli,
technique_primary,
intent_secondary_multilabel,
db_engine,
db_family,
syntax_validity,
confidence_score,
confidence_band,
conflict_flags,
review_priority,
review_reason,
label_sources_json,
verified_label_flag,
split
```

---

## 11. Cách evaluate phase này

| Metric | Ý nghĩa |
|---|---|
| Label distribution | Kiểm tra lệch class |
| Technique entropy | Độ đa dạng technique |
| Conflict rate | Tỷ lệ mâu thuẫn |
| Unknown db rate | DB label có hữu dụng không |
| Gold size | Có đủ train/eval không |
| Gold diversity | Không toàn pattern obvious |
| Confidence calibration | Confidence có đáng tin không |
| Review yield | Queue review có nhiều sample giá trị không |
| Cluster leakage | 0 giữa split |

Không dùng top-10 coverage ngưỡng cứng. Dùng relative/per-condition report:

```text
generated/train top-k ratio
top-k per technique
top-k per lane
```

---

## 12. Kết luận

Label system không chỉ gán nhãn. Nó là hệ thống kiểm soát chất lượng semantic cho toàn bộ pipeline.
