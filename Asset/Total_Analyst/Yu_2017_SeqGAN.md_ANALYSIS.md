# Phân Tích Chuyên Sâu: SeqGAN: Sequence Generative Adversarial Nets with Policy Gradient

---

## 3-Tier Explanation

| Cấp độ | Giải thích |
|--------|------------|
| **ELI5 (Dễ hiểu nhất)** | Hãy tưởng tượng bạn đang viết một bài thơ. Sau khi viết được vài chữ, bạn dừng lại và tưởng tượng xem nếu mình viết tiếp như thế này thì bài thơ cuối cùng sẽ hay hay dở. Bạn hỏi một giám khảo xem bài thơ "trong tưởng tượng" đó được bao nhiêu điểm, rồi dựa vào điểm số đó để quyết định từ tiếp theo nên viết là gì. SeqGAN chính là người viết thơ thông minh như vậy. |
| **Technical (Kỹ thuật)** | SeqGAN giải quyết vấn đề không thể truyền ngược gradient qua các token rời rạc trong GAN truyền thống. Nó coi Generator là một tác tử Học tăng cường (Reinforcement Learning), trong đó việc chọn từ tiếp theo là một "hành động" (action). Để đánh giá một câu chưa hoàn chỉnh, SeqGAN sử dụng Monte Carlo search để "viết nốt" câu đó nhiều lần, lấy điểm số trung bình từ Discriminator làm phần thưởng (reward) để cập nhật chính sách (policy) của Generator. |
| **Researcher (Nghiên cứu)** | Bài báo thiết lập một khung làm việc kết hợp GAN và RL cho dữ liệu rời rạc. Đóng góp cốt lõi là việc sử dụng thuật toán REINFORCE kết hợp với Monte Carlo roll-outs để ước lượng hàm Q-value từ một Discriminator chỉ đánh giá được chuỗi hoàn chỉnh. Điều này giúp vượt qua rào cản về tính không khả vi (non-differentiability) của việc lấy mẫu từ phân phối rời rạc và khắc phục lỗi tích tụ (exposure bias) trong các mô hình RNN huấn luyện bằng Maximum Likelihood Estimation (MLE). |

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | SeqGAN: Sequence Generative Adversarial Nets with Policy Gradient |
| **Tác giả** | Lantao Yu, Weinan Zhang, Jun Wang, Yong Yu |
| **Năm** | 2017 |
| **Conference / Journal** | AAAI 2017 |
| **Link** | https://arxiv.org/abs/1609.05473 |

### A1. Phân Loại GAN Taxonomy

| Thuộc tính | Lựa chọn |
|------------|----------|
| **GAN Type** | RL-based GAN (Policy Gradient) |
| **Architecture Family** | RNN/LSTM (Generator) & CNN (Discriminator) |
| **Divergence** | RL Reward (không trực tiếp dùng Divergence truyền thống) |
| **Task Type** | Sequence Generation (Text, Poem, Music) |

---

## Phần B: Dữ Liệu — Data Pipeline Deep-Dive

### B1. Dataset Overview
- **Synthetic Data**: Sử dụng một mạng LSTM ngẫu nhiên (Oracle) để sinh dữ liệu chuẩn, giúp đánh giá chính xác độ tương đồng phân phối.
- **Real-world Data**: 
    - Thơ quatrains Trung Quốc (16,394 bài).
    - Diễn văn của Barack Obama (11,092 đoạn).
    - Dữ liệu nhạc folk (695 tệp MIDI).

### B2. Preprocessing
- Tokenization ở mức ký tự (cho thơ) hoặc từ.
- Dữ liệu nhạc được chuyển thành chuỗi cao độ (88 phím đàn).

---

## Phần C: Kiến Trúc Mô Hình — Architecture Blueprint

### C1. Generator (Policy)
- **Kiến trúc**: LSTM.
- **Input**: Hidden state hiện tại và token trước đó.
- **Output**: Phân phối xác suất (Softmax) trên từ điển cho token tiếp theo.

### C2. Discriminator (Reward Function)
- **Kiến trúc**: CNN (Convolutional Neural Network).
- **Input**: Chuỗi hoàn chỉnh.
- **Features**: Sử dụng nhiều kích thước kernel (vùng quan sát) khác nhau để bắt các đặc trưng n-gram.
- **Output**: Xác suất chuỗi là "thật" (0-1).

