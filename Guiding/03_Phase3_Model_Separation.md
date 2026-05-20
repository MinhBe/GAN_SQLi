# Phase 3 — Tách Bài Toán Model

> Mục tiêu: không dùng một GAN để làm tất cả. Tách rõ model dùng để đánh giá nhãn, model dùng để phân loại SQLi, và model dùng để sinh payload.

---

## 1. Vấn đề hiện tại

Một lỗi tư duy phổ biến là:

```text
Có dataset lớn
→ train GAN
→ GAN sinh payload
→ dùng reward đánh giá
```

Nhưng với bài toán SQLi, GAN không nên là model đầu tiên.

Vì sao?

```text
GAN học distribution.
Nếu distribution bị nhiễu nhãn, duplicate, collision, engine conflict,
GAN sẽ khuếch đại lỗi đó.
```

Do đó Phase 3 tách thành nhiều model nhỏ, mỗi model giải quyết một nhiệm vụ cụ thể.

---

# 2. Hướng xử lý tổng quan

Phase 3 gồm 3 nhóm model chính:

| Model | Tên đề xuất | Vai trò |
|---|---|---|
| Model A | Label Quality / Confidence Model | Hiệu chỉnh confidence và phát hiện label noise |
| Model B | SQLi Type & DB Classifier | Đánh giá payload thuộc type/db nào |
| Model C | Conditional Gumbel-SeqGAN | Sinh payload SQLi theo condition |
| Evaluator suite | Parser/DB/WAF/IDS/Novelty | Không hẳn là model duy nhất, nhưng là bộ kiểm thử |

---

# 3. Model A — Label Quality / Confidence Model

## 3.1. Model này là gì?

Model A không sinh payload. Nó học xác suất rằng label hiện tại đáng tin.

Input:

```text
payload_core
payload_delex
labeler features
technique_votes
db_engine_votes
syntax_validity
cluster features
```

Output:

```text
label_quality_score
prob_label_correct
needs_review
```

## 3.2. Tại sao cần?

Rule/heuristic labeler dễ tạo false confidence. Đặc biệt khi nhiều rule cùng dựa trên keyword matching, chúng không thật sự độc lập.

Model A giúp:

```text
phát hiện label conflict
calibrate confidence
chọn review queue
lọc gold/silver
giảm noise trước khi train GAN
```

## 3.3. Kiến trúc đề xuất

### Option đơn giản

```text
Gradient Boosting / XGBoost / LightGBM
```

Input là feature dạng bảng:

```text
keyword scores
technique scores
db scores
syntax flags
cluster size
duplicate count
collision count
```

Ưu điểm:

- nhanh;
- dễ giải thích;
- phù hợp dữ liệu tabular;
- dùng được trước khi có tokenizer neural tốt.

### Option neural

```text
Small Transformer / BiLSTM classifier
```

Input là token sequence `payload_delex`.

Ưu điểm:

- bắt pattern dài;
- học obfuscation tốt hơn.

### Khuyến nghị

Bắt đầu bằng:

```text
LightGBM/XGBoost + feature-based
```

Sau khi có gold review đủ tốt, thêm neural model.

## 3.4. Cơ sở khoa học / lý do kiến trúc

Đây là hướng **weak supervision + confidence calibration**:

```text
nhiều labeling function yếu
→ gom vote
→ phát hiện conflict/correlation
→ hiệu chỉnh confidence
→ tạo training set sạch hơn
```

Tính chất kiến trúc:

| Tính chất | Lý do phù hợp |
|---|---|
| Supervised/weak-supervised | Có labeler outputs làm weak labels |
| Tabular-friendly | Nhiều feature không phải sequence |
| Explainable | Cần biết vì sao sample bị review |
| Noise-aware | Mục tiêu là lọc nhiễu, không generate |

---

# 4. Model B — SQLi Type & DB Classifier

## 4.1. Model này là gì?

Model B là classifier độc lập dùng để đánh giá payload.

Input:

```text
payload_core hoặc payload_delex
```

Output:

```text
is_sqli
technique_primary
intent_secondary
db_engine
syntax_validity
```

## 4.2. Tại sao cần?

Generator cần một “giám khảo” độc lập.

Nếu generator được yêu cầu sinh:

```text
technique_primary = union_based
db_engine = mysql
```

ta cần kiểm tra:

```text
payload sinh ra có thật sự union_based không?
có đúng MySQL không?
hay chỉ là boolean/time generic?
```

Nếu không có Model B, ta chỉ có WAF/DB/AST, nhưng các metric đó không đảm bảo condition consistency.

## 4.3. Kiến trúc đề xuất

### Multi-task classifier

Một backbone, nhiều head:

```text
Backbone:
  token embedding
  BiLSTM hoặc Transformer encoder

Heads:
  is_sqli head
  technique_primary head
  intent_secondary head
  db_engine head
  syntax_validity head
```

Loss:

```text
L = CE(is_sqli)
  + CE(technique_primary)
  + CE(intent_secondary)
  + CE(db_engine)
  + CE(syntax_validity)
```

Có thể đặt weight khác nhau:

```text
technique/db_engine weight cao hơn
intent weight thấp hơn nếu label nhiễu
```

## 4.4. Cơ sở khoa học / lý do kiến trúc

### Vì sao multi-task?

Các nhãn có liên hệ:

```text
time_blind thường liên quan db-specific sleep functions
error_based thường liên quan engine-specific error functions
metadata intent liên quan information_schema/sys/v$
```

Nếu train từng classifier rời rạc, model không tận dụng quan hệ này.

Multi-task giúp:

