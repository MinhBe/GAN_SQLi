# 01 — Data Reality Check

> Mục tiêu: kiểm tra thực tế dữ liệu hiện có trước khi xử lý, vì dataset hiện tại chỉ còn `payload_norm` và có thể đang lẫn nhiều trạng thái: raw-like, normalized-like, delexed-like, mixed-state và malformed.

---

## 1. Vấn đề cần giải quyết

Tài sản đầu vào hiện tại là 16 file CSV:

```text
Asset/LabelData/FinalDataSet/final_dataset_*.csv
```

Mỗi file chỉ có một cột:

```csv
payload_norm
```

Không còn chắc chắn có:

```text
payload_raw
source
label
db_engine
technique
literal gốc
HTTP/SQL context ban đầu
```

Dataset có thể lẫn nhiều dạng:

```text
pg_sleep(5)
pg_sleep(__TIME__)
SELECT * FROM users WHERE id > 1 AND pg_sleep(5)--
__STR__ OR __STR__ = __STR__
```

Nếu xử lý toàn bộ như raw payload, pipeline sẽ sai từ đầu.

---

## 2. Tính chất của phase này

| Tính chất | Diễn giải |
|---|---|
| Diagnostic | Đo thực trạng dữ liệu |
| Non-destructive | Không overwrite `payload_norm` |
| Lane-based | Phân luồng xử lý theo trạng thái payload |
| Evidence-first | Quyết định xử lý dựa trên thống kê và mẫu kiểm tay |
| Risk-control | Ngăn lỗi giả định sai đầu vào lan sang các phase sau |

Phase này **không gán nhãn SQLi chính thức** và **không train model**.

---

## 3. Phân loại lane

| Lane | Tên | Mô tả | Cách dùng |
|---|---|---|---|
| N | normalized-like | Payload đã normalize, còn literal thật | Lane chính cho delex/relex/WAF/DB |
| R | raw-like / encoded-like | Payload còn encoding như `%27`, `&#x27;` | Decode an toàn rồi đưa về Lane N |
| D | delexed-like | Payload đã có placeholder, literal đã mất | Dùng phụ cho structure/type, không tin WAF/DB |
| X | mixed-state | Vừa có placeholder vừa có literal thật | Xử lý thận trọng, mặc định như Lane D |
| M | malformed | Rỗng, hỏng, binary junk, không thể xử lý | Cách ly, không train |

---

## 4. Định nghĩa lane cụ thể

### 4.1. Lane N — normalized-like

Điều kiện gợi ý:

```text
không có placeholder dạng __X__
có SQL keyword/operator/function rõ
literal còn nguyên như '1', 5, users, id
không có encoding artifact nổi bật
```

Ví dụ:

```sql
1 AND pg_sleep(5)--
' OR '1'='1' --
1 UNION SELECT 1,2,version()--
```

### 4.2. Lane R — raw-like / encoded-like

Điều kiện gợi ý:

```text
có URL encoding: %27, %20, %2f
có HTML entity: &#x27;, &quot;
có dấu + thay space
```

Ví dụ:

```text
%27%20OR%20%271%27%3D%271%27--
id=1%27%20UNION%20SELECT%201,2--
```

### 4.3. Lane D — delexed-like

Điều kiện gợi ý:

```text
có placeholder dạng __STR__, __NUM__, __TIME__, __ID__, __TABLE__
không còn literal thật đáng tin
```

Ví dụ:

```text
__STR__ OR __STR__ = __STR__ __COMMENT__
pg_sleep(__TIME__)
```

### 4.4. Lane X — mixed-state

Điều kiện gợi ý:

```text
có đồng thời placeholder và literal thật cùng payload
```

Ví dụ:

```text
id=1 AND pg_sleep(__TIME__) AND name='admin'
__STR__ OR user='admin'
```

Route an toàn:

```text
coi như Lane D cho WAF/DB
chỉ dùng cho structure/type nếu pattern còn rõ
```

