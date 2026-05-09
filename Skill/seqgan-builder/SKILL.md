---
name: seqgan-builder
description: |
  Build a SeqGAN model for SQL injection payload generation, step by step.
  Trigger when: implementing SeqGAN, coding generator / discriminator / reward oracle,
  setting up adversarial RL training loop, writing MLE pre-training, building SQLiEnv,
  implementing Monte Carlo rollout, debugging REINFORCE / policy gradient, or following
  the SeqGAN_SQLi implementation plan for this project.
  Do NOT trigger for: pure evaluation tasks, WAF rule analysis, dataset labeling.
---

# seqgan-builder — Skill Guide

## Role & Prime Directive

You are the **SeqGAN implementation engineer** for this project. Your job is to build a working
SeqGAN pipeline that generates SQL injection payloads and optimizes WAF Evasion Rate (ASR)
directly via policy gradient.

Bám sát `SeqGAN_SQLi/IMPLEMENTATION_PLAN.md` cho code cụ thể và `SeqGAN_SQLi/Guiding.md` cho
lý thuyết. Không thêm feature ngoài scope của 5 sprint dưới đây.

---

## Architecture Overview

```
Generator π_θ (LSTM 3-layer hidden=512)
    ↓ sample token a_t (multinomial)
SQLiEnv.step(a_t)
    ↓ EOS → compute_reward
RewardOracle: syntax(sqlparse) + bypass(ModSecurity) + D_φ(x)
    r_total = λ_D·D(x) + λ_bypass·r_bypass + λ_syntax·r_syntax − length_penalty
    ↓
MCRollout: K=16 rollouts → Q(s_t, a_t)
Advantage: A(s_t, a_t) = Q(s_t, a_t) − b_ψ(s_t)
    ↓
REINFORCE update: ∇_θ J = E[A · ∇_θ log π_θ(a|s)]
Discriminator D_φ (1D-CNN, WGAN-GP): update 5× per G update
```

**Data flow**: `combined_labeled_data.csv (40,860 rows)` → de-lex → split 70/15/15 → expert_demos →
MLE pretrain → adversarial RL → evaluate.

---

## Sprint Workflow

### Sprint 1 — Data Pipeline

**Files**: `src/tokenizer.py`, `data/prepare_seqgan_data.py`

**De-lexicalization rules** (full de-lex, giảm vocab từ nghìn xuống ~150 tokens):

| Pattern | Token |
|---------|-------|
| `'...'` hoặc `"..."` | `__STR__` |
| Integer `\b\d+\b` | `__INT__` |
| `0x[0-9a-fA-F]+` | `__HEX__` |
| Table names (users, admin, ...) | `__TABLE__` |
| Column names (id, name, password, ...) | `__COL__` |
| DB names (mysql, master, ...) | `__DB__` |

**Split strategy**: stratified theo `sqli_type`, seed=42 cố định, test set FROZEN không bao giờ
dùng cho training.

**Expert demos proxy** (khi chưa có Docker WAF):
```python
expert_mask = (df['is_attack'] == True) & (df['confidence'] >= 0.95)
expert_demos = df[expert_mask]
```

**Label normalization**:
```python
RENAME = {'boolean_based': 'boolean_blind', 'stacked_query': 'stacked_queries'}
df['sqli_type'] = df['sqli_type'].replace(RENAME)
```

**Smoke test Sprint 1**:
```bash
python data/prepare_seqgan_data.py
# Expected: vocab 100-200 tokens, train ~28.6k / val ~6.1k / test ~6.1k
```

---

### Sprint 2 — Model Code

**Files**: `src/utils.py`, `src/generator.py`, `src/discriminator.py`, `src/env.py`,
`src/reward.py`, `src/rollout.py`, `src/baseline.py`, `src/losses.py`,
`src/scheduled_sampling.py`

#### Generator (LSTM — recommended start)

```python
class GeneratorLSTM(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, hidden_dim=512, num_layers=3, dropout=0.2):
        ...
    def forward(self, input_ids, hidden=None):
        # Returns (logits: B×T×V, hidden)
    def sample(self, batch_size, max_len, device) -> Tensor:
        # Autoregressive multinomial sampling → token_ids (B, ≤max_len)
    def get_hidden(self, input_ids) -> Tensor:
        # Last hidden state → dùng cho baseline value network
```

> Transformer Decoder là option B — switch chỉ khi LSTM không đủ capacity.

#### Discriminator (TextCNN / WGAN-GP)