```text
shared SQL representation
+ regularization tự nhiên
+ giảm overfit từng label nhỏ
```

### Vì sao cần độc lập với Generator?

Nếu dùng chính discriminator để kết luận type/db, generator có thể học cách đánh lừa discriminator mà không thật sự đúng condition.

Do đó Model B là evaluator độc lập.

## 4.5. Output của Model B dùng ở đâu?

| Nơi dùng | Vai trò |
|---|---|
| Phase 2 | hỗ trợ relabel/confidence |
| Phase 4 training | type consistency loss, db consistency loss |
| Evaluation | đo type accuracy, db consistency |
| Review | phát hiện generated payload sai condition |

---

# 5. Model C — Conditional Gumbel-SeqGAN

## 5.1. Model này là gì?

Đây là generator chính của V5.

Input condition:

```text
technique_primary
db_engine
optional: intent_secondary
```

Output:

```text
payload_delex sequence
→ relex
→ payload SQLi candidate
```

## 5.2. Vì sao không dùng GAN cho labeling?

GAN không phù hợp làm labeler chính vì:

```text
GAN không học causal label
GAN học phân phối mẫu
GAN dễ collapse
GAN dễ reward hacking
```

GAN phù hợp hơn cho:

```text
synthetic payload generation
red-team dataset augmentation
WAF/IDS stress test trong lab
coverage expansion cho rare class
```

## 5.3. Cơ sở khoa học / lý do kiến trúc

Conditional GAN phù hợp khi cần sinh mẫu theo điều kiện:

```text
condition = class/type/db_engine
output = sequence payload
```

Gumbel-Softmax phù hợp vì output là discrete tokens nhưng cần gradient đi qua sampling.

WGAN-GP phù hợp vì discriminator quá mạnh dễ làm gradient vanish; gradient penalty giúp ổn định Lipschitz constraint.

Tính chất kiến trúc:

| Thành phần | Tính chất |
|---|---|
| Conditional generator | sinh có điều kiện, không chỉ random |
| Gumbel-Softmax STE | gradient đi qua discrete token approximation |
| WGAN-GP discriminator | ổn định adversarial training |
| Entropy regularization | chống collapse |
| Type/db consistency loss | ép generator không ignore condition |
| Novelty penalty | giảm memorization/duplicate |

---

# 6. Evaluator Suite

Evaluator không phải một model duy nhất. Nó là bộ kiểm thử.

## 6.1. Các evaluator cần có

| Evaluator | Vai trò |
|---|---|
| Parser/AST evaluator | Kiểm tra cấu trúc SQL |
| DB sandbox evaluator | Kiểm tra execute theo engine |
| Type classifier evaluator | Kiểm tra đúng technique |
| DB classifier evaluator | Kiểm tra đúng engine |
| Novelty evaluator | Kiểm tra không copy training |
| Diversity evaluator | Self-BLEU, uniqueness, AST entropy |
| WAF evaluator | Kiểm tra bypass trong môi trường lab |
| IDS evaluator | Kiểm tra evasion trong môi trường lab |

## 6.2. Nguyên tắc

Không dùng WAF score một mình.

Checkpoint chỉ pass nếu:

```text
uniqueness đủ cao
AST entropy đủ cao
type accuracy đủ cao
db consistency đủ cao
novelty đủ cao
```

---

# 7. Quan hệ giữa các model

```text
Phase 1 clean data
        ↓
Phase 2 weak labels
        ↓
Model A: label quality calibrator
        ↓
Gold/Silver dataset
        ↓
Model B: SQLi type/db classifier
        ↓
Evaluator độc lập
        ↓
Model C: Conditional Gumbel-SeqGAN
        ↓
Generated payloads
        ↓
Evaluator suite
```

---

# 8. Training order

Không train GAN trước.

Thứ tự đúng:

```text
1. Build Phase 1 data foundation
2. Build Phase 2 labeler
3. Train Model A label quality
4. Tạo gold/silver sạch
5. Train Model B classifier/evaluator
6. Freeze hoặc semi-freeze Model B
7. Train Conditional Gumbel-SeqGAN
8. Evaluate bằng evaluator suite
```

---

# 9. Output Phase 3

Folder đề xuất:

```text
models/
├── label_quality/
│   ├── train_label_quality.py
│   ├── label_quality_model.pkl
│   └── calibration_report.md
├── sql_classifier/
│   ├── train_multitask_classifier.py
│   ├── classifier_best.pt
│   └── classifier_eval_report.md
└── evaluators/
    ├── ast_eval.py
    ├── db_eval.py
    ├── novelty_eval.py
    ├── diversity_eval.py
    └── waf_eval.py
```

---

# 10. Quality gates Phase 3

| Model | Metric | Target |
|---|---|---:|
| Label Quality Model | calibration ECE | thấp, report rõ |
| Label Quality Model | review precision | cao trên queue review |
| SQLi classifier | is_sqli F1 | > 0.95 nếu gold đủ tốt |
| Technique classifier | macro F1 | > 0.75 ban đầu |
| DB classifier | macro F1 on known engines | > 0.75 ban đầu |
| Syntax classifier | macro F1 | > 0.80 |
| Evaluator | train/test cluster leakage | 0 |

---

# 11. Kết luận Phase 3

Phase 3 là bước biến bài toán từ:

```text
một GAN cố làm tất cả
```

thành:

```text
một hệ thống nhiều model:
  model kiểm soát nhãn
  model đánh giá type/db
  model sinh payload
  evaluator suite kiểm định
```

Đây là kiến trúc an toàn hơn, đo lường được hơn, và phù hợp hơn với bản chất AIOps.
