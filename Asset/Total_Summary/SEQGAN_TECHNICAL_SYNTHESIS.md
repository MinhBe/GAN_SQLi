# SEQGAN TECHNICAL SYNTHESIS — Tổng Hợp Kỹ Thuật

> Tổng hợp từ 51 bài báo phân tích. Cập nhật: 2026-05-18
> Mục tiêu: Hỗ trợ slide thầy Lâm 20/05 + Thesis Chapters 2-3

---

## SECTION 1 — SEQGAN EVOLUTION TIMELINE (2014–2024)

```
2014 ─── Goodfellow_2014_GAN
         GAN gốc (image domain, continuous output)
         ✗ Không áp dụng cho discrete tokens
         → Mọi text GAN sau đây phải giải quyết vấn đề này

2017a ── Arjovsky_2017_WGAN
         Wasserstein distance thay JS divergence
         ✓ Giải quyết: gradient vanishing khi D quá tốt
         ✗ Weight clipping → capacity degradation

2017b ── Gulrajani_2017_WGAN_GP
         Gradient Penalty thay weight clipping
         ✓ Giải quyết: Lipschitz constraint đúng cách
         → V5 dùng WGAN-GP (thầy Lâm confirm)

2017c ── Yu_2017_SeqGAN
         REINFORCE + MC roll-out cho discrete text
         ✓ Giải quyết: non-differentiable discrete sampling
         ✗ High variance, sparse reward, O(N×T) MC cost
         → Root cause collapse V1-V4 của bạn

2017d ── Jang_2017_Gumbel_Softmax | Maddison_2017_Concrete_Dist
         Gumbel-Softmax: differentiable categorical sampling
         ✓ Giải quyết: backprop qua discrete tokens trực tiếp
         ✓ Không cần MC roll-out, gradient always exists
         → V5 (Gumbel-SeqGAN) dùng kỹ thuật này

2017e ── Williams_1992_REINFORCE + Bengio_2013_STE
         Baseline: REINFORCE (high variance)
         STE: Straight-Through = biased nhưng simple
         → Reference papers cho thesis Section 2.3

2018a ── Guo_2018_LeakGAN
         Manager-Worker hierarchy + leaked D features
         ✓ Giải quyết: sparse reward cho long sequences
         ✗ Phức tạp hơn SeqGAN 3×, khó tune
         → Potential upgrade sau V5 stable

2018b ── Fedus_2018_MaskGAN
         Conditional text infilling với MASK tokens
         ✓ Ứng dụng: cải thiện payload tại vị trí cụ thể
         → Future work: SQLi payload surgery

2018c ── Miyato_2018_Spectral_Norm
         SpectralNorm cho discriminator stability
         ✓ Alternative/complement cho WGAN-GP
         → P2: thay LayerNorm trong D CNN

2019a ── Nie_2019_RelGAN
         Relational memory, multi-step attention
         ✓ Long-range dependencies (GROUP_CONCAT...closing paren)
         → P2 upgrade sau V5

2019b ── Blonde_2019_SAM_GAIL
         GAIL-based reward (imitation learning)
         → Reference nếu muốn thay reward function design

2020 ─── Demetrio_2020_WAF_A_MoLE
         6 mutation operators + WAF oracle
         ✓ Trực tiếp: OWASP bypass 2% → 15-30%
         → V5 Phase 3: post-processing augmentation

2024 ─── Atkinson_2024 | Pearson_2024 (defensive publications)
         WGAN + PPO cho SeqGAN
         Improved WGAN: NLL=8.509 (SeqGAN gốc: 8.639)
         ✗ PPO thua REINFORCE (PPO: 9.065 vs REINFORCE: 8.639)
         → CẢNH BÁO: Không dùng PPO cho V5
```

**Kết luận Timeline**: Lộ trình kỹ thuật của V5 là hợp lý và được justify bởi 7 năm evolution literature (2017→2024).

---

## SECTION 2 — GRADIENT ESTIMATOR COMPARISON TABLE

