# Phân Tích: Self-Critical Sequence Training for Image Captioning

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | Self-critical Sequence Training for Image Captioning |
| **Tác giả** | Steven J. Rennie, Etienne Marcheret, Youssef Mroueh, Jerret Ross, Vaibhava Goel |
| **Tổ chức** | IBM Watson |
| **Năm** | 2017 |
| **Conference / Journal** | CVPR 2017 |
| **Link** | https://arxiv.org/abs/1612.00563 |

### A1. Phân Loại GAN Taxonomy

| Thuộc tính | Lựa chọn |
|------------|----------|
| **GAN Type** | N/A — Sequence-level RL (không phải GAN) |
| **Architecture Family** | LSTM + Attention (Generator); không có Discriminator |
| **Divergence** | REINFORCE với self-critical baseline |
| **Task Type** | Image Captioning (Sequence Generation) |

### A2. Code Availability

| Mục | Thông tin |
|-----|-----------|
| **Official code** | Có |
| **URL** | https://github.com/ruotianluo/self-critical.pytorch |
| **Framework** | PyTorch |
| **Dependencies** | torchvision, COCO evaluation |

---

## Phần B: Dữ Liệu — Data Pipeline Deep-Dive

### B1. Dataset Overview

| Thuộc tính | Mô tả |
|------------|-------|
| **Tên dataset** | MSCOCO Captions |
| **Nguồn** | Microsoft COCO dataset |
| **Kích thước train** | ~83K images, 5 captions/image |
| **Kích thước test** | ~5K images (official eval) |
| **Domain** | Image captioning (cross-modal) |
| **Public** | ✓ Public |

### B2. Data Characteristics

| Đặc điểm | Mô tả |
|----------|-------|
| **Data type** | Text sequences (captions) |
| **Vocab size** | ~10,000 words |
| **Avg sequence length** | ~10-12 tokens |
| **Task** | Generate natural language description cho ảnh |

### B3. Preprocessing Pipeline

| Bước | Chi tiết |
|------|----------|
| **Tokenization** | Word-level, lowercase |
| **Filtering** | Loại bỏ rare words (<5 occurrences) |
| **Feature extraction** | CNN (ResNet/VGG) visual features |

### B6. Data Leakage Check

| Mục | Trạng thái |
|-----|-----------|
| Random split tránh overlap | [x] Dùng official COCO splits |
| No temporal leakage | [x] N/A (static image dataset) |
| No duplicate test | [x] Official eval server |
| Feature vs label leakage | [x] Visual features extracted trước |

---

## Phần C: Kiến Trúc Mô Hình — Architecture Blueprint

### C1. Tổng Quan Kiến Trúc

```
Image → CNN Feature Extractor → Visual Features
                                       ↓
                              LSTM Language Model
                              (Attention mechanism)
                                       ↓
                         SCST Training Loop:
                         ┌─────────────────────────────┐
                         │  beam search output (test)  │ ← baseline b(s)
                         │  sampled output (train)      │ ← get CIDEr reward r(s)
                         │  reward = r(s) - b(s)        │ ← self-critical signal
                         │  gradient = (r-b) × ∇log_π  │ ← REINFORCE update
                         └─────────────────────────────┘
```

### C2. Generator Architecture

| Layer | Component | Output | Activation | Notes |
|-------|-----------|--------|------------|-------|
| Input | CNN features + prev token | [B, feature_dim] | — | ResNet/VGGNet |
| 1 | LSTM cell | [B, 512] | tanh | Language model |
| 2 | Attention layer | [B, feature_dim] | softmax | Soft attention |
| Output | Linear + Softmax | [B, vocab_size] | softmax | Word distribution |

| Parameter | Value |
|-----------|-------|
| **Hidden dim** | 512 |
| **Vocab size** | ~10,000 |
| **Attention** | Soft attention |
| **Dropout** | 0.5 |

### C3. Discriminator

Không có Discriminator — SCST dùng model chính làm "oracle" để tính baseline.

---

## Phần D: Training Configuration

### D1. Optimizer

| | Generator |
|---|---|
| **Optimizer** | Adam |
| **LR** | 5e-4 → 5e-5 (decay) |

### D2. Training Loop

