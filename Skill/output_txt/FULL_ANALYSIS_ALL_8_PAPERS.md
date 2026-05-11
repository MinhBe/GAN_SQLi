# PHÂN TÍCH ĐẦY ĐỦ 8 BÀI BÁO GAN & AN NINH MẠNG

---

## BÀI BÁO 1: Advancements in Sequence Generation: A GAN-Based Reinforcement Learning Approach
**Tệp:** `C:\Projects\GAN_SQLi\Skill\output_txt\Advancements in Sequence Generation_ A GAN-Based Reinforcement Le.txt`

### A. THÔNG TIN CƠ BẢN
- **Tác giả:** Janet Rodriguez
- **Năm:** 2024 (15 Apr 2024)
- **Loại:** Technical Disclosure / Defensive Publication
- **Hội thảo/Tạp chí:** Technical Disclosure Commons (dpubs_series/6878)
- **Lĩnh vực:** Sequence Generation, NLP, Reinforcement Learning
- **Vấn đề:** Cải thiện SeqGAN cho sinh chuỗi token rời rạc

### B. PHÂN LOẠI GAN
- **Loại GAN chính:** SeqGAN (Sequence Generative Adversarial Nets)
- **Họ kiến trúc:** RNN (LSTM) Generator + CNN Discriminator + Policy Gradient (REINFORCE)
- **Hàm mất mát:** Cross-entropy (SeqGAN), Wasserstein distance (WGAN improvement), Clipped surrogate objective (PPO)
- **Kiểu tác vụ:** Sinh chuỗi rời rạc (discrete token sequence generation)

### C. QUY TRÌNH DỮ LIỆU
- **Nguồn dữ liệu:** Synthetic — oracle LSTM sinh 10,000 chuỗi độ dài 20
- **Tiền xử lý:** Token embedding, one-hot encoding
- **Kích thước:** 10,000 sequences, vocabulary size không được nêu rõ
- **Chia tập:** Không tách biệt (oracle dùng để sinh training set và đánh giá)

### D. KIẾN TRÚC
- **Generator:** LSTM, input là embedding vectors, softmax output layer, dùng LSTM cells để tránh vanishing gradient
- **Discriminator:** CNN với multiple kernels (window size 1-T), max-over-time pooling, highway architecture, fully connected + sigmoid output
- **Cơ chế đặc biệt:** Monte Carlo tree search (N lần roll-out), Policy Gradient (REINFORCE), discriminator đóng vai trò reward function
- **Pre-training:** MLE pretrain cho Generator trước khi adversarial training

### E. HUẤN LUYỆN
- **Pretrain:** MLE trên training set S (10,000 sequences)
- **Adversarial training:** Generator và Discriminator luân phiên — g-steps cho G, d-steps cho D
- **Cân bằng mẫu:** Số negative samples = số positive samples, dùng bootstrapping
- **Optimizer:** Adam, RMSprop (lưu ý: WGAN không dùng Adam, khuyến nghị RMSprop/SGD)

### F. CÁC ĐƯỜNG CƠ SỞ
- **So sánh với:** Random generation, MLE-trained LSTM, Scheduled Sampling, PG-BLEU (Policy Gradient với BLEU score)
- **Các cải tiến thử nghiệm:** WGAN, Improved WGAN (gradient penalty), Batch size increase, PPO, log-PPO

### G. THỬ NGHIỆM ABLATION
- So sánh từng cải tiến riêng lẻ:
  - SeqGAN gốc: NLL=8.639
  - WGAN: NLL=8.824 (kém hơn)
  - Improved WGAN: NLL=8.509 (tốt nhất)
  - Batch increase: NLL=8.567
  - PPO: NLL=9.065 (kém nhất)
  - PPO and change (log-PPO): NLL=8.729

### H. KẾT QUẢ
- **Chỉ số chính:** Negative Log-Likelihood (NLL) so với oracle — SeqGAN đạt 8.639, vượt MLE (9.038), Scheduled Sampling (8.985), PG-BLEU (8.946)
- **Improved WGAN là tốt nhất** (8.509) nhờ ổn định hội tụ
- **WGAN gốc bị overfitting** — hội tụ nhanh đến local optimum rồi giảm dần
- **Batch increase** nhảy ra khỏi valley sau ~150 epochs
- **PPO thua REINFORCE** — nguyên nhân đề nghị nghiên cứu thêm

### I. NHẬN XÉT CÁ NHÂN
- **⭐ (2/5):** Tài liệu kỹ thuật ngắn, không peer-reviewed, thuộc dạng defensive publication. Kết quả chỉ trên synthetic data, không có real-world validation. Tuy nhiên, phân tích ablation khá chi tiết.
- **Điểm mạnh:** So sánh có hệ thống nhiều policy gradient methods, phát hiện Improved WGAN > WGAN gốc cho discrete sequences, phát hiện PPO không phù hợp.
- **Điểm yếu:** Không có real dataset, không có statistical significance tests thực sự, số lượng epoch không chuẩn hóa.
- **Liên quan đến SQLi:** Có thể áp dụng SeqGAN-style cho sinh câu truy vấn SQL độc hại như discrete sequence generation task.

---

## BÀI BÁO 2: A Survey on GAN Techniques for Data Augmentation to Address the Imbalanced Data Issues in Credit Card Fraud Detection
**Tệp:** `C:\Projects\GAN_SQLi\Skill\output_txt\bf885090a345faa62a5cc818db2fd42a247a.txt`

