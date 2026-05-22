# Đánh giá triển khai hướng VAE-GAN cho sinh dữ liệu SQLi

Ngày lập: 2026-05-22.

File này không thay thế `00_Ke_Hoach_Tong_The.md`; nó là bản đánh giá triển khai có trích dẫn dòng cụ thể từ kết quả nội bộ và các bài báo đã lưu trong `Asset\Total_Analyst1` / `Asset\Total_OCR1`.

## 1. Phạm vi nguồn đã kiểm tra

- Bộ paper analysis trong `Asset\Total_Analyst1` có 55 OCR files được xử lý, 44 analysis cũ được copy/gộp, và 11 analysis mới được sinh; vì vậy đánh giá này dựa trên cả nhóm paper GAN text, VAE/tabular, SQLi/WAF, dedup và weak supervision. [`Asset\Total_Analyst1\TOTAL_ANALYST1_MANIFEST.md:11-13`](..\Asset\Total_Analyst1\TOTAL_ANALYST1_MANIFEST.md)
- Bộ OCR trong `Asset\Total_OCR1` có 55 file markdown được giữ lại, đã bỏ 8 file reject và 1 file trùng lặp chính xác; các citation OCR bên dưới dùng nguồn này khi bản analysis chưa đủ chi tiết. [`Asset\Total_OCR1\TOTAL_OCR1_MANIFEST.md:9-12`](..\Asset\Total_OCR1\TOTAL_OCR1_MANIFEST.md)
- Các nguồn chính cho VAE-GAN gồm Dasari 2025 SQLi với VAE + CWGAN-GP, Xu 2019 CTGAN/TVAE, InfoGAN, Rosa survey về text GAN latent space, RelGAN/SeqGAN cho vấn đề discrete text, WGAN-GP/Spectral Norm cho ổn định adversarial, Lee dedup và Ratner Snorkel cho dữ liệu/nhãn. [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:8-20`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md) [`Asset\Total_Analyst1\Xu_2019_CTGAN.md_ANALYSIS.md:10-11`](..\Asset\Total_Analyst1\Xu_2019_CTGAN.md_ANALYSIS.md)

## 2. Kết luận điều hành

VAE-GAN là hướng **đáng thử nếu mục tiêu là latent controllability, nén biểu diễn, sinh biến thể có điều kiện và chống memorization**, nhưng không nên kỳ vọng nó tự động vượt Conditional MLE trong vòng đầu. Cơ sở là GAN nội bộ hiện đã thua MLE và bị collapse nhiều seed, trong khi các paper VAE/GAN cho thấy kết quả phụ thuộc domain, metric và ablation chặt chẽ. [`Guiding\Phase 3\eval\phase03\decision.json:2-4`](..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\Phase 3\eval\phase03\decision.json:30-38`](..\Guiding\Phase%203\eval\phase03\decision.json)

Đánh giá khả thi định lượng:

