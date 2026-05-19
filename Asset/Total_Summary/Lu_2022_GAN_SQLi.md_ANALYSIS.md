# Phân Tích Bài Báo Khoa Học: A GAN-based Method for Generating SQL Injection Attack Samples

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | A GAN-based Method for Generating SQL Injection Attack Samples |
| **Tác giả** | Dongzhe Lu, Jinlong Fei, Long Liu, Zecun Li |
| **Năm** | 2022 |
| **Conference / Journal** | IEEE 10th Joint International Information Technology and Artificial Intelligence Conference (ITAIC) |
| **Link** | https://doi.org/10.1109/ITAIC54216.2022.9836726 |

### A1. Phân Loại GAN Taxonomy

| Thuộc tính | Lựa chọn |
|------------|----------|
| **GAN Type** | Wasserstein GAN (WGAN) / DCGAN |
| **Architecture Family** | CNN-based (DCGAN) |
| **Divergence** | Wasserstein Distance (W-distance) |
| **Task Type** | Sequence Generation / Data Augmentation |

### A2. Code Availability

| Mục | Thông tin |
|-----|-----------|
| **Official code** | Không đề cập (Sử dụng Keras/Python) |
| **URL** | N/A |
| **Framework** | Keras 2.2.4 |
| **Dependencies** | Python 3.6, Conda 4.11.0, SQLParse, Keras |

---

## Phần B: Dữ Liệu — Data Pipeline Deep-Dive

### B1. Dataset Overview

| Thuộc tính | Mô tả |
|------------|-------|
| **Tên dataset** | Custom SQLi Payload Dataset |
| **Nguồn** | CVE, CNVD, exploit-db (2015 - nay) |
| **Kích thước** | > 2,000 payloads sau khi làm sạch |
| **Domain** | Web Security / SQL Injection |
| **Public / Private** | Private (Custom crawled) |

### B2. Data Characteristics

| Đặc điểm | Mô tả |
|----------|-------|
| **Data type** | Text (SQL Payloads) |
| **Input dimensions** | Không nêu cụ thể độ dài vector |
| **Class distribution** | Tập trung vào SQLi (Boolean-blind, Time-blind, Union-based, Error-based) |

### B3. Preprocessing Pipeline

| Bước | Chi tiết | Công cụ / Library |
|------|----------|-------------------|
| **Tokenization** | SQL keywords/tokens granularity | SQLParse |
| **Normalization** | Scaling data về khoảng [-1, 1] cho Tanh | Custom script |
| **Encoding** | Decoding & Generalization (Library/Table/Column names) | Custom script |
| **Filtering** | Loại bỏ các payload trùng lặp hoặc tương tự về mặt logic | Custom script |

---

## Phần C: Kiến Trúc Mô Hình — Architecture Blueprint

### C1. Tổng Quan Kiến Trúc
Mô hình kết hợp **Genetic Algorithm (GA)** để khởi tạo và tiến hóa quần thể các câu lệnh SQL sơ khai, sau đó dùng **DCGAN** để sinh ra các biến thể phức tạp hơn.

```
Noise/Genes → GA (Selection/Crossover/Mutation) → Initial Population 
     ↓
DCGAN Generator → Synthetic Payloads → Variational Operators (Tamper) → Final Samples
     ↓
DCGAN Discriminator (W-Distance)
```

### C2. Generator & Discriminator Architecture (DCGAN)
- **Generator**: 4 lớp ẩn, sử dụng ReLU cho các lớp trung gian và Tanh cho lớp đầu ra. Loại bỏ Pooling, thay bằng Deconvolution.
- **Discriminator**: 4 lớp ẩn, sử dụng LeakyReLU cho tất cả các lớp, đầu ra Sigmoid. Sử dụng Convolution thay vì Pooling.

---

## Phần D: Training Configuration

| Hyperparameter | Giá trị |
|---------------|---------|
| **Optimizer** | Adam (Learning rate: 0.0002, Momentum: 0.5) |
| **Batch size** | 500 |
| **Epochs** | 300 |
| **Loss function** | Wasserstein Distance (W-loss) |
| **Activation** | LeakyReLU (slope 0.2), Tanh, Sigmoid |

---

## Phần E: So Sánh Với Baselines — Beyond Baselines

### E1. "X-Factor" — Innovation Chính
Sự kết hợp giữa **Genetic Algorithm (GA)** và **WGAN**. GA đảm bảo cấu trúc cú pháp SQL cơ bản (thông qua SQLParse evaluation), trong khi WGAN học phân phối đặc trưng để sinh ra các mẫu đa dạng và tránh lỗi "mode collapse" nhờ W-distance.

---

## Phần F: Ablation & Experiments — Surgical Analysis

