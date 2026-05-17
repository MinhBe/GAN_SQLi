# Phân Tích Bài Báo Khoa Học: GSQLi (Le et al., 2024)

---

## Core Question
**Làm thế nào để tự động hóa việc tạo ra các payload tấn công SQL Injection (SQLi) đa dạng, có khả năng vượt qua các hệ thống tường lửa ứng dụng web (WAF) hiện đại (cả dựa trên Machine Learning và các WAF thực tế như ModSecurity) mà vẫn giữ nguyên được tính năng tấn công ban đầu?**

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | GSQLi: A GAN-based Approach for Adversarial SQL Injection Sample Generation against WAF |
| **Tác giả** | Le Minh Khan, Hien Do Hoang, Khoa Ngo-Khanh, Phan The Duy, Van-Hau Pham |
| **Năm** | 2024 (Dựa trên thông tin grant D1-2024-60) |
| **Conference / Journal** | University of Information Technology (UIT), VNU-HCM |
| **Link** | N/A (Tài liệu nội bộ/Bản thảo) |

### A1. Phân Loại GAN Taxonomy

| Thuộc tính | Lựa chọn |
|------------|----------|
| **GAN Type** | Customized Conditional GAN (cGAN) |
| **Architecture Family** | MLP-based (Dense layers) |
| **Task Type** | Adversarial Sample Generation / SQLi Mutation |
| **Input** | Mutation Vector (15 features) + Noise |

### A2. Code Availability

| Mục | Thông tin |
|-----|-----------|
| **Official code** | N/A |
| **Framework** | TensorFlow v2.16.1, Python v3.10 |
| **Tools used** | Libinjection (để parse token) |

---

## Phần B: Dữ Liệu — Data Pipeline Deep-Dive

### B1. Dataset Overview

| Thuộc tính | Mô tả |
|------------|-------|
| **Tên dataset** | HttpParams và SSHS (từ Kaggle) |
| **Quy mô** | HttpParams: 5,557 SQLi; SSHS: 6,217 SQLi (đều < 100 ký tự) |
| **Domain** | SQL Injection Payloads |

### B2. Preprocessing Pipeline

| Bước | Chi tiết |
|------|----------|
| **Tokenization** | Sử dụng **Libinjection** để tách payload thành các token (keywords, operations, strings, etc.) |
| **Feature Extraction** | Tạo **Mutation Vector** 15 chiều (đếm Union, Where, Space, True/False Exp, Comment, etc.) |
| **Attack Classifier** | Một mô hình CNN được huấn luyện trước để gán nhãn cho Discriminator. |

---

## Phần C: Kiến Trúc Mô Hình — Architecture Blueprint

### C1. Tổng Quan Kiến Trúc
GSQLi sử dụng mô hình GAN tùy chỉnh để sinh ra các **Mutation Actions** (hành động biến đổi).
- **Generator**: Nhận Noise và Mutation Vector, sinh ra chuỗi các Mutation Actions phù hợp với từng token.
- **Discriminator**: Phân biệt giữa hành động biến đổi dẫn đến payload bị phát hiện (malicious) và hành động dẫn đến payload vượt qua được WAF (normal).

### C2. Generator & Discriminator Details
- **Generator Layers**: Dense(512) -> Normalization -> Dense(256) -> Normalization -> Dense(128) -> Normalization -> Dense(a).
- **Discriminator Layers**: Tương tự nhưng kết thúc bằng Dense(2) để phân loại nhãn.

---

## Phần D: Training Configuration

### D1. Mutation Actions (Hành động biến đổi)
Các kỹ thuật biến đổi chính bao gồm:
- **Case Swapping**: `UNION` -> `uNIoN`
- **Inline Comment**: `UNION` -> `/*!50000UNION*/`
- **Whitespace Swapping**: Dùng comment thay khoảng trắng.
- **Logical/Compare Operators Swapping**: `OR` -> `||`, `=` -> `LIKE`.
- **Encoding**: Hex encoding cho chuỗi hoặc số.

### D2. Loss Function
Sử dụng **Cross-Entropy (CE)**:
- $L_G = CE(y_0, D(v, a))$ : Generator cố gắng sinh hành động để Discriminator đoán là 0 (normal).
- $L_D = CE(y_c, D(v, a))$ : Discriminator cố gắng bắt chước nhãn từ Classifier ($y_c$).

---

## Phần E: So Sánh Với Baselines — Beyond Baselines

| Component | GSQLi | AdvSQLi (Qu et al.) | SSQLi (Guan et al.) |
|-----------|-------|---------------------|---------------------|
| Model | Customized GAN | CFG, MCTS | SAC (Reinforcement Learning) |
| Goal | Sinh payload vượt WAF | Sinh payload vượt WAF | Sinh payload vượt WAF |
| Functionality Check | Có | Có | Có |

---

## Phần H: Kết Quả & Đánh Giá