- Prototype VAE/VAE-GAN cho latent SQLi: **0.55/1.00**. Cơ sở: Dasari 2025 có hướng VAE giảm FastText vectors về latent `448` chiều rồi dùng U-Net/CWGAN-GP cho SQLi, nhưng chính analysis cũng ghi compute cost cao và khó real-time trên thiết bị yếu. [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:16-20`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md) [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:44`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md)
- Vượt MLE toàn cục: **0.30/1.00** ở vòng đầu. Cơ sở: MLE best unique ratio `0.8032128514056225` và self-BLEU3 `0.012445255997627793`, trong khi GAN best unique ratio chỉ `0.49698795180722893` và Phase 3 khuyến nghị không scale GAN nếu chưa có giả thuyết mới rõ ràng. [`Guiding\Phase 3\eval\phase03\decision.json:30-38`](..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\Phase 3\eval\phase03\decision.json:91`](..\Guiding\Phase%203\eval\phase03\decision.json)
- Giá trị như công cụ latent-control/evaluator-guided augmentation: **0.70/1.00**, nếu dùng pure VAE làm baseline, VAE-GAN là nhánh thêm adversarial, và chỉ giữ khi có frontier point tốt hơn. InfoGAN cho thấy latent code có thể học factor diễn giải được qua mutual information, còn CTGAN/TVAE cho thấy VAE có thể cạnh tranh với GAN trên dữ liệu có điều kiện nhưng không luôn thua/thắng tuyệt đối. [`Asset\Total_Analyst1\Chen_2016_InfoGAN.md_ANALYSIS.md:8-24`](..\Asset\Total_Analyst1\Chen_2016_InfoGAN.md_ANALYSIS.md) [`Asset\Total_OCR1\Xu_2019_CTGAN.md:647-654`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md)

## 3. Vì sao cần hướng khác SeqGAN

SeqGAN Phase 2 collapse ở cả ba seed đã chạy. Seed 42 có unique ratio `0.010040160642570281` và self-BLEU3 `0.9340322580645163`, seed 123 bị collapse dù self-BLEU thấp hơn, seed 456 có syntax validity chỉ `0.2781124497991968`. [`Guiding\Phase 2\eval\gan_results.json:3-9`](..\Guiding\Phase%202\eval\gan_results.json) [`Guiding\Phase 2\eval\gan_results.json:37-43`](..\Guiding\Phase%202\eval\gan_results.json) [`Guiding\Phase 2\eval\gan_results.json:91-97`](..\Guiding\Phase%202\eval\gan_results.json)

Phase 3 quyết định `MLE_MAIN`, vì GAN fail 4/6 gates gồm unique ratio, self-BLEU, no-collapse và frontier dominance; đây là bằng chứng nội bộ mạnh nhất chống lại việc tiếp tục một GAN full-sequence không có anchor/ablation. [`Guiding\Phase 3\eval\phase03\decision.json:2-4`](..\Guiding\Phase%203\eval\phase03\decision.json)

VAE-GAN khác SeqGAN ở chỗ nó có reconstruction/latent anchor để giữ cấu trúc payload, adversarial chỉ đóng vai trò regularizer/phân phối; text GAN survey cũng nêu một hướng xử lý discrete text là làm việc trong latent space hoặc dùng autoencoder để nhúng dữ liệu rời rạc vào không gian liên tục. [`Asset\Total_OCR1\Nie_2019_RelGAN.md:695-704`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) [`Asset\Total_OCR1\Rosa_2022_Survey_Text_GAN.md:1718-1729`](..\Asset\Total_OCR1\Rosa_2022_Survey_Text_GAN.md)

## 4. Vấn đề dữ liệu và nhãn phải xử lý trước

Phase 4 đã xử lý `12,753,953` dòng, có `12,753,951` exact unique canonical payloads, `4,131,974` near-duplicate cluster buckets và `268,272` delex template keys; đây là quy mô đủ lớn nhưng cũng yêu cầu VAE phải train theo cluster/template để tránh học copy. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:4`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:19-22`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

Cluster leakage giữa split đã bằng `0`, nên mọi latent reconstruction/generation phải giữ split này; nếu không, VAE có thể đạt reconstruction cao bằng memorization trên near-duplicate. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:33`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

Label system Phase 5 hiện ở `detector_only`, sample report xử lý `10,000` dòng, có `review_queue=5,360` và chỉ `verified_dev=504`, `verified_test=468`; VAE-GAN conditional không nên tin tuyệt đối vào nhãn chưa calibration. [`Guiding\Phase 5\reports\05_full_label_system_report.md:4-20`](..\Guiding\Phase%205\reports\05_full_label_system_report.md)

Progress full Phase 5 mới ghi `3,900,000 / 12,753,953` dòng, tức `30.5788%`, nên nếu dùng full condition label cần chạy hoàn tất hoặc giới hạn rõ trên subset đã label. [`Guiding\Phase 5\logs\phase05_full_progress.json:4-10`](..\Guiding\Phase%205\logs\phase05_full_progress.json)

## 5. VAE-GAN giải quyết gì và không giải quyết gì

VAE giải quyết được bài toán nén payload/feature về latent liên tục và reconstruction, giúp GAN không phải học trực tiếp trên chuỗi rời rạc từ đầu. Dasari 2025 dùng VAE để giảm vector FastText về latent `448` chiều trước khi dùng U-Net/CWGAN-GP; Xu 2019 mô tả TVAE như mô hình VAE với `p_theta`, `q_phi` và evidence objective cho dữ liệu tabular. [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:16`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md) [`Asset\Total_OCR1\Xu_2019_CTGAN.md:392-395`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md)

GAN trong VAE-GAN có thể dùng để làm phân phối latent/generated gần dữ liệu thật hơn, hoặc dùng feature matching/critic trên embedding liên tục; survey text GAN nêu các loss không cần discrete sampling hoặc làm việc trong latent space như một nhánh chính cho text GAN. [`Asset\Total_Analyst1\Rosa_2022_Survey_Text_GAN.md_ANALYSIS.md:57`](..\Asset\Total_Analyst1\Rosa_2022_Survey_Text_GAN.md_ANALYSIS.md) [`Asset\Total_OCR1\Rosa_2022_Survey_Text_GAN.md:1718-1729`](..\Asset\Total_OCR1\Rosa_2022_Survey_Text_GAN.md)

VAE-GAN **không tự giải quyết** label noise, semantic validity, execution validity, duplicate leakage, hoặc collapse do adversarial quá mạnh. WGAN-GP giúp ổn định critic liên tục nhưng analysis cảnh báo không nên áp dụng trực tiếp lên token ids/chars rời rạc; Phase 4 còn `round_trip_status=not_evaluated`, nên evaluator vẫn là blocker. [`Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md:80-96`](..\Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:72`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

Rủi ro riêng của VAE là posterior collapse hoặc decoder học như language model bỏ qua latent; vì vậy phải log KL, reconstruction, latent utilization và ablation pure-VAE vs VAE-GAN. Đây là yêu cầu kỹ thuật suy ra từ mục tiêu VAE latent; paper nguồn hỗ trợ việc VAE/TVAE học qua latent objective, còn quyết định gate phải do benchmark nội bộ chứng minh. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:392-395`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) [`Guiding\Phase 3\eval\phase03\decision.json:91`](..\Guiding\Phase%203\eval\phase03\decision.json)

## 6. Kiến trúc đề xuất

### 6.1. Mục tiêu hẹp

Mục tiêu vòng đầu là tạo một latent generator có thể reconstruct payload hợp lệ, sample latent biến thể ít trùng, và condition theo technique/DBMS/attack family đủ tin cậy. Mục tiêu không phải là thay thế MLE ngay, vì Phase 3 đã chọn `MLE_MAIN` và MLE frontier hiện tốt hơn GAN. [`Guiding\Phase 3\eval\phase03\decision.json:2-4`](..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\Phase 3\eval\phase03\decision.json:30-38`](..\Guiding\Phase%203\eval\phase03\decision.json)

### 6.2. Pipeline kỹ thuật

1. Dùng Phase 4 canonical/delex split có leakage `0`, gắn condition từ label đã calibration hoặc gold/silver. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:33`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Guiding\Phase 5\reports\05_full_label_system_report.md:15-20`](..\Guiding\Phase%205\reports\05_full_label_system_report.md)
2. Tokenize bằng BPE/subword hoặc semantic tokens thay vì raw char-only; Sennrich BPE nêu subword units xử lý open-vocabulary, còn Chowdhary dùng semantic tokenization/BPE cho SQLi sequence GAN. [`Asset\Total_Analyst1\Sennrich_2016_BPE.md_ANALYSIS.md:139-152`](..\Asset\Total_Analyst1\Sennrich_2016_BPE.md_ANALYSIS.md) [`Asset\Total_OCR1\Chowdhary_2023_GAN_Pentesting.md:497-515`](..\Asset\Total_OCR1\Chowdhary_2023_GAN_Pentesting.md)
3. Train pure conditional VAE trước: encoder nhận payload + condition, decoder reconstruct canonical/delex payload. Latent khởi tạo nên nhỏ hơn Dasari `448` chiều, ví dụ `z_dim=64-128`, vì Dasari analysis ghi compute cost cao và dữ liệu nội bộ có hơn `12.7M` dòng. [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:16`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md) [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:44`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:4`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)
4. Thêm adversarial sau khi VAE reconstruct ổn: discriminator/critic nhận latent hoặc decoder embedding, không nhận token id rời rạc trực tiếp. WGAN-GP ổn định critic liên tục, nhưng analysis nhấn mạnh giới hạn khi áp dụng lên token discrete. [`Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md:10`](..\Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md) [`Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md:96`](..\Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md)
5. Thêm InfoGAN-style mutual information head nếu cần controllability theo technique/DBMS. InfoGAN tối ưu mutual information giữa latent code `c` và output, với objective `V_InfoGAN = V(D,G) - lambda L_I`; paper ghi `lambda=1` cho discrete code. [`Asset\Total_Analyst1\Chen_2016_InfoGAN.md_ANALYSIS.md:23-24`](..\Asset\Total_Analyst1\Chen_2016_InfoGAN.md_ANALYSIS.md) [`Asset\Total_OCR1\Chen_2016_InfoGAN.md:206-223`](..\Asset\Total_OCR1\Chen_2016_InfoGAN.md)
6. Relex/evaluate mọi sample bằng syntax, duplicate cluster, self-BLEU, template entropy, detector/WAF, và manual review. Phase 4 hiện chưa evaluate round-trip, nên phần này là bắt buộc trước khi kết luận. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:72`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

### 6.3. Cấu hình khởi tạo đề xuất

- `z_dim=64` cho prototype đầu, nâng `128` nếu reconstruction tốt nhưng diversity kém; không bắt đầu bằng `448` như Dasari nếu GPU/VRAM hạn chế, vì paper analysis ghi compute cost cao. [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:16`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md) [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:44`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md)
- `decoder` nhỏ hơn anchor MLE ban đầu để buộc dùng latent; nếu decoder quá mạnh, log KL/latent usage để phát hiện posterior collapse. Đây là gate kỹ thuật suy ra từ mục tiêu latent và phải kiểm chứng qua reconstruction/KL, không phải kết luận từ paper. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:392-395`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md)
- `adv_weight` bắt đầu rất thấp, ví dụ `0.01-0.05`, chỉ tăng nếu pure VAE reconstruct ổn và adversarial cải thiện frontier. Lý do là Phase 2/3 cho thấy adversarial đã làm collapse và không thống trị MLE. [`Guiding\Phase 2\eval\gan_results.json:3-9`](..\Guiding\Phase%202\eval\gan_results.json) [`Guiding\Phase 3\eval\phase03\decision.json:79-91`](..\Guiding\Phase%203\eval\phase03\decision.json)
- `condition_sampling` nên dùng log-frequency/training-by-sampling cho class hiếm; CTGAN paper nêu conditional generator và log-frequency sampling để xử lý imbalance, và ablation bỏ sampling có thể làm F1 về `0%` trên credit. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:278-280`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) [`Asset\Total_OCR1\Xu_2019_CTGAN.md:669-675`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md)

