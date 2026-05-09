---
aliases: [Gumbel-Softmax Roadmap v2]
created: 2026-04-29
progress: research
blueprint: [SQLi-GAN]
tags: [spec, gumbel-softmax, sql-injection, gan, benchmark]
category: [blueprint]
---

# Lộ trình Kỹ thuật: SQLi-GAN — Benchmark Sinh Chuỗi Rời rạc Có Cấu trúc
## (Gumbel-Softmax Reparameterization Approach)

> **Mục tiêu nghiên cứu:** Xây dựng một bộ benchmark thực nghiệm đầy đủ (dataset + metrics + baselines) cho bài toán *Structured Discrete Sequence Generation (SDSG)*, sử dụng SQL Injection làm domain cụ thể do tính xác minh được của ngữ pháp hình thức. Đóng góp chính là bộ Composite Score và giao thức so sánh giữa 5 phương pháp sinh chuỗi.

---

## 🟩 Giai đoạn 1: Phát biểu Bài toán & Dữ liệu

**Mục tiêu:** Định nghĩa chính xác không gian bài toán SDSG và xây dựng nền tảng xác suất $P_{data}$.

- **Formal Task Definition:** Định nghĩa bài toán SDSG: học generative model $p_\theta(x)$ sao cho samples $x \sim p_\theta$ thỏa mãn đồng thời (1) hợp lệ theo SQL grammar $\mathcal{G}$, (2) đa dạng (không collapse), và (3) in-distribution so với $P_{data}$.
- **Scope Constraint rõ ràng:** Phạm vi nghiên cứu giới hạn ở *syntactic generation*, không đánh giá semantic correctness hay adversarial effectiveness — đây là **pure generation benchmark**.
- **Research Questions:**
  - RQ1: Phương pháp nào đạt Composite Score cao nhất trên SDSG task?
  - RQ2: Có sự đánh đổi (tradeoff) nào giữa Validity và Diversity không?
  - RQ3: Gumbel-Softmax có lợi thế gì so với policy-gradient methods (SeqGAN) trên domain có formal grammar?
- **Data Sourcing:**
  - Thu thập 50k mẫu SQLi từ PayloadsAllTheThings, SecLists, và 50k mẫu SQL sạch từ application logs.
  - Phân chia train/validation/test theo tỉ lệ 70/15/15; tập test được giữ cố định (frozen) cho toàn bộ benchmark.
- **Vocabulary Construction $V$:**
  - Trích xuất từ khóa SQL, ký tự đặc biệt (`'`, `--`, `/*`, `#`), và abstract tokens (`<TABLE>`, `<NUM>`, `<STR>`).
  - Tính **Entropy** $H(V)$ của tập dữ liệu để đo độ đa dạng ban đầu, dùng làm tham chiếu (reference entropy) trong đánh giá.
- **Latent Space Prior $p_z$:** Chọn Gaussian $\mathcal{N}(0, 1)$ để đảm bảo Latent Space mượt mà, thuận lợi cho nội suy cấu trúc.

---

## 🟨 Giai đoạn 2: Tiền xử lý & Phân tích Khám phá (EDA)

**Mục tiêu:** Chuyển đổi dữ liệu về dạng tensor mà không làm mất tính Linear Independence của các đặc trưng cú pháp.

- **SQL-Aware Tokenization (Regex-based):**
  - Không dùng whitespace tokenization đơn thuần; tách các token nhạy cảm như `'`, `--`, `/*`, `UNION`, `SELECT` thành các atomic tokens độc lập.
- **De-lexicalization (Structural Anonymization):**
  - Thay thế tên bảng bằng `<TABLE>`, số bằng `<NUM>`, chuỗi ký tự bằng `<STR>`.
  - Mục đích toán học: giảm variance không liên quan, ép model tập trung vào cấu trúc logic (manifold) thay vì giá trị cụ thể.
- **Sequence Standardization:**
  - Quyết định độ dài tối đa $L$ dựa trên phân vị thứ 95 của phân phối độ dài corpus.
  - Sử dụng `<SOS>`, `<EOS>`, `<PAD>` làm special tokens.
- **EDA — Phân tích đặc trưng:**
  - Vẽ biểu đồ phân phối độ dài chuỗi để chọn $L$ phù hợp.
  - Tính Cosine Similarity giữa các cụm tấn công để xác định các "modes" chính trong $P_{data}$, phục vụ cho việc phát hiện Mode Collapse sau này.

