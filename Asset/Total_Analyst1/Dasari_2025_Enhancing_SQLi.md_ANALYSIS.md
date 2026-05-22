# Phân Tích Paper: Enhancing SQL Injection Detection and Prevention Using Generative Models

## Phần A: Thông Tin Cơ Bản & Phân Loại
- **Tiêu đề:** Enhancing SQL Injection Detection and Prevention Using Generative Models
- **Tác giả:** Naga Sai Dasari, Atta Badii, Armin Moin, Ahmed Ashlam
- **Năm xuất bản:** 2025
- **Phân loại:** Cybersecurity, SQL Injection (SQLi), Data Augmentation, Generative Models.
- **Từ khóa:** VAE, CWGAN-GP, U-Net, SQL Injection, FastText.

## Phần B: Dữ Liệu
- **Tập dữ liệu:** Lấy từ Kaggle (sqli csv và Modified SQL Dataset), bổ sung các kỹ thuật SQLi nâng cao (error-based, time-based, blind).
- **Đặc điểm:** Các truy vấn SQL (benign và malicious).
- **Tiền xử lý:** Token hóa tùy chỉnh, chuyển đổi truy vấn thành vector sử dụng **FastText** (được chứng minh là cân bằng nhất giữa độ chính xác và thời gian).

## Phần C: Kiến Trúc Mô Hình
- **VAE (Variational Autoencoder):** Dùng để trích xuất đặc trưng và giảm chiều dữ liệu (từ vector FastText xuống không gian tiềm ẩn 448 chiều).
- **Generative Models (Tăng cường dữ liệu):**
    - **U-Net:** capture các phụ thuộc cục bộ và toàn cục của chuỗi SQL.
    - **CWGAN-GP:** Sinh dữ liệu có điều kiện (nhãn benign/malicious) với Gradient Penalty để ổn định.
- **Classifier:** XGBoost (đạt hiệu suất cao nhất 99.40% so với SVM, RF, KNN).

## Phần D: Training Configuration
- **Hyperparameter Optimization:** Sử dụng framework **Optuna** (Tree-structured Parzen Estimator) để tìm bộ tham số tối ưu cho U-Net và CWGAN-GP.
- **Pseudo-labelling:** Dùng PCA để giảm chiều và KMeans clustering để gán nhãn giả cho dữ liệu tổng hợp.

## Phần E: Beyond Baselines
- Kết hợp dữ liệu thực với dữ liệu tổng hợp theo các tỷ lệ khác nhau.
- Tỷ lệ tối ưu được tìm thấy là: **80% dữ liệu U-Net + 70% dữ liệu CWGAN-GP** kết hợp với dữ liệu thực.

## Phần F: Ablation & Experiments
- So sánh các phương pháp embedding: FastText, BPE, BERT, Character-level.
- Đánh giá chất lượng dữ liệu sinh bằng các metric: BLEU score (0.99 cho U-Net), Cosine Similarity, Lowenstein Distance.

## Phần G: Stability & Mode Collapse
- CWGAN-GP giúp giải quyết vấn đề vanishing gradient và mode collapse khi xử lý các cấu trúc truy vấn SQL phức tạp.
- U-Net cho thấy sự ổn định vượt trội trong việc bảo toàn cấu trúc cú pháp của SQL.

## Phần H: Kết Quả & Đánh Giá
- Mô hình XGBoost cuối cùng đạt độ chính xác **98%** trên tập validation với Recall cho lớp tấn công (Class 1) được cải thiện đáng kể.
- Giảm thiểu cả False Positives và False Negatives thông qua việc đa dạng hóa tập huấn luyện.

## Phần I: Đánh Giá Cá Nhân
- **Ưu điểm:** Một quy trình cực kỳ hiện đại (VAE -> Generative Models -> Optuna -> XGBoost). Việc dùng U-Net cho dữ liệu 1D SQL là một sáng kiến thú vị.
- **Hạn chế:** Chi phí tính toán để sinh dữ liệu và huấn luyện VAE/GAN khá cao, khó triển khai thời gian thực trên các thiết bị yếu.