### A. THÔNG TIN CƠ BẢN
- **Tác giả:** Emilija Strelcenia & Simant Prakoonwit (Bournemouth University, UK)
- **Năm:** 2023 (Published: 11 March 2023)
- **Loại:** Survey paper
- **Tạp chí:** Machine Learning and Knowledge Extraction (MDPI), Vol. 5, 304–329
- **Lĩnh vực:** Fraud Detection, Class Imbalance, Data Augmentation
- **Vấn đề:** Xử lý mất cân bằng lớp trong phát hiện gian lận thẻ tín dụng

### B. PHÂN LOẠI GAN
- **Các loại GAN được khảo sát:**
  - Duo-GAN (2 GANs — 1 cho fraud, 1 cho legal)
  - Majority-Minority GAN Transfer
  - CTAB-GAN (Conditional Table GAN)
  - SDG-GAN (Synthetic Data Generation GAN)
  - OCAN (One-Class Adversarial Nets)
  - Table-GAN
  - WGAN, WGAN-GP
  - cGAN (Conditional GAN)
  - IGAFN (Imbalanced Generative Adversarial Fusion Network)
- **Họ kiến trúc:** Đa dạng — MLP, LSTM-autoencoder, CNN
- **Hàm mất mát:** Cross-entropy, Wasserstein distance, Feature matching loss
- **Kiểu tác vụ:** Data augmentation cho imbalanced classification

### C. QUY TRÌNH DỮ LIỆU
- **Nguồn dữ liệu (các paper được survey sử dụng):** Credit card transaction datasets (thường rất imbalanced), Pima Diabetes, Breast Cancer Wisconsin
- **Tiền xử lý:** Encoding mixed data types, handling missing values, mode-specific normalization (CTAB-GAN)
- **Vấn đề:** Tỉ lệ mất cân bằng cực cao (fraud transactions << legal transactions)

### D. KIẾN TRÚC (điển hình)
- **Duo-GAN:** Hai GAN song song — mỗi GAN học phân phối của một class
- **Majority-Minority GAN Transfer:** Học majority class trước, chuyển một phần cấu trúc sang minority GAN — transfer learning
- **CTAB-GAN:** Conditional generator + mode-specific normalization cho mixed data types
- **OCAN:** LSTM-autoencoder cho feature extraction + GAN discriminator cho one-class classification
- **SDG-GAN:** MLP feed-forward + Feature matching loss

### E. HUẤN LUYỆN
- **Alternating training:** G và D luân phiên
- **Duo-GAN:** Hai GAN được train riêng biệt
- **OCAN:** Hai phase — Phase 1: LSTM-autoencoder, Phase 2: GAN training
- **Thách thức:** Mode collapse, vanishing gradient, training instability

### F. CÁC ĐƯỜNG CƠ SỞ
- SMOTE, ROS (Random Oversampling), RUS (Random Undersampling), các GAN variants khác
- So sánh trên Precision, Recall, F1-score

### G. THỬ NGHIỆM ABLATION
- Duo-GAN so với single-GAN: Duo-GAN outperforms
- CTAB-GAN so với CTGAN, Table-GAN, MedGAN: CTAB-GAN outperforms
- OCAN so với one-class SVM, isolation forest: OCAN tốt hơn

### H. KẾT QUẢ
- **Ngwenduna & Mbuvha (2020):** WGAN-GP + XGBoost tăng 5% recall trên credit card fraud detection
- **Kim et al.:** CTAB-GAN vượt state-of-the-art cho tabular data generation
- **Ba (2019):** GAN augmentation outperforms các phương pháp khác về generalization
- **OCAN:** Vượt các one-class classification models khác
- **CTAB-GAN:** Outperforms CTGAN, MedGAN, Table-GAN về Accuracy, F1, AUC

### I. NHẬN XÉT CÁ NHÂN
- **⭐⭐⭐ (3/5):** Survey khá toàn diện, phủ nhiều GAN variants cho financial fraud detection. Có so sánh có cấu trúc (strengths/limitations table). Nhưng chủ yếu là liệt kê, không có meta-analysis định lượng.
- **Điểm mạnh:** Bao phủ nhiều GAN variants, phân tích Strengths/Limitations cho từng loại, có so sánh evaluation metrics
- **Điểm yếu:** Không có empirical experiments riêng, chủ yếu tổng hợp literature. Một số GAN variants thiếu chi tiết implementation
- **Liên quan đến SQLi:** Survey approach có thể tham khảo cho taxonomy of GAN-based SQLi detection/augmentation. Phân loại GAN variants có thể mapping sang cybersecurity tasks.

---

## BÀI BÁO 3: Nghiên cứu các mô hình GAN xử lý mất cân bằng dữ liệu trong dự đoán lỗi phần mềm
**Tệp:** `C:\Projects\GAN_SQLi\Skill\output_txt\DHVH-2023-03.KHCN-Ha Thi Minh Phuong.txt`

### A. THÔNG TIN CƠ BẢN
- **Tác giả:** ThS. Hà Thị Minh Phương (Đại học Đà Nẵng, trường ĐH CNTT&TT Việt-Hàn)
- **Năm:** 2023 (tháng 5-12/2023)
- **Loại:** Báo cáo tổng kết đề tài khoa học và công nghệ cấp cơ sở
- **Mã số:** ĐHVH-2023-03
- **Lĩnh vực:** Software Fault Prediction, Class Imbalance, Feature Selection
- **Vấn đề:** Xử lý mất cân bằng dữ liệu trong dự đoán lỗi phần mềm

