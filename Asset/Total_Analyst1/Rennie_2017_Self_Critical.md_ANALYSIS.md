# Phân Tích Bài Báo Khoa Học: Self-critical Sequence Training for Image Captioning

> Nguồn phân tích: `Asset/Total_OCR1/Rennie_2017_Self_Critical.md`  
> Tạo bằng workflow `transcript-analysis` — Scientific Paper Hybrid Framework A-I.  
> Ghi chú: Đây là analysis mới vì chưa có file tương ứng trong `Asset/Total_Analyst`.

---

## Core Question
**SCST dùng output greedy/test-time của chính mô hình làm baseline cho REINFORCE, giúp tối ưu metric không khả vi như CIDEr.**

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | Self-critical Sequence Training for Image Captioning |
| **Tác giả** | Steven J. Rennie et al. |
| **Năm** | 2017 |
| **Loại tài liệu** | Sequence RL / REINFORCE baseline improvement |
| **Nguồn OCR** | `Rennie_2017_Self_Critical.md` |

### A1. GAN / ML Taxonomy

| Thuộc tính | Nhận định |
|------------|----------|
| **Vai trò trong dự án** | Tài liệu liên quan đến GAN/sequence generation. Cần phân biệt rõ kỹ thuật ổn định huấn luyện với bằng chứng nó thắng MLE trong bài toán SQLi. |
| **Kỹ thuật chính nhận diện từ OCR** | Không trích được keyword chắc chắn từ OCR; cần đọc thủ công phần methodology. |
| **Mức liên quan với GAN_SQLi** | Trung bình / hỗ trợ |

---

## Phần B: Dữ Liệu — Data Pipeline Deep-Dive

MSCOCO image captioning.

**Đoạn abstract/OCR đầu vào đáng chú ý:**

> Recently it has been shown that policy-gradient methods for reinforcement learning can be utilized to train deep end- to-end systems directly on non-differentiable metrics for the task at hand. In this paper we consider the problem of opti- mizing image captioning systems using reinforcement learn- ing, and show that by carefully optimizing our systems us- ing the test metrics of the MSCOCO task, signiﬁcant gains in performance can be realized. Our systems are built using a new optimization approach that we call self-critical se- quence training (SCST). SCST is a form of the popular RE- INFORCE algorithm that, rather than estimating a “base- line” to normalize the rewards and reduce variance, utilizes the output of its own test-time inference algorithm to nor- malize the rewards it experiences. Using this approach, es- timating the reward signal (as actor-critic methods must do) and esti

---

## Phần C: Kiến Trúc Mô Hình — Architecture Blueprint

Captioning model được fine-tune bằng policy gradient; reward là metric captioning trực tiếp.

---

## Phần D: Training Configuration

Advantage = reward(sample) - reward(greedy baseline), giảm variance mà không cần critic riêng.

---

## Phần E: Beyond Baselines — X-Factor

X-Factor là baseline tự phê bình gắn với inference procedure, tránh lệch giữa train-time và test-time.

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

Cải thiện CIDEr và đạt SOTA image captioning thời điểm đó.

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
Có thể dùng như controlled reward fine-tune cho MLE SQLi, nhưng không nên xem là thuốc chữa collapse nếu reward/evaluator chưa đáng tin.

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
