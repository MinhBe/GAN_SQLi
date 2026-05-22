# 11 — Phản biện kế hoạch triển khai (nhánh VAE-GAN)

> **Ngày:** 2026-05-22 · **Vai trò:** đánh giá phản biện *bộ kế hoạch 00–10* trong thư mục này. Kế hoạch đã hấp thụ tốt phản biện ở `../02` và `../03` (pure-VAE trước, adversarial có gate, MI controllability, tải paper nền). File này tìm **lớp vấn đề tiếp theo** còn tồn đọng / cần làm lại / cần xem xét. Mỗi vấn đề kèm **tối thiểu 5 nguyên nhân & góc nhìn**.

---

## Nhận xét tổng quan (mặt được)

Kế hoạch mạnh ở: (1) đặt **pure-VAE + posterior-collapse gate** đứng trước adversarial [`02_De_Risk_Pure_VAE_Slice.md:60-79`](02_De_Risk_Pure_VAE_Slice.md); (2) tách ba gate G0/G1/G2 không gộp composite [`03_Decision_Gate.md:7-15`](03_Decision_Gate.md); (3) mở đường unsupervised-MI để né nhãn yếu [`05_Label_Condition_Calibration.md:36-55`](05_Label_Condition_Calibration.md); (4) ablation A0–A4 buộc adversarial phải thắng pure-VAE [`08_VAE_GAN_Adversarial_Challenger.md:54-64`](08_VAE_GAN_Adversarial_Challenger.md). Sáu vấn đề dưới đây là chỗ kế hoạch chưa đứng vững.

---

## VĐ-1 — Kế hoạch **tự khóa mình**: kỹ thuật chống posterior-collapse (free-bits, KL-annealing) bị hoãn "đến khi có paper", nhưng Phase 02/07 *cần* chúng để chạy

Phase 02 và 07 phải tránh posterior collapse, nhưng kế hoạch ghi free-bits/KL-annealing "chỉ đưa vào claim chính thức sau khi bổ sung paper nền" [`02_De_Risk_Pure_VAE_Slice.md:41`](02_De_Risk_Pure_VAE_Slice.md) [`07_Pure_VAE_Warmup_And_MI.md:26`](07_Pure_VAE_Warmup_And_MI.md), trong khi paper Bowman/Kingma lại chưa có trong corpus [`10_Literature_And_Implementation_Roadmap.md:11-18`](10_Literature_And_Implementation_Roadmap.md). Cần làm lại: tách "cần paper để TRÍCH DẪN" khỏi "cần paper để DÙNG".

**Nguyên nhân & góc nhìn:**
1. **Phụ thuộc vòng:** Phase 02 cần free-bits để qua G0 (chống KL→0), nhưng kế hoạch hoãn free-bits chờ paper → Phase 02 không khởi động được.
2. **Nhầm "dùng" với "trích":** free-bits/KL-anneal là kỹ thuật chuẩn, cài được từ công thức mà không cần paper trong tay; chặn dùng vì chưa có paper là **chặn nhầm**.
3. **Không có phương án dự phòng nếu tải paper thất bại:** Larsen/Bowman/Higgins có thể bị tường phí/không tải được → toàn nhánh treo.
4. **KPI headline phụ thuộc paper vắng:** metric disentanglement (β-VAE/Higgins) là thước đo controllability chính; nếu không có Higgins, **KPI không định nghĩa được**.
5. **Rủi ro lịch:** front-load việc săn paper trước mọi tiến triển mô hình → có thể đốt thời gian đầu mà không có kết quả chạy nào.
6. **Có nguồn thay thế trong corpus chưa được tận dụng:** survey text-GAN/ARAE [`03_Phan_Tich_Sau_Tu_Paper.md:52-58`](..\03_Phan_Tich_Sau_Tu_Paper.md) có thể tạm làm chỗ dựa lý thuyết cho latent-adversarial trong khi chờ paper gốc — kế hoạch chưa nói cách bắc cầu này.

---

## VĐ-2 — "Hai đường controllability" (supervised vs unsupervised MI) là **quyết định bị hoãn**, lan ambiguity xuống Phase 05/07/08 và **nhân đôi khối lượng**

