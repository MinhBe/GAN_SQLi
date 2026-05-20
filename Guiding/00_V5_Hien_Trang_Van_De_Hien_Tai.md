# V5 Rebuild — Hiện Trạng & Vấn Đề Hiện Tại

> Mục tiêu: tái kiến trúc lại mô hình SQL Injection GAN từ đầu.  
> Giả định khởi điểm: chỉ còn **16 file CSV shard**, mỗi file `<100 MB`, có đúng **1 cột `payload_norm`**.  
> Không giả định còn gold/silver/bronze, label cũ, tokenizer cũ, checkpoint cũ, hay evaluator cũ.

---

## 1. Tài sản hiện có

### 1.1. Nguồn dữ liệu raw

| # | Source | File(s) | Rows | Status |
|---|---|---|---:|---|
| 1 | RbSQLi | `rbsqli_dataset.csv` | 10,190,450 | OK |
| 2 | Zenodo | `zenodo_dataset.csv` | 3,688,977 | OK |
| 3 | Github HTTP Params | `github_http_params/` | 61,312 | OK |
| 4 | Github Yogsec | `github_yogsec_payloads/` | 3,640 | OK |
| 5 | Github Payloadbox | `github_payloadbox/` | 165 | OK |
| 6 | PayloadsAllTheThings | `github_payloadsallthethings/` | 1,581 | OK |
| 7 | Github FuzzDB | `github_fuzzdb/` | 664 | OK |
| 8 | BCCC-SFU | `bccc_sfu/` | 11,011 | OK |
| 9 | Gist johntroony | `gist_johntroony/` | 624 | OK |
| 10 | Github ajinmathew | `github_ajinmathew/` | 12,580 | OK |
| 11 | Github sqliv5 | `github_sqliv5/` | 149,748 | OK |
| 12 | CSIC-ECML | `github_csic_ecml_combined/` | 32,162 | OK |
| 13 | Kaggle sources | `kaggle/` | 132,776 | OK |
| 14 | Benign complex | `spider/ + huggingface/` | 192,462 | OK |
| 15 | Auto-discover | catch-all | 0 | SKIP |
| **Total** | | | **14,478,152** | |

### 1.2. Trạng thái dữ liệu thật sự

Hiện tại, sau khi gom lại, dữ liệu chỉ còn:

```text
payload_norm
```

Tức là chưa có:

- `is_sqli`
- `technique_primary`
- `intent_secondary`
- `db_engine`
- `confidence_score`
- `source`
- `syntax_validity`
- `dedup_hash`
- `canonical_payload`
- `payload_delex`
- `review_priority`

Vì vậy, V5 phải được xem là **rebuild full pipeline**, không phải fine-tune tiếp từ V3/V4.

---

## 2. Vấn đề hiện tại

## 2.1. Vấn đề 1 — Raw size lớn nhưng chưa chắc usable

Bạn có 14.47M rows, đây là lợi thế rất lớn. Nhưng raw size không đồng nghĩa với training quality.

Các nguồn payload SQLi công khai thường có:

- nhiều dòng trùng hệt nhau;
- nhiều near-duplicate chỉ khác encoding, whitespace, case;
- payload fragment chưa hoàn chỉnh;
- payload bị wrapper bởi query HTTP hoặc SQL context;
- payload không phải SQLi nhưng nằm lẫn trong source;
- payload benign nhưng giống attack;
- payload attack nhưng không biết engine cụ thể.

Nếu đưa thẳng vào training, GAN sẽ học:

```text
duplicate bias
+ label noise
+ syntax noise
+ source bias
+ mode phổ biến nhất
```

Kết quả thường gặp là:

```text
val metric đẹp
nhưng generation bị lặp pattern đơn giản
và collapse nhanh trong adversarial phase
```

---

## 2.2. Vấn đề 2 — Không còn source metadata sau khi chỉ giữ `payload_norm`

Khi chỉ còn 1 cột `payload_norm`, ta mất các thông tin rất quan trọng:

| Metadata mất | Tại sao quan trọng |
|---|---|
| Source gốc | Một số source thiên về SQLi, một số source thiên benign |
| Injection type gốc | RbSQLi/Zenodo có thể có nhãn hoặc implicit pattern |
| Tamper method | Có thể dùng để học obfuscation/bypass |
| HTTP context | Payload là query param, path, body, hay SQL fragment |
| Benign/attack source | Dễ phân biệt hơn nếu còn nguồn |

Vì vậy, V5 không được giả định source label còn tồn tại. Tất cả nhãn phải được tái tạo bằng pipeline mới.

---

## 2.3. Vấn đề 3 — Duplicate và near-duplicate có thể thống trị dataset

Ví dụ cùng một payload có thể xuất hiện trong nhiều source:

```sql
' OR '1'='1' --
```

Nếu không dedup trước khi label và train:

```text
payload phổ biến bị overweight
→ model tưởng đây là pattern quan trọng
→ MLE perplexity đẹp giả
→ generator học vài mẫu kinh điển
→ WAF/IDS dễ nhận diện
→ adversarial phase collapse nhanh
```

Trong V5, dedup không phải bước phụ. Đây là bước nền tảng.

---

## 2.4. Vấn đề 4 — Wrapper có thể làm mất attack pattern

Nhiều dòng raw không phải payload thuần mà là SQL/HTTP wrapper chứa payload bên trong.

Ví dụ:

```sql
SELECT * FROM users WHERE username = 'admin' OR '1'='1' --'
```

Nếu chạy delex trước khi strip wrapper:

```text
OR '1'='1' bị nuốt vào string placeholder
→ boolean_blind, union_based, error_based có thể thành cùng một delex pattern
→ collision tăng
→ conditional generator không học được type-specific structure
```

