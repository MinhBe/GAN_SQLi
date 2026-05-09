# Lộ Trình Kỹ Thuật: SQLi-GAN (Hướng Tiếp Cận SeqGAN / Policy Gradient)

> **Tóm tắt hướng tiếp cận:** Mô hình hóa quá trình sinh SQL Injection như một bài toán ra quyết định tuần tự (Sequential Decision Making). Generator đóng vai trò Agent, chọn token tiếp theo tại mỗi bước thời gian $t$. Discriminator và WAF Oracle cung cấp tín hiệu phần thưởng để tối ưu hóa Policy qua thuật toán REINFORCE có giảm variance.

---

## 🟩 Giai đoạn 1: Xác Định Bài Toán & Xây Dựng Dữ Liệu

**Mục tiêu:** Xây dựng phân phối dữ liệu thực $P_{data}$ và thiết lập môi trường tương tác cho Agent.

- **Thu thập dữ liệu (Data Sourcing):**
  - Thu thập tối thiểu 50k mẫu SQLi (nguồn: GitHub, SecLists, OWASP) và 50k mẫu SQL sạch (log ứng dụng thực tế).
  - Phân loại mẫu theo kiểu tấn công: UNION-based, Boolean-based, Time-based, Stacked queries.
  - *Lưu ý:* Discriminator cần học phân biệt SQL sạch và SQLi — không chỉ học nhận dạng từ khóa `SELECT`.

- **Xây dựng Expert Demonstrations:**
  - Tách riêng tập các payload đã xác nhận bypass WAF thành công để dùng trong giai đoạn Pre-training (Behavior Cloning).
  - *Lưu ý thuật ngữ:* Đây là Imitation Learning (Behavior Cloning), không phải SeqGAN vanilla. Cần ghi rõ để tránh nhầm lẫn trong báo cáo.

- **Thiết lập Reward Oracle:**
  - **SQL Parser Oracle:** Dùng `sqlparse` hoặc `antlr4-sql` để kiểm tra tính hợp lệ cú pháp. Trả về $r_{syntax} \in \{0, 1\}$.
  - **WAF Oracle:** Dùng ModSecurity với ruleset OWASP CRS để đánh giá khả năng bypass. Trả về $r_{bypass} \in \{0, 1\}$.
  - *Quan trọng:* ModSecurity là rule-based và deterministic — model sẽ học cách vượt qua ruleset cụ thể, không phải học generalization. Cần ghi nhận giới hạn này.

- **Định nghĩa State-Action Space:**
  - State $s_t$: chuỗi token đã sinh từ bước 0 đến $t$.
  - Action $a_t$: chọn một token tiếp theo từ từ vựng $V$.
  - Terminal state: khi gặp token `<EOS>` hoặc đạt độ dài tối đa $L$.

---

## 🟨 Giai đoạn 2: Tiền Xử Lý & Thiết Lập Môi Trường

**Mục tiêu:** Chuẩn hóa dữ liệu và xây dựng lớp giao tiếp giữa Agent và Oracle.

- **SQL-Aware Tokenization:**
  - Không dùng whitespace tokenization đơn thuần. Tách chính xác các token nhạy cảm: `'`, `--`, `/*`, `UNION`, `SELECT`, `OR`, `AND`, `=`.
  - Xây dựng từ vựng $V$ bao gồm: từ khóa SQL, ký tự đặc biệt, placeholder `<TABLE>`, `<NUM>`, `<STR>`, `<PAD>`, `<EOS>`.

- **De-lexicalization (Ẩn danh hóa):**
  - Thay thế tên bảng, cột, giá trị cụ thể bằng placeholder để giảm variance không cần thiết.
  - Mục đích: ép model tập trung học *cấu trúc logic tấn công*, không memorize payload cụ thể.

- **Padding & Truncation:**
  - Quyết định độ dài chuỗi tối đa $L$ dựa trên phân tích phân phối độ dài trong dataset.
  - Dùng `<PAD>` cho chuỗi ngắn hơn $L$, cắt bớt chuỗi dài hơn $L$.

