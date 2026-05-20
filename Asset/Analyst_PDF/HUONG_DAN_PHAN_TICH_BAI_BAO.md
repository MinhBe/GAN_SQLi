# Hướng Dẫn Phân Tích Bài Báo Khoa Học — Yêu Cầu & Phong Cách Trình Bày

> Tài liệu này mô tả cấu trúc, yêu cầu và phong cách trình bày khi phân tích bài báo khoa học cho dự án GAN_SQLi.

---

## 1. CẤU TRÚC BẮT BUỘC (9 Phần A–I)

Mọi bài phân tích phải tuân theo **9 phần chuẩn**, đánh dấu bằng heading `##`:

| Phần | Tiêu đề | Mục đích |
|------|---------|----------|
| **A** | Thông Tin Cơ Bản & Phân Loại | Metadata, GAN taxonomy, code availability |
| **B** | Dữ Liệu — Data Pipeline Deep-Dive | Dataset, preprocessing, feature engineering, leakage check |
| **C** | Kiến Trúc Mô Hình — Architecture Blueprint | Generator, Discriminator, layer stack, conditioning |
| **D** | Training Configuration | Optimizer, hyperparameters, regularization, reproducibility |
| **E** | So Sánh Với Baselines — Beyond Baselines | What changed, expected vs actual result, X-Factor |
| **F** | Ablation & Experiments — Surgical Analysis | Research questions, variants, results, statistical rigor |
| **G** | Training Stability & Mode Collapse | Stability techniques, countermeasures, observed issues |
| **H** | Kết Quả & Đánh Giá | Quantitative results, qualitative analysis, limitations |
| **I** | Đánh Giá Cá Nhân | Strengths, weaknesses, actionable insights, gaps, verdict |

---

## 2. PHONG CÁCH TRÌNH BÀY

### 2.1. Ưu tiên Tables thay vì Paragraphs

**ĐÚNG:**
```markdown
| Thuộc tính | Giá trị |
|------------|---------|
| **GAN Type** | WGAN-GP |
| **Architecture** | MLP-based |
| **Loss** | Wasserstein distance |
```

**SAI:**
```markdown
Bài báo sử dụng WGAN-GP với kiến trúc MLP-based và hàm mất mát là Wasserstein distance...
```

### 2.2. Rating Hệ Thống — ⭐ 1–5

Mọi bài phân tích phải có **Verdict table** ở Phần I5:

| Criteria | Rating | Notes |
|----------|--------|-------|
| **Technical soundness** | ⭐⭐⭐⭐☆ | Experimental design vững |
| **Novelty** | ⭐⭐⭐☆☆ | Combination, không phải new technique |
| **Reproducibility** | ⭐⭐⭐⭐☆ | Hyperparameters đầy đủ |
| **Overall quality** | ⭐⭐⭐⭐☆ | Practical value cao |

### 2.3. Evidence-Based — Mọi Nhận Xét Phải Có Dẫn Chứng

**ĐÚNG:**
```markdown
| # | Weakness | Evidence |
|---|----------|----------|
| 1 | Không statistical rigor | Chỉ 1 seed, không confidence intervals |
```

**SAI:**
```markdown
Bài báo thiếu statistical rigor.
```

### 2.4. Actionable Insights — Bảng "What I Can Use"

Phần I3 **bắt buộc** có table với các cột:

| Idea | Source | Priority | Effort | How to implement |
|------|--------|----------|--------|-------------------|
| SMOTE + GAN hybrid | SMOTE logic + GAN | High | Medium | Dùng GAN generate + SMOTE interpolate |

### 2.5. Architecture Diagram — ASCII Art

Phần C1 phải có sơ đồ kiến trúc dạng text:

```
Raw Data → Preprocessing → Hybrid Sampling
    ↓
┌─────────────────────────────────────┐
│         Ensemble Classification      │
├──────────┬──────────┬───────────────┤
│ CatBoost │ LightGBM │   XGBoost     │
└──────────┴──────────┴───────────────┘
    ↓
Final Prediction
```

### 2.6. Checklist Format

Dùng `[x]` và `[ ]` cho các mục đã/ chưa được áp dụng:

```markdown
| **Tokenization** | [x] Word-level [ ] BPE [ ] Character-level |
| **Normalization** | [x] Min-max [ ] Standard [ ] Robust |
```

### 2.7. Ngôn Ngữ

- **Tiếng Việt** cho tiêu đề, nhận xét, phân tích
- **Tiếng Anh** cho thuật ngữ kỹ thuật (GAN, WGAN-GP, discriminator, v.v.)
- **Giữ nguyên** tên dataset, metric, library từ paper gốc

---

## 3. YÊU CẦU NỘI DUNG CHI TIẾT THEO PHẦN

### Phần A — Thông Tin Cơ Bản

**Bắt buộc có:**
- Tên bài báo, tác giả, năm, conference/journal, link
- GAN Taxonomy table: GAN Type, Architecture Family, Divergence, Task Type
- Code Availability: official code (có/không), URL, framework, dependencies

### Phần B — Data Pipeline

**Bắt buộc có:**
- B1: Dataset Overview — tên, nguồn, kích thước (train/val/test), domain, public/private
- B2: Data Characteristics — data type, dimensions, class distribution, imbalance ratio
- B3: Preprocessing Pipeline — từng bước với công cụ/library
- B6: Data Leakage Check — 4 mục (random split, no leakage, no temporal, no duplicate)

