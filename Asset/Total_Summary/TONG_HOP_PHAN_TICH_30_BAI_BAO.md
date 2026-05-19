# TỔNG HỢP PHÂN TÍCH TOÀN BỘ 30 BÀI BÁO KHOA HỌC

> Thời gian phân tích: 05/2026 (cập nhật 2026-05-18)
> Template: `scientific_paper_analysis_template.md`
> Tổng số file phân tích: **51** (50 bài báo + 1 template)

---

## DANH MỤC BÀI BÁO & XẾP HẠNG

### Nhóm 1: GAN + SQL Injection (LIÊN QUAN TRỰC TIẾP đến GAN_SQLi)

| # | Tên Bài Báo | Năm | Loại | GAN Type | Rating |
|---|---|---|---|---|---|
| 1 | **Lu et al. - A GAN-based Method for Generating SQL Injection Attack Samples** | 2022 | Original | DCGAN + Genetic Algorithm | ⭐⭐⭐⭐ |
| 2 | **Dasari et al. - Enhancing SQL Injection Detection Using Generative Models** | 2025 | Original | CWGAN-GP + U-Net + VAE | ⭐⭐⭐⭐ |
| 3 | **Le Minh Khan et al. - GSQLi: GAN-based Adversarial SQLi Sample Generation** | 2024 | Original | Customized Conditional GAN | ⭐⭐⭐⭐ |
| 4 | **Chowdhary et al. - GAN-Based Autonomous Penetration Testing for Web Apps** | 2023 | Original | Conditional SeqGAN | ⭐⭐⭐½ |
| 5 | **Cao Phan Xuân Quí et al. - DIGFuPAS: Phát sinh dữ liệu tấn công đánh lừa IDS** | 2020 | Original | WGAN | ⭐⭐⭐ |

### Nhóm 2: GAN + IDS / Network Anomaly Detection (LIÊN QUAN CAO)

| # | Tên Bài Báo | Năm | Loại | GAN Type | Rating |
|---|---|---|---|---|---|
| 6 | **Ahsan et al. - CGAN-based Oversampling for Anomaly Detection** | 2022 | Original | CGAN | ⭐⭐⭐⭐ |
| 7 | **Jamoos et al. - TDCGAN: Triple Discriminator CGAN for IDS** | 2023 | Original | TDCGAN (3 discriminators) | ⭐⭐⭐⭐ |
| 8 | **Zhao et al. - Enhancing NIDS Performance using GAN (ST Engineering)** | 2024 | Original | Vanilla/WGAN/CTGAN | ⭐⭐⭐⭐ |
| 9 | **Alauthman et al. - GAN for IDS: Comprehensive Survey** | 2026 | Survey | Multiple | ⭐⭐⭐⭐⭐ |
| 10 | **Nawaz et al. - Generative AI Driven Synthetic Attack Augmentation** | 2025 | Original | CTGAN | ⭐⭐⭐ |
| 11 | **Rahman et al. - GANs for Synthetic Data to Improve IDS** | 2025 | Original | Vanilla GAN | ⭐⭐⭐ |
| 12 | **Kashaf ul Emaan - Transformer-Enhanced GAN for Fraud Detection** | 2025 | Original | GAN + Transformer | ⭐⭐⭐ |
| 13 | **Peppes et al. - BNGAN: Botnet Attack Data Generation** | 2025 | Original | Vanilla GAN (8-layer) | ⭐⭐ |
| 14 | **Project NT204 - CTGAN + RF cho IDS** | 2021 | Project | CTGAN | ⭐⭐ |

### Nhóm 3: Foundational GAN Methods (ÁP DỤNG CHO GAN_SQLi)

| # | Tên Bài Báo | Năm | Loại | GAN Type | Rating |
|---|---|---|---|---|---|
| 15 | **Yu et al. - SeqGAN: Sequence GAN with Policy Gradient** | 2017 | Foundational | SeqGAN | ⭐⭐⭐⭐½ |
| 16 | **Scott - GAN-SMOTE: GAN Approach to Synthetic Oversampling** | 2019 | Original | Vanilla GAN | ⭐⭐⭐ |
| 17 | **Atkinson - SeqGAN + WGAN/PPO for Sequence Generation** | 2024 | Technical Disclosure | SeqGAN/WGAN/PPO | ⭐⭐⭐ |
| 18 | **Rodriguez - SeqGAN-based RL for Sequence Generation** | 2024 | Technical Disclosure | SeqGAN | ⭐⭐ |
| 19 | **Pearson - Enhancing Seq Modeling with GANs and RL** | 2024 | Technical Disclosure | SeqGAN (duplicate) | ⭐⭐ |

