# 02 — Phản biện độc lập & bổ sung (nhánh VAE-GAN)

> **Ngày:** 2026-05-22 · **Vai trò:** file này **không thay** `00_Ke_Hoach_Tong_The.md` và `01_Danh_Gia_Trien_Khai_Co_Trich_Dan.md`.
> Nó là lớp **kiểm chứng + phản biện cứng + lấp lỗ hổng**, đọc *sau* hai file kia.
> Nguyên tắc: chỉ viết điều trỏ được tới dòng/nguồn cụ thể; phản biện xây dựng kể cả khi tiêu cực.

---

## 1. Đã kiểm chứng những gì

- `decision.json`, `gan_results.json`, `04_data_foundation_report.md` — khớp 100% với nguồn nội bộ đang dùng làm nền kiểm chứng. [`Guiding\Phase 3\eval\phase03\decision.json:2-4`](..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\Phase 2\eval\gan_results.json:3-9`](..\Guiding\Phase%202\eval\gan_results.json)
- `Dasari_2025` analysis khớp: VAE giảm vector FastText về **latent 448 chiều** (dòng 16), **CWGAN-GP + U-Net** (17-19), XGBoost **99.40%** (20), "compute cost cao, khó real-time trên thiết bị yếu" (44). [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:16-20`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md) [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:44`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md)
- Phase 5 ở `detector_only`, `verified_dev=504`, `verified_test=468`, `review_queue=5,360`; full progress `3,900,000/12,753,953` = `30.5788%`. [`Guiding\Phase 5\reports\05_full_label_system_report.md:4-20`](..\Guiding\Phase%205\reports\05_full_label_system_report.md) [`Guiding\Phase 5\logs\phase05_full_progress.json:4-10`](..\Guiding\Phase%205\logs\phase05_full_progress.json)

**Kết luận kiểm chứng:** trích dẫn của `01` chính xác. Phần dưới vá điểm mù logic, không sửa citation.

---

## 2. Năm phản biện cứng

### PB1 — Nhánh này **mang tên một phương pháp mà corpus của bạn chưa có paper nền**. Đây là lỗ hổng nghiêm trọng nhất.

`00` mục F.10 đề "nhấn `Larsen_2016_VAE_GAN` (gốc kiến trúc), Kingma VAE, `Bowman_2016` (KL annealing/posterior collapse), β-VAE". Nhưng đối chiếu toàn bộ `Asset/Total_OCR1` (55 file) và `Asset/Total_Analyst1`:

- **Không có** Larsen 2016 ("Autoencoding beyond pixels", paper VAE-GAN gốc).
- **Không có** Kingma & Welling 2014 (VAE gốc).
- **Không có** Bowman 2016 (KL-annealing / posterior collapse cho text — *chính xác* vấn đề `00` D.4 lo ngại).
- **Không có** Higgins β-VAE (disentanglement — *chính xác* metric controllability bạn cần ở RQ1).

[`Asset\Total_OCR1\TOTAL_OCR1_MANIFEST.md:9-12`](..\Asset\Total_OCR1\TOTAL_OCR1_MANIFEST.md) (55 file giữ lại; danh sách không chứa các tên trên.)

⇒ **Toàn bộ luận chứng VAE-GAN hiện đang dựa gián tiếp** vào: Dasari 2025 (thực chất là VAE-cho-feature + CWGAN-GP + U-Net, **không phải** VAE-GAN của Larsen — xem PB2) và Xu 2019 CTGAN/TVAE (dữ liệu **tabular**, không phải chuỗi rời rạc). Hai nguồn này **không** đủ để bảo vệ các claim cốt lõi của nhánh: posterior collapse, KL-annealing, free-bits, disentanglement.

**Khắc phục bắt buộc trước khi viết proposal:** tải Larsen 2016, Kingma 2014, Bowman 2016, Higgins 2017 (có skill `sci-paper-downloader`). Nếu không tải được, phải **hạ cấp** mọi mệnh đề trích các paper này thành "theo hiểu biết chung của lĩnh vực, chưa có nguồn trong corpus" — nếu không sẽ là citation rỗng, vi phạm chính nguyên tắc bạn đặt ra.

### PB2 — Dasari **không phải tiền lệ VAE-GAN** cho generator có điều khiển; trích nó như "bằng chứng VAE-GAN làm được" là lệch loại.

Đọc kỹ analysis: Dasari dùng VAE để **trích đặc trưng/giảm chiều** vector FastText (448-d), rồi U-Net + CWGAN-GP **tăng cường dữ liệu**, rồi XGBoost **phân loại** đạt 99.40%. [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:16-20`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md) Đây là **pipeline phát hiện/augmentation downstream**, không phải VAE-GAN sinh payload *có điều khiển latent* — chính là novelty bạn tuyên bố. Hai khác biệt chí mạng:

1. "99.40%" là **utility của classifier downstream**, *không* chứng minh generator không collapse hay latent có disentangle. `01` bước 5 đã cảnh báo điều này — giữ nguyên cảnh báo, đừng để 99.40% xuất hiện như điểm mạnh của VAE-GAN.
2. Dasari sinh trên **vector liên tục** (FastText embedding), không sinh chuỗi token SQL hợp lệ trực tiếp; vấn đề relex/round-trip của bạn (`round_trip_status=not_evaluated`) không tồn tại trong setup của họ. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:72`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

### PB3 — Novelty cốt lõi (controllability) **được xây trên thành phần yếu nhất của nền** (nhãn).

`00` đặt controllability (RQ1/RQ2: latent tách kiểu attack, conditional accuracy theo `technique_primary`) làm "novelty mạnh nhất 3 nhánh" (B, D.6). Nhưng:

- Phase 5 mới `detector_only`, **30.58%** dòng, `verified_dev=504`/`test=468`, `review_queue=5,360`. [`Guiding\Phase 5\reports\05_full_label_system_report.md:4-20`](..\Guiding\Phase%205\reports\05_full_label_system_report.md) [`Guiding\Phase 5\logs\phase05_full_progress.json:4-10`](..\Guiding\Phase%205\logs\phase05_full_progress.json)
- `db_hint` 78% unknown; `error_based` chỉ 405 mẫu (`00` D.3).
- InfoGAN-style MI head (`01` hướng #3) tối đa hóa MI giữa code `c` và output — nếu `c` (= nhãn technique) **nhiễu**, MI sẽ học **shortcut sai**, không phải kiểu attack thật. [`Asset\Total_Analyst1\Chen_2016_InfoGAN.md_ANALYSIS.md:53-55`](..\Asset\Total_Analyst1\Chen_2016_InfoGAN.md_ANALYSIS.md)

⇒ **Mâu thuẫn cấu trúc:** đóng góp bán-chạy nhất của nhánh phụ thuộc vào dữ liệu *chưa sẵn sàng nhất*. Khuyến nghị: (a) chỉ đo controllability trên **verified split** (504/468) cho RQ, chấp nhận coverage hẹp; (b) gộp về **ít lớp condition tin cậy** (ví dụ 3-4 technique mạnh) thay vì toàn bộ; (c) nếu disentanglement không đo được trên nhãn sạch, **pre-commit** rằng đóng góp lùi về "δ-tradeoff + recon-anchor" (`00` F.09 (b)) — đừng để controllability thành claim không kiểm chứng được.

### PB4 — 6GB + VAE rời rạc nhỏ = **posterior collapse là kịch bản mặc định, không phải rủi ro phụ**.

`00` D.4 thừa nhận full-spec (Transformer 4-6 lớp, latent 256, WGAN-GP) "khó/không chạy nổi" trên 6GB và phải thu nhỏ về LSTM 2 lớp / z=64-128. Vấn đề: VAE text **nhỏ + decoder tự hồi quy mạnh** là công thức kinh điển của posterior collapse (KL→0, decoder bỏ qua z) — và đây *chính* là paper Bowman 2016 mô tả, paper bạn **chưa có** (PB1). Khi z bị bỏ qua thì controllability = 0, tức novelty của nhánh biến mất. `00` đã có warm-up gate G0 (`KL∈[5,50]`, recon≥70%) — đúng hướng, nhưng:

- Free-bits / KL-annealing là kỹ thuật từ Bowman/Kingma-Fixing-VAE — phải đọc nguồn để chỉnh đúng, không đoán.
- Khuyến nghị bổ sung: **giảm capacity decoder có chủ đích** (decoder yếu hơn anchor MLE) để buộc dùng z — `01` mục 6.3 đã nêu, nâng thành **điều kiện kiến trúc cứng**, không phải tùy chọn.

### PB5 — Bỏ WGAN-GP token rời rạc là đúng; nhưng `01` vẫn còn để WGAN-GP-trên-embedding như tùy chọn → cần dứt khoát.

`00` mục C/G đã loại GP và chọn **feature-matching + critic hinge nhẹ**. `01` (bước 4, hướng #4/#9) vẫn liệt kê "WGAN-GP nếu cần, trên embedding liên tục". [`Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md:96`](..\Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md) ⇒ Lấy `00` làm chuẩn: trên 6GB, GP nhân đôi bộ nhớ qua `create_graph` (`00` D.4) — **không dùng** ở vòng đầu, kể cả trên embedding. Feature-matching là đòn bẩy chống D-saturation phù hợp hơn và rẻ hơn ở đây.

---

## 3. Hợp nhất `01` ↔ `00` (lệch pha)

- `01` chấm "prototype VAE/VAE-GAN = 0.55", "vượt MLE = 0.30", "latent-control/augmentation = 0.70". `00` đã **đổi khung mục tiêu**: không còn nhắm "vượt MLE toàn cục" mà nhắm **controllability + δ-tradeoff + recon-anchor** với pure-VAE làm ablation bắt buộc. ⇒ con số 0.30 không còn là KPI; KPI đúng là G1 (full VAE-GAN > pure-VAE) + G2 (controllability đo được).
- `01` mở đầu bằng "tokenize BPE/subword" (bước 2). `00` F.04 chốt **partial de-lex span-preserving** (giữ keyword + ~30 hàm whitelist, mask identifier/literal, vocab ~200-300 frozen). Hai cái không mâu thuẫn nhưng phải chọn một: `00` partial-delex hợp domain SQLi hơn BPE thuần.

---

## 4. Đánh giá khả thi (độc lập)

| Mục tiêu | Điểm `01` | Điểm của tôi | Lý do |
|---|---:|---:|---|
| Pure-VAE chạy + qua gate posterior-collapse (6GB) | 0.55 | **0.55** | Khả thi nếu thu nhỏ + free-bits đúng; rủi ro collapse cao (PB4). |
| Adversarial **thắng** pure-VAE (G1) | — | **0.40** | Nhiều paper (Xu TVAE) cho thấy adversarial *không* luôn thắng VAE. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:647-654`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) |
| Controllability đo được (RQ1/2) | 0.70 | **0.45** | Hạ vì PB3 (nhãn yếu) + PB1 (thiếu paper disentanglement). |
| Vượt MLE toàn cục | 0.30 | **(không còn là KPI)** | `00` đổi mục tiêu. |
| **Độ sẵn sàng học thuật của nhánh** | — | **0.40** | Hạ mạnh vì PB1: paper nền chưa có trong corpus. |