```python
class DiscriminatorCNN(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, kernel_sizes=[3,4,5], num_filters=128):
        ...
    def forward(self, input_ids) -> Tensor:
        # Wasserstein score (B,) — không sigmoid
    def gradient_penalty(self, real_ids, fake_ids) -> Tensor:
        # λ_gp = 10
```

#### SQLiEnv

```python
class SQLiEnv:
    def reset(self) -> State:
        """s_0 = (<SOS>,)"""
    def step(self, action: int) -> Tuple[State, float, bool, dict]:
        """reward=0 tại intermediate; reward=compute_reward(...) khi done"""
    def compute_reward(self, token_ids: List[int]) -> dict:
        """{'syntax': 0/1, 'bypass': float, 'total': float}"""
```

#### Reward shaping

```
r_total = λ_D·D(x) + λ_bypass·r_bypass + λ_syntax·r_syntax − length_penalty

Khởi đầu: λ_D=0.3, λ_bypass=0.5, λ_syntax=0.2
length_penalty = 0.01 * max(0, len(seq) − max_len)

Dev mode (không có Docker ModSecurity):
  r_bypass = 0.1 nếu sqli_type != 'benign'
  r_bypass = 0.0 nếu sqli_type == 'benign'
```

#### MCRollout

```python
class MCRollout:
    def __init__(self, generator, K=16):
        ...
    def estimate_q(self, seqs, t) -> Tensor:
        # Sinh K rollouts từ prefix seqs[:, :t+1]
        # Batch reshape: (B,K,L) → (B*K, L) để forward 1 lần
        # Returns Q(s_t, a_t): shape (B,)
```

#### ValueBaseline

```python
class ValueBaseline(nn.Module):
    # MLP trên hidden state của Generator
    # EMA decay=0.95 cho running baseline
    def forward(self, hidden) -> Tensor:  # (B,)
```

**Smoke test Sprint 2**:
```python
vocab = json.load(open('data/tokenizer_vocab.json'))
g = GeneratorLSTM(len(vocab))
x = torch.randint(0, len(vocab), (4, 20))
logits, _ = g(x)
assert logits.shape == (4, 20, len(vocab))  # Generator OK
seqs = g.sample(4, 32, 'cpu')
assert seqs.ndim == 2  # Sample OK
```

---

### Sprint 3 — MLE Pre-training

**File**: `pretrain_mle.py`

```
1. Load tokenized train.csv + expert_demos.csv
2. Teacher forcing: loss = CrossEntropy(logits_t, token_{t+1})
3. Expert demos: upweight × 3.0
4. Scheduled Sampling: ε(step) = min(1.0, step/5000) — linear ramp
5. Val perplexity sau mỗi epoch → save best checkpoint
6. Early stop: patience=3 epochs
```

**Config** (`configs/seqgan_default.yaml`):
```yaml
pretrain:
  epochs: 10
  lr: 1.0e-3
  batch_size: 64
  expert_weight: 3.0
  scheduled_sampling_steps: 5000
  grad_clip: 1.0
```

**Verify**: val perplexity giảm monotonically sau ~3 epoch đầu.

**Smoke test Sprint 3**:
```bash
python pretrain_mle.py --config configs/seqgan_default.yaml --epochs 1 --steps 100
# Expected: loss giảm, không NaN
```

---

### Sprint 4 — Adversarial RL

**File**: `train_adversarial.py`

```python
for step in range(50_000):
    # 1. Generator sample batch
    seqs, log_probs = generator.sample(B=64)

    # 2. MC rollout Q estimate  ← bottleneck: batch tất cả K rollouts
    for t in range(T):
        q_values[:, t] = mc_rollout.estimate_q(seqs, t)
    # reshape (B,K,L) → (B*K, L) để 1 forward pass

    # 3. Advantage = Q − baseline
    advantages = q_values - baseline(generator.get_hidden(seqs))

    # 4. REINFORCE update
    g_loss = -( log_probs * advantages.detach() ).mean()
    clip_grad_norm_(g_params, 1.0)
    g_optim.step()

    # 5. Discriminator × 5 (WGAN-GP)
    for _ in range(5):
        d_loss = -d(real).mean() + d(fake).mean() + gradient_penalty(real, fake)
        d_optim.step()

    # 6. Baseline MSE update
    b_loss = F.mse_loss(baseline(hidden), q_values.detach())
    b_optim.step()
```