### Nhóm 4: Surveys & Reviews (THAM KHẢO)

| # | Tên Bài Báo | Năm | Loại | Rating |
|---|---|---|---|---|
| 20 | **Udu et al. - Emerging SMOTE & GAN Variants Review** | 2025 | Survey | ⭐⭐⭐⭐ |
| 21 | **Agrawal et al. - Generative Models for Synthetic Attack Data** | 2024 | Review+Critique | ⭐⭐⭐⭐ |
| 22 | **Strelcenia & Prakoonwit - GAN Survey for Fraud Detection** | 2023 | Survey | ⭐⭐⭐ |
| 23 | **Hà Thị Minh Phương - GAN xử lý mất cân bằng SFP** | 2023 | Research Report | ⭐⭐⭐ |

### Nhóm 5: Khác (ÍT/ Không Liên Quan)

| # | Tên Bài Báo | Năm | Domain | Rating |
|---|---|---|---|---|
| 24 | **Khoirunnisa - SMOTE vs CTGAN vs Hybrid (Medical)** | 2025 | Medical | ⭐⭐⭐ |
| 25 | **Julianti et al. - CTGAN + DT for Student Graduation** | 2024 | Education | ⭐⭐ |
| 26 | **Smith et al. - Offline Bilingual Word Vectors** | 2017 | NLP (not GAN) | ⭐⭐⭐⭐ |
| 27 | **Trần Quý Nam - Ứng dụng GAN sinh dữ liệu Pokemon** | 2023 | Image Generation | ⭐⭐ |

---

### Nhóm 6: Gradient Estimators cho Discrete Sequences (QUAN TRỌNG CHO V5)

| # | Tên Bài Báo | Năm | Kỹ Thuật | Rating |
|---|---|---|---|---|
| 28 | **Jang et al. - Categorical Reparameterization with Gumbel-Softmax** | 2017 | Gumbel-Softmax STE | ⭐⭐⭐⭐⭐ |
| 29 | **Maddison et al. - The Concrete Distribution** | 2017 | Concrete Distribution (tương đương Gumbel) | ⭐⭐⭐⭐⭐ |
| 30 | **Bengio et al. - Estimating or Propagating Gradients Through Stochastic Neurons** | 2013 | Straight-Through Estimator (STE) | ⭐⭐⭐⭐☆ |
| 31 | **Williams - Simple Statistical Gradient-Following Algorithms (REINFORCE)** | 1992 | REINFORCE baseline | ⭐⭐⭐⭐☆ |
| 32 | **Rennie et al. - Self-Critical Sequence Training** | 2017 | SCST — self-critical baseline | ⭐⭐⭐⭐☆ |

### Nhóm 7: GAN Training Stability (ÁP DỤNG CHO DISCRIMINATOR V5)

| # | Tên Bài Báo | Năm | Kỹ Thuật | Rating |
|---|---|---|---|---|
| 33 | **Gulrajani et al. - Improved Training of WGANs (WGAN-GP)** | 2017 | Gradient Penalty λ=10 | ⭐⭐⭐⭐⭐ |
| 34 | **Arjovsky et al. - Wasserstein GAN** | 2017 | Wasserstein distance (WGAN gốc) | ⭐⭐⭐⭐⭐ |
| 35 | **Miyato et al. - Spectral Normalization for GANs** | 2018 | SpectralNorm cho D layers | ⭐⭐⭐⭐☆ |
| 36 | **Goodfellow et al. - Generative Adversarial Nets** | 2014 | GAN framework gốc | ⭐⭐⭐⭐⭐ |

### Nhóm 8: Text/Sequence GAN Variants (REFERENCE)

| # | Tên Bài Báo | Năm | GAN Type | Rating |
|---|---|---|---|---|
| 37 | **Guo et al. - LeakGAN: Long Text Generation** | 2018 | Hierarchical RL + leaked D features | ⭐⭐⭐⭐☆ |
| 38 | **Nie et al. - RelGAN: Relational Memory for Text GANs** | 2019 | Relational memory + multi-step attention | ⭐⭐⭐⭐☆ |
| 39 | **Fedus et al. - MaskGAN: Text Infilling with GANs** | 2018 | Conditional infilling với MASK tokens | ⭐⭐⭐☆☆ |
| 40 | **Blonde & Kalinichenko - SAM/GAIL** | 2019 | GAIL-based reward (imitation learning) | ⭐⭐⭐☆☆ |

