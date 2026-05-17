# Phân Tích Bài Báo Khoa Học: MaskGAN (Fedus et al., 2018)

---

## Core Question
**Làm thế nào để cải thiện chất lượng văn bản sinh ra từ mạng neural, vượt qua giới hạn của phương pháp Maximum Likelihood Estimation (MLE) vốn thường dẫn đến hiện tượng "exposure bias" và sự sai khác giữa mục tiêu tối ưu (perplexity) với chất lượng thực tế?**

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | MASKGAN: BETTER TEXT GENERATION VIA FILLING IN THE ____ |
| **Tác giả** | William Fedus, Ian Goodfellow, Andrew M. Dai |
| **Năm** | 2018 |
| **Conference / Journal** | ICLR 2018 |
| **Link** | https://arxiv.org/abs/1801.07736 |

### A1. Phân Loại GAN Taxonomy

| Thuộc tính | Lựa chọn |
|------------|----------|
| **GAN Type** | Actor-Critic Conditional GAN |
| **Architecture Family** | RNN-based (LSTM) + Attention |
| **Divergence** | Policy Gradient (Reinforcement Learning) |
| **Task Type** | Sequence Generation / Text In-filling |

### A2. Code Availability

| Mục | Thông tin |
|-----|-----------|
| **Official code** | Có |
| **URL** | https://github.com/tensorflow/models/tree/master/research/maskgan |
| **Framework** | TensorFlow |

---

## Phần B: Dữ Liệu — Data Pipeline Deep-Dive

### B1. Dataset Overview

| Thuộc tính | Mô tả |
|------------|-------|
| **Tên dataset** | Penn Treebank (PTB), IMDB Movie Reviews |
| **Nguồn** | Marcus et al. (1993), Maas et al. (2011) |
| **Kích thước** | PTB: 930k words train; IMDB: 100k reviews (~3M words) |
| **Domain** | News (PTB), Movie Reviews (IMDB) |

### B2. Data Characteristics

| Đặc điểm | Mô tả |
|----------|-------|
| **Data type** | Text |
| **Sequence length** | PTB: ~20 tokens; IMDB: ~40 tokens |
| **Vocabulary size** | PTB: 10,000; IMDB: (Không nêu cụ thể nhưng lớn hơn PTB) |

### B3. Preprocessing Pipeline

| Bước | Chi tiết |
|------|----------|
| **Tokenization** | Word-level |
| **Encoding** | Word Embedding (650 dims) |
| **Masking** | Thay thế một phần văn bản bằng token `<m>`. Tỷ lệ 0.5. |

---

## Phần C: Kiến Trúc Mô Hình — Architecture Blueprint

### C1. Tổng Quan Kiến Trúc
Mô hình sử dụng cấu trúc **seq2seq** với Attention mechanism. 
- **Encoder**: Đọc chuỗi đã bị che (masked sequence) để lấy ngữ cảnh.
- **Decoder**: Sinh các token bị thiếu một cách autoregressive.

### C2. Generator Architecture
- **Layer Stack**: 2 lớp LSTM, 650 hidden units.
- **Special Components**: Attention mechanism (Luong-style) để kết nối với Encoder.

### C3. Discriminator / Critic Architecture
- **Discriminator**: Có kiến trúc tương tự Generator nhưng đầu ra là xác suất scalar cho mỗi time step (rt).
- **Critic**: Một "đầu" (head) bổ sung từ Discriminator để ước lượng giá trị (Value function - bt).

---

## Phần D: Training Configuration

### D1. Optimizer & Learning Rate
- **Optimizer**: Adam (β1 = 0.99, β2 = 0.999).
- **Learning rate**: Được tinh chỉnh qua Bayesian hyperparameter tuning.

### D2. Training Loop
- **Pretraining**: 
    1. Huấn luyện Language Model (LM) chuẩn bằng MLE.
    2. Huấn luyện seq2seq trên task in-filling bằng MLE.
- **Adversarial Training**: Sử dụng Policy Gradient (REINFORCE) với Critic làm baseline để giảm variance.

### D4. Loss Function Details
- **Generator**: Maximize discounted total return R = Σ γ^s * r_s.
- **Discriminator**: Standard GAN binary cross-entropy loss tại mỗi time step.

---

## Phần E: So Sánh Với Baselines — Beyond Baselines

| Component | Paper's Version (MaskGAN) | Base Version (MLE) |
|-----------|---------------------------|--------------------|
| Training | GAN + RL (Policy Gradient) | Teacher Forcing (MLE) |
| Evaluation | Human Eval, n-gram diversity | Perplexity |

---

## Phần F: Ablation & Experiments — Surgical Analysis

### F2. Key Ablation Insight
- **Critic**: Việc thêm Critic giúp giảm variance của gradient xuống một bậc độ lớn (order of magnitude), giúp quá trình huấn luyện ổn định hơn.
- **Attention**: Rất quan trọng để Generator có thể điều kiện hóa (condition) dựa trên ngữ cảnh xung quanh các từ bị che.

---

## Phần G: Training Stability & Mode Collapse

