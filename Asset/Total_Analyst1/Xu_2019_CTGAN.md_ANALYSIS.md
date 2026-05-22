# Phân Tích Chuyên Sâu: Modeling Tabular Data using Conditional GAN (CTGAN)

---

## 3-Tier Explanation

| Cấp độ | Giải thích |
|--------|------------|
| **ELI5 (Dễ hiểu nhất)** | Hãy tưởng tượng bạn có một tập hợp các tờ biểu mẫu thông tin khách hàng rất phức tạp. Có những ô điền số (như thu nhập) biến động rất kỳ lạ, và có những ô chọn (như nghề nghiệp) mà một vài nghề rất hiếm gặp. CTGAN giống như một "robot sao chép" thông minh: nó không chỉ học cách điền các con số sao cho giống thật nhất mà còn biết tập trung học kỹ các "nghề hiếm" để không bao giờ bỏ sót chúng khi tạo ra biểu mẫu mới. |
| **Technical (Kỹ thuật)** | CTGAN là một khung làm việc GAN được thiết kế riêng cho dữ liệu bảng (tabular data) không đồng nhất. Nó giải quyết hai vấn đề cốt lõi: (1) Các cột liên tục đa phương thức (multi-modal) thông qua cơ chế Mode-specific Normalization (sử dụng Variational Gaussian Mixture) và (2) Sự mất cân bằng nghiêm trọng trong các cột phân loại thông qua Conditional Generator kết hợp với chiến lược Training-by-sampling dựa trên log-frequency. |
| **Researcher (Nghiên cứu)** | Bài báo giải quyết các thách thức của phân phối không phải dạng Gaussian và thưa thớt của vector one-hot trong tổng hợp dữ liệu bảng. CTGAN sử dụng mạng fully-connected với PacGAN để chống mode collapse. Đóng góp chính bao gồm việc chuẩn hóa dữ liệu dựa trên chế độ (mode) để biểu diễn các cột liên tục và một hàm loss bổ sung (cross-entropy penalty) để đảm bảo Generator tuân thủ các điều kiện (conditions) được đưa vào, tối ưu hóa khả năng học các lớp thiểu số (minority classes). |

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | Modeling Tabular Data using Conditional GAN |
| **Tác giả** | Lei Xu, Maria Skoularidou, Alfredo Cuesta-Infante, Kalyan Veeramachaneni |
| **Năm** | 2019 |
| **Conference / Journal** | NeurIPS 2019 |
| **Link** | https://arxiv.org/abs/1907.00503 |

### A1. Phân Loại GAN Taxonomy

| Thuộc tính | Lựa chọn |
|------------|----------|
| **GAN Type** | Conditional / Wasserstein (WGAN-GP) |
| **Architecture Family** | MLP (Fully-connected) |
| **Divergence** | Wasserstein |
| **Task Type** | Tabular Data Generation / Data Augmentation |

---

## Phần B: Dữ Liệu — Data Pipeline Deep-Dive

### B1. Dataset Overview
Sử dụng benchmark **SDGym** gồm:
- 7 tập dữ liệu mô phỏng (Gaussian Mixture, Bayesian Networks).
- 8 tập dữ liệu thực (Adult, Census, Covertype, Credit, Intrusion, News, MNIST12, MNIST28).

### B2. Preprocessing Pipeline: Mode-Specific Normalization
Đây là điểm sáng tạo nhất:
1. Sử dụng **Variational Gaussian Mixture (VGM)** để ước lượng số mode ($m_i$) cho mỗi cột liên tục.
2. Với mỗi giá trị, tính xác suất nó thuộc về từng mode.
3. Biểu diễn một giá trị liên tục thành: một vector one-hot chỉ định mode ($ \beta $) và một giá trị scalar đã chuẩn hóa ($ \alpha $) trong mode đó.

---

## Phần C: Kiến Trúc Mô Hình — Architecture Blueprint