Phase 05/07/08 đều rẽ nhánh "nếu nhãn đủ sạch → A, không thì B" [`05_Label_Condition_Calibration.md:14-55`](05_Label_Condition_Calibration.md) [`07_Pure_VAE_Warmup_And_MI.md:44-51`](07_Pure_VAE_Warmup_And_MI.md). Kế hoạch không bao giờ chốt, nên mọi phase sau phải hỗ trợ cả hai. Cần xem xét: chốt sớm bằng một phép đo readiness định lượng, hoặc thừa nhận chỉ làm B.

**Nguyên nhân & góc nhìn:**
1. **Gấp đôi bề mặt thực thi:** ba phase phải code/đo cho cả A lẫn B → tốn gấp đôi cho một người/6GB.
2. **Tiêu chí chuyển A/B là TBD:** "nhãn đủ sạch" là ngưỡng để trống → quyết định lại trượt về sau.
3. **Đường B có thể không cho gì:** factor unsupervised có thể không khớp technique; "post-hoc alignment" có thể *thất bại*, để lại **không có claim controllability nào** — nhưng kế hoạch trình B như lưới an toàn chắc chắn.
4. **Đường A có thể bất khả thi ngay từ dữ liệu:** verified chỉ 504/468 [`05_Label_Condition_Calibration.md:9`](05_Label_Condition_Calibration.md) — đủ để *đánh giá* chứ khó *huấn luyện* một conditional VAE; nên A có thể chết vì thiếu dữ liệu train.
5. **Chưa dự đoán factor mà B sẽ tìm thấy:** trên SQLi, MI không giám sát nhiều khả năng bắt độ dài/đếm keyword/template — có thể tiên liệu và kiểm trước, kế hoạch chưa làm.
6. **MI không "miễn phí" như InfoGAN nói:** InfoGAN tuyên bố MI "comes for free" trên *ảnh* [`03_Phan_Tich_Sau_Tu_Paper.md:34-36`](..\03_Phan_Tich_Sau_Tu_Paper.md); với VAE text rời rạc nhỏ + thêm adversarial = 3–4 mục tiêu tương tác, cân bằng chưa ai nghiên cứu → không thể giả định free.

---

## VĐ-3 — Novelty headline là "latent interpolation/disentanglement", nhưng kế hoạch **không định nghĩa thế nào là một interpolation HỢP LỆ của payload SQL** — và miền này có thể không hỗ trợ nó

`00` đặt interpolation/disentanglement là lý do tồn tại của nhánh [`00_Tong_Quan_Kien_Truc_VAE_GAN.md:84-86`](00_Tong_Quan_Kien_Truc_VAE_GAN.md); gate G1 đòi "latent traversal tạo payload còn hợp lệ ở tỷ lệ đáng kể" [`02_De_Risk_Pure_VAE_Slice.md:69`](02_De_Risk_Pure_VAE_Slice.md). Nhưng nội suy latent giữa hai payload (ví dụ UNION-based ↔ time-based) **không có điểm giữa hợp lệ hiển nhiên**. Cần xem xét: biến interpolation từ "năng lực giả định" thành "câu hỏi nghiên cứu".

**Nguyên nhân & góc nhìn:**
1. **SQL rời rạc/cấu trúc:** "điểm giữa" của hai payload thường **sai cú pháp** — không có đảm bảo liên tục như ảnh.
2. **KPI có thể ≈ 0 do bản chất miền:** "interpolation validity" có thể gần 0 → novelty headline *không đo được*, không phải do model kém.
3. **Ngưỡng "tỷ lệ đáng kể" để trống:** không cam kết con số, và miền có thể không đỡ nổi bất kỳ tỷ lệ nào.
4. **Nhãn của payload nội suy không xác định:** kể cả hợp cú pháp, technique của điểm giữa là gì? → controllability-của-interpolation là bài toán ill-posed.
5. **Phép loại suy InfoGAN/ảnh không chuyển được:** xoay/độ rộng chữ số là thuộc tính *liên tục thị giác*; SQL không có trục liên tục tương tự [`03_Phan_Tich_Sau_Tu_Paper.md:39-48`](..\03_Phan_Tich_Sau_Tu_Paper.md).
6. **Không có tiền lệ trong corpus** cho thấy nội suy latent ra SQL hợp lệ → claim đang dựa vào kỳ vọng; nên hạ thành RQ có thể trả lời "không".

