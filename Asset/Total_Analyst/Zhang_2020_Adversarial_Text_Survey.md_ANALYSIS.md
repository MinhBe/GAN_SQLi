# Phân Tích Bài Báo Khoa Học: Adversarial Text Survey (Zhang et al., 2020)

---

## Core Question
**Làm thế nào để hệ thống hóa và phân loại các phương pháp tấn công đối kháng (adversarial attacks) lên các mô hình học sâu trong lĩnh vực xử lý ngôn ngữ tự nhiên (NLP), từ đó xác định các lỗ hổng hiện tại và định hướng các chiến lược phòng thủ hiệu quả?**

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | Adversarial Attacks on Deep Learning Models in Natural Language Processing: A Survey |
| **Tác giả** | Wei Emma Zhang, Quan Z. Sheng, Ahoud Alhazmi, Chenliang Li |
| **Năm** | 2020 |
| **Conference / Journal** | ACM Transactions on Intelligent Systems and Technology (TIST) |
| **Link** | https://dl.acm.org/doi/10.1145/3374217 |

### A1. Phân Loại Taxonomy

| Thuộc tính | Lựa chọn |
|------------|----------|
| **Loại bài báo** | Survey / Review |
| **Lĩnh vực** | Adversarial Machine Learning in NLP |
| **Đối tượng nghiên cứu** | Tấn công (Attacks) & Phòng thủ (Defenses) |

---

## Phần B: Nội Dung Chính — Taxonomy & Concepts

### B1. Phân Loại Các Phương Pháp Tấn Công (Taxonomy)
Bài báo phân loại tấn công dựa trên 5 tiêu chí:
1. **Model Access**: White-box (biết rõ mô hình) vs. Black-box (chỉ biết input/output).
2. **Target**: Targeted (ép ra nhãn cụ thể) vs. Untargeted (chỉ cần làm sai).
3. **Granularity**: Character-level (ký tự), Word-level (từ), Sentence-level (câu).
4. **Task**: Classification, Machine Translation, QA, v.v.
5. **Attacked DNNs**: CNN, RNN, Transformer, v.v.

### B2. Sự khác biệt giữa Hình ảnh và Văn bản
- **Discrete vs. Continuous**: Hình ảnh là liên tục (pixels), văn bản là rời rạc (tokens).
- **Perceivability**: Thay đổi nhỏ ở ảnh khó nhận ra, nhưng thay đổi ở văn bản dễ làm mất tính tự nhiên hoặc sai ngữ pháp.
- **Semantic**: Thay đổi nhỏ ở văn bản có thể làm đảo lộn hoàn toàn ý nghĩa câu.

### B3. Phương pháp đo lường nhiễu (Perturbation Measurement)
- **Norm-based**: $L_0, L_2, L_\infty$ (áp dụng trên không gian nhúng - embedding).
- **Edit-based**: Edit distance (Levenshtein), Jaccard similarity.
- **Semantic-based**: Cosine similarity giữa các word vectors.
- **Syntactic-based**: Sử dụng các bộ kiểm tra ngữ pháp hoặc perplexity.

---

## Phần C: Các Chiến Lược Tấn Công Phổ Biến

### C1. White-box Attacks
- **FGSM-based**: Sử dụng gradient của hàm mất mát để tìm hướng thay đổi token hiệu quả nhất.
- **JSMA-based**: Sử dụng Jacobian matrix để xác định độ nhạy của đầu ra đối với từng token đầu vào.
- **HotFlip**: Sử dụng đạo hàm hướng (directional derivatives) để thực hiện các thao tác đổi chỗ (flip), chèn hoặc xóa ký tự.

### C2. Black-box Attacks
- **Concatenation Adversaries**: Thêm các câu vô nghĩa nhưng gây nhiễu vào cuối đoạn văn (phổ biến trong bài toán Reading Comprehension).
- **Edit Adversaries**: Thay đổi từ bằng từ đồng nghĩa (synonyms) hoặc tạo lỗi chính tả (typos).
- **GAN-based**: Sử dụng GAN để sinh ra các mẫu đối kháng trông tự nhiên hơn.

---

## Phần D: Chiến Lược Phòng Thủ (Defense)

1. **Adversarial Training**: Đưa các mẫu đối kháng vào tập huấn luyện để mô hình làm quen.
2. **Knowledge Distillation**: Sử dụng một mô hình nhỏ để học từ mô hình lớn nhằm giảm độ nhạy với nhiễu.
3. **Input Transformation**: Loại bỏ nhiễu trước khi đưa vào mô hình (ví dụ: dùng spell-check).

