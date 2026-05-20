# Tổng Hợp Paper Bổ Trợ — SeqGAN-SQLi (Gumbel-Softmax + WGAN-GP + InfoGAN + WAF-A-MoLE)

- **Ngày**: 2026-05-18
- **Tác giả tổng hợp**: Pham Do Anh Minh (cho luận văn)
- **Tham chiếu kiến trúc**: `SeqGAN_SQLi/timeline/Guideline_2026_05_17.md`
- **Phạm vi**: 51 file ANALYSIS trong `Asset/Total_Analyst/`, đã loại duplicate
- **Bảng tra cứu kèm theo**: `Asset/RELATED_WORK_INDEX.csv`

> **Quy ước ký hiệu**: `(CORE · Ax · By)` = mức quan trọng (CORE/SUPPORT/CONTEXT) · nhóm chủ đề Phần A · component được justify Phần B. File ANALYSIS gốc luôn nằm trong `Asset/Total_Analyst/<filename>`.

---

## 0. Bản đồ một trang (One-page map)

| Component model (Phần B) | Paper CORE (trụ cột) | Paper SUPPORT (so sánh / baseline / ablation) |
|---|---|---|
| **B1. Data Pipeline** (delex_v2, dedup, type mapping) | Lee 2022 (Deduplicating) | Gilardi 2023 (LLM labeling), Halfond 2006 (SQLi taxonomy) |
| **B2. Tokenization & Vocab** (434 tokens whitelist) | Sennrich 2016 (BPE) | Feng 2020 (CodeBERT), Lu 2022 (SQLParse tokens) |
| **B3. Generator — BiLSTM + Gumbel-Softmax STE** | Jang 2017 (Gumbel-Softmax), Bengio 2013 (STE), Yu 2017 (SeqGAN framework) | Maddison 2017 (Concrete), Williams 1992 (REINFORCE — cái bị thay), Guo 2018 (LeakGAN), Fedus 2018 (MaskGAN) |
| **B4. Discriminator — CNN + WGAN-GP** | Gulrajani 2017 (WGAN-GP), Arjovsky 2017 (WGAN), Goodfellow 2014 (GAN gốc) | Miyato 2018 (Spectral Norm — alt), Yu 2017 (CNN-D), Lu 2022 (DCGAN+W cho SQLi) |
| **B5. Conditional Control — InfoGAN Q-network** | Chen 2016 (InfoGAN) | Xu 2019 (CTGAN conditional vector) |
| **B6. Reward Function** (WAF+DB+AST+IDS+novelty) | Williams 1992 (REINFORCE — vẫn dùng cho reward shaping), WAF-A-MoLE 2020 (WAF oracle) | Schulman 2017 (PPO — alt RL), Chowdhary 2023 sensors-23-08014 (CGAN+RL+ModSecurity), Le et al. GSQLi (FH0103) |
| **B7. Mutation Augmentation** (6 rules + Zenodo tamper) | WAF-A-MoLE 2020 | Lu 2022 (tamper scripts), GSQLi (FH0103 mutation actions) |
| **B8. Training Loop** (Warmup MLE → Adv → Reward FT) | Yu 2017 (3-phase đã có), Goodfellow 2014 (minimax) | Guo 2018 (interleaved MLE+GAN), Fedus 2018 (Actor-Critic baseline) |
| **B9. Evaluation** (composite, Self-BLEU-3, type acc) | de Rosa 2022 (Survey GAN-text — Self-BLEU), Yu 2017 (NLL oracle) | Lin 2018 IDSGAN (evasion rate), Zhao 2024 (Cosine + Cumulative Sum) |
| **B10. Baselines so sánh** | Xu 2019 (CTGAN), Yu 2017 (SeqGAN gốc) | Lin 2018 (IDSGAN — domain neighbor), Lu 2022 (GAN-SQLi DCGAN), Dasari 2025 (VAE+CWGAN-GP+U-Net SQLi) |

> Lưu ý đọc: paper xuất hiện nhiều lần trong các component vì 1 paper có thể justify nhiều phần. Chi tiết trong Phần B.

---

## PHẦN A — TỔNG HỢP THEO CHỦ ĐỀ HỌC THUẬT

Quy ước viết mỗi mục: **Nói gì** / **Chứng minh gì** / **Nói như nào** / **Áp dụng cho ta** / **File**. Paper SUPPORT và CONTEXT viết ngắn hơn (1–2 dòng).

### A1. Nền tảng GAN

#### Goodfellow et al. 2014 — Generative Adversarial Nets *(CORE · A1 · B4, B8)*
- **Nói gì**: Framework minimax 2-người: G (sinh từ nhiễu) đấu D (phân biệt thật/giả). Khi D tối ưu, G cực tiểu hóa Jensen-Shannon divergence.
- **Chứng minh**: GAN cạnh tranh với DBN/GSN trên MNIST/TFD bằng Parzen log-likelihood; không cần MCMC.
- **Nói như nào**: MLP G+D, Maxout trong D, Dropout. Loss `min_G max_D E[log D(x)] + E[log(1 - D(G(z)))]`.
- **Áp dụng cho ta**: Nền tảng để biện minh sự tồn tại của Generator + Discriminator trong thesis. Đề cập như "starting point" rồi dẫn sang WGAN-GP để giải thích lý do không dùng JS divergence cho discrete tokens.
- **File**: `Goodfellow_2014_GAN.md_ANALYSIS.md`

#### Arjovsky et al. 2017 — Wasserstein GAN *(CORE · A1 · B4)*
- **Nói gì**: Thay JS divergence bằng khoảng cách Wasserstein-1 (Earth-Mover). Critic phải là 1-Lipschitz → enforce bằng weight clipping `[-0.01, 0.01]`.
- **Chứng minh**: WGAN sinh ảnh ổn định cả trên kiến trúc không có BatchNorm; loss curve tương quan với chất lượng ảnh (điều JS không làm được).
- **Nói như nào**: RMSProp, n_critic=5, không sigmoid, output là score Wasserstein.
- **Áp dụng cho ta**: Justify chọn Wasserstein loss thay vì BCE để tránh vanishing gradient khi G và D khác mode (cực kỳ quan trọng với token rời rạc đã delex). Nhưng weight clipping thô → dùng WGAN-GP (Gulrajani) thay.
- **File**: `Arjovsky_2017_WGAN.md_ANALYSIS.md`

#### Gulrajani et al. 2017 — Improved Training of WGANs (WGAN-GP) *(CORE · A1 · B4, B7)*
- **Nói gì**: Thay weight clipping bằng gradient penalty `λ × (||∇D(x̂)||₂ − 1)²` với `λ=10`, x̂ nội suy giữa real và fake. Không dùng BatchNorm trong D (vì GP tính từng sample độc lập).
- **Chứng minh**: Inception Score CIFAR-10 = 7.86 (unsupervised). Train được ResNet-101 trong G mà không collapse. Áp dụng cả cho language modeling continuous-G.
- **Nói như nào**: Adam (β₁=0, β₂=0.9, lr=1e-4). Loss = `E[D(fake)] - E[D(real)] + λ × GP`.
- **Áp dụng cho ta**: **Discriminator của thesis chính xác là WGAN-GP** — Guideline §3.2 dùng nguyên công thức. Layer Normalization (không BatchNorm) trong D. Bài này là cái đã được "thầy Lâm confirm".
- **File**: `Gulrajani_2017_WGAN_GP.md_ANALYSIS.md`

