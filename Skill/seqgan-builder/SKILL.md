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
┌─────────────────────────────────────────────────────────────────────┐
│                     LUỒNG DỮ LIỆU & REWARD                          │
│                                                                      │
│  G (Bi-LSTM 2-layer)  ──── payload (token_ids) ────►  D (WGAN-GP)  │
│       │                                                    │         │
│       │ type_embedding                              Wasserstein loss  │
│       │ (conditioned)                               (W-distance)     │
│       │                                                    │         │
│       │◄──── REINFORCE update ◄─── SQLiEnv.step() ◄────── │         │
│       │           ∇_θ J = E[A·∇log π]                     │         │
│       │                    │                               │         │
│       │              compute_reward()                      │         │
│       │              ┌─────┴───────────────────────┐       │         │
│       │              │  r_total (weighted sum):     │       │         │
│       │              │  α·WAF_score   (ModSec)      │       │         │
│       │              │  β·syntax_score (sqlparse)   │       │         │
│       │              │  γ·diversity_bonus           │       │         │
│       │              │  δ·D_wasserstein (normalized)│       │         │
│       │              │  −ε·repetition_penalty       │       │         │
│       │              └─────────────────────────────-┘       │         │
│       │                                                      │         │
│       │         WAF (ModSecurity OWASP CRS)                 │         │
│       │         bypass=1.0 / partial=0.5 / blocked=0.0      │         │
│       │         [Docker REST endpoint hoặc dev proxy]        │         │
└───────────────────────────────────────────────────────────────────────┘
```

**Mối quan hệ 3 thành phần**:

| Cặp | Quan hệ |
|-----|---------|
| G → D | G sinh payload; D đo Wasserstein distance giữa real và fake |
| D → G | D_loss làm 1 thành phần của reward (γ·D_score normalized) |
| G → WAF | G sinh payload; WAF chấm bypass score (0/0.5/1) |
| WAF → G | WAF score là thành phần reward chính (α·WAF_score) |
| D + WAF → G | Tổng reward = α·WAF + β·syntax + γ·diversity − δ·repetition; dùng trong REINFORCE |

**Lưu ý quan trọng**: D (Discriminator) và WAF là **2 nguồn reward độc lập**:
- D đo "payload có trông giống attack thật không" (phân phối)
- WAF đo "payload có vượt qua firewall không" (thực tế)

**Data flow**: `combined_labeled_data.csv (17,821 rows attack + ~5000 benign)` → de-lex → split
70/15/15 → expert_demos → MLE pretrain → adversarial RL → evaluate.

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

**Benign SQL data** (cho Discriminator training):
```python
# Cần ~5000 benign queries: SELECT/INSERT/UPDATE không có injection patterns
# Nguồn gợi ý: spider dataset, WikiSQL, hoặc tự generate từ template
# Schema: payload_norm, sqli_type='benign', db_engine='generic', confidence=0.95
benign_df = pd.read_csv('data/benign_sql_5000.csv')
# Lưu riêng — chỉ dùng cho Discriminator, KHÔNG trộn vào Generator training data
benign_df.to_csv('data/benign_for_discriminator.csv', index=False)
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

#### Generator (Bi-LSTM 2-layer — recommended)

```python
class GeneratorBiLSTM(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, hidden_dim=256, num_layers=2,
                 dropout=0.2, num_attack_types=14):
        # BiLSTM: 2 directions × hidden_dim = 512 effective hidden
        # type_embedding: num_attack_types → embed_dim (conditioned generation)
        # input = token_embed + type_embed (concatenate trước LSTM)
        ...
    def forward(self, input_ids, attack_type_ids=None, hidden=None):
        # attack_type_ids: (B,) — index của attack type để condition
        # Returns (logits: B×T×V, hidden)
    def sample(self, batch_size, max_len, device, attack_type=None) -> Tensor:
        # Autoregressive multinomial sampling → token_ids (B, ≤max_len)
        # attack_type: None = random sample from all types (balanced)
    def get_hidden(self, input_ids) -> Tensor:
        # Last hidden state → dùng cho baseline value network
```

**Lý do BiLSTM**: Forward pass sinh token trái-phải; backward pass cung cấp context toàn câu.
SQL có cú pháp phụ thuộc xa (keyword cuối ảnh hưởng keyword đầu) → BiLSTM tốt hơn unidirectional.

> Transformer Decoder là option C — switch chỉ khi BiLSTM không đủ capacity sau 10k steps.

#### Discriminator (WGAN-GP Critic)