### C1. Generator Architecture
- **Input**: Latent vector $z$ + Conditional vector $cond$.
- **Layers**: 2 tầng ẩn (256 units), sử dụng BatchNorm và ReLU.
- **Output Activation**: 
    - `tanh` cho giá trị scalar $\alpha$.
    - `Gumbel-Softmax` cho mode indicator $\beta$ và các cột rời rạc.

### C2. Critic Architecture
- **Input**: PacGAN (kích thước 10 mẫu cùng lúc) để chống mode collapse.
- **Layers**: 2 tầng ẩn (256 units), sử dụng LeakyReLU và Dropout (0.5).
- **Loss**: WGAN-GP (Gradient Penalty).

---

## Phần D: Training Configuration

| Thông số | Giá trị |
|----------|---------|
| **Optimizer** | Adam |
| **Learning Rate** | 2e-4 |
| **Batch Size** | 500 |
| **Epochs** | 300 |
| **PacGAN Size** | 10 |

---

## Phần E: So Sánh Với Baselines — Beyond Baselines

CTGAN được so sánh với:
- **Bayesian Networks**: CLBN, PrivBN.
- **Deep Learning**: MedGAN, VeeGAN, TableGAN.
- **Kết quả**: CTGAN vượt trội hơn các phương pháp Bayesian trên hầu hết các bộ dữ liệu thực tế về độ chính xác của bộ phân loại (Machine Learning efficacy).

---

## Phần F: Ablation & Experiments — Surgical Analysis

**Các câu hỏi nghiên cứu (RQ):**
- **RQ1**: Mode-specific normalization có thực sự tốt hơn Min-Max? (Kết quả: Tăng hiệu suất đáng kể, Min-Max làm giảm 25.7%).
- **RQ2**: Conditional Generator và Training-by-sampling có giúp xử lý dữ liệu mất cân bằng? (Kết quả: Loại bỏ chúng làm giảm 36.5% hiệu suất trên tập dữ liệu mất cân bằng).

---

## Phần G: Training Stability & Mode Collapse

- **PacGAN**: Sử dụng 10 mẫu trong Critic giúp tăng tính ổn định và giảm Mode Collapse.
- **Training-by-sampling**: Thay vì lấy mẫu ngẫu nhiên, hệ thống lấy mẫu theo log-frequency của các phạm vi giá trị để Generator "thấy" các lớp thiểu số thường xuyên hơn.

---

## Phần H: Kết Quả & Đánh Giá

- **Định lượng**: Trên tập dữ liệu `credit` (cực kỳ mất cân bằng), CTGAN đạt F1 cao vượt trội so với các GAN khác.
- **TVAE**: Một biến thể VAE được giới thiệu trong bài cũng cho kết quả rất tốt, đôi khi thắng CTGAN, nhưng GAN được ưu tiên hơn khi cần tính riêng tư (Differential Privacy).

---

## Phần I: Đánh Giá Cá Nhân

- **Điểm Mạnh**: Giải quyết triệt để vấn đề phân phối đa mode trong dữ liệu bảng. Cung cấp bộ benchmark SDGym giá trị cho cộng đồng.
- **Điểm Yếu**: Kiến trúc MLP có thể chưa tối ưu cho các bảng có sự phụ thuộc cấu trúc phức tạp (như chuỗi thời gian).
- **Actionable Insight**: Cơ chế **Mode-specific normalization** cực kỳ hữu ích cho việc tiền xử lý dữ liệu SQL Injection trước khi đưa vào mô hình học máy.

---

## Misconception Seeds

1. **Lầm tưởng**: GAN chỉ hiệu quả cho hình ảnh và âm thanh.
   - **Thực tế**: CTGAN chứng minh rằng với cơ chế chuẩn hóa đúng đắn, GAN có thể mô hình hóa dữ liệu bảng tốt hơn cả các mạng Bayes truyền thống.