#### Miyato et al. 2018 — Spectral Normalization *(SUPPORT · A1 · B4)*
- **Nói gì**: Chuẩn hóa ma trận trọng số D bằng spectral norm (giá trị riêng lớn nhất, ước lượng bằng power iteration). Ép Lipschitz toàn cục.
- **Chứng minh**: Inception Score vượt WGAN-GP + weight-clipping trên CIFAR-10 và ImageNet 128×128. Chi phí thêm ~10%.
- **Áp dụng cho ta**: **Alternative cho WGAN-GP**. Có thể nhắc trong phần "ablation đã cân nhắc": nếu WGAN-GP gặp khó train sâu thì swap sang Spectral Norm. Hiện tại Guideline không dùng → SUPPORT.
- **File**: `Miyato_2018_Spectral_Norm.md_ANALYSIS.md`

#### Chen et al. 2016 — InfoGAN *(CORE · A1 · B5)*
- **Nói gì**: Thêm latent code `c` (rời rạc/liên tục) vào input G, kèm Q-network ước lượng `c` từ G(z,c). Tối đa hóa mutual information `I(c; G(z,c))` qua variational lower bound.
- **Chứng minh**: Tự động disentangle yếu tố (chữ số/độ nghiêng/độ dày nét trên MNIST; kiểu tóc/cảm xúc trên CelebA) — không cần nhãn. Tỷ lệ lỗi MNIST 5% từ `c` zero-shot.
- **Nói như nào**: V_InfoGAN = V(D,G) − λ·L_I(G,Q). λ=1 cho rời rạc.
- **Áp dụng cho ta**: **Justify Q-network cho conditional control attack_type + db_engine** (Guideline §12). Ta share CNN giữa D và Q, đầu Q dự đoán `attack_type` (4 class) và `db_engine` (4 class). Mục tiêu: nâng type_accuracy 45% → >80%.
- **File**: `Chen_2016_InfoGAN.md_ANALYSIS.md`

---

### A2. Discrete Gradient Estimators (cốt lõi cho thay REINFORCE)

#### Jang, Gu, Poole 2017 — Categorical Reparameterization with Gumbel-Softmax *(CORE · A2 · B3)*
- **Nói gì**: Lấy mẫu categorical khả vi bằng cách thêm Gumbel noise + softmax có nhiệt độ `τ`: `y_i = exp((log π_i + g_i)/τ) / Σ`. Với `τ→0`, hội tụ về one-hot.
- **Chứng minh**: Trên SBN categorical đạt NLL 59.0 (vượt MuProp 63.0, DARN 67.9). Semi-supervised classification nhanh gấp 2–10× phương pháp marginalization.
- **Nói như nào**: τ annealing từ 1.0 → 0.5. Trade-off: τ thấp → gần discrete nhưng variance gradient cao; τ cao → smooth nhưng bias cao.
- **Áp dụng cho ta**: **Thay đổi cốt lõi của thesis** — thay REINFORCE bằng Gumbel-Softmax STE trong Generator (Guideline §2.1, §3.1). τ schedule: warmup `τ=1.0`, adversarial `τ = max(0.5, exp(-5e-5 × step))`. Đây là chìa khoá giải quyết mode collapse.
- **File**: `Jang_2017_Gumbel_Softmax.md_ANALYSIS.md`

#### Bengio, Léonard, Courville 2013 — Estimating or Propagating Gradients (STE) *(CORE · A2 · B3)*
- **Nói gì**: Đề xuất Straight-Through Estimator: forward pass dùng hàm ngưỡng cứng (argmax/threshold), backward giả vờ đạo hàm = 1 (identity). Biased nhưng low-variance, thực tế chạy tốt hơn REINFORCE.
- **Chứng minh**: 4 methods so sánh trên MNIST: STE đạt test error 1.39% — thấp nhất trong các phương pháp stochastic.
- **Áp dụng cho ta**: **STE Gumbel-Softmax** — Guideline §3.1: `hard = soft.detach().argmax(-1)`. Forward dùng hard cho re-lex/reward, gradient flow qua soft cho Discriminator. Bài này là nền tảng lý thuyết cho `hard=False` trong `F.gumbel_softmax`.
- **File**: `Bengio_2013_STE.md_ANALYSIS.md`

#### Maddison, Mnih, Teh 2017 — Concrete Distribution *(SUPPORT · A2 · B3)*
- **Nói gì**: Lý thuyết song song với Gumbel-Softmax. Đưa ra closed-form density trên simplex, chứng minh tính reparameterizable.
- **Chứng minh**: NLL trên MNIST/Omniglot cạnh tranh hoặc tốt hơn NVIL/VIMCO.
- **Áp dụng cho ta**: **Bằng chứng lý thuyết bổ sung** cho Gumbel-Softmax (Jang & Maddison ICLR 2017 trùng ý tưởng). Trích trong section "Discrete Gradient Estimators" của thesis để cho thấy đây là approach có cơ sở vững.
- **File**: `Maddison_2017_Concrete_Dist.md_ANALYSIS.md`

---

### A3. Sequence GAN cho text (framework chính của thesis)

#### Yu, Zhang, Wang, Yu 2017 — SeqGAN *(CORE · A3 · B3, B4, B6, B8)*
- **Nói gì**: Coi Generator (LSTM) là RL agent, action = chọn token tiếp theo. Discriminator (CNN multi-kernel) chỉ chấm chuỗi hoàn chỉnh → dùng Monte Carlo roll-out để ước lượng Q-value cho từng bước, cập nhật G bằng REINFORCE.
- **Chứng minh**: Trên synthetic LSTM-oracle: NLL thấp hơn MLE/Scheduled Sampling/PG-BLEU. Thơ tứ tuyệt Trung Quốc đạt gần ngưỡng người viết theo đánh giá chuyên gia. Pre-training MLE là bắt buộc.
- **Nói như nào**: G = LSTM, D = CNN với kernels 1–10 + Highway + max-over-time pool. MC search N=16 lần roll-out.
- **Áp dụng cho ta**: **Framework chính của thesis** — giữ nguyên kiến trúc G + D + Reward. Chỉ thay 1 thứ: REINFORCE → Gumbel-Softmax. Lý do thay: V1–V4 chứng minh empirical rằng REINFORCE gây mode collapse step ~2500 do `advantage → 0` (Guideline §1). Cũng giữ pre-train MLE 2,000 steps (val_ppl=1.74) như khuyến nghị của Yu 2017.
- **File**: `Yu_2017_SeqGAN.md_ANALYSIS.md`

#### Guo, Lu, Cai, Zhang, Yu, Wang 2018 — LeakGAN *(SUPPORT · A3 · B3, B6)*
- **Nói gì**: Hierarchical RL: MANAGER (LSTM) nhận "leaked features" từ CNN của D, sinh goal vector; WORKER (LSTM) chọn token dựa trên goal.
- **Chứng minh**: BLEU-2 trên Chinese Poems 0.881 vs SeqGAN 0.739. Vượt Turing test trên long text. Survey Rosa 2022 xác nhận.
- **Áp dụng cho ta**: **Baseline so sánh trong eval** (B10). Giải quyết sparse reward khác với cách Gumbel-Softmax — nhắc trong related work để cho thấy ta đã cân nhắc Hierarchical RL nhưng chọn approach đơn giản hơn (Gumbel) vì lý do training stability đã chứng minh trên SQLi domain.
- **File**: `Guo_2018_LeakGAN.md_ANALYSIS.md`