| Thuộc tính | Giá trị |
|------------|---------|
| **Pretrain** | Cross-entropy (MLE) trước, sau đó fine-tune bằng SCST |
| **Batch size** | 64 images |
| **Metric** | CIDEr (sequence-level, non-differentiable) |
| **Baseline** | b(s) = CIDEr score của beam search output |

### D5. Reproducibility Checklist

| Mục | Trạng thái |
|-----|-----------|
| Random seeds được fix | [ ] Không đề cập |
| Confidence intervals | [ ] Không có |
| Multiple runs | [ ] Không đề cập |
| Hyperparameters đầy đủ | [x] Có |
| **Confidence rating** | ⭐⭐⭐☆☆ |

---

## Phần E: So Sánh Với Baselines — Beyond Baselines

### E1. Base vs Paper's Version

| Aspect | MLE baseline | SCST (paper) |
|--------|--------------|--------------|
| Loss function | Cross-entropy (token-level) | REINFORCE với CIDEr reward |
| Baseline | None (teacher forcing) | Beam search output of same model |
| Gradient | Dense (every token) | Sparse (sequence-level, REINFORCE) |
| Exposure bias | Yes (training ≠ inference) | Reduced (inference-mode sampling) |

### E2. Key Modifications

| What Changed | Expected Benefit | Actual Result |
|---|---|---|
| MLE → SCST | Optimize actual metric (CIDEr) | +10 CIDEr points improvement |
| Greedy baseline → Beam search baseline | Lower variance baseline | Reduced gradient variance |
| Token-level → Sequence-level optimization | Better sequence coherence | Better BLEU, METEOR, CIDEr |

### E3. X-Factor

**Innovation**: Dùng chính model ở inference mode (beam search) làm baseline cho REINFORCE — không cần critic network riêng. Khi model tốt hơn → baseline tốt hơn → adaptive curriculum học tự động. Giải quyết "training-inference mismatch" mà teacher forcing gây ra.

---

## Phần F: Ablation & Experiments

### F1. Research Questions

| RQ | Câu hỏi | Kết quả |
|----|---------|---------|
| RQ1 | SCST có tốt hơn REINFORCE với fixed baseline không? | ✓ SCST > fixed baseline đáng kể |
| RQ2 | Beam search baseline tốt hơn greedy baseline không? | ✓ Beam search cho variance thấp hơn |
| RQ3 | SCST có outperform MLE trên tất cả metrics không? | ✓ CIDEr, BLEU4, METEOR, ROUGE-L |

### F2. Main Results Table

| Model | CIDEr | BLEU-4 | METEOR | ROUGE-L |
|-------|-------|--------|--------|---------|
| MLE (Attention) | 104.9 | 32.5 | 26.0 | 54.3 |
| SCST (single model) | 113.7 | 34.2 | 26.7 | 55.7 |
| SCST (ensemble ×4) | **114.7** | **35.4** | **27.1** | **56.6** |

### F3. Statistical Rigor

| Mục | Trạng thái |
|-----|-----------|
| Random seeds | [ ] 1 run, không đề cập seeds |
| Confidence intervals | [ ] Không có |
| Significance test | [ ] Không có |
| Evaluation | [x] Official COCO eval server |
| **Statistical rigor rating** | ⭐⭐☆☆☆ (single run, no CI) |

---

## Phần G: Training Stability & Mode Collapse

### G1. Stability Techniques

| Kỹ thuật | Mô tả |
|----------|-------|
| **MLE Pretrain** | Khởi động với cross-entropy trước, tránh gradient chaos |
| **Self-critical baseline** | Adaptive baseline giảm variance tốt hơn fixed |
| **Beam search baseline** | Beam search output → lower variance than greedy |

### G2. Mode Collapse Countermeasures

| Vấn đề | Giải pháp |
|--------|----------|
| Reward saturation | Self-critical baseline: khi model tốt → baseline cao → advantage = 0 → **VẪN CÒN VẤN ĐỀ** |
| Sequence repetition | Beam search diversity không được đề cập |

### G3. Observed Issues

| Vấn đề | Bằng chứng |
|--------|-----------|
| Baseline cũng bị reward saturation | Khi model rất tốt, beam search baseline ≈ sampled output → advantage→0 → gradient vanish |
| Domain specific | SCST được optimize cho CIDEr (image captioning), không trivially transfer |

---

## Phần H: Kết Quả & Đánh Giá

### H1.1. Main Results