| Estimator | Paper | Bias | Variance | Gradient | Mode Collapse | Cost | SQLi Viable? |
|---|---|---|---|---|---|---|---|
| **REINFORCE** | Williams_1992 | Unbiased | **High** (MC reduce) | Sparse → vanish khi advantage→0 | **Luôn xảy ra** (V1-V4) | O(N×T) per step | ✗ (proven failed) |
| **SCST** (Self-Critical) | Rennie_2017 | Unbiased | Medium | Better than REINFORCE (baseline = test-time output) | Unknown | O(2×T) | ? (không tested) |
| **Gumbel-Softmax** | Jang_2017 | Biased (τ→0 = unbiased) | **Low** | Dense, **always exists** | **Giải quyết** | O(T) | **✓ (V5 choice)** |
| **Concrete Distribution** | Maddison_2017 | Biased | Low | Dense | Giải quyết | O(T) | ✓ (equivalent) |
| **Straight-Through (STE)** | Bengio_2013 | Biased | Low | Direct identity pass | Giảm | O(T) | ✓ (simpler) |
| **GAIL** | Blonde_2019 | Complex | Medium | Model-based | Unknown | High (train separate model) | ? |
| **PPO** | Schulman_2017 | Unbiased | Medium | Clipped ratio | Unknown | O(N×T) + KL | ✗ (Atkinson: worse) |

### Tại sao chọn Gumbel-Softmax cho V5?

| Criterion | REINFORCE | Gumbel-Softmax |
|-----------|-----------|----------------|
| Root cause fix | ✗ Patch symptoms | **✓ Gradient luôn non-zero** |
| SeqGAN framework giữ nguyên | ✓ | ✓ |
| WGAN-GP compatible | ✓ | **✓ (D nhận soft tokens)** |
| Code change nhỏ | N/A | **~60 dòng thay** |
| Empirical support | V1-V4 failed | Jang_2017 benchmarks |
| τ schedule control | Không | **✓ τ∈[0.5,1.0]** |

**Kết luận**: Gumbel-Softmax là **lựa chọn duy nhất đáp ứng cả 3 điều kiện**: (1) giải quyết mode collapse, (2) giữ framework SeqGAN cho thesis, (3) compatible với WGAN-GP đã chọn.

---

## SECTION 3 — SQLI DATASET COMPARISON TABLE

| Paper | Dataset | Size (raw) | Size (clean) | Types | DB Engine | Public? | Ghi chú quan trọng |
|---|---|---|---|---|---|---|---|
| Lu_2022_GAN_SQLi | CVE+CNVD+exploit-db | ~5,000 | 2,000+ | 4 types | Multi | ✗ | SQLParse tokenization, 8 variational operators |
| Le_2024_GSQLi | Custom Vietnamese | Unknown | Unknown | Binary (attack/benign) | MySQL | ✗ | Focused on Vietnamese web apps |
| Dasari_2025 | Kaggle SQLi dataset | ~30K | ~30K | Binary | Multi | ✓ Kaggle | **CAVEAT**: CWGAN-GP cho R²=-1.7253 (invalid) |
| Chowdhary_2023 | DVWA + SQLi-labs | Small (~500) | Small | Attack categories | MySQL | Partial | Pentest environment, không representative |
| Lin_2018_IDSGAN | KDD Cup 1999 | 4.9M | ~125K | Network traffic | N/A | ✓ | Khác domain nhưng GAN evasion technique relevant |
| Demetrio_2020_WAF | HTTPCS commercial WAF | ~1M requests | ~1M | HTTP requests (binary) | Any | ✓ Zenodo | tamper_method labels: 7 techniques |
| **V5 (bạn)** | RbSQLi+Zenodo+Kaggle+GitHub | **14.6M raw** | **~50K gold** | **4 types** | **Multi** | Partial | delex_v2: collision 71.89%→4.33%, 22× more than V3 |

### V5 Dataset Advantage vs Prior Work