#### Fedus, Goodfellow, Dai 2018 — MaskGAN *(SUPPORT · A3 · B6, B8)*
- **Nói gì**: Actor-Critic Conditional GAN cho text in-filling. Tạo dense reward tại mỗi time step (thay vì chỉ end-of-sequence) — giải quyết exposure bias + credit assignment.
- **Chứng minh**: Human eval thắng MLE 58% vs 40% trên IMDB. Perplexity *cao hơn* MLE nhưng chất lượng mẫu tốt hơn → **misconception**: PPL thấp ≠ chất lượng tốt.
- **Áp dụng cho ta**: **Cơ sở lý thuyết cho việc dùng learned baseline (Critic)** giảm variance — ta dùng entropy regularization để giải quyết tương tự. Cũng justify thiết kế reward function của ta vốn cũng "dense" theo từng payload.
- **File**: `Fedus_2018_MaskGAN.md_ANALYSIS.md`

#### Nie, Narodytska, Patel 2019 — RelGAN *(SUPPORT · A3 · B3)*
- **Nói gì**: Relational Memory + Gumbel-Softmax + multiple embedded representations trong D. 3 components chính: (1) Relational Memory-based generator cho long-distance dependency, (2) Gumbel-Softmax relaxation thay RL heuristics, (3) multiple embeddings trong D cho diverse signal.
- **Chứng minh**: Outperforms SOTA text GANs về sample quality và diversity trên COCO. Là architecture đầu tiên chứng minh Gumbel-Softmax có thể sinh realistic text. Ablation: mỗi component đều critical.
- **Áp dụng cho ta**: **Bằng chứng mạnh cho Gumbel-Softmax approach** (thay REINFORCE) đã được ICLR 2019 công nhận. RelMemory là hướng mở rộng nếu cần long-text generation sau thesis. Multiple-embed D gợi ý cải tiến D hiện tại (single embedding).
- **File**: `Nie_2019_RelGAN.md_ANALYSIS.md`

#### Zhang et al. 2020 — Adversarial Attacks on DL Models in NLP *(CONTEXT · A3 · B6)*
- **Nói gì**: Comprehensive survey về adversarial attacks trong NLP. Phân loại: (1) target (classification/generation/sequence), (2) perturbation granularity (character/word/sentence), (3) attack method (gradient/population/feature).
- **Áp dụng cho ta**: **Background cho adversarial evaluation** của thesis. Taxonomies giúp framing "adversarial text generation" trong NLP context. Dataset/modelling discussion gợi ý metric cho reward function.
- **File**: `Zhang_2020_Adversarial_Text_Survey.md_ANALYSIS.md`

#### de Rosa & Papa 2022 — A Survey on Text Generation using GANs *(CORE · A3 · B9)*
- **Nói gì**: Phân loại 3 hướng giải quyết tính rời rạc: (1) Gumbel-Softmax (GSGAN, RelGAN, Meta-CoTGAN), (2) RL/Policy Gradient (SeqGAN, LeakGAN, MaskGAN, SentiGAN), (3) Modified Objectives (TextGAN, FM-GAN). Bảng BLEU-2 đầy đủ.
- **Chứng minh**: LeakGAN 0.881 (Chinese Poems), RelGAN 0.849 (COCO). Trend chuyển sang Transformer + Pre-trained LMs.
- **Áp dụng cho ta**: **Justify chọn Gumbel-Softmax (hướng 1) thay vì RL (hướng 2)** trong thesis. Cũng cung cấp danh sách metric chuẩn (Self-BLEU cho diversity) — ta dùng Self-BLEU-3 với target <0.70 (Guideline §7.1).
- **File**: `Rosa_2022_Survey_Text_GAN.md_ANALYSIS.md`

#### Atkinson 2024 / Rodriguez 2024 / Pearson 2024 — Advancements in Sequence Generation *(CONTEXT · A3)*
- **Nói gì**: 3 technical disclosure parallel — thử kết hợp SeqGAN với WGAN + PPO. Improved WGAN (I-WGAN) đạt NLL 8.509 vs SeqGAN gốc 8.639.
- **Áp dụng cho ta**: **Bằng chứng cộng đồng** rằng hướng kết hợp SeqGAN + WGAN là khả thi. Lưu ý quan trọng: bài này báo cáo PPO *kém hơn* REINFORCE trên discrete sequence — củng cố quyết định không thử PPO trong thesis.
- **Files**: `Atkinson_2024_Advancements_SeqGAN.md_ANALYSIS.md`, `Rodriguez_2024_GAN_RL.md_ANALYSIS.md`, `Pearson_2024_Enhancing_SeqGAN.md_ANALYSIS.md`

---

### A4. Reinforcement Learning trong text generation

#### Williams 1992 — REINFORCE *(CORE · A4 · B3 (cái bị thay), B6)*
- **Nói gì**: Policy Gradient nguyên thuỷ: `Δw ∝ (r − b) × ∂log π/∂w`. Baseline `b` giảm variance, không thiên kiến gradient.
- **Chứng minh**: Định lý 1 — hill-climbing trên expected reward surface (unbiased).
- **Áp dụng cho ta**: **Cái bị thay** trong thesis. Nhưng vẫn justify reward shaping trong Phase 3 (Reward Fine-tuning) khi D bị freeze — ta dùng entropy-regularized REINFORCE-style update với baseline EMA. Trích để giải thích "tại sao V1–V4 collapse": variance cao + advantage → 0.
- **File**: `Williams_1992_REINFORCE.md_ANALYSIS.md`

#### Schulman et al. 2017 — PPO *(SUPPORT · A4)*
- **Nói gì**: Clipped surrogate objective `L^CLIP = E[min(r_t·A_t, clip(r_t, 1-ε, 1+ε)·A_t)]` với ε≈0.2. Giới hạn cập nhật policy mà không cần KL constraint phức tạp như TRPO.
- **Chứng minh**: Vượt TRPO/A2C trên MuJoCo và Atari, đơn giản hơn nhiều.
- **Áp dụng cho ta**: **Alternative đã cân nhắc và loại** (xem Atkinson 2024 — PPO kém REINFORCE trên discrete). Ghi vào related work để chứng minh đã đánh giá đầy đủ phương án RL hiện đại.
- **File**: `Schulman_2017_PPO.md_ANALYSIS.md`

---

### A5. Tabular / Imbalance / CGAN oversampling

#### Xu et al. 2019 — CTGAN *(CORE · A5 · B5, B10)*
- **Nói gì**: 2 đóng góp: (1) Mode-Specific Normalization (VGM cho từng cột continuous → `(α scalar, β one-hot mode)`); (2) Conditional Generator + Training-by-sampling theo log-frequency để xử lý class imbalance.
- **Chứng minh**: ML efficacy vượt MedGAN, VeeGAN, TableGAN; mode-specific norm tăng 25.7% hiệu suất; Conditional vector tăng 36.5% trên imbalanced data. PacGAN size=10 chống mode collapse.
- **Nói như nào**: WGAN-GP loss, Adam lr=2e-4, batch=500, MLP 2 hidden 256.
- **Áp dụng cho ta**: **Baseline bắt buộc trong eval** (yêu cầu thầy Lâm — Guideline §7.2). Đại diện cho approach tabular thuần tuý vs approach sequence-based của ta. Cũng gợi ý conditional vector — tương tự cách ta dùng `attack_type + db_engine` embedding.
- **File**: `Xu_2019_CTGAN.md_ANALYSIS.md`

#### Strelcenia & Prakoonwit 2023 — Survey GAN for Credit Fraud *(CONTEXT · A5)*
- **Nói gì**: Survey GAN variants cho tabular imbalanced data: Duo-GAN, CTAB-GAN, OCAN, Majority-Minority transfer.
- **Áp dụng cho ta**: Reference cho "tại sao GAN trong tabular thay vì SMOTE" — luận điểm "GAN học phân phối thật" (không chỉ nội suy tuyến tính).
- **File**: `Strelcenia_2023_GAN_Survey_Credit.md_ANALYSIS.md`

