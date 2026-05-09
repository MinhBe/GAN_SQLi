# Kế hoạch Triển Khai SeqGAN SQLi

> Dựa trên: `SeqGAN_SQLi/Guiding.md` + dataset `Asset/LabelData/combined_labeled_data.csv` (40,860 rows)
> Trạng thái: Folder rỗng hoàn toàn — implement từ đầu.

---

## Tổng quan pipeline

```
combined_labeled_data.csv (40,860 rows)
        ↓ Sprint 1 — Data Pipeline
train/val/test.csv + tokenizer_vocab.json + expert_demos.csv
        ↓ Sprint 2 — Model Code (src/*.py)
Generator (LSTM) + Discriminator (1D-CNN) + SQLiEnv + RewardOracle
        ↓ Sprint 3 — MLE Pre-training
checkpoints/mle_best.pt  (perplexity converged)
        ↓ Sprint 4 — Adversarial RL (REINFORCE + MC rollout)
checkpoints/adv_final.pt
        ↓ Sprint 5 — Evaluation
ASR / Syntax Validity / Self-BLEU report
```

---

## Sprint 1: Data Pipeline

### Files cần tạo

| File | Mô tả |
|------|-------|
| `src/tokenizer.py` | SQLTokenizer: de-lex + tokenize + vocab + encode/decode |
| `data/prepare_seqgan_data.py` | Đọc CSV → de-lex → split → expert_demos → save |
| `data/tokenizer_vocab.json` | [generated] |
| `data/train.csv`, `val.csv`, `test.csv` | [generated, 70/15/15 stratified] |
| `data/expert_demos.csv` | [generated, confidence ≥ 0.95 làm proxy] |

### De-lexicalization rules

Mục đích: giảm vocab từ hàng nghìn xuống ~150 tokens để giảm variance cho policy gradient.

```
payload_norm:  "select * from users where id = '1' or 1=1 --"
payload_delex: "select * from __TABLE__ where __COL__ = __STR__ or __INT__ = __INT__ --"
```

| Pattern | Token |
|---------|-------|
| `'...'` hoặc `"..."` | `__STR__` |
| Integer `\b\d+\b` | `__INT__` |
| `0x[0-9a-fA-F]+` | `__HEX__` |
| Common table names (users, admin, ...) | `__TABLE__` |
| Common column names (id, name, password, ...) | `__COL__` |
| DB names (mysql, master, ...) | `__DB__` |
| `__TIME__` (đã có sẵn trong dataset) | giữ nguyên |

### Split strategy

- Stratified split theo `sqli_type` để giữ đúng tỷ lệ mỗi type
- Test set **freeze seed=42 trước** — không bao giờ dùng cho training
- Expert demos proxy: `is_attack=True AND confidence ≥ 0.95`

### Label normalization nhẹ (trong data prep)

```python
RENAME = {'boolean_based': 'boolean_blind', 'stacked_query': 'stacked_queries'}
df['sqli_type'] = df['sqli_type'].replace(RENAME)
```

---

## Sprint 2: Model Code

### Files cần tạo

| File | Mô tả |
|------|-------|
| `src/utils.py` | `pad_sequences`, `set_seed`, `save_checkpoint`, `load_checkpoint` |
| `src/tokenizer.py` | SQLTokenizer class |
| `src/generator.py` | `GeneratorLSTM`: 3-layer LSTM hidden=512 |
| `src/discriminator.py` | `DiscriminatorCNN`: TextCNN kernels=[3,4,5], WGAN-GP |
| `src/env.py` | `SQLiEnv`: reset / step(action) / compute_reward |
| `src/reward.py` | `RewardOracle`: syntax (sqlparse) + bypass proxy + shaping |
| `src/rollout.py` | `MCRollout`: K=16 rollouts → Q(s,a) estimate |
| `src/baseline.py` | `ValueBaseline`: MLP trên hidden state, EMA decay=0.95 |
| `src/losses.py` | `reinforce_loss`, `wgan_gp_loss`, `mle_loss` |
| `src/scheduled_sampling.py` | `ScheduledSampler`: ε tăng linear 0→1 trong 5k steps |

### Generator (LSTM)

```python
class GeneratorLSTM(nn.Module):
    # embed_dim=128, hidden_dim=512, num_layers=3, dropout=0.2
    # forward(input_ids, hidden) → (logits: B×T×V, hidden)
    # sample(batch_size, max_len) → token_ids  (autoregressive, multinomial)
    # get_hidden(input_ids) → last hidden state  (dùng cho baseline)
```

### Discriminator (TextCNN / WGAN-GP)

