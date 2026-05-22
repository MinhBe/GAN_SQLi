# 04 — Full Data Foundation Và Action Taxonomy

> Mục tiêu: dựng nền dữ liệu full cho action-surgery, kế thừa Phase 4 nhưng bổ sung taxonomy phi-literal/tamper.

---

## 1. Nền hiện có

Phase 4 đã xử lý `12,753,953` dòng, có `12,753,951` exact unique canonical payloads, `4,131,974` near-duplicate cluster buckets, và `268,272` delex template keys. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:4-5`](..\..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:19-22`](..\..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

Cluster leakage đã bằng `0`; mọi split mới phải giữ nguyên nguyên tắc này. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:33`](..\..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

---

## 2. Bổ sung cần làm

```text
canonical_action_view
libinjection_token_view
tamper_action_candidates
action_equivalence_rules
dialect_compatibility_tags
round_trip_action_map
```

---

## 3. Action taxonomy full

Nhóm action:

```text
case
comment
whitespace
encoding
operator_equivalence
keyword_split
function_variant
literal_transform
logic_constant
dialect_specific
```

Mỗi action phải có:

```text
action_id
action_family
precondition
payload_span
before_value
after_value
dialect_allowed
semantic_risk_level
round_trip_status
```

---

## 4. Relex và dialect

Không dùng sqlite execution như hard constraint duy nhất cho payload đa dialect. Phản biện đã chỉ ra MySQL/MSSQL payload có thể fail sqlite dù hợp lệ ở DB đích. [`Guiding_Gumbel-Softmax\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md:46-48`](..\02_Phan_Bien_Doc_Lap_Va_Bo_Sung.md)

Kế hoạch:

```text
sqlite: fast proxy
mysql/postgres/mssql: dialect lab nếu có môi trường
unknown dialect: parse/structure/slot validity, không hard-fail execution
```

---

## 5. Output

```text
data/gumbel/full/action_foundation.parquet
data/gumbel/full/action_taxonomy.json
data/gumbel/full/action_splits.json
data/gumbel/full/near_dup_action_clusters.parquet
reports/gumbel/04_full_data_foundation_action_taxonomy.md
```

---

## 6. Gate

Phase này pass nếu:

```text
cluster leakage = 0
round_trip_action_success >= ngưỡng đăng ký
action family chính có train/dev/test coverage
top action/template không thống trị quá mức
literal-only fallback được đánh dấu riêng
```

---

## 7. Kết luận

Full data foundation của nhánh Gumbel không phải chỉ là delex. Nó phải biến SQLi payload thành không gian **action có nghĩa**, vì action mới là đối tượng generator học.