#### Jamoos et al. 2023 — TDCGAN (Triple Discriminator CGAN) *(CONTEXT · A5)*
- **Nói gì**: 1 G + 3 D với kiến trúc khác nhau + Election Layer. Tránh D hội tụ quá nhanh.
- **Chứng minh**: UGR'16 NIDS, Acc 0.95 vs CTGAN 0.76.
- **Áp dụng cho ta**: Ý tưởng multi-D có thể là extension tương lai (post-thesis), không cần trong V5.
- **File**: `Jamoos_2023_TDCGAN.md_ANALYSIS.md`

#### Udu et al. 2025 — SMOTE & GAN Variants Review *(CONTEXT · A5)*
- **Nói gì**: Phân loại imbalanced (intrinsic/extrinsic, global/local, absolute/relative). Liệt kê biến thể SMOTE & GAN.
- **Áp dụng cho ta**: Giúp framing chương 2 "background imbalanced learning". Lưu ý local imbalance — phù hợp khi SQLi imbalance theo từng db_engine.
- **File**: `Udu_2025_SMOTE_GAN_Review.md_ANALYSIS.md`

#### Scott 2019 — GAN-SMOTE *(CONTEXT · A5)*
- **Nói gì**: GAN-SMOTE cho dataset cực nhỏ (n=70 petrography). Minibatch discrimination, bit-flips, SGDR cosine annealing chống mode collapse.
- **Áp dụng cho ta**: Tham khảo các kỹ thuật ổn định khi small data — relevant cho giai đoạn đầu của ta (Gold 662 rows trước khi mở rộng sang RbSQLi 10M).
- **File**: `Scott_2019_GAN_SMOTE.md_ANALYSIS.md`

#### Khoirunnisa & Rosyda 2025 — SMOTE+CTGAN Hybrid Medical *(CONTEXT · A5)*
- **Nói gì**: Hybrid SMOTE → train CTGAN → sinh thêm. So sánh recall minority/majority.
- **Áp dụng cho ta**: SMOTE recall minority cao hơn (0.85) nhưng phá majority (0.84); CTGAN bảo thủ hơn (0.71-0.75) nhưng giữ majority >0.90. Tradeoff để cân nhắc khi tinh chỉnh resample.
- **File**: `Khoirunnisa_2025_SMOTE_CTGAN.md_ANALYSIS.md`

#### Emaan 2025 — T-GAN (Transformer-Enhanced GAN) *(CONTEXT · A5)*
- **Nói gì**: Transformer encoder trong Generator FastGAN. Self-attention học correlation feature.
- **Áp dụng cho ta**: Hướng mở rộng tương lai (Transformer Generator thay BiLSTM). Hiện thesis giữ BiLSTM theo yêu cầu thầy.
- **File**: `Emaan_2025_T_GAN.md_ANALYSIS.md`

#### Julianti et al. 2024 — CTGAN + Decision Tree (Student Graduation) *(CONTEXT · A5)*
- **Nói gì**: CTGAN cho dữ liệu giáo dục, đạt 99% accuracy. Ghi nhận: 99% có thể là overfit do dataset nhỏ.
- **Áp dụng cho ta**: Cảnh báo về việc đánh giá overfitting khi báo cáo metric quá cao trên synthetic data.
- **File**: `Julianti_2024_CTGAN_Graduation.md_ANALYSIS.md`

---

### A6. IDS / Network Security GAN

#### Lin et al. 2018 — IDSGAN *(CORE · A6 · B10)*
- **Trạng thái**: File ANALYSIS gốc đã đọc qua các paper khác, nhưng entry chi tiết không có trong batch này. Chính file: `Lin_2018_IDSGAN.md_ANALYSIS.md` — nội dung từ context: Wasserstein GAN sinh malicious traffic vượt qua black-box IDS, chia 4 nhóm feature (intrinsic/content/time-based/host-based), chỉ modify nhóm "non-functional" để giữ tính tấn công.
- **Áp dụng cho ta**: **Baseline domain-neighbor**: IDSGAN ở network flow level, ta ở SQL syntax level. Trích trong related work để chứng minh GAN-evasion attack đã được proven trong cybersecurity, ta extend sang ứng dụng layer.
- **File**: `Lin_2018_IDSGAN.md_ANALYSIS.md`

#### Alauthman et al. 2026 — GAN for IDS Survey *(CORE · A6 · B6, B9)*
- **Nói gì**: Survey comprehensive nhất 2026. Phân loại GAN variants: Vanilla, WGAN, CGAN, DCGAN, SAGAN, ACGAN, CTGAN, qGAN. 3 ứng dụng: Data Augmentation, Adversarial Training, Anomaly Detection. Dataset: NSL-KDD, UNSW-NB15, CIC-IDS2017, CSE-CIC-IDS2018, BoT-IoT, CICIoT2023.
- **Áp dụng cho ta**: **Reference chính cho chương 2 Related Work**. Đặt thesis vào bức tranh tổng "GAN for cybersecurity" — ta là Adversarial Training subtype (sinh payload để augment + test WAF).
- **File**: `Alauthman_2026_GAN_IDS_Survey.md_ANALYSIS.md`

#### Peppes et al. 2025 — BNGAN (Botnet) *(CONTEXT · A6)*
- **Nói gì**: 8-layer GAN cho dữ liệu botnet CTU-13, sinh 200k+ mẫu.
- **Áp dụng cho ta**: Evaluation methodology — cumulative sums, correlation matrices để verify synthetic.
- **File**: `Peppes_2025_BNGAN.md_ANALYSIS.md`

#### Zhao et al. 2024 — WGAN cho CIC-IDS2017 Botnet *(SUPPORT · A6 · B9)*
- **Nói gì**: Vanilla GAN vs WGAN vs CTGAN trên Botnet class. Chia nhỏ data theo port trước khi sinh → giảm mode collapse.
- **Chứng minh**: F1 Botnet 0.60 → 0.90 với 99× WGAN samples. Recall 0.46 → 0.82.
- **Áp dụng cho ta**: **Bằng chứng số** rằng WGAN trên security data hiệu quả. Strategy "chia nhỏ theo port" — analogue: ta chia theo `attack_type × db_engine` (Guideline §4.2).
- **File**: `Zhao_2024_WGAN_Botnet.md_ANALYSIS.md`

#### Ahsan et al. 2022 — CGAN-based oversampling for anomaly detection *(CONTEXT · A6 · B10)*
- **Nói gì**: CGAN + Reinforcement Learning hybrid oversampling cho anomaly detection trên IDS datasets. So sánh CGAN-based oversampling với SMOTE, ADASYN trên Naive Bayes, MLP, Random Forest, Logistic Regression.
- **Áp dụng cho ta**: **Baseline tham khảo** cho CGAN approach trong IDS domain. Cho thấy CGAN oversampling cải thiện đáng kể so với SMOTE truyền thống trên dữ liệu mất cân bằng.
- **File**: `Ahsan_2022_Comparative_CGAN.md_ANALYSIS.md`

#### Rahman, Francia, Shahriar 2025 — Leveraging GANs for IDS (UNSW-NB15) *(CONTEXT · A6)*
- **Nói gì**: Vanilla GAN + Random Forest, UNSW-NB15. RF gốc 97.58% → RF+GAN 98.27%.
- **Áp dụng cho ta**: Reference cho approach "GAN augment + downstream classifier" — pattern phổ biến.
- **File**: `Rahman_2025_Leveraging_GANs_IDS.md_ANALYSIS.md`