### Nhóm 9: NLP Foundations (TOKENIZATION & EMBEDDINGS)

| # | Tên Bài Báo | Năm | Kỹ Thuật | Rating |
|---|---|---|---|---|
| 41 | **Sennrich et al. - BPE for NMT** | 2016 | Byte-Pair Encoding tokenization | ⭐⭐⭐⭐☆ |
| 42 | **Feng et al. - CodeBERT** | 2020 | Pre-trained model cho code/SQL | ⭐⭐⭐☆☆ |
| 43 | **Hwang et al. - SQLova** | 2019 | BERT + SQL semantic parsing | ⭐⭐⭐☆☆ |

### Nhóm 10: Data & Labeling (DATA PIPELINE)

| # | Tên Bài Báo | Năm | Kỹ Thuật | Rating |
|---|---|---|---|---|
| 44 | **Ratner et al. - Snorkel: Weak Supervision** | 2017 | Labeling functions + generative model | ⭐⭐⭐⭐☆ |
| 45 | **Rennie et al. - SCST** | 2017 | Self-critical training (gradient estimator) | ⭐⭐⭐⭐☆ |
| 46 | **Lee et al. - Deduplicating Training Data** | 2022 | Near-dedup cho NLP datasets | ⭐⭐⭐⭐☆ |
| 47 | **Gilardi et al. - ChatGPT vs Human Labelers** | 2023 | LLM-based labeling quality study | ⭐⭐⭐☆☆ |

### Nhóm 11: InfoGAN & Conditional (CONDITIONAL GENERATION)

| # | Tên Bài Báo | Năm | GAN Type | Rating |
|---|---|---|---|---|
| 48 | **Chen et al. - InfoGAN** | 2016 | Mutual information maximization | ⭐⭐⭐⭐☆ |
| 49 | **Ahsan et al. - Comparative CGAN** | 2022 | CGAN oversampling comparison | ⭐⭐⭐⭐☆ |

### Nhóm 12: Reinforcement Learning Foundations

| # | Tên Bài Báo | Năm | Kỹ Thuật | Rating |
|---|---|---|---|---|
| 50 | **Schulman et al. - PPO** | 2017 | Proximal Policy Optimization | ⭐⭐⭐⭐☆ |

> **Ghi chú**: PPO được Atkinson_2024 test nhưng **thua REINFORCE** trong SeqGAN context. Không khuyến nghị dùng PPO cho V5.

---

## PHÂN TÍCH CHI TIẾT CÁC BÀI BÁO QUAN TRỌNG NHẤT

---

### BÀI BÁO #1: GAN-based Method for Generating SQL Injection Attack Samples (Lu et al., 2022)

| Mục | Nội dung |
|-----|----------|
| **Tên** | A GAN-based Method for Generating SQL Injection Attack Samples |
| **Tác giả** | Dongzhe Lu, Jinlong Fei, Long Liu, Zecun Li |
| **Năm** | 2022 |
| **Conference** | IEEE ITAIC (ISSN: 2693-2865) |
| **Link** | IEEE Xplore |

#### GAN Taxonomy
| Thuộc tính | Giá trị |
|------------|---------|
| **GAN Type** | DCGAN (Improved) + Genetic Algorithm |
| **Architecture Family** | DCGAN (CNN-based) |
| **Divergence** | Wasserstein distance |
| **Task Type** | Data Augmentation (SQLi sample generation) |
| **Code** | Keras 2.2.4, Python 3.6, VS Code |

#### Data Pipeline
| Thuộc tính | Mô tả |
|------------|-------|
| **Dataset** | 2000+ payloads từ CVE, CNVD, exploit-db (2015-present) |
| **Coverage** | Boolean blind, time blind, joint query, error reporting injection |
| **Preprocessing** | Generalization & decoding, remove noise/inline annotations. Payload scaling [-1,1] |
| **Tokenization** | SQLParse for tokenization, Gene list for GA (select, where, drop, create, etc.) |
| **Batch size** | 500 |

#### Architecture
```
Generator (DCGAN): 4 hidden layers → LeakyReLU → Tanh output
Discriminator: 4 hidden layers → LeakyReLU
GA Component: 100 individuals/generation, gene size 5, crossover + mutation 30%
8 Variational Operators: base64, Keywords(case), Space, UTF8, Apostrophe, ASCII, Interface, Comment
```

