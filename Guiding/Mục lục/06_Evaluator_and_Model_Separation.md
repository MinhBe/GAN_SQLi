# 06 — Evaluator & Model Separation

> Mục tiêu: tách rõ model dùng để kiểm soát nhãn, model dùng để đánh giá consistency, và evaluator dùng để đo chất lượng thật. Tránh để một classifier rule-trained trở thành “ground truth giả”.

---

## 1. Vấn đề cần giải quyết

Nếu chỉ có một model hoặc một labeler làm mọi việc:

```text
label
train
reward
evaluate
```

thì rất dễ Goodhart:

```text
model tối ưu proxy
proxy tăng
true quality giảm
```

Vì vậy cần tách:

```text
Model A — label quality
Model B — learned consistency evaluator
Verified dev/test — ground truth độc lập hơn
Evaluator suite — parser/DB/WAF/novelty/diversity
```

---

## 2. Tính chất của phase này

| Tính chất | Diễn giải |
|---|---|
| Separation of concerns | Mỗi model một vai trò |
| Proxy-aware | Biết Model B chỉ là proxy |
| Verified evaluation | Có dev/test độc lập |
| Goodhart-resistant | Theo dõi proxy-true gap |
| Relex-aware | DB/WAF đo trên payload literal |

---

## 3. Model A — Label Quality Model

### 3.1. Vai trò

Dự đoán label có đáng tin không.

Input:

```text
labeler scores
conflict flags
lane
cluster features
syntax signals
db signals
duplicate count
```

Output:

```text
label_quality_score
needs_review
prob_label_correct
```

### 3.2. Kiến trúc đề xuất

```text
LightGBM / XGBoost
```

Lý do:

```text
tabular-friendly
dễ explain
nhanh
phù hợp feature từ labeler
```

### 3.3. Evaluate

```text
calibration curve
ECE
review precision
error analysis theo lane/technique
```

---

## 4. Model B — Learned Consistency Evaluator

### 4.1. Vai trò đúng

Không gọi Model B là independent ground truth.

Vai trò đúng:

```text
learned consistency evaluator
type/db/syntax assistant
train-time regularizer cho generator
fast evaluator
```

### 4.2. Kiến trúc

Multi-task classifier:

```text
Backbone:
  token embedding + BiLSTM/Transformer

Heads:
  is_sqli
  technique_primary
  intent_secondary
  db_engine/db_family
  syntax_validity
```

### 4.3. Soft-token compatibility

Model B phải nhận được:

```text
hard token ids
soft token distribution
```

Soft input:

```python
soft_emb = soft_tokens @ embedding_matrix
```

Điều này cần cho consistency loss của Gumbel-SeqGAN.

### 4.4. Abstain output

Model B nên có:

```text
unknown
abstain
low confidence
```

Không ép mọi payload vào class cụ thể.

---

## 5. Verified dev/test sets

### 5.1. Vì sao cần

Model B train từ weak labels nên không độc lập.

Cần set verified để đo true quality.

### 5.2. Chia làm hai

```text
verified_dev:
  dùng để early stop, phát hiện Goodhart

verified_test:
  chỉ dùng báo cáo cuối
```

Không tune quá nhiều trên verified_test.

### 5.3. Nguồn verified label

Kết hợp:

```text
human review
LLM-assisted review với schema chặt
DB execution evidence
parser/AST evidence
curated known payloads
```

DB execution không phải oracle tuyệt đối, vì nhiều SQLi là fragment/context-dependent.

---

## 6. Evaluator suite

### 6.1. Parser / AST evaluator

Đo:

```text
syntax validity
AST structure
AST entropy
parse error type
```

### 6.2. DB sandbox evaluator

Đo trên payload literal sau relex.

Theo engine nếu có:

```text
mysql
postgresql
mssql
sqlite
oracle nếu có môi trường
```

Nếu không có context đầy đủ, phân biệt:

```text
valid query
valid fragment
context-dependent
```

### 6.3. Novelty evaluator

Đo:

```text
exact copy rate
near-copy similarity
nearest training neighbor
cluster novelty
```

### 6.4. Diversity evaluator

Đo:

```text
unique ratio
self-BLEU
template entropy
AST entropy
top-k coverage relative to train
```

### 6.5. WAF evaluator

Chỉ dùng nếu relex đủ tốt.

Đo:

```text
WAF pass/bypass
rule triggered
payload category
```

Không dùng WAF score một mình.

---

## 7. Goodhart / reward overoptimization control

Nếu Model B hoặc evaluator learned được dùng làm loss/reward, phải monitor:

```text
proxy_score
verified_dev_score
proxy_true_gap
```

Nếu:

```text
proxy tăng
verified_dev giảm
```

thì dừng hoặc giảm weight proxy.

---

## 8. Kết quả đầu ra

```text
models/phase06/label_quality_model.pkl
models/phase06/consistency_classifier.pt
data/phase06/verified_dev.parquet
data/phase06/verified_test.parquet
eval/phase06/classifier_eval.json
reports/06_model_separation_report.md
```

---

## 9. Cách evaluate phase này

| Thành phần | Evaluate |
|---|---|
| Model A | calibration, review precision |
| Model B | F1 trên verified_dev/test, không chỉ weak labels |
| Evaluator | consistency across lanes |
| Verified set | frozen, versioned, provenance rõ |
| Goodhart control | proxy_true_gap monitoring |

---

## 10. Kết luận

Model B không phải ground truth. Nó là công cụ hỗ trợ. Ground truth phải đến từ verified dev/test và evaluator suite đa nguồn.
