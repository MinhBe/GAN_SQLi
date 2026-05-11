# Phân tích: A Survey on Text Generation using Generative Adversarial Networks

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | A Survey on Text Generation using Generative Adversarial Networks |
| **Tác giả** | Gustavo H. de Rosa, João P. Papa |
| **Năm** | 2022 (arXiv: 20 Dec 2022) |
| **Conference / Journal** | arXiv:2212.11119 (cs.CL) — Submitted to Pattern Recognition |
| **Link** | https://arxiv.org/abs/2212.11119 |

### A1. Phân Loại GAN Taxonomy

| Thuộc tính | Lựa chọn |
|------------|----------|
| **GAN Type** | Survey — covers Vanilla / WGAN / Conditional / VAE-GAN / Multiple architectures |
| **Architecture Family** | RNN-based / CNN-based / Transformer-based / Hybrid |
| **Divergence** | JS / Wasserstein / f-divergence / Hinge / Least-squares / KL / Reverse KL |
| **Task Type** | Text Generation (Survey) |

### A2. Code Availability

| Mục | Thông tin |
|-----|-----------|
| **Official code** | Không (survey paper) |
| **URL** | N/A |
| **Framework** | N/A (survey — references PyTorch/TF for cited works) |
| **Dependencies** | N/A |

---

## Phần B: Dữ Liệu — Data Pipeline Deep-Dive

### B1. Dataset Overview

| Thuộc tính | Mô tả |
|------------|-------|
| **Tên dataset** | Amazon Customer Reviews, Chinese Poems, COCO Image Captions, EMNLP2017 WMT News |
| **Nguồn** | Amazon, multiple online poem sources, MS COCO, WMT 2017 |
| **Kích thước train** | Amazon: 233M reviews; Chinese Poems: 284,299 poems; COCO: 1,026,459 captions; WMT: pairs of documents |
| **Kích thước validation** | N/A (không được báo cáo riêng) |
| **Kích thước test** | N/A |
| **Domain** | E-commerce reviews, poetry, image captions, machine translation |
| **Public / Private** | Public |

### B2. Data Characteristics

| Đặc điểm | Mô tả |
|----------|-------|
| **Data type** | Text |
| **Input dimensions** | Variable-length sequences |
| **Sequence length** | Không được báo cáo thống nhất |
| **Vocabulary size** | Không được báo cáo (phụ thuộc dataset) |
| **Class distribution** | N/A (ngôn ngữ tự nhiên, không phân lớp) |
| **Imbalance ratio** | N/A |

### B3. Preprocessing Pipeline

| Bước | Chi tiết | Công cụ / Library |
|------|----------|-------------------|
| **Tokenization** | [x] Word-level — Stanford PTB Tokenizer cho COCO; không báo cáo cụ thể cho dataset khác | Stanford PTB Tokenizer |
| **Normalization** | [ ] Không được mô tả |
| **Encoding** | [x] Embedding — word embeddings |
| **Augmentation** | [ ] Không |
| **Filtering** | [ ] Remove punctuation cho COCO Captions |
| **Handling imbalance** | [ ] Không |
| **Other** | Standard NLP preprocessing |

### B4. Feature Engineering — N/A (text generation, không feature engineering thủ công)

### B5. Data Loading — N/A (không được báo cáo chi tiết trong survey)

### B6. Data Leakage Check

| Checklist | Status |
|-----------|--------|
| Train/Val/Test random split | Không được báo cáo cho từng paper riêng |
| No data leakage between splits | Không được xác nhận |
| No temporal leakage | Không rõ |
| No duplicate across splits | Không rõ |

---

## Phần C: Kiến Trúc Mô Hình — Architecture Blueprint

### C1. Tổng Quan Kiến Trúc (Survey — tổng hợp từ nhiều paper)

Survey phân loại các kiến trúc GAN cho text generation theo 3 hướng:

