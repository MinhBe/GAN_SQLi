# Guiding — Định hướng triển khai đã chốt

Ngày lập: 2026-05-29

## 0. File này là gì

- Đây là file định hướng thi hành (operational guiding) cho giai đoạn hiện tại của đề tài.
- Nó **chốt lại mục tiêu sau khi thu hẹp**, dùng thay cho phần tham vọng "protocol contribution" quá nặng trong `Mục tiêu đề tài/03_ke_hoach_toi_uu_giai_doan_1.md`.
- Khi tiếp tục công việc, đọc theo thứ tự: `guiding.md` (file này) → `RECOVERY.md` → `TRAJECTORY_AUDIT.md` → `TIMELINE.md`.
- Quy ước: file này quyết định "làm gì và làm thế nào"; `RECOVERY.md` giữ trạng thái hiện tại; `TRAJECTORY_AUDIT.md` kiểm tra drift; `TIMELINE.md` ghi nhật ký việc đã làm.

## 1. Mục tiêu đã chốt

> Sản phẩm cuối là **MỘT BÀI KHẢO SÁT (survey)** về sinh payload / synthetic SQLi bằng generative models, trong đó **bằng chứng thực tế** đến từ việc **tái hiện code thầy** và **tái hiện các bài báo khoa học**.

Bốn quyết định nền tảng:

1. **Đóng góp chính = survey + reproduction evidence**, KHÔNG còn là "xây protocol đánh giá". Evaluator / split / baseline đã dựng ở Week 1–5 chỉ đóng vai **công cụ đo lại cho các reproduction**, không phải đóng góp chính.
2. **Code thầy = PayloadsAllTheThings** → đã được tái hiện về cơ bản ở Week 1 (trích taxonomy + dựng seed corpus + baseline rule/mutation). Đây là repo seed/taxonomy, không phải code train/generate model, nên "tái hiện" đúng nghĩa là trích taxonomy + dựng baseline → **đã xong, không còn nợ**.
3. **Bài báo = "toàn bộ" paper lõi**, nhưng tái hiện theo **mức phân tầng** (xem mục 2 và 3).
4. **WAF-A-MoLE đóng băng**: giữ kết quả `threshold_reached=0` như một kết quả baseline/failure trung thực; **không đầu tư thêm**.

## 2. Nguyên tắc "Toàn bộ ở mức phân tầng"

"Tái hiện toàn bộ" ở mức **full/exact cho mọi paper là KHÔNG khả thi** với điều kiện hiện có (máy RTX 3050 6GB, thời gian thesis, nhiều paper không công khai code/data). Nếu hiểu sai chữ "toàn bộ", đề tài sẽ vỡ trận đúng như rủi ro "Scope phình rộng".

Cách làm "toàn bộ" đúng và bảo vệ được trong một bài khảo sát:

- **Phủ hết** tất cả paper lõi trong phần survey.
- Mỗi paper được gán **một mức tái hiện thực tế**: `exact` / `partial` / `conceptual` / `cite-only`.
- **Trung thực** ghi rõ paper nào tới mức nào và **vì sao** (thiếu code, thiếu data, vượt tài nguyên...).
- **Chỉ chạy thật 1–2 paper khả thi**; phần còn lại để conceptual hoặc cite-only.

Định nghĩa mức tái hiện:

| Mức | Khi dùng |
|---|---|
| `exact` | Có code + data + config gốc, chạy lại đúng pipeline |
| `partial` | Có data hoặc mô tả đủ nhưng thiếu một số chi tiết; tự bù phần thiếu |
| `conceptual` | Chỉ có mô tả paper, phải tự dựng pipeline tương đương và ghi rõ là tự dựng |
| `cite-only` | Chỉ trích dẫn làm nền lý thuyết, không chạy |

## 3. Ma trận tái hiện (chốt)

