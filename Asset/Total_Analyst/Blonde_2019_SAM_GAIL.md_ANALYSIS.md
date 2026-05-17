# Phân Tích Paper: A Survey on GAN Techniques for Data Augmentation to Address the Imbalanced Data Issues in Credit Card Fraud Detection

## Phần A: Thông Tin Cơ Bản & Phân Loại
- **Tiêu đề:** A Survey on GAN Techniques for Data Augmentation to Address the Imbalanced Data Issues in Credit Card Fraud Detection
- **Tác giả:** Emilija Strelcenia, Simant Prakoonwit
- **Năm xuất bản:** 2023
- **Phân loại:** Survey, Credit Card Fraud Detection, Imbalanced Learning, Data Augmentation.
- **Từ khóa:** Generative Adversarial Networks, Fraud detection, Synthetic data, Deep learning.

## Phần B: Dữ Liệu
- **Tập dữ liệu:** Credit, Loan, Adult, Cover-type, Intrusion (KDD), Tripadvisor, Yelp, và bộ dữ liệu 80 triệu giao dịch thực tế.
- **Đặc điểm:** Dữ liệu dạng bảng (tabular data), cực kỳ mất cân bằng (fraud là thiểu số).
- **Thách thức:** Bảo mật thông tin khách hàng, rò rỉ dữ liệu nhạy cảm.

## Phần C: Kiến Trúc Mô Hình
- **Các biến thể GAN được khảo sát:**
    - **Duo-GAN:** Hai mạng GAN chạy song song cho hai lớp khác nhau.
    - **CTAB-GAN:** Chuyên cho dữ liệu bảng, xử lý biến hỗn hợp và đuôi dài.
    - **OCAN:** GAN một lớp (one-class) chỉ dùng dữ liệu hợp lệ để huấn luyện.
    - **cWGAN:** GAN có điều kiện kết hợp Wasserstein loss và Gradient Penalty.
    - **ScoreGAN:** Tạo review giả có ngữ nghĩa chính xác dựa trên điểm số.

## Phần D: Training Configuration
- Đề cập đến sự tiến hóa của các hàm loss: từ Mini-max loss truyền thống đến Wasserstein loss, AC loss để tăng tính ổn định và chất lượng mẫu sinh ra.

## Phần E: Beyond Baselines
- GAN vượt trội hơn SMOTE và các kỹ thuật lấy mẫu truyền thống vì hiểu được cấu trúc ẩn của dữ liệu thay vì chỉ nội suy khoảng cách.
- GAN giúp tránh over-fitting và overlapping tốt hơn so với SMOTE.

## Phần F: Ablation & Experiments
- So sánh Precision, Recall, F1-score của nhiều mô hình GAN khác nhau trên các bộ dữ liệu chuẩn.
- GAN-RF đạt độ chính xác 99.83% trên tập dữ liệu được tăng cường.

## Phần G: Stability & Mode Collapse
- Khảo sát các kỹ thuật như mini-batch discrimination, gradient penalty và cấu trúc mạng mới để giải quyết mode collapse và mất ổn định khi huấn luyện.

## Phần H: Kết Quả & Đánh Giá
- Tổng hợp bảng so sánh hiệu suất: SDG GAN đạt Precision 0.9863, Tuned GAN đạt Accuracy 0.9996.
- Kết luận: GAN là công cụ mạnh mẽ để tái cân bằng dữ liệu tài chính mà vẫn bảo vệ được quyền riêng tư.

## Phần I: Đánh Giá Cá Nhân
- **Ưu điểm:** Khảo sát rất toàn diện các biến thể GAN hiện đại nhất cho dữ liệu dạng bảng và tài chính.
- **Hạn chế:** Chưa đi sâu vào chi phí tính toán và thời gian huấn luyện thực tế cho các tập dữ liệu khổng lồ.

## Trích xuất kiến thức (Skill-style)
- **Core Question:** Tại sao GAN lại hiệu quả hơn các phương pháp lấy mẫu truyền thống trong phát hiện gian lận thẻ tín dụng?
- **3-tier explanation:**
    - **Child:** Thay vì chỉ copy các ví dụ cũ, GAN giống như một họa sĩ học cách vẽ những bức tranh gian lận mới trông y như thật, giúp máy tính luyện tập bắt trộm tốt hơn.
    - **Student:** GAN học phân phối xác suất chung của dữ liệu thực. Trong khi SMOTE chỉ nội suy giữa các điểm lân cận, GAN có thể sinh ra các mẫu ở những vùng chưa có dữ liệu nhưng vẫn thuộc phân phối, giúp mô hình phân loại có khả năng tổng quát hóa cao hơn.
    - **Expert:** Bài báo tổng hợp các kiến trúc GAN chuyên biệt (như CTAB-GAN, OCAN) giải quyết các vấn đề đặc thù của dữ liệu tài chính: biến rời rạc/liên tục hỗn hợp, phân phối đuôi dài, và yêu cầu bảo mật thông tin cá nhân thông qua việc sinh dữ liệu tổng hợp.
- **Misconception Seeds:** Nghĩ rằng GAN chỉ dùng cho hình ảnh; nhầm lẫn rằng dữ liệu tổng hợp từ GAN luôn tốt hơn dữ liệu thực.
- **Transfer Question:** Làm thế nào để áp dụng OCAN (One-class Adversarial Nets) cho bài toán phát hiện xâm nhập mạng (IDS) khi không có mẫu tấn công?
