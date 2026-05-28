# Kế hoạch tối ưu giai đoạn 1 sau khi giới hạn lại bài toán

Ngày lập: 2026-05-28

## 1. Mục tiêu giai đoạn 1

Mục tiêu giai đoạn 1 là tạo bằng chứng ban đầu, không chỉ tạo kế hoạch.

Chuỗi kết quả cần đạt:

```text
Paper inventory
-> paper card
-> dataset/source inventory
-> evaluator chung
-> baseline rule/mutation
-> chạy mô hình/pipeline paper hoặc code thầy
-> bảng so sánh
-> failure analysis
```

Kết quả cuối của giai đoạn 1 phải trả lời được:

> Với cùng dữ liệu, cùng evaluator và cùng WAF local, mô hình/pipeline từ paper hoặc code thầy có tốt hơn baseline rule/mutation ở đâu, kém ở đâu, và có đủ căn cứ để phát triển thành đề tài chính không?

## 2. Quyết định thiết kế

| Thành phần | Quyết định |
|---|---|
| Đóng góp chính | Protocol đánh giá payload SQLi sinh bởi generative models. |
| Paper chạy trước | `Le_2024_GSQLi.md`. |
| Paper hỗ trợ baseline | `Lu_2022_GAN_SQLi.md`. |
| Testbed chính | ModSecurity + OWASP CRS local. |
| Baseline tối thiểu | Template/rule baseline và mutation baseline. |
| Metric tối thiểu | Validity, ASR, uniqueness, novelty, duplicate rate, diversity, failure distribution. |
| Tạm hoãn | Diffusion, cloud WAF, nhiều WAF, defense contribution đầy đủ, nhiều GAN nâng cao. |

## 3. Sản phẩm đầu ra bắt buộc

Tạo hoặc cập nhật các artifact sau:

```text
GAN/Reports/01_paper_screening.md
GAN/Survey/paper_cards/
GAN/Reports/02_dataset_inventory.md
GAN/Reproduction/configs/evaluation_config.yaml
GAN/Reproduction/results/evaluator_smoke_test.md
GAN/Reports/03_baseline_results.md
GAN/Reproduction/results/baseline_metrics.csv
GAN/Reproduction/paper_models/selected_paper_reproduction_plan.md
GAN/Reports/04_reproduction_results.md
GAN/Reproduction/results/final_comparison_table.csv
GAN/Reports/05_final_analysis.md
```

## 4. Tuần 1 - Paper screening và paper card

Mục tiêu: biết paper nào dùng được, paper nào loại, paper nào chạy trước.

Việc cần làm:

1. Đọc `OCR_RUN_MANIFEST.csv` và `OCR_QUALITY_REPORT.md`.
2. Lập bảng 100% file OCR.
3. Gán nhóm:
   - `core_sqli_generation`
   - `detection_augmentation`
   - `gan_foundation`
   - `text_gan_foundation`
   - `security_synthetic_data`
   - `exclude_or_uncertain`
4. Viết paper card cho ít nhất:
   - `Le_2024_GSQLi.md`
   - `Lu_2022_GAN_SQLi.md`
   - `Research+on+SQL+injection+attacks+detection+method+based+on+BERT-GAN.md`
   - `2502.04786v1.md`
   - `Goodfellow_2014_GAN.md`
   - `Gulrajani_2017_WGAN_GP.md`
   - `2212.11119v1.md`

Output:

```text
GAN/Reports/01_paper_screening.md
GAN/Survey/paper_cards/*.md
GAN/Survey/tables/paper_inventory.csv
```

Tiêu chí đạt:

- Tất cả paper OCR được phân loại.
- Có danh sách `paper lõi`, `paper phụ`, `paper loại`.
- Chốt được paper chạy trước là GSQLi 2024.

## 5. Tuần 2 - Dataset/source inventory

Mục tiêu: biết dữ liệu nào có thể dùng thật.

Nguồn cần kiểm tra:

| Nguồn | Vai trò |
|---|---|
| HttpParams | Dataset chính theo GSQLi 2024 nếu tải được. |
| SSHS/Kaggle SQL Injection Dataset | Dataset đánh giá theo GSQLi 2024 nếu tải được. |
| PayloadsAllTheThings SQL Injection | Seed/taxonomy thay thế, không gọi là dataset gốc của paper. |
| SecLists/SQLMap tamper | Tham chiếu baseline hoặc mutation operators. |
| Dữ liệu từ Lu 2022 | Nếu không công khai, đánh dấu reproduction level là conceptual. |

Bảng inventory tối thiểu:

| Source | Vai trò | Local file | Raw rows | Usable rows | Duplicate | Invalid | License | Label source | Status |
|---|---|---|---:|---:|---:|---:|---|---|---|

Output:

```text
GAN/Reports/02_dataset_inventory.md
GAN/Data/manifests/dataset_inventory.csv
GAN/Data/manifests/source_cards.md
GAN/Data/splits/split_rule.md
```

Tiêu chí đạt:

- Có ít nhất một seed corpus chạy được.
- Có số dòng raw/usable/duplicate/invalid.
- Có rule split tránh leakage.

## 6. Tuần 3 - Evaluator và WAF smoke test

Mục tiêu: mọi phương pháp sinh payload đều được đo bằng cùng bộ đo.

Evaluator tối thiểu:

| Thành phần | Chức năng |
|---|---|
| Normalize/de-dup | Chuẩn hóa và loại trùng exact. |
| Validity checker | Kiểm tra cú pháp/định dạng bằng parser/rule nhẹ. |
| Novelty checker | So với train/seed bằng exact và near-duplicate. |
| Diversity checker | Đo unique ratio, token entropy hoặc khoảng cách chuỗi. |
| WAF runner | Gửi payload vào ModSecurity CRS local và ghi allow/block/rule hit. |
| Aggregator | Xuất bảng metric thống nhất. |

Output:

```text
GAN/Reproduction/configs/evaluation_config.yaml
GAN/Reproduction/results/evaluator_smoke_test.md
GAN/Reproduction/logs/waf_smoke_test.log
```

Bảng smoke test:

| Payload set | Total | Valid | Unique | Novel | WAF allowed | WAF blocked | Notes |
|---|---:|---:|---:|---:|---:|---:|---|

Tiêu chí đạt:

- Chạy được evaluator trên tập nhỏ 20-50 payload.
- Có log WAF allow/block.
- Có config để chạy lại.

## 7. Tuần 4 - Chạy baseline

Mục tiêu: có mốc so sánh trước khi chạy model.

Baseline 1: template/rule.

- Dùng seed payload hoặc template SQLi đã phân nhóm.
- Sinh biến thể đơn giản có kiểm soát.

Baseline 2: mutation.

- Dựa trên mutation operators từ GSQLi/Lu 2022/sqlmap tamper-style.
- Ví dụ nhóm operator: case swapping, inline comment, whitespace swapping, logical operator swapping, number/string encoding.

Output:

```text
GAN/Reports/03_baseline_results.md
GAN/Reproduction/results/baseline_metrics.csv
GAN/Reproduction/logs/baseline_run_<date>.log
```

Bảng metric:

| Method | Total generated | Validity | ASR | Uniqueness | Novelty | Duplicate rate | Main failure |
|---|---:|---:|---:|---:|---:|---:|---|
| Template/rule | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Mutation | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

Tiêu chí đạt:

- Ít nhất 2 baseline chạy qua cùng evaluator.
- Có bảng số liệu thật.
- Có failure analysis ngắn cho từng baseline.

## 8. Tuần 5 - Chạy code hoặc mô hình thầy chỉ

Mục tiêu: biến yêu cầu "chạy mô hình thầy chỉ" thành kết quả kiểm chứng được.

Việc cần làm:

1. Xác định chính xác code/model thầy chỉ nằm ở đâu.
2. Lập code inventory:
   - file train
   - file generate
   - file evaluate
   - dependency
   - input expected
   - output produced
3. Chạy smoke test với dữ liệu nhỏ.
4. Chuyển output về format evaluator chung.
5. Ghi log lỗi nếu không chạy được.

Output:

```text
GAN/Reproduction/teacher_code/teacher_code_inventory.md
GAN/Reproduction/teacher_code/teacher_code_smoke_test.md
GAN/Reproduction/results/teacher_code_metrics.csv
```

Tiêu chí đạt:

- Biết code thầy chạy được phần nào.
- Có output hoặc failure report cụ thể.
- Nếu có output, đưa vào bảng metric chung.

## 9. Tuần 6-7 - Tái triển khai paper GSQLi 2024

Mục tiêu: chạy lại hoặc mô phỏng trung thực pipeline paper lõi.

Reproduction level:

| Level | Khi nào dùng |
|---|---|
| Exact | Có code, dataset, config đủ. |
| Partial | Có dataset hoặc mô tả đủ nhưng thiếu một số chi tiết. |
| Conceptual | Chỉ có mô tả paper, phải tự dựng lại pipeline tương đương. |

Pipeline cần dựng:

```text
Seed payload
-> token parser
-> mutation vector
-> generator/action selector
-> payload transformer
-> evaluator chung
-> WAF testbed
-> metric table
```

Nếu chưa train được GAN:

- Dựng mutation-action baseline theo đúng mutation set của paper.
- Ghi rõ đây là ablation/conceptual reproduction, chưa phải GAN đầy đủ.

Output:

```text
GAN/Reproduction/paper_models/selected_paper_reproduction_plan.md
GAN/Reproduction/results/paper_model_metrics.csv
GAN/Reports/04_reproduction_results.md
GAN/Reproduction/logs/paper_model_run_<date>.log
```

Tiêu chí đạt:

- Có ít nhất một output từ paper model/pipeline.
- Output được đo bằng cùng evaluator với baseline.
- Có ghi rõ khác gì so với paper gốc.

## 10. Tuần 8 - So sánh tổng hợp

Mục tiêu: kết luận bằng số liệu.

Bảng chính:

| Method | Source | Validity | ASR | Uniqueness | Novelty | Diversity | Duplicate rate | Runtime | Main failure |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Template/rule | Baseline | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Mutation | Baseline | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Teacher code | Internal | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| GSQLi reproduction | Paper | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

Câu hỏi kết luận:

1. Mô hình/pipeline nào tái lập được?
2. Mô hình nào không tái lập được và vì sao?
3. Method nào thắng baseline ở metric nào?
4. Method nào chỉ copy/near-copy seed?
5. Method nào bị mode collapse hoặc duplicate cao?
6. Kết quả nào đủ tin để trình bày với thầy?
7. Bước tiếp theo nên là protocol contribution, model contribution hay defense contribution?

Output:

```text
GAN/Reproduction/results/final_comparison_table.csv
GAN/Reports/05_final_analysis.md
```

## 11. Tuần 9 - Báo cáo trình bày

Cấu trúc báo cáo:

1. Bài toán đã thu hẹp.
2. Tiêu chuẩn của thầy và cách đáp ứng.
3. Paper inventory và paper lõi.
4. Dataset/source inventory.
5. Evaluator và WAF testbed.
6. Baseline.
7. Code thầy/model paper.
8. Bảng so sánh.
9. Failure analysis.
10. Hướng giai đoạn 2.

Output:

```text
GAN/Reports/final_reproduction_report.md
GAN/Reports/final_slide_outline.md
```

## 12. Ngưỡng nghiệm thu giai đoạn 1

| Hạng mục | Ngưỡng đạt |
|---|---|
| Paper inventory | 100% file OCR được phân loại. |
| Paper card | Ít nhất 5 paper card lõi/phụ quan trọng. |
| Dataset inventory | Có raw/usable/duplicate/invalid cho ít nhất một corpus. |
| Evaluator | Chạy được sample nhỏ và xuất metric. |
| WAF testbed | Có log allow/block local. |
| Baseline | Ít nhất 2 baseline có kết quả. |
| Code thầy/paper model | Có smoke test hoặc reproduction result/failure report. |
| So sánh | Có bảng chung giữa baseline và model. |
| Phân tích | Có failure analysis và giới hạn. |

## 13. Rủi ro và phương án xử lý

| Rủi ro | Cách xử lý |
|---|---|
| Dataset paper không tải được | Dùng replacement corpus nhưng ghi rõ không phải exact reproduction. |
| Code paper không có | Tái triển khai conceptual và ghi rõ sai khác. |
| GAN không train ổn | Báo cáo failure bằng duplicate/entropy/loss; dùng mutation-action ablation để giữ tiến độ. |
| WAF setup chậm | Chạy evaluator offline trước, WAF smoke test với tập nhỏ. |
| Metric ASR gây hiểu nhầm dual-use | Báo cáo ở mức thống kê, không công bố payload bypass chi tiết. |
| Scope phình rộng | Giữ đúng 1 paper chính, 2 baseline, 1 WAF chính. |

## 14. Kết luận kế hoạch

Kế hoạch tối ưu của giai đoạn 1 là không cố chứng minh ngay "GAN tốt", mà chứng minh năng lực nghiên cứu:

- Biết chọn paper đúng.
- Biết loại paper sai chủ đề.
- Biết dữ liệu đến từ đâu.
- Biết chạy baseline.
- Biết đo bằng metric thống nhất.
- Biết tái triển khai hoặc báo cáo failure trung thực.
- Biết kết luận hướng tiếp theo dựa trên số liệu.

Khi hoàn thành giai đoạn 1, đề tài sẽ chuyển từ mức "kế hoạch tốt" sang mức "nghiên cứu có bằng chứng ban đầu".
