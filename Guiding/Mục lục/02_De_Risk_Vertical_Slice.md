# 02 — De-risk Vertical Slice

> Mục tiêu: xây một lát cắt end-to-end nhỏ nhưng đủ thật để kiểm tra sớm kiến trúc generation, tránh đầu tư full-scale rồi mới phát hiện GAN vẫn collapse hoặc không hơn MLE.

---

## 1. Vấn đề cần giải quyết

Trong các version trước, lỗi lớn xuất hiện ở adversarial training:

```text
mode collapse
condition ignore
reward hacking
WAF score cao nhưng diversity thấp
```

Nếu làm full data foundation + full label system + full evaluator rồi mới train GAN, rủi ro phát hiện quá muộn.

Phase này tạo một vertical slice:

```text
sample nhỏ nhưng có kiểm soát
→ xử lý dữ liệu tối thiểu
→ label tối thiểu
→ train MLE baseline
→ train mini Gumbel-SeqGAN challenger
→ so sánh bằng protocol nghiêm túc
```

---

## 2. Tính chất của phase này

| Tính chất | Diễn giải |
|---|---|
| End-to-end | Có đủ data → label → model → eval |
| Small but realistic | 30k–50k dòng, không phải toy data |
| De-risk | Phát hiện lỗi kiến trúc sớm |
| Baseline-first | MLE là baseline chính thức |
| Kill-capable | Có quyền dừng hướng GAN nếu không đạt |

---

## 3. Input

Từ phase 01:

```text
data/phase01/phase01_data_reality.parquet
```

Ưu tiên sample:

```text
Lane N: chính
Lane R: decode được rồi đưa về N
Lane D/X: lấy một phần nhỏ để kiểm robustness
Lane M: không dùng train
```

---

## 4. Sampling strategy

Không random thuần.

Sample theo bucket:

```text
lane
length bucket
SQL keyword presence
known function family
placeholder state
comment marker
quote pattern
possible technique
possible db signal
benign-like / attack-like
```

Mục tiêu:

```text
30k–50k rows
coverage tốt
không bị thống trị bởi 1–2 pattern phổ biến
```

---

## 5. Xử lý dữ liệu tối thiểu

Trong slice, làm tối thiểu nhưng không cẩu thả:

```text
exact dedup
basic decode cho Lane R
basic wrapper detection cho Lane N/R
basic delex_v5 cho Lane N/R
Lane D giữ delex input
Lane X xử lý như Lane D nếu không recover được
```

Output tạm:

```text
data/phase02/slice_payloads.parquet
```

Schema:

```csv
slice_id,
row_id,
payload_input,
lane,
payload_working,
payload_delex,
dedup_hash,
basic_cluster_key
```

---

## 6. Labeler tối giản

Labeler tối giản không cần full taxonomy, nhưng phải đủ để condition và eval.

Nhãn tối thiểu:

```text
is_sqli
technique_primary
db_hint
syntax_validity
confidence_basic
```

Technique ban đầu:

```text
benign
boolean_blind
time_blind
union_based
error_based
generic_sqli
unknown
```

Rare classes như `stacked_queries`, `out_of_band`, `metadata_enumeration`, `db_fingerprint` có thể đưa vào `generic_sqli` hoặc `intent_hint`.

---

## 7. Relex tối thiểu nhưng phải nghiêm túc

Nếu phase này muốn đo WAF/DB, relex không được fill hằng số đơn giản.

Cần literal pools tối thiểu:

```text
STR_POOL
NUM_POOL
TIME_POOL
COMMENT_POOL
ID_POOL
TABLE_POOL
```

Và context-aware fill:

```text
__TIME__ + pg_sleep      → 5
__TIME__ + sleep         → 5
__TIME__ + waitfor delay → '0:0:5'
__STR__ + tautology      → '1'
__NUM__ + union select   → 1, 2, 3
```

Nếu chưa làm được relex nghiêm túc:

```text
không tin WAF/IDS metric trong phase này
chỉ tin syntax/type/diversity/collapse metric
```

---

## 8. MLE baseline

### 8.1. Mục tiêu

MLE không phải warmup phụ. MLE là đối thủ chính thức.

### 8.2. Kiến trúc

```text
Conditional autoregressive generator
condition = technique_primary
output = payload_delex tokens
```

Có thể dùng:

```text
LSTM decoder
hoặc small Transformer decoder
```

### 8.3. Sampling sweep

Phải quét:

```text
temperature
top-k
top-p / nucleus
repetition penalty
max length
```

Output là MLE quality-diversity frontier.

---

## 9. Mini Gumbel-SeqGAN challenger

### 9.1. Generator

```text
ConditionalGumbelGenerator
condition = technique_primary
tau schedule thử nghiệm
soft token path
hard token path
```

### 9.2. Discriminator

Không dùng real one-hot vs fake soft trực tiếp.

Dùng embedding-compatible representation:

```python
real_emb = embedding(real_ids)
fake_emb = fake_soft @ embedding_matrix
```

Discriminator nhận:

```text
[B, T, E]
```

### 9.3. Consistency loss

Không dùng:

```text
fake_hard → relex → classifier → CE
```

Dùng:

```text
fake_soft → soft embedding → classifier → CE
```

---

## 10. Experiment protocol

Trước khi chạy, tạo:

```text
reports/02_experiment_protocol.md
```

Nội dung phải khóa trước:

```text
primary metrics
secondary metrics
random seeds
MLE sampling grid
GAN configs được phép thử
Decision Gate
vùng quality-diversity cần so
số bước train tối đa
early-stop rules
```

Không chạy xong rồi mới chọn metric.

---

## 11. Số seed

Tối thiểu:

```text
3 seeds cho MLE
3 seeds cho Gumbel-SeqGAN
```

Report:

```text
mean
std
confidence interval hoặc bootstrap interval
best seed
worst seed
```

Không dùng best run làm kết luận.

---

## 12. Metrics

### 12.1. Collapse metrics

```text
unique_ratio
self-BLEU-3
token_entropy
top-k generated coverage
copy rate
```

### 12.2. Quality metrics

```text
syntax_validity
type_accuracy
delex validity
relex round-trip nếu có
DB execution nếu relex đủ tốt
```

### 12.3. Diagnostic metrics

```text
D_score
D shortcut diagnostic
gradient norm
tau curve
proxy-true gap
```

---

## 13. D shortcut diagnostic

Test bắt buộc:

```text
D(real_onehot/embedding)
D(real_softened)
D(real_with_noise)
```

Nếu nội dung không đổi nhưng D score lệch mạnh chỉ vì representation bị làm mềm, D đang học shortcut.

Metrics:

```text
delta_D_real_softened
corr(D_score, token_entropy)
corr(D_score, max_token_probability)
```

---

## 14. Kết quả đầu ra

```text
data/phase02/slice_payloads.parquet
models/phase02/mle_baseline/
models/phase02/gumbel_seqgan/
eval/phase02/mle_frontier.json
eval/phase02/gan_results.json
reports/02_experiment_protocol.md
reports/02_slice_eval_report.md
```

---

## 15. Cách evaluate phase này

Phase này không nhằm chứng minh GAN là tối ưu cuối cùng. Nó nhằm trả lời:

```text
GAN có collapse không?
GAN có học shortcut không?
GAN có đáng để scale tiếp không?
MLE baseline mạnh đến đâu?
```

Phase này pass nếu có đủ bằng chứng cho Decision Gate ở phase kế tiếp.