2. **Lầm tưởng**: Chỉ cần Min-Max normalization là đủ cho dữ liệu số.
   - **Thực tế**: Dữ liệu thực tế thường đa mode (multi-modal). Việc ép chúng vào khoảng [-1, 1] mà không quan tâm đến mode sẽ làm mất thông tin cấu trúc phân phối.

---

## Transfer Question

**Ứng dụng vào SQL Injection:**
Làm thế nào để áp dụng cơ chế **Mode-specific normalization** của CTGAN để biểu diễn các đặc trưng như "độ dài câu truy vấn" hoặc "số lượng từ khóa SQL" trong các cuộc tấn công SQLi, vốn thường có phân phối đa mode (ví dụ: các câu truy vấn bình thường thì ngắn, nhưng các câu truy vấn tấn công Union-based thì rất dài)?

---

## Bổ Sung Của Codex — Kiểm Tra Lại Theo Total_OCR1 (2026-05-22)

> Phần này được append thêm vào cuối file theo yêu cầu, không xóa hoặc sửa nội dung analysis gốc của đồng nghiệp.  
> Nguồn kiểm tra bổ sung: `Asset/Total_OCR1/Xu_2019_CTGAN.md`.  
> Workflow tham chiếu: `transcript-analysis` — Scientific Paper Hybrid Framework A-I.

### 1. Quan điểm bổ sung
Tài liệu liên quan đến GAN/sequence generation. Cần phân biệt rõ kỹ thuật ổn định huấn luyện với bằng chứng nó thắng MLE trong bài toán SQLi.

Các tín hiệu kỹ thuật nổi bật đọc được từ OCR hiện tại:

- gradient penalty / Lipschitz constraint
- Gumbel-Softmax / categorical relaxation
- Generator-Discriminator adversarial loop

### 2. Phản biện và rủi ro diễn giải
- Không nên dùng paper này để biện minh trực tiếp cho việc mở lại GAN nếu paper không giải quyết rõ cơ chế **D saturation**, **mode collapse**, **syntax validity** và **seed variance** trong bài toán discrete sequence.
- Nếu paper báo cáo metric downstream tốt nhưng không có kiểm tra novelty/diversity/syntax, thì trong GAN_SQLi nó chỉ là bằng chứng phụ.
- Khi paper thuộc domain IDS/tabular/fraud, cần ghi rõ khác biệt với SQLi payload: dữ liệu bảng thường không có ràng buộc ngữ pháp và relex như payload SQL.
- Không phát hiện ghi chú provenance nghiêm trọng riêng cho file này trong bước crosscheck.

### 3. Áp dụng thực tế cho pipeline GAN_SQLi
- Ưu tiên rút ra cơ chế có thể kiểm chứng bằng evaluator độc lập, không chỉ dùng làm khẩu hiệu kiến trúc.
- Nếu cơ chế liên quan augmentation hoặc GAN, nên thử trước trên vertical slice và so với **Conditional MLE + evaluator-guided search**.
- Nếu cơ chế liên quan data/label/tokenization, nên đưa vào Phase 04/05/06 trước khi động tới adversarial training.

### 4. Trích yếu OCR để đối chiếu nhanh
> Modeling the probability distribution of rows in tabular data and generating realistic synthetic data is a non-trivial task. Tabular data usually contains a mix of discrete and continuous columns. Continuous columns may have multiple modes whereas discrete columns are sometimes imbalanced making the modeling difﬁcult. Existing statistical and deep neural network models fail to properly model this type of data. We design CTGAN, which uses a conditional generator to address these challenges. To aid in a fair and thorough comparison, we design a benchmark with 7 simulated and 8 real datasets and several Bayesian network baselines. CTGAN outperforms Bayesian methods on most of the real datasets whereas other deep learning methods could not.

### 5. Quyết định sử dụng
- **Dùng được cho**: related work, thiết kế ablation, hoặc lập luận phụ tùy theo nhóm paper.
- **Chưa đủ cho**: kết luận rằng GAN sẽ thắng MLE trên SQLi nếu không có thực nghiệm nội bộ và decision gate mới.