### G1. Stability Techniques
- **Actor-Critic**: Sử dụng baseline (bt) để ổn định Policy Gradient.
- **Shared Embeddings**: Chia sẻ trọng số embedding giữa Generator và Discriminator để tăng tốc hội tụ.

### G3. Observed Issues
- **Boundary matching**: Khó khăn trong việc khớp ngữ pháp tại ranh giới giữa từ được sinh ra và từ gốc.

---

## Phần H: Kết Quả & Đánh Giá

### H1. Quantitative Results
- **Human Evaluation**: MaskGAN thắng MLE trên IMDB (58% vs 40% overall quality). Trên PTB, MaskGAN cũng vượt trội hơn SeqGAN.
- **Perplexity**: MaskGAN có perplexity cao hơn (tệ hơn) trên tập test so với MLE, nhưng chất lượng mẫu thực tế lại tốt hơn.

---

## Phần I: Đánh Giá Cá Nhân

### I1. Điểm Mạnh
- Giải quyết trực tiếp vấn đề **Objective Mismatch** và **Exposure Bias**.
- Task **In-filling** cung cấp tín hiệu reward dày đặc (dense reward) giúp credit assignment tốt hơn.

### I5. Verdict
⭐ ⭐ ⭐ ⭐ (4/5) - Một bước tiến quan trọng trong việc ứng dụng GAN cho văn bản, dù vẫn còn thách thức về độ ổn định.

---

## 3-Tier Explanation

### 1. Cấp độ Đứa trẻ (Child)
Hãy tưởng tượng bạn đang chơi trò "điền vào chỗ trống". Bình thường bạn học bằng cách đọc sách và cố gắng đoán từ tiếp theo. Nhưng đôi khi bạn đoán sai, và vì không có ai sửa ngay lúc đó, bạn cứ thế đoán sai tiếp cả câu. **MaskGAN** giống như có một người giám khảo khó tính ngồi cạnh. Người đó không chỉ nhìn vào từng từ bạn điền, mà còn xem cả câu có "giống người thật nói" hay không. Nhờ đó, bạn học được cách điền từ sao cho tự nhiên nhất.

### 2. Cấp độ Sinh viên (Student)
Trong huấn luyện ngôn ngữ truyền thống (MLE), chúng ta dùng **Teacher Forcing**. Tuy nhiên, khi sinh văn bản thực tế (Inference), mô hình phải tự dựa vào các từ nó vừa sinh ra (có thể sai) để dự đoán tiếp, gây ra **Exposure Bias**. **MaskGAN** giải quyết việc này bằng cách đưa vào cơ chế **GAN**. Generator cố gắng điền vào các từ bị thiếu (In-filling), trong khi Discriminator đánh giá độ thực của từng từ dựa trên ngữ cảnh. Vì văn bản là dữ liệu rời rạc (discrete), chúng ta không thể dùng backpropagation thông thường mà phải dùng **Reinforcement Learning** (Policy Gradient) kết hợp với **Actor-Critic** để giảm phương sai (variance).

### 3. Cấp độ Chuyên gia (Expert)
**MaskGAN** tối ưu hóa hàm mục tiêu văn bản thông qua khung tham chiếu **Actor-Critic Conditional GAN**. Khác với các mô hình GAN cho văn bản trước đó (như SeqGAN) thường chỉ có reward sau khi kết thúc chuỗi, MaskGAN tận dụng task **In-filling** để cung cấp **dense rewards** tại mỗi time step. Kiến trúc này sử dụng một Encoder để nắm bắt ngữ cảnh tương lai (future context) và Decoder để sinh token autoregressively. Để vượt qua rào cản tính không khả vi (non-differentiability) của các token rời rạc, mô hình áp dụng thuật toán **REINFORCE** với một **learned baseline (Critic)**. Điều này giúp giảm thiểu đáng kể variance trong ước lượng gradient, cho phép mô hình hội tụ tốt hơn trong không gian hành động (action space) cực lớn của từ vựng tự nhiên.

---

## Misconception Seeds
1. **Lầm tưởng**: Perplexity càng thấp thì văn bản sinh ra càng hay.
   - **Sự thật**: Bài báo chỉ ra rằng mô hình có perplexity cao (như MaskGAN) vẫn có thể tạo ra văn bản chất lượng cao hơn và tự nhiên hơn so với mô hình có perplexity thấp (MLE).
2. **Lầm tưởng**: GAN cho văn bản chỉ cần Discriminator chấm điểm cuối câu.
   - **Sự thật**: Việc chỉ chấm điểm cuối câu dẫn đến vấn đề credit assignment khó khăn. MaskGAN chứng minh reward tại mỗi time step hiệu quả hơn.

---

## Transfer Question
**Làm thế nào để áp dụng cơ chế "In-filling" của MaskGAN vào việc phát hiện các câu truy vấn SQL Injection (SQLi) bị biến đổi (obfuscated), nơi mà kẻ tấn công thường chèn thêm các từ khóa hoặc ký tự lạ vào giữa các câu lệnh hợp lệ?**