### B. PHÂN LOẠI GAN
- **Các loại GAN được sử dụng:**
  - VanillaGAN
  - CTGAN (Conditional Tabular GAN)
  - WGANGP (Wasserstein GAN with Gradient Penalty)
- **Họ kiến trúc:** MLP-based GAN, Conditional GAN, WGAN
- **Hàm mất mát:** Cross-entropy (VanillaGAN, CTGAN), Wasserstein distance + gradient penalty (WGANGP)
- **Kiểu tác vụ:** Oversampling cho imbalanced software fault prediction

### C. QUY TRÌNH DỮ LIỆU
- **Nguồn dữ liệu:** 4 datasets từ PROMISE repository: CM1, KC1, KC3, PC1
- **Đặc trưng:** Software metrics (các độ đo phần mềm — coupling, lines of code, complexity metrics)
- **Feature Selection:** 4 kỹ thuật filter-based: Chi-Squared, Information Gain, Fisher, Relief
- **Kích thước (ví dụ):** CM1: ~500 modules, PC1: ~1000 modules. Tỉ lệ mất cân bằng vừa phải.
- **Chia tập:** Train/test split cho từng dataset

### D. KIẾN TRÚC
- **Feature Selection:** Filter-based ranking (Chi2, IG, Fisher, Relief)
- **GAN Augmentation:** Dùng GAN sinh synthetic minority class samples
- **Classifier:** Random Forest (RF), Extra Tree (ET), AdaBoost (AB), Histogram Gradient Boosting (HGB)
- **Pipeline:** Feature Selection → GAN Oversampling → Classifier Training

### E. HUẤN LUYỆN
- **Kết hợp feature selection + GAN:** 4 × 3 = 12 combinations
- Đánh giá trên 4 classifiers × 4 datasets = 16 scenarios per combination
- **Metrics:** Precision, Recall, F1-score, AUC

### F. CÁC ĐƯỜNG CƠ SỞ
- So sánh GAN methods với traditional sampling: SMOTE, ADASYN, Border-SMOTE, Random Undersampling
- So sánh với no-sampling baseline

### G. KẾT QUẢ CHI TIẾT (Average across 4 datasets)

**Với Chi-Squared feature selection:**
| Metric | VanillaGAN+ET | CTGAN+ET | WGANGP+ET |
|--------|--------------|----------|-----------|
| Precision | 0.844 | 0.848 | 0.837 |
| Recall | 0.841 | 0.867 | 0.781 |
| F1 | 0.840 | 0.851 | 0.790 |
| AUC | 0.775 | 0.771 | 0.722 |

**Với Relief feature selection (tốt nhất):**
| Metric | VanillaGAN+ET | CTGAN+ET | WGANGP+ET |
|--------|--------------|----------|-----------|
| Precision | 0.843 | **0.857** | 0.841 |
| Recall | 0.842 | **0.873** | 0.773 |
| F1 | 0.840 | **0.856** | 0.782 |
| AUC | 0.767 | 0.767 | 0.720 |

**Kết luận chi tiết:**
- **Relief + CTGAN + Extra Tree** là combination tốt nhất: Precision=0.857, Recall=0.873, F1=0.856, AUC=0.767
- **Relief + CTGAN + HGB** cũng mạnh: Precision=0.851, Recall=0.867, F1=0.855, AUC=0.758
- **CTGAN consistently outperforms** VanillaGAN và WGANGP across hầu hết metrics và feature selection methods
- **WGANGP hoạt động kém nhất** — đặc biệt Recall chỉ ~0.72-0.78 so với CTGAN ~0.85-0.87

### H. KẾT QUẢ WRAPPER-BASED FEATURE SELECTION
- Cũng được thử nghiệm nhưng kết quả trong bảng 6 và 7 (không được extract đầy đủ trong text)
- Wrapper methods nhìn chung đắt hơn về mặt tính toán

### I. NHẬN XÉT CÁ NHÂN
- **⭐⭐⭐ (3/5):** Nghiên cứu thực nghiệm có hệ thống tốt, phủ 3 GAN variants × 4 feature selection methods × 4 classifiers × 4 datasets. Code và implementation rõ ràng (báo cáo đề tài cấp cơ sở).
- **Điểm mạnh:** So sánh toàn diện nhiều combinations, tập trung vào tabular data oversampling, dataset từ PROMISE repository có tính chuẩn hóa cao
- **Điểm yếu:** Limited novelty — áp dụng existing methods vào bài toán SFP, không đề xuất architecture mới. WGANGP tuning có thể chưa optimal. All datasets đều là cũ (NASA PROMISE).
- **Liên quan đến SQLi:** Trực tiếp relevant — cùng bài toán class imbalance + tabular data + binary classification. Feature selection + GAN oversampling pipeline có thể apply cho SQLi detection. CTGAN là lựa chọn tốt cho tabular data oversampling.

---

## BÀI BÁO 4: A comparative study on SMOTE, CTGAN, and hybrid SMOTE-CTGAN for medical data augmentation
**Tệp:** `C:\Projects\GAN_SQLi\Skill\output_txt\document.txt`

### A. THÔNG TIN CƠ BẢN
- **Tác giả:** Ninda Khoirunnisa & Miftahurrahma Rosyda (Universitas Ahmad Dahlan, Indonesia)
- **Năm:** 2025 (May 2025)
- **Loại:** Research Article
- **Tạp chí:** Science in Information Technology Letters, Vol. 6, No. 1, pp. 44-54
- **Lĩnh vực:** Medical Data Mining, Class Imbalance
- **Vấn đề:** So sánh SMOTE vs CTGAN vs Hybrid cho cardiovascular disease prediction