## 7. Roadmap xây dựng

### Bước 0: Giả thuyết và kill-switch

Giả thuyết cần ghi trước: "VAE latent anchor cộng adversarial/MI regularization cải thiện novelty/controllability mà không làm giảm syntax/reconstruction so với pure VAE và Conditional MLE anchor." Dừng nếu VAE-GAN không vượt pure VAE, vì Xu 2019 cho thấy TVAE có thể thắng CTGAN ở một số dataset và không có lý do mặc định để chọn GAN phức tạp hơn. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:647-654`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md)

### Bước 1: Dataset và labels

Tạo subset đầu tiên từ Phase 4 canonical/delex, giữ split cluster leakage `0`, loại hoặc hạ trọng số condition `unknown`. Guiding nội bộ nói `unknown` là thiếu bằng chứng chứ không phải engine category. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:33`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md:210-219`](..\Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md)

### Bước 2: Pure VAE baseline

Train pure conditional VAE với reconstruction loss + KL schedule; report reconstruction validity, exact/near duplicate, syntax validity, KL, active dimensions, latent interpolation validity. TVAE trong Xu 2019 được mô tả bằng encoder/decoder probabilistic objective, nên pure VAE là baseline bắt buộc trước GAN. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:392-395`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md)

### Bước 3: Latent sampling và controllability

