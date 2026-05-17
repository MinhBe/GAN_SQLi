# Phân tích: Towards Unbalanced Multiclass Intrusion Detection with Hybrid Sampling Methods and Ensemble Classification

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | Towards unbalanced multiclass intrusion detection with hybrid sampling methods and ensemble classification |
| **Tác giả** | Thi-Thu-Huong Le, Yeongjae Shin, Myeongkil Kim, Howon Kim |
| **Năm** | 2024 |
| **Conference / Journal** | Applied Soft Computing, Volume 157, 111517 (Elsevier) |
| **Link** | https://doi.org/10.1016/j.asoc.2024.111517 |

### A1. Phân Loại GAN Taxonomy

| Thuộc tính | Lựa chọn |
|------------|----------|
| **GAN Type** | Ensemble Classification (Không phải GAN — hybrid sampling + boosting) |
| **Architecture Family** | Tree-based (CatBoost / LightGBM / XGBoost) |
| **Divergence** | N/A (classification loss — multi:softprob) |
| **Task Type** | Intrusion Detection — Multiclass Classification, Data Augmentation (SMOTE-based) |

### A2. Code Availability

| Mục | Thông tin |
|-----|-----------|
| **Official code** | Không (Data will be made available on request) |
| **URL** | N/A |
| **Framework** | Python 3.8, scikit-learn, TensorFlow |
| **Dependencies** | scikit-learn, TensorFlow, XGBoost, LightGBM, CatBoost |

---

## Phần B: Dữ Liệu — Data Pipeline Deep-Dive

### B1. Dataset Overview

| Thuộc tính | CHADC2020 | IoTID20 |
|------------|-----------|---------|
| **Nguồn** | Car Hacking: Attack and Defense Challenge 2020 | IoT device maker collaboration 2020 |
| **Kích thước** | ~2 triệu entries | ~5 triệu entries |
| **Benign** | ~1.95M | ~4.8M |
| **Malicious** | ~50,000 | ~200,000 |
| **Domain** | In-vehicle network (CAN bus) | IoT network traffic |
| **Public / Private** | Public | Public |

### B2. Data Characteristics

| Đặc điểm | CHADC2020 | IoTID20 |
|----------|-----------|---------|
| **Data type** | Tabular | Tabular |
| **Input dimensions** | Nhiều features (telemetry: speed, RPM, brake pressure) | Nhiều features (device telemetry, network packets) |
| **Class distribution** | Cực kỳ mất cân bằng (~97.5% benign) | Cực kỳ mất cân bằng (~96% benign) |
| **Imbalance ratio** | ~39:1 | ~24:1 |

### B3. Preprocessing Pipeline

| Bước | Chi tiết | Công cụ / Library |
|------|----------|-------------------|
| **Handling missing** | [x] Median imputation | pandas |
| **Normalization** | [x] Min-Max scaling [0,1] | scikit-learn |
| **Feature selection** | [x] Correlation-based | pandas |
| **Handling imbalance** | [x] Hybrid US-OS: ENN, Tomek Links, SMOTE, BorderlineSMOTE, SMOTETomek, SMOTEENN, BorderlineSMOTETomek | imbalanced-learn |

### B4. Feature Engineering

| Loại | Mô tả |
|------|-------|
| **Manual features** | N/A (raw telemetry / network features) |
| **Statistical features** | Correlation-based selection |
| **Dimensionality reduction** | [ ] None (correlation-based selection thay vì reduction) |

### B5. Data Loading

| Thông số | Giá trị |
|----------|---------|
| **Batch size** | N/A (tree-based, không batch training) |
| **Sampling strategy** | [ ] Auto (sampling strategy) |

### B6. Data Leakage Check

| Checklist | Status |
|-----------|--------|
| Train/Val/Test random split | [x] Có (training/testing phases riêng) |
| No data leakage between splits | [x] Implicit (test set riêng cho evaluation cuối) |
| No temporal leakage | Không rõ (CAN bus data có temporal nature) |
| No duplicate across splits | Không rõ |

---

## Phần C: Kiến Trúc Mô Hình — Architecture Blueprint

### C1. Tổng Quan Kiến Trúc

```
Raw Data → Preprocessing (clean + normalize + feature select)
    ↓
Hybrid Sampling (US → OS → US-OS combinations)
    ↓
┌────────────────────────────────────────────────────┐
│              Ensemble Classification                │
├─────────────────┬─────────────────┬────────────────┤
│    CatBoost     │    LightGBM     │    XGBoost     │
│ (depth=6,       │ (objective:     │ (objective:    │
│  lr=0.1,        │  multi:softprob, │  multi:softprob,│
│  iter=500)      │  n_estim=100)   │  n_estim=100)  │
└─────────────────┴─────────────────┴────────────────┘
    ↓
Majority Voting / Weighted Aggregation
    ↓
Final Prediction (multiclass attack classification)
```