Bài báo thực hiện thử nghiệm thay đổi hyperparameter (LeakyReLU slope, batch size, learning rate) để chứng minh cấu hình tối ưu.
- Kết quả: Batch size 500 và Adam LR 0.0002 cho độ hội tụ nhanh và ổn định nhất.

---

## Phần G: Stability & Mode Collapse

| Technique | Status |
|-----------|--------|
| **Wasserstein Distance** | Sử dụng để thay thế KL/JS divergence, giải quyết triệt để mode collapse. |
| **Batch Normalization** | Áp dụng cho cả G và D. |

---

## Phần H: Kết Quả & Đánh Giá

### H1. Quantitative Results
Thử nghiệm trên môi trường **sqli-lab** và **SafeDog V4.0** (WAF):
- Thành công trên hầu hết các loại injection (Error-based, Integer-based, Boolean-blind, Header Injection).
- Thất bại trên: `Dump into outfile` và `Second Degree Injections`.

---

## Phần I: Đánh Giá Cá Nhân

- **Điểm Mạnh**: Kết hợp GA để giải quyết vấn đề cú pháp SQL (một điểm yếu kinh điển của GAN truyền thống khi sinh văn bản có cấu trúc cứng). Sử dụng W-distance giúp quá trình huấn luyện ổn định.
- **Điểm Yếu**: Độ mịn của gene trong GA còn hơi thô. Chưa so sánh hiệu quả cải thiện độ chính xác của các mô hình detection sau khi được augment bằng dữ liệu này.

---

## 3-Tier Explanation

### 1. Child (Analogy)
Hãy tưởng tượng bạn đang học viết những câu đố mẹo để vượt qua một người gác cổng thông thái. Đầu tiên, bạn lấy những từ ngữ rời rạc và ghép chúng lại theo cách có nghĩa (giống GA). Sau đó, bạn đưa chúng cho một "cỗ máy sáng tạo" (Generator) để biến hóa chúng thành hàng ngàn câu đố khác nhau nhưng vẫn giữ được "mẹo" đó. Một người bạn khác (Discriminator) sẽ đóng vai người gác cổng để kiểm tra xem câu đố của bạn có giống thật không.

### 2. Student (Mechanism)
Quy trình gồm 3 giai đoạn:
1. **Tiến hóa (GA)**: Khởi tạo các đoạn mã SQL từ tập gene (từ khóa SQL). Sử dụng `SQLParse` để chấm điểm cú pháp, chỉ giữ lại những cá thể có cấu trúc hợp lệ.
2. **Sinh mẫu (WGAN)**: Sử dụng DCGAN với hàm mất mát là khoảng cách Wasserstein để học phân phối của các payload thực. Việc này giúp sinh ra các mẫu có đặc trưng tương tự nhưng đa dạng hơn, tránh lặp lại mẫu cũ.
3. **Biến dị (Tamper Scripts)**: Áp dụng các kỹ thuật obfuscation (Base64, comment intrusion...) để vượt qua chữ ký của WAF.

### 3. Expert (Trade-offs)
Việc sử dụng GA như một bước tiền lọc (pre-filter) giúp thu hẹp không gian tìm kiếm của GAN, đảm bảo tính hợp lệ về mặt cú pháp — điều mà GAN thuần túy thường gặp khó khăn khi xử lý dữ liệu rời rạc (discrete data). Tuy nhiên, sự phụ thuộc vào các `tamper scripts` thủ công cho thấy GAN vẫn chưa hoàn toàn tự học được các kỹ thuật bypass phức tạp. Khoảng cách Wasserstein mang lại sự ổn định tuyệt vời, nhưng chi phí tính toán có thể cao hơn so với Vanilla GAN.

---

## Misconception Seeds
1. **Sai lầm**: GAN có thể tự học cú pháp SQL hoàn hảo chỉ từ nhiễu ngẫu nhiên.
   - **Thực tế**: SQL là ngôn ngữ có cấu trúc chặt chẽ; GAN thuần túy dễ sinh ra các chuỗi vô nghĩa. Bài báo này phải dùng GA và SQLParse để "ép" mô hình đi đúng hướng cú pháp.
2. **Sai lầm**: Càng nhiều mẫu sinh ra thì mô hình detection càng mạnh.
   - **Thực tế**: Nếu các mẫu sinh ra bị lặp (mode collapse), nó sẽ làm mô hình detection bị overfitting vào một vài kiểu tấn công nhất định.

---

## Transfer Question
Nếu bạn muốn áp dụng phương pháp này để sinh mã độc **XSS**, bạn sẽ cần thay đổi "tập gene" trong GA và "công cụ đánh giá cú pháp" như thế nào để phù hợp với ngữ cảnh trình duyệt?