#### Nawaz et al. 2025 — CTGAN trên CICIDS2017 Web Attacks *(CONTEXT · A6 · B10)*
- **Nói gì**: CTGAN cho Brute Force + Web Attacks. Recall Web Attacks 28% → 91% (RF), 32% → 94% (XGBoost).
- **Áp dụng cho ta**: Đặc biệt relevant vì Web Attacks ≈ class chứa SQLi. Tham khảo cho mục evaluation gain.
- **File**: `Nawaz_2025_CTGAN_Web_Attacks.md_ANALYSIS.md`

#### Le et al. 2024 — Hybrid Sampling for Multiclass IDS *(CONTEXT · A6)*
- **Nói gì**: BorderlineSMOTETomek + XGBoost trên CHADC2020/IoTID20, F1 > 98%.
- **Áp dụng cho ta**: Reference cho mục "hybrid SMOTE+GAN vs pure GAN" trong related work.
- **File**: `Le_2024_Hybrid_Sampling_IDS.md_ANALYSIS.md`

#### Agrawal et al. 2024 — Review Generative Models for Cybersecurity *(CONTEXT · A6)*
- **Nói gì**: Critical review — chỉ ra GAN-generated network attack data thường mất correlation giữa features → là noise hơn là attack thật.
- **Áp dụng cho ta**: **Cảnh báo quan trọng** — ta phải verify synthetic SQLi vẫn execute được trên DB sandbox (đây là lý do reward function của ta có `db_execution_rate` 0.25 weight).
- **File**: `Agrawal_2024_GenAI_Synthetic.md_ANALYSIS.md`

#### Blondé & Kalousis 2019 — SAM (Sample-Efficient GAIL) *(CONTEXT · A6)*
- **Nói gì**: Off-policy GAIL với replay buffer, giảm sample complexity 1-2 orders.
- **Áp dụng cho ta**: Reference cho hướng future work "Off-policy GAN cho SQLi attack" — đặc biệt khi WAF query rate-limited.
- **File**: `Blonde_2019_SAM_GAIL.md_ANALYSIS.md`

---

### A7. SQLi domain (paper trọng yếu nhất cho thesis)

#### Demetrio et al. 2020 — WAF-A-MoLE *(CORE · A7 · B6, B7)*
- **Nói gì**: Mutational fuzzer guided-search với 7 mutation operators (CS, WS, CI, CR, IE, OS, LI) + priority queue dựa trên confidence score WAF. Bảo toàn semantics, chỉ thay đổi cú pháp.
- **Chứng minh**: Bypass 100% WAF-Brain (GRU), Token-based RF/SVM. SQLiGoT (graph) là khó nhất nhưng vẫn bị bypass. Bypass trong vài giây.
- **Áp dụng cho ta**: **Trụ cột thứ 2 của thesis** (Guideline §11). 6 mutation rules được port nguyên: space, comment, case, urlencode, dbl_enc, equiv. Zenodo tamper_method (7 methods) làm "mutation training set" để học mutation nào bypass tốt cho từng payload type. Tích hợp augment replay buffer mỗi 500 G steps. Kỳ vọng OWASP bypass 2-10% → 15-30%.
- **File**: `Demetrio_2020_WAF_A_MoLE.md_ANALYSIS.md`

#### Dasari, Badii, Moin, Ashlam 2025 — Enhancing SQLi Detection (VAE + CWGAN-GP + U-Net) *(CORE · A7 · B10)*
- **Nói gì**: Pipeline: FastText embedding → VAE (latent 448-d) → U-Net + CWGAN-GP sinh mẫu → KMeans pseudo-label → XGBoost classifier. Optuna tuning.
- **Chứng minh**: XGBoost đạt 98% validation. Optimal blend: 80% U-Net + 70% CWGAN-GP synthetic + real data.
- **Áp dụng cho ta**: **Đối thủ trực tiếp nhất 2025**. So sánh: ta dùng SeqGAN+Gumbel sinh trực tiếp tokens; họ dùng VAE+CWGAN-GP+U-Net sinh trong latent space. Trích trong gap analysis: ta khác họ ở (1) sinh token rời rạc trực tiếp, (2) reward đa thành phần (WAF+DB+AST), (3) conditional theo attack_type/db_engine.
- **File**: `Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md`

#### Le Minh Khan et al. 2024 — GSQLi (UIT VNU-HCM) *(CORE · A7 · B6, B7, B10)*
- **Nói gì**: Customized CGAN sinh **Mutation Actions** (không sinh chuỗi text). Input = Noise + 15-d Mutation Vector. Discriminator học từ Attack Classifier (CNN oracle). Libinjection để token-ize.
- **Chứng minh**: ModSecurity FNR 2.3% (SSHS) / 0.19% (HttpParams). Bypass RNN/GRU/BiLSTM ML-WAFs xuống ~88% TPR.
- **Áp dụng cho ta**: **Domestic baseline số 1** (cùng UIT, cùng SQLi, cùng GAN). Gap với ta: họ sinh mutation actions; ta sinh tokens trực tiếp + có conditional + có WAF-A-MoLE post-augment. Phải trích trong related work, có thể compare side-by-side trong eval nếu lấy được code.
- **File**: `Le_2024_GSQLi.md_ANALYSIS.md`

#### Lu, Fei, Liu, Li 2022 — GAN-based SQLi (GA + WGAN/DCGAN) *(CORE · A7 · B4, B7, B10)*
- **Nói gì**: GA tiến hoá initial population (SQL keywords) → DCGAN sinh biến thể với W-distance → tamper scripts cho obfuscation. SQLParse evaluate cú pháp.
- **Chứng minh**: Trên sqli-lab + SafeDog V4.0 WAF. Bypass Error-based/Integer/Boolean-blind/Header Injection. Thất bại trên `Dump into outfile`, Second Degree.
- **Áp dụng cho ta**: **Baseline trực tiếp**. Ta khác họ: (1) thay GA+DCGAN bằng SeqGAN+Gumbel (đầu-cuối, không cần GA pre-filter), (2) ta có conditional InfoGAN, (3) ta có reward đa thành phần với DB sandbox. Trích để justify "tại sao không dùng GA pre-filter": vì delex_v2 + function whitelist đã đảm bảo cú pháp.
- **File**: `Lu_2022_GA_WGAN_SQLi.md_ANALYSIS.md`

#### Chowdhary, Jha, Zhao 2023 — GAN-based Autonomous Penetration Testing (Sensors) *(CORE · A7 · B3, B6, B7)*
- **Nói gì**: Conditional SeqGAN + Semantic Tokenization + BPE cho XSS payload. Test trên ModSecurity và AWS WAF thật.
- **Chứng minh**: ModSecurity bypass 12%, AWS WAF 8%.
- **Áp dụng cho ta**: **Paper rất gần thesis** về phương pháp (SeqGAN + conditional + WAF test). Khác biệt: họ XSS, ta SQLi; họ tokenization semantic, ta delex_v2 + BPE potential; họ chưa Gumbel-Softmax. Trích để chứng minh hướng "conditional SeqGAN cho web attack" đã có precedent.
- **File**: `Chowdhary_2023_GAN_Pentesting.md_ANALYSIS.md`

#### Trương Thị Hoàng Hảo et al. (UIT NT204 đồ án 2023) — CTGAN cho IDS Imbalance *(CONTEXT · A7)*
- **Nói gì**: CTGAN trên CICIDS2017, sinh 10k mẫu cho Bot/Infiltration/Heartbleed. Acc 99.87% với CTGAN vs 99.85% SMOTE.
- **Áp dụng cho ta**: Đồ án cùng trường, cùng dataset family. Reference local cho phần "tabular GAN baseline".
- **File**: `Truong_2023_CTGAN_IDS.md_ANALYSIS.md`