### C2. Sampling Components

#### Undersampling Methods

| Method | Type | Mechanism |
|--------|------|-----------|
| ENN | Undersampling | Remove instances misclassified by k-NN neighbors |
| Tomek Links | Undersampling | Remove pairs of nearest neighbors from opposite classes |

#### Oversampling Methods

| Method | Type | Mechanism |
|--------|------|-----------|
| SMOTE | Oversampling | Interpolate between minority instances |
| BorderlineSMOTE | Oversampling | Focus on borderline minority instances |

#### Hybrid Methods (US-OS)

| Method | Oversampling | Undersampling | Rationale |
|--------|-------------|---------------|-----------|
| SMOTETomek | SMOTE | Tomek Links | SMOTE augments → Tomek cleans boundaries |
| SMOTEENN | SMOTE | ENN | SMOTE augments → ENN removes noisy instances |
| BorderlineSMOTETomek | BorderlineSMOTE | Tomek Links | Focus on borderline + clean boundaries |

### C3. Ensemble Classifiers

| Model | Key Features | Hyperparameters |
|-------|-------------|----------------|
| **CatBoost** | Symmetric trees, ordered boosting | lr=0.1, depth=6, iterations=500, loss=MultiClass |
| **LightGBM** | Leaf-wise growth, GOSS | objective=multi:softprob, n_estimators=100 |
| **XGBoost** | Regularized boosting, pruning | objective=multi:softprob, n_estimators=100 |

### C4. Layer Functional Analysis — Không áp dụng (tree-based ensemble, không neural network layers)

### C5. Conditioning Method — N/A

---

## Phần D: Training Configuration

### D1. Optimizer & Learning Rate

| Hyperparameter | CatBoost | LightGBM | XGBoost |
|---------------|----------|----------|---------|
| **Learning rate** | 0.1 | default | default |
| **Boosting iterations** | 500 | 100 | 100 |

### D2. Training Loop

| Hyperparameter | Value |
|---------------|-------|
| **Hardware** | Intel i7-10700K, 64GB RAM |
| **Validation** | Learning curve trên training/validation |
| **Evaluation** | ROC curve + Precision/Recall/F1/Accuracy |

### D3. Regularization

| Technique | Status |
|-----------|--------|
| **XGBoost regularization** | [x] Yes (L1/L2 regularization built-in) |
| **Pruning** | [x] Yes (XGBoost) |
| **CatBoost overfitting detector** | [x] Yes |

### D4. Loss Function Details

| Loss Component | Formula |
|----------------|---------|
| **Multi-class classification** | multi:softprob (cross-entropy) |

### D5. Reproducibility Checklist

| Item | Status |
|------|--------|
| Random seed reported | [x] Yes — random_state=42 |
| Hardware specified | [x] Yes — i7-10700K, 64GB RAM |
| Training time reported | [ ] No |
| Framework version specified | [ ] Partial — Python 3.8, libraries named |
| Hyperparameters fully specified | [x] Yes — Tables 2 & 3 |

**Confidence to reproduce:** ⭐⭐⭐⭐☆ — Hyperparameters rõ ràng, preprocessing steps cụ thể

---

## Phần E: So Sánh Với Baselines — Beyond Baselines

### E1. Key Comparisons

| Component | Prior Work | This Paper |
|-----------|-----------|------------|
| Sampling approach | US or OS alone | Hybrid US-OS (7 combinations) |
| Classifiers | Single model | Ensemble (3 models) |
| Evaluation | Binary classification | Multiclass IDS |
| Datasets | Various | CHADC2020 + IoTID20 |
| Focus | Either undersampling or oversampling | Integration of both trong ensemble framework |

### E2. Key Modifications

| Component | What Changed | Expected Benefit | Actual Result |
|-----------|-------------|-------------------|----------------|
| Sampling | US-OS hybrid thay vì US hoặc OS riêng | Giảm information loss (US) + overfitting (OS) | F1 > 98% |
| Ensemble | 3 classifiers + voting | Robust aggregation | CatBoost/XGBoost outperform LightGBM |
| Borderline focus | BorderlineSMOTE + Tomek | Clearer decision boundaries | Best combo: BorderlineSMOTETomek + XGBoost |

### E3. "X-Factor" — Innovation Chính

**Hệ thống hoá 7 kỹ thuật hybrid sampling (US, OS, US-OS) kết hợp 3 ensemble classifiers (CatBoost, LightGBM, XGBoost) trong cùng một framework, chứng minh BorderlineSMOTETomek + XGBoost đạt F1 > 98% trên 2 IDS datasets multiclass.**

