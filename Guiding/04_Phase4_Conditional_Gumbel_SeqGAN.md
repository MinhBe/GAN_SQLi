# Phase 4 — Conditional Gumbel-SeqGAN V5

> Mục tiêu: xây model generator chính cho V5 sau khi dữ liệu và nhãn đã sạch hơn.

---

## 1. Tóm tắt kiến trúc đầu tiên

### Generator

```text
ConditionalGumbelGenerator

Condition:
  technique_primary + db_engine

Core:
  condition embedding
  sequence decoder
  Gumbel-Softmax Straight-Through

Temperature:
  tau schedule 1.0 → 0.5
```

### Discriminator

```text
Conditional WGAN-GP

Input:
  real one-hot token sequence
  fake soft-token sequence

Output:
  Wasserstein score

Important:
  no sigmoid
```

### Loss

```text
adversarial loss
+ entropy regularization
+ type consistency loss
+ db consistency loss
+ novelty penalty
```

---

# 2. Vấn đề Phase 4 cần giải quyết

Các version cũ có 4 vấn đề chính:

| Vấn đề | Hậu quả |
|---|---|
| REINFORCE gradient sparse/high variance | collapse sau adversarial phase |
| Generator ignore condition | yêu cầu union_based nhưng sinh boolean/time |
| WAF reward hacking | bypass cao nhưng uniqueness thấp |
| DB syntax bị trộn | payload engine-specific sai |

V5 xử lý bằng:

```text
Gumbel-Softmax
+ conditional architecture
+ independent classifier loss
+ db consistency loss
+ novelty/diversity controls
+ WGAN-GP discriminator
```

---

# 3. Generator chi tiết

## 3.1. Input condition

Điều kiện tối thiểu:

```text
technique_primary
db_engine
```

Ví dụ condition:

```text
technique_primary = union_based
db_engine = mysql
```

Optional sau khi ổn định:

```text
intent_secondary
syntax_validity
length_bucket
obfuscation_level
```

Khuyến nghị V5 ban đầu:

```text
chỉ dùng technique_primary + db_engine
```

Đừng đưa quá nhiều condition từ đầu, vì label noise sẽ tăng.

---

## 3.2. Condition embedding

Mỗi condition được embed:

```text
technique_embedding = Embedding(num_techniques, d)
db_embedding        = Embedding(num_db_engines, d)
condition_vector    = concat(technique_embedding, db_embedding)
```

Condition vector dùng để:

```text
khởi tạo hidden state decoder
hoặc concat vào input mỗi decoding step
hoặc cả hai
```

Khuyến nghị:

```text
concat condition vào mỗi step
```

vì nếu chỉ dùng hidden state ban đầu, model dễ quên condition ở sequence dài.

---

## 3.3. Decoder

Decoder sinh token từng bước:

```text
BOS
→ token_1
→ token_2
→ ...
→ EOS
```

Input mỗi step:

```text
previous token embedding
+ condition embedding
```

Output mỗi step:

```text
logits over vocabulary
```

Vocabulary lấy từ delex_v2:

```text
SQL keywords
operators
preserved functions
placeholders:
  __STR__
  __NUM__
  __ID__
  __TABLE__
  __COMMENT__
```

---

## 3.4. Gumbel-Softmax

### Vấn đề cần giải

Token là discrete:

```python
token = argmax(logits)
```

`argmax` không có gradient.

### Giải pháp

Dùng Gumbel-Softmax:

```text
soft_token = softmax((logits + gumbel_noise) / tau)
```

Output:

```text
soft_token: distribution có gradient
hard_token: token rời rạc dùng cho next step/relex/eval
```

### Straight-Through

Forward:

```text
dùng hard token để mô phỏng generation thật
```

Backward:

```text
gradient đi qua soft token
```

Đây là điểm khác cốt lõi so với REINFORCE.

---

## 3.5. Tau schedule 1.0 → 0.5

### Ý nghĩa tau

| Tau | Hành vi |
|---:|---|
| Cao | output mềm hơn, explore nhiều hơn |
| Thấp | output gần one-hot hơn, giống discrete hơn |

### Schedule đề xuất

```text
tau_start = 1.0
tau_end   = 0.5
decay     = theo step hoặc epoch
```

Ví dụ:

```python
tau = max(0.5, 1.0 * exp(-decay_rate * step))
```

### Không nên để tau quá thấp sớm

Nếu tau xuống quá thấp:

```text
soft token gần one-hot
→ gradient kém mượt
→ dễ collapse trở lại
```

---