## Trích xuất kiến thức (Skill-style)
- **Core Question:** Làm thế nào để bắt được các biến thể SQL Injection "lạ" mà các hệ thống cũ thường bỏ sót?
- **3-tier explanation:**
    - **Child:** Giống như việc dạy một cảnh sát nhận mặt tội phạm. Thay vì chỉ đưa vài tấm ảnh cũ, chúng ta dùng máy tính để vẽ ra hàng triệu khuôn mặt tội phạm giả nhưng trông rất thật để cảnh sát luyện tập kỹ hơn.
    - **Student:** Paper sử dụng VAE để nén dữ liệu SQL, sau đó dùng U-Net và CWGAN-GP để tạo ra các biến thể tấn công mới. Những dữ liệu giả này được gán nhãn tự động bằng KMeans rồi trộn với dữ liệu thật để huấn luyện bộ phân loại XGBoost, giúp nó nhận diện được cả những mẫu tấn công chưa từng thấy.
    - **Expert:** Nghiên cứu đề xuất một kiến trúc hybrid độc đáo. VAE đóng vai trò trích xuất đặc trưng bậc cao (latent features). Việc áp dụng Gradient Penalty trong CWGAN đảm bảo tính liên tục Lipschitz, ngăn chặn mode collapse. U-Net với skip-connections giúp bảo toàn các đặc trưng cấu trúc phân cấp của ngôn ngữ SQL, điều mà các phương pháp nội suy đơn giản như SMOTE không làm được.
- **Misconception Seeds:** Nghĩ rằng chỉ cần dùng GAN là đủ (thực tế U-Net trong bài này còn tốt hơn); tin rằng nhãn của dữ liệu giả luôn luôn đúng (cần qua bước Pseudo-labelling).
- **Transfer Question:** Có thể áp dụng quy trình này để phát hiện các cuộc tấn công XSS (Cross-Site Scripting) không?

---

## Bổ Sung Của Codex — Kiểm Tra Lại Theo Total_OCR1 (2026-05-22)

> Phần này được append thêm vào cuối file theo yêu cầu, không xóa hoặc sửa nội dung analysis gốc của đồng nghiệp.  
> Nguồn kiểm tra bổ sung: `Asset/Total_OCR1/Dasari_2025_Enhancing_SQLi.md`.  
> Workflow tham chiếu: `transcript-analysis` — Scientific Paper Hybrid Framework A-I.

### 1. Quan điểm bổ sung
Tài liệu liên quan trực tiếp đến domain SQLi/WAF. Giá trị cao nhất nằm ở taxonomy, evaluator, mutation hoặc dữ liệu, không nhất thiết ở kiến trúc GAN.

Các tín hiệu kỹ thuật nổi bật đọc được từ OCR hiện tại:

- gradient penalty / Lipschitz constraint
- SQL Injection payload/domain
- oversampling cho class imbalance
- Generator-Discriminator adversarial loop

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
> JOURNAL OF CYBERSECURITY AND DATA SCIENCE, JANUARY 2025 1 Enhancing SQL Injection Detection and Prevention Using Generative Models Naga Sai Dasari Dept.of Computer Science, University of Reading, UK nagasai.dasari@reading.ac.uk Atta Badii Dept.of Computer Science, University of Reading, UK atta.badii@reading.ac.uk Armin Moin Dept.of Computer Science, University of Colorado Colorodo Springs,CO, USA amoin@uccs.edu Ahmed Ashlam Dept.of Computer Science, University of Reading, UK

### 5. Quyết định sử dụng
- **Dùng được cho**: related work, thiết kế ablation, hoặc lập luận phụ tùy theo nhóm paper.
- **Chưa đủ cho**: kết luận rằng GAN sẽ thắng MLE trên SQLi nếu không có thực nghiệm nội bộ và decision gate mới.