### 4.5. Lane M — malformed

Điều kiện gợi ý:

```text
empty/null
quá ngắn không có nghĩa
binary/non-printable junk
không phải text xử lý được
```

---

## 5. Cách thực hiện

### 5.1. Đọc dữ liệu

Đọc 16 file theo chunk:

```python
import pandas as pd

for path in shard_paths:
    for chunk in pd.read_csv(path, chunksize=200_000):
        process(chunk["payload_norm"])
```

Không load toàn bộ vào memory nếu không cần.

### 5.2. Tạo feature kiểm tra

Với mỗi payload, tính:

```text
length
num_tokens
has_placeholder
placeholder_types
has_sql_keyword
has_sql_comment
has_quote
has_semicolon
has_url_encoding
has_html_entity
has_known_function
has_non_printable
has_literal_number
has_literal_string
```

### 5.3. Rule phân lane

Pseudo-rule:

```text
if empty/non-printable/invalid:
    lane = M

elif has_placeholder and has_literal_signal:
    lane = X

elif has_placeholder:
    lane = D

elif has_encoding_artifact:
    lane = R

else:
    lane = N
```

Kèm theo:

```text
lane_confidence
lane_reason
```

Không chỉ lưu kết quả, phải lưu lý do.

---

## 6. Phương pháp kiểm chứng

### 6.1. Audit mẫu kiểm tay

Không chỉ random 100 dòng. Nên lấy stratified audit:

| Nhóm | Số mẫu |
|---|---:|
| Random toàn dataset | 100 |
| Có placeholder | 100 |
| Có SQL keyword | 100 |
| Có function sleep/pg_sleep/waitfor/extractvalue | 100 |
| Có encoding artifact | 100 |
| Dòng rất ngắn | 100 |
| Dòng rất dài | 100 |
| Lane X | 100 nếu đủ |

Output:

```text
reports/01_audit_samples.csv
```

### 6.2. Đánh giá độ đúng của lane

Kiểm tay các mẫu audit và tính:

```text
lane_precision
state_detection_error_rate
mixed_state_false_negative
malformed_false_negative
```

---

## 7. Kết quả đầu ra

File chính:

```text
data/phase01/phase01_data_reality.parquet
```

Schema đề xuất:

```csv
row_id,
source_file,
source_row_index,
payload_input,
payload_length,
lane,
lane_confidence,
lane_reason,
payload_state,
has_placeholder,
placeholder_types,
has_sql_keyword,
has_known_function,
has_encoding_artifact,
has_literal_string,
has_literal_number,
recoverability_score,
relex_potential,
db_eval_potential
```

Report:

```text
reports/01_data_reality_check.md
reports/01_audit_samples.csv
reports/01_lane_distribution.json
```

---

## 8. Cách evaluate phase này

Phase này pass nếu:

| Tiêu chí | Điều kiện |
|---|---|
| Đọc đủ 16 shard | Không lỗi schema |
| Có phân phối lane | Báo cáo rõ N/R/D/X/M |
| Có audit mẫu | Có file audit stratified |
| Lane precision | Được kiểm tay và report |
| Lane X rõ ràng | Có định nghĩa và ví dụ |
| Không overwrite input | `payload_norm` được giữ nguyên |
| Soft-signal không hard gate | `recoverability_score` không dùng để drop hàng loạt |

---

## 9. Lưu ý quan trọng

Các score như:

```text
recoverability_score
relex_potential
db_eval_potential
```

chỉ là heuristic. Không dùng làm hard gate trước khi validate bằng audit.

---

## 10. Kết luận

Phase này trả lời câu hỏi:

```text
Dữ liệu hiện tại thật sự đang ở trạng thái nào?
Bao nhiêu dòng còn literal?
Bao nhiêu dòng đã delex?
Bao nhiêu dòng mixed?
Bao nhiêu dòng có thể dùng cho WAF/DB sau này?
```

Nếu chưa trả lời được, không nên đi tiếp.