---

## Phần D (bổ sung): D5. Reproducibility Checklist

| Mục | Trạng thái |
|-----|-----------|
| Random seeds được fix | [ ] Không đề cập |
| Confidence intervals | [ ] Không có CI |
| Multiple runs | [ ] 1 run duy nhất |
| Hyperparameters đầy đủ | [x] Adam lr=0.0002, batch=500, epochs=300 |
| Hardware specification | [x] Intel i7-9700, 24GB RAM, Windows 11 |
| Test environment | [x] sqli-lab + SafeDog WAF — nhưng version-specific |
| **Confidence rating** | ⭐⭐☆☆☆ — 1 seed, 1 WAF env, không có statistical test |

**Implication**: Kết quả bypass rate "6/8 injection types" chưa được validated trên multiple WAFs hay multiple runs.

---

## Phần F (bổ sung): F3. Statistical Rigor

| Mục | Trạng thái |
|-----|-----------|
| Random seeds | [ ] Không đề cập |
| p-value | [ ] Không có |
| Significance test | [ ] Không có |
| Cross-validation | [ ] Không có |
| WAF diversity | [ ] Chỉ test SafeDog V4.0 — không test ModSecurity, Cloudflare |
| **Statistical rigor rating** | ⭐☆☆☆☆ (chỉ 1 WAF, 1 environment, không CI) |

---

## Phần I (bổ sung): I3. Actionable Insights

| Idea | Source | Priority | Effort | How to Implement |
|------|--------|----------|--------|-----------------|
| SQLParse tokenization cho SQL-aware vocab | Paper Section 3.2 | **P0** | Đã có V5 | delex_v2 dùng SQLParse + function whitelist |
| 8 variational operators từ sqlmap | Paper Section 3.3 | P1 | Medium | WAF-A-MoLE integration: map Lu's 8 operators → Demetrio's 6 mutations |
| 4 SQLi type coverage (error/bool/time/union) | Paper dataset | **P0** | Đã có | V5 dataset: 4 types + db_engine labels |
| GA gene list (SQL keywords) | Paper Appendix | P2 | Low | Dùng làm reference cho delex_v2 whitelist expansion |
| W-distance thay KL | Paper Section 3.1 | **P0** | Đã có V4 | WGAN-GP discriminator (Gulrajani_2017) |

### I4. Research Gaps

| Gap | Mô tả | Potential Direction |
|-----|-------|---------------------|
| Không có sequence model (DCGAN only) | DCGAN không capture sequential structure của SQL | V5: LSTM/BiLSTM generator capture SQL token dependencies |
| GA không có RL feedback loop | GA mutation không được guided bởi reward signal | WAF-A-MoLE: score-guided mutation selection |
| SQLi type không được conditioned | Model sinh tất cả types bất kể condition | V5: conditional generation với attack_type + db_engine |
| Reproducibility thấp | 1 seed, 1 WAF | V5: 3 seeds, multiple WAFs (ModSecurity + SafeDog) |

### I5. Verdict

| Criteria | Rating | Notes |
|----------|--------|-------|
| **Technical soundness** | ⭐⭐⭐⭐☆ | DCGAN+GA combination là creative |
| **Novelty** | ⭐⭐⭐⭐☆ | First DCGAN+GA cho SQLi generation |
| **Reproducibility** | ⭐⭐☆☆☆ | 1 seed, 1 WAF, no CI |
| **Relevance to SQLi** | ⭐⭐⭐⭐⭐ | **Closest prior work** — same domain |
| **Overall quality** | ⭐⭐⭐⭐☆ | Strong domain contribution, weak stats |

**Summary**: Lu_2022 là paper **gần nhất với bài toán của V5** trong literature — cùng domain SQLi generation. Key contributions: DCGAN+GA combination, SQLParse tokenization, 8 variational operators. Key gaps: không có sequence model, không conditioned, reproducibility thấp. V5 giải quyết tất cả gaps này: BiLSTM (sequence), conditional, 3 seeds, multiple WAFs.

---

### H10. Thesis Section Mapping

| Thesis Section | Nội dung từ paper này |
|----------------|----------------------|
| 2.1 Literature Review | **Closest prior work** — cite là related work trực tiếp |
| 2.4 SQLi Dataset | "Lu et al. (2022) dùng 2,000 payloads từ CVE/CNVD/exploit-db" |
| 4.1 Data Pipeline | SQLParse tokenization → inspire delex_v2 function whitelist |
| 4.2 Comparison | V5 vs Lu_2022: sequence model, conditional, larger dataset |
| References | Lu et al. (2022), IEEE ITAIC |
