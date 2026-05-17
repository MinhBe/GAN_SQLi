# Phân Tích Bài Báo Khoa Học: LeakGAN (Guo 2018)

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | Long Text Generation via Adversarial Training with Leaked Information |
| **Tác giả** | Jiaxian Guo, Sidi Lu, Han Cai, Weinan Zhang, Yong Yu, Jun Wang |
| **Năm** | 2018 |
| **Conference / Journal** | AAAI 2018 |
| **Link** | https://arxiv.org/abs/1709.08624 |

### A1. Phân Loại GAN Taxonomy

| Thuộc tính | Lựa chọn |
|------------|----------|
| **GAN Type** | Hierarchical GAN / LeakGAN |
| **Architecture Family** | RNN-based (LSTM) + CNN |
| **Divergence** | Policy Gradient (Reinforcement Learning) |
| **Task Type** | Long Text Generation |

---

## Phần B: Dữ Liệu — Data Pipeline Deep-Dive

### B1. Dataset Overview
- **Synthetic Data**: Độ dài 20 và 40.
- **EMNLP2017 WMT News**: Dữ liệu tin nhắn dài.
- **COCO Image Captions**: Dữ liệu trung bình.
- **Chinese Poems**: Dữ liệu ngắn (Thơ tứ tuyệt).

### B3. Preprocessing Pipeline
- **Tokenization**: Word-level.
- **Filtering**: Loại bỏ từ tần suất thấp (< 4050 cho WMT), loại bỏ câu ngắn (< 20 từ cho WMT).

---

## Phần C: Kiến Trúc Mô Hình — Architecture Blueprint

### C1. Tổng Quan Kiến Trúc
- **Discriminator (D)**: Một mạng CNN dùng để trích xuất đặc trưng (Feature Extractor) và phân loại.
- **Generator (G)**: Cấu trúc phân cấp (Hierarchical):
    - **MANAGER**: Nhận đặc trưng "leaked" (bị rò rỉ) từ CNN của D, tạo ra mục tiêu (goal vector $g_t$).
    - **WORKER**: Nhận $g_t$ và từ hiện tại để dự đoán từ tiếp theo.

### C2. Generator Architecture
- **MANAGER**: LSTM.
- **WORKER**: LSTM kết hợp với Goal Embedding.
- **Mechanism**: Thông tin từ D "rò rỉ" qua các lớp đặc trưng cấp cao đến MANAGER của G để hướng dẫn WORKER.

---

## Phần D: Training Configuration

### D4. Loss Function Details
- **Manager Loss**: Cực đại hóa sự tương đồng cosine giữa vector mục tiêu và sự thay đổi thực tế trong không gian đặc trưng của D.
- **Worker Loss**: Sử dụng Policy Gradient (REINFORCE) với phần thưởng nội tại (intrinsic reward) dựa trên việc tuân thủ mục tiêu của Manager.

---

## Phần E: Beyond Baselines — X-Factor

**Innovation Chính**: Giải quyết vấn đề tín hiệu thưởng thưa thớt (sparse rewards) trong sinh văn bản dài bằng cách cho phép Discriminator "rò rỉ" thông tin đặc trưng trung gian cho Generator. Sử dụng Học tăng cường phân cấp (Hierarchical RL) để G có thể học cấu trúc câu một cách gián tiếp.

---

## Phần G: Training Stability & Mode Collapse

### G1. Stability Techniques
- **Bootstrapped Rescaled Activation**: Kỹ thuật dựa trên xếp hạng (rank-based) để chuẩn hóa phần thưởng, tránh vanishing gradient.
- **Interleaved Training**: Huấn luyện xen kẽ giữa Supervised Learning (MLE) và Adversarial Training (GAN) để tránh sụp đổ mode (mode collapse).

---

## Phần H: Kết Quả & Đánh Giá

- Vượt xa các model như SeqGAN, RankGAN trên các bộ dữ liệu văn bản dài.
- Điểm BLEU cải thiện đáng kể khi độ dài câu tăng lên.
- Vượt qua bài kiểm tra Turing (Turing test) với tỷ lệ người tin là văn bản thật cao hơn hẳn các model trước.

---

## Three-tier Explanation

**1. Cấp độ Trẻ em (Analogy):**
Hãy tưởng tượng một người thầy (Discriminator) và một học trò (Generator). Bình thường, thầy chỉ chấm "Đạt" hoặc "Không đạt" sau khi học trò viết xong cả bài văn dài. Điều này khiến học trò rất khó học. Trong LeakGAN, người thầy cho phép học trò "nhìn trộm" vào các ghi chú của mình trong khi đang viết từng câu. Nhờ những gợi ý nhỏ này, học trò biết mình nên viết tiếp theo hướng nào để bài văn hay hơn.

**2. Cấp độ Sinh viên (Mechanism):**
LeakGAN sử dụng Hierarchical Reinforcement Learning để sinh văn bản. Discriminator (CNN) cung cấp các feature vector $f_t$ tại mỗi bước. Mạng MANAGER của Generator nhận $f_t$ và tạo ra một "goal vector" $g_t$ trong không gian tiềm ẩn. Mạng WORKER sử dụng $g_t$ này làm điều kiện để chọn từ tiếp theo. Việc này biến phần thưởng từ một giá trị scalar duy nhất ở cuối câu thành một chuỗi các chỉ dẫn đặc trưng xuyên suốt quá trình sinh.

**3. Cấp độ Chuyên gia (Trade-offs):**
LeakGAN giải quyết hạn chế của SeqGAN bằng cách cung cấp thông tin cấu trúc trung gian. Việc sử dụng không gian đặc trưng của Discriminator làm không gian mục tiêu cho Manager giúp Generator nắm bắt được các đặc điểm ngữ nghĩa và cú pháp cấp cao mà D đã học được. Tuy nhiên, kiến trúc này phức tạp hơn nhiều, yêu cầu phối hợp nhịp nhàng giữa Manager, Worker và Discriminator, đồng thời tốn nhiều tài nguyên tính toán hơn cho việc trích xuất đặc trưng liên tục.

---

## Misconception Seeds
1. **Lầm tưởng**: LeakGAN cần các nhãn ngữ pháp (noun, verb) để học cấu trúc câu.
   *Thực tế*: LeakGAN học cấu trúc câu một cách tự động (implicitly) thông qua sự tương tác giữa Manager và Worker mà không cần bất kỳ sự giám sát nào.
2. **Lầm tưởng**: Goal vector của Manager là một từ cụ thể trong từ điển.
   *Thực tế*: Goal vector là một vector trong không gian đặc trưng của mạng CNN, đại diện cho một hướng đi hoặc một phong cách ngữ nghĩa cần hướng tới.

---

## Transfer Question
Làm thế nào để áp dụng cơ chế "Leak Information" (rò rỉ thông tin) từ một mô hình phân loại (Classifier) sang một mô hình sinh (Generator) trong các tác vụ không phải văn bản, ví dụ như sinh lộ trình di chuyển của robot trong môi trường phức tạp?