| Dataset | Metric | Paper's Result | Best Prior | Improvement |
|---------|--------|---------------|------------|-------------|
| MSCOCO | CIDEr | 113.7 (single) | 104.9 (MLE) | **+8.4% (+8.8 points)** |
| MSCOCO | BLEU-4 | 34.2 | 32.5 | +5.2% |
| MSCOCO | METEOR | 26.7 | 26.0 | +2.7% |

### H2. Qualitative Analysis

- Captions SCST sinh ra: tự nhiên hơn, ít lặp từ hơn, cover nhiều chi tiết ảnh hơn
- Failure cases: long complex scenes có nhiều objects → captions vẫn bị truncate

### H3. Limitations

- Chỉ test trên image captioning (MSCOCO) — không test trên other sequence tasks
- Beam search baseline tốn 2× computation so với greedy baseline
- Reward saturation vẫn xảy ra khi model mature (advantage → 0)

---

## Phần I: Đánh Giá Cá Nhân

### I1. Điểm Mạnh

| # | Điểm mạnh | Evidence |
|---|-----------|---------|
| 1 | Self-critical baseline không cần network phụ | Không cần critic, đơn giản hơn Actor-Critic |
| 2 | Adaptive curriculum | Baseline tự tăng khi model tốt hơn |
| 3 | Strong empirical results | +8.4% CIDEr trên MSCOCO |

### I2. Điểm Yếu

| # | Điểm yếu | Evidence |
|---|----------|---------|
| 1 | Vẫn còn reward saturation | Khi model mature → advantage → 0 → gradient vanish |
| 2 | Domain specific | Chỉ proven trên image captioning với CIDEr |
| 3 | 1 seed, không CI | Statistical rigor thấp |
| 4 | Không giải quyết mode collapse hoàn toàn | Chỉ giảm variance, không fix root cause |

### I3. Actionable Insights

| Idea | Source | Priority | Effort | How to Implement |
|------|--------|----------|--------|-----------------|
| SCST baseline cho SQLi | SCST mechanism | Medium | Low | Baseline = reward của G ở test-time (τ=0.1) thay vì MovingAverage |
| So sánh SCST vs Gumbel | SCST + Jang_2017 | High | Medium | Ablation: train V5 với SCST thay Gumbel, compare unique/64 |
| MLE pretrain trước SCST | Paper Section 3 | P0 | Đã có | Phase 1 warmup giống SCST pretrain (giữ V5) |

### I4. Research Gaps

| Gap | Mô tả | Potential Direction |
|-----|-------|---------------------|
| SCST on discrete security tasks | SCST chưa được test cho adversarial payload generation | Apply SCST baseline cho SQLi reward: baseline = G(τ=0, greedy) score |
| SCST vs Gumbel comparison | Không có paper so sánh trực tiếp hai approaches | Ablation study trong V5 nếu thời gian cho phép |
| Reward saturation | Cả SCST và REINFORCE đều bị saturation khi mature | Gumbel-Softmax giải quyết root cause hơn |

### I5. Verdict

| Criteria | Rating | Notes |
|----------|--------|-------|
| **Technical soundness** | ⭐⭐⭐⭐☆ | Clear mechanism, good results |
| **Novelty** | ⭐⭐⭐⭐☆ | Self-critical baseline idea là elegant |
| **Reproducibility** | ⭐⭐⭐☆☆ | 1 seed, no CI |
| **Relevance to SQLi** | ⭐⭐⭐☆☆ | Indirect — gradient estimator alternative |
| **Overall quality** | ⭐⭐⭐⭐☆ | Strong paper, limited domain |

**Summary**: SCST là alternative REINFORCE với baseline thông minh hơn. Không giải quyết root cause mode collapse (reward saturation vẫn xảy ra khi mature). Gumbel-Softmax (Jang_2017) giải quyết root cause tốt hơn cho bài toán SQLi. SCST vẫn đáng cite trong thesis Section 2.3 như "alternative candidate được xem xét".

---

### H10. Thesis Section Mapping

| Thesis Section | Nội dung từ paper này |
|----------------|----------------------|
| 2.3 Gradient Estimators | SCST: alternative candidate — baseline = model test-time output |
| 2.3 Comparison Table | SCST column: unbiased, medium variance, không cần critic |
| 5.2 Future Work | "SCST baseline là alternative cho Gumbel-Softmax trong future experiments" |
| References | Rennie et al. (2017), CVPR |
