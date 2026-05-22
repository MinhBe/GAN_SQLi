# Đánh giá triển khai hướng Gumbel-Softmax cho GAN sinh dữ liệu SQLi

Ngày lập: 2026-05-22.

File này không thay thế `00_Ke_Hoach_Tong_The.md`; nó là bản đánh giá triển khai có trích dẫn dòng cụ thể từ kết quả nội bộ và các bài báo đã lưu trong `Asset\Total_Analyst1` / `Asset\Total_OCR1`.

## 1. Phạm vi nguồn đã kiểm tra

- Bộ phân tích paper trong `Asset\Total_Analyst1` có 55 file OCR được xử lý, 44 phân tích đã có được sao chép/gộp, và 11 phân tích mới được sinh thêm; vì vậy đánh giá dưới đây dựa trên một tập paper đủ rộng nhưng vẫn phải coi các kết luận là giả thuyết triển khai cần kiểm chứng bằng benchmark nội bộ. [`Asset\Total_Analyst1\TOTAL_ANALYST1_MANIFEST.md:11-13`](..\Asset\Total_Analyst1\TOTAL_ANALYST1_MANIFEST.md)
- Bộ OCR trong `Asset\Total_OCR1` có 55 file markdown được giữ lại, có loại bỏ 8 file reject và 1 bản trùng lặp chính xác; đây là nguồn dòng OCR để đối chiếu các nhận định kỹ thuật từ bản analysis. [`Asset\Total_OCR1\TOTAL_OCR1_MANIFEST.md:9-12`](..\Asset\Total_OCR1\TOTAL_OCR1_MANIFEST.md)
- Nhóm paper trực tiếp liên quan đến hướng này gồm Jang 2017 Gumbel-Softmax, Maddison 2017 Concrete Distribution, Yu 2017 SeqGAN, RelGAN, WGAN, WGAN-GP, Spectral Normalization, LeakGAN, MaskGAN, InfoGAN, các paper SQLi/WAF như WAF-A-MoLE, GSQLi, Lu 2022 và Chowdhary 2023. [`Asset\Total_Analyst1\TOTAL_ANALYST1_MANIFEST.md:38`](..\Asset\Total_Analyst1\TOTAL_ANALYST1_MANIFEST.md) [`Asset\Total_Analyst1\TOTAL_ANALYST1_MANIFEST.md:69`](..\Asset\Total_Analyst1\TOTAL_ANALYST1_MANIFEST.md)

## 2. Kết luận điều hành

Hướng Gumbel-Softmax **khả thi để thử nghiệm**, nhưng không nên hiểu là "SeqGAN cũ cộng Gumbel là hết collapse". Gumbel-Softmax giải quyết điểm nghẽn gradient qua token rời rạc bằng relaxation khả vi, trong khi paper gốc chỉ khẳng định thay sampling không khả vi bằng mẫu Gumbel-Softmax có thể backprop; nguồn nội bộ paper analysis cũng cảnh báo không được suy diễn rằng nó tự giải quyết discriminator saturation hoặc collapse trên SQLi. [`Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md:40`](..\Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md) [`Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md:80`](..\Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md) [`Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md:91`](..\Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md)