```
┌─────────────────────────────────────────────────────────────┐
│                 GAN-based Text Generation                    │
├─────────────────┬───────────────────┬───────────────────────┤
│ Gumbel-Softmax  │ Reinforcement     │ Modified Training     │
│ Differentiation │ Learning (RL)     │ Objectives            │
├─────────────────┼───────────────────┼───────────────────────┤
│ GSGAN, RelGAN,  │ SeqGAN, RankGAN,  │ MaliGAN, TextGAN,     │
│ Meta-CoTGAN     │ LeakGAN, MaskGAN, │ LaTextGAN, STGAN,     │
│                 │ VGAN, ORGAN,      │ TextKD-GAN, FM-GAN,   │
│                 │ CS-GAN, DP-GAN,   │ JSD-GAN, DGSAN,       │
│                 │ BFGAN, SAL,       │ WGAN-GP, AltGAN       │
│                 │ TranGAN, QuGAN    │                       │
└─────────────────┴───────────────────┴───────────────────────┘
```

### C2. Generator Architecture (đại diện — SeqGAN làm baseline chính)

#### C2.1. Layer Stack (SeqGAN — LSTM-based)

| Layer # | Component Type | Input Dim | Output Dim | Activation | Notes |
|---------|---------------|-----------|------------|------------|-------|
| 1 | Embedding | vocab_size | embed_dim | — | |
| 2 | LSTM | embed_dim | hidden_dim | tanh | |
| 3 | LSTM (stacked) | hidden_dim | hidden_dim | tanh | optional |
| N | Softmax | hidden_dim | vocab_size | Softmax | discrete output |

#### C2.2. Component Details (SeqGAN)

| Component | Specification | Value |
|-----------|---------------|-------|
| **Total parameters** | Không báo cáo |
| **Hidden dimension** | Không báo cáo cố định |
| **Number of layers** | 1-2 LSTM layers |
| **Activation function** | tanh (LSTM), Softmax (output) |
| **Normalization** | [ ] None |
| **Dropout** | Không báo cáo |
| **Residual connections** | [ ] Không |
| **Skip connections** | Không |

#### C2.3. Special Components (các biến thể)

| Component | Type | Purpose |
|-----------|------|---------|
| **Attention** | [x] Self (RelGAN, C-SeqGAN, TG-SeqGAN) | Long-term dependencies |
| **Relational Memory** | Self-attention memory | Better long-term extraction |
| **VAE** | Latent variables (VGAN) | Model text variability |
| **Transformer** | Encoder-decoder (TranGAN) | Multi-head self-attention |
| **Quasi-RNN** | CNN+RNN hybrid (QuGAN) | Fast parallel processing |
| **Pre-trained LM** | GPT-2, RoBERTa (TextGAIL) | Improved generation quality |

### C3. Discriminator / Critic Architecture (đa dạng theo từng paper)

| Component | Specification | Giá trị chung |
|-----------|---------------|---------------|
| **Architecture type** | [x] CNN / [x] RNN / [x] Transformer / [x] MLP / [x] Hybrid | Tuỳ paper |
| **Output** | [x] Single scalar (majority) / [x] Comparative (RankGAN, SAL) | |

### C4. Layer Functional Analysis — Không áp dụng do là survey tổng hợp nhiều kiến trúc

### C5. Conditioning Method

| Method | Implementation | Paper |
|--------|---------------|-------|
| [x] Label as additional input | Emotion label + text | CTGAN, CS-GAN, SentiGAN |
| [x] Class embedding + concatenate | Category information | CS-GAN |
| [ ] Other | Domain adaptation | CD-GAN (2 discriminators: sentiment + domain) |

---

## Phần D: Training Configuration

### D1. Optimizer & Learning Rate — Không được báo cáo thống nhất (survey)

### D2. Training Loop — Không áp dụng do survey

### D3. Regularization — Tuỳ từng paper

| Technique | Status |
|-----------|--------|
| Weight decay | Một số paper có |
| Gradient clipping | Một số paper có |
| Dropout rate | Một số paper có |
| Label smoothing | [ ] Không phổ biến |
| Spectral normalization | [ ] Có trong WGAN-GP |
| EMA decay | [ ] Không |