| Paper | Vai trò | Mức tái hiện | Bằng chứng cần có | Lý do mức đó |
|---|---|---|---|---|
| **Dasari 2025 — CWGAN-GP** (`2502.04786v1.md`) | Lõi — augmentation, **khớp đề tài đăng ký** | **partial → exact (chạy thật)** | Train CWGAN-GP trên Kaggle `sqli.csv`; đo synthetic quality + uplift detection; đo lại qua evaluator chung | Data Kaggle có sẵn; CWGAN-GP train được trên 6GB |
| **Le 2024 — GSQLi** (`Le_2024_GSQLi.md`) | Lõi — evasion | **conceptual / partial** | Dựng lại pipeline mutation-action + ablation; đo qua evaluator + ModSecurity | Không có repo/data gốc công khai đủ |
| **Lu 2022 — GAN SQLi** (`Lu_2022_GAN_SQLi.md`) | Lõi — generation | **conceptual** | Tái dựng tamper/mutation operators làm baseline; đo qua evaluator | Data CVE/CNVD/exploit-db không công khai đủ |
| **Demetrio 2020 — WAF-A-MoLE** | Baseline evasion | **đóng băng (threshold=0)** | Giữ nguyên kết quả honest hiện có; KHÔNG đào thêm | Đã đạt mức nghiệm thu baseline |
| BERT-GAN (`Research+...BERT-GAN.md`) | Related — detection | **cite-only** (smoke nếu dư thời gian) | — | Đầu ra là detector, không phải generator |
| Goodfellow 2014 / WGAN-GP / DCGAN | Nền tảng lý thuyết | **cite-only** | — | Chỉ để giải thích cơ sở GAN |
| Text GAN Survey 2022 (`2212.11119v1.md`) | Nền tảng | **cite-only** | — | Giải thích vì sao GAN text rời rạc khó train |

Lý do thiết kế: ma trận này cho **chạy thật 1 paper khớp đúng topic đăng ký (Dasari CWGAN-GP — augmentation)** + **1 paper conceptual cho hướng evasion (GSQLi)**, đồng thời phủ toàn bộ phần còn lại ở mức cite/conceptual. Như vậy khảo sát vừa "toàn bộ", vừa có ≥1 bằng chứng tái hiện chạy thật, vừa giữ được cả hai nhánh evasion và augmentation trong cùng một báo cáo.

## 4. Kế hoạch chi tiết từng phần

### 4.1. Code thầy — PayloadsAllTheThings (ĐÃ XONG)

- Trạng thái: hoàn tất ở Week 1.
- Bằng chứng đã có: source card, teacher seed inventory, normalized corpus, baseline rule/mutation.
- Việc còn lại: chỉ cần trích dẫn lại trong phần survey như "tài nguyên thầy chỉ + baseline xuất phát". Không làm thêm.

### 4.2. Dasari 2025 — CWGAN-GP (ƯU TIÊN 1, CHẠY THẬT)

Đây là reproduction chạy thật đầu tiên và khớp đúng đề tài đăng ký (CWGAN-GP augmentation).

Các bước:

1. **Lấy data**: xác định và tải Kaggle `sqli.csv` và `Modified SQL Dataset.csv`. Ghi nguồn, license, snapshot/commit hoặc ngày tải vào dataset inventory. Nếu không tải được, ghi rõ và dùng corpus thay thế (đánh dấu không phải exact).
2. **Tiền xử lý**: tokenize/encode SQL query về biểu diễn số; tách train/test theo split chống leakage đã có; ghi rõ độ dài, vocab, phân bố nhãn.
3. **Dựng CWGAN-GP**: Generator + Critic theo WGAN-GP (gradient penalty), điều kiện (conditional) theo nhãn; cấu hình batch/epoch vừa với 6GB.
4. **Sinh synthetic SQLi**: tạo tập synthetic có điều kiện nhãn.
5. **Đo synthetic quality**: MSE/R2/PCA như paper + bổ sung evaluator chung (validity, uniqueness, novelty, diversity, duplicate rate).
6. **Đo uplift detection**: train classifier (XGBoost hoặc tương đương) trên (a) data thật và (b) data thật + synthetic; so sánh precision/recall/F1.
7. **Ghi reproduction level**: exact nếu khớp; partial nếu phải bù chi tiết; nêu rõ khác gì so với paper gốc.

Tiêu chí đạt:

- Chạy được end-to-end và có checkpoint + config + log + metrics (không claim "đã train" nếu thiếu 4 thứ này).
- Có bảng so sánh có/không augmentation.
- Có failure analysis (mode collapse, duplicate cao, synthetic kém chất lượng...).

Output:

```text
GAN/Timeline/Reproduction/configs/dasari_cwgangp_config.yaml
GAN/Timeline/Reproduction/results/dasari_cwgangp_metrics.csv
GAN/Timeline/Reproduction/results/dasari_cwgangp_detection_uplift.csv
GAN/Timeline/Reproduction/logs/dasari_cwgangp_run.log
GAN/Timeline/Reports/04a_dasari_cwgangp_reproduction.md
```

### 4.3. Le 2024 — GSQLi (ƯU TIÊN 2, CONCEPTUAL/PARTIAL)

Các bước:

1. Dựng lại pipeline conceptual: `token parser → mutation vector → action selector → payload transformer → evaluator → ModSecurity`.
2. Nếu chưa train được GAN, dùng **mutation-action ablation** theo đúng mutation set của paper; ghi rõ đây là conceptual/ablation, chưa phải GAN đầy đủ.
3. Đo bằng cùng evaluator + real WAF testbed đã có; báo cáo validity, ASR/FNR, uniqueness, novelty, diversity, failure distribution.

Tiêu chí đạt: có ≥1 output đi qua cùng evaluator với baseline; ghi rõ khác gì so với paper gốc; nêu giới hạn.

Output:

```text
GAN/Timeline/Reproduction/paper_models/gsqli_conceptual_plan.md
GAN/Timeline/Reproduction/results/gsqli_conceptual_metrics.csv
GAN/Timeline/Reports/04b_gsqli_conceptual_reproduction.md
```

### 4.4. Lu 2022 — GAN SQLi (CONCEPTUAL)

- Tái dựng các tamper/mutation operators (base64, case confusion, comment/space, UTF-8, unicode-url, MySQL versioned comment...) làm mutation baseline.
- Phần lớn trùng với baseline mutation đã có ở Week 5 → chỉ cần bổ sung operator còn thiếu và ghi rõ nguồn Lu 2022.
- Đánh dấu conceptual vì data gốc không công khai đủ.

### 4.5. Demetrio 2020 — WAF-A-MoLE (ĐÓNG BĂNG)

- **Không chạy thêm.** Giữ nguyên kết quả `threshold_reached=0` (5 models, 4 guided attempted, 1 skipped).
- Trong báo cáo: trình bày như một honest reproduction/failure result của baseline guided mutation.
- Tuyệt đối không tăng rounds/runtime hay tinh chỉnh thêm để "ép" ra success.

### 4.6. Nhóm cite-only

- Goodfellow 2014, WGAN-GP, DCGAN: nền lý thuyết GAN; trích dẫn trong phần background.
- Text GAN Survey 2022: giải thích GAN cho text rời rạc khó train.
- BERT-GAN: related work detection; chỉ smoke test nếu còn dư thời gian.

## 5. Thứ tự thực hiện

1. **Đóng băng WAF-A-MoLE** (chỉ cập nhật trạng thái, không chạy thêm). — đã phản ánh trong `RECOVERY.md`.
2. **Tái hiện Dasari CWGAN-GP** (mục 4.2) — reproduction chạy thật đầu tiên.
3. **Tái hiện conceptual GSQLi** (mục 4.3).
4. **Bổ sung operator Lu 2022** vào mutation baseline (mục 4.4).
5. **Bảng so sánh tổng hợp** giữa baseline và các reproduction, đo bằng cùng evaluator.
6. **Viết survey + failure analysis + giới hạn + hướng tiếp theo.**

## 6. Tiêu chí nghiệm thu mới (thay cho mục 14 của kế hoạch cũ)

| Hạng mục | Ngưỡng đạt |
|---|---|
| Code thầy (PayloadsAllTheThings) | Có source card, taxonomy, seed inventory, baseline — ĐÃ XONG |
| Survey paper | Toàn bộ paper lõi có paper card + mức tái hiện gán rõ |
| Reproduction chạy thật | ≥1 paper chạy end-to-end (mục tiêu: Dasari CWGAN-GP) với checkpoint/config/log/metrics |
| Reproduction conceptual | GSQLi (và Lu 2022) có pipeline conceptual + metrics qua evaluator chung |
| WAF-A-MoLE | Giữ kết quả honest threshold=0, không đào thêm |
| Bảng so sánh | Có bảng chung baseline vs reproduction trên cùng evaluator |
| Failure analysis | Mỗi reproduction có phân tích thất bại và giới hạn |

## 7. Ranh giới an toàn (giữ nguyên)

- Chỉ chạy local/lab/sandbox; không gửi payload vào website thật; không test cloud WAF khi chưa có quyền.
- Báo cáo public chỉ dùng thống kê/taxonomy/metric; **không** in payload bypass chi tiết.
- Không trộn dataset IDS (CIC-IDS2017, UNSW-NB15, NSL-KDD) vào corpus SQLi payload.
- Mỗi nguồn data phải có URL + commit/hash hoặc ngày tải.
- Không claim "đã train/đã reproduce" nếu thiếu checkpoint + config + log + metrics.

## 8. Việc KHÔNG làm (chống scope creep)

- Không nâng cấp WAF-A-MoLE để ép ra evasion success.
- Không tái hiện full/exact mọi paper.
- Không train diffusion / nhiều biến thể GAN nâng cao trong giai đoạn này.
- Không biến đề tài thành "protocol contribution" hay "LLM contribution".
- Không mở rộng sang cloud WAF / nhiều WAF thương mại.