Đề xuất triển khai không phải là sinh toàn bộ payload bằng GAN từ đầu. Đường đi hợp lý hơn là **MLE/conditional generator làm anchor, Gumbel-Softmax chỉ dùng cho masked-slot hoặc action-level mutation**, rồi chấm bằng evaluator cú pháp, novelty, duplicate cluster, relex, detector/WAF và benchmark nhiều seed. Lý do là Phase 3 đã quyết định `MLE_MAIN`, vì GAN thất bại 4/6 gate gồm `G1_unique_ratio`, `G2_self_bleu3`, `G5_no_collapse`, `G6_frontier_dominance`, còn MLE đạt frontier tốt hơn GAN. [`Guiding\Phase 3\eval\phase03\decision.json:2-4`](..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\Phase 3\eval\phase03\decision.json:30-38`](..\Guiding\Phase%203\eval\phase03\decision.json)

Đánh giá khả thi định lượng cho hướng này:

- Prototype nghiên cứu có ích: **0.65/1.00**, nếu giới hạn ở masked-slot/action mutation, dùng anchor MLE, batch nhỏ, và đánh giá nhiều seed. Cơ sở: Gumbel-Softmax/Concrete có gradient low-variance hơn REINFORCE nhưng bị bias theo temperature. [`Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md:58`](..\Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md) [`Asset\Total_Analyst1\Maddison_2017_Concrete_Dist.md_ANALYSIS.md:120`](..\Asset\Total_Analyst1\Maddison_2017_Concrete_Dist.md_ANALYSIS.md)
- Đánh bại MLE trên toàn payload: **0.35/1.00** ở vòng đầu. Cơ sở: GAN nội bộ đã thua MLE rõ ràng về unique/self-BLEU/frontier, và khuyến nghị Phase 3 là không scale GAN nếu chưa có giả thuyết mới xử lý trực tiếp D-saturation và tradeoff syntax/diversity. [`Guiding\Phase 3\eval\phase03\decision.json:30-38`](..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\Phase 3\eval\phase03\decision.json:91`](..\Guiding\Phase%203\eval\phase03\decision.json)
- Khả năng giảm collapse so với SeqGAN REINFORCE cũ: **có, nhưng chỉ có điều kiện**. Gumbel giảm vấn đề gradient rời rạc, RelGAN cũng dùng Gumbel thay REINFORCE và báo cáo gradient ổn định hơn, nhưng temperature quá sắc vẫn có thể góp phần mode collapse. [`Asset\Total_Analyst1\Nie_2019_RelGAN.md_ANALYSIS.md:73`](..\Asset\Total_Analyst1\Nie_2019_RelGAN.md_ANALYSIS.md) [`Asset\Total_Analyst1\Nie_2019_RelGAN.md_ANALYSIS.md:114`](..\Asset\Total_Analyst1\Nie_2019_RelGAN.md_ANALYSIS.md) [`Asset\Total_OCR1\Nie_2019_RelGAN.md:279-282`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md)

## 3. Bằng chứng nội bộ: vì sao không nên lặp lại SeqGAN cũ

SeqGAN Phase 2 bị collapse trên cả ba seed đã chạy. Seed 42 có `collapse_detected=true`, unique ratio chỉ `0.010040160642570281`, self-BLEU3 `0.9340322580645163`, nghĩa là mẫu lặp rất nặng dù syntax validity đạt `0.8323293172690763`. [`Guiding\Phase 2\eval\gan_results.json:3-9`](..\Guiding\Phase%202\eval\gan_results.json)

Seed 123 vẫn bị đánh dấu collapse, unique ratio `0.3674698795180723`, self-BLEU3 `0.036586328350314765`, syntax validity `0.7349397590361446`, và log adversarial có giai đoạn unique ratio tụt xuống `0.12` rồi `0.08`. [`Guiding\Phase 2\eval\gan_results.json:37-43`](..\Guiding\Phase%202\eval\gan_results.json) [`Guiding\Phase 2\eval\gan_results.json:80-85`](..\Guiding\Phase%202\eval\gan_results.json)

Seed 456 cũng bị collapse, unique ratio `0.49698795180722893`, self-BLEU3 `0.3364321334858476`, syntax validity chỉ `0.2781124497991968`, và log có unique ratio `0.02`. [`Guiding\Phase 2\eval\gan_results.json:91-97`](..\Guiding\Phase%202\eval\gan_results.json) [`Guiding\Phase 2\eval\gan_results.json:129`](..\Guiding\Phase%202\eval\gan_results.json)

So với đó, MLE frontier có điểm tốt hơn: best MLE unique ratio `0.8032128514056225`, best self-BLEU3 `0.012445255997627793`, syntax reference `0.7098393574297188`; trong khi GAN best unique ratio chỉ `0.49698795180722893`, GAN mean unique ratio `0.2914993306559572`, mean self-BLEU3 `0.4356835733002262`. [`Guiding\Phase 3\eval\phase03\decision.json:30-38`](..\Guiding\Phase%203\eval\phase03\decision.json)

Kết luận nội bộ hiện tại là không scale GAN Phase 02, tiếp tục Conditional MLE + evaluator-guided search trừ khi có giả thuyết GAN đã đăng ký trước và xử lý trực tiếp D-saturation cùng tradeoff syntax/diversity. [`Guiding\Phase 3\eval\phase03\decision.json:91`](..\Guiding\Phase%203\eval\phase03\decision.json)

## 4. Vấn đề dữ liệu và nhãn phải xử lý trước khi train

