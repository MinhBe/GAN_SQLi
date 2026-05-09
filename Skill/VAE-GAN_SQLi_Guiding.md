# Guiding — VAE-GAN SQLi (Latent Hybrid Approach)

> **Đối tượng đọc**: Bản thân nghiên cứu sinh khi tái kích hoạt nhánh VAE-GAN sau gián đoạn dài. Tự chứa, không cần mở Roadmap gốc — nhưng nếu cần chi tiết về Constraint Density & các experiments, vẫn nên tham chiếu `Asset/Guiding/SQLi-VAE-GAN-Roadmap.md`.
>
> **Phong cách**: technical thẳng, không 4 tầng (giả định đọc giả đã đọc các file Foundations).

> **Cập nhật**: 2026-05-04
> **Trạng thái implementation**: ❌ Folder rỗng — chưa code dòng nào.

---

## Mục lục

1. [Mở đầu & Mục tiêu approach](#1-mở-đầu--mục-tiêu-approach)
2. [Trạng thái hiện tại & Bắt đầu lại từ đâu](#2-trạng-thái-hiện-tại)
3. [Why this approach? — Lý do tồn tại](#3-why-this-approach)
4. [Cơ sở toán học](#4-cơ-sở-toán-học)
5. [Why this NOT that — So sánh với SeqGAN & Gumbel-Softmax](#5-why-this-not-that)
6. [Limitations / Nhược điểm](#6-limitations)
7. [Quick-start tái kích hoạt (10 bước)](#7-quick-start)
8. [Đặc thù approach: Kiến trúc & Dataset transformation](#8-đặc-thù-approach)
9. [Hyperparameters tham chiếu nhanh](#9-hyperparameters)
10. [Đánh giá: Metrics & Baselines](#10-đánh-giá)
11. [Cấu trúc thư mục đề xuất](#11-cấu-trúc-thư-mục)
12. [Vị trí dữ liệu, tài liệu, code đã có](#12-vị-trí-dữ-liệu)

---

## 1. Mở đầu & Mục tiêu approach

**Bài toán chung của dự án**: Sinh chuỗi token $s \in \mathcal{S}$ thỏa mãn ràng buộc cứng $\mathcal{C}$ (cú pháp SQL hợp lệ) và tối đa hóa objective $f(s)$ (WAF evasion rate). Đây là **Constrained Discrete Sequence Generation (CDSG)**, không phải open-ended text generation.

**VAE-GAN approach** = giải quyết bài toán bằng kiến trúc **hybrid Latent**: kết hợp VAE (cho structured latent space) với GAN (cho output sắc nét, realistic). Mục tiêu chính: chứng minh được latent space tách biệt được **"SQL thuần túy"** vs **"SQL ngụy trang/obfuscated"** → có thể control kiểu attack qua latent vector $z$.

**Core Claim của paper VAE-GAN**: Khi *Constraint Density* $\delta$ (tỉ lệ token phải conform to grammar) cao, baseline có cấu trúc (n-gram LM + mutation) đạt WAF Evasion Rate cạnh tranh với VAE-GAN — với chi phí tính toán thấp hơn nhiều. Thí nghiệm này nhằm **demonstrate trade-off**, không phải prove VAE-GAN luôn tốt nhất.

**Đặc trưng phân biệt với 2 approach kia**:
- VAE-GAN có **encoder** (Transformer) → tận dụng được thông tin từ payload thật để build latent space.
- VAE-GAN có **structured latent z ∈ R²⁵⁶** → control được kiểu attack qua z (interpolation, conditional generation).
- VAE-GAN có **4 loss components** → phức tạp nhất trong 3 approach.

---

## 2. Trạng thái hiện tại

**Cập nhật 2026-05-04**:

| Stage | Status | Notes |
|---|---|---|
| Data engineering | ✅ Done (xem `Asset/Guiding/Data_Engineering_Recap.md`) | 41,460 payloads classified |
| Roadmap kỹ thuật | ✅ Done (`Asset/Guiding/SQLi-VAE-GAN-Roadmap.md`) | 6 giai đoạn chi tiết |
| Dataset transformation cho VAE-GAN | ❌ Cần làm | Partial de-lex, vocab construction |
| Tokenizer code | ❌ Chưa có | SQL-aware regex-based |
| Encoder Transformer | ❌ Chưa có | |
| Decoder Transformer + Gumbel-Softmax | ❌ Chưa có | |
| Discriminator 1D-CNN | ❌ Chưa có | |
| Loss combiner (recon + KL + adv + fm) | ❌ Chưa có | |
| Training loop với warm-up phase | ❌ Chưa có | |
| WAF evaluation harness | ❌ Chưa có | Cần Docker ModSecurity |
| Reproducibility package | ❌ Chưa có | |

**Bắt đầu lại từ đâu (priority order)**:
1. **Verify dataset**: chạy `Asset/Opencode/check_duplicates_v2.py` trên `Asset/Data/results/` xem còn duplicate.
2. **Merge → master_sqli.csv**: chạy `data_engine/merge.py` (hoặc viết script merge nếu chưa).
3. **Tạo `data/prepare_vae_data.py`**: read master_sqli.csv → partial de-lex → split train/val/test → save.
4. **Implement tokenizer + vocab**: `src/tokenizer.py` với SQL-aware regex.
5. **Implement encoder + decoder + discriminator** stub trước, smoke test với small batch.
6. **Implement loss combiner**: recon + KL (with annealing + free bits) + adversarial (WGAN-GP) + feature matching.
7. **Warm-up phase training**: VAE alone (no D) → check KL ∈ [5, 50] nats và recon accuracy ≥ 70%.
8. **Adversarial phase**: thêm D, train với D:G = 5:1.
9. **Evaluation**: WER + validity + diversity.
10. **Reproducibility package**.

---

## 3. Why this approach?

### 3.1 Vấn đề gốc

Bài toán sinh SQL injection đối mặt với:

1. **Discrete output**: token sequence rời rạc → argmax không differentiable → vanilla GAN không train được trực tiếp.
2. **Hard grammar constraints**: SQL phải parse được — không thể coi là "free text generation".
3. **Hai lớp distribution chồng chéo**: SQL hợp lệ (large) ⊃ SQLi payload (small subset). Discriminator cần học phân biệt SQLi vs benign SQL, KHÔNG chỉ phân biệt "SQL vs random".
4. **Obfuscation diversity**: payload thật có nhiều biến thể bề mặt (URL encoding, case variation, hex string) cho cùng pattern logic.

### 3.2 Tại sao VAE-GAN giải quyết tốt?

- **Encoder cho structured latent**: VAE encoder học map payload → distribution Gaussian trong $\mathbb{R}^{256}$. Nhờ KL regularization, latent space "smooth" → có thể interpolate giữa 2 payload, sample neighborhoods, control attribute qua dimension.
- **Decoder cho generation**: VAE decoder + GAN discriminator song song. Decoder học không chỉ reconstruct (recon loss) mà còn fool D (adversarial loss) → output realistic + diverse.
- **Tách biệt "thuần" vs "ngụy trang"**: Hypothesis chính — encoder mapping `payload_norm` (SQL thuần) và `payload_raw` (có obfuscation) sẽ produce latent z khác nhau (potentially separable clusters trong z space). Nếu đúng → có thể generate "ngụy trang version" của một payload thuần bằng cách add noise vào z hợp lý.
- **Gumbel-Softmax cho discrete sampling**: bypass argmax non-differentiable bằng continuous relaxation. Choice trong roadmap: "Gumbel-Softmax cho giai đoạn đầu vì ổn định hơn REINFORCE" (xem so sánh ở mục 5).

### 3.3 Cơ sở khoa học / intuition

- **VAE structure ⇒ smooth manifold learning**: chuẩn ML, hoạt động tốt cho image (ELBO + reparameterization trick).
- **GAN augmentation ⇒ sharp realistic output**: VAE alone bị blur (do KL pull về N(0,I)), GAN component sửa được điều này.
- **Hybrid VAE-GAN ⇒ best of both worlds**: structured latent + realistic output. Đã được chứng minh trên image (Larsen et al. 2016, "Autoencoding Beyond Pixels Using a Learned Similarity Metric"). VAE-GAN cho text discrete là extension của ý tưởng này.

---

## 4. Cơ sở toán học

### 4.1 Total loss

$$\mathcal{L}_{total} = \mathcal{L}_{recon} + \beta \cdot \mathcal{L}_{KL} + \lambda \cdot \mathcal{L}_{adv} + \gamma \cdot \mathcal{L}_{fm}$$

Khởi đầu: $\beta = 1.0$ (sau KL annealing), $\lambda = 0.1$, $\gamma = 10.0$.

### 4.2 Reconstruction loss

$$\mathcal{L}_{recon} = -\sum_{t=1}^L \log p_\theta(y_t^* | y_{<t}^*, z)$$

(autoregressive cross-entropy, teacher forcing với ground-truth tokens $y^*$)

### 4.3 KL divergence (encoder vs prior)

$$\mathcal{L}_{KL} = KL[q_\phi(z|x) \| p(z)] = KL[\mathcal{N}(\mu_\phi, \sigma_\phi^2) \| \mathcal{N}(0, I)]$$

Closed-form Gaussian:
$$\mathcal{L}_{KL} = \frac{1}{2} \sum_i (\mu_i^2 + \sigma_i^2 - \log \sigma_i^2 - 1)$$

**KL annealing**: $\beta(t) = \min(1, t / T_{anneal})$ với $T_{anneal} = 10000$ steps.

**Free bits** (chống posterior collapse): $\mathcal{L}_{KL}^{fb} = \sum_i \max(KL_i, \lambda_{fb})$ với $\lambda_{fb} = 2$ nats per dimension.

### 4.4 Reparameterization trick

$$z = \mu_\phi(x) + \sigma_\phi(x) \odot \epsilon, \quad \epsilon \sim \mathcal{N}(0, I)$$

→ gradient flow qua $\mu_\phi, \sigma_\phi$ (deterministic transform của $\epsilon$).

### 4.5 Adversarial loss (WGAN-GP)

**Discriminator (Critic)** loss:
$$\mathcal{L}_D = \mathbb{E}_{x \sim p_{data}}[D(x)] - \mathbb{E}_{\tilde{x} \sim p_g}[D(\tilde{x})] + \lambda_{gp} \mathbb{E}_{\hat{x}}[(\|\nabla_{\hat{x}} D(\hat{x})\|_2 - 1)^2]$$

với $\hat{x} = \epsilon x + (1-\epsilon)\tilde{x}$, $\epsilon \sim U(0,1)$, $\lambda_{gp} = 10$.

**Generator** loss (adversarial part):
$$\mathcal{L}_{adv} = -\mathbb{E}_{z}[D(G(z))]$$

### 4.6 Feature Matching loss

$$\mathcal{L}_{fm} = \| \mathbb{E}_{x \sim p_{data}}[f(x)] - \mathbb{E}_{z}[f(G(z))] \|_2^2$$

với $f$ = output từ layer $L-2$ của Discriminator (penultimate intermediate).

### 4.7 Gumbel-Softmax (cho discrete sampling)

$$y_i = \frac{\exp((\log \pi_i + g_i)/\tau)}{\sum_j \exp((\log \pi_j + g_j)/\tau)}, \quad g_i = -\log(-\log U_i), \quad U_i \sim U(0,1)$$

Temperature schedule: $\tau: 1.0 \to 0.1$, exponential decay.

### 4.8 Phép toán nền tảng

- Variational inference + ELBO derivation.
- KL divergence (asymmetric, Gibbs' inequality, closed-form Gaussian).
- Gradient flow qua reparameterization & continuous relaxation.
- Wasserstein-1 distance + Kantorovich-Rubinstein duality + Lipschitz continuity.
- Gumbel distribution (extreme value theory).

---

## 5. Why this NOT that?

### 5.1 VS SeqGAN

| Aspect | VAE-GAN | SeqGAN |
|---|---|---|
| Discrete handling | Gumbel-Softmax (continuous relaxation) | REINFORCE (policy gradient) |
| External reward signal | ❌ Chỉ dùng D + recon | ✅ Dùng được WAF Oracle, parser |
| Latent space | ✅ Structured z ∈ R²⁵⁶ | ❌ Không có encoder |
| Training stability | Trung bình (4 loss → tinh tế) | Thấp hơn (high-variance gradient) |
| Speed | Nhanh hơn (no MC rollout) | Chậm hơn (MC rollout K=16 per step) |
| Optimize trực tiếp ASR | ❌ Indirect qua D | ✅ Trực tiếp |

**Khi nào ưu tiên VAE-GAN over SeqGAN**: cần control kiểu attack qua latent (vd "sinh union_based attack với obfuscation cao"); cần training nhanh; chấp nhận indirect ASR optimization.

### 5.2 VS Gumbel-Softmax (pure)

| Aspect | VAE-GAN | Gumbel-Softmax pure |
|---|---|---|
| Encoder | ✅ Transformer encoder | ❌ Không có |
| Latent input cho G | $z$ từ $q(z|x)$ encoder | $z$ random từ prior |
| Loss components | 4 (recon + KL + adv + fm) | 2 (WGAN-GP cho G + D) |
| Tận dụng payload thật | ✅ Encoder learns from x | ❌ Chỉ qua D |
| Training complexity | Cao | Thấp |
| Reconstruction capability | ✅ Có thể encode → decode | ❌ Không thể |
| Latent walk meaningful | ✅ Có | Không có structured walk |

**Khi nào ưu tiên VAE-GAN over Gumbel-Softmax**: cần encode payload thật vào latent (vd phục vụ analysis, anomaly detection, transfer); cần latent walk experiment.

### 5.3 Tóm tắt: VAE-GAN tỏa sáng khi

1. Cần **structured latent** (control, interpolate, anomaly detect).
2. Có thể chấp nhận **complexity cao** (4 loss components).
3. Không cần **direct WAF reward optimization** (vì không có WAF Oracle differentiable).

---

## 6. Limitations

### 6.1 Posterior collapse

KL → 0, encoder ignored → latent vô dụng. Decoder mạnh → có thể chỉ dùng autoregressive structure, ignore $z$.

**Mitigation trong dự án**:
- KL annealing: β tăng dần 0 → 1 trong 10k steps đầu.
- Free bits: $\lambda_{fb} = 2$ nats per dimension.
- Monitor: KL phải ∈ [5, 50] nats sau warm-up. Nếu KL < 5: tăng $\lambda_{fb}$.

### 6.2 β tuning sensitivity

$\beta$ quá lớn → posterior collapse. Quá nhỏ → latent không đủ regularize, prior matching kém.

**Mitigation**: ablation study với β ∈ {0.5, 1.0, 2.0, 4.0} trên validation. Pick β tốt nhất.

### 6.3 Training 2-stage phức tạp

Warm-up phase (VAE only) → adversarial phase (add D). Transition tinh tế:
- Quá sớm add D: VAE chưa hội tụ, D dominate → mode collapse.
- Quá muộn: lãng phí compute.

**Acceptance criteria** trước khi add D:
- Recon accuracy ≥ 70% trên validation.
- KL ∈ [5, 50] nats.
- Gradient norm stable.

### 6.4 Discrete sampling khó

Gumbel-Softmax temperature $\tau$ schedule sensitive:
- $\tau$ cao (gần 1.0): output soft, không discrete enough → D distinguishable artifacts.
- $\tau$ thấp (gần 0.1): output discrete nhưng gradient vanish.

**Mitigation**: exponential decay $\tau$ qua 5000 steps. Monitor $\|\nabla G\|$.

### 6.5 Inference chậm hơn pure GAN

VAE-GAN cần encoder + decoder, pure GAN chỉ G. Inference time: ~2× pure GAN.

**Mitigation**: tại deploy, có thể dùng decoder only (sample $z \sim N(0,I)$, không dùng encoder).

### 6.6 Interaction giữa các loss components

4 loss với weights cân bằng → tradeoff vô tận. Khi one loss dominates: model degenerate.

**Mitigation trong roadmap**:
- "Monitor gradient norm của G liên tục — nếu gradient norm của G đột ngột tăng > 10x: dừng, kiểm tra balance giữa $\lambda$ và $\gamma$."

---

## 7. Quick-start tái kích hoạt (10 bước)

```powershell
# Bước 1: Vào project root
cd C:\Users\Admin\Documents\GAN

# Bước 2: Tạo virtualenv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Bước 3: Cài dependencies (xem requirements.txt khi tạo)
pip install torch transformers numpy pandas scipy sqlparse pyyaml tqdm tensorboard

# Bước 4: Verify dataset
python -c "import pandas as pd; df = pd.read_csv('Asset/Guiding/master_unlabeled.csv'); print(df.shape, df.columns.tolist())"
# Kỳ vọng: (41460, 7), cols ['payload_raw', 'payload_norm', 'payload_delex', 'label', 'is_obfuscated', 'sqli_type_hint', 'source']

# Bước 5: Verify result_batch_*.csv merged
python -c "import os; print(len([f for f in os.listdir('Asset/Data/results') if f.startswith('result_batch')]))"
# Kỳ vọng: 1382

# Bước 6: Vào folder approach + tạo skeleton
cd VAE-GAN_SQLi
mkdir data, src, configs, waf_eval, checkpoints

# Bước 7: Implement tokenizer (file đầu tiên)
# Tạo src/tokenizer.py với SQL-aware regex
# Test: tokenize 5 sample, check output reasonable

# Bước 8: Implement prepare_vae_data.py
# data/prepare_vae_data.py: read master_sqli.csv → partial de-lex → split 70/15/15 → save train.csv, val.csv, test.csv

# Bước 9: Implement encoder + decoder + discriminator stubs
# src/encoder.py, decoder.py, discriminator.py — chỉ skeleton, forward pass với random output
# Smoke test: x → encoder → z → decoder → x_recon (đúng shape)

# Bước 10: Smoke train loop
# train.py với 1 epoch, batch_size=4 trên 100 samples → check loss giảm, không NaN
python train.py --config configs/vae_gan_default.yaml --smoke-test
```

Khi smoke test pass: tiến hành full training (warm-up → adversarial → eval).

---

## 8. Đặc thù approach: Kiến trúc & Dataset transformation

### 8.1 Kiến trúc tổng thể

```
                          ┌──────────────────────┐
                          │   Encoder            │
              x →         │   Transformer        │   →  μ, log σ²
        (token IDs)       │   4-6 layers, h=8    │      ∈ R²⁵⁶
                          └──────────────────────┘
                                    ↓
                          Reparameterization:
                          z = μ + σ · ε,  ε ~ N(0,I)
                                    ↓
                          ┌──────────────────────┐
                          │   Decoder            │
              z →         │   Transformer        │   →  logits per token
                          │   4-6 layers         │
                          │   Cross-attn vào z   │
                          │   Gumbel-Softmax     │
                          └──────────────────────┘
                                    ↓
                          Output: token sequence
                                    ↓
                          ┌──────────────────────┐
                          │   Discriminator      │
                          │   1D-CNN [3,4,5]     │   →  D(x) ∈ R
                          │   + feature matching │      (penultimate L-2)
                          └──────────────────────┘
```

### 8.2 Dataset transformation cho VAE-GAN

**Input source**: `Asset/Data/master_sqli.csv` (sau merge từ 1382 result batches).

**Transformations**:

1. **Filter** label=1 (chỉ keep SQLi, không benign — VAE-GAN focus trên distribution của attacks).
2. **Filter** confidence ≥ 0.85 hoặc reviewed (loại noisy labels).
3. **Filter** sqli_type ∈ top-5 thường gặp (`union_based`, `boolean_blind`, `error_based`, `time_blind`, `lateral`) → đảm bảo có đủ samples mỗi class. Hoặc keep all + weighted loss.
4. **Tokenization**: SQL-aware regex (xem mục 8.3).
5. **Partial de-lexicalization** (đặc trưng VAE-GAN — KHÁC SeqGAN/Gumbel):
   - **Giữ nguyên**: SQL keywords (`SELECT`, `UNION`, `FROM`, `WHERE`, `OR`, `AND`, ...) + attack functions (`SLEEP`, `BENCHMARK`, `pg_sleep`, `extractvalue`, `utl_inaddr`, `xp_cmdshell`, ...) + special chars (`'`, `--`, `/*`, `;`).
   - **Thay placeholder**: tên bảng → `<TABLE>`, tên cột → `<COL>`, số literal → `<NUM>`, string literal trong dấu nháy → `<STR>`.
   - **Lý do partial**: encoder phải học structure tấn công (signal) — keyword cụ thể là signal, không phải nhiễu.
6. **Padding/truncation**: max length $L$ = percentile 95 của distribution (đo từ data, ước lượng L ≈ 60-100 tokens).
7. **Train/Val/Test split**: 70/15/15, stratified theo `sqli_type`.

### 8.3 Vocabulary

**Token types**:
- Special: `<PAD>`, `<SOS>`, `<EOS>`, `<UNK>`.
- Placeholders: `<TABLE>`, `<COL>`, `<NUM>`, `<STR>`.
- SQL keywords: ~80 (SELECT, FROM, WHERE, UNION, ALL, INSERT, ...).
- Operators: `=`, `<`, `>`, `<=`, `>=`, `!=`, `<>`, `+`, `-`, `*`, `/`, `%`.
- Special chars: `'`, `"`, `(`, `)`, `,`, `;`, `--`, `/*`, `*/`, `#`.
- Attack functions: ~50 (pg_sleep, sleep, benchmark, waitfor, extractvalue, ...).
- DB-specific (optional): version(), database(), user(), ...

Tổng vocabulary: ~200-300 tokens. Lưu thành `data/vocab.json`.

### 8.4 Loss schedule cụ thể

```python
def beta_schedule(step):
    return min(1.0, step / 10000)

def tau_schedule(step):
    tau_0 = 1.0
    tau_min = 0.1
    decay_rate = -math.log(tau_min / tau_0) / (TOTAL_STEPS * 0.8)
    return max(tau_min, tau_0 * math.exp(-decay_rate * step))

# In training loop:
for step in range(TOTAL_STEPS):
    beta = beta_schedule(step)
    tau = tau_schedule(step)
    
    # Forward
    mu, log_var = encoder(x)
    z = mu + torch.exp(0.5*log_var) * torch.randn_like(mu)
    logits = decoder(z, x_input)  # teacher forcing
    
    # Reconstruction loss (cross-entropy with teacher forcing)
    L_recon = F.cross_entropy(logits, x_target, ignore_index=PAD_ID)
    
    # KL with free bits
    kl_per_dim = -0.5 * (1 + log_var - mu**2 - log_var.exp())
    L_KL = torch.sum(torch.clamp(kl_per_dim, min=FREE_BITS))
    
    # If past warm-up, add adversarial + feature matching
    if step >= WARMUP_STEPS:
        gumbel_samples = gumbel_softmax(decoder_logits, tau)
        L_adv = -D(gumbel_samples).mean()
        L_fm = ((D.feature_layer(gumbel_samples).mean(0) - D.feature_layer(x).mean(0))**2).sum()
        L_total = L_recon + beta * L_KL + 0.1 * L_adv + 10.0 * L_fm
    else:
        L_total = L_recon + beta * L_KL
    
    L_total.backward()
    optimizer.step()
```

---

## 9. Hyperparameters tham chiếu nhanh

| Hyperparameter | Khởi đầu | Khoảng tune | Notes |
|---|---|---|---|
| **Latent dim** $d_z$ | 256 | 128-512 | Cao hơn → expressive nhưng KL khó train |
| **Encoder/Decoder layers** | 4-6 | 2-8 | Transformer |
| **Attention heads** | 8 | 4-16 | |
| **Embed dim** | 256 | 128-512 | |
| **FFN dim** | 1024 | 4× embed | |
| **β (KL weight)** | 1.0 (after anneal) | 0.5-4.0 | KL annealing 0→1 trong 10k steps |
| **Free bits** $\lambda_{fb}$ | 2 nats | 0.5-4 | Per dimension |
| **λ (adversarial)** | 0.1 | 0.01-1.0 | Khởi nhỏ để không destabilize VAE |
| **γ (feature matching)** | 10.0 | 1-50 | Cao vì feature matching loss tự nhiên nhỏ |
| **Gumbel τ** | 1.0 → 0.1 | exponential decay over 80% steps | Reset nếu gradient vanish |
| **Discriminator kernels** | [3, 4, 5] | | TextCNN |
| **D filters per kernel** | 128 | 64-256 | |
| **D:G ratio** | 5:1 | | WGAN-GP standard |
| **WGAN-GP λ** | 10 | | Standard |
| **Optimizer** | Adam β=(0.5, 0.999) | | Standard cho GAN |
| **LR (warm-up)** | 1e-3 | | VAE alone |
| **LR (adversarial G)** | 1e-4 | | |
| **LR (adversarial D)** | 4e-4 | | D nhanh hơn vì train 5× |
| **Batch size** | 64 | 32-128 | Tùy GPU |
| **Total steps** | 100k | 50k-500k | Depending dataset size |
| **Warm-up steps** | 30k | | Trước khi add D |

---

## 10. Đánh giá: Metrics & Baselines

### 10.1 Primary metric — WAF Evasion Rate (WER)

**Định nghĩa**: 
$$\text{WER} = \frac{\#\{x \in \text{samples} : x \text{ syntactically valid AND bypasses WAF}\}}{1000}$$

**Setup**:
- Sinh 1000 sample từ trained G (sample $z \sim \mathcal{N}(0,I)$ → decode → re-lexicalize nếu cần).
- Chạy qua **3 WAF targets**:
  1. ModSecurity CRS default ruleset.
  2. ModSecurity CRS paranoia level 3.
  3. Cloudflare-equivalent ruleset (open-source emulation).
- Đếm bypass (não bị WAF block) AND parse được bằng `sqlparse`.

**Threshold for success**: WER ≥ 30% trên ModSecurity default (so với template-based baseline ~5%).

### 10.2 Secondary metrics

1. **Syntax Validity Rate**:
   - Parse 1000 samples bằng `sqlparse`, đếm parse thành công.
   - Threshold: ≥ 85%. Nếu < 85%, WER không có ý nghĩa.

2. **Structural Diversity**:
   - Pairwise edit distance giữa 1000 samples.
   - Report mean ± std.
   - Self-BLEU n=3 < 0.5 (low = diverse).

3. **Constraint Density** $\delta$:
   - Đo trên output của G.
   - So sánh với $\delta$ của corpus thật.
   - Nếu output có $\delta$ thấp hơn corpus → G không học được structure.

### 10.3 Experiment 1 — Main Comparison (paper claim)

**Hypothesis**: KN-5 + Mutation baseline cạnh tranh với VAE-GAN khi $\delta$ cao.

**Methods to compare**:
- KN-5 + Mutation (Kneser-Ney 5-gram LM + grammar-aware mutation).
- Template + Random Fill (existing baseline).
- LSTM LM only.
- Pure VAE.
- VAE-GAN (full).

**Statistical rigor**: Bootstrap CI (n=10,000) cho WER. Không claim "better" nếu CI overlap.

### 10.4 Experiment 2 — δ Correlation (most important)

**Generate synthetic CDSG domains** với $\delta \in \{0.1, 0.3, 0.5, 0.7, 0.9\}$ bằng cách vary grammar strictness.

**Plot**: $\delta$ (x) vs WER gap (y) = WER_baseline - WER_VAE-GAN.

**Expected finding**: gap → 0 khi $\delta$ → 1 (high constraint).

### 10.5 Experiment 3 — Sample Efficiency

Train với {1k, 5k, 10k, 50k} samples. Plot learning curve WER vs training size.

**Expected finding**: baseline converges với < 5k; deep models cần > 10k.

---

## 11. Cấu trúc thư mục đề xuất

```
VAE-GAN_SQLi/
├── Guiding.md                    ← FILE NÀY
├── README.md                     ← Quick description, repo link
├── requirements.txt              ← torch, transformers, sqlparse, ...
├── data/
│   ├── prepare_vae_data.py       ← read master_sqli.csv → partial de-lex → split
│   ├── tokenizer_vocab.json      ← Frozen vocab sau prepare
│   ├── train.csv                 ← Output của prepare (70%)
│   ├── val.csv                   ← (15%)
│   └── test.csv                  ← Frozen (15%)
├── src/
│   ├── tokenizer.py              ← SQL-aware regex tokenizer
│   ├── encoder.py                ← Transformer encoder → (μ, log σ²)
│   ├── decoder.py                ← Transformer decoder + Gumbel-Softmax head + cross-attn
│   ├── discriminator.py          ← 1D-CNN multi-kernel + feature output L-2
│   ├── losses.py                 ← recon + KL (free bits) + adv (WGAN-GP) + feature matching
│   ├── kl_anneal.py              ← β schedule
│   ├── gumbel.py                 ← Gumbel-Softmax sampler + τ schedule
│   └── utils.py                  ← misc (seed, masks, logging)
├── configs/
│   ├── vae_gan_default.yaml      ← Hyperparams default
│   └── vae_gan_ablation.yaml     ← Cho ablation study (β, λ, γ)
├── train.py                      ← Main training: warm-up → adversarial
├── evaluate.py                   ← WER + validity + diversity
├── generate.py                   ← Sample inference từ trained model
├── waf_eval/
│   ├── modsec_runner.py          ← Docker ModSecurity wrapper
│   ├── docker-compose.yml        ← ModSec containers (default + paranoia 3)
│   └── cloudflare_emulator.py    ← Open-source CF rules emulation
├── scripts/
│   ├── run_warmup.sh             ← Warm-up phase
│   ├── run_adversarial.sh        ← Adversarial phase
│   ├── run_eval.sh               ← Eval pipeline
│   └── run_experiments.sh        ← All 3 experiments
└── checkpoints/                  ← .pt files
```

---

## 12. Vị trí dữ liệu, tài liệu, code đã có

### 12.1 Dữ liệu

- **Master input**: `C:\Users\Admin\Documents\GAN\Asset\Guiding\master_unlabeled.csv` (41,460 rows × 7 cols).
- **Result batches**: `C:\Users\Admin\Documents\GAN\Asset\Data\results\result_batch_*.csv` (1,382 file).
- **Master labeled** (sau merge): `C:\Users\Admin\Documents\GAN\Asset\Data\master_sqli.csv` (cần verify đã tạo chưa).

### 12.2 Tài liệu tham khảo

- `Asset/Guiding/SQLi-VAE-GAN-Roadmap.md` — Roadmap kỹ thuật chi tiết 6 giai đoạn (đã đọc khi viết file này, vẫn nên tham chiếu cho details).
- `Asset/Guiding/Data_Engineering_Recap.md` — Pipeline data đã làm.
- `Asset/Guiding/Data_Engineering_Foundation.md` — Concepts data engineering với 4 tầng.
- `Asset/Guiding/AI_Foundations_For_Team_01_Neural_Net_And_Training.md` — NN cơ bản.
- `Asset/Guiding/AI_Foundations_For_Team_03_Attention_And_Transformer.md` — Transformer (cho encoder/decoder).
- `Asset/Guiding/AI_Foundations_For_Team_04_Generative_Models.md` — VAE + GAN concepts (quan trọng nhất).

### 12.3 Code data engineering (re-use)

- `data_engine/normalizer.py` — chuẩn hóa text. Có thể re-use cho tokenizer pre-process.
- `data_engine/merge.py` — merge result batches.
- `Asset/Opencode/check_duplicates_v2.py` — verify dataset quality.

### 12.4 Tracking

- `Asset/Opencode/progress.json` — confirm classify đã xong: `"status": "completed", "1382/1382"`.

---

## 13. Checklist trước khi start training serious

- [ ] Dataset đã merge → master_sqli.csv (12 cols, 41,460 rows).
- [ ] Train/val/test split saved (random seed fixed).
- [ ] Vocabulary fixed và saved (vocab.json).
- [ ] Tokenizer đã smoke test (decode round-trip = identity).
- [ ] Encoder forward pass output shape đúng `(B, 256, 2)` (μ, log σ²).
- [ ] Decoder forward pass output shape đúng `(B, L, V)`.
- [ ] Discriminator forward pass output shape đúng `(B, 1)`.
- [ ] Smoke training 100 steps không NaN.
- [ ] WandB/TensorBoard logging set up cho: L_recon, L_KL, L_adv, L_fm, ||grad_G||, ||grad_D||, KL nats.
- [ ] Random seed fixed (torch + numpy).
- [ ] Docker ModSecurity build được (cho eval phase, không cần ngay).
- [ ] Initial git commit cho reproducibility.

---

## 14. Mẹo & "khi gặp vấn đề thì làm gì"

| Triệu chứng | Nguyên nhân khả dĩ | Hành động |
|---|---|---|
| Loss NaN trong warm-up | LR quá cao, init lỗi | Giảm LR, dùng He init cho ReLU layers |
| KL → 0 | Posterior collapse | Tăng $\lambda_{fb}$, giảm decoder capacity, KL anneal chậm hơn |
| KL > 100 nats | Encoder không học được prior | Giảm $\lambda_{fb}$, tăng β anneal speed |
| Recon accuracy < 50% sau 20k steps | Architecture/capacity | Tăng layers, embed dim |
| ||grad_G|| đột tăng > 10× | Adversarial imbalance | Giảm $\lambda$, kiểm tra D output range |
| Mode collapse (median edit dist < 5) | Adversarial dominate | Tăng dropout 0.1→0.3, inject noise vào z |
| WER thấp dù validity cao | G học "giống SQL" không "bypass WAF" | Add WAF reward to loss (next iteration) |
| Gumbel τ vanish gradient | τ giảm quá nhanh | Slower decay, hoặc τ floor cao hơn |

---

## 15. Bước tiếp theo (sau khi train + eval xong)

1. **Conditional generation**: extend với class condition $y$ (`sqli_type`). $G(z, y)$.
2. **Latent walk experiments**: visualize z space, walk between 2 payloads.
3. **Disentanglement analysis**: từng dim của z control attribute gì?
4. **Comparison với SeqGAN, Gumbel-Softmax** trên cùng frozen test set.
5. **Paper writing**.

---

*File này là "self-contained reactivation guide" cho nhánh VAE-GAN. Khi quay lại sau gián đoạn, đọc file này từ đầu đến cuối là đủ. Khi cần chi tiết technical về methodology paper, mở `Asset/Guiding/SQLi-VAE-GAN-Roadmap.md`.*