```python
class DiscriminatorCNN(nn.Module):
    # kernels=[3,4,5], filters=128 each → concat → Linear → scalar
    # forward(input_ids) → Wasserstein score (B,)
    # gradient_penalty(real_ids, fake_ids) → scalar  (λ=10)
```

### SQLiEnv

```python
class SQLiEnv:
    def reset() → State(<SOS>)
    def step(action_token) → (next_state, reward=0, done, info)
    # reward = 0 cho intermediate steps
    # reward = compute_reward(full_seq) khi done=True (EOS hoặc max_len)
    def compute_reward(token_ids) → {'syntax': 0/1, 'bypass': float, 'total': float}
```

### Reward shaping

```
r_total = λ_D·D(x) + λ_bypass·r_bypass + λ_syntax·r_syntax - length_penalty

Khởi đầu: λ_D=0.3, λ_bypass=0.5, λ_syntax=0.2

Dev mode (không có Docker ModSecurity):
  r_bypass = 0.1 nếu sqli_type != 'benign'  (proxy flat)
  r_bypass = 0.0 nếu sqli_type == 'benign'
  
length_penalty = 0.01 * max(0, len(seq) - max_len)
```

---

## Sprint 3: MLE Pre-training

### File: `pretrain_mle.py`

```
1. Load tokenized train.csv + expert_demos.csv
2. Teacher forcing: loss = CrossEntropy(logits_t, token_{t+1})
3. Expert demos: upweight loss × 3.0
4. Scheduled Sampling: ε(step) = min(1.0, step/5000) — tăng linear
5. Val perplexity sau mỗi epoch → save best checkpoint
6. Early stop khi plateau (patience=3)
```

### Config (configs/seqgan_default.yaml)

```yaml
pretrain:
  epochs: 10
  lr: 1.0e-3
  batch_size: 64
  expert_weight: 3.0
  scheduled_sampling_steps: 5000
  grad_clip: 1.0
```

**Verify:** val perplexity giảm monotonically sau ~3 epoch đầu.

---

## Sprint 4: Adversarial RL Training

### File: `train_adversarial.py`

**REINFORCE loop (50k steps):**

```python
for step in range(50_000):
    # 1. Generator sample batch
    seqs, log_probs = generator.sample(B=64)

    # 2. MC rollout Q estimate  ← bottleneck
    for t in range(T):
        q_values[:, t] = mc_rollout(generator, seqs[:, :t+1], K=16)
    # Optimization: batch tất cả K rollouts: reshape (B,K,L) → (B*K, L)

    # 3. Advantage
    advantages = q_values - baseline(hidden_states)

    # 4. Generator update (REINFORCE)
    g_loss = -mean(log_probs * advantages.detach())
    g_loss.backward()
    clip_grad_norm_(g_params, 1.0)
    g_optim.step()

    # 5. Discriminator update ×5 (WGAN-GP)
    for _ in range(5):
        d_loss = d(real) - d(fake) + gradient_penalty(real, fake)
        d_loss.backward(); d_optim.step()

    # 6. Baseline update
    b_loss = MSE(baseline(hidden), q_values.detach())
    b_loss.backward(); b_optim.step()
```

**Reward hacking prevention:**
- Length penalty trong reward
- Nếu syntax_rate < 0.5 sau 5k steps → tự động raise λ_syntax lên 0.4

```yaml
adversarial:
  total_steps: 50000
  lr_g: 1.0e-4
  lr_d: 1.0e-4
  batch_size: 64
  mc_rollout_k: 16
  d_steps_per_g: 5
  gp_lambda: 10.0
  baseline_ema_decay: 0.95
  grad_clip: 1.0
```

---

## Sprint 5: Evaluation + Baselines

### Files

| File | Mô tả |
|------|-------|
| `evaluate.py` | ASR + Syntax + Self-BLEU-3 trên 1000 samples |
| `generate.py` | Inference: sinh payload từ checkpoint |
| `baselines/template_based.py` | Random template fill |
| `baselines/mle_lm_only.py` | Pretrained checkpoint, không RL |
| `baselines/seqgan_vanilla.py` | RL không có advantage (Q thay vì Q-b) |

### Metrics bắt buộc (Guiding.md §10)

| Metric | Cách tính | Target |
|--------|-----------|--------|
| **ASR** | % 1000 samples bypass (dev: sqlparse proxy) | > MLE baseline + 30% |
| **Syntax Validity** | % parse được bằng `sqlparse` | > 90% |
| **Self-BLEU-3** | n-gram diversity (thấp hơn = đa dạng hơn) | < dataset baseline |
| **Reward convergence** | mean reward per 1000 steps | Tăng dần, không plateau sớm |

