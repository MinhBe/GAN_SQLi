# 02 — Phản biện độc lập & bổ sung (nhánh Gumbel-Softmax)

> **Ngày:** 2026-05-22 · **Vai trò:** file này **không thay** `00_Ke_Hoach_Tong_The.md` và `01_Danh_Gia_Trien_Khai_Co_Trich_Dan.md`.
> Nó là một lớp **kiểm chứng + phản biện cứng + lấp lỗ hổng**, đọc *sau* hai file kia.
> Nguyên tắc: chỉ viết điều có thể trỏ tới dòng/nguồn cụ thể; phản biện mang tính xây dựng kể cả khi tiêu cực.

---

## 1. Đã kiểm chứng những gì (để bạn tin phần phản biện bên dưới)

Tôi mở trực tiếp các file nguồn mà `01` trích dẫn và đối chiếu từng số:

- `decision.json` khớp 100%: `decision="MLE_MAIN"`, `gate_passed=false`, fail 4/6 gate `G1/G2/G5/G6`, `mle_best_unique_ratio=0.8032128514056225`, `gan_best_unique_ratio=0.49698795180722893`, `gan_mean_unique_ratio=0.2914993306559572`, `collapse_count=3`, `dominating_pair_count=0`. [`Guiding\Phase 3\eval\phase03\decision.json:2-4`](..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\Phase 3\eval\phase03\decision.json:30-38`](..\Guiding\Phase%203\eval\phase03\decision.json) [`Guiding\Phase 3\eval\phase03\decision.json:79-89`](..\Guiding\Phase%203\eval\phase03\decision.json)
- `gan_results.json` khớp 100%: seed 42 `unique_ratio=0.010040160642570281`, `self_bleu3=0.9340322580645163`, `token_entropy=0.8329840706381901`; seed 123 log tụt `1.0→0.12→0.08`; seed 456 `syntax_validity_rate=0.2781124497991968`. [`Guiding\Phase 2\eval\gan_results.json:3-9`](..\Guiding\Phase%202\eval\gan_results.json) [`Guiding\Phase 2\eval\gan_results.json:80-97`](..\Guiding\Phase%202\eval\gan_results.json)
- `Jang_2017` analysis khớp: ST forward-hard/backward-soft (dòng 46-52), low-variance vs REINFORCE (58), "không tự động giải quyết discriminator saturation" (80). [`Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md:46-52`](..\Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md) [`Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md:80`](..\Asset\Total_Analyst1\Jang_2017_Gumbel_Softmax.md_ANALYSIS.md)
- `04_data_foundation_report.md` khớp: `12,753,953` dòng, `4,131,974` near-dup buckets, `268,272` template keys, leakage `0`, `round_trip_status=not_evaluated`. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:4-33`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:72`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)

**Kết luận kiểm chứng:** trích dẫn của `01` là *thật và chính xác*. Vì vậy phần phản biện dưới đây không phải để sửa lỗi citation, mà để **vá những điểm mù về logic** mà cả `00` lẫn `01` chưa nói đủ mạnh.

---

## 2. Sáu phản biện cứng

### PB1 — Gumbel-Softmax **không phải** đòn bẩy chống collapse. Đây là điểm mù nguy hiểm nhất.

Khung trình bày của bạn dễ khiến người đọc (và hội đồng) hiểu "đổi từ SeqGAN sang Gumbel = hết collapse". Bằng chứng nội bộ **bác bỏ** cách hiểu đó:

- Phase 2 đã chạy **chính Gumbel-Softmax có anneal nhiệt độ** mà vẫn collapse cả 3 seed: training log seed 42 ghi `tau` giảm `0.91018 → 0.82018 → 0.73018` trong khi `unique_ratio` đứng yên ở `0.02`. [`Guiding\Phase 2\eval\gan_results.json:18-34`](..\Guiding\Phase%202\eval\gan_results.json)
- File hướng dẫn Phase 4 nội bộ tên thẳng là **`04_Phase4_Conditional_Gumbel_SeqGAN.md`** — tức Gumbel **đã** là lõi của cấu hình fail, không phải hướng mới.

⇒ **Hệ quả viết luận văn:** phải nói rõ trong proposal rằng Gumbel relaxation chỉ sửa *đường gradient qua token rời rạc* (đúng như Jang dòng 46-52, 80), **không** sửa D-saturation/mode-collapse. Ba đòn bẩy *thật sự mới* của nhánh này là (a) **masked-slot** (thu hẹp bề mặt quyết định), (b) **MLE anchor** (mỏ neo cú pháp), (c) **paired-D** (chống shortcut template). `00` đã chốt đúng 3 đòn bẩy này (mục E, D.2) nhưng tiêu đề nhánh "Gumbel-Softmax" lại đặt sai trọng tâm. Đề nghị: trong abstract, gọi đóng góp là **"masked payload-surgery GAN"**, Gumbel chỉ là chi tiết kỹ thuật của decoder.

### PB2 — Rủi ro chịu tải (load-bearing): **slot hiện tại gần như toàn literal** → centerpiece có thể rỗng tín hiệu adversarial.

Đây là rủi ro quyết định *toàn bộ* sự sống còn của Phase 07 và `00` mới chỉ thừa nhận một nửa (D.5).

- Phase 4 chỉ trích được literal pools: `STR/NUM/TIME/ID/TABLE/COMMENT`; top template toàn `__TABLE__ / __ID__ / __STR__ / __NUM__`. **Không có** slot operator tương đương, encoding, comment-as-mutation, function-choice. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:36-59`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md)
- Nếu G chỉ điền literal vào slot literal, thì payload "thật" và "fake" khác nhau ở *giá trị literal* — thứ mà paired-D gần như **không** phân biệt được về chất lượng tấn công. ⇒ tín hiệu adversarial ≈ 0 ⇒ **adv hội tụ về anchor-only** (đúng kịch bản D.5 của `00`).