**"Có chống collapse như SeqGAN không?":** VAE-GAN có **cơ chế khác** (recon-anchor giữ mẫu gần manifold, latent liên tục cho gradient mượt), nhưng đổi lấy một failure-mode mới (posterior collapse, PB4) và một rủi ro nền (thiếu paper + nhãn yếu). Net: nhánh này có rủi ro cao, nhưng trần novelty cũng cao nếu controllability đo được.

---

## 5. Mười hướng cải thiện — tái ưu tiên (kèm cờ rủi ro)

> **[NỀN]** = phải làm trước, không phải cải thiện mô hình. **[CHẮC]** = deliverable an toàn.

| # | Hướng | Công đoạn | Ưu | Nhược / rủi ro | Nguồn |
|---|---|---|---|---|---|
| 1 **[NỀN]** | **Tải paper nền VAE-GAN** | Dùng skill `sci-paper-downloader`: Larsen 2016, Kingma 2014, Bowman 2016, β-VAE. | Mọi claim posterior-collapse/disentangle mới có nguồn. | Tốn thời gian; có thể không tải được vài paper. | PB1; corpus thiếu (manifest 55 file). [`Asset\Total_OCR1\TOTAL_OCR1_MANIFEST.md:9-12`](..\Asset\Total_OCR1\TOTAL_OCR1_MANIFEST.md) |
| 2 **[NỀN]** | **Calibrate nhãn** trước controllability | Snorkel-style accuracy/correlation; chỉ dùng verified/gold-silver làm condition. | Tránh MI học shortcut từ nhãn nhiễu. | Thêm vòng kiểm định + review. | PB3; Phase 5 detector_only. [`Guiding\Phase 5\reports\05_full_label_system_report.md:4-20`](..\Guiding\Phase%205\reports\05_full_label_system_report.md) [`Asset\Total_Analyst1\Ratner_2017_Snorkel.md_ANALYSIS.md:46-52`](..\Asset\Total_Analyst1\Ratner_2017_Snorkel.md_ANALYSIS.md) |
| 3 **[CHẮC]** | **Pure-VAE warm-up + gate G0** | recon+KL, β-anneal 0→1, free-bits 2 nats; gate `KL∈[5,50]`, recon≥70%. | Baseline rõ; chống adversarial phá sớm. | VAE sinh "trung bình"; decoder bỏ z (PB4). | `00` F.06; TVAE objective. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:392-395`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) |
| 4 **[CHỊU TẢI]** | **Giảm capacity decoder có chủ đích** | Decoder yếu hơn anchor MLE; log KL/active-dim/latent-usage mỗi epoch. | Buộc z mang thông tin → cứu controllability. | Recon có thể giảm; cần cân bằng. | PB4; `01` mục 6.3. |
| 5 | **Feature-matching thay GP** | Critic 1D-CNN [3,4,5] LayerNorm; L_fm khớp thống kê đặc trưng; KHÔNG GP. | Chống D-saturation, rẻ trên 6GB. | Latent tốt nhưng decoded vẫn có thể invalid. | PB5; `00` E. [`Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md:96`](..\Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md) |
| 6 | **InfoGAN MI head** *chỉ sau khi #2* | Code `c`=technique tin cậy + Q-head dự đoán lại `c`; `λ≈1`. | Tăng controllability, latent có nghĩa. | Nhãn nhiễu → shortcut (phụ thuộc #2). | InfoGAN MI. [`Asset\Total_OCR1\Chen_2016_InfoGAN.md:206-223`](..\Asset\Total_OCR1\Chen_2016_InfoGAN.md) |
| 7 | **Conditional sampling cho class hiếm** | Log-frequency / training-by-sampling; oversample technique/db hiếm; report per-condition. | Giảm majority bias, tăng coverage. | Oversample nhãn nhiễu khuếch đại lỗi. | CTGAN sampling; bỏ sampling F1→0%. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:669-675`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) |
| 8 | **Partial de-lex span-preserving** | Giữ keyword+~30 hàm; mask identifier/literal; round-trip ≥99%; vocab ~200-300 frozen. | Giảm vocab, bảo toàn cấu trúc, relex được. | Template hẹp → sáng tạo bị giới hạn. | `00` F.04; Phase 4 template/pools. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:46-59`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) |
| 9 | **Novelty theo near-dup cluster** | Phạt/reject sample gần train cluster; report exact/near-dup; chống recon=memorization. | Chống copy & điểm ảo; tin cậy publish. | Novelty mạnh → xa manifold. | Phase 4 buckets+leakage 0; Lee dedup. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:21-33`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Asset\Total_OCR1\Lee_2022_Deduplicating.md:775`](..\Asset\Total_OCR1\Lee_2022_Deduplicating.md) |
| 10 | **δ-correlation + ablation pure-VAE vs VAE-GAN** | Vary constraint density δ; cùng seed/sample/cond; chỉ giữ adversarial nếu thắng pure-VAE trên frontier. | Kết luận trung thực dù thắng/thua; chống phức tạp vô ích. | Có thể kết luận "adversarial không đáng" (kết quả hợp lệ). | `00` F.08; Xu TVAE đôi khi > CTGAN. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:647-654`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) [`Guiding\Phase 3\eval\phase03\decision.json:85-91`](..\Guiding\Phase%203\eval\phase03\decision.json) |