---

## Cấu trúc thư mục cuối cùng

```
SeqGAN_SQLi/
├── Guiding.md
├── IMPLEMENTATION_PLAN.md        ← FILE NÀY
├── requirements.txt
├── configs/
│   ├── seqgan_default.yaml
│   └── seqgan_ablation.yaml
├── data/
│   ├── prepare_seqgan_data.py
│   ├── extract_expert_demos.py   (placeholder — Docker WAF sau)
│   ├── tokenizer_vocab.json      [generated]
│   ├── train.csv                 [generated]
│   ├── val.csv                   [generated]
│   ├── test.csv                  [generated, FROZEN]
│   └── expert_demos.csv          [generated]
├── src/
│   ├── tokenizer.py
│   ├── generator.py
│   ├── discriminator.py
│   ├── env.py
│   ├── reward.py
│   ├── rollout.py
│   ├── baseline.py
│   ├── losses.py
│   ├── scheduled_sampling.py
│   └── utils.py
├── baselines/
│   ├── template_based.py
│   ├── mle_lm_only.py
│   └── seqgan_vanilla.py
├── waf_eval/
│   ├── modsec_runner.py          (stub — Docker sau)
│   └── docker-compose.yml
├── pretrain_mle.py
├── train_adversarial.py
├── evaluate.py
├── generate.py
└── checkpoints/
```

---

## Thứ tự implementation

```
Sprint 1  src/tokenizer.py
          data/prepare_seqgan_data.py
          → chạy: python data/prepare_seqgan_data.py
          → verify: vocab ~100-200 tokens, splits đúng tỷ lệ

Sprint 2  src/utils.py → src/generator.py → src/discriminator.py
          → src/reward.py → src/env.py → src/rollout.py
          → src/baseline.py → src/losses.py → src/scheduled_sampling.py
          → smoke test: generator forward pass shape OK

Sprint 3  pretrain_mle.py
          → python pretrain_mle.py --config configs/seqgan_default.yaml
          → verify: val perplexity giảm sau mỗi epoch

Sprint 4  train_adversarial.py
          → python train_adversarial.py --pretrain_ckpt checkpoints/mle_best.pt
          → verify: mean_reward tăng dần, không NaN

Sprint 5  evaluate.py → generate.py → baselines/
          → python evaluate.py --ckpt checkpoints/adv_final.pt --n_samples 1000
```

---

## Smoke test checklist (Guiding.md §13)

```bash
# Sprint 1
python data/prepare_seqgan_data.py
# Expected: vocab 100-200 tokens, train ~28.6k / val ~6.1k / test ~6.1k

# Sprint 2
python -c "
import sys; sys.path.insert(0, '.')
import torch, json
from src.tokenizer import SQLTokenizer
from src.generator import GeneratorLSTM
vocab = json.load(open('data/tokenizer_vocab.json'))
g = GeneratorLSTM(len(vocab))
x = torch.randint(0, len(vocab), (4, 20))
logits, _ = g(x)
print('Generator OK:', logits.shape)   # (4, 20, vocab_size)
seqs = g.sample(4, 32, 'cpu')
print('Sample OK:', seqs.shape)        # (4, <=32)
"

# Sprint 3 smoke
python pretrain_mle.py --config configs/seqgan_default.yaml --epochs 1 --steps 100
# Expected: loss giảm, không NaN

# Sprint 4 smoke
python train_adversarial.py --pretrain_ckpt checkpoints/mle_best.pt --steps 100
# Expected: không NaN, reward log hợp lý

# Sprint 5
python evaluate.py --ckpt checkpoints/adv_final.pt --n_samples 100
# Expected: syntax_rate, asr, self_bleu được in ra
```

---

## Troubleshooting (Guiding.md §14)

| Triệu chứng | Nguyên nhân | Hành động |
|---|---|---|
| MLE loss không giảm | LR hoặc architecture | Tune LR, tăng capacity G |
| RL divergence / NaN | Variance gradient | Tăng baseline weight, K=24-32 |
| Reward plateau, ASR thấp | Reward hacking | Thêm length penalty, semantic check |
| Mode collapse | G collapse về 1 mode | Tăng dropout, diversity bonus |
| ASR cao, validity thấp | G học bypass trick không hợp lệ SQL | Tăng λ_syntax |
| Validity cao, ASR ngang baseline | G chỉ học MLE distribution | Tăng λ_bypass, train RL lâu hơn |
| OOM với MC rollout | K quá lớn | Giảm K=8, gradient checkpointing |