#### Hà Thị Minh Phương 2023 — GAN cho Software Fault Prediction (ĐH Đà Nẵng) *(CONTEXT · A7)*
- **Nói gì**: VanillaGAN/CTGAN/WGAN-GP cho dữ liệu lỗi phần mềm PROMISE. Kết hợp feature selection (Chi-squared, GA, PSO).
- **Áp dụng cho ta**: Reference cho approach "feature selection + GAN" trên dữ liệu bảng — tham khảo cho phần data pipeline nếu cần lọc features từ Zenodo (tamper_method + attack_technique + 13 cột khác).
- **File**: `Ha_2023_GAN_Fault_Prediction.md_ANALYSIS.md`

---

### A8. NLP-to-SQL / Tokenization / Embedding bổ trợ

#### Sennrich, Haddow, Birch 2016 — BPE *(CORE · A8 · B2)*
- **Nói gì**: Byte-Pair Encoding chia từ thành sub-word units bằng cách lặp merge cặp ký tự xuất hiện nhiều nhất. Open-vocabulary.
- **Chứng minh**: +1.1 BLEU EN-DE, +1.3 BLEU EN-RU vs back-off dictionary. Đặc biệt hiệu quả với rare words và tên riêng.
- **Áp dụng cho ta**: **Tokenization baseline cho thesis**. Hiện ta dùng delex_v2 + function whitelist (vocab=434). Trong related work: trích BPE để giải thích "tại sao không dùng BPE thuần" — vì BPE không hiểu cấu trúc SQL (cắt random ở giữa keyword), trong khi delex_v2 đảm bảo mỗi token là 1 SQL function/keyword hợp lệ.
- **File**: `Sennrich_2016_BPE.md_ANALYSIS.md`

#### Feng et al. 2020 — CodeBERT *(SUPPORT · A8)*
- **Nói gì**: Transformer pre-trained bimodal (NL + 6 ngôn ngữ PL) với MLM + Replaced Token Detection. CodeSearchNet 2.1M bimodal + 6.4M unimodal.
- **Chứng minh**: SOTA code search và doc generation.
- **Áp dụng cho ta**: Hướng future work — dùng CodeBERT làm Discriminator pre-trained để chấm "SQL có giống code thật không". Hiện thesis dùng CNN-D từ đầu.
- **File**: `Feng_2020_CodeBERT.md_ANALYSIS.md`

#### Hwang et al. 2019 — SQLova *(CONTEXT · A8 · B2)*
- **Nói gì**: Text-to-SQL model đầu tiên đạt human performance trên WikiSQL. BERT + table-aware word contextualization + seq2seq-style decoder. Logical form 83.69%, execution 89.69%.
- **Áp dụng cho ta**: Tham khảo cho phần tokenization và SQL domain knowledge. Cho thấy BERT có thể hiểu cấu trúc bảng (table-aware) — relevant nếu sau này fine-tune CodeBERT cho SQLi detection.
- **File**: `Hwang_2019_SQLova.md_ANALYSIS.md`

---

### A9. Data Engineering / Labeling

#### Lee et al. 2022 — Deduplicating Training Data Makes LMs Better *(CORE · A9 · B1)*
- **Nói gì**: Suffix Array (exact substring >50 tokens) + MinHash (near-duplicate Jaccard). Khử 19% C4 → giảm memorization 10×, không giảm perplexity.
- **Chứng minh**: 1 câu 61-từ xuất hiện >60,000 lần trong C4. Train/test overlap RealNews 14.4%.
- **Áp dụng cho ta**: **Justify bước dedup trong data pipeline** (Guideline §13 — RBSQLi 10M rows). Khi mở rộng dataset, áp suffix array SHA-256 dedup, kỳ vọng ~30% reduction (sqliv5 trùng nhiều Kaggle sources).
- **File**: `Lee_2022_Deduplicating.md_ANALYSIS.md`

#### Gilardi, Alizadeh, Kubli 2023 — ChatGPT Outperforms Crowd-Workers *(CORE · A9 · B1)*
- **Nói gì**: GPT-3.5 zero-shot đạt accuracy text annotation cao hơn MTurk 25%, intercoder agreement 97% (vs 79% trained, 56% MTurk). Cost ~$0.003/label, rẻ 30×.
- **Áp dụng cho ta**: **Justify dùng Claude/LLM labeling cho 40k SQLi rows** (Guideline §13). Đặc biệt khi sources_agree 0/3 = 55% (không Haiku source). Có thể dùng LLM làm "source thứ 3" để nâng confidence.
- **File**: `Gilardi_2023_ChatGPT_Labeling.md_ANALYSIS.md`

---

### A10. Tham khảo mở rộng / OCR lỗi

| File | Lý do |
|------|------|
| `Lu_2022_GAN_SQLi.md_ANALYSIS.md` | OCR mismatch → Pokemon GAN VN. Lu2022 real đã có ở `Lu_2022_GA_WGAN_SQLi.md_ANALYSIS.md` |
| Các duplicate `{Author}_{Year}.md_ANALYSIS.md` vs `{Author}_{Year}_{Method}.md_ANALYSIS.md` | Trùng nội dung — đã merge trong CSV với cờ `duplicate_of:` |

---

## PHẦN B — MAPPING NGƯỢC: COMPONENT MODEL → PAPER JUSTIFY

### B1. Data Pipeline (delex_v2 + benign + dedup + type mapping)
- **Quyết định**: 4-step pipeline (Triage → Relabel → Strip+Delex → Tier), thêm dedup SHA-256 cho 10M+ dataset RbSQLi.
- **Paper foundation**: 
  - `Lee_2022_Deduplicating` (A9) → dedup methodology.
  - `Gilardi_2023_ChatGPT_Labeling` (A9) → LLM labeling như source thứ 3.
  - `WAF-A-MoLE` (A7) → Zenodo tamper_method = 7 ground-truth mutations cho training mutation selector.
- **Alternative đã loại**: SMOTE-style nội suy (không phù hợp text rời rạc — xem Udu 2025 critique).
- **Reference Guideline**: §4.1, §13.

### B2. Tokenization & Vocab (434 tokens, function whitelist)
- **Quyết định**: Custom SQL tokenizer + function whitelist (xmltype, pg_sleep, group_concat...). Collision rate 71.89% → 4.33% sau delex_v2.
- **Paper foundation**: 
  - `Sennrich_2016_BPE` (A8) → reference cho sub-word approach, ta không dùng vì BPE không hiểu cấu trúc SQL.
  - `Feng_2020_CodeBERT` (A8) → BPE-based code tokenization (alt).
  - `Lu_2022` (A7) → SQLParse-based tokenization (gần với ta nhất).
- **Reference Guideline**: §4.2.

### B3. Generator — BiLSTM encoder + LSTM decoder + Gumbel-Softmax STE
- **Quyết định**: Giữ kiến trúc V4 (BiLSTM 2-layer encoder + LSTM 2-layer decoder, embed=256, hidden=512), thay `multinomial sampling + REINFORCE` bằng `F.gumbel_softmax(τ, hard=False)` + STE.
- **Paper foundation**:
  - `Yu_2017_SeqGAN` (A3) → framework G+D+Reward.
  - `Jang_2017_Gumbel_Softmax` (A2) → reparameterization trick.
  - `Bengio_2013_STE` (A2) → STE cho discrete forward + soft backward.
  - `Maddison_2017_Concrete_Dist` (A2) → bằng chứng lý thuyết song song.