### Phần C — Kiến Trúc

**Bắt buộc có:**
- C1: ASCII architecture diagram
- C2: Generator Layer Stack table (Layer#, Component, Input/Output Dim, Activation, Notes)
- C2.2: Component Details (total params, hidden dim, layers, activation, normalization, dropout)
- C3: Discriminator Architecture — tương tự Generator

### Phần D — Training Config

**Bắt buộc có:**
- D1: Optimizer & LR cho Generator và Discriminator (separate columns)
- D2: Batch size, g_steps:d_steps ratio, epochs, iterations
- D5: Reproducibility Checklist — 5 mục + Confidence rating ⭐/5

### Phần E — Beyond Baselines

**Bắt buộc có:**
- E1: Base vs Paper's version comparison
- E2: Key Modifications table — What Changed / Expected Benefit / Actual Result
- E3: **"X-Factor"** — 1-3 câu mô tả innovation quan trọng nhất

### Phần F — Ablation

**Bắt buộc có:**
- F1: Research Questions (RQ1, RQ2, RQ3...)
- F2.1: Ablation Variants table
- F2.2: Ablation Results table
- F2.3: **Key Ablation Insight** — 1 câu kết luận chính
- F3: Statistical Rigor — random seeds, confidence intervals, significance test, p-value

### Phần G — Stability

**Bắt buộc có:**
- G1: Stability Techniques table (gradient penalty, spectral norm, label smoothing, TTUR...)
- G2: Mode Collapse Countermeasures
- G3: Observed Issues table (mode collapse, instability, gradient vanishing/explosion)

### Phần H — Kết Quả

**Bắt buộc có:**
- H1.1: Main Results Table — Dataset, Metric, Paper's Result, Best Baseline, Improvement
- H2: Qualitative Analysis — quality, diversity, failure cases, surprising findings
- H3: Limitations — paper tự thừa nhận gì

### Phần I — Đánh Giá Cá Nhân

**Bắt buộc có:**
- I1: Điểm Mạnh — 3+ items với evidence
- I2: Điểm Yếu — 3+ items với evidence
- I3: Actionable Insights table — Idea / Source / Priority / Effort / How to implement
- I4: Research Gaps table — Gap / Description / Potential direction
- I5: Verdict table + Summary (1-2 câu)

---

## 4. QUY TẮC CHUNG

### 4.1. Không Copy-Paste Abstract

Tóm tắt bằng ngôn ngữ của mình, tập trung vào **methodology + results + limitations**.

### 4.2. Trích Dẫn Số Liệu Cụ Thể

**ĐÚNG:**
```
F1 = 0.98, Recall = 0.99, Accuracy = 0.97
```

**SAI:**
```
Kết quả rất tốt, độ chính xác cao.
```

### 4.3. Ghi Rõ "Không Áp Dụng" Khi Phù Hợp

Nếu bài báo không phải GAN (ví dụ: chỉ dùng SMOTE), ghi rõ:

```markdown
### G1. Stability Techniques — Không áp dụng (tree-based ensemble, không GAN)
### G2. Mode Collapse — Không áp dụng (classification, không generation)
```

### 4.4. Cross-Reference Giữa Các Bài Báo

Khi phát hiện liên quan đến bài khác:

```markdown
**Liên quan đến SQLi:** Agrawal 2024 cảnh báo — synthetic data cần validate correlations.
```

### 4.5. Phát Hiện Vấn Đề — Không Ngại Ghi Nhận

Nếu phát hiện paper yếu, duplicate, hoặc kết quả đáng ngờ:

```markdown
### NGHI VẤN
- Near-duplicate publication — khác tác giả nhưng nội dung identical
- CWGAN-GP cho R² = -1.7253 → synthetic data kém chất lượng
```

---

## 5. TEMPLATE TỐI THIỂU

File phân tích mới phải bắt đầu bằng:

```markdown
# Phân tích: [Tên Bài Báo]

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | |
| **Tác giả** | |
| **Năm** | |
| **Conference / Journal** | |
| **Link** | |

### A1. Phân Loại GAN Taxonomy
...
```

---

## 6. FILE TỔNG HỢP (Khi Phân Tích Nhiều Bài)

Khi có ≥3 bài phân tích, tạo file `TONG_HOP_*.md` với:

1. **Bảng ranking** tất cả bài báo — nhóm theo relevance
2. **Chi tiết 3-5 bài quan trọng nhất** — full analysis
3. **Tổng hợp phát hiện** — insights cross-paper
4. **Bảng so sánh** — các papers cùng domain
5. **Kiến trúc đề xuất** — dựa trên lessons learned
6. **Khuyến nghị** — actionable next steps
7. **References đầy đủ** — citation table

---

## 7. CHECKLIST TRƯỚC KHI HOÀN THÀNH

- [ ] Đủ 9 phần (A–I)
- [ ] Tất cả tables có header rõ ràng
- [ ] Có rating ⭐ trong Verdict
- [ ] Có Actionable Insights table
- [ ] Có Research Gaps table
- [ ] ASCII architecture diagram (nếu có model)
- [ ] Reproducibility Checklist điền đầy đủ
- [ ] Số liệu cụ thể, không nhận xét mơ hồ
- [ ] Cross-reference đến papers liên quan
- [ ] Summary 1-2 câu ở cuối

---

*Tài liệu này được tạo dựa trên phân tích 30+ bài báo và template `scientific_paper_analysis_template.md`.*