### H1. Quantitative Results
- **Scenario 2 (ML-based)**: Tỷ lệ phát hiện (TPR) của các mô hình RNN, GRU, BiLSTM giảm mạnh khi đối mặt với payload đột biến từ GSQLi (đặc biệt trên tập SSHS, TPR giảm xuống còn ~88%).
- **Scenario 3 (Real-world WAF)**: Trên **ModSecurity (OWASP rule set)**, tỷ lệ lọt lưới (FNR) đạt 2.3% cho tập SSHS và 0.19% cho HttpParams.

---

## Phần I: Đánh Giá Cá Nhân

### I1. Điểm Mạnh
- Sử dụng **Mutation Vector** thay vì chỉ Noise giúp Generator học được chiến lược đột biến tùy chỉnh cho từng payload.
- Kết hợp thành công **Libinjection** để đảm bảo tính hợp lệ về mặt cú pháp của payload sau đột biến.
- Đánh giá trên cả mô hình ML và WAF thực tế (ModSecurity).

### I5. Verdict
⭐ ⭐ ⭐ ⭐ (4/5) - Một nghiên cứu thực tiễn, có tính ứng dụng cao trong Pen-testing, đặc biệt trong bối cảnh các WAF dựa trên ML đang trở nên phổ biến.

---

## 3-Tier Explanation

### 1. Cấp độ Đứa trẻ (Child)
Hãy tưởng tượng bạn muốn lẻn vào một bữa tiệc nhưng có một chú bảo vệ (WAF) đứng ở cửa. Chú bảo vệ sẽ đuổi những ai mặc áo phông có chữ "Kẻ trộm". **GSQLi** giống như một chiếc máy biến hình kỳ diệu. Nó sẽ giúp bạn thay đổi chữ trên áo, ví dụ như viết thành "k_E_t_R_o_M" hoặc dán thêm những miếng sticker che đi. Bạn vẫn là bạn, nhưng chú bảo vệ không còn nhận ra bạn là kẻ trộm nữa và cho bạn vào trong.

### 2. Cấp độ Sinh viên (Student)
**GSQLi** là một hệ thống sử dụng mạng đối kháng sinh (**GAN**) để tạo ra các biến thể tấn công SQL Injection. Thay vì sinh ra toàn bộ chuỗi văn bản, Generator của GSQLi sinh ra các **Mutation Actions** (ví dụ: đổi chữ hoa chữ thường, mã hóa Hex, chèn comment). Những hành động này được áp dụng lên payload gốc thông qua một bộ chuyển đổi (**Payload Transformer**). Điểm hay của hệ thống là việc sử dụng **Libinjection** để tách payload thành các token, đảm bảo rằng sau khi biến đổi, câu lệnh SQL vẫn có thể thực thi được trên database.

### 3. Cấp độ Chuyên gia (Expert)
**GSQLi** đề xuất một kiến trúc **Conditional GAN** tùy chỉnh cho nhiệm vụ sinh mẫu đối kháng (adversarial samples). Generator nhận đầu vào là sự kết hợp giữa vector nhiễu và **Mutation Vector** (vector đặc trưng chứa 15 thuộc tính cú pháp của payload). Đầu ra của Generator là một tập hợp các chỉ thị biến đổi (Mutation Actions). Hệ thống tích hợp một **Attack Classifier** (mô hình CNN) đóng vai trò là "Oracle" để cung cấp nhãn thực cho Discriminator trong quá trình huấn luyện. Cách tiếp cận này giúp GAN hội tụ nhanh hơn và sinh ra các payload có khả năng đánh lừa các bộ phân loại sâu (RNN, GRU, BiLSTM) và WAF dựa trên luật (ModSecurity) một cách hiệu quả mà vẫn bảo toàn được tính logic và khả năng khai thác lỗ hổng (**payload functionality**).

---

## Misconception Seeds
1. **Lầm tưởng**: GAN trong GSQLi sinh ra các chuỗi văn bản ngẫu nhiên.
   - **Sự thật**: GAN sinh ra các **chiến lược biến đổi** (actions), sau đó mới áp dụng lên payload gốc để đảm bảo tính đúng đắn về cú pháp.
2. **Lầm tưởng**: Chỉ cần đổi chữ hoa thành chữ thường là đủ để vượt qua WAF.
   - **Sự thật**: Các WAF hiện đại (như ModSecurity) có các quy tắc giải mã phức tạp. GSQLi phải kết hợp nhiều hành động (Case Swapping, Inline Comment, Whitespace Swapping) mới có thể bypass thành công.

---

## Transfer Question
**Dựa trên cơ chế "Mutation Actions" của GSQLi, bạn có thể đề xuất thêm những hành động biến đổi nào khác đặc thù cho cơ sở dữ liệu NoSQL (như MongoDB) để vượt qua các bộ lọc bảo mật dành cho NoSQL Injection không?**
