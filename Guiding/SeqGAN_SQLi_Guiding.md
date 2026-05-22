# Guiding — SeqGAN SQLi (Policy Gradient / REINFORCE Approach)

> **Đối tượng đọc**: Bản thân nghiên cứu sinh khi tái kích hoạt nhánh SeqGAN sau gián đoạn dài. Self-contained — không cần mở Roadmap gốc cho ngày-ngày coding, nhưng cho details paper-level vẫn nên tham chiếu `Asset/Guiding/SQLi-SeqGAN-Roadmap.md`.
>
> **Phong cách**: technical thẳng (giả định đã đọc `AI_Foundations_For_Team_*.md` series).

> **Cập nhật**: 2026-05-04
> **Trạng thái implementation**: ❌ Folder rỗng — chưa code dòng nào.

---

## Mục lục

1. [Mở đầu & Mục tiêu approach](#1-mở-đầu)
2. [Trạng thái hiện tại & Bắt đầu lại từ đâu](#2-trạng-thái)
3. [Why this approach? — Lý do tồn tại](#3-why)
4. [Cơ sở toán học](#4-toán-học)
5. [Why this NOT that — So sánh](#5-not-that)
6. [Limitations](#6-limitations)
7. [Quick-start tái kích hoạt](#7-quick-start)
8. [Đặc thù: Kiến trúc & Dataset transformation](#8-đặc-thù)
9. [Hyperparameters](#9-hyperparams)
10. [Đánh giá: Metrics & Baselines](#10-eval)
11. [Cấu trúc thư mục đề xuất](#11-skeleton)
12. [Vị trí dữ liệu & tài liệu](#12-paths)

---

## 1. Mở đầu & Mục tiêu approach

**Bài toán chung**: Sinh chuỗi token SQL injection thỏa mãn ràng buộc grammar và tối đa hóa **WAF Evasion Rate (ASR)**.

**SeqGAN approach** = mô hình hóa quá trình sinh SQLi như **Sequential Decision Making (RL)**: Generator đóng vai **Agent** chọn token tại mỗi bước thời gian; Discriminator + WAF Oracle + SQL Parser cung cấp **reward signal**; tối ưu Policy qua thuật toán **REINFORCE** với variance reduction (baseline + Monte Carlo rollout).

**Đặc trưng phân biệt với 2 approach kia**:
- SeqGAN dùng được **reward không-differentiable** (WAF Oracle, SQL parser) — tối ưu trực tiếp ASR.
- SeqGAN **không có encoder** → không có structured latent space.
- SeqGAN có **Expert Demonstrations** (payload đã bypass WAF) cho Behavior Cloning pre-training.

**Mục tiêu paper**: Demonstrate model có thể tối ưu trực tiếp objective **WAF bypass** thay vì proxy loss; baseline so sánh với pure MLE LM và SeqGAN vanilla.

---

## 2. Trạng thái hiện tại

| Stage | Status |
|---|---|
| Data engineering | ✅ Done (xem `Asset/Guiding/Data_Engineering_Recap.md`) |
| Roadmap (`Asset/Guiding/SQLi-SeqGAN-Roadmap.md`) | ✅ Done |
| Dataset transformation cho SeqGAN (full de-lex) | ❌ Cần làm |
| Expert Demonstrations extraction | ❌ Cần làm (chạy WAF Oracle trên dataset, tag bypass) |
| Tokenizer | ❌ |
| Generator (LSTM hoặc Transformer Decoder) | ❌ |
| Discriminator (1D-CNN) | ❌ |
| `SQLiEnv` wrapper | ❌ |
| Reward Oracle (sqlparse + ModSecurity Docker) | ❌ |
| Monte Carlo rollout module | ❌ |
| Baseline value network | ❌ |
| MLE pre-training (+ Scheduled Sampling) | ❌ |
| Adversarial RL loop (REINFORCE + advantage) | ❌ |
| Evaluation harness | ❌ |

**Bắt đầu lại từ đâu (priority order)**:
1. Verify dataset (mục 12).
2. Implement tokenizer + full de-lex.
3. Build `SQLiEnv` (gym-like interface) + Reward Oracle.
4. Extract Expert Demonstrations: chạy ModSecurity trên train set, tag những payload bypass.
5. Implement Generator policy + Discriminator stub.
6. MLE pre-training (~10 epochs) + Scheduled Sampling.
7. Implement MC rollout + baseline.
8. Adversarial RL loop.
9. Evaluation.

---

## 3. Why this approach?

### 3.1 Vấn đề gốc

Vanilla GAN cho text gặp 2 vấn đề chí mạng:
1. **Argmax không differentiable** → gradient không pass qua sampling step.
2. **Discriminator trả output cho cả chuỗi** → không có signal cho intermediate tokens.

SeqGAN giải quyết bằng cách **coi Generator như RL agent**:
- State $s_t$ = chuỗi đã sinh từ 0..t.
- Action $a_t$ = chọn next token từ vocab.
- Reward $r$ tại terminal state (sau `<EOS>`).
- Policy gradient (REINFORCE) update Generator dựa trên expected reward.

→ KHÔNG cần gradient qua argmax. Sampling là discrete OK.

### 3.2 Lợi thế độc đáo

**Reward có thể là bất kỳ hàm nào** — không cần differentiable:
- $r_{syntax}$ từ `sqlparse` (parse được = 1, không = 0).
- $r_{bypass}$ từ ModSecurity (bypass = 1, blocked = 0).
- Có thể combine: $r = \alpha \cdot r_{bypass} + (1-\alpha) \cdot r_{syntax}$.

Đây là **direct optimization** của metric thực tế (ASR), không phải proxy loss.

### 3.3 Cơ sở khoa học

- **Policy gradient theorem** (Sutton et al.): $\nabla J(\theta) = \mathbb{E}_\tau[\sum_t \nabla \log \pi_\theta(a_t|s_t) \cdot R_\tau]$.
- **REINFORCE** (Williams 1992): unbiased estimator của policy gradient.
- **Variance reduction**: baseline $b(s)$ giảm variance, advantage $A = Q - b$.
- **SeqGAN paper** (Yu et al. 2017): áp dụng vào sequence generation với MC rollout cho Q-value.

---

## 4. Cơ sở toán học

### 4.1 Policy gradient (REINFORCE)

$$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta}\left[\sum_{t=1}^T A(s_t, a_t) \nabla_\theta \log \pi_\theta(a_t | s_t)\right]$$

**Advantage**: $A(s_t, a_t) = Q(s_t, a_t) - b(s_t)$.

### 4.2 Q-value qua Monte Carlo rollout

Tại step $t$ với state $s_t$ và action $a_t$, sinh $K$ rollouts đầy đủ đến terminal state, tính trung bình reward:

$$Q(s_t, a_t) \approx \frac{1}{K} \sum_{k=1}^K R(\tau^{(k)})$$

với $\tau^{(k)} = (s_t, a_t, s_{t+1}^{(k)}, ..., s_T^{(k)})$, rollout policy = chính $\pi_\theta$.

Số $K$ = 16 phổ biến — trade-off giữa variance và compute.

### 4.3 Baseline function

$b_\psi(s_t)$ = value network (MLP nhỏ trên hidden state of $\pi_\theta$). Train với MSE:
$$\mathcal{L}_{baseline} = \frac{1}{T} \sum_t (b_\psi(s_t) - Q(s_t, a_t))^2$$

EMA decay 0.95 cho stability.

### 4.4 Reward shaping

$$r_{total} = \lambda_D \cdot D_\phi(x) + \lambda_{bypass} \cdot r_{bypass} + \lambda_{syntax} \cdot r_{syntax}$$

Khởi đầu: $\lambda_D = 0.3$, $\lambda_{bypass} = 0.5$, $\lambda_{syntax} = 0.2$.

**Reward sparse**: chỉ tại terminal state. MC rollout là cách credit-assign về intermediate tokens.

### 4.5 MLE pre-training

$$\mathcal{L}_{MLE} = -\sum_{(\mathbf{x}^*, t)} \log \pi_\theta(x_t^* | x_{<t}^*)$$

Teacher forcing với ground-truth tokens. Sau pretrain, áp dụng **Scheduled Sampling**: probability $\epsilon(s)$ thay GT bằng $\hat{x}_{t-1}$ (own prediction), tăng tuyến tính 0 → 1 trong 5k steps.

### 4.6 Discriminator (WGAN-GP)

$$\mathcal{L}_D = \mathbb{E}_{x \sim p_{data}}[D(x)] - \mathbb{E}_{\tilde{x} \sim G}[D(\tilde{x})] + \lambda_{gp} \mathbb{E}[(\|\nabla_{\hat{x}} D\|_2 - 1)^2]$$

D:G ratio = 5:1 (D update 5 lần per G update).

### 4.7 Phép toán nền tảng

- Markov Decision Process (MDP) formulation.
- Policy gradient theorem + likelihood ratio trick: $\nabla_\theta \pi_\theta(a|s) = \pi_\theta(a|s) \nabla_\theta \log \pi_\theta(a|s)$.
- Monte Carlo estimation, unbiased estimator, variance reduction.
- Bellman equation (cho value function).
- Wasserstein distance + Lipschitz constraint (WGAN-GP).

---

## 5. Why this NOT that?

### 5.1 VS VAE-GAN

| Aspect | SeqGAN | VAE-GAN |
|---|---|---|
| Discrete handling | REINFORCE (gradient không cần qua argmax) | Gumbel-Softmax (continuous relaxation) |
| External reward signal | ✅ WAF + parser | ❌ Chỉ D + recon |
| Latent space | ❌ | ✅ z ∈ R²⁵⁶ |
| Optimize trực tiếp ASR | ✅ Direct | ❌ Indirect |
| Training variance | High (REINFORCE) | Trung bình |
| Speed | Chậm (MC rollout K=16) | Nhanh hơn |

**Khi ưu tiên SeqGAN**: cần optimize ASR trực tiếp, có WAF Oracle/parser sẵn sàng, chấp nhận training chậm.

### 5.2 VS Gumbel-Softmax

| Aspect | SeqGAN | Gumbel-Softmax |
|---|---|---|
| Discrete handling | REINFORCE | Continuous relaxation |
| Reward không-differentiable | ✅ Dùng được | ❌ Không trực tiếp |
| Gradient stability | Low (high variance) | High (stable) |
| Training speed | Chậm | Nhanh |
| Benchmark cleanness | Khó so sánh fair | Dễ so sánh fair |

**Khi ưu tiên SeqGAN**: cần exploit external reward (WAF), không quan tâm đến benchmark cleanliness.

### 5.3 Tóm tắt: SeqGAN tỏa sáng khi

1. Có **WAF Oracle/SQL parser sẵn sàng** để dùng làm reward.
2. Cần **direct ASR optimization** (real-world deployment).
3. Chấp nhận **training instability + slow** trade-off.

---

## 6. Limitations

### 6.1 High-variance gradient (REINFORCE)

REINFORCE notoriously unstable do variance cao của gradient estimator.

**Mitigation trong dự án**:
- Baseline function $b(s_t)$ giảm variance (advantage = Q - b).
- MC rollout K=16 (compromise giữa precision và compute).
- Gradient clipping (||∇|| ≤ 1.0).

### 6.2 Sparse reward

Reward chỉ tại terminal → khó credit-assign cho intermediate tokens. MC rollout giải quyết một phần nhưng compute đắt: K=16 rollouts × seq length = $O(K \cdot L)$ extra forward passes per step.

**Mitigation**: 
- Reward shaping: thêm $r_{syntax}$ dày hơn (parse partial sequence khi có thể).
- Curriculum learning: bắt đầu với sequence ngắn.

### 6.3 Exposure bias từ MLE pretrain

Model train với GT tokens, RL phase với own predictions → distribution shift.

**Mitigation**: Scheduled Sampling (gradually thay GT bằng prediction trong pretrain).

### 6.4 Reward hacking

G có thể sinh payload trivial bypass parser nhưng không thực hiện attack:
- Empty/short string parse được.
- Comment-only payload: `--`.

**Mitigation**: 
- Add length penalty.
- Add semantic check (effects on database — hard to implement without execution).
- Add penalty cho payload < min_attack_length.

### 6.5 Slow training

MC rollout là bottleneck. Mỗi step cần $T \cdot K$ extra forward passes. Với $T=80, K=16$ → 1280 extra forwards per step.

**Mitigation**:
- Reduce K khi training stable (K=8, K=4).
- Batch rollouts together.
- Cache hidden states.

### 6.6 WAF overfitting (generalization issue)

Model học bypass **specific WAF ruleset** (ModSecurity CRS default), KHÔNG generalize sang WAF khác.

**Mitigation**:
- Train với multi-WAF reward (ModSec CRS + paranoia 3 + Cloudflare-like).
- Test với held-out WAF (vd Cloudflare emulation, không tham gia training).
- Document explicitly trong paper limitations.

### 6.7 Mode collapse

GAN bệnh chung. SeqGAN có thể collapse vào "vài payload bypass dễ".

**Detection**: variance batch, self-BLEU.
**Mitigation**: dropout, noise inject, diversity bonus trong reward.

---

## 7. Quick-start tái kích hoạt

```powershell
# 1. Vào project root
cd C:\Users\Admin\Documents\GAN

# 2. Tạo & activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Cài deps
pip install torch transformers numpy pandas sqlparse pyyaml tqdm tensorboard docker

# 4. Verify dataset
python -c "import os; print(len(os.listdir('Asset/Data/results')))"

# 5. Vào folder approach
cd SeqGAN_SQLi
mkdir data, src, configs, baselines, waf_eval, checkpoints

# 6. Build ModSecurity Docker (cho reward oracle)
# waf_eval/Dockerfile.modsec → docker build -t sqli-modsec ./waf_eval

# 7. Implement tokenizer + full de-lex
# src/tokenizer.py, data/prepare_seqgan_data.py

# 8. Extract expert demos
# data/extract_expert_demos.py: chạy WAF Oracle trên train set, save bypass payloads

# 9. Implement Generator policy + Discriminator stubs
# src/generator.py (LSTM hoặc Transformer Decoder)
# src/discriminator.py (1D-CNN)

# 10. SQLiEnv + Reward
# src/env.py: step(action), reset, render
# src/reward.py: combine syntax + bypass

# 11. MLE pre-training
python pretrain_mle.py --config configs/seqgan_default.yaml --epochs 10

# 12. Adversarial RL loop
python train_adversarial.py --config configs/seqgan_default.yaml --resume checkpoints/mle_best.pt
```

---

## 8. Đặc thù approach: Kiến trúc & Dataset transformation

### 8.1 Kiến trúc tổng thể

```
                        ┌──────────────────────────┐
                        │   Generator π_θ          │
                        │   LSTM 3-layer hidden=512 │  →  π(a_t | s_t) over V
              s_t →     │   hoặc Transformer Dec    │
                        │   Output: vocab logits    │
                        └──────────────────────────┘
                                    ↓ sample a_t (multinomial)
                             s_{t+1} = s_t ⊕ a_t
                                    ↓
                        ┌──────────────────────────┐
                        │   SQLiEnv                │
                        │   step(a_t)              │
                        │   if EOS: compute reward │
                        └──────────────────────────┘
                                    ↓
                        ┌──────────────────────────┐  ┌────────────────┐
                        │   Reward Oracle          │  │  Discriminator │
                        │   syntax (sqlparse)      │  │  D_φ           │
                        │   bypass (ModSecurity)   │  │  1D-CNN        │
                        └──────────────────────────┘  └────────────────┘
                                    ↓                        ↓
                              r_total = λ_D·D + λ_b·r_b + λ_s·r_s
                                    ↓
                        ┌──────────────────────────┐
                        │   MC Rollout + Baseline  │
                        │   Q(s,a) - b(s) = A(s,a) │
                        └──────────────────────────┘
                                    ↓
                        REINFORCE update for π_θ
```

### 8.2 Dataset transformation cho SeqGAN

**Input**: `Asset/Data/master_sqli.csv` (sau merge).

**Khác VAE-GAN**: dùng **full de-lexicalization** — thay TẤT CẢ tên cụ thể (kể cả keywords có thể không chuyên về attack):
- Mục đích: giảm variance không liên quan trong policy gradient.
- `payload_delex` cột (từ master_unlabeled) đã có sẵn → re-use trực tiếp.

**Splits**:
- Train: 70% (~29k payloads).
- Val: 15% (~6k).
- Test (frozen): 15% (~6k).

**Expert Demonstrations** (đặc trưng SeqGAN):
- Chạy `waf_eval/modsec_runner.py` trên train set.
- Tag payload nào bypass ModSecurity default → save thành `data/expert_demos.csv`.
- Estimated size: ~5-10% của train (~1500-3000 payloads).
- Dùng cho MLE pretrain với upweight (weight 2-3× so với non-expert).

**Vocabulary**: tương tự VAE-GAN nhưng có thể gọn hơn do full de-lex (~150 tokens).

### 8.3 SQLiEnv interface

```python
class SQLiEnv:
    def reset(self) -> State:
        """Trả về initial state s_0 = (<SOS>,)."""
        ...
    
    def step(self, action: int) -> Tuple[State, float, bool]:
        """Append action vào state. Return (next_state, reward, done).
        Reward: 0 cho intermediate; tại done (EOS hoặc max_len): tính reward."""
        ...
    
    def compute_reward(self, sequence: List[int]) -> Dict[str, float]:
        """Decode sequence → string. Return {syntax: 0/1, bypass: 0/1, total}."""
        ...
```

### 8.4 Generator architecture choice

**Option A — LSTM** (recommended cho sequence dài + memory):
```python
class GeneratorLSTM(nn.Module):
    def __init__(self, vocab_size, embed_dim=256, hidden_dim=512, num_layers=3, dropout=0.2):
        ...
    def forward(self, input_ids, hidden=None):
        # Returns logits (B, T, V), hidden
        ...
```

**Option B — Transformer Decoder** (recommended cho parallel pretraining):
```python
class GeneratorTransformer(nn.Module):
    def __init__(self, vocab_size, d_model=256, n_heads=8, n_layers=6):
        ...
```

→ Khuyến nghị start với **LSTM** (simpler, less memory) → switch Transformer nếu hiệu quả.

### 8.5 Discriminator

```python
class DiscriminatorCNN(nn.Module):
    def __init__(self, vocab_size, embed_dim=128, kernel_sizes=[3,4,5], num_filters=128):
        ...
    def forward(self, input_ids):
        # Returns score (B,)
        ...
```

---

## 9. Hyperparameters tham chiếu nhanh

| Hyperparameter | Khởi đầu | Khoảng tune | Notes |
|---|---|---|---|
| **Generator type** | LSTM | LSTM/Transformer | LSTM đơn giản hơn |
| **G hidden dim** | 512 | 256-1024 | |
| **G num layers** | 3 | 2-6 | |
| **G dropout** | 0.2 | 0.1-0.4 | |
| **D kernel sizes** | [3,4,5] | TextCNN style | |
| **D filters per kernel** | 128 | 64-256 | |
| **MLE pretrain epochs** | 10 | 5-30 | Đến validation perplexity converge |
| **MLE LR** | 1e-3 | | |
| **Scheduled Sampling ramp** | 0→1 trong 5k steps | | linear |
| **K (MC rollout)** | 16 | 4-32 | Trade-off precision vs compute |
| **α (bypass vs syntax)** | 0.7 | 0.5-0.9 | $r = \alpha r_{bypass} + (1-\alpha) r_{syntax}$ |
| **λ_D, λ_bypass, λ_syntax** | 0.3, 0.5, 0.2 | | reward shaping |
| **Baseline EMA** | 0.95 | | |
| **D:G ratio** | 5:1 | | WGAN-GP |
| **WGAN-GP λ** | 10 | | |
| **Adversarial G LR** | 1e-4 | | |
| **Adversarial D LR** | 1e-4 | | |
| **Optimizer** | Adam β=(0.5, 0.999) | | |
| **Gradient clip** | 1.0 | | Cho REINFORCE stability |
| **Batch size** | 64 | 32-128 | |
| **Total adversarial steps** | 50k | 30k-200k | |

---

## 10. Đánh giá: Metrics & Baselines

### 10.1 Primary — Attack Success Rate (ASR)

$$\text{ASR} = \frac{\#\{x : \text{bypass ModSecurity CRS default}\}}{1000}$$

Trên 1000 sample sinh ra. Ghi rõ **version ruleset** dùng (CRS 4.0.0 vs 3.x).

**Per-type ASR**: report riêng cho mỗi attack type (UNION, Boolean, Time, ...) khi có `<CLASS>` token guide generation hoặc post-classify.

**Threshold**: target ASR > Pure MLE baseline + 30%.

### 10.2 Syntax Validity Rate

Parse 1000 samples bằng `sqlparse`. Threshold: > 90%.

Nếu < 90%: ASR không có ý nghĩa (payload invalid không thể attack).

### 10.3 Self-BLEU (diversity)

n-gram order N=3. Score thấp = đa dạng cao. So sánh với Self-BLEU của dataset gốc.

### 10.4 Reward Convergence

Plot mean reward per epoch. Nếu plateau sớm và ASR thấp → model học "giống SQL" chứ không "bypass".

### 10.5 Baselines (bắt buộc cho paper)

1. **Template-based**: chèn ngẫu nhiên vào template cố định.
2. **Pure MLE LM**: chỉ pretrain, không adversarial.
3. **SeqGAN vanilla**: không có advantage estimation, không reward shaping.
4. **SeqGAN + advantage** (SeqGAN của dự án này): full implementation.

→ Mỗi baseline phải report cùng metrics: ASR, validity, Self-BLEU, reward convergence.

### 10.6 Statistical rigor

- Bootstrap CI (n=10,000) cho ASR.
- Mean ± std trên ≥ 3 random seeds.
- Significance testing với p-value.

---

## 11. Cấu trúc thư mục đề xuất

```
SeqGAN_SQLi/
├── Guiding.md                    ← FILE NÀY
├── README.md
├── requirements.txt
├── data/
│   ├── prepare_seqgan_data.py    ← read master_sqli → full de-lex → split
│   ├── extract_expert_demos.py   ← chạy WAF Oracle, tag bypass payloads
│   ├── tokenizer_vocab.json
│   ├── train.csv
│   ├── val.csv
│   ├── test.csv                  ← Frozen
│   └── expert_demos.csv          ← Subset đã bypass WAF
├── src/
│   ├── tokenizer.py              ← SQL-aware
│   ├── generator.py              ← LSTM/Transformer policy π_θ
│   ├── discriminator.py          ← 1D-CNN
│   ├── env.py                    ← SQLiEnv: step, reset, compute_reward
│   ├── reward.py                 ← Syntax + WAF + reward shaping
│   ├── rollout.py                ← Monte Carlo Q(s,a) estimate
│   ├── baseline.py               ← Value baseline b(s) network
│   ├── losses.py                 ← REINFORCE + WGAN-GP
│   ├── scheduled_sampling.py
│   └── utils.py
├── configs/
│   ├── seqgan_default.yaml
│   └── seqgan_ablation.yaml
├── baselines/
│   ├── template_based.py         ← Random template fill
│   ├── mle_lm_only.py            ← Pure MLE
│   └── seqgan_vanilla.py         ← Without advantage
├── waf_eval/
│   ├── modsec_runner.py          ← Docker ModSecurity wrapper
│   ├── Dockerfile.modsec
│   └── docker-compose.yml
├── pretrain_mle.py               ← MLE + Scheduled Sampling
├── train_adversarial.py          ← REINFORCE loop
├── evaluate.py                   ← ASR + validity + Self-BLEU
├── generate.py                   ← Inference
├── scripts/
│   ├── run_pretrain.sh
│   ├── run_adversarial.sh
│   └── run_eval.sh
└── checkpoints/
```

---

## 12. Vị trí dữ liệu, tài liệu, code đã có

### 12.1 Dữ liệu

- Master input: `C:\Users\Admin\Documents\GAN\Asset\Guiding\master_unlabeled.csv` — đã có cột `payload_delex` sẵn (full de-lex).
- Result batches: `C:\Users\Admin\Documents\GAN\Asset\Data\results\result_batch_*.csv`.
- Master labeled (sau merge): `C:\Users\Admin\Documents\GAN\Asset\Data\master_sqli.csv` (verify đã merge chưa).

### 12.2 Tài liệu tham chiếu

- `Asset/Guiding/SQLi-SeqGAN-Roadmap.md` — Roadmap đầy đủ 6 giai đoạn.
- `Asset/Guiding/Data_Engineering_Recap.md` — Pipeline data.
- `Asset/Guiding/AI_Foundations_For_Team_02_CNN_RNN_Sequences.md` — LSTM (cho Generator).
- `Asset/Guiding/AI_Foundations_For_Team_04_Generative_Models.md` — GAN, SeqGAN biến thể.
- `Asset/Guiding/Onboarding_AI_Knowledge_*.md` — bản đơn giản (nếu cần ôn lại).

### 12.3 Code re-use

- `data_engine/normalizer.py` — chuẩn hóa text.
- `data_engine/merge.py` — merge results.

---

## 13. Checklist trước khi start serious

- [ ] Dataset merge → master_sqli.csv (verify).
- [ ] Train/val/test split với seed cố định.
- [ ] Vocabulary frozen.
- [ ] Tokenizer round-trip identity test.
- [ ] ModSecurity Docker build OK.
- [ ] WAF Oracle smoke test: 10 known-bypass payloads → reward = 1.
- [ ] Expert demos extracted (~5-10% train set).
- [ ] Generator forward pass shape OK.
- [ ] Discriminator forward pass shape OK.
- [ ] SQLiEnv interface match gym-like spec.
- [ ] Smoke MLE pretrain 100 steps → loss giảm.
- [ ] Smoke RL phase 100 steps → no NaN.
- [ ] Logging: G loss, D loss, mean reward, ASR (val), validity rate, ||grad_G||.

---

## 14. Mẹo & "khi gặp vấn đề thì làm gì"

| Triệu chứng | Nguyên nhân | Hành động |
|---|---|---|
| MLE loss không giảm | LR/architecture | Tune LR, tăng capacity G |
| RL phase divergence | Variance gradient | Tăng baseline weight, K=24-32 |
| Reward plateau, ASR thấp | Reward hacking | Add length penalty, semantic check |
| Mode collapse | G converge 1 mode | Tăng dropout, diversity bonus |
| ASR cao nhưng validity thấp | G learn bypass tricks không SQL hợp lệ | Tăng λ_syntax |
| Validity cao nhưng ASR ngang baseline | G học MLE distribution | Tăng λ_bypass, train RL phase lâu hơn |
| WAF Oracle quá chậm | Docker overhead | Batch payloads, parallel containers |
| OOM với MC rollout | K quá lớn | Giảm K, hoặc gradient checkpointing |

---

## 15. Bước tiếp theo (sau train + eval)

1. **Multi-WAF training**: train với 3 WAF rewards (ModSec default + paranoia 3 + Cloudflare-like).
2. **Conditional generation**: G(z, attack_type).
3. **Compare on frozen test set** với VAE-GAN, Gumbel-Softmax (cùng test set, cùng vocab, cùng L).
4. **Paper writing**.

---

*File này là "self-contained reactivation guide" cho nhánh SeqGAN. Chi tiết paper-level: `Asset/Guiding/SQLi-SeqGAN-Roadmap.md`.*