# 4. Discriminator chi tiết

## 4.1. Discriminator nhận gì?

Real sample:

```text
payload_delex real
→ one-hot sequence [B, T, V]
```

Fake sample:

```text
Generator output
→ soft-token sequence [B, T, V]
```

Cả hai có cùng shape.

---

## 4.2. Conditional WGAN-GP

Discriminator không trả probability.

Không dùng:

```text
sigmoid
binary cross entropy
```

Dùng:

```text
Wasserstein score
```

Loss D:

```text
L_D = D(fake) - D(real) + lambda_gp * gradient_penalty
```

Loss G adversarial:

```text
L_G_adv = -D(fake)
```

## 4.3. Vì sao no sigmoid?

WGAN không học xác suất real/fake. Nó học khoảng cách phân phối. Sigmoid sẽ ép score vào 0–1, làm mất tính chất Wasserstein và dễ gây gradient saturation.

---

## 4.4. Gradient penalty

Mục tiêu:

```text
giữ discriminator 1-Lipschitz
```

Cách làm:

```text
interpolate real/fake
tính gradient của D theo input
phạt nếu norm khác 1
```

Công thức:

```text
GP = (||∇D(interpolated)||2 - 1)^2
```

---

# 5. Loss function chi tiết

Tổng loss generator:

```text
L_G =
  L_adv
+ λ_entropy * L_entropy
+ λ_type * L_type_consistency
+ λ_db * L_db_consistency
+ λ_novelty * L_novelty
```

Lưu ý dấu:

```text
entropy và novelty có thể được viết dưới dạng reward hoặc penalty.
Cần thống nhất implementation để không ngược dấu.
```

---

## 5.1. Adversarial loss

```text
L_adv = -D(fake_soft, condition)
```

Mục tiêu:

```text
fake distribution giống real SQLi distribution cùng condition
```

---

## 5.2. Entropy regularization

Mục tiêu:

```text
chống mode collapse
khuyến khích phân phối token không quá tự tin sớm
```

Cách tính:

```text
H = -sum(p * log p)
```

Loss dạng reward:

```text
L_entropy = -H
```

Nếu entropy giảm quá nhanh, model đang collapse.

Monitor:

```text
token_entropy
unique/64
self_bleu
top-k generated coverage
```

---

## 5.3. Type consistency loss

Dùng Model B đã train ở Phase 3.

Quy trình:

```text
fake_hard tokens
→ relex/decode
→ classifier technique head
→ CE(predicted_technique, condition_technique)
```

Loss:

```text
L_type = CE(C_type(fake), technique_condition)
```

Mục tiêu:

```text
request union_based → sinh union_based
request time_blind → sinh time_blind
```

Không để generator ignore condition.

---

## 5.4. DB consistency loss

Dùng Model B hoặc DB rule detector.

Quy trình:

```text
fake_hard tokens
→ classifier db_engine head
→ CE(predicted_db, condition_db)
```

Loss:

```text
L_db = CE(C_db(fake), db_condition)
```

Mục tiêu:

```text
request mysql → không sinh oracle/mssql syntax
request postgresql → không sinh mysql-only function
```

Với `db_engine=unknown`:

```text
không dùng L_db engine-specific
hoặc loại khỏi conditional generator
```

---

## 5.5. Novelty penalty

Mục tiêu:

```text
không copy training set
không lặp lại 1-2 payload
```

Cách đo:

| Metric | Vai trò |
|---|---|
| exact match to train | cấm hoặc phạt mạnh |
| nearest neighbor similarity | phạt nếu quá gần |
| delex pattern frequency | phạt pattern quá phổ biến |
| cluster novelty | ưu tiên cluster mới |

Loss minh họa:

```text
L_novelty = max(0, similarity_to_train - threshold)
```

---

# 6. Training process từng bước

## 6.1. Step 0 — Chuẩn bị data

Input:

```text
gold + selected silver
```

Điều kiện:

```text
technique_primary != unknown
db_engine known hoặc generic_sql
syntax_validity acceptable
near_dup_cluster split sạch
```

Không dùng:

```text
malformed
non_sql
label conflict nặng
duplicate cluster leak
```

---

## 6.2. Step 1 — MLE warmup

Mục tiêu:

```text
học SQL syntax và token order trước khi adversarial
```

Loss:

```text
CrossEntropy(real next token)
+ entropy regularization nhẹ
```

Monitor:

```text
val_ppl
unique/64
syntax validity
teacher-forcing loss
```

Không dùng WAF ở step này.

---