- **Alternative đã loại**:
  - REINFORCE thuần (`Williams_1992`): empirical proven collapse step 2500 trên SQLi V1-V4.
  - PPO (`Schulman_2017`): Atkinson 2024 cho thấy PPO kém hơn REINFORCE trên discrete sequence.
  - Hierarchical RL (`Guo_2018_LeakGAN`): phức tạp, chưa cần thiết cho payload ngắn (~20-40 tokens).
- **Reference Guideline**: §2.2, §3.1, §3.5 (Implementation Delta — chỉ ~60 dòng code).

### B4. Discriminator — CNN multi-kernel + WGAN-GP
- **Quyết định**: CNN multi-kernel (size 1,2,3) + max-pool + dense, output 1 scalar Wasserstein score (không sigmoid). Gradient Penalty λ=10, không BatchNorm.
- **Paper foundation**:
  - `Gulrajani_2017_WGAN_GP` (A1) → công thức chính, được thầy Lâm confirm.
  - `Arjovsky_2017_WGAN` (A1) → cơ sở Wasserstein.
  - `Yu_2017_SeqGAN` (A3) → CNN multi-kernel architecture.
  - `Goodfellow_2014_GAN` (A1) → minimax background.
- **Alternative đã cân nhắc**: `Miyato_2018_Spectral_Norm` — chưa swap, dự phòng nếu WGAN-GP collapse.
- **Reference Guideline**: §3.2.

### B5. Conditional Control — InfoGAN Q-network (attack_type + db_engine)
- **Quyết định**: Q-network chia sẻ CNN encoder với D, 2 đầu (attack_head 4 class, db_head 4 class). Loss G += `0.2 × q_loss` (CE).
- **Paper foundation**:
  - `Chen_2016_InfoGAN` (A1) → mutual information maximization, Q-network.
  - `Xu_2019_CTGAN` (A5) → conditional vector (alt).
- **Mục tiêu định lượng**: type accuracy 45% → >80%, db accuracy 30% → >70% (Guideline §12).
- **Reference Guideline**: §12.

### B6. Reward Function — D_score + WAF + DB exec + AST entropy + IDS evasion + novelty
- **Quyết định**: `reward = 0.30·waf + 0.25·db_exec + 0.20·ast_h + 0.15·ids_evasion + 0.10·novelty`. Áp dụng cho hard tokens sau re-lex.
- **Paper foundation**:
  - `Williams_1992_REINFORCE` (A4) → policy gradient cho reward shaping trong Phase 3.
  - `WAF-A-MoLE` (A7) → WAF oracle methodology.
  - `Lin_2018_IDSGAN` (A6) → IDS evasion metric.
  - `Lu_2022` (A7), `Chowdhary_2023_sensors` (A7) → multi-component reward đã được chứng minh.
- **Alternative**: pure adversarial loss (chỉ D score) — không bảo đảm payload thực sự exploit; pure WAF reward — không học diversity.
- **Reference Guideline**: §3.3.

### B7. Mutation Augmentation — WAF-A-MoLE 6 rules + Zenodo tamper map
- **Quyết định**: Post-processing sau G sinh payload. 6 mutation rules (space, comment, case, urlencode, dbl_enc, equiv). Mỗi 500 G steps, gọi `augment_replay_buffer()`, lấy top-3 mutants có score >0.7.
- **Paper foundation**:
  - `WAF-A-MoLE` (A7) → mutation operators chính.
  - `Lu_2022` (A7) → tamper scripts approach.
  - `FH0103/GSQLi` (A7) → Mutation Actions.
- **Reference Guideline**: §11.
- **Kỳ vọng**: OWASP bypass 2-10% → 15-30%.

### B8. Training Loop — 3-phase (Warmup MLE → Adversarial → Reward Fine-tune)
- **Phase 1 (Warmup, 2k steps)**: MLE pretrain, τ=1.0, val_ppl≤2.0.
- **Phase 2 (Adversarial, 12k steps)**: n_critic=5 (WGAN), τ annealing exp(-5e-5·step), mixed loss `-D(soft) - 0.05·H - 0.10·reward`.
- **Phase 3 (Reward Fine-tune, 6k steps)**: Freeze D, `-reward + 0.05·H`, τ=0.5 fixed.
- **Paper foundation**:
  - `Yu_2017_SeqGAN` (A3) → pretrain MLE bắt buộc.
  - `Goodfellow_2014_GAN` (A1) → adversarial loop.
  - `Guo_2018_LeakGAN` (A3) → interleaved MLE+GAN.
  - `Fedus_2018_MaskGAN` (A3) → Actor-Critic baseline reduction variance.
- **Reference Guideline**: §3.4.

### B9. Evaluation — composite metric, Self-BLEU-3, type accuracy, τ-diversity curve
- **Composite**: `0.30·owasp + 0.25·db_exec + 0.20·(ast_h/5) + 0.15·ids_evasion + 0.10·relex_uniq`.
- **Target Gumbel-SeqGAN**: composite >0.55 (V3 baseline = 0.471), Self-BLEU-3 <0.70 (V3 = 0.99), unique/64 >40 (V3 = 6-7).
- **Paper foundation**:
  - `de Rosa 2022` survey (A3) → Self-BLEU metric chuẩn.
  - `Yu_2017_SeqGAN` (A3) → NLL oracle methodology.
  - `Lin_2018_IDSGAN` (A6) → evasion rate.
  - `Zhao_2024` (A6) → Cosine + Cumulative Sum cho synthetic verification.
- **Reference Guideline**: §7.1.

### B10. Baselines so sánh
| Baseline | Mục đích | Paper foundation | Status |
|----------|---------|------------------|--------|
| MLE-only (V3 step2000) | Đã có, composite=0.471 | Yu 2017 (warmup phase) | Có checkpoint |
| CTGAN | Tabular baseline (yêu cầu thầy Lâm) | Xu 2019 (A5) | Implement |
| WGAN-GP text (standard, no Gumbel) | Ablation: WGAN-GP không có Gumbel | Gulrajani 2017 (A1) | Implement |
| IDSGAN-style | Domain-neighbor (network flow) | Lin 2018 (A6) | Reference only |
| GAN-SQLi (Lu 2022 DCGAN+GA) | SQLi-specific competitor | Lu 2022 (A7) | Re-implement nếu có code |
| GSQLi (FH0103) | Cùng UIT, cùng SQLi domain | Le et al. 2024 (A7) | Quan trọng để compare |
| VAE+CWGAN-GP+U-Net SQLi | 2025 SOTA SQLi | Dasari 2025 (A7) | Reference + compare metric |
| **Gumbel-SeqGAN (model của ta)** | **Main result** | **Build mới** | **In progress** |

---

## PHẦN C — KHOẢNG TRỐNG & ĐÓNG GÓP CỦA THESIS

So sánh ngắn với 5 paper "near-neighbor" — paper nào gần ta nhất, ta khác họ chỗ nào.

### C1. vs Yu 2017 SeqGAN (framework gốc)
- **Giống**: G LSTM + D CNN + Reward + 3-phase pretrain MLE.
- **Khác**: Thay REINFORCE → Gumbel-Softmax STE (fix mode collapse). Discriminator WGAN-GP thay vì sigmoid BCE. Conditional InfoGAN. Domain SQLi (Yu chỉ thơ/diễn văn/nhạc).
- **Đóng góp**: Áp dụng SeqGAN cho cybersecurity domain với gradient estimator hiện đại — kết quả mode collapse fix được trong khi giữ framework để hợp thesis.

