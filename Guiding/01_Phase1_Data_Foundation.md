# Phase 1 — Data Foundation

> Mục tiêu: biến 16 CSV shard chỉ có cột `payload_norm` thành một nền dữ liệu sạch, dedup được, canonical được, và sẵn sàng cho labeling.

---

## 1. Vấn đề hiện tại

Hiện tại dữ liệu đầu vào chỉ có:

```csv
payload_norm
```

Không có source, không có label, không có db engine, không có injection type, không có confidence.

Vì vậy Phase 1 không được làm labeling ngay. Trước tiên phải tạo lại nền dữ liệu.

Nếu label ngay trên dữ liệu raw:

```text
duplicate còn nguyên
wrapper còn nguyên
encoding chưa thống nhất
SQL fragment lẫn HTTP fragment
near-duplicate nằm ở cả train/val/test
```

thì mọi bước sau sẽ nhiễu.

---

## 2. Hướng xử lý ở mức giải pháp

Phase 1 gồm 8 bước:

| Bước | Tên | Mục tiêu |
|---|---|---|
| 1 | Load shards | Đọc 16 file CSV an toàn, stream/chunk |
| 2 | Basic normalize | Chuẩn hóa encoding, whitespace, null, quote |
| 3 | Decode variants | URL decode, HTML decode, unicode normalization |
| 4 | Exact dedup | Xóa payload trùng hệt |
| 5 | Canonicalize | Tạo dạng canonical để so sánh payload |
| 6 | Near-dedup | Gom cụm payload gần giống nhau |
| 7 | Wrapper detection/strip | Tách payload attack khỏi SQL/HTTP wrapper |
| 8 | Delex v2 preparation | Chuẩn bị payload cho tokenizer/model |

---

# 3. Diễn giải chi tiết nguyên nhân và giải pháp

## 3.1. Load shards

### Nguyên nhân cần làm kỹ

Dataset 14.47M rows lớn, nếu load toàn bộ vào memory dễ lỗi RAM.

### Giải pháp

Đọc từng file theo chunk:

```python
for file in shard_files:
    for chunk in pd.read_csv(file, chunksize=200_000):
        process(chunk)
```

### Output

```csv
row_id,
payload_norm
```

Trong đó `row_id` là ID mới của V5, không phụ thuộc index cũ.

---

## 3.2. Basic normalize

### Vấn đề

Một payload có thể xuất hiện dưới nhiều dạng:

```text
' OR '1'='1' --
' OR '1' = '1' --
'  OR  '1'='1'  --
%27%20OR%20%271%27%3D%271%27%20--
```

Nếu không normalize, dedup sẽ bỏ sót.

### Giải pháp

Tạo `payload_norm_v5`:

| Normalize | Mô tả |
|---|---|
| Unicode NFKC | Chuẩn hóa unicode |
| Strip outer whitespace | Xóa khoảng trắng đầu/cuối |
| Collapse whitespace | Nhiều whitespace thành một space |
| Lowercase shadow copy | Chỉ dùng cho hash/canonical, không thay raw |
| Quote normalization | Chuẩn hóa quote nếu an toàn |
| Remove null bytes | Xóa ký tự lỗi |

### Output

```csv
payload_raw,
payload_norm_v5,
normalization_flags
```

---

## 3.3. Decode variants

### Vấn đề

Nhiều payload bị URL-encoded hoặc HTML-encoded:

```text
%27+OR+%271%27%3D%271
&#x27; OR &#x27;1&#x27;=&#x27;1
```

Nếu không decode:

- labeler rule không nhận ra SQLi;
- tokenizer học token rác;
- duplicate không được gom.

### Giải pháp

Tạo nhiều view:

```text
payload_raw
payload_url_decoded_once
payload_url_decoded_recursive_safe
payload_html_decoded
payload_best_view
```

Không nên overwrite raw. Luôn giữ raw để trace.

### Rule chọn `payload_best_view`

```text
Nếu decoded version tăng số token SQL hợp lệ
và không tạo ký tự lỗi
→ chọn decoded làm best view
ngược lại giữ bản normalized
```

### Output

```csv
payload_raw,
payload_norm_v5,
payload_decoded,
decode_depth,
decode_flags
```

---

## 3.4. Exact dedup

### Vấn đề

Nếu cùng payload xuất hiện 10,000 lần, model sẽ overweight pattern đó.

### Giải pháp

Tạo hash:

```text
sha256(payload_canonical_light)
```

Trong đó `payload_canonical_light` là bản đã:

- strip whitespace;
- lowercase shadow;
- normalize quote nhẹ;
- decode an toàn.

### Output

```csv
dedup_hash,
duplicate_count,
first_seen_row_id,
is_exact_duplicate
```

Chỉ giữ một row đại diện cho training, nhưng lưu `duplicate_count` để biết pattern phổ biến.

### Lưu ý

Không xóa duplicate vĩnh viễn. Nên lưu:

```text
dedup_map.parquet
```

để truy vết.

---

## 3.5. Canonicalize

### Mục tiêu

Tạo dạng canonical để so sánh payload khác nhau về format nhưng giống cấu trúc.

Ví dụ:

```sql
SELECT * FROM users WHERE id=1 OR 1=1
select * from users where id = 1 or 1 = 1
```

nên gần nhau trong canonical form.

### Canonical form đề xuất

```text
lowercase keywords
collapse whitespace
normalize numeric literals
normalize string literals
normalize comments
preserve SQL functions
preserve operators
```