---

## VĐ-4 — Mâu thuẫn nội tại: **decoder cố tình yếu** (chống collapse) >< **gate reconstruction phải cao**

Để chống posterior collapse, kế hoạch yêu cầu "decoder nhỏ hơn anchor MLE" [`02_De_Risk_Pure_VAE_Slice.md:37`](02_De_Risk_Pure_VAE_Slice.md) [`07_Pure_VAE_Warmup_And_MI.md:12`](07_Pure_VAE_Warmup_And_MI.md); đồng thời G0 đòi "reconstruction >= ngưỡng đăng ký" [`02_De_Risk_Pure_VAE_Slice.md:65`](02_De_Risk_Pure_VAE_Slice.md). Hai yêu cầu kéo ngược nhau mà kế hoạch không nêu chính sách hòa giải. Cần làm lại: thay ngưỡng vô hướng bằng một frontier recon↔KL↔capacity, và kiểm vùng pass có rỗng không.

**Nguyên nhân & góc nhìn:**
1. **Đối kháng trực tiếp:** decoder yếu ↓ reconstruction; G0 cần reconstruction ↑ → không có chính sách giải.
2. **Ngưỡng 70% (ở `00` gốc) có thể bất khả thi:** với decoder cố tình nhỏ trên partial-delex, đạt recon cao là khó.
3. **Vùng pass có thể rỗng:** `KL∈[5,50]` ∧ `recon≥70%` ∧ `active-dims>min` có thể không có cấu hình nào thỏa trên 6GB → gate "không bao giờ qua".
4. **Chưa có pilot kiểm vùng pass không rỗng** trước khi cam kết ba ngưỡng đồng thời.
5. **Lối thoát free-bits bị hoãn (VĐ-1):** free-bits cho phép giữ decoder mạnh mà vẫn không collapse — nhưng đang bị chặn → kẹt ở nhánh "decoder yếu".
6. **Bản chất đa mục tiêu:** recon vs KL vs capacity là tradeoff, cần đường Pareto, không phải ba ngưỡng vô hướng rời rạc.

---

## VĐ-5 — Lỗi nền nội bộ: **ngưỡng pre-registered để trống** + **đảo thứ tự evaluator**

Gate khắp nơi ghi "ngưỡng đăng ký" [`03_Decision_Gate.md:23-29`](03_Decision_Gate.md) [`07_Pure_VAE_Warmup_And_MI.md:57-65`](07_Pure_VAE_Warmup_And_MI.md), và Phase 02 dùng metric (KL, active-dims, round-trip, latent traversal) [`02_De_Risk_Pure_VAE_Slice.md:46-56`](02_De_Risk_Pure_VAE_Slice.md) trong khi evaluator chỉ được định nghĩa ở Phase 06 [`06_Evaluator_And_Model_Separation.md:8-48`](06_Evaluator_And_Model_Separation.md). Cần một protocol đặt-ngưỡng riêng cho nhánh VAE-GAN và sửa thứ tự phụ thuộc.

**Nguyên nhân & góc nhìn:**
1. **Đảo phụ thuộc:** Phase 02 de-risk cần các metric mà Phase 06 mới dựng.
2. **"posterior-collapse indicator" chưa định nghĩa:** là giá trị KL? số active-dim? hay tổng hợp? [`06_Evaluator_And_Model_Separation.md:21-27`](06_Evaluator_And_Model_Separation.md) — không nói.
3. **"near-copy không tăng bất thường" thiếu baseline:** "bất thường" so với mức nào?
4. **Số seed cho VAE chưa cam kết:** chỉ ghi "robustness across seeds" [`09_Final_Evaluation_And_Delivery.md:40`](09_Final_Evaluation_And_Delivery.md), chưa chốt mức tối thiểu cho pilot và confirmatory run.
5. **Không hiệu chỉnh đa so sánh:** bốn nhóm metric × nhiều model A0–A4 × seed → dương tính giả nếu không Holm/Bonferroni.
6. **"frontier đã đăng ký" cho G2** [`03_Decision_Gate.md:62`](03_Decision_Gate.md) chưa liệt kê trục/điểm cụ thể.