⇒ **Hệ quả:** Phase 07 **không được phép train** trước khi Phase 04 (`slot_audit.py`) **chứng minh bằng số** có đủ slot *non-literal* khả dụng theo `technique × db`. Nếu audit ra "chỉ literal", phải **chuyển sang S2 tamper-action** (sinh tổ hợp phép biến đổi giữ-hợp-lệ kiểu sqlmap tamper) — đây không phải tinh chỉnh mà là **đổi đối tượng nghiên cứu**. Khuyến nghị: nâng `slot_audit` thành **gate G0 cứng** đứng *trước* mọi quyết định kiến trúc Phase 07.

### PB3 — Cỡ mẫu đánh giá Phase 2 quá nhỏ → một số kết luận collapse có biên độ thống kê yếu.

`gan_results.json` ghi `n_total=996` cho mỗi seed. [`Guiding\Phase 2\eval\gan_results.json:6`](..\Guiding\Phase%202\eval\gan_results.json) Với ~1k mẫu, `unique_ratio` và `self_bleu3` có phương sai lấy mẫu đáng kể; seed 42 (`0.01`) thì rõ ràng là collapse, nhưng seed 123 (`0.367`) ở ranh giới. ⇒ Benchmark Phase 08 phải **cố định cỡ sinh lớn hơn** (đề nghị ≥ 5–10k/seed) và báo bootstrap CI theo seed — đúng tinh thần `00` mục G5 nhưng cần ghi rõ con số, vì 996 là di sản dễ bị phản biện.

### PB4 — "Validity_exec trên sqlite" có thể **chấm sai** payload đa-dialect.

`00` (mục E, F.03) định nghĩa `Validity_exec` = parse + **execute trên sqlite**. Nhưng phân bố `db_hint` của bạn lệch mạnh về MSSQL/MySQL (`00` D.3: mssql 2205, mysql 5211, sqlite chỉ 286). Payload time-based/error-based đặc thù MySQL (`SLEEP()`, `BENCHMARK()`) hoặc MSSQL (`WAITFOR DELAY`) sẽ **fail execute trên sqlite** dù hoàn toàn hợp lệ với DB đích. ⇒ rủi ro: validity bị chấm thấp giả cho đúng nhóm payload bạn quan tâm. Khuyến nghị: (a) **route theo dialect** (sqlite/mysql/pg sandbox riêng) hoặc (b) nếu chỉ giữ sqlite, hạ execute xuống *một* tín hiệu trong validity và nói rõ giới hạn dialect — đừng để execute thành hard-constraint loại bỏ payload đúng-DB-khác.