---

## 🟧 Giai đoạn 2.5: Thiết lập Baseline Registry

**Mục tiêu:** Định nghĩa giao thức so sánh chuẩn trước khi xây dựng mô hình chính — đây là nền tảng của toàn bộ benchmark.

- **Ngưỡng thành công (Success Threshold):** Gumbel-GAN phải đạt `Composite Score(GAN) > Composite Score(MLE-Baseline) + 15%` trên tập test cố định.
- **Tier 1 — Non-GAN Baselines (đo giá trị của adversarial training):**
  - **Markov Chain / Template-based:** Đo tính ngẫu nhiên cú pháp thuần túy, không có học máy.
  - **Standard Transformer-MLE:** Sinh chuỗi bằng cross-entropy loss thuần, không có adversarial loop.
- **Tier 2 — GAN Baselines (đo giá trị của Gumbel-Softmax so với các phương pháp GAN-for-text khác):**
  - **SeqGAN:** Policy Gradient với Monte Carlo rollout.
  - **MaliGAN:** Maximum Likelihood augmented GAN.
  - **RelGAN:** Relational Memory GAN với interpolation-based training.
- **Giao thức so sánh:** Tất cả 5 baselines và Gumbel-GAN được train trên cùng một tập dữ liệu, cùng vocabulary, cùng độ dài $L$; kết quả được report trên frozen test set duy nhất.

---

## 🟧 Giai đoạn 3: Kiến trúc Mô hình (Core Architecture)

**Mục tiêu:** Giải quyết bài toán "gradient không truyền qua discrete sampling" trong không gian token rời rạc.

- **Generator $G$ — Transformer Decoder:**
  - Sử dụng kiến trúc Transformer Decoder với cơ chế Masked Self-Attention.
  - **Gumbel-Softmax Layer:** Tích hợp ở đầu ra để biến đổi logits thành soft continuous vectors có khả năng truyền đạo hàm, thay thế hoàn toàn bước argmax không khả vi.
  - **MLE Pre-training:** Huấn luyện $G$ như một language model thông thường trước khi bước vào adversarial loop, đảm bảo $G$ học được cú pháp SQL cơ bản.
- **Discriminator $D$ — Dilated CNN (thay thế TextCNN nguyên bản):**
  - Sử dụng **Dilated Convolutional Network** với multi-scale kernels được thiết kế theo cấu trúc phân tầng của SQL:
    - Kernels `[2, 3]`: bắt các toán tử và từ khóa kép (`UNION SELECT`, `OR 1`).
    - Kernels `[5, 8]`: bắt các mệnh đề đơn (`WHERE id = <NUM>`).
    - Kernels `[12, 16]`: bắt các cấu trúc lồng nhau như subquery (`SELECT ... FROM (SELECT ...)`).
  - **Lý do chọn Dilated CNN thay TextCNN:** SQL có cấu trúc phân tầng và global dependency; dilation cho phép receptive field lớn mà không tăng số tham số, bắt được context xa hơn so với vanilla convolution.
- **Loss Function:** Triển khai **WGAN-GP** (Wasserstein GAN với Gradient Penalty) để đảm bảo Lipschitz Continuity cho $D$, tránh vanishing gradient và đảm bảo tính ổn định huấn luyện.

---

## 🟥 Giai đoạn 4: Chiến lược Huấn luyện Đối kháng

**Mục tiêu:** Đạt Nash Equilibrium mà không bị Mode Collapse, đồng thời duy trì khả năng truyền đạo hàm qua Gumbel-Softmax.

- **Adversarial Loop:** Huấn luyện song song $G$ và $D$ với tỉ lệ cập nhật $D:G = 5:1$ theo chuẩn WGAN.
- **Temperature Scheduling $\tau$ — Exponential Decay:**
  - Hàm decay: $\tau(t) = \tau_0 \cdot \exp(-r \cdot t)$, với $\tau_0 = 1.0$ và $r$ được chọn để $\tau$ đạt $0.1$ sau 80% số bước huấn luyện.
  - *Mục tiêu:* Giai đoạn đầu ($\tau$ cao) — phân phối mềm (soft) giúp đạo hàm truyền ổn định; giai đoạn cuối ($\tau$ thấp) — phân phối cứng (hard) gần với categorical thực tế.
