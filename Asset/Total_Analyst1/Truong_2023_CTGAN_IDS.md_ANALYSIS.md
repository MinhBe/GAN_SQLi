# PHÂN TÍCH CHI TIẾT ĐỒ ÁN: GAN-BASED IMBALANCED DATA INTRUSION DETECTION SYSTEM

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên báo cáo** | Hệ thống tìm kiếm, phát hiện và ngăn ngừa xâm nhập (GAN-based imbalanced data intrusion detection system) |
| **Tác giả** | Trương Thị Hoàng Hảo, Nguyễn Đức Trung, Lê Quang Minh, Nguyễn Việt Hoàng (Nhóm 5) |
| **Năm** | 2023 (Dựa trên mã môn học NT204) |
| **Trường** | Đại học Công nghệ Thông tin - ĐHQG TP.HCM |

### A1. Phân Loại GAN Taxonomy

| Thuộc tính | Lựa chọn |
|------------|----------|
| **GAN Type** | CTGAN (Conditional Tabular GAN) |
| **Architecture Family** | Fully-connected (MLP) |
| **Task Type** | Data Augmentation for Intrusion Detection |

---

## Phần B: Dữ Liệu — Data Pipeline Deep-Dive

### B1. Dataset Overview

| Thuộc tính | Mô tả |
|------------|-------|
| **Tên dataset** | CICIDS 2017 |
| **Đặc điểm** | Traffic bình thường chiếm >80%; các lớp thiểu số (Bot, Infiltration, Heartbleed) < 0.1% |
| **Kích thước mẫu tạo thêm** | 10,000 mẫu cho mỗi lớp hiếm |

### B3. Preprocessing Pipeline

| Bước | Chi tiết |
|------|----------|
| **Normalization** | Chuẩn hóa theo chế độ (Mode-specific normalization) để xử lý dữ liệu bảng không Gaussian |
| **Encoding** | Xử lý các cột rời rạc không cân bằng |
| **Handling imbalance** | [x] GAN-based Oversampling (CTGAN) |

---

## Phần C: Kiến Trúc Mô Hình — Architecture Blueprint

### C1. Tổng Quan Kiến Trúc
Quy trình: Dataset gốc -> Tiền xử lý -> CTGAN (học các lớp hiếm) -> Tạo mẫu mới -> Kết hợp dữ liệu (Gốc + GAN) -> Random Forest Classifier.

### C2. Generator (trong CTGAN)
- Sử dụng bộ sinh có điều kiện (conditional generator).
- Huấn luyện bằng cách lấy mẫu (training by sampling) dựa trên tần suất log của các danh mục.

### C3. Classifier (Random Forest)
- Thư viện: sklearn.
- Hyperparameters: `n_estimators = 100`, `random_state = 1`.

---

## Phần D: Kết Quả & Đánh Giá

### H1. Quantitative Results
- **Accuracy:** 99.87% (với CTGAN) so với 99.85% (với SMOTE).
- **Phân loại sai:** 1458 mẫu (CTGAN) so với 1588 mẫu (SMOTE).
- **Nhận xét:** CTGAN giúp mô hình tổng quan tốt hơn và tránh mất dữ liệu so với Random Undersampling + SMOTE.

### H3. Limitations
- Khả năng nhận diện lớp "Bot" và "Infiltration" vẫn còn thấp do dữ liệu gốc quá ít, không đủ thỏa mãn yêu cầu học của CTGAN (chất lượng mẫu ảo chỉ đạt 76.29% so với mẫu thật).

---

## Three-tier explanation

### Child (analogy)
Hãy tưởng tượng một thư viện có hàng triệu cuốn sách bình thường nhưng chỉ có vài cuốn sách cực hiếm về phép thuật. Nếu bạn muốn dạy một robot nhận ra sách hiếm, robot sẽ khó học vì có quá ít ví dụ. Nhóm sinh viên đã dùng một "máy photocopy thông minh" (CTGAN) để tạo ra thêm hàng ngàn cuốn sách tương tự sách hiếm đó. Nhờ vậy, robot có nhiều tài liệu để học tập hơn và trở nên giỏi hơn trong việc tìm kiếm sách hiếm.