Phase 4 đã xử lý `12,753,953` dòng trong `7667.5` giây, có `12,753,951` exact unique canonical payloads, `4,131,974` near-duplicate cluster buckets và `268,272` delex template keys. Đây là nền tốt cho chống memorization/collapse nhưng cũng cho thấy không thể train thẳng trên raw payload mà bỏ qua cluster/template. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:4-5`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:19-22`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

Split leakage theo cluster đã được đưa về `0` bằng deterministic cluster assignment; đây phải là điều kiện bắt buộc cho mọi benchmark Gumbel-GAN vì duplicate leakage có thể tạo điểm giả. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:33`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

Literal pools hiện có giới hạn `ID=20,000`, `TABLE=20,000`, `COMMENT=20,000`; masked-slot Gumbel nên sinh trên slot/action hoặc tập candidate có kiểm soát, không nên softmax trên toàn vocabulary raw quá lớn. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:42-44`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

Vòng label hiện tại mới ở `detector_only`, sample report xử lý `10,000` dòng với `gold=4,821`, `silver=1,251`, `bronze=3,928`, `review_queue=5,360`, `verified_dev=504`, `verified_test=468`; do đó condition label chưa đủ tin cậy để làm reward chính nếu không calibration thêm. [`Guiding\Phase 5\reports\05_full_label_system_report.md:4-20`](..\Guiding\Phase%205\reports\05_full_label_system_report.md)

Full Phase 5 trong log mới đi tới `3,900,000 / 12,753,953` dòng, tức `30.5788%`, nên không được xem bộ nhãn full là đã hoàn tất. [`Guiding\Phase 5\logs\phase05_full_progress.json:4-10`](..\Guiding\Phase%205\logs\phase05_full_progress.json)

## 5. Gumbel-Softmax giải quyết gì và không giải quyết gì

Gumbel-Softmax dùng công thức `softmax((logits + Gumbel noise) / tau)` và anneal nhiệt độ `tau`, cho phép backprop qua lựa chọn categorical; Straight-Through có thể dùng hard token ở forward nhưng gradient đi qua bản mềm ở backward. [`Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md:46-52`](..\Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md)

Concrete Distribution mô tả cùng họ relaxation: lấy Gumbel noise, cộng logits, chia temperature và softmax; khi temperature tiến về 0 thì mẫu tiến gần one-hot, nhưng gradient vẫn bị bias và chọn temperature sai có thể làm mẫu quá mềm hoặc gradient quá nhiễu. [`Asset\Total_Analyst1\Maddison_2017_Concrete_Dist.md_ANALYSIS.md:55-59`](..\Asset\Total_Analyst1\Maddison_2017_Concrete_Dist.md_ANALYSIS.md) [`Asset\Total_Analyst1\Maddison_2017_Concrete_Dist.md_ANALYSIS.md:93-107`](..\Asset\Total_Analyst1\Maddison_2017_Concrete_Dist.md_ANALYSIS.md)

So với REINFORCE của SeqGAN, lợi ích chính là giảm variance của gradient. SeqGAN dùng policy gradient/REINFORCE và MC rollout vì discriminator chỉ chấm full sequence, còn paper REINFORCE kinh điển cũng nêu các thuật toán này có nhược điểm như thiếu lý thuyết hội tụ tổng quát và dễ vào false optima. [`Asset\Total_Analyst1\Yu_2017_SeqGAN.md_ANALYSIS.md:46-52`](..\Asset\Total_Analyst1\Yu_2017_SeqGAN.md_ANALYSIS.md) [`Asset\Total_OCR1\Yu_2017_SeqGAN.md:237-249`](..\Asset\Total_OCR1\Yu_2017_SeqGAN.md) [`Asset\Total_OCR1\Williams_1992_REINFORCE.md:161`](..\Asset\Total_OCR1\Williams_1992_REINFORCE.md)

Điều Gumbel **không tự giải quyết** là discriminator quá mạnh, reward hacking, memorization, label noise, relex lỗi, execution invalid, và shortcut theo template. Tài liệu nội bộ đã ghi REINFORCE gây structural collapse, reward WAF có thể bị hack, và nếu uniqueness hoặc AST entropy thấp thì phải coi là collapse dù bypass cao. [`Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md:224`](..\Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md) [`Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md:60-62`](..\Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md) [`Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md:250-264`](..\Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md)

## 6. Kiến trúc đề xuất

### 6.1. Mục tiêu hẹp