Đánh giá sample theo condition và latent interpolation; nếu condition bị bỏ qua, thêm MI head kiểu InfoGAN. InfoGAN paper tối đa hóa mutual information giữa latent code và observation để học yếu tố diễn giải được. [`Asset\Total_OCR1\Chen_2016_InfoGAN.md:7-13`](..\Asset\Total_OCR1\Chen_2016_InfoGAN.md) [`Asset\Total_OCR1\Chen_2016_InfoGAN.md:143-144`](..\Asset\Total_OCR1\Chen_2016_InfoGAN.md)

### Bước 4: Thêm adversarial nhẹ

Thêm discriminator/critic trên latent hoặc embedding; dùng Spectral Norm hoặc WGAN-GP nếu cần. WGAN-GP default có gradient penalty và paper report stable training, nhưng analysis cảnh báo chỉ dùng trong không gian liên tục/embedding cho text. [`Asset\Total_OCR1\Gulrajani_2017_WGAN_GP.md:11-18`](..\Asset\Total_OCR1\Gulrajani_2017_WGAN_GP.md) [`Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md:96`](..\Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md)

### Bước 5: Evaluator và downstream utility

Chạy syntax/relex/duplicate/novelty/frontier và downstream detector. Dasari dùng XGBoost và báo `99.40%` so với các baseline, nhưng đó là downstream classifier utility, không chứng minh generator không collapse trong hệ nội bộ. [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:20`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md) [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:74`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md)

