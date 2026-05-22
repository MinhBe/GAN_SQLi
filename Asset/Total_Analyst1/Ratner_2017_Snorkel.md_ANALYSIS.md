# Phân Tích Bài Báo Khoa Học: Snorkel: Rapid Training Data Creation with Weak Supervision

> Nguồn phân tích: `Asset/Total_OCR1/Ratner_2017_Snorkel.md`  
> Tạo bằng workflow `transcript-analysis` — Scientific Paper Hybrid Framework A-I.  
> Ghi chú: Đây là analysis mới vì chưa có file tương ứng trong `Asset/Total_Analyst`.

---

## Core Question
**Snorkel cho phép tạo training labels bằng labeling functions thay vì gán nhãn thủ công từng mẫu, rồi mô hình hóa noise/correlation giữa các nguồn nhãn.**

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | Snorkel: Rapid Training Data Creation with Weak Supervision |
| **Tác giả** | Alexander Ratner et al. |
| **Năm** | 2017 |
| **Loại tài liệu** | Weak supervision / data programming |
| **Nguồn OCR** | `Ratner_2017_Snorkel.md` |

### A1. GAN / ML Taxonomy

| Thuộc tính | Nhận định |
|------------|----------|
| **Vai trò trong dự án** | Tài liệu hỗ trợ data/label/tokenization. Đây là nền móng để tránh label noise, duplicate leakage và tokenization mất semantics. |
| **Kỹ thuật chính nhận diện từ OCR** | weak supervision / labeling functions |
| **Mức liên quan với GAN_SQLi** | Cao |

---

## Phần B: Dữ Liệu — Data Pipeline Deep-Dive

Nhiều case study với domain experts, gồm biomedical, enterprise và relation extraction tasks.

**Đoạn abstract/OCR đầu vào đáng chú ý:**

> Snorkel: Rapid Training Data Creation with Weak Supervision Alexander Ratner Stephen H. Bach Henry Ehrenberg Jason Fries Sen Wu Christopher R´e Stanford University Stanford, CA, USA {ajratner, bach, henryre, jfries, senwu, chrismre}@cs.stanford.edu ABSTRACT Labeling training data is increasingly the largest bottleneck in deploying machine learning systems. We present Snorkel, a ﬁrst-of-its-kind system that enables users to train state- of-the-art models without hand labeling any training data. Instead, users write labeling functions that express arbi- trary heuristics, which can have unknown accuracies and correlations. Snorkel denoises their outputs without ac-

---

## Phần C: Kiến Trúc Mô Hình — Architecture Blueprint

Labeling functions -> label matrix -> generative label model -> discriminative end model.

---

## Phần D: Training Configuration

Học accuracy và correlation của labeling functions không cần ground truth đầy đủ; sau đó train model downstream bằng probabilistic labels.

---

## Phần E: Beyond Baselines — X-Factor

X-Factor là biến heuristic/proxy labels thành weak supervision có hiệu chuẩn thay vì tin từng rule riêng lẻ.

---

## Phần F: Ablation & Experiments

- Cần ưu tiên đọc các bảng experiment, metric và setting train/test trước khi đưa paper vào luận văn.
- Nếu paper chỉ báo cáo một best run hoặc thiếu seed/CI, không nên dùng để biện minh cho quyết định kiến trúc chính.
- Với bài liên quan GAN, cần hỏi: kỹ thuật đó xử lý **mode collapse**, **D saturation**, hay chỉ cải thiện metric phụ?

---

## Phần G: Stability & Mode Collapse

- Nếu paper dùng GAN/WGAN/SeqGAN, cần kiểm tra có đo collapse bằng unique ratio, entropy, self-BLEU, coverage hoặc seed variance hay không.
- Nếu không có collapse diagnostic, paper chỉ nên được dùng làm related work hoặc ý tưởng phụ.
- Trong bối cảnh GAN_SQLi, mọi kỹ thuật adversarial phải vượt MLE frontier qua gate đã đăng ký trước.

---

## Phần H: Kết Quả & Đánh Giá

Giảm thời gian tạo data và tăng performance so với hand-labeling giới hạn trong nhiều case study.

---

## Phần I: Đánh Giá Cá Nhân

### I1. Điểm mạnh
- Paper bổ sung một mảnh ghép hữu ích cho hệ thống GAN_SQLi: hoặc ở tầng domain SQLi, hoặc ở tầng data/label, hoặc ở tầng sequence/GAN training.
- Có thể dùng để làm related work nếu ghi rõ phạm vi áp dụng và giới hạn.

### I2. Điểm yếu / Phản biện
- Không nên suy diễn rằng kỹ thuật trong paper sẽ tự động giải quyết collapse trên SQLi discrete payload.
- Cần tách bằng chứng paper khỏi bằng chứng thực nghiệm nội bộ Phase 2/3/3.5.
- Nếu OCR có lỗi hoặc thiếu bảng, phải quay lại PDF trước khi trích số liệu.

### I3. Áp dụng cho GAN_SQLi
Rất phù hợp Phase 05 của GAN_SQLi: rule labeler, DB detector, syntax checker, LLM review đều nên là labeling functions có confidence, không phải ground truth tuyệt đối.

---

## 3-Tier Explanation

### 1. Cấp độ Trẻ em
Paper này giống như một mảnh bản đồ. Nó không tự xây toàn bộ hệ thống, nhưng giúp ta biết nên tránh đường nào và nên đi qua vùng nào khi xây mô hình sinh payload SQLi.

### 2. Cấp độ Sinh viên
Giá trị của paper nằm ở việc chỉ ra một cơ chế kỹ thuật hoặc một bối cảnh dữ liệu cụ thể. Khi áp dụng vào GAN_SQLi, cần chuyển cơ chế đó sang pipeline có kiểm soát: dữ liệu sạch, nhãn có confidence, evaluator độc lập và so sánh với MLE baseline.

### 3. Cấp độ Chuyên gia
Paper chỉ nên ảnh hưởng đến quyết định kiến trúc nếu cơ chế của nó tương thích với dữ liệu rời rạc, điều kiện tài nguyên RTX 3050 6GB, và protocol chống cherry-pick. Nếu không, nó vẫn có giá trị related work nhưng không đủ để mở lại nhánh GAN chính.

---

## Misconception Seeds
1. **Lầm tưởng**: Paper có GAN là đủ để chứng minh nên dùng GAN cho SQLi.  
   **Sự thật**: Cần chứng minh bằng frontier, multi-seed và verified metrics trên chính dữ liệu SQLi.
2. **Lầm tưởng**: Metric trên dataset khác có thể chuyển nguyên sang SQLi payload.  
   **Sự thật**: SQLi có ràng buộc cú pháp, DB dialect, context injection và WAF behavior riêng.

---

## Transfer Question
**Nếu lấy cơ chế chính của paper này đưa vào GAN_SQLi, metric nào trên verified_dev sẽ chứng minh nó thật sự cải thiện chất lượng thay vì chỉ tăng proxy score?**