### D4. Loss Function Details

| Loss Component | Các biến thể |
|----------------|--------------|
| **Adversarial loss** | Standard min-max / Wasserstein / JS Divergence |
| **Policy gradient** | REINFORCE (SeqGAN, LeakGAN, ORGAN) |
| **Domain-specific** | ORGAN: discriminator + domain objective |
| **KL divergence** | BGAN: f-divergences |
| **Feature matching** | TextGAN: RKHS kernelized discrepancy |
| **Feature-Mover's Distance** | FM-GAN: EMD variation |

### D5. Reproducibility Checklist

| Item | Status |
|------|--------|
| Random seed reported | [ ] Không (survey scope) |
| Hardware specified | [ ] Không |
| Training time reported | [ ] Không |
| Framework version specified | [ ] Không |
| Hyperparameters fully specified | [ ] Không |

**Confidence to reproduce:** ⭐⭐☆☆☆ / 5 — Survey không nhằm mục đích reproduction

---

## Phần E: So Sánh Với Baselines — Beyond Baselines

### E1. Bảng BLEU-2 Benchmark (key contribution của survey)

| Architecture | Amazon Review | Chinese Poems | COCO Captions | WMT News |
|--------------|:------------:|:-------------:|:-------------:|:--------:|
| MLE RNNLM | 0.848 | 0.667 | 0.781 | 0.768 |
| SeqGAN | 0.856 | 0.739 | 0.745 | 0.777 |
| RankGAN | — | 0.812 | 0.743 | 0.727 |
| LeakGAN | — | **0.881** | 0.746 | 0.826 |
| RelGAN | — | — | **0.849** | **0.881** |
| JSD-GAN | — | 0.536 | **0.894** | **0.943** |
| BFGAN | **0.920** | — | — | — |
| VGAN | 0.868 | — | — | — |
| Meta-CoTGAN | — | — | 0.858 | 0.882 |

### E2. Key Modifications — 3 hướng chính

| Component | What Changed | Expected Benefit |
|-----------|-------------|-------------------|
| Gumbel-Softmax | Replace Softmax with continuous approx | Enable backprop through discrete sampling |
| RL/Policy Gradient | REINFORCE + Monte Carlo search | Bypass differentiability problem |
| Modified objectives | Latent feature matching, FMD, closed-form | Remove need for RL or softmax tricks |

### E3. "X-Factor" — Innovation Chính

**Phân loại toàn diện 35+ kiến trúc GAN text generation thành 3 taxonomy (Gumbel-Softmax, RL, modified objectives) kèm BLEU-2 benchmark chuẩn hoá trên 4 datasets, giúp researcher có "bản đồ" lựa chọn kiến trúc phù hợp.**

---

## Phần F: Ablation & Experiments — Surgical Analysis

### F1. Research Questions

| # | Research Question |
|---|-------------------|
| RQ1 | Làm thế nào để GANs hoạt động được với discrete data (text)? |
| RQ2 | Hướng nào (Gumbel-Softmax / RL / modified objectives) cho kết quả tốt nhất? |
| RQ3 | Những kiến trúc nào đạt BLEU cao nhất trên các text generation benchmarks? |

### F2. Ablation Study — Không có (survey compiles results from individual papers)

### F3. Key Insight từ Phân Tích

- **JSD-GAN** đạt BLEU-2 cao nhất trên COCO Captions (0.894) và WMT News (0.943) — RL-free, optimize JS divergence trực tiếp.
- **LeakGAN** đạt BLEU-2 cao nhất trên Chinese Poems (0.881) — discriminator leak features rất quan trọng.
- **BFGAN** đạt 0.920 trên Amazon Review — backward+forward generators hiệu quả cho lexically-constrained text.
- Gumbel-Softmax architectures (RelGAN: 0.849 COCO, 0.881 WMT) cần pre-training tốt.
- RL-based architectures (SeqGAN, RankGAN) có performance trung bình nhưng là foundational work.