Mục tiêu vòng đầu là chứng minh Gumbel/action generator tạo được payload biến thể hợp lệ, ít trùng, có kiểm soát theo condition, và cải thiện frontier so với anchor-only trên một lát dữ liệu nhỏ. Mục tiêu **không** phải là thay toàn bộ Conditional MLE ngay lập tức, vì Phase 3 đã chứng minh MLE đang là baseline mạnh hơn. [`Guiding\Phase 3\eval\phase03\decision.json:2-4`](..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\Phase 3\eval\phase03\decision.json:91`](..\Guiding\Phase%203\eval\phase03\decision.json)

### 6.2. Pipeline kỹ thuật

1. Lấy dữ liệu từ Phase 4 canonical/delex/template split đã có leakage `0`, không lấy raw split chưa cluster. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:33`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)
2. Dùng Conditional MLE làm anchor generator, vì MLE frontier đang có unique/self-BLEU tốt hơn GAN nội bộ. [`Guiding\Phase 3\eval\phase03\decision.json:30-38`](..\Guiding\Phase%203\eval\phase03\decision.json)
3. Chọn vị trí mask hoặc action mutation từ delex template/literal slots; cơ sở là Phase 4 đã có `268,272` template keys và literal pools lớn nhưng hữu hạn cho relex. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:21-22`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:42-44`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)
4. Generator xuất phân phối action/token bằng Gumbel-Softmax ST: forward hard action để tạo payload thật, backward dùng soft relaxation. [`Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md:46-52`](..\Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md)
5. Discriminator nhận cặp `(payload gốc, payload mutate, condition)` thay vì chỉ fake/real độc lập để giảm shortcut template; RelGAN cho thấy multi-representation của discriminator cung cấp tín hiệu phong phú hơn cho generator. [`Asset\Total_OCR1\Nie_2019_RelGAN.md:300-307`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md)
6. Loss chính là anchor reconstruction / language-model likelihood + adversarial + entropy floor + novelty/cluster penalty + syntax/relex invalid penalty. Tài liệu Phase 4 đã đề xuất entropy/novelty trong loss và coi entropy tụt nhanh là tín hiệu collapse. [`Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md:352-355`](..\Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md) [`Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md:402`](..\Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md)
7. Nếu cần ổn định discriminator, ưu tiên Spectral Normalization trước WGAN-GP trên token ids. WGAN-GP phù hợp khi critic nhận embedding/soft-token liên tục, còn analysis của Gulrajani cảnh báo không áp dụng trực tiếp lên token ids/chars rời rạc. [`Asset\Total_Analyst1\Miyato_2018_Spectral_Norm.md_ANALYSIS.md:69`](..\Asset\Total_Analyst1\Miyato_2018_Spectral_Norm.md_ANALYSIS.md) [`Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md:80-96`](..\Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md)

### 6.3. Tham số khởi tạo đề xuất

Các tham số dưới đây là điểm bắt đầu, không phải kết luận cuối:

- `tau_start=1.0`, `tau_min=0.5`, anneal chậm theo validation entropy; Maddison nêu temperature quá cao làm mẫu nằm trong simplex, quá thấp làm gradient có variance cao, nên không anneal xuống quá nhanh. [`Asset\Total_Analyst1\Maddison_2017_Concrete_Dist.md_ANALYSIS.md:93`](..\Asset\Total_Analyst1\Maddison_2017_Concrete_Dist.md_ANALYSIS.md)
- `entropy_weight=0.03-0.08`, tăng nếu unique ratio giảm dưới gate; Phase 4 đã ghi entropy thấp là collapse và dùng entropy weight `0.05` trong bản hướng dẫn. [`Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md:402`](..\Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md) [`Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md:751`](..\Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md)
- `novelty_weight=0.05-0.12`, bắt đầu quanh `0.10` theo hướng dẫn Phase 4, nhưng phải gắn với cluster/template chứ không chỉ edit distance thô. [`Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md:500`](..\Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md) [`Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md:754`](..\Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md)
- `n_discriminator_steps=1-3` cho prototype nhỏ; RelGAN từng dùng `5` D steps/G trong cấu hình text GAN, nhưng GPU 6GB và dữ liệu SQLi lớn khiến vòng đầu nên thận trọng. [`Asset\Total_OCR1\Nie_2019_RelGAN.md:847-856`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md)
- `eval_seeds >= 5`; Phase 2 đã cho thấy seed variance lớn và cả ba seed bị collapse, nên một seed không đủ quyết định. [`Guiding\Phase 2\eval\gan_results.json:3-9`](..\Guiding\Phase%202\eval\gan_results.json) [`Guiding\Phase 2\eval\gan_results.json:37-43`](..\Guiding\Phase%202\eval\gan_results.json) [`Guiding\Phase 2\eval\gan_results.json:91-97`](..\Guiding\Phase%202\eval\gan_results.json)