| Metric | Lu_2022 (best prior) | V5 (target) | Factor |
|--------|---------------------|-------------|--------|
| Gold training samples | ~2,000 | ~15,000-20,000 | 7.5-10× |
| Type coverage | 4/4 | 4/4 | = |
| Collision rate | Unknown | 4.33% | Measured |
| DB engine coverage | Multi (unknown) | Multi (labeled) | Better |
| Injection type labels | Inferred | Explicit (RbSQLi injection_type) | Better |
| Tamper method labels | None | ✓ (Zenodo tamper_method) | New |

**Kết luận**: V5 có dataset lớn nhất và tốt nhất trong literature so với papers trong domain.

---

## SECTION 4 — FAILURE MODE ANALYSIS

| Paper | Failure Mode | Nguyên nhân | Bài học cho V5 |
|---|---|---|---|
| **Yu_2017_SeqGAN** | Reward saturation → mode collapse | REINFORCE: reward ceiling → advantage→0 → gradient=0 → G freeze | Dùng Gumbel-Softmax: gradient không phụ thuộc advantage |
| **Atkinson_2024** | PPO thua REINFORCE (NLL: 9.065 vs 8.639) | KL penalty quá bảo thủ với non-stationary D reward signal | **Không dùng PPO** cho SeqGAN SQLi |
| **Pearson_2024** | WGAN gốc overfit, converge về local min | Không có gradient penalty → Lipschitz violation | Dùng WGAN-**GP** (thầy Lâm confirm) |
| **Dasari_2025** | CWGAN-GP cho R²=-1.7253 (negative!) | D quá mạnh → G không học được distribution | n_critic không cân bằng; cần theo dõi D_loss/G_loss ratio |
| **Rahman_2025** | Vanilla GAN không hội tụ trên network traffic | Không dùng WGAN-GP → gradient vanish khi D tốt | WGAN-GP là bắt buộc cho discrete/tabular data |
| **Lu_2022** | GA operators sinh syntactically invalid SQL | Crossover không respect SQL grammar structure | SQLParse validation sau mỗi mutation step |
| **Lin_2018_IDSGAN** | IDS evasion chỉ trên KDD'99 (outdated) | Dataset quá cũ, không reflect modern IDS | Dùng ML IDS model được train trên data hiện đại |
| **V1-V4 (bạn)** | Collapse tại step 800/2000/2500/750 | REINFORCE root cause → Gumbel solution | V5: Gumbel-Softmax target unique/64 > 40 |

### Pattern tổng hợp từ failures:

```
1. Gradient estimator kém → luôn collapse (V1-V4, Yu gốc)
2. D quá mạnh mà không có constraint → G không học (Dasari, Rahman)
3. PPO không phù hợp cho non-stationary reward (Atkinson)
4. Grammar-unaware mutation → invalid samples (Lu, Chowdhary)
5. Outdated dataset → kết quả không generalizable (Lin)
```

---

## SECTION 5 — PROPOSED ARCHITECTURE

### 5.1. Tại Sao Chọn Từng Component (Paper Evidence)

```
┌─────────────────────────────────────────────────────────────────────┐
│              SeqGAN + Gumbel-Softmax Architecture (V5)               │
│                                                                       │
│  Input: [attack_type ∈ {error,boolean,time,union}]                   │
│         [db_engine   ∈ {mysql,oracle,mssql,sqlite}]                  │
│                        │                                             │
│              Condition Embedding (dim=32)                            │
│              [Paper: Chen_2016_InfoGAN — conditional signal]         │
│                        │                                             │
│         BiLSTM Encoder (2 layers, hidden=512)                        │
│         [Paper: thầy Lâm gợi ý; capture SQL bidirectional context]   │
│                        │                                             │
│         LSTM Decoder (2 layers, step-by-step)                        │
│         [Paper: Yu_2017_SeqGAN — autoregressive generation]          │
│                        │                                             │
│         Gumbel-Softmax(logits, τ∈[0.5,1.0])                         │
│         [Paper: Jang_2017 — fixes REINFORCE mode collapse]           │
│         ↙ soft_tokens [B,T,V]    ↘ hard_tokens [B,T]                │
│         │                         │                                  │
│  ┌──────────────────┐      ┌───────────────────┐                    │
│  │ WGAN-GP Discrim. │      │    Re-lex + Eval  │                    │
│  │ CNN (k=1,2,3)    │      │ WAF oracle        │                    │
│  │ No BatchNorm ★   │      │ DB sandbox        │                    │
│  │ SpectralNorm (P2)│      │ AST entropy       │                    │
│  │ [Gulrajani_2017] │      │ IDS evasion       │                    │
│  │ [Miyato_2018 P2] │      │ [Lu_2022, Demetrio│                    │
│  │                  │      │  _2020, Lin_2018] │                    │
│  └────────┬─────────┘      └──────────┬────────┘                    │
│           │ W-distance                │ reward scalar               │
│           │                          │                              │
│  ┌────────┴──────────────────────────┴────────┐                    │
│  │         Composite Reward Signal             │                    │
│  │  G_loss = -D(soft) - 0.05H - 0.10×reward   │                    │
│  │  backprop qua soft_tokens (Gumbel ST)       │                    │
│  │  [Jang_2017: gradient always exists]        │                    │
│  └─────────────────────────────────────────────┘                    │
│                        │                                             │
│  ★ No BatchNorm: Gulrajani_2017 (GP requires independent samples)    │
└─────────────────────────────────────────────────────────────────────┘
```