#### Training Config
| Hyperparameter | Giá trị |
|---------------|---------|
| **Optimizer** | Adam |
| **Learning rate** | 0.0002 |
| **Momentum** | 0.5 |
| **Batch size** | 500 |
| **Epochs** | 300 |
| **Activation** | LeakyReLU (slope=0.2), Tanh (output), Sigmoid |
| **Weight init** | Glorot_uniform |
| **Dropout** | 0.5 |
| **Hardware** | Intel i7-9700, 24GB RAM, Windows 11 |

#### Kết quả
| Thí nghiệm | Kết quả |
|------------|---------|
| 4 hyperparameter configs so sánh | Group (a) converges fastest (loss ~0.693) |
| sqli-lab test (8 injection types) | **6/8 types successful** |
| sqli-lab + SafeDog WAF | Bypass thành công |
| Failed types | Dump into outfile, Second Degree |

#### X-Factor (Innovation)
Kết hợp **DCGAN + Genetic Algorithm + 8 variational operators** (từ sqlmap) để sinh adversarial SQLi payloads. Wasserstein distance thay KL scatter để chống mode collapse.

#### Verdict
| Criteria | Rating |
|----------|--------|
| Technical soundness | ⭐⭐⭐⭐ |
| Novelty | ⭐⭐⭐⭐ |
| Reproducibility | ⭐⭐⭐⭐ |
| Overall | ⭐⭐⭐⭐ |

---

### BÀI BÁO #2: Enhancing SQL Injection Detection Using Generative Models (Dasari et al., 2025)

| Mục | Nội dung |
|-----|----------|
| **Tên** | Enhancing SQL Injection Detection and Prevention Using Generative Models |
| **Tác giả** | Naga Sai Dasari, Atta Badii, Armin Moin, Ahmed Ashlam |
| **Năm** | 2025 |
| **Type** | arXiv preprint |

#### GAN Taxonomy
| Thuộc tính | Giá trị |
|------------|---------|
| **GAN Type** | CWGAN-GP (Conditional WGAN with Gradient Penalty) |
| **Other models** | U-Net (1D convolutional), VAE |
| **Architecture Family** | Hybrid (U-Net + CWGAN-GP + VAE) |
| **Divergence** | Wasserstein distance + Gradient Penalty |
| **Task Type** | Data Augmentation for SQLi Detection |

#### Architecture Pipeline
```
Raw SQL → VAE Encoder → Latent → U-Net Generator → Synthetic SQL
                              → CWGAN-GP Generator → Synthetic SQL
Synthetic (U-Net + CWGAN-GP) → Pseudo-labelling (PCA + KMeans) → XGBoost
```

#### Component Details
| Component | Specification |
|-----------|---------------|
| **VAE** | Encoder → latent (μ, σ²) → reparameterization → Decoder |
| **U-Net** | Conv1D encoder-decoder + skip connections. Base filters=704, depth=3-5, dropout=0.03 |
| **CWGAN-GP** | Dense(ReLU) layers. n_critic=2. Input: noise z + one-hot label y |
| **Discriminator** | Dense(ReLU) layers → Wasserstein score |
| **Tokenizer** | Custom tokenizer. Embedding: FastText (best among FastText, Character-level, BPE, BERT) |
| **Optimizer** | Adam. U-Net: LR=4.61e-5 |

#### Kết quả
| Model | Accuracy | Notes |
|-------|----------|-------|
| XGBoost baseline | 98.17% | |
| **Final (80% U-Net + 70% CWGAN-GP)** | **99.984%** | Best |
| U-Net synthetic quality | MSE=0.0005, R²=0.8159, BLEU=0.9919 | Excellent |
| CWGAN-GP synthetic quality | MSE=0.0108, **R²=-1.7253** | Poor statistical fidelity |

#### Verdict
| Criteria | Rating |
|----------|--------|
| Technical soundness | ⭐⭐⭐⭐ |
| Novelty | ⭐⭐⭐⭐ |
| Reproducibility | ⭐⭐⭐ |
| Overall | ⭐⭐⭐⭐ |

---

### BÀI BÁO #3: GSQLi - GAN-based Adversarial SQLi Sample Generation (Le Minh Khan et al., 2024)

| Mục | Nội dung |
|-----|----------|
| **Tên** | GSQLi: A GAN-based Approach for Adversarial SQL Injection Sample Generation against WAF |
| **Tác giả** | Le Minh Khan, Hien Do Hoang, Khoa Ngo-Khanh, Phan The Duy, Van-Hau Pham |
| **Năm** | 2024 |
| **Affiliation** | University of Information Technology - VNU HCMC |

