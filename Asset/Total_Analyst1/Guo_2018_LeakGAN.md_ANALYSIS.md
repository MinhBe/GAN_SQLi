# Phân Tích Bài Báo Khoa Học: Long Text Generation via Adversarial Training with Leaked Information

> Nguồn phân tích: `Asset/Total_OCR1/Guo_2018_LeakGAN.md`  
> Tạo bằng workflow `transcript-analysis` — Scientific Paper Hybrid Framework A-I.  
> Ghi chú: Đây là analysis mới vì chưa có file tương ứng trong `Asset/Total_Analyst`.

---

## Core Question
**LeakGAN xử lý sparse reward trong text GAN bằng cách cho Discriminator leak feature trung gian cho Generator.**

---

## Phần A: Thông Tin Cơ Bản & Phân Loại

| Mục | Nội dung |
|-----|----------|
| **Tên bài báo** | Long Text Generation via Adversarial Training with Leaked Information |
| **Tác giả** | Jiaxian Guo et al. |
| **Năm** | 2018 |
| **Loại tài liệu** | Text GAN / hierarchical RL |
| **Nguồn OCR** | `Guo_2018_LeakGAN.md` |

### A1. GAN / ML Taxonomy

| Thuộc tính | Nhận định |
|------------|----------|
| **Vai trò trong dự án** | Tài liệu liên quan đến GAN/sequence generation. Cần phân biệt rõ kỹ thuật ổn định huấn luyện với bằng chứng nó thắng MLE trong bài toán SQLi. |
| **Kỹ thuật chính nhận diện từ OCR** | Monte Carlo rollout cho reward từng bước, Generator-Discriminator adversarial loop |
| **Mức liên quan với GAN_SQLi** | Cao |

---

## Phần B: Dữ Liệu — Data Pipeline Deep-Dive

Synthetic data, COCO image captions và text generation tasks.

**Đoạn abstract/OCR đầu vào đáng chú ý:**

> Automatically generating coherent and semantically mean- ingful text has many applications in machine translation, di- alogue systems, image captioning, etc. Recently, by com- bining with policy gradient, Generative Adversarial Nets (GAN) that use a discriminative model to guide the train- ing of the generative model as a reinforcement learning pol- icy has shown promising results in text generation. However, the scalar guiding signal is only available after the entire text has been generated and lacks intermediate information about text structure during the generative process. As such, it lim- its its success when the length of the generated text samples is long (more than 20 words). In this paper, we propose a new framework, called LeakGAN, to address the problem for long text generation. We allow the discriminative net to leak its own high-level extracted features to the generative ne

---

## Phần C: Kiến Trúc Mô Hình — Architecture Blueprint

Generator tách thành Manager và Worker; Manager nhận feature từ Discriminator, tạo goal vector; Worker sinh token theo goal.

---

## Phần D: Training Configuration

Huấn luyện adversarial dựa trên policy gradient, dùng signal rò rỉ từ D thay vì chỉ reward cuối chuỗi.

---

## Phần E: Beyond Baselines — X-Factor

X-Factor là leaked high-level features giúp có reward/định hướng dày hơn cho long sequence.

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

Cải thiện long text generation so với SeqGAN, đặc biệt khi chuỗi dài và reward cuối chuỗi quá thưa.

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
Có thể là future work nếu MLE SQLi thất bại ở long payload, nhưng chi phí/tuning cao và không nên mở lại GAN khi chưa có gate mới.

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