```python
class DiscriminatorCNN(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, kernel_sizes=[3,4,5], num_filters=128):
        # Output: Wasserstein score (B,) — KHÔNG sigmoid, không softmax
        # Training: WGAN loss = E[D(real)] − E[D(fake)] + λ_gp·GP
        ...
    def forward(self, input_ids) -> Tensor:
        # Wasserstein critic score (B,) — unbounded real number
    def gradient_penalty(self, real_ids, fake_ids, λ_gp=10.0) -> Tensor:
        # Interpolated gradient penalty để enforce 1-Lipschitz
```

**Dữ liệu training Discriminator** (3 class):
- `real_attack`: 17,821 rows từ `combined_labeled_data.csv` (positive)
- `fake_attack`: sinh từ G mỗi step (negative)
- `benign_sql`: ~5,000 benign SQL queries (SELECT/INSERT/UPDATE không có injection) — negative

> **Lý do thêm benign**: D phải học phân biệt malicious vs benign, không chỉ real vs fake.
> Nếu thiếu benign, D sẽ chỉ phân biệt "cũ vs mới" → reward signal vô nghĩa.

**Adapter WGAN score → reward component**:
```python
def wgan_to_reward(wasserstein_score: float, percentile_95: float) -> float:
    # Normalize về [0, 1] dựa trên running percentile của real data scores
    return float(np.clip(wasserstein_score / (percentile_95 + 1e-8), 0, 1))
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

#### Reward shaping (Multi-signal)

```
r_total = α·WAF_score + β·syntax_score + γ·diversity_bonus
        + δ·D_score_normalized − ε·repetition_penalty − length_penalty

Khởi đầu: α=0.40, β=0.25, γ=0.15, δ=0.20
          (tổng = 1.0 trước penalties)

WAF_score:
  - Real WAF (Docker ModSecurity): bypass=1.0, partial=0.5, blocked=0.0
  - Dev proxy: sqli_type != 'benign' → 0.3, else 0.0

syntax_score:
  - 1.0 nếu sqlparse.parse(relex(payload)) hợp lệ
  - 0.0 nếu không parse được

diversity_bonus:
  - 1 − max_char_ngram_overlap(payload, last_64_generated)
  - Đo novelty so với 64 payloads gần nhất đã sinh
  - = 1.0 nếu hoàn toàn mới; = 0.0 nếu trùng hoàn toàn

D_score_normalized:
  - wgan_to_reward(D.forward(payload), running_percentile_95)
  - Measure "trông giống attack thật không"

repetition_penalty:
  - 1.0 nếu payload giống >90% với bất kỳ payload trong last_64_generated
  - 0.0 otherwise

length_penalty:
  - 0.02 * max(0, len(seq) − max_len)

Auto-adjust (sau mỗi 5000 steps):
  - Nếu syntax_rate < 0.50 → tăng β lên 0.40 (tạm thời 5000 steps)
  - Nếu self_bleu_3 > 0.80 → tăng γ lên 0.25 (mode collapse detected)
  - Nếu WAF bypass < 20% → tăng α lên 0.55
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

**Type-conditioned batch sampling** (chống mode collapse):
```python
ATTACK_TYPES = ['union_based','boolean_blind','time_blind','error_based',
                'stacked_queries','auth_bypass','out_of_band','second_order']
# Mỗi batch: sample đều từ tất cả types
type_ids = torch.tensor([i % len(ATTACK_TYPES) for i in range(B)], device=device)
seqs, log_probs = generator.sample(B=64, attack_type=type_ids)
```

**Reward hacking prevention**:
- Length penalty trong reward (đã định nghĩa Sprint 2)
- Diversity bonus + repetition penalty trong reward (đã định nghĩa Sprint 2)
- Auto-adjust weights: nếu `syntax_rate < 0.5` → raise β; nếu `self_bleu_3 > 0.80` → raise γ

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
| Bi-LSTM 2-layer thay LSTM 1-layer | SQL cú pháp phụ thuộc xa; thầy gợi ý trực tiếp; tăng capacity ~2x |
| REINFORCE thay vì DDPG | Phù hợp discrete action space; không cần differentiable reward |
| WGAN-GP thay vì vanilla GAN | Training stable hơn; thầy gợi ý; tránh D quá mạnh → G không học |
| K=16 rollout | Compromise variance vs compute; giảm xuống K=8 khi stable |
| Full de-lex | Giảm vocab ~150 tokens → giảm variance policy gradient |
| Expert demos upweight ×3 | MLE pretrain học từ bypass payloads trước → better RL init |
| Scheduled Sampling (0→1, 5k steps) | Giảm exposure bias giữa pretrain và RL phase |
| Type-conditioned generation | 88.6% data là Oracle XMLTYPE → buộc G sinh đa dạng per-type |
| Benign SQL trong Discriminator | Thầy yêu cầu; D phải học malicious vs benign, không chỉ real vs fake |
| Multi-signal reward (α·WAF+β·syntax+γ·diversity−δ·rep) | Ngăn reward hacking và mode collapse gốc rễ |

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