---

## Phần D: Training Configuration

| Thông số | Giá trị |
|----------|---------|
| **Pre-training** | Sử dụng MLE cho Generator và Cross-Entropy cho Discriminator (rất quan trọng) |
| **RL Algorithm** | REINFORCE |
| **MC Search (N)** | Số lần lấy mẫu ngẫu nhiên để ước lượng reward cho trạng thái trung gian |
| **Optimizer** | Adam / RMSprop |

---

## Phần E: So Sánh Với Baselines — Beyond Baselines

- **Baselines**: RNN (MLE), Scheduled Sampling, PG-BLEU.
- **Sự khác biệt**: SeqGAN không cần một hàm đánh giá cố định (như BLEU), mà tự học hàm đánh giá thông qua Discriminator, giúp nó tổng quát hóa tốt hơn cho nhiều loại dữ liệu (nhạc, thơ).

---

## Phần F: Ablation & Experiments — Surgical Analysis

- **Tầm quan trọng của Pre-training**: Nếu không huấn luyện trước (Pre-train) đủ tốt, Generator sẽ hoạt động ngẫu nhiên, Discriminator sẽ dễ dàng phân biệt và không cung cấp được tín hiệu chỉ dẫn (reward) hữu ích.
- **Tính ổn định**: Việc cập nhật xen kẽ giữa g-steps (Generator) và d-steps (Discriminator) cần được tinh chỉnh kỹ để tránh mất cân bằng.

---

## Phần G: Training Stability & Mode Collapse

- SeqGAN sử dụng **Monte Carlo search** để giảm phương sai (variance) của gradient, một vấn đề cố hữu của các phương pháp Policy Gradient, từ đó giúp quá trình huấn luyện ổn định hơn.

---

## Phần H: Kết Quả & Đánh Giá

- **Định lượng**: Đạt Negative Log-Likelihood (NLL) thấp nhất trên dữ liệu mô phỏng.
- **Định tính**: Trong bài kiểm tra với chuyên gia thơ Trung Quốc, thơ do SeqGAN tạo ra có điểm số gần xấp xỉ với thơ do người viết.

---

## Phần I: Đánh Giá Cá Nhân

- **Điểm Mạnh**: Mở ra một hướng đi mới cho việc áp dụng GAN vào xử lý ngôn ngữ tự nhiên. Kết hợp khéo léo giữa RL và GAN.
- **Điểm Yếu**: Chi phí tính toán cao do phải thực hiện Monte Carlo roll-outs nhiều lần cho mỗi bước sinh token.
- **Actionable Insight**: Có thể sử dụng SeqGAN để sinh các payload tấn công mạng có cấu trúc chuỗi (như lệnh shell, script độc hại) mà các mô hình sinh truyền thống thường thất bại do tính rời rạc của câu lệnh.

---

## Misconception Seeds

1. **Lầm tưởng**: Discriminator trong SeqGAN chấm điểm cho từng từ khi chúng được sinh ra.
   - **Thực tế**: Discriminator chỉ chấm điểm cho **cả câu**. Điểm số cho từng từ là điểm trung bình của các câu "giả định" được sinh tiếp theo từ từ đó (thông qua Monte Carlo).
2. **Lầm tưởng**: SeqGAN có thể thay thế hoàn toàn huấn luyện MLE.
   - **Thực tế**: SeqGAN cần MLE để khởi tạo (warm-up). Nếu không có MLE, mô hình gần như không thể hội tụ.

---

## Transfer Question

**Ứng dụng vào SQL Injection:**
Các câu lệnh SQL là chuỗi các token rời rạc có cấu trúc ngữ pháp chặt chẽ. Nếu ta coi WAF là một Discriminator, liệu ta có thể dùng SeqGAN để sinh ra các câu lệnh SQL Injection "vượt rào" không? Đặc biệt, cơ chế **Monte Carlo roll-outs** có thể giúp Generator "dự đoán" xem một từ khóa SQL vừa thêm vào (như `' OR '1'='1`) có khả năng dẫn đến một chuỗi exploit thành công ở cuối câu hay không?
