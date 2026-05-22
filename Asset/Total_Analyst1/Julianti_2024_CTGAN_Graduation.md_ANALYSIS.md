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

---

## Bổ Sung Của Codex — Kiểm Tra Lại Theo Total_OCR1 (2026-05-22)

> Phần này được append thêm vào cuối file theo yêu cầu, không xóa hoặc sửa nội dung analysis gốc của đồng nghiệp.  
> Nguồn kiểm tra bổ sung: `Asset/Total_OCR1/Julianti_2024_CTGAN_Graduation.md`.  
> Workflow tham chiếu: `transcript-analysis` — Scientific Paper Hybrid Framework A-I.

### 1. Quan điểm bổ sung
Tài liệu liên quan đến GAN/sequence generation. Cần phân biệt rõ kỹ thuật ổn định huấn luyện với bằng chứng nó thắng MLE trong bài toán SQLi.

Các tín hiệu kỹ thuật nổi bật đọc được từ OCR hiện tại:

- oversampling cho class imbalance

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
> - Student graduation in one course is the main factor in supporting the learning process and minimizing the occurrence of drop outs. In this case, a prediction model is needed to be able to identify student graduation at the beginning of the learning process. The aim of this research is to produce a prediction model that has significant accuracy in predicting student graduation in one course using the decision tree algorithm and implementing the conditional tabular generative adversarial networks (CTGAN) model. CTGAN is a model that can produce synthetic data on certain input variables. First, the graduation dataset is collected and pre-processed, then a labeling process is carried out on the dataset, so that the data can be used as initial input for CTGAN modeling. Next, the dataset with certain label features is subjected to an oversampling process using the CTGAN model. Finally, a pre

### 5. Quyết định sử dụng
- **Dùng được cho**: related work, thiết kế ablation, hoặc lập luận phụ tùy theo nhóm paper.
- **Chưa đủ cho**: kết luận rằng GAN sẽ thắng MLE trên SQLi nếu không có thực nghiệm nội bộ và decision gate mới.