### Bước 6: So sánh 3 tầng

So sánh `Conditional MLE anchor`, `pure VAE`, và `VAE-GAN` cùng seed/condition/sample count. Chỉ scale nếu VAE-GAN có frontier point tốt hơn cả hai baseline, không bị collapse, và không tăng duplicate cluster leakage. Phase 3 đã dùng logic frontier/gate để loại GAN cũ. [`Guiding\Phase 3\eval\phase03\decision.json:79-91`](..\Guiding\Phase%203\eval\phase03\decision.json)

## 8. Có chống collapse như SeqGAN không?

Câu trả lời ngắn: **VAE-GAN có cơ chế giảm collapse khác SeqGAN, nhưng vẫn có thể collapse nếu adversarial quá mạnh hoặc latent không được dùng**.

Cơ chế tích cực là reconstruction loss giữ mẫu gần manifold dữ liệu, latent continuous giúp critic/GAN nhận gradient dễ hơn so với token rời rạc, và MI/condition có thể buộc latent mang thông tin điều khiển. Các nguồn liên quan gồm TVAE objective trong Xu, latent-space text GAN trong Rosa/Nie, và InfoGAN mutual information. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:392-395`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) [`Asset\Total_OCR1\Nie_2019_RelGAN.md:695-704`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) [`Asset\Total_Analyst1\Chen_2016_InfoGAN.md_ANALYSIS.md:53-55`](..\Asset\Total_Analyst1\Chen_2016_InfoGAN.md_ANALYSIS.md)

Cơ chế tiêu cực là adversarial vẫn có thể làm mode dropping, posterior collapse có thể làm decoder bỏ qua latent, và downstream score có thể bị reward hacking nếu syntax/relex không kiểm. WGAN paper nói WGAN giảm mode collapse trong ngữ cảnh GAN liên tục, nhưng internal SQLi phải chứng minh lại vì Phase 3 đã fail no-collapse/frontier. [`Asset\Total_OCR1\Arjovsky_2017_WGAN.md:528`](..\Asset\Total_OCR1\Arjovsky_2017_WGAN.md) [`Guiding\Phase 3\eval\phase03\decision.json:79-91`](..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:72`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

Điều kiện chống collapse tối thiểu là: pure VAE pass reconstruction/latent gate trước; adversarial weight nhỏ; KL/active-dim không về 0; duplicate cluster novelty bắt buộc; multi-seed benchmark; và kill-switch nếu VAE-GAN không hơn pure VAE. [`Guiding\Phase 3\eval\phase03\decision.json:91`](..\Guiding\Phase%203\eval\phase03\decision.json) [`Asset\Total_OCR1\Xu_2019_CTGAN.md:647-654`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md)

## 9. Mười hướng cải thiện

