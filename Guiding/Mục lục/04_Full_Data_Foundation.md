# 04 — Full Data Foundation

> Mục tiêu: xây nền dữ liệu đầy đủ sau khi đã có Data Reality Check và Decision Gate. Phase này tạo dataset sạch, dedup, lane-aware, delex/relex được, và split không leakage.

---

## 1. Vấn đề cần giải quyết

Dữ liệu đầu vào lớn nhưng không đồng nhất:

```text
14.47M payload_norm
nhiều nguồn trộn
duplicate/near-duplicate
raw-like/normalized/delexed/mixed
literal có thể mất
wrapper có thể tồn tại
```

Nếu không xử lý tốt:

```text
train/val leakage
memorization
delex collision
relex sai
label sai
metric ảo
```

---

## 2. Tính chất của phase này

| Tính chất | Diễn giải |
|---|---|
| Lane-aware | Xử lý theo N/R/D/X/M |
| Non-destructive | Giữ payload input gốc quan sát được |
| Dedup-first | Exact dedup trước label/train |
| Relex-aware | Thiết kế relex từ đầu |
| Split-safe | Split theo cluster, không theo row |

---

## 3. Input

Từ phase 01:

```text
data/phase01/phase01_data_reality.parquet
```

và bài học từ phase 02:

```text
literal pools ban đầu
delex rules ban đầu
sampling/lane observations
```

---

## 4. Canonicalization

### 4.1. Mục tiêu

Tạo dạng chuẩn để so sánh payload.

### 4.2. Cách làm

```text
normalize whitespace
lowercase shadow copy
normalize quote form nếu an toàn
normalize comments
normalize numeric literals cho canonical key
preserve SQL keywords/functions quan trọng
```

Không overwrite `payload_input`.

Output:

```text
payload_canonical_light
payload_canonical_structural
```

---

## 5. Exact dedup

### 5.1. Phương pháp

Hash:

```text
sha256(payload_canonical_light)
```

Output:

```text
dedup_hash
duplicate_count
first_seen_row_id
is_exact_duplicate
```

### 5.2. Cách dùng

Training chỉ dùng representative, nhưng giữ duplicate_count để biết pattern phổ biến.

---

## 6. Near-dedup

### 6.1. Phương pháp

Dùng candidate trước, full sau nếu cần:

```text
SimHash
MinHash
token n-gram similarity
```

Không bắt buộc full 14.47M ngay nếu tài nguyên hạn chế.

### 6.2. Output

```text
near_dup_cluster_id
near_dup_cluster_size
cluster_representative
```

---

## 7. Lane-aware processing

### 7.1. Lane N

```text
wrapper detect
strip wrapper nếu có
delex_v5
literal extraction
relex map creation
```

### 7.2. Lane R

```text
safe decode
nếu decode tốt → Lane N
nếu không → giữ R hoặc chuyển M
```

### 7.3. Lane D

```text
giữ delex input
không claim literal fidelity
dùng cho structure/type phụ
```

### 7.4. Lane X

```text
mặc định như Lane D
audit riêng
không dùng WAF/DB chính nếu không recover được
```

### 7.5. Lane M

```text
cách ly
không train
chỉ report
```

---

## 8. Delex v5

### 8.1. Nguyên tắc

Không xóa function quan trọng.

Preserve:

```text
sleep
pg_sleep
waitfor
benchmark
dbms_pipe
extractvalue
updatexml
xmltype
group_concat
version
database
user
information_schema
sqlite_master
```

Replace:

```text
string literal → __STR__
numeric literal → __NUM__
time literal → __TIME__
identifier generic → __ID__
table generic → __TABLE__
comment → __COMMENT__
```

### 8.2. Output

```text
payload_delex_v5
delex_version
delex_flags
delex_collision_key
```

---

## 9. Relex map

### 9.1. Vì sao cần

WAF/DB/IDS không đánh giá delex template. Chúng đánh giá payload literal.

### 9.2. Thành phần

```text
placeholder type
literal pool
context
db hint
technique hint
source lane
delex template
candidate fill values
```

### 9.3. Literal pools

```text
STR_POOL
NUM_POOL
TIME_POOL
ID_POOL
TABLE_POOL
COMMENT_POOL
DB_FUNCTION_POOL
```

### 9.4. Context-aware fill

Ví dụ:

```text
pg_sleep(__TIME__)      → pg_sleep(5)
sleep(__TIME__)         → sleep(5)
waitfor delay __TIME__  → waitfor delay '0:0:5'
__STR__ = __STR__       → '1'='1'
UNION SELECT __NUM__    → UNION SELECT 1
```

---

## 10. Round-trip test

Kiểm tra:

```text
payload_working
→ delex_v5
→ relex
→ classify/evaluate
```

Metrics:

```text
round_trip_success_rate
technique_preserved_rate
db_hint_preserved_rate
syntax_preserved_rate
```

---

## 11. Split theo cluster

Không split theo row.

Quy tắc:

```text
cùng near_dup_cluster_id chỉ được nằm trong một split
```

Splits:

```text
train
val
test
verified_candidate
holdout_rare
```

---

## 12. Kết quả đầu ra

```text
data/phase04/phase04_payload_foundation.parquet
data/phase04/exact_dedup_map.parquet
data/phase04/near_dup_clusters.parquet
data/phase04/relex_map.parquet
data/phase04/literal_pools.json
reports/04_data_foundation_report.md
```

Schema chính:

```csv
row_id,
payload_input,
lane,
lane_confidence,
payload_working,
payload_canonical_light,
payload_delex_v5,
dedup_hash,
duplicate_count,
near_dup_cluster_id,
delex_version,
relex_map_id,
round_trip_status,
split
```

---

## 13. Cách evaluate phase này

| Metric | Yêu cầu |
|---|---|
| Exact dedup report | Có |
| Near-dup leakage | 0 giữa train/val/test |
| Lane distribution | Có report |
| Delex collision | Report theo lane và technique nếu có |
| Relex round-trip | Có rate và sample lỗi |
| Literal preservation | Report theo lane |
| Split integrity | Cluster không bị chia |

---

## 14. Kết luận

Phase này tạo nền dữ liệu thật sự để label và train. Nếu relex map không tốt, các metric WAF/DB ở phase sau không đáng tin.