Ví dụ:

```sql
SELECT name FROM users WHERE id=1 OR 'a'='a' --
```

thành:

```sql
select __id__ from __table__ where __id__ = __num__ or __str__ = __str__ __comment__
```

### Output

```csv
payload_canonical,
canonical_hash
```

---

## 3.6. Near-dedup

### Vấn đề

Exact dedup không bắt được near-duplicate.

Ví dụ:

```sql
' OR 1=1 --
' or 1 = 1 #
" OR "1"="1" /*
```

### Giải pháp

Dùng clustering nhẹ:

| Kỹ thuật | Vai trò |
|---|---|
| SimHash | Nhanh cho token shingles |
| MinHash | Tốt cho Jaccard similarity |
| Token n-gram | So sánh cấu trúc |

### Output

```csv
near_dup_cluster_id,
near_dup_cluster_size,
near_dup_representative
```

### Quy tắc split

Rất quan trọng:

```text
Không được để cùng near_dup_cluster_id xuất hiện ở cả train và val/test.
```

Nếu không, validation metric sẽ đẹp giả.

---

## 3.7. Wrapper detection và strip wrapper

### Vấn đề

Payload có thể nằm trong:

```sql
SELECT * FROM users WHERE username = '<payload>'
```

hoặc URL:

```text
?id=1' OR '1'='1'--
```

Nếu không strip wrapper đúng, delex có thể nuốt mất attack pattern.

### Giải pháp

Tạo `wrapper_type`:

| wrapper_type | Ví dụ |
|---|---|
| `raw_payload` | `' OR 1=1 --` |
| `sql_query_wrapper` | `SELECT * FROM users WHERE id=...` |
| `http_param_wrapper` | `id=1' OR 1=1` |
| `url_wrapper` | `/search?q=...` |
| `unknown_wrapper` | Không rõ |

Tạo `payload_core`:

```text
payload_best_view
→ detect wrapper
→ extract likely injected segment
```

### Output

```csv
payload_best_view,
wrapper_type,
payload_core,
strip_confidence
```

---

## 3.8. Delex v2 preparation

### Mục tiêu

Tạo biểu diễn cho model nhưng không làm mất SQL semantics.

### Sai lầm cần tránh

Không được xóa toàn bộ function names thành `__FUNC__`, vì:

```text
sleep
pg_sleep
waitfor
extractvalue
xmltype
group_concat
```

là tín hiệu quan trọng cho technique và db_engine.

### Giải pháp

Delex v2:

```text
replace identifiers → __ID__
replace table names → __TABLE__
replace numbers → __NUM__
replace generic strings → __STR__
preserve SQL keywords
preserve SQL operators
preserve whitelisted functions
preserve comment markers
preserve db-specific tokens
```

### Output

```csv
payload_delex,
delex_collision_key,
delex_flags
```

---

# 4. Schema output Phase 1

Sau Phase 1, tạo file:

```text
data/processed/phase1_payload_foundation.parquet
```

Schema:

```csv
v5_row_id,
payload_raw,
payload_norm_v5,
payload_decoded,
payload_best_view,
payload_core,
wrapper_type,
strip_confidence,
payload_canonical,
dedup_hash,
duplicate_count,
canonical_hash,
near_dup_cluster_id,
near_dup_cluster_size,
payload_delex,
delex_collision_key,
normalization_flags,
decode_flags,
delex_flags
```

---

# 5. Quality gates Phase 1

Phase 1 chỉ pass nếu đo được:

| Metric | Target |
|---|---:|
| Exact duplicate rate | báo cáo rõ, không cần target cứng |
| Near-duplicate cluster leakage | 0 giữa train/val/test |
| Wrapper detection coverage | > 90% có quyết định rõ hoặc unknown có lý do |
| Delex collision rate | < 10% cho high-confidence subset về sau |
| Top-10 delex coverage | < 10% |
| Empty/invalid payload rate | được report riêng |

---

# 6. File/folder output đề xuất

```text
data/
├── raw_shards/
│   ├── shard_00.csv
│   ├── shard_01.csv
│   └── ...
├── processed/
│   ├── phase1_payload_foundation.parquet
│   ├── exact_dedup_map.parquet
│   ├── near_dup_clusters.parquet
│   └── phase1_quality_report.json
└── reports/
    └── phase1_data_foundation_report.md
```

---

# 7. Checklist triển khai Phase 1

- [ ] Đọc được 16 CSV shard bằng chunk.
- [ ] Validate tồn tại cột `payload_norm`.
- [ ] Tạo `payload_raw`, không overwrite.
- [ ] Normalize unicode/whitespace/null.
- [ ] Decode URL/HTML an toàn.
- [ ] Exact dedup bằng SHA-256.
- [ ] Canonicalize.
- [ ] Near-dedup bằng SimHash/MinHash.
- [ ] Detect/strip wrapper trước delex.
- [ ] Delex v2 giữ function whitelist.
- [ ] Sinh report duplicate/collision/top-k.
- [ ] Không split train/val/test trước khi near-dedup.

---

# 8. Kết luận Phase 1

Phase 1 không tạo model. Phase 1 tạo nền dữ liệu đáng tin.

Câu hỏi kết thúc Phase 1:

```text
Từ 14.47M dòng payload_norm, ta còn bao nhiêu payload unique, canonical unique,
near-duplicate cluster, wrapper type, và delex pattern hợp lệ?
```

Nếu chưa trả lời được câu đó, chưa nên label lại và chưa nên train GAN.