| # | Hướng cải thiện | Công đoạn triển khai | Ưu điểm | Nhược điểm / rủi ro | Nguồn |
|---|---|---|---|---|---|
| 1 | Pure-VAE warmup và posterior-collapse gate | Train VAE trước GAN; log reconstruction validity, KL, active dims, latent interpolation; dừng nếu latent không mang thông tin. | Có baseline rõ và tránh adversarial phá từ đầu. | VAE có thể sinh quá trung bình hoặc decoder bỏ qua latent. | TVAE dùng VAE objective; Phase 3 yêu cầu giả thuyết mới có gate rõ. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:392-395`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) [`Guiding\Phase 3\eval\phase03\decision.json:91`](..\Guiding\Phase%203\eval\phase03\decision.json) |
| 2 | Reconstruction anchor + teacher forcing | Decoder reconstruct canonical/delex payload trước; dùng scheduled sampling nhẹ sau khi pass validity. | Giữ syntax tốt hơn full adversarial. | Có thể overfit/copy train nếu không có cluster novelty. | GAN cũ collapse nhiều seed; Phase 4 có split cluster để chống copy. [`Guiding\Phase 2\eval\gan_results.json:3-9`](..\Guiding\Phase%202\eval\gan_results.json) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:33`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) |
| 3 | InfoGAN-style controllable latent code | Thêm code `c` cho technique/DBMS/payload family và Q-head dự đoán lại `c` từ output. | Tăng controllability và giảm latent vô nghĩa. | Nếu nhãn condition nhiễu, MI sẽ học sai shortcut. | InfoGAN tối đa hóa MI giữa latent code và output; Phase 5 label còn detector-only/review queue cao. [`Asset\Total_Analyst1\Chen_2016_InfoGAN.md_ANALYSIS.md:53-55`](..\Asset\Total_Analyst1\Chen_2016_InfoGAN.md_ANALYSIS.md) [`Guiding\Phase 5\reports\05_full_label_system_report.md:4-20`](..\Guiding\Phase%205\reports\05_full_label_system_report.md) |
| 4 | Feature matching hoặc latent-space GAN thay token GAN | D/critic nhận encoder latent hoặc decoder hidden states; tránh D trên token id. | Phù hợp không gian liên tục, giảm vấn đề discrete sampling. | Latent tốt nhưng decoded payload vẫn có thể invalid. | Text GAN survey nêu latent/AE path; WGAN-GP analysis cảnh báo token discrete. [`Asset\Total_OCR1\Rosa_2022_Survey_Text_GAN.md:1718-1729`](..\Asset\Total_OCR1\Rosa_2022_Survey_Text_GAN.md) [`Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md:96`](..\Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md) |
| 5 | Partial delex span-preserving decoder | Decode template + slots, không decode literal raw hoàn toàn; relex từ pool rồi validate. | Giảm vocabulary và bảo toàn cấu trúc SQLi. | Có thể hạn chế sáng tạo nếu template set hẹp. | Phase 4 có `268,272` template keys và literal pools `20,000`; Guiding cảnh báo duplicate/near-duplicate domination. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:21-22`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:42-44`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md:110`](..\Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md) |
| 6 | Conditional training-by-sampling cho class hiếm | Sampling theo condition log-frequency; oversample technique/DBMS hiếm; report per-condition utility. | Giảm majority bias và tăng coverage. | Oversampling nhãn nhiễu có thể khuếch đại lỗi. | CTGAN dùng conditional generator/log-frequency sampling; bỏ sampling có thể làm F1 về `0%` trên credit. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:278-280`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) [`Asset\Total_OCR1\Xu_2019_CTGAN.md:669-675`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) |
| 7 | Kiến trúc nhẹ cho RTX 3050 6GB / dữ liệu lớn | `z_dim=64-128`, encoder/decoder nhỏ, gradient accumulation, subset vertical slice trước full data. | Có khả năng chạy thực tế và debug nhanh. | Mô hình nhỏ có thể underfit cấu trúc phức tạp. | Dasari dùng latent `448` nhưng ghi compute cost cao; dữ liệu Phase 4 có `12,753,953` dòng. [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:16`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md) [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:44`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:4`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) |
| 8 | Pure VAE vs VAE-GAN ablation | Chạy cùng seed/sample/condition; chỉ giữ adversarial nếu frontier tốt hơn pure VAE. | Ngăn tăng độ phức tạp vô ích. | Có thể kết luận GAN không đáng triển khai. | Xu ghi TVAE có thể outperform CTGAN trên vài dataset; Phase 3 loại GAN vì không frontier-dominant. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:647-654`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) [`Guiding\Phase 3\eval\phase03\decision.json:85-91`](..\Guiding\Phase%203\eval\phase03\decision.json) |
| 9 | Latent novelty và privacy/dedup guard | Phạt sample gần train cluster; report exact/near dup, template coverage, memorization. | Chống copy và tăng độ tin cậy publish. | Novelty quá mạnh làm sample xa manifold. | Lee dedup cho thấy near-duplicate overlap và memorization; Phase 4 đã có cluster buckets lớn. [`Asset\Total_OCR1\Lee_2022_Deduplicating.md:27`](..\Asset\Total_OCR1\Lee_2022_Deduplicating.md) [`Asset\Total_OCR1\Lee_2022_Deduplicating.md:775`](..\Asset\Total_OCR1\Lee_2022_Deduplicating.md) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:21`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) |
| 10 | Downstream utility sau syntax/relex gate | Chỉ dùng sample pass syntax/relex để augment detector; đo recall/precision theo minority class. | Chứng minh giá trị sản phẩm thay vì chỉ metric sinh mẫu. | Downstream tăng không chứng minh payload semantic đúng nếu evaluator yếu. | Dasari báo XGBoost `99.40%`; Agrawal nhấn mạnh accuracy không đủ trong imbalance. [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:20`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md) [`Asset\Total_OCR1\Agrawal_2024_GenAI_Synthetic.md:875`](..\Asset\Total_OCR1\Agrawal_2024_GenAI_Synthetic.md) |

