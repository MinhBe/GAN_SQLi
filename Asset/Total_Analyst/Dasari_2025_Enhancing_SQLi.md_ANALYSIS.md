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