#### GAN Taxonomy
| Thuộc tính | Giá trị |
|------------|---------|
| **GAN Type** | Customized Conditional GAN |
| **Architecture Family** | Conditional GAN |
| **Divergence** | Cross-entropy (BCE) |
| **Task Type** | Adversarial Attack Generation (WAF Evasion) |
| **Code** | TensorFlow 2.16.1, Python 3.10, Ubuntu 22.04 |

#### Approach (ĐỘC ĐÁO)
GAN sinh **mutation actions** (không sinh payload trực tiếp):
```
SQLi Payload → Token Parser (Libinjection) → Tokens → Mutation Vector (15 features)
Mutation Vector + Noise → Generator → Mutated Vector → Payload Transformer → Functionality Check
```

Mutation Vector features: UNION, WHERE, LIKE, spaces, comments, etc. (15 features)
11 mutation methods

#### Architecture
| Component | Specification |
|-----------|---------------|
| **Generator** | Input(n+v) → Concat → Dense(512)→Norm → Dense(256)→Norm → Dense(128)→Norm → Dense(a) |
| **Discriminator** | Input(v+a) → Concat → Dense(256)→Norm → Dense(128)→Norm → Dense(64)→Norm → Dense(2) |
| **Attack Classifier** | CNN (embedding + CNN layers) |

#### Kết quả
| Scenario | Kết quả |
|----------|---------|
| Scenario 1 | Generated nhiều unique mutated payloads |
| Scenario 2 (SSHS) | TPR giảm từ ~99% → 87.5% (RNN), 88.9% (GRU), 88.3% (BiLSTM) |
| Scenario 3 (ModSecurity WAF) | FNR = 0.19% (HttpParams), **2.3% (SSHS)** |

#### Verdict
| Criteria | Rating |
|----------|--------|
| Technical soundness | ⭐⭐⭐⭐ |
| Novelty | ⭐⭐⭐⭐⭐ (mutation action generation) |
| Reproducibility | ⭐⭐⭐⭐ |
| Overall | ⭐⭐⭐⭐ |

---

### BÀI BÁO #4: SeqGAN (Yu et al., 2017) — Foundational

| Mục | Nội dung |
|-----|----------|
| **Tên** | SeqGAN: Sequence Generative Adversarial Nets with Policy Gradient |
| **Tác giả** | Lantao Yu, Weinan Zhang, Jun Wang, Yong Yu |
| **Năm** | 2017 |
| **Conference** | AAAI-17 |
| **Code** | https://github.com/LantaoYu/SeqGAN |

#### Core Innovation
- **First GAN to generate discrete sequences** (solved non-differentiable token problem)
- **Monte Carlo search** for intermediate state-action reward estimation
- **Policy Gradient (REINFORCE)** for generator update

#### Architecture
```
Generator (LSTM RNN) → Sequence Y₁...Yₜ
    ↓
Monte Carlo Search (N roll-outs) → Intermediate Rewards
    ↓
Discriminator (CNN: kernels 1-T, 100-200 per size, max-over-time pooling, highway) → Reward
    ↓
Policy Gradient → Update Generator
```

#### Results (Synthetic Data)
| Method | NLL_oracle |
|--------|------------|
| Random | 10.310 |
| MLE | 9.038 |
| **SeqGAN** | **8.736** (p<10⁻⁶) |
| Scheduled Sampling | 8.985 |
| PG-BLEU | 8.946 |

#### Impact
- >2000 citations
- Nền tảng cho tất cả sequence generation GANs
- Được dùng trong bài báo #4 (Chowdhary et al. Sensors 2023)

---

### BÀI BÁO #5: DIGFuPAS - WGAN cho IDS Evasion (Cao Phan Xuân Quí et al., 2020)

| Mục | Nội dung |
|-----|----------|
| **Tên** | Phương Pháp Phát Sinh Dữ Liệu Tấn Công Đánh Lừa IDS Học Máy Dựa Trên Mạng Sinh Đối Kháng |
| **Tác giả** | Cao Phan Xuân Quí, Đặng Hoàng Quang, Phan Thế Duy, Đỗ Thị Thu Hiền, Phạm Văn Hậu |
| **Năm** | 2020 |
| **Conference** | REV-ECIT2020 (VN) |
| **ISBN** | 978-604-80-5076-4 |

#### Approach
- **WGAN** với Wasserstein distance
- **Chỉ thay đổi non-functional features**, giữ nguyên functional features → attack validity
- **Black-box IDS**: LR, SVM, NB, DT, RF
- Dataset: CICIDS2017