## 10. Gate triển khai đề xuất

| Gate | Điều kiện pass | Lý do |
|---|---|---|
| Data gate | Cluster leakage `0`; không generated sample nào nằm trong train near-duplicate cluster. | Phase 4 đã đạt leakage `0`, còn Lee cho thấy near-duplicate overlap làm memorization. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:33`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Asset\Total_OCR1\Lee_2022_Deduplicating.md:775`](..\Asset\Total_OCR1\Lee_2022_Deduplicating.md) |
| VAE gate | Reconstruction syntax/relex đạt baseline; KL/active dims không collapse; latent interpolation còn hợp lệ. | VAE-GAN chỉ có ý nghĩa nếu latent thật sự được dùng; TVAE objective giả định encoder/decoder latent hoạt động. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:392-395`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) |
| Adversarial gate | VAE-GAN phải tốt hơn pure VAE trên frontier, không chỉ tốt hơn một metric đơn. | CTGAN/TVAE không có thứ tự thắng cố định; Phase 3 đã dùng frontier để loại GAN cũ. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:647-654`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) [`Guiding\Phase 3\eval\phase03\decision.json:85-91`](..\Guiding\Phase%203\eval\phase03\decision.json) |
| Condition gate | Per-condition validity/coverage không suy sụp ở class hiếm; không dùng `unknown` như class thật. | `unknown` là thiếu bằng chứng, không phải engine category; CTGAN sampling xử lý imbalance bằng condition. [`Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md:210-219`](..\Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md) [`Asset\Total_OCR1\Xu_2019_CTGAN.md:708-713`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) |
| Utility gate | Augmentation phải cải thiện recall/robustness trên detector/WAF sau khi sample pass syntax/relex. | Downstream accuracy đơn lẻ không đủ trong dữ liệu imbalance; SQLi/WAF paper cho thấy bypass thực tế khó. [`Asset\Total_OCR1\Agrawal_2024_GenAI_Synthetic.md:875`](..\Asset\Total_OCR1\Agrawal_2024_GenAI_Synthetic.md) [`Asset\Total_OCR1\Chowdhary_2023_GAN_Pentesting.md:798-807`](..\Asset\Total_OCR1\Chowdhary_2023_GAN_Pentesting.md) |

## 11. Quyết định đề xuất

Nên xây hướng VAE-GAN theo lộ trình **pure VAE trước, adversarial sau**, và giữ `Conditional MLE` làm baseline chính. Lý do là VAE có thể mang lại latent controllability và reconstruction anchor, nhưng adversarial chỉ đáng giữ nếu chứng minh được giá trị hơn pure VAE/MLE trên frontier nhiều metric. [`Asset\Total_OCR1\Xu_2019_CTGAN.md:647-654`](..\Asset\Total_OCR1\Xu_2019_CTGAN.md) [`Guiding\Phase 3\eval\phase03\decision.json:30-38`](..\Guiding\Phase%203\eval\phase03\decision.json)

Không nên bắt đầu bằng VAE-GAN full model lớn theo Dasari ngay. Dasari có VAE latent `448` và CWGAN-GP/U-Net, nhưng analysis cũng ghi compute cost cao; với dữ liệu nội bộ hơn `12.7M` dòng, vòng đầu nên là vertical slice nhỏ, `z_dim=64-128`, evaluator đầy đủ, và kill-switch nếu không hơn pure VAE. [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:16-20`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md) [`Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md:44`](..\Asset\Total_Analyst1\Dasari_2025_Enhancing_SQLi.md_ANALYSIS.md) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:4`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)
