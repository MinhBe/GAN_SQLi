# Phân Tích Bài Báo: Imbalanced Data Classification Modelling Using CTGAN and Decision Tree

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | Imbalanced Data Classification Modelling Using CTGAN and Decision Tree for Student Graduation Predicting in a Courses |
| **Tác giả** | M. Ramaddan Julianti, Yaya Heryadi, Budi Yulianto, Widodo Budiharto |
| **Năm** | 2024 |
| **Conference / Journal** | Journal of Electrical Systems (JES) |
| **Link** | http://journal.esrgroups.org/jes/article/view/1000 |

### A1. Phân Loại GAN Taxonomy

| Thuộc tính | Lựa chọn |
|------------|----------|
| **GAN Type** | Conditional Tabular GAN (CTGAN) |
| **Architecture Family** | MLP-based (for Tabular data) |
| **Divergence** | WGAN-GP (CTGAN usually uses Wasserstein loss with Gradient Penalty) |
| **Task Type** | Data Augmentation / Oversampling for Imbalanced Classification |

---

## Phần B: Dữ Liệu — Data Pipeline Deep-Dive

### B1. Dataset Overview

| Thuộc tính | Mô tả |
|------------|-------|
| **Tên dataset** | Student Graduation Dataset |
| **Nguồn** | Private course data (Bina Nusantara University) |
| **Kích thước** | 330 mẫu (sau khi balancing) |
| **Domain** | Education / Academic Performance |

### B2. Data Characteristics

| Đặc điểm | Mô tả |
|----------|-------|
| **Data type** | Tabular |
| **Features** | Attendance, Quizzes (Quis), Independent Assignments (TM), Group Assignments (TK), Midterm (Middle test), Final test |
| **Class distribution** | Ban đầu mất cân bằng (Pass > Fail), sau đó được balance thành 180 Pass / 150 Fail |

### B3. Preprocessing Pipeline

| Bước | Chi tiết |
|------|----------|
| **Tokenization** | N/A (Dữ liệu số/phân loại) |
| **Normalization** | Mode-specific normalization (đặc thù của CTGAN cho dữ liệu multimodal) |
| **Encoding** | Labeling cho các tính năng phân loại |

---

## Phần C: Kiến Trúc Mô Hình — Architecture Blueprint

### C1. Tổng Quan Kiến Trúc

- **Giai đoạn 1 (Data Balancing):** Sử dụng CTGAN để sinh dữ liệu nhân tạo cho lớp thiểu số (Fail).
- **Giai đoạn 2 (Prediction):** Sử dụng thuật toán Decision Tree (Cây quyết định) để phân loại dựa trên tập dữ liệu đã được cân bằng.

### C2. Generator (CTGAN)

- Sử dụng **Conditional Generator** để giải quyết vấn đề mất cân bằng lớp bằng cách lấy mẫu có điều kiện.
- Áp dụng **Gumbel-Softmax** hoặc các kỹ thuật tương tự để xử lý dữ liệu rời rạc (categorical).

---

## Phần D: Training Configuration

- **Split ratio:** 80% Training / 20% Testing.
- **Metrics:** Accuracy, Precision, Recall, F1-Score.

---

## Phần H: Kết Quả & Đánh Giá

### H1. Quantitative Results

| Metric | Value |
|--------|-------|
| **Accuracy** | 99% |
| **Precision (Failed)** | 0.99 |
| **Recall (Failed)** | 0.99 |

---

## Phần I: Đánh Giá Cá Nhân

### I1. Điểm Mạnh
- Kết hợp hiệu quả giữa kỹ thuật sinh dữ liệu hiện đại (GAN) với thuật toán phân loại cổ điển dễ giải thích (Decision Tree).
- Giải quyết trực diện bài toán dữ liệu mất cân bằng trong giáo dục.

### I2. Điểm Yếu
- Dataset còn khá nhỏ (330 mẫu sau khi augment).
- Độ chính xác 99% trên dữ liệu nhân tạo có thể dẫn đến rủi ro overfitting nếu phân phối của CTGAN quá khớp với dữ liệu gốc.

---

## 3-Tier Explanation

### 1. Plain English (Dành cho người không chuyên)
Hãy tưởng tượng bạn đang dạy một lớp học và muốn biết học sinh nào có nguy cơ trượt ngay từ đầu năm. Tuy nhiên, trong quá khứ, số người trượt rất ít so với số người đỗ, khiến máy tính khó học được "dáng dấp" của một người sắp trượt. Bài báo này sử dụng một "máy photocopy thông minh" (CTGAN) để tạo ra thêm các hồ sơ giả lập của những học sinh trượt (dựa trên các đặc điểm thực tế). Sau khi có đủ dữ liệu cân bằng, họ dùng một "sơ đồ dòng chảy" (Decision Tree) để đưa ra quyết định dự đoán chính xác tới 99%.

### 2. Technical (Dành cho kỹ sư/sinh viên chuyên ngành)
Bài báo giải quyết vấn đề mất cân bằng lớp (class imbalance) trong bài toán dự đoán kết quả học tập bằng cách sử dụng CTGAN (Conditional Tabular Generative Adversarial Networks). CTGAN vượt trội hơn SMOTE truyền thống nhờ khả năng mô hình hóa các phân phối phi Gaussian và đa phương thức (multimodal) trong dữ liệu bảng. Sau khi oversampling lớp thiểu số, mô hình Decision Tree được huấn luyện, đạt được Precision và Recall cực cao (0.99) cho cả hai lớp, giúp xác định sớm các sinh viên có rủi ro "dropout".

### 3. Analogical (Dùng phép ẩn dụ)
CTGAN giống như một nghệ nhân làm hoa giả: thay vì chỉ có vài bông hoa héo (dữ liệu học sinh trượt) giữa một rừng hoa tươi (học sinh đỗ), nghệ nhân này quan sát kỹ các bông hoa héo thực và làm thêm hàng trăm bông hoa giả giống y hệt. Nhờ vậy, người làm vườn (mô hình Decision Tree) có thể học được cách phân biệt hoa héo và hoa tươi một cách rõ ràng nhất vì đã có đủ mẫu vật để quan sát cả hai loại.

---

## Misconception Seeds (Hạt giống hiểu lầm)
1. **Lầm tưởng:** GAN chỉ dùng cho hình ảnh. **Thực tế:** CTGAN được thiết kế riêng để sinh dữ liệu dạng bảng (tabular) với các biến số và biến phân loại.
2. **Lầm tưởng:** Accuracy 99% luôn là tốt. **Thực tế:** Trong dữ liệu được sinh nhân tạo, độ chính xác cao có thể do dữ liệu nhân tạo quá giống dữ liệu huấn luyện, cần kiểm tra tính đa dạng (diversity) của mẫu sinh ra.

---

## Transfer Question (Câu hỏi chuyển đổi)
"Nếu chúng ta áp dụng CTGAN để tạo dữ liệu tấn công SQL Injection nhân tạo dựa trên một tập mẫu nhỏ các cuộc tấn công thực tế, làm thế nào để đảm bảo dữ liệu sinh ra không chỉ là bản sao của dữ liệu cũ mà còn chứa các biến thể mới có khả năng vượt qua WAF?"