#### Architecture
```
Generator (6-layer FC): Input(N-M non-functional + noise) → ReLU → Sigmoid → Output(N-M features)
Discriminator: Input(N-M) → ReLU(x2) → Output
```

#### Training
| Parameter | Value |
|-----------|--------|
| Optimizer | RMSprop |
| LR | 0.0005 |
| Batch size | 512 |
| Epochs | 50 |
| D:G training ratio | 5:1 |
| Framework | PyTorch + sklearn |
| Hardware | Intel Xeon E5-2660, 16GB RAM, no GPU |

#### Results
| Attack Type | Best Evasion | Notes |
|-------------|-------------|-------|
| DoS | RF completely fooled | DT không bị đánh lừa |
| DDoS | All algorithms fooled | Best result |
| Bruteforce | Không đánh lừa được LR | Unstable results |
| Infiltration | No usable results | Only 36 samples |

---

## TỔNG HỢP CÁC PHÁT HIỆN QUAN TRỌNG

### 1. Phát hiện Critical: "Not Normal ≠ Attack Data" (Agrawal et al., 2024)
- GAN-generated data thường được báo cáo là "attack data" nhưng thực chất chỉ là **noise**
- Feature correlations bị thiếu trong synthetic data
- **Cần kiểm tra feature correlations trước khi dùng synthetic data cho training**

### 2. So sánh Các Phương Pháp Oversampling

| Method | Khi nào dùng | Hạn chế |
|--------|-------------|---------|
| **SMOTE** | Tabular data, low-dim, nhanh | Thiếu diversity, linear interpolation |
| **CTGAN** | Tabular mixed-type data | Cần nhiều data, computational cost |
| **WGAN/WGAN-GP** | Ổn định nhất, chống mode collapse | Training chậm |
| **GAN+Transformer** | High-dim feature dependencies | Phức tạp, khó train |
| **SeqGAN** | Discrete sequence generation | Cần pre-training + MC search |
| **DCGAN+GA** | SQLi payload generation | Cần nhiều tuning |

### 3. Key Insights cho GAN_SQLi Project

| Insight | Source | Mức độ |
|---------|--------|--------|
| Kết hợp GAN + Genetic Algorithm cho SQLi generation | Lu et al. 2022 | **ÁP DỤNG NGAY** |
| Mutation action generation thay vì sinh payload trực tiếp | GSQLi 2024 | **ÁP DỤNG NGAY** |
| Kiểm tra feature correlations của synthetic data | Agrawal 2024 | **BẮT BUỘC** |
| WGAN ổn định hơn Vanilla GAN cho tabular data | Zhao 2024, DIGFuPAS 2020 | **KHUYẾN NGHỊ** |
| SeqGAN + MC Search cho sequence generation | Yu 2017 | **CÓ THỂ ÁP DỤNG** |
| Multiple discriminators giúp ổn định training | TDCGAN 2023 | **CÓ THỂ THỬ** |
| 4× augmentation cho improvement tốt nhất (diminishing returns) | Zhao 2024 | **THAM KHẢO** |
| GAN-SMOTE với minibatch discrimination cho small datasets | Scott 2019 | **THAM KHẢO** |
| CTGAN outperform các method khác cho tabular data oversampling | Hà 2023, Khoirunnisa 2025 | **XÁC NHẬN** |
| CWGAN-GP có thể cho R² âm (synthetic data kém chất lượng) | Dasari 2025 | **CẢNH BÁO** |

---

## KIẾN TRÚC ĐỀ XUẤT CHO GAN_SQLi

Dựa trên phân tích 30 bài báo, kiến trúc tối ưu cho GAN_SQLi:

```
┌─────────────────────────────────────────────────────────┐
│                   GAN_SQLi PIPELINE                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  1. DATA PREPARATION (Tham khảo: GSQLi 2024)            │
│     - Token parser (SQLParse / Libinjection)             │
│     - Mutation Vector (15-20 SQL features)               │
│     - One-hot encoding + MinMax scaling                  │
│                                                         │
│  2. GENERATION STRATEGY (Lu 2022 + GSQLi 2024)           │
│     ├─ Option A: GAN + Genetic Algorithm                │
│     │   - DCGAN generator + Wasserstein loss             │
│     │   - 8+ variational operators (base64, case, etc.)  │
│     │   - Functionality check (SQL parsing)              │
│     │                                                    │
│     └─ Option B: Mutation Action GAN                     │
│         - Generator → mutation vector                    │
│         - Payload transformer → mutated SQLi             │
│         - Không sinh payload trực tiếp                   │
│                                                         │
│  3. GAN ARCHITECTURE (Zhao 2024 + TDCGAN 2023)           │
│     - WGAN-GP (Wasserstein + gradient penalty)           │
│     - Optional: 2 discriminators cho stability           │
│     - Squeeze-and-Excitation blocks cho feature modeling │
│                                                         │
│  4. TRAINING (Multiple sources)                          │
│     - Optimizer: Adam (lr=0.0002) hoặc RMSprop (lr=0.0005)│
│     - Batch size: 128-512                                │
│     - D:G ratio: 5:1 hoặc 2:1                            │
│     - 300-1000 epochs                                    │
│     - Early stopping on loss convergence                  │
│                                                         │
│  5. VALIDATION (Agrawal 2024 - QUAN TRỌNG)               │
│     - Feature correlation check (Pearson)                │
│     - Cosine similarity với real data                    │
│     - Cumulative sums visualization                      │
│     - ML validation (Random Forest/XGBoost)              │
│     - SQL parsing functionality check                    │
│                                                         │
│  6. EVALUATION                                           │
│     - Test trên WAF (ModSecurity, SQLite)                │
│     - Detection rate bypass                              │
│     - Diversity metrics                                  │
│     - Compare: SMOTE, CTGAN, WGAN baselines              │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## BẢNG SO SÁNH CHI TIẾT

### So sánh 5 bài báo SQLi-specific

| Tiêu chí | Lu 2022 | Dasari 2025 | GSQLi 2024 | Chowdhary 2023 | DIGFuPAS 2020 |
|----------|---------|-------------|------------|-----------------|---------------|
| **GAN Type** | DCGAN+GA | CWGAN-GP+U-Net | Conditional GAN | Conditional SeqGAN | WGAN |
| **Task** | SQLi Generation | SQLi Detection+Gen | WAF Evasion | Pentesting (XSS) | IDS Evasion |
| **Dataset** | CVE/CNVD/exploit-db | Kaggle SQL Datasets | HttpParams/SSHS | XSS PayloadBox | CICIDS2017 |
| **Evaluation** | sqli-lab + SafeDog | XGBoost Accuracy | ModSecurity WAF | AWS WAF, ModSecurity | LR/SVM/NB/DT/RF |
| **Unique feature** | Genetic Algorithm + 8 tamper ops | VAE+pseudo-labelling | Mutation actions | Semantic tokenization | Functional feature preservation |
| **Reproducibility** | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐⭐ |
| **Rating** | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐½ | ⭐⭐⭐ |

### So sánh các Survey

| Tiêu chí | Alauthman 2026 | Udu 2025 | Agrawal 2024 | Strelcenia 2023 |
|----------|---------------|----------|--------------|-----------------|
| **Domain** | GAN+IDS (tổng quát) | SMOTE+GAN (tổng quát) | Synthetic Attack Data | Credit Card Fraud |
| **Số papers** | 147 refs | 61 papers | Nhiều | ~40 papers |
| **Năm** | 2026 | 2025 | 2024 | 2023 |
| **Điểm mạnh** | IoT, Federated, Quantum GAN | Unified taxonomy, 85+ SMOTE variants | **Critical analysis, noise detection** | GAN variants comparison |
| **Điểm yếu** | Thiếu meta-analysis | Thiếu empirical benchmarking | Only DoS tested | Thiếu depth |
| **Rating** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |

---

## KẾT LUẬN & KHUYẾN NGHỊ

### 3 Papers QUAN TRỌNG NHẤT cho GAN_SQLi
1. **Lu et al. 2022** (DCGAN + GA cho SQLi generation) — Kiến trúc nền tảng
2. **GSQLi 2024** (Mutation action generation) — Cách tiếp cận độc đáo
3. **Agrawal 2024** (Critical analysis: "not normal ≠ attack") — Validation methodology

### 5 Khuyến nghị cho GAN_SQLi Implementation
1. **Dùng WGAN-GP** thay vì Vanilla GAN cho training stability
2. **Kết hợp Genetic Algorithm** (Lu 2022) + **Mutation actions** (GSQLi 2024)
3. **Validate synthetic data quality** bằng feature correlation analysis (Agrawal 2024)
4. **Functionality check** sau mỗi generation cycle (parse SQL output)
5. **Test trên nhiều WAF** (ModSecurity, AWS WAF, Cloudflare)

### Cảnh báo
- **"Not normal ≠ attack data"** — synthetic data cần được kiểm tra feature correlations
- **CWGAN-GP có thể cho R² âm** — U-Net outperforms GAN cho SQL data generation (Dasari 2025)
- **Diminishing returns** sau 4× augmentation (Zhao 2024)

---

## REFERENCES ĐẦY ĐỦ

| # | Citation |
|---|----------|
| 1 | Kashaf ul Emaan. "Improving Credit Card Fraud Detection through Transformer-Enhanced GAN Oversampling." arXiv:2509.19032v2, 2025. |
| 2 | Ahsan, R., Shi, W., Ma, X., Croft, W.L. "A comparative analysis of CGAN-based oversampling for anomaly detection." IET Cyber-Physical Systems, 2022. |
| 3 | Peppes, N., Alexakis, T., Daskalakis, E., Adamopoulou, E., Demestichas, K. "BNGAN." In: Paradigms on Technology Development for Security Practitioners, Springer, 2025. |
| 4 | Jamoos, M., Mora, A.M., AlKhanafseh, M., Surakhi, O. "TDCGAN for NIDS." Electronics, 2023. |
| 5 | Scott, M. "GAN-SMOTE." ABCs 2019, ANU. |
| 6 | Atkinson, D. "Advancements in Sequence Generation Through GAN-Enhanced RL." TD Commons, 2024. |
| 7 | Rodriguez, J. "Advancements in Sequence Generation: A GAN-Based RL Approach." TD Commons, 2024. |
| 8 | Strelcenia, E., Prakoonwit, S. "GAN Survey for Credit Card Fraud." MDPI MAKE, 2023. |
| 9 | Hà Thị Minh Phương. "GAN xử lý mất cân bằng SFP." ĐHVH-2023-03, 2023. |
| 10 | Khoirunnisa, N., Rosyda, M. "SMOTE vs CTGAN vs Hybrid for Medical Data." Sci. Inf. Technol. Lett., 2025. |
| 11 | Agrawal, G., Kaur, A., Myneni, S. "A Review of Generative Models in Generating Synthetic Attack Data for Cybersecurity." Electronics, 2024. |
| 12 | Udu, A.G., et al. "Emerging SMOTE and GAN Variants Review." IEEE Access, 2025. |
| 13 | Zhao, X., Fok, K.W., Thing, V.L.L. "Enhancing NIDS Performance using GAN." ST Engineering, 2024. |
| 14 | Pearson, H. "Enhancing Sequence Modeling with GANs and RL." TD Commons, 2024. |
| 15 | Dasari, N.S., Badii, A., Moin, A., Ashlam, A. "Enhancing SQLi Detection Using Generative Models." arXiv, 2025. |
| 16 | Le Minh Khan, et al. "GSQLi." UIT-VNU HCMC, 2024. |
| 17 | Alauthman, M., et al. "GAN for IDS: Comprehensive Survey." Arabian JSE, 2026. |
| 18 | Nawaz, M., Tahira, S., Yasmin, A. "Generative AI Driven Synthetic Attack Augmentation." Preprints, 2025. |
| 19 | Julianti, M.R., et al. "CTGAN + DT for Student Graduation." J. Electrical Systems, 2024. |
| 20 | Lu, D., Fei, J., Liu, L., Li, Z. "GAN-based Method for Generating SQLi Attack Samples." IEEE ITAIC, 2022. |
| 21 | Trương Thị Hoàng Hảo, et al. "CTGAN + RF cho IDS." Project NT204, 2021. |
| 22 | Smith, S.L., et al. "Offline Bilingual Word Vectors." ICLR 2017. |
| 23 | Cao Phan Xuân Quí, et al. "DIGFuPAS." REV-ECIT2020. |
| 24 | Chowdhary, A., Jha, K., Zhao, M. "GAN-Based Autonomous Pentesting." Sensors, 2023. |
| 25 | Yu, L., Zhang, W., Wang, J., Yu, Y. "SeqGAN." AAAI-17. |
| 26 | Rahman, M.A., Francia, G.A., Shahriar, H. "GANs for Synthetic Data to Improve IDS." FAITH, 2025. |
| 27 | Trần Quý Nam. "Ứng dụng GAN sinh dữ liệu đa phương tiện." Tạp chí KH CNTT&TT, 2023. |

---

*Báo cáo được tạo tự động dựa trên phân tích 30 file đầu vào theo template `scientific_paper_analysis_template.md`*