> Lưu ý thứ tự: **#1 và #2 là điều kiện cần** (nền), không phải cải tiến mô hình — nếu bỏ qua, mọi hướng còn lại đứng trên cát.

---

## 6. Khuyến nghị triển khai trong nhánh này

| Tiêu chí (6GB, lịch sử collapse) | VAE-GAN (nhánh này) |
|---|---|
| Trần novelty | cao nếu controllability/latent traversal đo được |
| Rủi ro compute | cao |
| Rủi ro nền chưa sẵn sàng | cao: thiếu paper PB1 + nhãn yếu PB3 |
| Failure-mode riêng | posterior collapse |
| Deliverable dương chắc chắn | pure-VAE hoặc MI-VAE nếu qua gate |

**Khuyến nghị thẳng:** Trong thư mục `Guiding_VAE_GAN`, chỉ theo đuổi nhánh VAE-GAN. Không mở adversarial ngay; đầu tư trước vào #1 (tải paper) + #2 (calibrate nhãn) + #3 (pure-VAE qua gate). Nếu pure-VAE đã cho controllability đo được, thì *kể cả khi adversarial không thắng*, luận văn vẫn có đóng góp dương (latent controllable + δ-tradeoff).

Chỉ khi paper, label và pure-VAE gate đều sẵn sàng mới thêm adversarial.

---

## 7. Kết luận

`00`/`01` chính xác về số liệu và đúng kỷ luật. Khoảng trống thực sự của nhánh VAE-GAN **không nằm ở kiến trúc** mà ở **nền**: (1) paper định danh phương pháp (Larsen/Kingma/Bowman/β-VAE) chưa có trong corpus — phải tải trước khi viết, nếu không các trích dẫn về posterior-collapse/disentanglement là rỗng (PB1); (2) novelty controllability tựa lên nhãn yếu nhất hệ thống (PB3); (3) trên 6GB, posterior collapse là kịch bản mặc định chứ không phải rủi ro phụ (PB4). Xử lý xong ba điều này thì VAE-GAN trở thành nhánh có trần đóng góp cao nhất; chưa xử lý thì nó là nhánh rủi ro cao nhất. Quyết định chọn nhánh nên dựa trên việc bạn có sẵn sàng đầu tư vào hai bước nền #1/#2 hay không.