### PB5 — Composite Score vẫn có nguy cơ "tăng proxy mà verified giảm".

`00` đặt hard-constraint Validity_exec < 50% → loại (mục E). Tốt. Nhưng `S = w1·Validity + w2·(1−SelfBLEU3) + w3·(1−Ŵ1) + w4·Novelty` vẫn cho phép **đánh đổi**: một mô hình tăng Novelty/diversity bằng cách sinh payload *lệch khung* nhưng vẫn vượt ngưỡng 50% có thể nâng S mà chất lượng tấn công thật giảm. `01` mục G đã cảnh báo nguyên tắc này. Bổ sung cụ thể: **khóa trọng số `w` trước khi train**, và thêm một **gate phủ quyết riêng cho từng sub-metric** (validity *và* diversity *và* novelty đều không được tụt dưới sàn) — không để tổng số bù trừ.

### PB6 — D-as-scorer (F.06) là deliverable chắc nhất, nhưng đang bị mô tả như "lưới an toàn" thay vì đóng góp chính.

`00` F.06 đặt H2 D-as-scorer (rerank candidate MLE bằng paired-D đã freeze) là "lưới an toàn". Thực tế đây có thể là **kết quả dương dễ đạt nhất**: nó là ứng dụng GAN *chạy được* ngay cả khi Phase 07 thất bại (kịch bản (a) của F.09). Khuyến nghị chiến lược: viết luận văn sao cho **D-as-scorer là một đóng góp đứng độc lập** ("discriminator học từ adversarial vẫn hữu ích như evaluator/reranker"), không phụ thuộc Phase 07 thắng. Như vậy luận văn có *ít nhất một* đóng góp GAN dương chắc chắn.

---

## 3. Hợp nhất `01` ↔ `00` (chúng lệch pha)

`01` (đánh giá) viết theo khung **cũ hơn**: "MLE anchor + Gumbel masked/action mutation + paired/contrastive D + evaluator". `00` (kế hoạch) **tiến hóa thêm**: đóng khung **benchmark SDSG** (Composite Score, RQ1/2/3), tách rõ **S1 paired-masked vs S2 tamper-action** qua audit 08A, và nâng evaluator thành **cổng đo lường** (Phase 03). Hai điểm cần đồng bộ:

1. `01` còn nhắc "WGAN-GP trên embedding liên tục" như tùy chọn (mục 6.2 bước 7, hướng #9). `00` mục C/nguyên tắc bất biến #4 đã **loại WGAN-GP**. ⇒ Lấy `00` làm chuẩn: **không WGAN-GP**, kể cả trên embedding, ở vòng đầu — vì nó tốn `create_graph` (mục H), và Phase 3.5 đã cho thấy GAN trade chất lượng lấy đa dạng. Spectral Norm là đủ nếu cần ổn định D.
2. `01` chấm "đánh bại MLE toàn payload = 0.35". `00` đã **bỏ mục tiêu thay MLE toàn payload** (chuyển sang masked-surgery). ⇒ con số 0.35 của `01` không còn là KPI đúng; KPI đúng là G1 (adv > anchor-only) + G2 (phá tradeoff trên slot), không phải "thắng MLE end-to-end".

---

## 4. Đánh giá khả thi (độc lập, có điều kiện)

| Mục tiêu | Điểm `01` | Điểm của tôi | Lý do điều chỉnh |
|---|---:|---:|---|
| Prototype masked-surgery chạy được trên 6GB | 0.65 | **0.70** | Bỏ GP + Gumbel chỉ trên slot + model nhỏ là khả thi; Phase 3.5 đã chạy ~4h trên đúng máy (`00` D.4). |
| adv **thắng** anchor-only (G1) | — | **0.40** | Phụ thuộc hoàn toàn PB2: nếu slot toàn literal thì rất khó. Đây là biến quyết định. |
| Phá tradeoff validity↔diversity (G2) | — | **0.35** | Phase 3.5 đã cho thấy GAN trượt dọc frontier; cần slot non-literal mới có cửa. |
| D-as-scorer cho deliverable dương | — | **0.80** | Ít rủi ro nhất; freeze D rồi rerank là kỹ thuật ổn định. |
| "Thắng MLE end-to-end" | 0.35 | **(không còn là KPI)** | `00` đã đổi mục tiêu — xem mục 3.2. |

**Câu trả lời "có chống collapse như SeqGAN không?":** *Có giảm rủi ro, không đảm bảo* — và **lý do giảm không phải Gumbel** (PB1) mà là masked-slot + anchor + paired-D + entropy floor + multi-seed kill-switch. Điều kiện cần: G0 slot-audit qua được (PB2).

---

## 5. Mười hướng cải thiện — tái ưu tiên theo *đòn bẩy thật* (kèm cờ rủi ro)

> Khác `01`: ở đây xếp theo mức đòn bẩy & gắn cờ **[CHỊU TẢI]** cho hướng quyết định sống còn, **[CHẮC]** cho deliverable an toàn.

| # | Hướng | Công đoạn | Ưu | Nhược / rủi ro | Nguồn |
|---|---|---|---|---|---|
| 1 **[CHỊU TẢI]** | Slot-audit non-literal làm **gate G0** trước Phase 07 | `slot_audit.py` đếm slot operator/encoding/comment/function theo `technique×db`; nếu < ngưỡng → chuyển S2. | Chặn được kịch bản adv≈anchor-only ngay từ đầu. | Có thể kết luận "không đủ slot" → phải đổi đối tượng. | PB2; literal-only pools. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:36-59`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) |
| 2 | **S2 tamper-action** dự phòng (sinh tổ hợp phép biến đổi giữ-hợp-lệ) | Action set: comment-insert, case, whitespace, encoding, keyword-split, operator-rewrite; Gumbel chọn chuỗi action trên payload anchor. | Giữ semantic, slot "có nghĩa" hơn literal. | Cần evaluator semantic; action sai phá payload. | Lu 2022 (biến đổi giữ cú pháp), WAF-A-MoLE (mutation giữ logic). [`Asset\Total_OCR1\Lu_2022_GAN_SQLi.md:432-437`](..\Asset\Total_OCR1\Lu_2022_GAN_SQLi.md) [`Asset\Total_Analyst1\Demetrio_2020_WAF_A_MoLE.md_ANALYSIS.md:91-94`](..\Asset\Total_Analyst1\Demetrio_2020_WAF_A_MoLE.md_ANALYSIS.md) |
| 3 | **MLE anchor luôn bật** trên slot | Warm-start/freeze từ MLE baseline; anchor loss trên slot mọi step. | Chống drift cú pháp (RC2); ổn định nhất. | Anchor mạnh → adv gain nhỏ (đo bằng ablation). | MLE best unique `0.8032` >> GAN `0.4970`. [`Guiding\Phase 3\eval\phase03\decision.json:30-38`](..\Guiding\Phase%203\eval\phase03\decision.json) |
| 4 **[CHẮC]** | **D-as-scorer** thành đóng góp độc lập | Train paired-D (real vs MLE-gen, cùng khung+cond) → freeze → rerank/guided-decode candidate. | Deliverable GAN dương gần như chắc chắn. | Chỉ là reranker, không phải generator mới. | PB6; `00` F.06. |
| 5 | **Paired/contrastive D** thay D nhị phân | D nhận `(base, mutated, cond)`; chẩn đoán shortcut: D mù khi slot fill giống nhau. | Buộc D chấm *chất lượng slot*, chống bắt template/độ dài. | Phức tạp hơn, cần real mutation pairs. | RelGAN multi-representation. [`Asset\Total_OCR1\Nie_2019_RelGAN.md:300-307`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) |
| 6 | **Entropy floor + temperature schedule** | `tau:1.0→0.5` chậm, log token/action entropy/epoch, kill nếu entropy tụt nhanh. | Tránh argmax sớm; có tín hiệu collapse sớm. | Sharp samples vẫn có thể collapse (không phải thuốc tiên). | Maddison (temp tradeoff), RelGAN OCR (sharp→collapse), Phase 4 entropy=collapse. [`Asset\Total_Analyst1\Maddison_2017_Concrete_Dist.md_ANALYSIS.md:93`](..\Asset\Total_Analyst1\Maddison_2017_Concrete_Dist.md_ANALYSIS.md) [`Asset\Total_OCR1\Nie_2019_RelGAN.md:279-282`](..\Asset\Total_OCR1\Nie_2019_RelGAN.md) |
| 7 | **Novelty theo near-dup cluster**, không edit-distance thô | Phạt/reject sample rơi vào train cluster; report exact/near-dup theo split. | Chống memorization & điểm ảo do duplicate. | Phạt mạnh đẩy mẫu sang invalid. | Phase 4 `4,131,974` buckets, leakage 0; Lee dedup. [`Guiding\Phase 4\outputs\full\04_data_foundation_report.md:21-33`](..\Guiding\Phase%204\outputs\full\04_data_foundation_report.md) [`Asset\Total_OCR1\Lee_2022_Deduplicating.md:775`](..\Asset\Total_OCR1\Lee_2022_Deduplicating.md) |
| 8 | **Evaluator đa-dialect**, không chỉ sqlite | Route execute theo `db_hint` (sqlite/mysql/pg); validity = soft khi cross-dialect. | Tránh chấm sai payload MySQL/MSSQL (đa số corpus). | Sandbox nhiều DB tốn vận hành. | PB4; phân bố db_hint lệch MSSQL/MySQL (`00` D.3). |
| 9 | **Sub-metric floor gates** (chống bù trừ proxy) | Khóa `w` trước train; mỗi sub-metric có sàn riêng; tổng không bù cho sàn. | Chống "Composite tăng, verified giảm". | Nhiều gate → dễ "không hướng nào qua". | PB5; `01` mục G nguyên tắc. |
| 10 | **Multi-seed ≥5, cỡ sinh ≥5k, kill-switch** | Đơn vị = seed; bootstrap CI; dừng nếu < 3/5 seed vượt anchor. | Chống cherry-pick; biên thống kê đủ. | Tốn compute; có thể dừng sớm (đó là kết quả hợp lệ). | PB3 (n=996 quá nhỏ); `00` G3/G5. [`Guiding\Phase 2\eval\gan_results.json:6`](..\Guiding\Phase%202\eval\gan_results.json) |

---

## 6. Khuyến nghị triển khai trong nhánh này

| Tiêu chí (6GB, lịch sử collapse) | Gumbel masked-surgery (nhánh này) | MLE-first (V5) |
|---|---|---|
| Rủi ro compute | thấp-trung | thấp |
| Novelty đóng góp | trung, tập trung vào action/slot mutation có kiểm soát | thấp hơn, GAN không trung tâm |
| Rủi ro "rỗng kết quả" | PB2: slot literal-only hoặc action signal yếu | thấp hơn nhưng đóng góp GAN phụ |
| Deliverable GAN dương chắc chắn | **có** nếu D-as-scorer cải thiện reranking | không phải trọng tâm của nhánh này |

**Khuyến nghị:** trong thư mục `Guiding_Gumbel-Softmax`, chỉ theo đuổi Gumbel masked-surgery. Gate G0 slot-audit phải đứng trước mọi training adversarial; D-as-scorer giữ vai trò lưới đỡ dương độc lập nếu action-GAN không vượt anchor.

---

## 7. Kết luận

Hai file `00`/`01` của bạn đúng về kỷ luật và *chính xác về trích dẫn* (tôi đã kiểm chứng). Điểm cần sửa **không phải số liệu** mà là **trọng tâm tự sự**: (1) Gumbel không phải thứ chống collapse — masked-slot/anchor/paired-D mới là (PB1); (2) cả centerpiece phụ thuộc vào một dữ kiện chưa chứng minh — slot non-literal có tồn tại đủ không (PB2). Hãy biến `slot_audit` thành gate G0 cứng, giữ D-as-scorer như đóng góp dương độc lập, và khóa sub-metric floor + multi-seed trước khi train. Làm vậy thì dù masked-surgery thắng hay thua, luận văn vẫn đứng vững — đúng tinh thần "sống sót mọi kết cục" của `00`.