---

## Phần F: Ablation & Experiments — Surgical Analysis

### F1. Research Questions

| # | Research Question |
|---|-------------------|
| RQ1 | Hybrid US-OS có outperform US hoặc OS riêng trong multiclass IDS không? |
| RQ2 | Ensemble model nào (CatBoost / LightGBM / XGBoost) kết hợp tốt nhất với sampling? |
| RQ3 | BorderlineSMOTETomek + XGBoost có outperform prior methods trên CHADC2020 và IoTID20 không? |

### F2. Ablation Study

#### F2.1. Ablation Variants (implicit in experimental design)

| Variant | Sampling | Classifier |
|---------|----------|------------|
| V1 (BL) | None | CatBoost baseline |
| V2 (BL) | None | LightGBM baseline |
| V3 (BL) | None | XGBoost baseline |
| V4 | ENN (US) | CatBoost / LightGBM / XGBoost |
| V5 | Tomek (US) | CatBoost / LightGBM / XGBoost |
| V6 | SMOTE (OS) | CatBoost / LightGBM / XGBoost |
| V7 | BorderlineSMOTE (OS) | CatBoost / LightGBM / XGBoost |
| V8 | SMOTETomek (US-OS) | CatBoost / LightGBM / XGBoost |
| V9 | SMOTEENN (US-OS) | CatBoost / LightGBM / XGBoost |
| V10 | BorderlineSMOTETomek (US-OS) | CatBoost / LightGBM / XGBoost |

#### F2.2. Key Results (CHADC2020 — F1 Score)

| Variant | CatBoost | LightGBM | XGBoost |
|---------|:--------:|:--------:|:-------:|
| BL (no sampling) | 0.90 | 0.75 | 0.93 |
| ENN (US) | 0.92 | 0.92 | 0.93 |
| Tomek (US) | 0.93 | 0.93 | 0.90 |
| SMOTE (OS) | 0.95 | 0.96 | 0.96 |
| BorderlineSMOTE (OS) | 0.95 | 0.96 | **0.97** |
| SMOTETomek (US-OS) | 0.95 | 0.96 | 0.96 |
| SMOTEENN (US-OS) | **0.97** | 0.93 | 0.96 |
| BorderlineSMOTETomek (US-OS) | 0.96 | 0.96 | **0.98** |

#### F2.3. Key Ablation Insight

**BorderlineSMOTETomek + XGBoost là best combination cho cả 2 datasets (F1=0.98). Oversampling (OS) outperform undersampling (US). Hybrid US-OS nói chung không outperform OS riêng đáng kể — lợi ích chính là decision boundary refinement.**

### F3. Statistical Rigor

| Metric | Value |
|--------|-------|
| Number of random seeds | 1 (random_state=42) |
| Confidence intervals | Không báo cáo |
| Significance test used | Không |

---

## Phần G: Training Stability & Mode Collapse

### G1. Stability Techniques (tree-based ensemble, không có GAN stability issues)

### G2. Mode Collapse — Không áp dụng (classification, không generation)

### G3. Observed Issues

| Issue | Occurred? |
|-------|-----------|
| Overfitting | [x] Discussed — XGBoost regularization + pruning mitigates |
| Computational overhead | [x] Yes — acknowledged as limitation |
| Efficiency | LightGBM hiệu quả nhất về computation nhưng accuracy thấp hơn |

---

## Phần H: Kết Quả & Đánh Giá

### H1. Quantitative Results

#### H1.1. Best Results

| Dataset | Method | Precision | Recall | Accuracy | F1 |
|---------|--------|:--------:|:------:|:--------:|:--:|
| CHADC2020 | BorderlineSMOTETomek + XGBoost | 0.98 | **0.99** | 0.97 | **0.98** |
| IoTID20 | BorderlineSMOTETomek + XGBoost | 0.99 | 0.98 | 0.98 | **0.98** |

#### H1.2. Comparison with Prior Methods

| Dataset | Prior Best (Method) | Prior F1/Acc | Ours F1 |
|---------|--------------------|:----------:|:-------:|
| CHADC2020 | GIDS (GAN-based) | Acc=98% | **F1=98%** |
| CHADC2020 | FCN | F1=97.86% | **F1=98%** |
| IoTID20 | PSO+XGB+RF | Acc=83% | **F1=98%** |
| IoTID20 | RF | Acc=96.5% | **F1=98%** |

### H2. Qualitative Analysis

| Aspect | Observation |
|--------|-------------|
| **ROC-AUC** | 0.96 — excellent discrimination capability |
| **LightGBM** | Fastest training but consistently lowest accuracy |
| **CatBoost vs XGBoost** | CatBoost tốt với US; XGBoost tốt nhất với OS và US-OS |
| **Failure cases** | 'Spoofing' attack on CHAD2020 — chỉ 55% ROC accuracy với Tomek+CatBoost |

