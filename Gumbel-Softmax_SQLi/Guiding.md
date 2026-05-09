# Guiding — Gumbel-Softmax SQLi (Benchmark SDSG Approach)

> **Đối tượng đọc**: Bản thân nghiên cứu sinh khi tái kích hoạt nhánh Gumbel-Softmax sau gián đoạn dài. Self-contained — chi tiết paper-level: `Asset/Guiding/SQLi-Gumbel-SoftmaxGAN-Roadmap.md`.
>
> **Phong cách**: technical thẳng (giả định đã đọc `AI_Foundations_For_Team_*.md`).

> **Cập nhật**: 2026-05-04
> **Trạng thái implementation**: ❌ Folder rỗng.

---

## Mục lục

1. [Mở đầu & Mục tiêu approach](#1-mở-đầu)
2. [Trạng thái & Bắt đầu lại từ đâu](#2-trạng-thái)
3. [Why this approach](#3-why)
4. [Cơ sở toán học](#4-toán-học)
5. [Why this NOT that](#5-not-that)
6. [Limitations](#6-limitations)
7. [Quick-start tái kích hoạt](#7-quick-start)
8. [Đặc thù: Kiến trúc & Dataset transformation](#8-đặc-thù)
9. [Hyperparameters](#9-hyperparams)
10. [Đánh giá: Composite Score & Baselines](#10-eval)
11. [Cấu trúc thư mục đề xuất](#11-skeleton)
12. [Vị trí dữ liệu & tài liệu](#12-paths)

---

## 1. Mở đầu & Mục tiêu approach

**Bài toán chung**: Sinh chuỗi token SQL injection thỏa mãn ràng buộc grammar.

**Gumbel-Softmax approach** = xây dựng **bộ benchmark thực nghiệm đầy đủ** cho **Structured Discrete Sequence Generation (SDSG)**, dùng SQL Injection làm domain cụ thể (vì có formal grammar verifiable). Đóng góp chính của paper: bộ **Composite Score** + giao thức so sánh giữa **6 phương pháp** (Markov + MLE + SeqGAN + MaliGAN + RelGAN + Gumbel-GAN).

**Đặc trưng phân biệt với 2 approach kia**:
- Gumbel-Softmax dùng **continuous relaxation** của argmax — gradient flow end-to-end qua sampling step.
- **Decoder-only**, không có encoder (sample $z$ từ noise prior).
- **Multi-scale Dilated CNN** cho Discriminator (kernels [2,3,5,8,12,16]).
- Thiết kế **Re-lexicalization module** post-generation (placeholder → giá trị cụ thể).
- **Frozen test set** cho fair comparison.

**Mục tiêu paper**: Trả lời 3 câu hỏi research:
- **RQ1**: Phương pháp nào đạt Composite Score cao nhất trên SDSG task?
- **RQ2**: Có tradeoff nào giữa Validity vs Diversity?
- **RQ3**: Gumbel-Softmax có lợi thế gì so với policy-gradient (SeqGAN) trên domain có formal grammar?

**Scope**: pure generation benchmark (syntactic), KHÔNG đánh giá semantic correctness hay adversarial effectiveness.

---

## 2. Trạng thái hiện tại

| Stage | Status |
|---|---|
| Data engineering | ✅ Done |
| Roadmap (`Asset/Guiding/SQLi-Gumbel-SoftmaxGAN-Roadmap.md`) | ✅ Done |
| Dataset transformation (full de-lex + frozen test) | ❌ |
| Tokenizer + vocab fixed | ❌ |
| Generator (Transformer Decoder + Gumbel-Softmax) | ❌ |
| Discriminator (Dilated CNN multi-scale) | ❌ |
| Loss (WGAN-GP) | ❌ |
| Temperature schedule + reset trigger | ❌ |
| Re-lexicalization module | ❌ |
| Syntax-Filter buffer | ❌ |
| Composite Score evaluator (Validity + Self-BLEU + Wasserstein) | ❌ |
| 5 baselines (Markov, MLE LM, SeqGAN, MaliGAN, RelGAN) | ❌ |
| Frozen test set generation | ❌ |
| Inference API (FastAPI) | ❌ |

**Bắt đầu lại từ đâu (priority order)**:
1. Verify dataset (mục 12).
2. Build vocab + tokenizer + frozen test set TRƯỚC TIÊN (sẽ dùng cho mọi baseline).
3. Implement Generator + Discriminator stubs.
4. Implement WGAN-GP loss + temperature schedule.
5. MLE pretrain → adversarial.
6. Implement Composite Score evaluator.
7. Implement 5 baselines, train trên cùng dataset, eval trên cùng frozen test.
8. Implement Re-lex + Syntax-Filter.
9. Inference API.

---

## 3. Why this approach?

### 3.1 Vấn đề gốc

Bài toán "gradient không pass qua argmax" chia thành 3 trường phái giải:
1. **Continuous relaxation** (Gumbel-Softmax): smooth approximation của argmax.
2. **Policy gradient** (SeqGAN/REINFORCE): treat sampling như RL, dùng log-prob trick.
3. **Latent-based** (VAE-GAN): encode → sample latent → decode.

Approach này thuộc trường phái 1.

### 3.2 Tại sao Gumbel-Softmax?

- **Gumbel-Max trick**: $\arg\max_i [\log \pi_i + g_i]$ với $g_i \sim \text{Gumbel}(0,1)$ tương đương sampling từ distribution $\pi$.
- **Continuous relaxation**: thay $\arg\max$ bằng $\text{softmax}((\log \pi + g)/\tau)$. Khi $\tau \to 0$: approaches one-hot. Khi $\tau$ moderate: differentiable.
- **End-to-end gradient flow**: khác REINFORCE high-variance, Gumbel có gradient determined trực tiếp qua softmax → low-variance, stable.

### 3.3 Cơ sở khoa học

- **Jang et al. 2016** & **Maddison et al. 2016** (concurrent): "Categorical Reparameterization with Gumbel-Softmax".
- **Wasserstein distance theory** (Villani 2008): optimal transport cho distribution matching.
- **WGAN-GP** (Gulrajani 2017): gradient penalty enforce Lipschitz softly.
- **Multi-scale CNN** (Inception, Dilated): bắt features ở nhiều granularity.

### 3.4 Lý do nâng cấp Discriminator → Dilated CNN

SQL có cấu trúc **phân tầng**: token kề nhau quan trọng (ngắn-range), nhưng cũng có dependency xa (long-range qua subqueries). Dilated CNN cho phép:
- Kernels nhỏ [2,3] bắt **toán tử + từ khóa kép** (`UNION SELECT`, `OR 1`).
- Kernels vừa [5,8] bắt **mệnh đề đơn** (`WHERE id = <NUM>`).
- Kernels rộng [12,16] bắt **subqueries** (`SELECT ... FROM (SELECT ...)`).

→ Receptive field lớn không cần stack quá sâu.

---

## 4. Cơ sở toán học

### 4.1 Gumbel-Max trick

Cho distribution $\pi$ over vocab:
$$z = \arg\max_i [\log \pi_i + g_i], \quad g_i = -\log(-\log U_i), \quad U_i \sim U(0, 1)$$

$z$ có cùng phân phối như sampling trực tiếp $z \sim \text{Categorical}(\pi)$.

### 4.2 Gumbel-Softmax (continuous relaxation)

$$y_i = \frac{\exp((\log \pi_i + g_i)/\tau)}{\sum_j \exp((\log \pi_j + g_j)/\tau)}$$

$y$ là vector trên simplex, $\tau$ = temperature. Khi $\tau \to 0$: $y$ → one-hot. Differentiable theo $\pi$.

### 4.3 Temperature schedule

$$\tau(t) = \tau_0 \cdot \exp(-r \cdot t)$$

với $\tau_0 = 1.0$, $r$ chọn để $\tau$ đạt $0.1$ sau 80% số bước. → $r = -\ln(0.1) / (0.8 \cdot T_{total})$.

**Reset trigger**: nếu $\|\nabla_\theta G\| < \epsilon_{threshold}$ khi $\tau < 0.3$ → reset $\tau \leftarrow 0.5$ hoặc stop-and-sample tại checkpoint tốt nhất.

### 4.4 Wasserstein-1 distance

$$W_1(P, Q) = \inf_{\gamma \in \Pi(P,Q)} \mathbb{E}_{(x,y) \sim \gamma}[\|x - y\|]$$

**Kantorovich-Rubinstein duality**:
$$W_1(P, Q) = \sup_{\|f\|_L \leq 1} \mathbb{E}_P[f] - \mathbb{E}_Q[f]$$

### 4.5 WGAN-GP loss

**D loss**:
$$\mathcal{L}_D = \mathbb{E}_{x \sim p_{data}}[D(x)] - \mathbb{E}_{\tilde{x} \sim p_g}[D(\tilde{x})] + \lambda_{gp} \mathbb{E}_{\hat{x}}[(\|\nabla_{\hat{x}} D\|_2 - 1)^2]$$

với $\hat{x} = \epsilon x + (1-\epsilon)\tilde{x}$, $\epsilon \sim U(0,1)$, $\lambda_{gp} = 10$.

**G loss**:
$$\mathcal{L}_G = -\mathbb{E}_z[D(G(z))]$$

### 4.6 Composite Score (paper's contribution)

$$S = w_1 \cdot \text{Validity} + w_2 \cdot (1 - \text{Self-BLEU}) + w_3 \cdot (1 - \hat{W}_1)$$

- $w_1 = 0.4$, $w_2 = 0.3$, $w_3 = 0.3$ (khởi đầu, refine qua ablation).
- **Hard constraint**: Validity < 50% → loại khỏi bảng xếp hạng chính.

### 4.7 Phép toán nền tảng

- **Gumbel distribution** (extreme value theory): $G_i = -\log(-\log U_i)$.
- **Continuous relaxation** (smoothing argmax với temperature).
- **Optimal transport theory** (Wasserstein distance).
- **Lipschitz continuity** + Kantorovich-Rubinstein duality.
- **Spectral analysis** cho Lipschitz norm of D.

---

## 5. Why this NOT that?

### 5.1 VS VAE-GAN

| Aspect | Gumbel-Softmax | VAE-GAN |
|---|---|---|
| Encoder | ❌ | ✅ |
| Latent input | $z$ random từ N(0,I) | $z$ từ $q(z|x)$ |
| Loss components | 2 (G + D với WGAN-GP) | 4 (recon + KL + adv + fm) |
| Training complexity | Thấp | Cao |
| Reconstruction | ❌ | ✅ |
| Latent walk meaningful | ❌ Ngẫu nhiên | ✅ |
| Benchmark cleanness | ✅ Cao | Trung bình |
| Speed | Nhanh | Chậm hơn |

**Khi ưu tiên Gumbel-Softmax**: cần benchmark sạch, simplicity, không cần encoder/reconstruction.

### 5.2 VS SeqGAN

| Aspect | Gumbel-Softmax | SeqGAN |
|---|---|---|
| Discrete handling | Continuous relaxation | REINFORCE |
| Gradient stability | ✅ Cao (low variance) | Thấp |
| Training speed | ✅ Nhanh | Chậm (MC rollout) |
| External reward (WAF) | ❌ Khó tích hợp | ✅ Native |
| Optimize ASR direct | ❌ | ✅ |
| Benchmark cleanness | ✅ Cao | Trung bình |

**Khi ưu tiên Gumbel-Softmax**: cần fair benchmark, không cần WAF reward, prefer stability.

### 5.3 Tóm tắt: Gumbel-Softmax tỏa sáng khi

1. Cần **benchmark sạch fair** với nhiều baseline (paper-grade comparison).
2. Cần **gradient stability** (low variance) cho training reliable.
3. Có thể chấp nhận **không direct ASR optimization** — pure generation focus.
4. Cần **inference nhanh** (latency < 100ms/payload trên CPU).

---

## 6. Limitations

### 6.1 Temperature schedule sensitivity

$\tau$ schedule là crucial:
- $\tau$ cao (gần 1): output soft → D dễ phát hiện artifacts → adversarial signal kém.
- $\tau$ thấp (gần 0.1): output gần one-hot → gradient vanish → training stuck.

**Mitigation**:
- Exponential decay schedule.
- Gradient norm monitoring.
- Reset trigger: $\tau \leftarrow 0.5$ nếu $\|\nabla G\| < \epsilon$.
- Stop-and-sample tại checkpoint tốt nhất nếu reset không cứu.

### 6.2 Mode collapse

Vẫn xảy ra dù WGAN-GP giảm risk.

**Detection**: variance batch sinh ra. Sau mỗi epoch, sample 500 → check variance.
**Mitigation**: tăng dropout, inject noise vào z, diversity bonus.

### 6.3 Re-lexicalization phức tạp

Generator output `<TABLE>`, `<COL>`, `<NUM>`, `<STR>` placeholder. Cần module thay placeholder bằng giá trị cụ thể, đảm bảo:
- Tên bảng/cột tồn tại trong target schema.
- Số literal hợp kiểu (vd column kiểu INT thì NUM phải là int).
- String literal hợp context.

**Mitigation**:
- Input thêm JSON Schema của target DB.
- Map: `<TABLE>` → random pick từ schema tables; `<NUM>` → int/float theo column type; `<STR>` → string mẫu phù hợp.
- **Syntax-Filter buffer**: chỉ trả về payload **vẫn parse được sau re-lex**. Loại payload broken.

### 6.4 Không tối ưu trực tiếp ASR

Gumbel-Softmax tối ưu G qua D loss + Composite Score evaluation, KHÔNG có WAF Oracle trong loop. Nếu paper goal là "bypass cao", đây là disadvantage so với SeqGAN.

**Workaround**: post-hoc evaluation qua WAF, không trong training. Paper claim phải reframe — focus là **pure generation quality** (validity + diversity + distribution match), không phải attack effectiveness.

### 6.5 Discriminator overfitting

D có thể overfit vào quirks của G nếu D:G ratio sai.

**Mitigation**:
- D:G = 5:1 (standard WGAN-GP).
- Spectral normalization như backup.
- Gradient penalty enforce Lipschitz.

### 6.6 Vocabulary fixed limitation

Vocabulary phải fix sau khi finalize. Nếu thêm token mới (mở rộng SQL dialect), cần re-train từ đầu.

**Mitigation**: ngay từ đầu construct vocabulary đủ lớn, bao quát các DB engines (MySQL + Oracle + PostgreSQL + MSSQL + SQLite + NoSQL).

---

## 7. Quick-start tái kích hoạt

```powershell
# 1. Vào project root
cd C:\Users\Admin\Documents\GAN

# 2. Tạo & activate venv
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 3. Cài deps
pip install torch transformers numpy pandas sqlparse pyyaml tqdm tensorboard scipy nltk fastapi uvicorn

# 4. Verify dataset
python -c "import os; print(len(os.listdir('Asset/Data/results')))"

# 5. Vào folder approach
cd Gumbel-Softmax_SQLi
mkdir data, src, configs, baselines, eval, api, checkpoints

# 6. Build frozen test set TRƯỚC
# data/prepare_gumbel_data.py: split → save train/val/test, FREEZE test set

# 7. Build vocab + tokenizer
# data/build_vocab.py → vocab.json (bao quát tất cả DB engines)

# 8. Implement Generator + Discriminator stubs
# src/generator.py (Transformer Decoder + Gumbel-Softmax)
# src/discriminator.py (Dilated CNN [2,3,5,8,12,16])

# 9. Smoke test forward + backward
python -c "from src.generator import Generator; ..."

# 10. MLE pretrain
python train.py --stage mle --config configs/gumbel_default.yaml

# 11. Adversarial phase
python train.py --stage adversarial --resume checkpoints/mle_best.pt

# 12. Eval với Composite Score
python evaluate.py --checkpoint checkpoints/best.pt --test-set data/frozen_test_set.csv

# 13. Train 5 baselines + benchmark
python benchmark.py --frozen-test data/frozen_test_set.csv
```

---

## 8. Đặc thù approach: Kiến trúc & Dataset transformation

### 8.1 Kiến trúc tổng thể

```
                          ┌──────────────────────────┐
              z ~ N(0,I) →│   Generator              │
                          │   Transformer Decoder    │
                          │   6 layers, h=8, d=256   │
                          │   + Gumbel-Softmax head  │  → soft one-hot (B, L, V)
                          └──────────────────────────┘
                                    ↓
                          ┌──────────────────────────┐
                          │   Discriminator          │
                          │   Dilated CNN multi-scale│
                          │   kernels [2,3,5,8,12,16]│  → score (B,)
                          │   WGAN-GP                │
                          └──────────────────────────┘

[Inference]:
              z ~ N(0,I) → G → argmax → tokens with placeholders
                                ↓
                          ┌──────────────────────────┐
                          │   Re-lexicalization      │
                          │   <TABLE>/<COL>/<NUM>/<STR>│
                          │   ← JSON schema input    │
                          └──────────────────────────┘
                                    ↓
                          ┌──────────────────────────┐
                          │   Syntax-Filter Buffer   │
                          │   chỉ trả payload parse OK│
                          └──────────────────────────┘
                                    ↓
                          Output: list of valid payloads
```

### 8.2 Dataset transformation cho Gumbel-Softmax

**Input**: `Asset/Data/master_sqli.csv` (sau merge).

**Khác VAE-GAN**: dùng **structural de-lexicalization** với placeholder vocab — tương tự SeqGAN.

**Vocabulary** (đặc trưng — phải đủ rộng):
- Special: `<PAD>`, `<SOS>`, `<EOS>`, `<UNK>`.
- Placeholders: `<TABLE>`, `<COL>`, `<NUM>`, `<STR>`.
- SQL keywords: ~80.
- Operators: ~15.
- Special chars: ~15.
- Attack functions multi-DB: ~50 (pg_sleep, sleep, benchmark, waitfor, extractvalue, utl_inaddr, xp_cmdshell, ...).
- DB-specific tokens: ~30.

**Tổng vocabulary**: ~200 tokens. Lưu `data/vocab.json` — **frozen** sau khi finalize.

**Reference Entropy** $H(V)$: tính trên train set, dùng làm reference cho sanity check.

**Splits**:
- Train: 70%.
- Val: 15%.
- **Frozen test: 15%** — NOT shuffled, NOT modified sau khi tạo. Lưu MD5 hash để verify.

### 8.3 Generator architecture

```python
class GeneratorTransformer(nn.Module):
    def __init__(self, vocab_size, d_model=256, n_heads=8, n_layers=6, max_len=128):
        self.embed = nn.Embedding(vocab_size, d_model)
        self.pos_enc = PositionalEncoding(d_model, max_len)
        self.decoder = nn.TransformerDecoder(
            nn.TransformerDecoderLayer(d_model, n_heads, 4*d_model),
            n_layers
        )
        self.out_proj = nn.Linear(d_model, vocab_size)
    
    def forward(self, z, tokens=None, tau=1.0):
        # z: (B, d_model) noise input
        # tokens: (B, L) for teacher forcing in MLE pretrain
        ...
        logits = self.out_proj(hidden)
        soft_onehot = gumbel_softmax(logits, tau=tau)  # (B, L, V)
        return soft_onehot, logits
```

### 8.4 Discriminator architecture

```python
class DiscriminatorDilatedCNN(nn.Module):
    def __init__(self, vocab_size, embed_dim=128):
        self.embed = nn.Linear(vocab_size, embed_dim)  # accept soft one-hot
        # Multi-scale dilated conv
        self.convs = nn.ModuleList([
            nn.Conv1d(embed_dim, 64, kernel_size=k, dilation=d, padding='same')
            for k, d in [(2,1), (3,1), (5,2), (8,2), (12,4), (16,4)]
        ])
        self.fc = nn.Sequential(
            nn.Linear(64 * 6, 128),
            nn.LayerNorm(128),
            nn.ReLU(),
            nn.Linear(128, 1)
        )
    
    def forward(self, x):
        # x: (B, L, V) soft one-hot from G OR (B, L, V) one-hot from data
        emb = self.embed(x)  # (B, L, embed_dim)
        emb = emb.transpose(1, 2)  # (B, embed_dim, L)
        feats = [F.relu(conv(emb)).max(dim=2)[0] for conv in self.convs]
        feat = torch.cat(feats, dim=1)  # (B, 64*6)
        return self.fc(feat).squeeze(-1)  # (B,)
```

**Lưu ý**: KHÔNG dùng BatchNorm trong D (break gradient penalty). Dùng LayerNorm.

### 8.5 Re-lexicalization module

```python
class Relexicalizer:
    def __init__(self, schema: Dict):
        # schema = {"tables": ["users", "products"], "columns": {...}, "types": {...}}
        self.schema = schema
    
    def relex(self, tokens: List[str]) -> str:
        result = []
        for tok in tokens:
            if tok == '<TABLE>':
                result.append(random.choice(self.schema['tables']))
            elif tok == '<COL>':
                result.append(random.choice(list(self.schema['columns'])))
            elif tok == '<NUM>':
                result.append(str(random.randint(1, 1000)))
            elif tok == '<STR>':
                result.append("'" + random.choice(['admin', 'test', 'a']) + "'")
            else:
                result.append(tok)
        return ' '.join(result)
```

### 8.6 Syntax-Filter buffer

```python
def syntax_filter(payloads: List[str]) -> List[str]:
    valid = []
    for p in payloads:
        try:
            parsed = sqlparse.parse(p)
            if parsed and parsed[0].tokens:
                valid.append(p)
        except Exception:
            continue
    return valid
```

---

## 9. Hyperparameters

| Hyperparameter | Khởi đầu | Khoảng | Notes |
|---|---|---|---|
| **G arch** | Transformer Decoder | | |
| **G d_model** | 256 | 128-512 | |
| **G n_heads** | 8 | 4-16 | |
| **G n_layers** | 6 | 4-12 | |
| **G FFN dim** | 1024 | 4× d_model | |
| **D arch** | Dilated CNN | | |
| **D kernels** | [2, 3, 5, 8, 12, 16] | | Multi-scale theo SQL hierarchy |
| **D dilation** | [1, 1, 2, 2, 4, 4] | | Tăng theo kernel size |
| **D filters per kernel** | 64 | 32-128 | |
| **D embed dim** | 128 | 64-256 | |
| **Gumbel τ** | 1.0 → 0.1 | exp decay over 80% steps | |
| **Reset threshold ε** | 0.01 | | $\|\nabla G\|$ floor |
| **Reset $\tau$ value** | 0.5 | | After trigger |
| **WGAN-GP λ** | 10 | | |
| **D:G ratio** | 5:1 | | |
| **Composite weights** | $w_1=0.4, w_2=0.3, w_3=0.3$ | ablation tune | |
| **Hard constraint** | Validity ≥ 50% | | Else loại khỏi rank |
| **Optimizer** | Adam β=(0.5, 0.9) | | WGAN-GP standard |
| **G LR** | 2e-4 | | |
| **D LR** | 2e-4 | | |
| **LR schedule** | Cosine | | |
| **Batch size** | 64 | 32-128 | |
| **MLE pretrain steps** | 10k | 5k-30k | |
| **Adversarial steps** | 50k | 30k-200k | |
| **Sequence max length L** | percentile 95 | | Đo từ data, ước lượng 60-100 |

---

## 10. Đánh giá: Composite Score & Baselines

### 10.1 Composite Score

$$S = w_1 \cdot \text{Validity} + w_2 \cdot (1 - \text{Self-BLEU}) + w_3 \cdot (1 - \hat{W}_1)$$

**Hard constraint**: Validity < 50% → loại.

### 10.2 Validity (parse rate)

Parse 1000 samples bằng `sqlparse`. Threshold: ≥ 80% để vào ranking, ≥ 50% là hard constraint.

### 10.3 Self-BLEU (diversity)

n-gram order N=3, score càng thấp càng đa dạng.

### 10.4 Wasserstein Distance $\hat{W}_1$

Tính trên embedding space giữa $P_G$ (samples sinh ra) và $P_{data}$ (test set).

**Implementation**: Sinkhorn divergence approximation hoặc dual form via critic.

**Lý do dùng $\hat{W}_1$ thay JSD**: nhất quán với WGAN-GP loss đã dùng khi train; tránh saturation khi 2 distributions không overlap.

### 10.5 Latent Space Walk (qualitative)

Sample 2 vector $z_A, z_B$, interpolate $z_t = (1-t)z_A + t z_B$, decode mỗi điểm. **Qualitative analysis**, không phải metric chính.

### 10.6 Baselines (5 phương pháp comparison)

**Tier 1 — Non-GAN (đo giá trị adversarial)**:
1. **Markov Chain / Template-based**: ngẫu nhiên cú pháp thuần.
2. **Standard Transformer-MLE**: cross-entropy thuần, không adversarial.

**Tier 2 — GAN (đo giá trị Gumbel-Softmax vs other GAN-for-text)**:
3. **SeqGAN**: REINFORCE với MC rollout.
4. **MaliGAN**: MLE-augmented gradient.
5. **RelGAN**: Relational memory generator.

**Giao thức so sánh**:
- Cùng dataset, cùng vocab, cùng max length $L$.
- Train từng baseline + Gumbel-GAN.
- Eval trên **frozen test set duy nhất**.
- Report Composite Score + sub-metrics.

**Success threshold**: $S(\text{Gumbel-GAN}) > S(\text{MLE-Baseline}) + 15\%$.

### 10.7 Statistical rigor

- Mean ± std trên ≥ 3 random seeds.
- Bootstrap CI cho Composite Score.
- Significance test (paired t-test) khi compare methods.

---

## 11. Cấu trúc thư mục đề xuất

```
Gumbel-Softmax_SQLi/
├── Guiding.md                    ← FILE NÀY
├── README.md
├── requirements.txt
├── data/
│   ├── prepare_gumbel_data.py    ← read master_sqli → full delex placeholder vocab
│   ├── build_vocab.py            ← Construct frozen vocab.json
│   ├── vocab.json                ← Frozen vocabulary
│   ├── train.csv
│   ├── val.csv
│   ├── frozen_test_set.csv       ← MD5 hash committed
│   └── frozen_test_set.md5       ← Hash for integrity
├── src/
│   ├── tokenizer.py              ← SQL-aware regex
│   ├── generator.py              ← Transformer Decoder + Gumbel-Softmax
│   ├── discriminator.py          ← Dilated CNN multi-scale
│   ├── losses.py                 ← WGAN-GP
│   ├── temperature_schedule.py   ← τ exp decay + reset trigger
│   ├── relex.py                  ← Re-lexicalization (JSON schema → SQL)
│   ├── syntax_filter.py          ← sqlparse-based buffer
│   └── utils.py
├── baselines/
│   ├── markov.py                 ← N-gram markov chain
│   ├── template_based.py         ← Random template fill
│   ├── mle_lm.py                 ← Standard Transformer MLE
│   ├── seqgan_baseline.py        ← Vanilla SeqGAN
│   ├── maligan.py                ← MaliGAN
│   └── relgan.py                 ← RelGAN
├── eval/
│   ├── composite_score.py        ← Main metric
│   ├── validity.py               ← sqlparse rate
│   ├── self_bleu.py              ← Diversity n-gram=3
│   ├── wasserstein.py            ← $\hat{W}_1$ on embedding
│   └── latent_walk.py            ← Qualitative
├── configs/
│   ├── gumbel_default.yaml
│   └── ablation_weights.yaml     ← w1, w2, w3 tuning
├── train.py                      ← MLE pretrain → adversarial
├── evaluate.py                   ← Single model eval
├── benchmark.py                  ← All 6 methods on frozen test
├── generate.py                   ← Sample inference
├── api/
│   ├── inference_server.py       ← FastAPI POST /generate
│   └── docker_compose.yml
├── scripts/
│   ├── run_train.sh
│   ├── run_baselines.sh
│   ├── run_benchmark.sh
│   └── run_api.sh
└── checkpoints/
```

---

## 12. Vị trí dữ liệu, tài liệu, code đã có

### 12.1 Dữ liệu

- Master input: `C:\Users\Admin\Documents\GAN\Asset\Guiding\master_unlabeled.csv` (cột `payload_delex` đã có).
- Result batches: `C:\Users\Admin\Documents\GAN\Asset\Data\results\result_batch_*.csv`.
- Master labeled: `C:\Users\Admin\Documents\GAN\Asset\Data\master_sqli.csv` (verify đã merge).

### 12.2 Tài liệu tham chiếu

- `Asset/Guiding/SQLi-Gumbel-SoftmaxGAN-Roadmap.md` — Roadmap kỹ thuật chi tiết 6 giai đoạn.
- `Asset/Guiding/Data_Engineering_Recap.md` — Pipeline data.
- `Asset/Guiding/AI_Foundations_For_Team_03_Attention_And_Transformer.md` — Transformer (cho Generator).
- `Asset/Guiding/AI_Foundations_For_Team_04_Generative_Models.md` — GAN, WGAN-GP, biến thể GAN (quan trọng).
- `Asset/Guiding/AI_Foundations_For_Team_02_CNN_RNN_Sequences.md` — Dilated CNN.

### 12.3 Code re-use

- `data_engine/normalizer.py` — chuẩn hóa text.
- `data_engine/merge.py` — merge results.

### 12.4 Tham khảo từ 2 approach kia

- `VAE-GAN_SQLi/Guiding.md` — partial de-lex, KL annealing, latent space.
- `SeqGAN_SQLi/Guiding.md` — REINFORCE, MC rollout, expert demos.

---

## 13. Checklist trước khi start serious

- [ ] Dataset merge → master_sqli.csv (verify).
- [ ] Frozen test set built + MD5 hash committed git.
- [ ] Vocabulary frozen + vocab.json committed.
- [ ] Reference Entropy $H(V)$ computed.
- [ ] Tokenizer round-trip test.
- [ ] Generator forward pass shape `(B, L, V)`.
- [ ] Discriminator accept `(B, L, V)` soft one-hot, output `(B,)`.
- [ ] Gumbel-Softmax layer differentiable check.
- [ ] WGAN-GP gradient penalty implementation correct (test với simple distribution).
- [ ] Temperature schedule code unit-test.
- [ ] Re-lex module tested với 5 schema khác nhau.
- [ ] Syntax-Filter test với 100 known-valid + 100 known-invalid samples.
- [ ] Smoke MLE pretrain 100 steps không NaN.
- [ ] Smoke adversarial 100 steps không NaN.
- [ ] 5 baselines smoke test pass.
- [ ] Composite Score evaluator tested.

---

## 14. Mẹo & "khi gặp vấn đề thì làm gì"

| Triệu chứng | Nguyên nhân | Hành động |
|---|---|---|
| Gradient G vanish khi $\tau < 0.3$ | Temperature decay quá nhanh | Slower decay, hoặc reset $\tau \leftarrow 0.5$ |
| D loss âm sâu (vd -100) | Lipschitz violation | Tăng λ_gp, check D có BatchNorm? |
| Validity < 50% sau full training | Generator chưa học được structure | Train MLE lâu hơn, increase G capacity |
| Mode collapse (Self-BLEU > 0.95) | Variance collapse | Tăng dropout, inject noise vào z, diversity bonus |
| Composite Score thấp dù validity cao | Self-BLEU cao hoặc $\hat{W}_1$ cao | Check diversity, distribution matching |
| Training rất chậm | Dilated CNN compute heavy | Reduce filters, prune kernel sizes |
| Re-lex output không parse được | Schema mismatch | Sửa Re-lexicalizer logic, thêm context-aware rules |
| Inference latency > 100ms | Model quá lớn | Reduce d_model, n_layers; quantize cho deployment |
| Frozen test set bị modified | Bug pipeline | Verify MD5, restore từ git commit cũ |

---

## 15. Bước tiếp theo (sau train + eval xong)

1. **Ablation study** trên Composite weights: tune $w_1, w_2, w_3$ trên validation, justify trong paper.
2. **Run all 6 methods** trên frozen test, report bảng so sánh.
3. **Failure analysis**: sample payloads từng method, qualitative comparison.
4. **Inference API + Docker**: deploy FastAPI service.
5. **Reproducibility package**: frozen test + checkpoints + eval script + Dockerfile.
6. **Paper writing**.

---

*File này là "self-contained reactivation guide" cho nhánh Gumbel-Softmax. Đây là approach thiên về **benchmark cleanness** — focus vào pure generation quality + multi-baseline comparison. Chi tiết paper-level: `Asset/Guiding/SQLi-Gumbel-SoftmaxGAN-Roadmap.md`.*