### F4. Statistical Rigor

| Metric | Value |
|--------|-------|
| Number of random seeds | Không báo cáo |
| Confidence intervals | Không |
| Significance test used | Không |

---

## Phần G: Training Stability & Mode Collapse

### G1. Stability Techniques (tổng hợp từ các paper)

| Technique | Status | Ghi chú |
|-----------|--------|---------|
| Gradient penalty | [x] Yes — WGAN-GP | λ = 10 (Gulrajani et al.) |
| Spectral normalization | [x] Yes — một số paper | |
| Label smoothing | [x] Yes — một số | |
| TTUR | [ ] Không phổ biến | |
| Standing statistics | [ ] Không |
| Historical averaging | [ ] Không |
| Other | Pre-training với MLE | Hầu hết architectures đều cần |

### G2. Mode Collapse Countermeasures

| Method | Implementation |
|--------|---------------|
| [x] Diversity penalty | DP-GAN: low reward for repeated text |
| [x] Multiple generators | SentiGAN: penalty-based objective |
| [x] Latent noise variation | VGAN: VAE latent variables |
| [x] Minibatch discrimination | STGAN |
| [x] Unrolled GAN | Not common |
| [x] Self-BLEU penalty | FM-GAN, DGSAN |
| [x] Reward sparsity reduction | IRL: inverse RL with denser rewards |
| [x] Cooperative training | Meta-CoTGAN: additional language model |

### G3. Observed Issues

| Issue | Occurred? | Resolution |
|-------|-----------|------------|
| Mode collapse | [x] Yes | DP-GAN, SentiGAN, IRL |
| Training instability | [x] Yes | WGAN-GP, pre-training |
| Gradient vanishing | [x] Yes | Bootstrapped re-scaling (LeakGAN) |
| Gradient explosion | [x] Yes | Gradient clipping |
| Discriminator dominating | [x] Yes | Slow teaching (AltGAN), cooperative training |

---

## Phần H: Kết Quả & Đánh Giá

### H1. Quantitative Results

#### H1.1. BLEU-2 Rankings

| Rank | Architecture | Best Dataset | BLEU-2 | Taxonomy |
|------|-------------|:------------:|:------:|----------|
| 1 | JSD-GAN | WMT News | 0.943 | Modified objective |
| 2 | BFGAN | Amazon Review | 0.920 | RL |
| 3 | JSD-GAN | COCO Captions | 0.894 | Modified objective |
| 4 | Meta-CoTGAN | WMT News | 0.882 | Gumbel-Softmax |
| 5 | RelGAN | WMT News | 0.881 | Gumbel-Softmax |

### H2. Qualitative Analysis

| Aspect | Observation |
|--------|-------------|
| **Generated quality** | Best architectures produce plausible sentences but still distinguishable from human-written |
| **Diversity** | DP-GAN, SAL improve diversity; mode collapse still open issue |
| **Failure cases** | Short sequences okay; long sequences degrade; RL-based lack generalization |
| **Surprising findings** | JSD-GAN (modified objective) outperforms complex RL architectures despite simplicity |

### H3. Limitations (của field, theo survey)

| Limitation | Description |
|------------|-------------|
| 1 | GANs inherently designed for continuous data → discrete text requires extra tricks |
| 2 | Most architectures need MLE pre-training → computational burden |
| 3 | Evaluation metrics (BLEU, NLL) không capture semantic quality well |
| 4 | Long text generation still struggles |

---

## Phần I: Đánh Giá Cá Nhân

### I1. Điểm Mạnh

| # | Strength | Evidence |
|---|----------|----------|
| 1 | Taxonomy rõ ràng, dễ follow | 3 hướng Gumbel-Softmax / RL / Modified objectives |
| 2 | BLEU-2 benchmark trên 4 common datasets | Bảng so sánh trực tiếp giữa các architectures |
| 3 | Critical analysis cho từng architecture | Mục 4 phân tích ưu/nhược điểm cụ thể |