### B. PHÂN LOẠI GAN
- **Loại GAN chính:** CTGAN (Conditional Tabular GAN)
- **Họ kiến trúc:** Conditional GAN + Mode-specific normalization
- **Hàm mất mát:** Cross-entropy loss + Auxiliary cross-entropy loss cho conditional vector compliance
- **Kiểu tác vụ:** Oversampling minority class trong Framingham Heart Study dataset

### C. QUY TRÌNH DỮ LIỆU
- **Nguồn dữ liệu:** Framingham Heart Study dataset (cardiovascular disease)
- **Tiền xử lý:** Remove ID và time-to-event columns, median imputation cho missing values, filter outliers (BMI, blood pressure, glucose), z-score normalization
- **Chia tập:** 75%-25% stratified split
- **Augmentation:** Chỉ áp dụng cho minority class (CVD positive)

### D. KIẾN TRÚC
- **SMOTE:** K-nearest neighbors (k=5), interpolation-based
- **CTGAN:** Conditional generator + Mode-specific normalization + variational Gaussian mixture model
  - Conditional vector (cond): one-hot encoded categorical variables + mask vector
  - Training-by-sampling strategy with log-frequency sampling
  - Cross-entropy penalty cho condition violation
- **SMOTE+CTGAN (Hybrid):** Phase 1: SMOTE generates initial synthetic minority samples → Phase 2: CTGAN trains on the expanded minority set to generate additional samples
- **Classifiers:** Decision Tree (DT), Random Forest (RF), XGBoost

### E. HUẤN LUYỆN
- **CTGAN params:** 50 epochs, batch size 500
- **Classifiers:** Default parameters (không spec rõ hyperparameter tuning)
- **Evaluation:** Accuracy, Macro/Weighted Precision/Recall/F1, Class-specific metrics

### F. CÁC ĐƯỜNG CƠ SỞ
- Imbalanced baseline (no augmentation)
- SMOTE-only
- CTGAN-only
- SMOTE+CTGAN hybrid

### G. KẾT QUẢ CHI TIẾT

**Table 1: Macro Average Performance**
| Method | DT Acc | DT F1 | RF Acc | RF F1 | XGB Acc | XGB F1 |
|--------|--------|-------|--------|-------|---------|--------|
| No aug | 0.7289 | 0.6489 | 0.8072 | 0.6978 | 0.7991 | 0.6975 |
| SMOTE | 0.7790 | 0.7790 | **0.8484** | **0.8484** | **0.8484** | 0.8482 |
| CTGAN | 0.7809 | 0.7749 | 0.8424 | 0.8316 | 0.8280 | 0.8175 |
| SMOTE+CTGAN | **0.7880** | **0.7820** | 0.8401 | 0.8290 | 0.8303 | 0.8190 |

**Table 2: Class-Specific Metrics (Quan trọng)**
- **Imbalanced baseline:** RF recall-0 = 0.9413 nhưng recall-1 = **0.4084** (thiên vị majority rõ rệt)
- **SMOTE (RF):** recall-0 = 0.8450, recall-1 = **0.8528** (cân bằng nhất)
- **CTGAN (RF):** recall-0 = 0.9310, recall-1 = 0.7157 (giữ majority recall tốt hơn)
- **SMOTE+CTGAN (RF):** recall-0 = 0.9301, recall-1 = 0.7115

**SMOTE wins on minority recall** (0.85 vs 0.71-0.75), **CTGAN wins on majority class preservation** (0.93 vs 0.84-0.88)

### H. KẾT LUẬN
- Không có single best method — trade-off giữa minority recall và majority recall
- SMOTE tốt nhất khi cần maximize minority detection
- CTGAN và hybrid phù hợp khi cần preserve majority accuracy song song với cải thiện minority
- Lựa chọn augmentation method phụ thuộc vào clinical context

### I. NHẬN XÉT CÁ NHÂN
- **⭐⭐⭐ (3/5):** Thiết kế thực nghiệm sạch, so sánh rõ ràng, kết luận balanced và practical. Paper gần đây (2025).
- **Điểm mạnh:** So sánh fair giữa SMOTE và GAN-based methods. Phân tích class-specific metrics (không chỉ macro averages). Implementation details rõ ràng cho CTGAN. Kết luận thực tế không thiên vị.
- **Điểm yếu:** Limited hyperparameter tuning. Chỉ một dataset duy nhất. Chỉ dùng CTGAN, không so sánh với WGAN-GP hay các GAN variants khác cho tabular data.
- **Liên quan đến SQLi:** Trực tiếp relevant — SMOTE vs CTGAN vs Hybrid là câu hỏi có thể translate sang SQLi dataset augmentation. Framingham dataset có cấu trúc tương tự tabular network traffic data.

---

## BÀI BÁO 5: A Review of Generative Models in Generating Synthetic Attack Data for Cybersecurity
**Tệp:** `C:\Projects\GAN_SQLi\Skill\output_txt\electronics-13-00322.txt`

### A. THÔNG TIN CƠ BẢN
- **Tác giả:** Garima Agrawal, Amardeep Kaur, Sowmya Myneni (Arizona State University; University of Western Australia)
- **Năm:** 2024 (Published: 11 January 2024)
- **Loại:** Review + Critical Analysis (with experiments)
- **Tạp chí:** Electronics (MDPI), Vol. 13, 322
- **Lĩnh vực:** Cybersecurity, Synthetic Attack Data, GAN Evaluation
- **Vấn đề:** Liệu GAN-generated attack data có thực sự là attack data không?