## 7. Roadmap xây dựng

### Bước 0: Đăng ký giả thuyết và stop condition

Ghi rõ giả thuyết: "Gumbel masked/action generator cải thiện frontier novelty-syntax-bypass so với anchor-only mà không collapse." Stop nếu không vượt anchor-only trên ít nhất 3/5 seed, vì Phase 3 yêu cầu giả thuyết GAN mới phải xử lý trực tiếp collapse và tradeoff syntax/diversity. [`Guiding\Phase 3\eval\phase03\decision.json:91`](..\Guiding\Phase%203\eval\phase03\decision.json)

### Bước 1: Chuẩn hóa dữ liệu và condition

Chỉ dùng split theo cluster leakage `0`, không train/evaluate trên near-duplicate lẫn nhau. Dùng `unknown` như trạng thái thiếu bằng chứng, không dùng như engine class, vì guiding nội bộ cảnh báo `unknown` không phải engine thật và nếu train như engine sẽ tạo SQL hybrid. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:33`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md:197-219`](..\Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md)

### Bước 2: Tạo anchor-only baseline

Train hoặc reuse Conditional MLE, sinh cùng số mẫu và cùng condition với Gumbel-GAN. Baseline phải dùng MLE frontier hiện tại làm chuẩn vì MLE đã đạt unique ratio `0.8032128514056225` ở cấu hình tốt. [`Guiding\Phase 2\eval\mle_frontier.json:362-365`](..\Guiding\Phase%202\eval\mle_frontier.json)

### Bước 3: Mask/action vocabulary

Tạo action set từ các biến đổi domain đã kiểm chứng: encoding, whitespace, comment, case, operator, keyword split, tamper. Lu 2022 ghi payload SQLi có ký hiệu/space/case/comment không làm thay đổi bản chất cú pháp, và WAF-A-MoLE dùng mutation operator thay đổi cú pháp mà vẫn giữ logic SQL. [`Asset\Total_OCR1\Lu_2022_GAN_SQLi.md:432-437`](..\Asset\Total_OCR1\Lu_2022_GAN_SQLi.md) [`Asset\Total_Analyst1\Demetrio_2020_WAF_A_MoLE.md_ANALYSIS.md:91-94`](..\Asset\Total_Analyst1\Demetrio_2020_WAF_A_MoLE.md_ANALYSIS.md)

### Bước 4: Generator Gumbel-ST

Generator chỉ chọn action/slot trên payload anchor, không sinh full sequence ở vòng đầu. Gumbel-ST phù hợp vì hard forward giữ payload rời rạc, soft backward cho gradient; đây là chính xác vai trò của ST estimator trong Gumbel-Softmax. [`Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md:52`](..\Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md)

### Bước 5: Discriminator và regularization

Dùng paired discriminator hoặc contrastive discriminator để phân biệt real mutation vs generated mutation cùng template/condition. Nếu discriminator quá mạnh, dùng Spectral Norm hoặc WGAN-GP trên embedding liên tục; WGAN-GP paper thay weight clipping bằng gradient penalty, nhưng phải tránh áp dụng trực tiếp lên token ids. [`Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md:10`](..\Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md) [`Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md:96`](..\Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md)

### Bước 6: Evaluator bắt buộc