### H3. Limitations (tự paper thừa nhận)

| Limitation | Description |
|------------|-------------|
| 1 | Computational overhead với large datasets |
| 2 | Generalizability to diverse network environments |
| 3 | Interpretability của ensemble models |
| 4 | Robustness to evolving threats |

---

## Phần I: Đánh Giá Cá Nhân

### I1. Điểm Mạnh

| # | Strength | Evidence |
|---|----------|----------|
| 1 | Experimental design systematic | 7 sampling × 3 classifiers = 21 combinations trên 2 datasets |
| 2 | Practical contribution | F1 > 98% — sẵn sàng cho deployment |
| 3 | Clear baseline comparison | So sánh với prior methods (GIDS, FCN, PSO+XGB+RF) |

### I2. Điểm Yếu

| # | Weakness | Evidence |
|---|-----------|----------|
| 1 | Không novelty về methodology | SMOTE, Tomek, ENN, BorderlineSMOTE đều là existing techniques |
| 2 | Không statistical rigor | Chỉ 1 seed, không confidence intervals, không significance test |
| 3 | So sánh với GIDS (2018) không cập nhật | GIDS đã cũ, không so sánh với recent GAN-based IDS |
| 4 | Temporal leakage không được check | CAN bus data có temporal dependencies |

### I3. Actionable Insights — What I Can Use

| Idea | Source | Priority | Effort | How to implement |
|------|--------|----------|--------|-------------------|
| **SMOTE + GAN hybrid augmentation** | SMOTE / BorderlineSMOTE logic combined với GAN | High | Medium | Dùng GAN generate SQLi + SMOTE-like interpolation for non-SQL features |
| **BorderlineSMOTE logic cho SQLi** | BorderlineSMOTE focuses on "danger" instances | High | Low | Prioritize generation near decision boundary (legitimate vs SQLi) |
| **Ensemble validation framework** | 3 classifiers (CatBoost/ LightGBM / XGBoost) | Medium | Low | Validate synthetic SQLi quality bằng ensemble detection rate |
| **Hybrid sampling pipeline** | US-OS pipeline architecture | Medium | Medium | Undersample majority legitimate + oversample minority SQLi before GAN training |

### I4. Research Gaps Identified

| Gap | Description | Potential direction |
|-----|-------------|---------------------|
| 1 | Paper không dùng GAN cho oversampling | GAN-SQLi có thể thay thế SMOTE bằng GAN-generated SQLi |
| 2 | No validation of synthetic data feature correlations | Agrawal 2024 cảnh báo — synthetic data cần validate correlations |
| 3 | Single dataset domain (CAN bus + IoT) | Cần validate trên web application datasets (HTTP payloads) |

### I5. Verdict

| Criteria | Rating | Notes |
|----------|--------|-------|
| **Technical soundness** | ⭐⭐⭐⭐☆ | Experimental design vững, kết quả clear |
| **Novelty** | ⭐⭐⭐☆☆ | Hybrid sampling là combination, không phải new technique |
| **Reproducibility** | ⭐⭐⭐⭐☆ | Hyperparameters + preprocessing được specify đầy đủ |
| **Overall quality** | ⭐⭐⭐⭐☆ | Bài báo applied tốt, practical value cao |

**Summary:** Bài báo cung cấp systematic comparison của 7 hybrid sampling methods + 3 ensemble classifiers trên 2 IDS datasets. Best configuration (BorderlineSMOTETomek + XGBoost) đạt F1 > 98%. Dù không sử dụng GAN, pipeline hybrid sampling và ensemble evaluation framework là reference quan trọng cho GAN_SQLi validation.

---

## References & Related Works

- GIDS (Seo et al., 2018) — GAN-based IDS for in-vehicle network
- CTGAN (Dina et al., 2022) — Conditional GAN for oversampling
- CTGAN-MOS (Majeed et al., 2023) — CTGAN Minority-Class-Augmented Oversampling
- Ding et al. (2022) — KNN + GAN hybrid for imbalanced IDS
- Le et al. (2022) — XGBoost + SHAP for IDS explanation

---

## Appendix: Raw Notes

- Paper uses traditional SMOTE-based oversampling — KHÔNG dùng GAN
- GIDS (Seo et al., 2018) là GAN-based IDS được so sánh — outdated
- Key practical takeaway: BorderlineSMOTETomek + XGBoost là config chuẩn cho multiclass IDS
- LightGBM bị underperform so với CatBoost và XGBoost trong hầu hết configurations
- Thứ tự performance: OS > US-OS > US > BL