---

## Phần E: Các Thử Thách & Hướng Nghiên Cứu Tương Lai

- **Tính tự nhiên (Perceivability)**: Làm sao để tấn công mà con người không nhận ra.
- **Khả năng chuyển đổi (Transferability)**: Mẫu đối kháng tạo ra cho mô hình A có thể tấn công được mô hình B không?
- **Tấn công trên các kiến trúc mới**: BERT, RoBERTa và các mô hình Transformer lớn.

---

## Phần I: Đánh Giá Cá Nhân

### I1. Điểm Mạnh
- Cung cấp một cái nhìn toàn cảnh và có hệ thống về một lĩnh vực đang phát triển rất nhanh.
- Phân tích sâu sắc sự khác biệt giữa tấn công trên dữ liệu liên tục (ảnh) và rời rạc (văn bản).

### I2. Verdict
⭐ ⭐ ⭐ ⭐ ⭐ (5/5) - Tài liệu nhập môn bắt buộc cho bất kỳ ai muốn nghiên cứu về bảo mật trong NLP.

---

## 3-Tier Explanation

### 1. Cấp độ Đứa trẻ (Child)
Hãy tưởng tượng bạn có một con robot rất giỏi đọc sách. Nhưng một kẻ xấu đã tìm cách lừa nó bằng cách thay đổi một vài chữ cái hoặc thêm một câu kỳ lạ vào trang sách khiến con robot hiểu sai hoàn toàn. Bài báo này giống như một cuốn từ điển liệt kê tất cả các "mẹo" mà kẻ xấu dùng để lừa robot, đồng thời chỉ cho chúng ta cách dạy robot trở nên thông minh hơn để không bị lừa nữa.

### 2. Cấp độ Sinh viên (Student)
Bài báo của **Zhang et al. (2020)** là một bản khảo sát toàn diện về **Adversarial Attacks** trong NLP. Nó phân loại các kỹ thuật tấn công dựa trên mức độ hiểu biết về mô hình (**White-box vs. Black-box**) và đơn vị tác động (**Character, Word, Sentence**). Nội dung trọng tâm xoay quanh việc làm thế nào để tạo ra các nhiễu (perturbations) vừa đủ để làm sai lệch kết quả của mạng neural nhưng vẫn giữ được cấu trúc ngữ pháp và ngữ nghĩa ban đầu. Bài báo cũng tổng hợp các phương pháp phòng thủ như **Adversarial Training** và xác định các lỗ hổng của các mô hình hiện đại.

### 3. Cấp độ Chuyên gia (Expert)
Đây là một công trình hệ thống hóa các phương pháp sinh mẫu đối kháng trong không gian rời rạc. Tác giả nhấn mạnh vào các kỹ thuật tối ưu hóa như **Gradient-based search** trong không gian embedding liên tục và sau đó ánh xạ ngược lại các token gần nhất. Bài báo phân tích kỹ lưỡng các cơ chế kiểm soát nhiễu thông qua các metric như **Word Mover’s Distance** và **Language Model Perplexity** để đảm bảo tính **unperceivability**. Về phía phòng thủ, nó thảo luận về giới hạn của việc huấn luyện đối kháng khi đối mặt với các cuộc tấn công không nằm trong tập dữ liệu huấn luyện (lack of transferability), mở ra hướng nghiên cứu về tính bền vững (robustness) của các kiến trúc Transformer.

---

## Misconception Seeds
1. **Lầm tưởng**: Mẫu đối kháng chỉ là thêm lỗi chính tả.
   - **Sự thật**: Có những tấn công tinh vi chỉ thay đổi các từ đồng nghĩa hoặc cấu trúc câu mà vẫn giữ đúng ngữ pháp nhưng làm mô hình dự đoán sai hoàn toàn.
2. **Lầm tưởng**: Các phương pháp tấn công ảnh có thể áp dụng trực tiếp cho văn bản.
   - **Sự thật**: Không thể dùng gradient trực tiếp trên token rời rạc; cần các kỹ thuật xấp xỉ hoặc tìm kiếm trong không gian embedding.

---

## Transfer Question
**Dựa trên phân loại của bài khảo sát này, dự án GAN-SQLi của chúng ta thuộc loại tấn công nào (White-box/Black-box, Targeted/Untargeted, Granularity)? Và chúng ta có thể tận dụng metric nào trong bài báo (như Jaccard hay Semantic similarity) để đảm bảo các câu lệnh SQLi sinh ra vẫn mang tính logic của SQL?**