### B. PHÂN LOẠI GAN
- **Các loại GAN được review:**
  - Vanilla GAN, DCGAN, CGAN, LAPGAN, PGGAN, StackGAN, InfoGAN, RenderGAN
  - WGAN, WGAN-GP, Cramer GAN, PAC-GAN
  - MalGAN, IDSGAN, Table-GAN, CTGAN
- **Họ kiến trúc:** Đa dạng — CNN, MLP, Laplacian pyramid, progressive growing
- **Hàm mất mát:** Cross-entropy, Wasserstein distance, Cramer distance, Mutual information
- **Kiểu tác vụ:** Sinh synthetic cyber attack data (DoS, adversarial examples, network traffic)

### C. QUY TRÌNH DỮ LIỆU (cho experiment riêng)
- **Nguồn dữ liệu:** NSL-KDD dataset (DoS attacks category)
- **Feature analysis:** Xác định features phản ánh DoS attack và correlation giữa chúng (Pearson's coefficient)
- **Các attack types trong NSL-KDD:** DoS (back, land, pod, smurf, teardrop), R2L, U2R, Probe
- **Số features:** 41 (9 discrete, 32 continuous)

### D. KIẾN TRÚC (cho experiment riêng)
- **Conditional GAN:** Discriminator trained chỉ trên attack samples
- **White-box model:** FNN (Feedforward Neural Network) supervised với cả normal + attack data
- **Anomaly detector:** Semi-supervised, trained chỉ trên normal data

### E. THỬ NGHIỆM ĐÁNH GIÁ SYNTHETIC DATA
**3 phương pháp đánh giá:**
1. **White-box model (FNN):** Detect normal vs attack — đạt >99% accuracy trên NSL-KDD test data
2. **Anomaly detector:** Semi-supervised — đạt >81% accuracy
3. **Statistical analysis:** Tính expected standard deviation của features phản ánh DoS, so sánh với GAN-generated data

### F. PHÁT HIỆN QUAN TRỌNG NHẤT
- **"Not normal ≠ attack data"**
- **White-box model** báo cáo GAN-generated data là "not normal" NHƯNG phân loại nó vào attack categories
- **Anomaly detector** cũng báo cáo "not normal"
- **Static analysis (Euclidean distance):** Feature values inconsistent — KHÔNG tương ứng với normal traffic hay DoS traffic
- **Feature correlations bị thiếu** — data là noise, không phải attack data
- **"not normal" được nhiều paper báo cáo là attack data nhưng thực chất chỉ là noise**

### G. CÁC MỤC REVIEW CHÍNH
- **Flow-based network traffic generation:** WGANs + IP2Vec embeddings + CIDDS-001 (Ring et al.); PAC-GAN (Cheng et al.); NetShare (Yin et al.)
- **Cyber intrusion alert data synthesis:** WGAN-GP, WPGAN-MI (Sweet et al.) — evaluated with histogram intersection và conditional entropy
- **Attack data via adversarial examples:** MalGAN (Hu et al.) — black-box malware example generation; IDSGAN — adversarial examples for IDS evasion
- **LLM-generated attack data:** ChatGPT-assisted phishing, malware generation (Karanjai, Beckerich)

### H. KẾT LUẬN
- GANs có khả năng sinh data có statistical similarity với real data
- Nhưng thiếu feature correlations cần thiết cho valid attack data
- Need balanced approach: combine natural + synthetic data
- Cần thêm research cho complex attacks: DDoS, SQL Injection, cross-site scripting
- **Future work:** Kết hợp LLMs + GANs cho synthetic attack data generation

### I. NHẬN XÉT CÁ NHÂN
- **⭐⭐⭐⭐ (4/5):** Paper xuất sắc với critical analysis độc lập, phát hiện quan trọng "not normal ≠ attack". Đây là paper hiếm hoi thực sự kiểm tra chất lượng GAN-generated attack data.
- **Điểm mạnh:** Critical analysis thay vì chỉ review, phát hiện noise problem, phân tích chi tiết feature correlation, discussion về LLMs
- **Điểm yếu:** Chỉ thử nghiệm với DoS từ NSL-KDD (dataset cũ), synthetic data experiment limited scope
- **Liên quan đến SQLi:** RẤT quan trọng — cảnh báo rằng GAN-generated attack data có thể là noise không phải valid attack data. Cần kiểm tra feature correlations của generated SQL queries trước khi dùng cho training.

---

## BÀI BÁO 6: Emerging SMOTE and GAN Variants for Data Augmentation in Imbalance Machine Learning Tasks: A Review
**Tệp:** `C:\Projects\GAN_SQLi\Skill\output_txt\Emerging_SMOTE_and_GAN_Variants_for_Data_Augmentation_in_Imbalance_Machine_Learning_Tasks_A_Review.txt`

### A. THÔNG TIN CƠ BẢN
- **Tác giả:** Amadi G. Udu, Marwah T. Salman, Maryam K. Ghalati, Andrea Lecchini-Visintini, David R. Siddle, Hongbiao Dong (University of Leicester; Wasit University; University of Southampton)
- **Năm:** 2025 (Published: 1 July 2025)
- **Loại:** Comprehensive Review
- **Tạp chí:** IEEE Access, Vol. 13
- **DOI:** 10.1109/ACCESS.2025.3584532
- **Lĩnh vực:** Class Imbalance, Data Augmentation
- **Vấn đề:** Unified taxonomy of class imbalance + emerging SMOTE and GAN variants

### B. PHÂN LOẠI GAN
- **Các GAN variants được review:**
  - WGAN-GP, LSGAN, HingeGAN
  - CTGAN, TableGAN, TGAN (modified)
  - CSWGAN (cosine similarity-based penalty)
  - LEGAN (intra-class model collapse addressing)
  - 1DWGANGP (multiple correlation analysis + GAN)
  - GAOSD (Bidirectional GAN + feature extraction)
  - Auxiliary classifier GAN (dual-module multi-head spatiotemporal)
- **SMOTE counterparts (comparative):** 85+ SMOTE variants trong Python package của Kovács
  - SMOTE-ENN, Borderline-SMOTE, SVM-SMOTE, ADASYN
  - OM-SMOTE, SMOTE-kTLNN, ASCFNO, MDOBoost
  - GLOS (global-local oversampling), COM (clustering-based)
  - SMOTE-TL, SMOTE+RSB, Safe-Level SMOTE

### C. TAXONOMY CỦA CLASS IMBALANCE
**Theo nguồn gốc:**
- **Intrinsic imbalance:** Do bản chất tự nhiên của dữ liệu (ví dụ: diseases hiếm)
- **Extrinsic imbalance:** Do phương pháp thu thập/preprocessing

**Theo số lớp:**
- **Binary imbalance:** 2 lớp (ví dụ: spam detection)
- **Multi-class imbalance:** >2 lớp (global imbalance × local imbalance)

**Theo tính chất:**
- **Relative imbalance:** m/N thấp
- **Absolute imbalance:** m intrinsically thấp
- **Static imbalance:** Constant over time
- **Dynamic imbalance:** Thay đổi theo thời gian/context

### D. COMPARISON TABLE (SMOTE vs GAN)
| Criterion | SMOTE | GAN |
|-----------|-------|-----|
| **Methodology** | Interpolation-based simple | Adversarial learning complex |
| **Training time** | Fast | Slow (convergence sensitive) |
| **Data type** | Low-dimensional tabular | High-dimensional, unstructured |
| **Sample quality** | Can introduce noise | More realistic (if trained well) |
| **Implementation** | Easy | Complex (hyperparameter tuning) |
| **Mode collapse** | N/A | Risk |
| **Computational cost** | Low | High |
| **Interpretability** | High | Low |

### E. EVALUATION METRICS
- **AUC-ROC** (independent of threshold)
- **MAUC** (M-measure — multi-class extension)
- **DID** (Discreteness-based Imbalanced Degree)
- **G-mean** (geometric mean of TPR × TNR)
- **Extended G-mean** (multi-class generalization)
- **MCC** (Matthew's Correlation Coefficient)
- **IMCP** (Imbalanced Multi-class Classification Performance)

### F. FUTURE DIRECTIONS
1. Scalability and large-scale datasets
2. Impact of data quality (noise resilience)
3. Integration with standard SMOTE variants in unified framework
4. Training stability and diversity in GANs
5. Comprehensive IMCP performance evaluation
6. Enhanced model validation in rarity conditions

### G. KẾT LUẬN
- No one-size-fits-all solution
- Domain-specific evaluation crucial
- SMOTE variants still competitive for tabular low-dim data
- GAN variants better for multi-modal, high-dim, unstructured data
- Hybrid approaches (SMOTE + GAN) under-explored

### H. NHẬN XÉT CÁ NHÂN
- **⭐⭐⭐⭐ (4/5):** Review gần đây nhất (2025), taxonomy class imbalance rất chi tiết. So sánh SMOTE vs GAN có hệ thống. 61 papers được chọn lọc kỹ.
- **Điểm mạnh:** Unified taxonomy, detailed comparison table SMOTE vs GAN, coverage of latest SMOTE variants (85+), domain-specific insights, future directions very practical
- **Điểm yếu:** Thiếu empirical benchmarking riêng, multi-class imbalance coverage còn hạn chế, một số GAN variants thiếu implementation detail
- **Liên quan đến SQLi:** SMOTE + GAN comparison rất relevant cho SQLi dataset augmentation decision. Classification of imbalance types giúp xác định nature of SQLi imbalance.

---

## BÀI BÁO 7: Enhancing Network Intrusion Detection Performance using Generative Adversarial Networks
**Tệp:** `C:\Projects\GAN_SQLi\Skill\output_txt\Enhancing Network Intrusion Detection Performance using Generative.txt`

### A. THÔNG TIN CƠ BẢN
- **Tác giả:** Xinxing Zhao, Kar Wai Fok, Vrizlynn L.L. Thing (ST Engineering, Singapore)
- **Năm:** 2024 (preprint)
- **Loại:** Research Article
- **Công ty:** ST Engineering
- **DOI:** (arXiv) — từ DOI 10.36227/techrxiv.171345670.08042024/c
- **Lĩnh vực:** Network Intrusion Detection, GAN-based Data Augmentation
- **Vấn đề:** Data scarcity in NIDS training datasets — CIC-IDS2017 Botnet class

### B. PHÂN LOẠI GAN
- **Các GAN models:**
  - **Vanilla GAN** (binary cross-entropy loss)
  - **WGAN** (Wasserstein distance / Earth-Mover's distance)
  - **CTGAN** (Conditional Tabular GAN with WGAN-GP principle + MMD)
- **Họ kiến trúc:** Fully connected (MLP) — Generator + Discriminator
- **Hàm mất mát:** Cross-entropy (Vanilla), Wasserstein distance (WGAN), MMD + WGAN-GP (CTGAN)
- **Kiểu tác vụ:** Oversampling Botnet attack class trong multi-class NIDS

### C. QUY TRÌNH DỮ LIỆU
- **Nguồn:** CIC-IDS2017 — multi-class network traffic dataset
- **Processing:**
  - Drop NaN/Null/Inf values
  - Group 15 original classes thành 8 general classes (Benign, DoS, Probe, DDoS, Brute Force, Web Attack, Botnet, Infiltration)
  - Chi-squared feature selection (top 32 features)
- **Phân phối (sau grouping):**
  - Benign: 2,271,320 | DoS: 251,723 | Probe: 158,804 | DDoS: 128,025
  - Brute Force: 13,832 | Web Attack: 2,180 | **Botnet: 1,956** | Infiltration: 36
- **Chia tập:** 80-20 train-test

### D. KIẾN TRÚC CHI TIẾT

**Vanilla GAN:**
- Generator: 3 FC layers (25→50→features_dim), ReLU, He uniform init, sigmoid output
- Discriminator: 3 FC layers (50→100→1), ReLU, sigmoid output

**WGAN:**
- Same architecture as Vanilla GAN, Wasserstein distance loss
- Weight clipping để enforce Lipschitz constraint

**CTGAN:**
- Generator: Input layer → 3 hidden layers (dim → dim*2 → dim*4 → output_dim), ReLU, label concatenation với noise
- Discriminator: Input (data + label concatenation) → dim*4 → dim*2 → dim → 1 neuron sigmoid, dropout 0.1
- Loss: Generator dùng MMD, Discriminator dùng WGAN-GP

### E. HUẤN LUYỆN
- **Original Botnet processing:**
  - Chia Botnet samples thành 2 primary groups dựa trên destination port (8080 vs non-8080)
  - Further divide thành smaller segments dựa trên column value patterns (columns with 2-3 distinct values)
  - Generate proportionally based on these segments
- **Closeness evaluation (3 methods):**
  1. Cosine similarity (8 representative features)
  2. Cumulative sums visualization
  3. ML validation (RF and DT classifiers on GAN-generated + Benign data)
- **Augmentation ratios:** 4×, 49×, 99× the original 1,956 Botnet samples

### F. KẾT QUẢ CLOSENESS EVALUATION
- **Cosine similarity (trung bình 8 features):**
  - Vanilla GAN: 0.9082
  - WGAN: 0.9073
  - CTGAN: 0.8221
- **Cumulative sums:** Vanilla GAN và WGAN gần khớp với original; CTGAN lệch đáng kể
- **ML validation:** RF trained on GAN-generated data đạt precision 1.00, recall 0.92-0.96 trên test set

### G. KẾT QUẢ IDS ENHANCEMENT (QUAN TRỌNG NHẤT)

**Classification performance on Generated Botnet samples:**
| Model (multiplier) | Precision | Recall | F1 |
|-------------------|-----------|--------|----|
| WGAN (4×) | 0.97 | 1.00 | 0.98 |
| WGAN (49×) | 1.00 | 1.00 | 1.00 |
| WGAN (99×) | 1.00 | 1.00 | 1.00 |
| Vanilla (4×) | 0.98 | 0.99 | 0.98 |
| Vanilla (49×) | 1.00 | 1.00 | 1.00 |
| Vanilla (99×) | 1.00 | 1.00 | 1.00 |
| CTGAN (4×) | 0.99 | 0.68 | 0.81 |
| CTGAN (49×) | 0.97 | 0.92 | 0.95 |
| CTGAN (99×) | 0.95 | 0.99 | 0.97 |

**Trained IDS performance on ORIGINAL 1,956 Botnet samples (critical metric):**
| Model (multiplier) | Precision | Recall | F1 | so với baseline (0.87/0.46/0.60) |
|-------------------|-----------|--------|----|------|
| WGAN (4×) | 1.00 | 0.74 | 0.85 | +0.13/+0.28/+0.25 |
| WGAN (49×) | 1.00 | 0.76 | 0.87 | +0.13/+0.30/+0.27 |
| WGAN (99×) | 1.00 | 0.82 | 0.90 | +0.13/+0.36/+0.30 |
| Vanilla (4×) | 1.00 | 0.66 | 0.80 | +0.13/+0.20/+0.20 |
| Vanilla (49×) | 1.00 | 0.76 | 0.87 | +0.13/+0.30/+0.27 |
| Vanilla (99×) | 1.00 | 0.81 | 0.90 | +0.13/+0.35/+0.30 |
| CTGAN (4×) | 1.00 | 0.43 | 0.60 | +0.13/-0.03/0 |
| CTGAN (49×) | 1.00 | 0.76 | 0.86 | +0.13/+0.30/+0.26 |
| CTGAN (99×) | 1.00 | 0.77 | 0.87 | +0.13/+0.31/+0.27 |

**Key findings:**
- **4× augmentation yields biggest improvement** (diminishing returns after 49×)
- **WGAN và Vanilla GAN outperform CTGAN** trên homogeneous data segments
- **CTGAN performance scales more with data volume** (4× kém, 49× ngang bằng, 99× gần bằng)
- **Other classes unaffected** — performance on non-Botnet classes remains stable
- **So sánh với literature:** Kết quả outperform Keserwani et al. (P=1.00, R=0.60, F1=0.75), Lee et al. (P=0.86, R=0.53, F1=0.66)

### H. KẾT LUẬN
- GAN-augmented NIDS significantly outperform standalone NIDS
- WGAN và Vanilla GAN better for homogeneous tabular segments
- ROC analysis unreachable due to RF probabilistic output limitations
- Research establishes new benchmark on CIC-IDS2017 Botnet classification (P=1.00, R=0.82, F1=0.90)

### I. NHẬN XÉT CÁ NHÂN
- **⭐⭐⭐⭐ (4/5):** Nghiên cứu empirical xuất sắc với methodology rõ ràng. Đo lường closeness đa chiều (cosine, cumulative sums, ML validation). Phân tích diminishing returns.
- **Điểm mạnh:** 3 GAN models applied systematically, closeness evaluation (3 methods), scalability analysis (4×/49×/99×), so sánh với SOTA literature, phát hiện WGAN ≈ Vanilla > CTGAN cho homogeneous data
- **Điểm yếu:** Chỉ focus vào Botnet class, Infiltration bỏ qua (quá ít samples), synthetic data quality evaluation có thể cần thêm metrics (privacy, diversity).
- **Liên quan đến SQLi:** TRỰC TIẾP APPLICABLE — cùng bài toán class imbalance trong IDS với tabular data. Phát hiện WGAN ≈ Vanilla > CTGAN rất relevant. Cần kiểm tra diminishing returns để chọn augmentation ratio optimal.

---

## BÀI BÁO 8: Enhancing Sequence Modeling: Leveraging GANs with Reinforcement Learning
**Tệp:** `C:\Projects\GAN_SQLi\Skill\output_txt\Enhancing Sequence Modeling_ Leveraging GANs with Reinforcement L.txt`

### A. THÔNG TIN CƠ BẢN
- **Tác giả:** Heather Pearson
- **Năm:** 2024 (16 Apr 2024)
- **Loại:** Technical Disclosure / Defensive Publication
- **Hội thảo/Tạp chí:** Technical Disclosure Commons (dpubs_series/6883)
- **Lĩnh vực:** Sequence Modeling, NLP, Reinforcement Learning
- **Vấn đề:** Gần như giống hệt Bài báo 1 (Janet Rodriguez) — SeqGAN improvements

### B-E. GIỐNG BÀI BÁO 1
Nội dung từ Sections I-VI gần như identical với Bài báo 1:
- SeqGAN architecture (LSTM generator + CNN discriminator + MC search + REINFORCE)
- WGAN và Improved WGAN
- PPO
- Batch size increase
- Synthetic data experiment với oracle LSTM
- Kết quả NLL (giống hệt: SeqGAN 8.639, Improved WGAN 8.509, etc.)

### F. KHÁC BIỆT CHÍNH
- **Tác giả khác:** Heather Pearson (vs. Janet Rodriguez)
- **Email:** "stevenanderson@yahoo.com" (không match author name)
- **Nội dung engineering:** References [16]-[24] từ cùng một nhóm tác giả (Sitao Luan et al.) giống hệt
- **Template text:** "Smith, Bowers and Wallace, stevenanderson@yahoo.com, Geologist, engineering" — lỗi template
- **Thời gian:** 16 Apr 2024 (1 ngày sau Bài báo 1)

### G. NGHI VẤN
- **Near-duplicate publication** — khác tác giả và email nhưng nội dung identical
- Technical Disclosure Commons có thể chấp nhận nhiều defensive publications tương tự
- Có thể là test/template submission hoặc duplicate từ cùng một source paper gốc
- References [16]-[24] bổ sung graph neural network papers không liên quan đến nội dung chính

### H. NHẬN XÉT CÁ NHÂN
- **⭐ (2/5):** Near-duplicate của Bài báo 1. Cùng nội dung SeqGAN improvements, synthetic data experiment, results. Không có contribution mới.
- **Điểm yếu:** Identical content, suspect author metadata, irrelevant extra references. Không nên sử dụng như một paper riêng biệt.
- **Liên quan đến SQLi:** Tương tự Bài báo 1 — SeqGAN framework có thể áp dụng cho SQL query generation.

---

## TỔNG HỢP XẾP HẠNG

| Bài báo | Rating | Lý do |
|---------|--------|-------|
| Bài 5 (Agrawal 2024) | ⭐⭐⭐⭐ | Critical analysis xuất sắc, phát hiện noise problem |
| Bài 7 (Zhao et al.) | ⭐⭐⭐⭐ | Empirical methodology tốt, closeness evaluation, diminishing returns analysis |
| Bài 6 (Udu et al. 2025) | ⭐⭐⭐⭐ | Unified taxonomy, SMOTE vs GAN comparison, comprehensive review |
| Bài 3 (Hà Thị Minh Phương) | ⭐⭐⭐ | Systematic empirical study, nhiều combinations |
| Bài 4 (Khoirunnisa 2025) | ⭐⭐⭐ | Clean comparison SMOTE vs CTGAN vs Hybrid |
| Bài 2 (Strelcenia 2023) | ⭐⭐⭐ | Survey toàn diện financial fraud GANs |
| Bài 1 (Rodriguez 2024) | ⭐⭐ | Defensive publication, synthetic data only |
| Bài 8 (Pearson 2024) | ⭐⭐ | Near-duplicate của Bài 1 |