- **Environment Interaction Wrapper:**
  - Xây dựng lớp `SQLiEnv` với interface: `step(action) → (next_state, reward, done)`.
  - Reward cuối chuỗi: $r = \alpha \cdot r_{bypass} + (1 - \alpha) \cdot r_{syntax}$, với $\alpha$ là hyperparameter cân bằng giữa hai mục tiêu.
  - *Lưu ý:* Reward chỉ có tại terminal state — đây là sparse reward problem, cần xử lý đặc biệt ở Giai đoạn 3.

---

## 🟧 Giai đoạn 3: Thiết Kế Kiến Trúc Mô Hình

**Mục tiêu:** Xây dựng Generator (Policy) và Discriminator (Reward Function).

- **Generator — Policy Network $\pi_\theta$:**
  - Kiến trúc: **LSTM** (phù hợp với sequence dài, tránh vanishing gradient) hoặc **Transformer Decoder** (nếu cần attention over full context).
  - Output: phân phối xác suất $\pi_\theta(a_t | s_t)$ trên từ vựng $V$ tại mỗi bước $t$.
  - Input: embedding của token hiện tại + hidden state từ bước trước.

- **Discriminator $D_\phi$:**
  - Kiến trúc: **1D-CNN** với nhiều kích thước filter để bắt n-gram đặc trưng tấn công.
  - Output: xác suất $D_\phi(x) \in [0, 1]$ — payload $x$ là "thật" (từ dataset) hay "giả" (từ Generator).
  - Loss: **WGAN-GP** (Gradient Penalty) để đảm bảo Lipschitz continuity, tránh exploding gradients.

- **Xử lý Sparse Reward — Monte Carlo Roll-out:**
  - SeqGAN dùng MC Roll-out để ước lượng $Q(s_t, a_t)$ cho intermediate token.
  - *Giới hạn cần thừa nhận:* MC Roll-out có variance cực cao với sequence dài và reward chỉ xuất hiện ở terminal state. Để giảm variance, triển khai **baseline function** $b(s_t)$ (value network đơn giản) và tính advantage $A(s_t, a_t) = Q(s_t, a_t) - b(s_t)$.
  - Số lần roll-out mỗi token $N$: cân bằng giữa variance thấp (N lớn) và chi phí tính toán.

---

## 🟥 Giai đoạn 4: Huấn Luyện & Tối Ưu Hóa

**Mục tiêu:** Huấn luyện Generator học bypass WAF mà không bị Mode Collapse hay gradient không hội tụ.

- **Pre-training — Supervised Phase (MLE):**
  - Huấn luyện $G$ bằng Cross-Entropy loss trên toàn bộ dataset (kể cả expert demonstrations) để model học cú pháp SQL cơ bản trước.
  - *Lưu ý Exposure Bias:* Pre-training với MLE tạo ra distribution mismatch khi chuyển sang adversarial phase (model quen với ground truth tokens, không quen với token tự sinh). Áp dụng **Scheduled Sampling** — dần dần thay thế ground truth tokens bằng token tự sinh trong quá trình pre-training.

- **Adversarial RL Loop — REINFORCE:**
  - Gradient update cho $G$:
    $$\nabla_\theta J(\theta) = \mathbb{E}_{\tau \sim \pi_\theta} \left[ \sum_{t=1}^{T} A(s_t, a_t) \nabla_\theta \log \pi_\theta(a_t | s_t) \right]$$
  - Cập nhật $D$ định kỳ (tỉ lệ $D:G = 5:1$) dựa trên mẫu thật từ dataset và mẫu giả từ $G$.
  - Reward Shaping: $r_{total} = \lambda_D \cdot D_\phi(x) + \lambda_{bypass} \cdot r_{bypass} + \lambda_{syntax} \cdot r_{syntax}$.