### Student (mechanism)
Đồ án giải quyết vấn đề mất cân bằng dữ liệu trong bài toán phát hiện xâm nhập mạng (IDS) bằng cách sử dụng CTGAN (Conditional Tabular GAN). Khác với GAN thông thường cho hình ảnh, CTGAN được thiết kế riêng cho dữ liệu bảng (tabular) bằng cách sử dụng mode-specific normalization để xử lý các phân phối phức tạp. Sau khi tạo ra 10,000 mẫu ảo cho mỗi lớp hiếm (Bot, Infiltration, Heartbleed), dữ liệu này được trộn với tập huấn luyện gốc để huấn luyện mô hình Random Forest. Kết quả cho thấy phương pháp này cải thiện độ chính xác và giảm số lượng mẫu phân loại sai so với kỹ thuật SMOTE truyền thống.

### Expert (trade-offs)
Việc sử dụng CTGAN mang lại lợi thế vượt trội trong việc mô hình hóa các biến rời rạc và phân phối không Gaussian đặc trưng của traffic mạng. Tuy nhiên, một đánh đổi quan trọng được ghi nhận là "độ trung thực" của dữ liệu sinh ra. Khi kích thước mẫu cực nhỏ (như lớp Infiltration), Generator không thể học đủ đặc trưng để tái tạo mẫu chất lượng cao (chỉ đạt ~76% chất lượng). Điều này đặt ra câu hỏi về ranh giới giữa việc tăng cường dữ liệu và việc đưa thêm nhiễu (noise) vào mô hình. Giải pháp tiềm năng là kết hợp Autoencoder để giảm chiều dữ liệu trước khi qua GAN như nhóm đã đề xuất.

---

## Misconception seeds
- **Lầm tưởng:** GAN luôn tạo ra dữ liệu hoàn hảo giúp tăng độ chính xác lên 100%.
  - **Sự thật:** Chất lượng dữ liệu GAN phụ thuộc vào lượng dữ liệu gốc. Nếu dữ liệu gốc quá ít (như Bot/Infiltration), GAN có thể tạo ra các mẫu không đủ đặc trưng.
- **Lầm tưởng:** CTGAN và SMOTE hoạt động giống hệt nhau.
  - **Sự thật:** SMOTE tạo mẫu bằng cách nội suy giữa các điểm dữ liệu có sẵn (có thể gây chồng lấp lớp), trong khi CTGAN học phân phối xác suất của toàn bộ dữ liệu để sinh mẫu mới (linh hoạt và đa dạng hơn).

---

## Transfer question
Nếu chúng ta áp dụng mô hình này vào việc phát hiện tấn công SQL Injection (SQLi) trong các hệ thống ngân hàng - nơi dữ liệu tấn công cực kỳ hiếm so với truy vấn hợp lệ - chúng ta cần điều chỉnh cấu trúc CTGAN như thế nào để đảm bảo các mẫu SQLi sinh ra vẫn giữ được cấu trúc ngữ pháp (syntax) hợp lệ của SQL?

---

## Bổ Sung Của Codex — Kiểm Tra Lại Theo Total_OCR1 (2026-05-22)

> Phần này được append thêm vào cuối file theo yêu cầu, không xóa hoặc sửa nội dung analysis gốc của đồng nghiệp.  
> Nguồn kiểm tra bổ sung: `Asset/Total_OCR1/Truong_2023_CTGAN_IDS.md`.  
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
> Hệ thống tìm kiếm, phát hiện và ngăn ngừa xâm nhập Project Report Group 5 1 ĐẠI HỌC QUỐC GIA THÀNH PHỐ HỒ CHÍ MINH – VIỆT NAM ĐẠI HỌC CÔNG NGHỆ THÔNG TIN ---------- BÁO CÁO ĐỒ ÁN HỆ THỐNG TÌM KIẾM, PHÁT HIỆN VÀ NGĂN NGỪA XÂM NHẬP GAN-based imbalanced data intrusion detection system GIẢNG VIÊN HƯỚNG DẪN: ĐỖ HOÀNG HIỂN NT204.N21.ATCL – VN NHÓM 5: TRƯƠNG THỊ HOÀNG HẢO - 20520191 NGUYỄN ĐỨC TRUNG - 20520956 LÊ QUANG MINH - 20520245 NGUYỄN VIỆT HOÀNG – 20520189 --- Hệ thống tìm kiếm, phát hiện và ngăn ngừa xâm nhập Project Report

### 5. Quyết định sử dụng
- **Dùng được cho**: related work, thiết kế ablation, hoặc lập luận phụ tùy theo nhóm paper.
- **Chưa đủ cho**: kết luận rằng GAN sẽ thắng MLE trên SQLi nếu không có thực nghiệm nội bộ và decision gate mới.
