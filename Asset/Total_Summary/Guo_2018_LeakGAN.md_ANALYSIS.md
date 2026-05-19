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

---

## Phần C (bổ sung): C1. ASCII Architecture Diagram

```
Real/Fake text → CNN Discriminator D
                      │
              D intermediate features f_t
              (leaked at EVERY step, not just end)
                      │
        ┌─────────────┴────────────┐
        ▼                          ▼
   MANAGER (LSTM)           WORKER (LSTM)
   Input: f_t (D features)  Input: goal g_t + current token
   Output: goal g_t          Output: next token distribution
        │                          │
        └─────────────┬────────────┘
                      ▼
             Generated Token t+1
                      │
              repeat until EOS
                      ▼
            Full Generated Sequence
                      │
              → D for final reward
              → Bootstrapped rescaled reward
```

**Key difference vs SeqGAN**: D features được leak ở EVERY step t, không chỉ ở cuối chuỗi.

---

## Phần H (bổ sung): H1.1. Main Results Table

| Dataset | Model | NLL (lower=better) | BLEU-2 | BLEU-3 | BLEU-4 |
|---------|-------|-------------------|--------|--------|--------|
| Synthetic (T=20) | SeqGAN | 8.736 | — | — | — |
| Synthetic (T=20) | **LeakGAN** | **7.038** | — | — | — |
| Synthetic (T=40) | SeqGAN | 10.310 | — | — | — |
| Synthetic (T=40) | **LeakGAN** | **7.191** | — | — | — |
| EMNLP2017 WMT | SeqGAN | — | 0.917 | 0.747 | 0.530 |
| EMNLP2017 WMT | **LeakGAN** | — | **0.926** | **0.816** | **0.660** |
| COCO Captions | SeqGAN | — | 0.917 | 0.747 | 0.530 |
| COCO Captions | **LeakGAN** | — | **0.926** | **0.816** | **0.660** |

**Key insight**: LeakGAN improvement lớn nhất ở T=40 (long sequences) — NLL gap 8.736→7.038 (SeqGAN) vs 10.310→7.191 (SeqGAN). SeqGAN degradation tăng theo T; LeakGAN gần như stable.

---

## Phần I (bổ sung): I3. Actionable Insights

| Idea | Source | Priority | Effort | How to Implement |
|------|--------|----------|--------|-----------------|
| LeakGAN cho long SQLi (T>30) | Paper Section 3 | P2 | High | Manager nhận D CNN features, Worker sinh tokens |
| Bootstrapped rescaled reward | Paper Section 4.1 | P1 | Medium | Rank-based normalization thay raw reward |
| Intermediate D features cho reward shaping | Core innovation | P2 | High | Extract intermediate CNN layer features, không chỉ scalar output |
| Interleaved MLE+Adversarial training | Paper Section 4.2 | P1 | Medium | Mỗi 5 adv steps → 1 MLE step để ổn định |

### I4. Research Gaps

| Gap | Mô tả | Potential Direction |
|-----|-------|---------------------|
| LeakGAN chưa test trên structured syntax | EMNLP/COCO là natural text, SQL có strict grammar | LeakGAN + SQLParse validation |
| Manager-Worker coordination | Khi Manager goal ≠ Worker token distribution | KL regularization giữa goal space và token space |
| Gumbel + LeakGAN combination | Chưa có paper kết hợp | V5 future: Gumbel-Softmax trong Worker, Manager nhận D features |

### I5. Verdict

| Criteria | Rating | Notes |
|----------|--------|-------|
| **Technical soundness** | ⭐⭐⭐⭐½ | Hierarchical RL + leaked features — elegant |
| **Novelty** | ⭐⭐⭐⭐½ | Giải quyết sparse reward problem một cách sáng tạo |
| **Reproducibility** | ⭐⭐⭐⭐☆ | Code available (AAAI), datasets public |
| **Relevance to SQLi** | ⭐⭐⭐⭐☆ | SQL payload T=40-80 → LeakGAN relevant hơn SeqGAN |
| **Overall quality** | ⭐⭐⭐⭐☆ | Strong paper, complex implementation |

**Summary**: LeakGAN giải quyết sparse reward problem của SeqGAN bằng cách để D "rò rỉ" intermediate features cho Generator ở mỗi bước generation. Kết quả đặc biệt tốt cho long sequences (T>30). Relevant cao cho SQLi vì payload có thể dài. Tuy nhiên, implementation phức tạp hơn SeqGAN ~3×. **Khuyến nghị**: Implement V5 Gumbel-SeqGAN trước, nếu BLEU/diversity target không đạt → upgrade lên LeakGAN architecture.

---

### H10. Thesis Section Mapping

| Thesis Section | Nội dung từ paper này |
|----------------|----------------------|
| 2.1 Literature Review | LeakGAN — hierarchical RL cho long text generation |
| 2.1 Sparse Reward Problem | "SeqGAN chỉ có reward ở cuối → LeakGAN giải quyết bằng intermediate features" |
| 5.2 Future Work | "LeakGAN architecture cho SQLi payloads dài (T>30)" |
| References | Guo et al. (2018), AAAI |
