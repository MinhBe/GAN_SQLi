# Phân Tích Bài Báo Khoa Học: CodeBERT (Feng et al., 2020)

---

## Core Question
**Làm thế nào để học được biểu diễn (representation) tổng quát kết hợp giữa ngôn ngữ tự nhiên (NL) và ngôn ngữ lập trình (PL) nhằm hỗ trợ hiệu quả cho các tác vụ hiểu và sinh mã nguồn, đồng thời tận dụng được cả dữ liệu song ngữ (bimodal) và đơn ngữ (unimodal)?**

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | CodeBERT: A Pre-Trained Model for Programming and Natural Languages |
| **Tác giả** | Zhangyin Feng, Daya Guo, Duyu Tang, Nan Duan, et al. |
| **Năm** | 2020 |
| **Conference / Journal** | arXiv (Microsoft Research Asia & Harbin Institute of Technology) |
| **Link** | https://arxiv.org/abs/2002.08155 |

### A1. Phân Loại GAN Taxonomy

| Thuộc tính | Lựa chọn |
|------------|----------|
| **Architecture Family** | Transformer-based (RoBERTa architecture) |
| **Task Type** | Pre-trained Model for NL-PL (Understanding & Generation) |
| **Learning Objective** | Masked Language Modeling (MLM) + Replaced Token Detection (RTD) |

### A2. Code Availability

| Mục | Thông tin |
|-----|-----------|
| **Official code** | Có |
| **URL** | https://github.com/microsoft/CodeBERT |
| **Framework** | PyTorch |

---

## Phần B: Dữ Liệu — Data Pipeline Deep-Dive

### B1. Dataset Overview

| Thuộc tính | Mô tả |
|------------|-------|
| **Tên dataset** | CodeSearchNet (Husain et al., 2019) |
| **Nguồn** | GitHub (Open-source repositories) |
| **Quy mô** | 2.1M bimodal NL-PL pairs; 6.4M unimodal PL codes |
| **Lập trình** | 6 ngôn ngữ: Python, Java, JavaScript, PHP, Ruby, Go |

### B2. Data Characteristics

| Đặc điểm | Mô tả |
|----------|-------|
| **Data type** | Text (NL) & Source Code (PL) |
| **Input format** | `[CLS] NL_tokens [SEP] PL_tokens [EOS]` |

### B3. Preprocessing Pipeline

| Bước | Chi tiết |
|------|----------|
| **Tokenization** | WordPiece (NL) & Tokenizer của từng ngôn ngữ (PL) |
| **Encoding** | Contextual vector representation qua Transformer |

---

## Phần C: Kiến Trúc Mô Hình — Architecture Blueprint

### C1. Tổng Quan Kiến Trúc
CodeBERT sử dụng kiến trúc **multi-layer bidirectional Transformer**, cụ thể là cấu hình của **RoBERTa-base**.

### C2. Model Details
- **Total parameters**: 125M.
- **Layers**: 12 layers.
- **Hidden dimension**: 768.
- **Attention heads**: 12.

---

## Phần D: Training Configuration

### D1. Pre-training Objectives
1. **Masked Language Modeling (MLM)**: Áp dụng trên bimodal data (NL-PL pairs), dự đoán các token bị che (15%).
2. **Replaced Token Detection (RTD)**: Áp dụng trên cả bimodal và unimodal data. Sử dụng các Generator (n-gram models) để tạo ra các token thay thế, sau đó Discriminator (CodeBERT) dự đoán token nào là "original" hay "replaced".

### D2. Hyperparameters
- **Batch size**: 2,048.
- **Learning rate**: 5e-4.
- **Warmup steps**: 10K.
- **Max length**: 512 tokens.

---

## Phần E: So Sánh Với Baselines — Beyond Baselines

| Component | CodeBERT | Baselines (RoBERTa, CNN, BIRNN, etc.) |
|-----------|----------|----------------------------------------|
| Multi-modal | Kết hợp NL và PL | Thường chỉ tập trung vào NL hoặc PL riêng lẻ |
| Training data | Bimodal + Unimodal | Chủ yếu chỉ dùng một loại dữ liệu |

---

## Phần F: Ablation & Experiments — Surgical Analysis

### F1. Kết quả chính
- **Natural Language Code Search**: CodeBERT đạt SOTA trên tập dữ liệu CodeSearchNet (Macro-avg MRR: 0.7603).
- **Code Documentation Generation**: Đạt SOTA với BLEU-4 score cao hơn RoBERTa và các mô hình pre-train chỉ dùng code.
- **NL-PL Probing**: CodeBERT vượt trội trong việc dự đoán mối quan hệ ngữ nghĩa giữa NL và PL ở chế độ zero-shot.