### C2. vs Lin 2018 IDSGAN (GAN cho IDS evasion)
- **Giống**: Adversarial attack generation cho security.
- **Khác**: Domain (SQLi vs NSL-KDD network flow), representation (token sequence vs numerical features 122-d), generator (LSTM seq2seq vs MLP).
- **Đóng góp**: Mở rộng GAN-evasion từ network layer sang application layer (web request/SQL); thêm WAF oracle (Lin 2018 chỉ test IDS).

### C3. vs WAF-A-MoLE 2020 (mutational fuzzer)
- **Giống**: Bypass WAF, target SQLi.
- **Khác**: WAF-A-MoLE là fuzzer (mutation thuần, không learn distribution), không sinh payload mới từ scratch. Ta là generative model học distribution → có khả năng sinh structural variation, dùng WAF-A-MoLE làm post-augmentation.
- **Đóng góp**: Hybrid generative + mutational — kết hợp khả năng generalize của GAN với hiệu quả bypass đã proven của mutation operators.

### C4. vs Lu 2022 GAN-SQLi (DCGAN + GA)
- **Giống**: GAN sinh SQLi payload, target WAF, dùng W-distance.
- **Khác**: Lu 2022 dùng GA pre-filter để đảm bảo cú pháp + DCGAN convolutional. Ta dùng delex_v2 + function whitelist + SeqGAN sequential. Ta có conditional, có reward đa thành phần, có DB sandbox verification.
- **Đóng góp**: End-to-end (không GA), conditional control attack_type/db_engine, reward function tích hợp DB execution check.

### C5. vs Dasari 2025 (VAE+CWGAN-GP+U-Net SQLi)
- **Giống**: SQLi domain, GAN-based, WAF-GP loss.
- **Khác**: Họ sinh trong latent space VAE rồi pseudo-label bằng KMeans; ta sinh tokens trực tiếp với conditional. Họ dùng U-Net (image-like); ta dùng SeqGAN sequential.
- **Đóng góp**: Direct token generation tránh được pseudo-labeling error; conditional control cho attack_type giúp generate payload theo nhu cầu (ví dụ chỉ time-blind cho MySQL).

### C6. vs Le et al. 2024 GSQLi (UIT, cùng trường)
- **Giống**: GAN cho SQLi bypass WAF, có Mutation, có ModSecurity test.
- **Khác**: GSQLi sinh **Mutation Actions** (action space rời rạc, không sinh text); ta sinh tokens trực tiếp. Họ MLP-based; ta SeqGAN sequential với Gumbel-Softmax. Họ Discriminator học từ external Classifier; ta adversarial + reward đa thành phần. Họ không có conditional; ta có InfoGAN.
- **Đóng góp so với baseline cùng trường**: End-to-end sinh payload thay vì chỉ mutation; conditional generation; reward DB execution.

---

## PHẦN D — TRA CỨU NHANH

### D1. Đường dẫn nhanh
- **Index CSV** (filter/sort): `Asset/RELATED_WORK_INDEX.csv`
- **OCR gốc** (đọc chi tiết): `Asset/Total_OCR/<filename>.md`
- **Analysis chi tiết**: `Asset/Total_Analyst/<filename>.md_ANALYSIS.md`

### D2. Bảng đối chiếu duplicate đã merge
Khi cả 2 file tồn tại, **giữ bản có suffix _Method** làm primary, đánh dấu bản còn lại `duplicate_of:` trong CSV.

| Primary (giữ) | Duplicate (đánh dấu) |
|---|---|
| `Yu_2017_SeqGAN.md_ANALYSIS.md` | `Yu_2017.md_ANALYSIS.md` |
| `Arjovsky_2017_WGAN.md_ANALYSIS.md` | `Arjovsky_2017.md_ANALYSIS.md` |
| `Gulrajani_2017_WGAN_GP.md_ANALYSIS.md` | `Gulrajani_2017.md_ANALYSIS.md` |
| `Jang_2017_Gumbel_Softmax.md_ANALYSIS.md` | `Jang_2017.md_ANALYSIS.md` |
| `Chen_2016_InfoGAN.md_ANALYSIS.md` | `Chen_2016.md_ANALYSIS.md` |
| `Lin_2018_IDSGAN.md_ANALYSIS.md` | `Lin_2018.md_ANALYSIS.md` |
| `Fedus_2018_MaskGAN.md_ANALYSIS.md` | `Fedus_2018.md_ANALYSIS.md` |
| `Guo_2018_LeakGAN.md_ANALYSIS.md` | `Guo_2018.md_ANALYSIS.md` |
| `Miyato_2018_Spectral_Norm.md_ANALYSIS.md` | `Miyato_2018.md_ANALYSIS.md` |
| `Bengio_2013_STE.md_ANALYSIS.md` | `Bengio_2013.md_ANALYSIS.md` |
| `Maddison_2017_Concrete_Dist.md_ANALYSIS.md` | `Maddison_2017.md_ANALYSIS.md` |
| `Schulman_2017_PPO.md_ANALYSIS.md` | `Schulman_2017.md_ANALYSIS.md` |
| `Sennrich_2016_BPE.md_ANALYSIS.md` | `Sennrich_2016.md_ANALYSIS.md` |
| `Xu_2019_CTGAN.md_ANALYSIS.md` | `Xu_2019.md_ANALYSIS.md` |
| `Lee_2022_Deduplicating.md_ANALYSIS.md` | `Lee_2022.md_ANALYSIS.md` |
| `Feng_2020_CodeBERT.md_ANALYSIS.md` | `Feng_2020.md_ANALYSIS.md` |
| `Goodfellow_2014_GAN.md_ANALYSIS.md` | `Goodfellow_2014.md_ANALYSIS.md` |
| `Strelcenia_2023_GAN_Survey_Credit.md_ANALYSIS.md` | `make-05-00019 (1).md_ANALYSIS.md` |
| `Ahsan_2022_Comparative_CGAN.md_ANALYSIS.md` | `A comparative analysis of CGAN‐based oversampling for anomaly detection 1.md_ANALYSIS.md` |

### D3. Top-10 paper bắt buộc đọc trước khi vào training
1. **Yu 2017 SeqGAN** — framework
2. **Jang 2017 Gumbel-Softmax** — đổi mới chính
3. **Bengio 2013 STE** — STE backward
4. **Gulrajani 2017 WGAN-GP** — Discriminator
5. **Chen 2016 InfoGAN** — Conditional Q-network
6. **WAF-A-MoLE 2020** — Mutation augmentation
7. **Xu 2019 CTGAN** — Baseline
8. **Le et al. 2024 GSQLi** — Baseline local
9. **Lu 2022 GAN-SQLi** — Baseline domain
10. **Goodfellow 2014 GAN** — Foundation

---

## Lưu ý cuối

- **Bản tổng hợp này dựa hoàn toàn vào nội dung file ANALYSIS sẵn có**. Không bịa số liệu, không thêm trích dẫn ngoài.
- **Các file OCR lỗi** (Nie_2019, Zhang_2020, Hwang_2019, CGAN) đã được OCR lại thành công — cập nhật trong INDEX.csv.
- **Khi viết luận văn**, nên đọc lại OCR đầy đủ ở `Asset/Total_OCR/` cho 10 paper trong D3 để lấy trích dẫn chính xác.
- **CSV `RELATED_WORK_INDEX.csv`** cho phép filter `relevance=CORE` để ra danh sách paper trụ cột, hoặc filter theo `supports_components` để thấy paper nào cho component nào.