Evaluator phải có syntax validity, round-trip/relex validity, uniqueness, self-BLEU, AST entropy/template entropy, cluster novelty, detector/WAF score cap, và manual review sample. Phase 4 hiện ghi `round_trip_status=not_evaluated`, nên đây là lỗ hổng cần đóng trước khi công bố kết quả. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:72`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

### Bước 7: Gate quyết định

Gumbel-GAN chỉ được coi là đi tiếp nếu: `collapse_count=0` trên 5 seed; unique ratio không thấp hơn MLE anchor quá `5%`; self-BLEU3 không xấu hơn anchor quá `10%`; syntax validity không thấp hơn anchor; generated samples không rơi vào duplicate cluster train; và có ít nhất một frontier point thống trị anchor-only. Phase 3 trước đó đã fail vì collapse count `3` và không có dominating pair. [`Guiding\Phase 3\eval\phase03\decision.json:79-86`](..\Guiding\Phase%203\eval\phase03\decision.json)

## 8. Có chống collapse như SeqGAN không?

Câu trả lời ngắn: **có thể giảm nguy cơ collapse, nhưng không bảo đảm chống collapse**.

Lý do tích cực là Gumbel-Softmax thay REINFORCE bằng gradient khả vi/low-variance hơn, RelGAN báo cáo Gumbel ổn định hơn REINFORCE, và WGAN/SN có thể giúp discriminator bớt bão hòa. [`Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md:58`](..\Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md) [`Asset\Total_OCR1\Nie_2019_RelGAN.md:640-648`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) [`Asset\Total_Analyst1\Miyato_2018_Spectral_Norm.md_ANALYSIS.md:176`](..\Asset\Total_Analyst1\Miyato_2018_Spectral_Norm.md_ANALYSIS.md)

Lý do tiêu cực là temperature quá thấp hoặc inverse temperature quá sắc vẫn làm phân phối tập trung, RelGAN OCR ghi sharp samples có thể góp phần mode collapse, còn Gumbel analysis cảnh báo không tự xử lý discriminator saturation. [`Asset\Total_OCR1\Nie_2019_RelGAN.md:279-282`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) [`Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md:80`](..\Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md)

Điều kiện chống collapse tối thiểu là giữ anchor MLE, entropy floor, novelty cluster penalty, multi-seed gate, paired discriminator, và stop nếu entropy/template diversity rơi nhanh. Phase 4 đã ghi entropy tụt nhanh là tín hiệu collapse và đã đưa entropy/novelty vào loss. [`Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md:352-355`](..\Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md) [`Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md:402`](..\Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md)

## 9. Mười hướng cải thiện

| # | Hướng cải thiện | Công đoạn triển khai | Ưu điểm | Nhược điểm / rủi ro | Nguồn |
|---|---|---|---|---|---|
| 1 | Masked-slot Gumbel thay vì full-sequence GAN | Từ delex template, chọn slot/action; generator xuất Gumbel-ST cho slot; relex rồi evaluate syntax/cluster. | Giảm không gian hành động, bám cấu trúc SQLi đã hợp lệ. | Có thể chỉ học biến thể nông, không tạo cấu trúc mới. | Phase 4 có `268,272` delex template keys và literal pools `20,000`; Gumbel-ST hỗ trợ hard forward/soft backward. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:21-22`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:42-44`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md:52`](..\Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md) |
| 2 | Anchor MLE + ablation anchor-only | Freeze hoặc warm-start từ MLE; mọi metric so với anchor-only cùng condition/seed. | Tránh lặp lại lỗi GAN thua MLE nhưng vẫn được scale. | Nếu anchor quá mạnh, adversarial gain có thể rất nhỏ. | MLE best unique `0.8032` vượt GAN best `0.4970`; Phase 3 chọn `MLE_MAIN`. [`Guiding\Phase 3\eval\phase03\decision.json:2-4`](..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\Phase 3\eval\phase03\decision.json:30-38`](..\Guiding\Phase%203\eval\phase03\decision.json) |
| 3 | Paired/contrastive discriminator theo cùng template | D nhận `(base, mutated, condition)` và real/generated label; không cho D chỉ nhìn template phổ biến. | Giảm shortcut và giúp D học mutation hợp lệ. | Phức tạp hơn D nhị phân, cần real mutation pairs. | RelGAN dùng nhiều representation để cung cấp guiding info phong phú; Demetrio nhấn mạnh cấu trúc quan trọng hơn histogram token. [`Asset\Total_OCR1\Nie_2019_RelGAN.md:300-307`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) [`Asset\Total_Analyst1\Demetrio_2020_WAF_A_MoLE.md_ANALYSIS.md:91-94`](..\Asset\Total_Analyst1\Demetrio_2020_WAF_A_MoLE.md_ANALYSIS.md) |
| 4 | Temperature schedule + entropy floor | Bắt đầu `tau≈1.0`, giảm chậm, chặn dưới `0.5`; log token/action entropy theo epoch. | Giữ gradient ổn định và tránh argmax quá sớm. | Mẫu mềm quá lâu làm D/G lệch giữa train và inference. | Concrete cảnh báo temperature cao/thấp đều có rủi ro; RelGAN OCR cảnh báo sharp samples có thể gây collapse. [`Asset\Total_Analyst1\Maddison_2017_Concrete_Dist.md_ANALYSIS.md:93`](..\Asset\Total_Analyst1\Maddison_2017_Concrete_Dist.md_ANALYSIS.md) [`Asset\Total_OCR1\Nie_2019_RelGAN.md:279-282`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) |
| 5 | Novelty chống memorization bằng near-duplicate cluster | Khi sinh, reject hoặc phạt nếu rơi vào train cluster/template quá gần; báo exact/near dup theo split. | Chống copy payload train và chống điểm ảo do duplicate. | Phạt quá mạnh có thể đẩy mẫu sang invalid hoặc out-of-domain. | Phase 4 có near-duplicate cluster buckets `4,131,974` và leakage `0`; Lee dedup chỉ ra near-duplicate train/test overlap gây memorization. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:21-33`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Asset\Total_OCR1\Lee_2022_Deduplicating.md:27`](..\Asset\Total_OCR1\Lee_2022_Deduplicating.md) [`Asset\Total_OCR1\Lee_2022_Deduplicating.md:775`](..\Asset\Total_OCR1\Lee_2022_Deduplicating.md) |
| 6 | Action vocabulary từ tamper/WAF domain | Tạo action: comment insertion, case, whitespace, encoding, keyword split, operator rewrite, URL encode, concat. | Hành động có ý nghĩa bảo toàn semantic hơn token ngẫu nhiên. | Cần evaluator semantic; mutation sai có thể phá payload. | Lu ghi mutation ngẫu nhiên SQL syntax element có thể không giữ semantic/syntax; WAF-A-MoLE dùng mutation giữ logic SQL. [`Asset\Total_OCR1\Lu_2022_GAN_SQLi.md:443-445`](..\Asset\Total_OCR1\Lu_2022_GAN_SQLi.md) [`Asset\Total_Analyst1\Demetrio_2020_WAF_A_MoLE.md_ANALYSIS.md:138`](..\Asset\Total_Analyst1\Demetrio_2020_WAF_A_MoLE.md_ANALYSIS.md) |
| 7 | Evaluator syntax + execution/relex trước reward WAF | Bắt buộc pass SQLParse/round-trip/relex trước khi tính bypass/detector reward. | Ngăn reward hacking bằng payload vô nghĩa nhưng qua detector. | Execution sandbox tốn công và có rủi ro vận hành. | Phase 4 hiện `round_trip_status=not_evaluated`; Lu dùng SQLParse để check syntax. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:72`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Asset\Total_OCR1\Lu_2022_GAN_SQLi.md:464`](..\Asset\Total_OCR1\Lu_2022_GAN_SQLi.md) |
| 8 | Weak-supervision label calibration trước condition/reward | Dùng labeling functions, ước lượng conflict/correlation, chỉ train condition trên gold/silver hoặc verified split. | Giảm reward/condition sai do label noise. | Cần thêm vòng kiểm định và review manual. | Phase 5 đang detector-only và review_queue cao; Snorkel học accuracy/correlation của labeling functions không cần full gold. [`Guiding\Phase 5\reports\05_full_label_system_report.md:4-20`](..\Guiding\Phase%205\reports\05_full_label_system_report.md) [`Asset\Total_Analyst1\Ratner_2017_Snorkel.md_ANALYSIS.md:46-52`](..\Asset\Total_Analyst1\Ratner_2017_Snorkel.md_ANALYSIS.md) |
| 9 | Discriminator ổn định bằng Spectral Norm hoặc WGAN-GP trên embedding | Thêm SN cho D layers; nếu dùng WGAN-GP thì critic nhận continuous embedding/soft token, không nhận token id. | Giảm D saturation/vanishing gradient. | WGAN-GP tốn compute; GP trên không gian token rời rạc có thể sai giả định. | SN kiểm soát Lipschitz bằng spectral norm; WGAN-GP thay clipping bằng gradient penalty nhưng analysis cảnh báo token discrete. [`Asset\Total_Analyst1\Miyato_2018_Spectral_Norm.md_ANALYSIS.md:69`](..\Asset\Total_Analyst1\Miyato_2018_Spectral_Norm.md_ANALYSIS.md) [`Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md:10`](..\Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md) [`Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md:96`](..\Asset\Total_Analyst1\Gulrajani_2017_WGAN_GP.md_ANALYSIS.md) |
| 10 | Multi-seed frontier benchmark và kill-switch | Chạy tối thiểu 5 seed; lập frontier `syntax-validity`, `unique`, `self-BLEU`, `AST entropy`, `bypass`; dừng nếu không thống trị anchor. | Chống cherry-pick và buộc mô hình chứng minh giá trị. | Tốn thời gian compute; có thể kết luận dừng sớm. | Phase 2 seed variance lớn và Phase 3 fail frontier dominance; Strelcenia khuyến nghị vertical slice và so với Conditional MLE + evaluator search. [`Guiding\Phase 2\eval\gan_results.json:3-9`](..\Guiding\Phase%202\eval\gan_results.json) [`Guiding\Phase 3\eval\phase03\decision.json:79-91`](..\Guiding\Phase%203\eval\phase03\decision.json) [`Asset\Total_Analyst1\Strelcenia_2023_GAN_Survey_Credit.md_ANALYSIS.md:127`](..\Asset\Total_Analyst1\Strelcenia_2023_GAN_Survey_Credit.md_ANALYSIS.md) |

## 10. Gate triển khai đề xuất

| Gate | Điều kiện pass | Lý do |
|---|---|---|
| Data gate | Split leakage theo cluster bằng `0`; generated samples không trùng train cluster. | Phase 4 đã đạt leakage `0`, phải giữ chuẩn này cho mọi mô hình mới. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:33`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) |
| Label gate | Không dùng `unknown` như engine class; chỉ condition trên nhãn đủ tin cậy hoặc có calibration. | Guiding nội bộ nói `unknown` là thiếu bằng chứng, không phải engine category. [`Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md:210-219`](..\Guiding\00_V5_Hien_Trang_Van_De_Hien_Tai.md) |
| Collapse gate | `collapse_count=0` trên 5 seed; entropy/template diversity không giảm đột ngột. | Phase 3 fail vì `collapse_count=3`; Phase 4 coi entropy tụt nhanh là collapse. [`Guiding\Phase 3\eval\phase03\decision.json:79`](..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md:402`](..\Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md) |
| Frontier gate | Có ít nhất một điểm thống trị anchor-only/MLE trên frontier đa mục tiêu. | Phase 3 fail vì `dominating_pair_count=0`. [`Guiding\Phase 3\eval\phase03\decision.json:85-86`](..\Guiding\Phase%203\eval\phase03\decision.json) |
| Utility gate | Mẫu sinh phải cải thiện hoặc giữ downstream detector/WAF test sau khi pass syntax/relex. | Chowdhary cho thấy AWS WAF chỉ khoảng `8%` bypass và nhiều mẫu bị rule khác bắt, nên bypass phải đo thực tế. [`Asset\Total_OCR1\Chowdhary_2023_GAN_Pentesting.md:798-807`](..\Asset\Total_OCR1\Chowdhary_2023_GAN_Pentesting.md) |

## 11. Quyết định đề xuất

Nên triển khai hướng Gumbel-Softmax như **một nhánh thử nghiệm có kill-switch**, không phải thay thế ngay pipeline MLE. Hình thái có xác suất thành công cao nhất là `Conditional MLE anchor -> Gumbel masked/action mutation -> paired discriminator/SN -> evaluator-guided selection`, vì nó trực tiếp sửa ba vấn đề đã làm SeqGAN fail: gradient rời rạc/REINFORCE, collapse do entropy thấp, và reward/evaluation không đủ ràng buộc. [`Guiding\Phase 2\eval\gan_results.json:3-9`](..\Guiding\Phase%202\eval\gan_results.json) [`Guiding\Phase 3\eval\phase03\decision.json:91`](..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md:778-791`](..\Guiding\04_Phase4_Conditional_Gumbel_SeqGAN.md)

Không nên triển khai `full-sequence Gumbel GAN` trước khi có evaluator round-trip/execution và label calibration, vì Phase 4 còn `round_trip_status=not_evaluated` và Phase 5 hiện còn detector-only/sample label với review queue lớn. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:72`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Guiding\Phase 5\reports\05_full_label_system_report.md:4-20`](..\Guiding\Phase%205\reports\05_full_label_system_report.md)