- **Gradient Norm Monitoring:**
  - Theo dõi $||\nabla_\theta G||$ liên tục trong suốt quá trình huấn luyện.
  - Nếu $||\nabla_\theta G|| < \epsilon_{threshold}$ khi $\tau < 0.3$: trigger **Temperature Reset** (đặt lại $\tau = 0.5$) hoặc **Stop-and-Sample** (lấy mẫu tại checkpoint tốt nhất).
- **Mode Collapse Detection:**
  - Kiểm tra variance của các batch sinh ra sau mỗi epoch; nếu variance giảm đột ngột dưới ngưỡng $\sigma_{min}^2$: tăng Dropout hoặc inject thêm nhiễu vào Latent Space.

---

## 🟦 Giai đoạn 5: Đánh giá & Composite Score

**Mục tiêu:** Kiểm chứng Fidelity, Diversity, và Distribution Matching; tính Composite Score duy nhất để so sánh tất cả 6 phương pháp.

- **Định nghĩa Composite Score $S$:**
$$S = w_1 \cdot \text{Validity} + w_2 \cdot (1 - \text{Self-BLEU}) + w_3 \cdot (1 - \hat{W}_1)$$
  - $w_1, w_2, w_3$ được xác định qua ablation study trên validation set (khởi đầu với $w_1=0.4, w_2=0.3, w_3=0.3$).
  - Validity là **hard constraint**: phương pháp đạt Validity < 50% bị loại khỏi bảng xếp hạng chính.

- **Syntax Validity Rate (thành phần $w_1$):**
  - Parse 1.000 mẫu sinh ra bằng `sqlparse`; tỉ lệ parse thành công là Validity score.
  - Ngưỡng tối thiểu: 80% để một phương pháp được tính vào bảng so sánh chính.

- **Self-BLEU (thành phần $w_2$):**
  - Đo mức độ lặp lại nội bộ giữa các mẫu sinh ra; score thấp = đa dạng cao.
  - Sử dụng n-gram order N=3 làm chuẩn.

- **Wasserstein Distance $\hat{W}_1$ (thành phần $w_3$):**
  - **Thay thế JS Divergence** (không nhất quán với WGAN-GP loss đã dùng khi train).
  - Tính $W_1$-distance trên embedding space giữa phân phối sinh ra $P_G$ và phân phối thực $P_{data}$; tránh vấn đề bão hòa của JS khi 2 phân phối không overlap.

- **Latent Space Walk:**
  - Thay đổi nhẹ vector $z$ để kiểm tra tính mượt mà của không gian nội suy; kết quả được report định tính (qualitative analysis).

---

## 🟪 Giai đoạn 6: Re-lexicalization & Đóng gói

**Mục tiêu:** Xây dựng pipeline đầu cuối có thể tái sử dụng; report latency và throughput để benchmark có tính reproducibility.

- **Re-lexicalization Module — Target Schema Injection:**
  - Module nhận đầu vào là **JSON Schema** của database mục tiêu (table names, column names, data types) để thực hiện *logic-preserving replacement* thay cho "wordlist mục tiêu" mờ nhạt.
  - Ánh xạ: `<TABLE>` → tên bảng từ schema, `<NUM>` → giá trị số hợp lệ theo kiểu dữ liệu cột, `<STR>` → chuỗi phù hợp context.
  - **Syntax-Filter Buffer:** Chỉ trả về các payload đã qua re-lexicalization và vẫn parse được bởi `sqlparse`; loại bỏ payload không hợp lệ sau khi thay thế.

- **Inference Pipeline:**
  - Input: vector nhiễu $z \sim \mathcal{N}(0,1)$ + JSON Schema.
  - Process: feed-forward qua $G$ → Gumbel-Softmax argmax → Re-lexicalization → Syntax-Filter.
  - Output: danh sách payload hợp lệ cú pháp.
  - **Latency target:** < 100ms/payload trên CPU inference (không có GPU).

- **API Service (FastAPI):**
  - `POST /generate` — nhận `{seed, schema, n_samples}`, trả về `{payloads[], validity_rate, generation_time_ms}`.
  - `GET /health` — kiểm tra trạng thái model.
  - Endpoint được thiết kế stateless để dễ containerize và reproduce.

- **Reproducibility Package:**
  - Đóng gói toàn bộ: frozen test set, pre-trained checkpoints của 6 phương pháp, evaluation script, và hướng dẫn re-run benchmark từ đầu.