Thứ tự xử lý bắt buộc:

```text
normalize/decode
→ strip wrapper
→ classify context
→ delex_v2
→ canonicalize
```

---

## 2.5. Vấn đề 5 — Taxonomy label cũ trộn technique và intent

Các nhãn như:

```text
boolean_blind
time_blind
union_based
error_based
metadata_enumeration
db_fingerprint
stacked_queries
out_of_band
```

không cùng một tầng khái niệm.

| Nhãn | Bản chất |
|---|---|
| `boolean_blind`, `time_blind`, `union_based`, `error_based`, `stacked_queries`, `out_of_band` | Technique |
| `metadata_enumeration`, `db_fingerprint` | Intent / behavior |

Nếu để tất cả trong `primary_sqli_type`, model sẽ học điều kiện bị nhiễu. Ví dụ, `metadata_enumeration` có thể được thực hiện bằng `union_based`, `error_based`, hoặc `boolean_blind`.

V5 cần tách:

```text
technique_primary
intent_secondary
```

---

## 2.6. Vấn đề 6 — `db_engine = unknown` không phải một engine thật

Trong bản label thử trước đó, `unknown` chiếm phần lớn. Nếu vẫn train conditional generator với `db_engine=unknown` như một class ngang hàng, model sẽ học một loại SQL lai:

```text
MySQL function
+ Oracle syntax
+ MSSQL delay keyword
+ SQLite permissive behavior
```

Kết quả là payload có thể qua evaluator giả nhưng không hợp lệ trên DB thật.

V5 phải xử lý `unknown` như:

```text
unknown = chưa đủ bằng chứng
```

Không phải:

```text
unknown = một engine category để generate
```

---

## 2.7. Vấn đề 7 — REINFORCE gây collapse có tính cấu trúc

Kết quả V1–V4 cho thấy adversarial phase bị collapse lặp lại.

Cơ chế:

```text
Generator tìm được vài payload reward cao
→ reward các sample trở nên gần nhau
→ advantage ≈ 0
→ gradient từ REINFORCE gần biến mất
→ generator freeze vào vài mode
→ uniqueness giảm mạnh
```

Entropy regularization ở V3 giúp trì hoãn collapse, nhưng không loại bỏ gốc rễ.

V5 cần thay gradient estimator:

```text
REINFORCE
→ Gumbel-Softmax Straight-Through
```

---

## 2.8. Vấn đề 8 — Composite score dễ bị reward hacking

Nếu WAF bypass được đặt trọng số cao, collapsed model có thể sinh 1–2 payload quá đơn giản, không match signature WAF, nên bypass cao nhưng diversity gần như bằng 0.

Do đó:

```text
WAF bypass cao
≠ model tốt
```

Metric V5 cần có điều kiện chặn:

```text
Nếu uniqueness thấp hoặc AST entropy thấp
→ không được xem là checkpoint tốt
dù WAF bypass cao
```

---

# 3. Hướng xử lý tổng quan

V5 nên chia thành 4 phase:

| Phase | Mục tiêu | Output chính |
|---|---|---|
| Phase 1 | Rebuild data foundation | clean/canonical/dedup/delex dataset |
| Phase 2 | Rebuild labeler | labeled dataset với confidence + taxonomy mới |
| Phase 3 | Tách bài toán model | label quality model, classifier/evaluator, generator |
| Phase 4 | Train Conditional Gumbel-SeqGAN | generator ổn định, có diversity và condition consistency |

---

# 4. Nguyên tắc kiến trúc V5

## 4.1. Không để GAN sửa dữ liệu bẩn

GAN chỉ học distribution. Nếu distribution bẩn, GAN sẽ học bẩn.

Vì vậy:

```text
data quality trước
label quality sau
classifier/evaluator sau nữa
GAN cuối cùng
```

## 4.2. Không dùng một model cho mọi nhiệm vụ

Tách rõ:

```text
labeling
classification
generation
evaluation
```

## 4.3. Không đánh giá bằng một metric duy nhất

Checkpoint chỉ được xem là tốt nếu đồng thời đạt:

```text
db validity
+ type accuracy
+ db consistency
+ AST diversity
+ uniqueness
+ novelty
+ WAF/IDS robustness
```

## 4.4. Không train trên `unknown` như một class engine thật

`unknown` dùng để:

- giữ lại dữ liệu generic;
- huấn luyện binary/type model;
- không dùng cho engine-specific generator nếu chưa đủ bằng chứng.

---

# 5. Output kỳ vọng sau rebuild

Sau V5, bộ dữ liệu nên có schema tối thiểu:

```csv
payload_raw,
payload_norm,
payload_canonical,
payload_delex,
is_sqli,
technique_primary,
intent_secondary,
db_engine,
syntax_validity,
confidence_score,
confidence_band,
label_sources,
review_priority,
dedup_hash,
near_dup_cluster_id,
split
```

Và model pipeline nên có:

```text
Data pipeline
→ Labeling pipeline
→ Label quality model
→ SQLi type/db classifier
→ Conditional Gumbel-SeqGAN
→ Evaluation suite
```

---

# 6. Kết luận file hiện trạng

V5 không nên bắt đầu bằng câu hỏi:

```text
Train GAN thế nào?
```

Mà nên bắt đầu bằng câu hỏi:

```text
Làm sao biến 14.47M payload_norm thành một tập dữ liệu có thể tin được?
```

Sau đó mới train GAN.

Công thức tái kiến trúc:

```text
Raw payload_norm shards
→ normalize
→ dedup
→ strip wrapper
→ delex_v2
→ relabel
→ confidence calibration
→ split clean train/val/test
→ train evaluator models
→ train Conditional Gumbel-SeqGAN
```