---

## Phần I: Đánh Giá Cá Nhân

### I1. Điểm Mạnh
- Mô hình pre-train bimodal quy mô lớn đầu tiên cho 6 ngôn ngữ lập trình phổ biến.
- Sử dụng hiệu quả cơ chế **RTD** (tương tự ELECTRA) để học từ dữ liệu đơn ngữ khổng lồ.
- Khả năng **generalization** tốt sang các ngôn ngữ chưa được thấy trong lúc pre-train (ví dụ: C#).

### I5. Verdict
⭐ ⭐ ⭐ ⭐ ⭐ (5/5) - Một cột mốc quan trọng trong lĩnh vực AI cho Kỹ thuật Phần mềm (AI4SE).

---

## 3-Tier Explanation

### 1. Cấp độ Đứa trẻ (Child)
Hãy tưởng tượng bạn có một người bạn siêu giỏi, vừa biết nói tiếng người (NL) vừa biết viết mật mã máy tính (PL). **CodeBERT** chính là người bạn đó. Người bạn này được học bằng cách đọc hàng triệu ví dụ về cách người ta giải thích một đoạn mã. Thỉnh thoảng, chúng ta thử thách bạn bằng cách thay đổi một vài từ trong mã nguồn và đố bạn biết từ nào là "hàng giả". Nhờ luyện tập như vậy, bạn ấy hiểu rất rõ mối liên hệ giữa lời nói và mã máy tính.

### 2. Cấp độ Sinh viên (Student)
**CodeBERT** là một mô hình học sâu dựa trên kiến trúc **Transformer-base**. Nó được huấn luyện theo phương pháp **Self-supervised learning** trên hai loại dữ liệu: song ngữ (cặp mã nguồn và chú thích) và đơn ngữ (chỉ có mã nguồn). Điểm đặc biệt của nó là mục tiêu huấn luyện **Replaced Token Detection (RTD)**, nơi mô hình đóng vai trò là một Discriminator để phân biệt token gốc và token được tạo ra bởi một Generator. Điều này giúp mô hình nắm bắt được cấu trúc cú pháp và ngữ nghĩa sâu sắc của mã nguồn trong mối tương quan với ngôn ngữ tự nhiên.

### 3. Cấp độ Chuyên gia (Expert)
**CodeBERT** tận dụng sức mạnh của **Contextual Embeddings** đa phương thức (NL và PL). Bằng cách sử dụng **RoBERTa-base** làm nền tảng và mở rộng với các mục tiêu tối ưu hóa lai (**MLM** và **RTD**), mô hình có thể ánh xạ cả văn bản tự nhiên và mã nguồn vào cùng một không gian vector (shared vector space). Cơ chế RTD cho phép mô hình khai thác dữ liệu unimodal hiệu quả hơn so với MLM truyền thống bằng cách cung cấp tín hiệu học tập trên toàn bộ chuỗi đầu vào. Điều này cực kỳ quan trọng đối với các tác vụ hạ nguồn (downstream tasks) như **Semantic Code Search** (truy vấn mã nguồn bằng ngôn ngữ tự nhiên) và **Summarization** (tự động viết tài liệu cho code).

---

## Misconception Seeds
1. **Lầm tưởng**: CodeBERT chỉ dùng được cho 6 ngôn ngữ lập trình được huấn luyện.
   - **Sự thật**: Bài báo cho thấy CodeBERT có khả năng chuyển đổi tri thức (transfer learning) sang các ngôn ngữ khác như C# với kết quả rất tốt.
2. **Lầm tưởng**: CodeBERT hiểu cấu trúc cây cú pháp (AST) của mã nguồn.
   - **Sự thật**: Phiên bản gốc của CodeBERT xử lý mã nguồn như một chuỗi các token (sequence of tokens), chưa tích hợp trực tiếp cấu trúc đồ thị hay cây của code.

---

## Transfer Question
**Làm thế nào để tinh chỉnh (fine-tune) CodeBERT để phát hiện các lỗ hổng bảo mật cụ thể trong mã nguồn (như SQL Injection), khi mà hành vi tấn công thường nằm ở sự kết hợp tinh vi giữa cấu trúc lệnh và dữ liệu đầu vào không được kiểm soát?**