---

## VĐ-6 — Câu hỏi tồn tại chưa trả lời: **VAE-GAN thắng bằng chiều nào?**

Kế hoạch thừa nhận phải "pre-commit metric interpolation" [`03_Phan_Tich_Sau_Tu_Paper.md:60-67`](..\03_Phan_Tich_Sau_Tu_Paper.md) nhưng chưa chốt điều kiện thắng chính của nhánh. Nếu interpolation/disentanglement bất khả đo (VĐ-3), nhánh phải có một novelty thay thế rõ ràng; nếu không, VAE-GAN dễ trở thành mô hình nặng nhưng claim yếu.

**Nguyên nhân & góc nhìn:**
1. **Nếu interpolation/disentanglement là cái duy nhất VAE-GAN thêm, mà nó lại khả nghi (VĐ-3)** → lý do tồn tại của nhánh mong manh.
2. **Condition generation chưa đủ làm novelty nếu latent không được dùng thật** → VAE-GAN phải thắng ở một chiều *quan trọng với luận văn*, chiều đó chưa định nghĩa.
3. **Ưu thế "privacy/anti-memorization" (theo Xu) được nhắc nhưng không có test privacy** [`10_Literature_And_Implementation_Roadmap.md:54`](10_Literature_And_Implementation_Roadmap.md) → không claim được.
4. **MI controllability không tự chứng minh latent có ý nghĩa:** cần đo alignment, traversal và active dimensions, không chỉ loss giảm.
5. **Luận văn cần một centerpiece bảo vệ được:** chạy VAE-GAN nặng dễ xé nhỏ nguồn lực nếu không có điều kiện thắng.
6. **Không có tiêu chí dừng nhánh VAE-GAN** dù chính kế hoạch thừa nhận nhánh này rủi ro cao nhất [`00_Tong_Quan_Kien_Truc_VAE_GAN.md:84-86`](00_Tong_Quan_Kien_Truc_VAE_GAN.md).

---

## Vấn đề xuyên suốt của nhánh VAE-GAN

1. **Nhiều việc lớn song song, một người, một 6GB:** paper, label, partial-delex, evaluator, pure-VAE, MI và adversarial đều cạnh tranh thời gian/compute.
2. **Lỗi đảo thứ tự evaluator** (gate dùng metric trước Phase 06).
3. **Ngưỡng để trống** → cần *threshold-setting protocol* cho riêng nhánh VAE-GAN (đặt ngưỡng từ baseline/dev, khóa trước train).
4. **"Tái dùng nền V5" nói lỏng:** chưa có hợp đồng artifact dùng chung (tên file/schema/version).
5. **Thiếu tiêu chí dừng cả nhánh:** mỗi phase có stop-rule, nhưng không có điều kiện "đóng nhánh để dồn nguồn lực" nếu gate sớm thất bại.

---

## Tóm tắt việc cần làm lại / xem xét (theo độ ưu tiên)

```text
P0  Gỡ khóa: phân biệt "dùng" vs "trích" free-bits/KL-anneal; cho phép dùng ngay, trích sau (VĐ-1)
P0  Hạ interpolation/disentanglement thành RQ có thể trả lời "không"; định nghĩa "interpolation hợp lệ" hoặc đổi novelty (VĐ-3)
P0  Kiểm vùng pass G0 không rỗng (recon↔KL↔capacity) bằng pilot trước khi cam kết ngưỡng (VĐ-4)
P1  Chốt A/B controllability bằng một phép đo readiness định lượng; thừa nhận nếu chỉ làm được B (VĐ-2)
P1  Threshold-setting protocol + sửa thứ tự evaluator + số seed + đa so sánh (VĐ-5)
P1  Định nghĩa điều kiện thắng và tiêu chí bỏ nhánh (VĐ-6)
P2  Tài liệu phân bổ nguồn lực nội bộ + hợp đồng artifact dùng chung
```