**Reward hacking prevention**:
- Length penalty trong reward (đã định nghĩa Sprint 2)
- Auto-adjust: nếu `syntax_rate < 0.5` sau 5k steps → raise `λ_syntax = 0.4`

**Config**:
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

**Logging bắt buộc mỗi 1000 steps**: G_loss, D_loss, mean_reward, ASR_val, syntax_rate, `‖∇G‖`.

**Smoke test Sprint 4**:
```bash
python train_adversarial.py --pretrain_ckpt checkpoints/mle_best.pt --steps 100
# Expected: không NaN, reward log hợp lý
```

---

### Sprint 5 — Evaluation & Baselines

**Files**: `evaluate.py`, `generate.py`, `baselines/template_based.py`,
`baselines/mle_lm_only.py`, `baselines/seqgan_vanilla.py`

**Metrics bắt buộc** — xem `references/evaluation-metrics.md` hoặc `SKILL_SEQGAN_EVALUATOR.md`:

| Metric | Cách tính | Target |
|--------|-----------|--------|
| ASR | % bypass / 1000 samples | > MLE baseline + 30% |
| Syntax Validity | % parse được (sqlparse) | ≥ 90% |
| Self-BLEU-3 | n-gram diversity | < dataset baseline |
| Reward convergence | mean reward per 1000 steps | Tăng dần, không plateau sớm |

**4 Baselines bắt buộc cho paper**:
1. `template_based.py` — random template fill
2. `mle_lm_only.py` — pretrained checkpoint, không RL
3. `seqgan_vanilla.py` — RL không advantage (Q thay vì Q−b)
4. **SeqGAN + advantage** (model chính)

**Smoke test Sprint 5**:
```bash
python evaluate.py --ckpt checkpoints/adv_final.pt --n_samples 100
# Expected: syntax_rate, asr, self_bleu được in ra
```

---

## Architecture Decisions

| Quyết định | Lý do |
|------------|-------|
| LSTM thay vì Transformer | Đơn giản hơn, ít memory hơn — switch Transformer nếu cần |
| REINFORCE thay vì DDPG | Phù hợp discrete action space; không cần differentiable reward |
| WGAN-GP thay vì vanilla GAN | Training stable hơn, tránh mode collapse |
| K=16 rollout | Compromise variance vs compute; giảm xuống K=8 khi stable |
| Full de-lex | Giảm vocab ~150 tokens → giảm variance policy gradient |
| Expert demos upweight ×3 | MLE pretrain học từ bypass payloads trước → better RL init |
| Scheduled Sampling (0→1, 5k steps) | Giảm exposure bias giữa pretrain và RL phase |

---

## Pre-Sprint Checklist

Verify trước khi bắt đầu code:

- [ ] `combined_labeled_data.csv` tồn tại và đúng schema
- [ ] Train/val/test split với seed=42 cố định
- [ ] Vocabulary frozen sau Sprint 1
- [ ] Tokenizer round-trip identity: `decode(encode(x)) == x`
- [ ] ModSecurity Docker build OK (hoặc dev mode proxy đã sẵn sàng)
- [ ] Expert demos extracted (~5-10% train set)
- [ ] Generator forward pass shape OK
- [ ] Discriminator forward pass shape OK
- [ ] SQLiEnv interface match gym-like spec
- [ ] Smoke MLE pretrain 100 steps → loss giảm
- [ ] Smoke RL 100 steps → no NaN

---

## Dev Mode (không có Docker/ModSecurity)

```python
# src/reward.py — dev mode bypass proxy
def bypass_proxy(sqli_type: str) -> float:
    return 0.1 if sqli_type != 'benign' else 0.0
```

Dùng proxy này trong Sprint 2-4. Thay thế bằng ModSecurity Docker ở Sprint 5.

---

## Reference Files

Đọc các file này khi cần lookup chi tiết — không cần load tất cả ngay:

| File | Khi nào đọc |
|------|-------------|
| `references/hyperparameters.md` | Tune hyperparams, OOM issues, so sánh config |
| `references/pitfalls.md` | Debug NaN, mode collapse, reward plateau, ASR thấp |
| `SeqGAN_SQLi/Guiding.md` | Lý thuyết, toán học, architecture, limitations |
| `SeqGAN_SQLi/IMPLEMENTATION_PLAN.md` | Code cụ thể, file paths, sprint checklist |
| `Asset/Guiding/SQLi-SeqGAN-Roadmap.md` | Roadmap đầy đủ 6 giai đoạn (paper-level) |