### 5.2. Component Decision Table

| Component | Chosen | Alternative(s) | Paper Evidence | Reason |
|---|---|---|---|---|
| Generator backbone | BiLSTM | LSTM, Transformer | thầy Lâm, Yu_2017 | BiLSTM capture SQL bidirectional |
| Gradient estimator | Gumbel-Softmax STE | REINFORCE, PPO, SCST | Jang_2017, V1-V4 empirical | Root cause fix |
| Discriminator loss | WGAN-GP | Vanilla GAN, WGAN-clip | Gulrajani_2017, thầy Lâm | Lipschitz guarantee |
| D architecture | CNN multi-scale | RNN, Transformer | Yu_2017, Ahsan_2022 | Faster, n-gram aware |
| D normalization | LayerNorm (now) → SpectralNorm (P2) | BatchNorm (✗) | Miyato_2018, Gulrajani_2017 | BatchNorm vi phạm GP |
| Conditional signal | Embedding + InfoGAN (P1) | One-hot concat, FiLM | Chen_2016 | Enforce condition adherence |
| Post-processing | WAF-A-MoLE mutations (P1) | None, sqlmap tampers | Demetrio_2020 | OWASP bypass 2%→15-30% |
| Tokenization | delex_v2 (vocab=434) | character-level, BPE | Lu_2022, Sennrich_2016 | Low collision, SQL-aware |

### 5.3. Metrics Target (V5 vs V3)

| Metric | V3 step2000 (baseline) | V5 target | Paper justification |
|--------|----------------------|-----------|---------------------|
| Self-BLEU-3 | 0.9894 (collapse) | **< 0.70** | Gumbel diversity |
| Unique/64 (adversarial) | 6/64 | **> 40/64** | Gumbel + entropy reg |
| Composite (no-WAF) | 0.471 | **> 0.50** | Better gradient + data |
| OWASP bypass | 2.0% | **> 8%** | + WAF mutation P1 |
| Type accuracy | N/A (~45%) | **> 70%** | + InfoGAN P1 |
| Relex uniqueness (adv) | 0.008 (collapse) | **> 0.80** | Gumbel diversity |

---

## THAM KHẢO PAPERS

| Paper | Contribution đến V5 | Urgency |
|---|---|---|
| Yu_2017_SeqGAN | Framework foundation | Cite thesis |
| Jang_2017_Gumbel_Softmax | Core V5 change | Implement NOW |
| Gulrajani_2017_WGAN_GP | Discriminator | Already in V4 |
| Demetrio_2020_WAF_A_MoLE | Post-processing | P1 |
| Chen_2016_InfoGAN | Conditional loss | P1 |
| Guo_2018_LeakGAN | Future architecture | P2 |
| Miyato_2018_Spectral_Norm | D normalization | P2 |
| Lu_2022_GAN_SQLi | Closest prior work | Cite thesis |