## 6.3. Step 2 — Adversarial training

Mỗi vòng:

```text
1. sample real batch theo condition
2. generator sinh fake_soft, fake_hard
3. train discriminator n_critic lần
4. train generator một lần
```

D step:

```text
L_D = D(fake_soft) - D(real_onehot) + GP
```

G step:

```text
L_G = L_adv
    + entropy
    + type consistency
    + db consistency
    + novelty
```

Monitor bắt buộc:

```text
D_real_mean
D_fake_mean
gradient_penalty
G_loss
token_entropy
unique/64
type_accuracy
db_accuracy
novelty_score
```

---

## 6.4. Step 3 — Reward fine-tuning có kiểm soát

Chỉ sau khi adversarial ổn định.

Có thể thêm:

```text
WAF lab score
DB execution score
AST diversity score
IDS evasion score
```

Nhưng không để WAF dominate.

Khuyến nghị:

```text
WAF chỉ là một phần nhỏ của reward
hoặc dùng làm evaluation riêng
```

Nếu WAF bypass tăng nhưng uniqueness giảm:

```text
dừng checkpoint
không xem là best
```

---

# 7. Checkpoint selection

Không chọn checkpoint cuối mặc định.

Chọn checkpoint theo multi-metric gate:

| Metric | Điều kiện |
|---|---|
| uniqueness | không collapse |
| AST entropy | đủ cao |
| type accuracy | đạt target |
| db consistency | đạt target |
| novelty | không copy train |
| WAF/IDS | tốt nhưng không hy sinh diversity |
| DB execution | validate theo đúng engine |

Ví dụ rule:

```text
Reject checkpoint nếu:
  unique/500 < 0.70
  hoặc self_bleu quá cao
  hoặc type_accuracy < 0.70
  hoặc db_consistency < 0.70
```

---

# 8. Evaluation output

Mỗi checkpoint tạo:

```text
eval/results_v5/checkpoint_stepXXXX.json
eval/samples_v5/checkpoint_stepXXXX.csv
eval/reports_v5/checkpoint_stepXXXX.md
```

Report gồm:

```text
sample_count
condition distribution
type accuracy
db consistency
syntax validity
AST entropy
relex uniqueness
novelty to train
WAF score
IDS score
DB execution by engine
top repeated payloads
failure examples
```

---

# 9. Code structure đề xuất

```text
v5/
├── configs/
│   └── gumbel_seqgan.yaml
├── src/
│   ├── generator_gumbel.py
│   ├── discriminator_wgan_gp.py
│   ├── losses.py
│   ├── train_mle.py
│   ├── train_adversarial.py
│   ├── reward_controlled.py
│   └── checkpointing.py
├── eval/
│   ├── evaluate_checkpoint.py
│   ├── diversity.py
│   ├── novelty.py
│   ├── type_db_consistency.py
│   └── report.py
└── checkpoints/
    └── v5/
```

---

# 10. Config mẫu

```yaml
model:
  generator: ConditionalGumbelGenerator
  discriminator: ConditionalWGANDiscriminator
  vocab_size: 434
  embed_dim: 256
  hidden_dim: 512
  condition_dim: 64

condition:
  use_technique_primary: true
  use_db_engine: true
  use_intent_secondary: false

gumbel:
  tau_start: 1.0
  tau_end: 0.5
  tau_decay_steps: 12000

training:
  mle_steps: 2000
  adv_steps: 12000
  finetune_steps: 4000
  batch_size: 64
  n_critic: 5
  lambda_gp: 10.0

loss_weights:
  entropy: 0.05
  type_consistency: 0.20
  db_consistency: 0.15
  novelty: 0.10
  waf_reward: 0.05

early_stop:
  min_unique_ratio: 0.70
  min_type_accuracy: 0.70
  min_db_consistency: 0.70
  max_self_bleu_3: 0.85
```

---

# 11. Kết luận Phase 4

V5 không phải chỉ là:

```text
V3 + thêm entropy
```

Mà là:

```text
Conditional SeqGAN giữ framework cũ
nhưng thay gradient estimator bằng Gumbel-Softmax
thêm evaluator độc lập cho type/db
thêm novelty/diversity guard
và không để WAF reward kéo model vào collapse
```

Câu chốt:

```text
Generator học sinh payload theo condition.
Discriminator học phân phối real/fake bằng WGAN-GP.
Classifier độc lập ép payload đúng type/db.
Novelty/diversity guard ngăn memorization.
Gumbel-Softmax thay REINFORCE để gradient không biến mất sau phase adversarial.
```