- **Kiểm soát Training Stability:**
  - Theo dõi **Gradient Norm** của $G$ và $D$ để phát hiện sớm mất ổn định.
  - Kiểm tra Mode Collapse: nếu variance của các batch sinh ra thấp bất thường → tăng Dropout hoặc thêm noise vào input.
  - Lưu checkpoint định kỳ — adversarial training có thể collapse đột ngột sau nhiều epoch ổn định.

---

## 🟦 Giai đoạn 5: Đánh Giá & Kiểm Thử

**Mục tiêu:** Đo lường ba chiều: Fidelity (chính xác), Diversity (đa dạng), Utility (hữu dụng thực tế).

- **Baseline để so sánh (bắt buộc):**
  - Baseline 1: Template-based generation (chèn ngẫu nhiên vào các mẫu cố định).
  - Baseline 2: Pure MLE Language Model (chỉ pre-training, không adversarial).
  - Baseline 3: SeqGAN vanilla (không có advantage estimation, không có reward shaping).
  - *Không có baseline thì mọi metric đều vô nghĩa.*

- **Syntax Validity Rate:**
  - Parse 1000 mẫu sinh ra bằng `sqlparse`. Mục tiêu: >90%.
  - *Lưu ý:* Ngưỡng cần được justify dựa trên use case hoặc prior work, không đặt tùy tiện.

- **Attack Success Rate (ASR) — Metric chính:**
  - Chạy payload qua ModSecurity (ruleset OWASP CRS cụ thể, ghi rõ version). Đây là metric quan trọng nhất.
  - Báo cáo ASR riêng cho từng loại tấn công (UNION-based, Boolean-based, v.v.).

- **Self-BLEU Score:**
  - Đo mức độ lặp lại nội bộ giữa các mẫu sinh ra. Score thấp = đa dạng cao.
  - So sánh với Self-BLEU của dataset gốc để có ngưỡng tham chiếu.

- **Reward Convergence:**
  - Theo dõi learning curve của reward trung bình theo epoch.
  - Nếu reward plateau sớm mà ASR thấp → model học "giống SQL" chứ không học bypass.

---

## 🟪 Giai đoạn 6: Đóng Gói & Tài Liệu Hóa

**Mục tiêu:** Đóng gói kết quả để có thể tái hiện và mở rộng.

- **Model Serialization:**
  - Lưu checkpoint của $G$ và $D$ kèm theo metadata: epoch, reward tốt nhất, hyperparameter configuration.
  - Export $G$ sang ONNX nếu cần inference nhẹ.

- **Inference API (Flask/FastAPI):**
  - Endpoint `POST /generate` nhận: `seed_token`, `num_samples`, `temperature`.
  - Trả về: danh sách payload kèm score từ $D$ và kết quả syntax check.
  - *Scope của giai đoạn này:* Phục vụ mục đích research demo và evaluation, không phải production deployment.

- **Reproducibility Package:**
  - `requirements.txt` với version đầy đủ.
  - Script `train.sh` với hyperparameter mặc định đã reproduce kết quả trong báo cáo.
  - Dataset split cố định (seed) để đảm bảo kết quả đánh giá có thể so sánh.

- **Tài liệu hóa Giới Hạn (Limitations):**
  - Model overfit vào ModSecurity ruleset cụ thể — chưa chứng minh generalization sang WAF khác.
  - Benchmark không reproducible nếu ruleset được cập nhật — ghi rõ version ruleset đã dùng.
  - Exposure bias từ MLE pre-training chưa được loại bỏ hoàn toàn.

---

## Phụ Lục: Ánh Xạ Toán Học

| Khái niệm | Vai trò trong hệ thống |
|---|---|
| Policy Gradient / REINFORCE | Cơ chế cập nhật trọng số $G$ |
| Advantage Function $A(s, a)$ | Giảm variance của gradient estimate |
| Lipschitz Continuity (WGAN-GP) | Ổn định training $D$ |
| Scheduled Sampling | Giảm exposure bias khi chuyển phase |
| Monte Carlo Roll-out | Ước lượng $Q$-value cho intermediate token |
| Sparse Reward | Vấn đề cốt lõi: WAF chỉ cho phản hồi ở cuối chuỗi |