### I2. Điểm Yếu

| # | Weakness | Evidence |
|---|-----------|----------|
| 1 | Chỉ dùng BLEU-2 — thiếu diversity metrics | Self-BLEU, MS-Jaccard chỉ xuất hiện trong table không được phân tích sâu |
| 2 | Coverage limited to 2016-2020 | Không bao gồm các pre-trained LM-based approaches (GPT-2/3 finetuning) |
| 3 | Thiếu hướng dẫn reproduction | Không có implementation details, hyperparameters |

### I3. Actionable Insights — What I Can Use

| Idea | Source | Priority | Effort | How to implement |
|------|--------|----------|--------|-------------------|
| **Gumbel-Softmax for SQLi generation** | GSGAN, RelGAN | High | Medium | Thay output layer của generator thành Gumbel-Softmax để differentiable |
| **LeakGAN-style feature leaking** | LeakGAN | High | Medium | Discriminator leak intermediate features cho generator |
| **RL-based SeqGAN cho SQL mutation** | SeqGAN | High | High | REINFORCE + Monte Carlo search cho SQLi sequence generation |
| **Diversity penalty (DP-GAN)** | DP-GAN | Medium | Low | Penalize generator khi sinh câu SQLi trùng lặp |
| **Feature-Mover's Distance loss** | FM-GAN | Medium | Medium | Dùng Earth-Mover's Distance thay vì JS divergence |

### I4. Research Gaps Identified

| Gap | Description | Potential research direction |
|-----|-------------|------------------------------|
| 1 | Evaluation metrics for SQLi quality | BLEU không phù hợp — cần valid-metric (SQL syntax validity, attack success rate) |
| 2 | No paper applies GAN text generation to SQL injection | Gap rõ ràng — SQLi là discrete sequence generation |
| 3 | Transformer-based GANs only at early stage (TranGAN) | Có thể dùng pre-trained LLM + GAN cho SQLi generation |

### I5. Verdict

| Criteria | Rating | Notes |
|----------|--------|-------|
| **Technical soundness** | ⭐⭐⭐⭐☆ | Taxonomy hợp lý, phân tích chi tiết |
| **Novelty** | ⭐⭐⭐☆☆ | Survey — không có contribution mới về methodology |
| **Reproducibility** | ⭐⭐☆☆☆ | Không cung cấp implementation details |
| **Overall quality** | ⭐⭐⭐⭐☆ | Tài liệu tham khảo tốt cho field text GAN |

**Summary:** Survey quan trọng mapping 35+ GAN text generation architectures vào 3 taxonomy. Cho GAN_SQLi, bài học chính là RL-based (SeqGAN, LeakGAN) phù hợp nhất cho SQLi sequence generation, Gumbel-Softmax là implementation đơn giản nhất, và diversity penalty là critical để tránh synthetic SQLi bị trùng lặp.

---

## References & Related Works (Trích từ survey)

- Yu et al. SeqGAN (2017) — foundational RL-based text GAN
- Nie et al. RelGAN (2019) — relational memory + Gumbel-Softmax
- Che et al. MaliGAN (2017) — normalized maximum likelihood
- Gulrajani et al. WGAN-GP (2017) — gradient penalty
- Guo et al. LeakGAN (2018) — leaked features from discriminator

---

## Appendix: Raw Notes

- Survey covers 35 papers; keyword search "generative adversarial network" + "text generation"
- Most common metric: BLEU-2 (used by 30/35 papers)
- Most common datasets: COCO Image Captions (14 papers), EMNLP2017 WMT News (12 papers)
- RL-based approaches dominate literature (17 papers) > Modified objectives (11) > Gumbel-Softmax (7)
- JSD-GAN đơn giản nhất nhưng đạt kết quả cao nhất — gợi ý rằng complexity không đồng nghĩa với quality
