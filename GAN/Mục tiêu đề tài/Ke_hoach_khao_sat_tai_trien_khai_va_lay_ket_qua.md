# Kế hoạch khảo sát, tái triển khai và tạo kết quả cho đề tài SQLi/WAF bằng generative models

Ngày lập: 2026-05-28  
Phạm vi: khảo sát bài báo, tái triển khai mô hình từ bài báo khoa học, đối chiếu với code/hướng của thầy, chạy baseline, tạo kết quả rõ ràng và viết báo cáo.

## 1. Mục tiêu cuối cùng

Mục tiêu không phải chỉ là đọc paper hoặc chạy thử mô hình. Mục tiêu là tạo được một chuỗi kết quả có thể kiểm chứng:

```text
Paper survey
-> paper card
-> related work map
-> lựa chọn mô hình tái triển khai
-> dataset/source card
-> baseline chạy được
-> mô hình bài báo/code thầy chạy được
-> bảng metric so sánh
-> phân tích lỗi
-> kết luận hướng nghiên cứu
```

Kết quả cuối cần có:

- Một bài khảo sát có cấu trúc về các hướng sinh/kiểm thử SQL Injection payload bằng generative models.
- Một bộ paper card cho các bài đã thu thập tại `GAN/Paper/OCR`.
- Một bảng chọn paper lõi, paper phụ và paper loại bỏ.
- Ít nhất 2 baseline chạy được.
- Ít nhất 1 mô hình từ paper hoặc code của thầy được tái triển khai end-to-end.
- Một bảng kết quả rõ ràng theo cùng metric.
- Một phần phân tích: mô hình nào tốt hơn baseline ở đâu, kém ở đâu, fail vì sao.

## 2. Tài nguyên đầu vào hiện có

Thư mục paper OCR:

```text
C:\Users\Admin\Documents\GAN_SQLi\GAN\Paper\OCR
```

Các nhóm tài liệu hiện có:

| Nhóm | File tiêu biểu | Vai trò |
|---|---|---|
| GAN nền tảng | `Goodfellow_2014_GAN.md`, `Radford_2015_DCGAN.md`, `Gulrajani_2017_WGAN_GP.md` | Nền lý thuyết GAN, training stability, WGAN-GP |
| Text generation | `2212.11119v1.md` | Khung khảo sát sinh văn bản bằng generative models |
| SQLi/GAN trực tiếp | `Lu_2022_GAN_SQLi.md`, `Lu_2022_GA_WGAN_SQLi.md`, `Le_2024_GSQLi.md` | Nhóm paper lõi cần đọc và tái triển khai trước |
| SQLi detection/prevention | `2502.04786v1.md`, `Research+on+SQL+injection+attacks+detection+method+based+on+BERT-GAN.md` | Bối cảnh phát hiện/phòng chống SQLi, có thể dùng làm related work |
| Synthetic/security data | `Agrawal_2024_GenAI_Synthetic.md`, `CTGAN_IDS_Rare_Attacks_2025_Menssouri.md`, `Xu_2023_S2CGAN_IDS_possible_IE_GAN.md` | Paper phụ, dùng để so sánh cách dùng GAN/CTGAN trong an ninh mạng |
| Cần kiểm tra/loại | `GSQLi_2025_uncertain_from_old_notes.md`, `Nawaz_2025_CTGAN_Web_Attacks.md` | OCR report cho thấy title có thể không khớp chủ đề, cần xác minh trước khi dùng |

Ghi chú chất lượng OCR:

- `OCR_QUALITY_REPORT.md` cho biết 14/14 file canonical đã OCR thành công.
- Có một số file có dấu hiệu không khớp title/chủ đề, không được đưa vào survey chính trước khi xác minh.

## 3. Nguyên tắc triển khai

Mỗi bước phải tạo ra một kết quả đọc được, lưu được, kiểm tra được.

Không chấp nhận các kết quả dạng:

- “Đã đọc qua”.
- “Đã hiểu sơ bộ”.
- “Mô hình có vẻ chạy”.
- “Kết quả có vẻ tốt”.

Mỗi bước phải có ít nhất một artifact:

- File markdown.
- Bảng CSV.
- Log chạy.
- Config.
- Script.
- Kết quả metric.
- Hình/bảng phân tích.

## 4. Cấu trúc thư mục đầu ra đề xuất

Tạo các thư mục sau nếu chưa có:

```text
GAN/
  Survey/
    paper_cards/
    tables/
    notes/
    final_survey.md
  Reproduction/
    baselines/
    paper_models/
    teacher_code/
    configs/
    logs/
    results/
  Data/
    manifests/
    splits/
    processed/
  Reports/
    01_paper_screening.md
    02_dataset_inventory.md
    03_baseline_results.md
    04_reproduction_results.md
    05_final_analysis.md
```

## 5. Giai đoạn 1: Kiểm kê và phân loại paper

### Mục tiêu

Biết chính xác đang có paper nào, paper nào liên quan trực tiếp, paper nào chỉ là nền tảng, paper nào cần loại.

### Việc cần làm

1. Đọc `OCR_RUN_MANIFEST.csv` và `OCR_QUALITY_REPORT.md`.
2. Lập bảng toàn bộ paper OCR.
3. Gán mỗi paper vào một nhóm:
   - `core_sql_generation`
   - `core_sqli_waf`
   - `gan_foundation`
   - `text_generation`
   - `security_synthetic_data`
   - `detection_defense`
   - `uncertain_or_exclude`
4. Đánh dấu paper nào có thể tái triển khai.
5. Đánh dấu paper nào có code/dataset/testbed rõ.

### Kết quả phải có

File:

```text
GAN/Reports/01_paper_screening.md
GAN/Survey/tables/paper_inventory.csv
```

Bảng tối thiểu:

| Paper | Nhóm | Mức liên quan | Có dataset | Có code | Có metric | Có thể tái triển khai | Ghi chú |
|---|---|---:|---|---|---|---|---|

### Tiêu chí đạt

- 100% paper trong `GAN/Paper/OCR` được phân loại.
- Paper lõi và paper phụ được tách rõ.
- Paper nghi ngờ không khớp chủ đề được đánh dấu, không dùng làm bằng chứng chính.

## 6. Giai đoạn 2: Viết paper card

### Mục tiêu

Biến mỗi paper quan trọng thành một bản tóm tắt có thể so sánh.

### Việc cần làm

Với mỗi paper lõi, tạo một paper card theo mẫu:

```text
Paper:
Năm / venue:
Bài toán:
Đối tượng nghiên cứu:
Phương pháp:
Dataset:
Code:
Testbed/WAF:
Metric:
Baseline:
Kết quả chính:
Giới hạn:
Có thể tái triển khai không:
Vai trò trong đề tài:
```

Ưu tiên paper card cho:

1. `Lu_2022_GAN_SQLi.md`
2. `Lu_2022_GA_WGAN_SQLi.md`
3. `Le_2024_GSQLi.md`
4. `Research+on+SQL+injection+attacks+detection+method+based+on+BERT-GAN.md`
5. `2502.04786v1.md`
6. `Goodfellow_2014_GAN.md`
7. `Gulrajani_2017_WGAN_GP.md`
8. `2212.11119v1.md`

### Kết quả phải có

Thư mục:

```text
GAN/Survey/paper_cards/
```

Mỗi paper lõi có một file:

```text
GAN/Survey/paper_cards/<paper_name>.md
```

File tổng hợp:

```text
GAN/Survey/tables/paper_card_summary.csv
```

### Tiêu chí đạt

- Có ít nhất 5 paper card lõi.
- Mỗi paper card phải chỉ ra rõ: data, method, metric, baseline, limitation.
- Không paper nào được đưa vào survey chính nếu chưa biết nó đóng vai trò gì.

## 7. Giai đoạn 3: Viết bản khảo sát lần 1

### Mục tiêu

Tạo bản survey có cấu trúc, không chỉ là danh sách paper.

### Cấu trúc survey

```text
1. Bài toán và phạm vi
2. Vì sao sinh payload SQLi là bài toán khó
3. Nhóm phương pháp rule/template/mutation
4. Nhóm phương pháp GAN/text GAN
5. Nhóm phương pháp LLM/generative AI
6. Nhóm phương pháp detection/defense
7. Dataset, testbed và metric trong các paper
8. Khoảng trống nghiên cứu
9. Hướng tái triển khai được chọn
```

### Kết quả phải có

File:

```text
GAN/Survey/final_survey_v1.md
GAN/Survey/tables/related_work_map.csv
GAN/Survey/tables/method_comparison.csv
```

Bảng bắt buộc:

| Nhóm phương pháp | Paper | Dữ liệu | Mô hình | Metric | Baseline | Giới hạn |
|---|---|---|---|---|---|---|

### Tiêu chí đạt

- Survey trả lời được: người ta đã làm gì, thiếu gì, mình sẽ tái triển khai gì.
- Có ít nhất 3 nhóm phương pháp được so sánh.
- Có kết luận rõ paper nào sẽ được tái triển khai trước.

## 8. Giai đoạn 4: Kiểm kê dữ liệu và nguồn seed

### Mục tiêu

Biết dữ liệu dùng để chạy baseline và mô hình đến từ đâu, có đáng tin không, có dùng được không.

### Việc cần làm

1. Với từng paper lõi, xác định dataset gốc có công khai không.
2. Nếu paper không có dataset, ghi rõ mức tái triển khai là `partial` hoặc `conceptual`.
3. Lập seed corpus thay thế nếu cần, nhưng phải ghi rõ không phải dataset gốc.
4. Kiểm tra nguồn như PayloadsAllTheThings, SecLists, SQLMap payload nếu dùng.
5. Tạo rule lọc, de-dup, normalize.
6. Tạo safe split để tránh leakage.

### Kết quả phải có

File:

```text
GAN/Reports/02_dataset_inventory.md
GAN/Data/manifests/dataset_inventory.csv
GAN/Data/manifests/source_cards.md
GAN/Data/splits/split_rule.md
```

Bảng tối thiểu:

| Source | Vai trò | File local | Raw rows | Usable rows | Duplicate | Invalid | License | Label source | Status |
|---|---|---|---:|---:|---:|---:|---|---|---|

### Tiêu chí đạt

- Có ít nhất một seed corpus dùng được.
- Có số dòng raw và usable.
- Có thống kê duplicate/invalid.
- Có rule split rõ.
- Không dùng dataset không rõ nguồn làm bằng chứng chính.

## 9. Giai đoạn 5: Xây evaluator và testbed tối thiểu

### Mục tiêu

Có môi trường đánh giá thống nhất cho baseline, paper model và code của thầy.

### Việc cần làm

1. Chọn testbed chính: ModSecurity + OWASP CRS local.
2. Nếu kịp, thêm testbed phụ: Coraza.
3. Xây evaluator nhẹ:
   - Syntax/format validity.
   - Duplicate check.
   - Novelty check với train/seed.
   - WAF allow/block log.
4. Chuẩn hóa format input/output.

### Kết quả phải có

File/thư mục:

```text
GAN/Reproduction/configs/evaluation_config.yaml
GAN/Reproduction/results/evaluator_smoke_test.md
GAN/Reproduction/logs/waf_smoke_test.log
```

Bảng smoke test:

| Payload set | Total | Valid | Duplicate | WAF allowed | WAF blocked | Notes |
|---|---:|---:|---:|---:|---:|---|

### Tiêu chí đạt

- Evaluator chạy được trên một tập payload nhỏ.
- WAF/testbed trả log allow/block.
- Có config để chạy lại.

## 10. Giai đoạn 6: Chạy baseline

### Mục tiêu

Có mốc so sánh trước khi chạy mô hình paper hoặc code của thầy.

### Baseline tối thiểu

1. Template/rule baseline.
2. Mutation baseline.

Baseline mở rộng nếu đủ thời gian:

3. SQLMap tamper-style baseline.
4. MLE/RNN hoặc Transformer nhỏ.

### Kết quả phải có

File:

```text
GAN/Reports/03_baseline_results.md
GAN/Reproduction/results/baseline_metrics.csv
GAN/Reproduction/logs/baseline_run_<date>.log
```

Bảng kết quả:

| Method | Total generated | Validity | ASR | Uniqueness | Novelty | Duplicate rate | Main failure |
|---|---:|---:|---:|---:|---:|---:|---|

### Tiêu chí đạt

- Có ít nhất 2 baseline chạy trên cùng evaluator.
- Có bảng metric thống nhất.
- Có log để tái lập.
- Có phân tích baseline fail ở đâu.

## 11. Giai đoạn 7: Kiểm kê và chạy code của thầy

### Mục tiêu

Biết code của thầy hiện có gì, chạy được đến đâu, output là gì, có thể so với baseline không.

### Việc cần làm

1. Xác định thư mục/code của thầy.
2. Lập code inventory:
   - Script train.
   - Script generate.
   - Script evaluate.
   - Config.
   - Dependency.
   - Input expected.
   - Output produced.
3. Chạy smoke test với dữ liệu nhỏ.
4. Gắn output của code thầy vào evaluator chung.
5. Ghi rõ phần nào chạy được, phần nào lỗi, phần nào cần sửa.

### Kết quả phải có

File:

```text
GAN/Reproduction/teacher_code/teacher_code_inventory.md
GAN/Reproduction/teacher_code/teacher_code_smoke_test.md
GAN/Reproduction/results/teacher_code_metrics.csv
```

Bảng:

| Component | Path | Input | Output | Status | Notes |
|---|---|---|---|---|---|

### Tiêu chí đạt

- Biết code của thầy chạy được phần nào.
- Có ít nhất một output từ code của thầy đưa vào evaluator chung.
- Nếu không chạy được, phải có log lỗi và nguyên nhân cụ thể.

## 12. Giai đoạn 8: Tái triển khai mô hình từ paper

### Mục tiêu

Chạy lại ít nhất một mô hình hoặc phương pháp từ paper để so sánh với baseline và code của thầy.

### Thứ tự ưu tiên

1. Paper gần SQLi generation nhất:
   - `Lu_2022_GAN_SQLi.md`
   - `Lu_2022_GA_WGAN_SQLi.md`
   - `Le_2024_GSQLi.md`
2. Nếu paper không đủ code/dataset:
   - Tái triển khai conceptual version.
   - Ghi rõ khác gì so với paper gốc.
3. Nếu GAN quá bất ổn:
   - Dùng Gumbel/SeqGAN smoke hoặc MLE baseline làm fallback.

### Việc cần làm

1. Chọn 1 paper chính.
2. Viết reproduction plan.
3. Xác định dataset/input.
4. Viết hoặc chỉnh script generate/train.
5. Chạy trên seed nhỏ trước.
6. Chạy bản chính với config cố định.
7. Đưa output vào evaluator chung.

### Kết quả phải có

File:

```text
GAN/Reproduction/paper_models/selected_paper_reproduction_plan.md
GAN/Reproduction/results/paper_model_metrics.csv
GAN/Reports/04_reproduction_results.md
GAN/Reproduction/logs/paper_model_run_<date>.log
```

Bảng:

| Paper model | Reproduction level | Dataset | Total generated | Validity | ASR | Uniqueness | Novelty | Notes |
|---|---|---|---:|---:|---:|---:|---:|---|

### Tiêu chí đạt

- Ít nhất 1 mô hình paper chạy end-to-end hoặc có reproduction failure rõ ràng.
- Kết quả được đo bằng cùng metric với baseline.
- Có phân tích vì sao kết quả giống/khác claim của paper.

## 13. Giai đoạn 9: So sánh tổng hợp

### Mục tiêu

Trả lời bằng số liệu: baseline, code của thầy và mô hình paper khác nhau thế nào.

### Kết quả phải có

File:

```text
GAN/Reproduction/results/final_comparison_table.csv
GAN/Reports/05_final_analysis.md
```

Bảng chính:

| Method | Source | Validity | ASR | Uniqueness | Novelty | Diversity | Runtime | Main failure |
|---|---|---:|---:|---:|---:|---:|---:|---|
| Template/rule | Baseline | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Mutation | Baseline | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Teacher code | Internal | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Paper model | Paper reproduction | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

### Câu hỏi phải trả lời

1. Phương pháp nào có validity cao nhất?
2. Phương pháp nào có ASR cao nhất?
3. Phương pháp nào đa dạng nhất?
4. Phương pháp nào tạo payload mới nhất?
5. Phương pháp nào bị lặp/mode collapse nhiều nhất?
6. Phương pháp nào đáng dùng tiếp cho luận văn?
7. Kết quả nào chưa đủ tin cậy?

### Tiêu chí đạt

- Có bảng so sánh duy nhất cho tất cả phương pháp.
- Mọi số liệu có log/config đi kèm.
- Có kết luận rõ, không chỉ mô tả.

## 14. Giai đoạn 10: Viết báo cáo khảo sát và tái triển khai

### Mục tiêu

Biến toàn bộ kết quả thành một bản báo cáo có thể trình bày với thầy.

### Cấu trúc báo cáo

```text
1. Bài toán và phạm vi
2. Khảo sát các hướng nghiên cứu
3. Paper screening và paper card
4. Dataset/source inventory
5. Baseline và evaluator
6. Tái triển khai code của thầy
7. Tái triển khai mô hình từ paper
8. Kết quả so sánh
9. Phân tích lỗi và giới hạn
10. Hướng nghiên cứu tiếp theo
```

### Kết quả phải có

File:

```text
GAN/Survey/final_survey.md
GAN/Reports/final_reproduction_report.md
GAN/Reports/final_slide_outline.md
```

### Tiêu chí đạt

- Báo cáo có đủ survey và kết quả thực nghiệm.
- Có bảng kết quả chính.
- Có kết luận hướng đi tiếp theo dựa trên số liệu.
- Có phần giới hạn và failure analysis.

## 15. Lịch triển khai đề xuất

| Tuần | Trọng tâm | Kết quả bắt buộc |
|---|---|---|
| Tuần 1 | Paper screening + paper card | `01_paper_screening.md`, ít nhất 5 paper card |
| Tuần 2 | Survey v1 + dataset inventory | `final_survey_v1.md`, `dataset_inventory.csv` |
| Tuần 3 | Evaluator + WAF smoke test | `evaluator_smoke_test.md`, WAF log |
| Tuần 4 | Baseline | `baseline_metrics.csv`, `03_baseline_results.md` |
| Tuần 5 | Code của thầy | `teacher_code_inventory.md`, `teacher_code_metrics.csv` |
| Tuần 6-7 | Tái triển khai paper model | `paper_model_metrics.csv`, reproduction log |
| Tuần 8 | So sánh tổng hợp | `final_comparison_table.csv`, `05_final_analysis.md` |
| Tuần 9 | Viết báo cáo và slide | `final_survey.md`, `final_reproduction_report.md`, `final_slide_outline.md` |

## 16. Tiêu chí nghiệm thu toàn bộ kế hoạch

Kế hoạch được xem là đạt khi có đủ:

- 100% paper OCR được phân loại.
- Ít nhất 5 paper card lõi.
- Một bản survey v1 có related work map.
- Một dataset/source inventory có số dòng thật.
- Một evaluator/testbed chạy được.
- Ít nhất 2 baseline có kết quả.
- Code của thầy được kiểm kê và có smoke test.
- Ít nhất 1 mô hình paper được tái triển khai hoặc có failure report rõ ràng.
- Một bảng so sánh cuối cùng giữa baseline, code thầy và paper model.
- Một báo cáo kết luận hướng đi tiếp theo dựa trên số liệu.

## 17. Quyết định thu hẹp để tránh quá tải

Để có kết quả rõ, không triển khai tất cả cùng lúc.

Ưu tiên:

1. Survey và paper card.
2. Dataset/source inventory.
3. Evaluator/testbed.
4. Template/rule baseline.
5. Mutation baseline.
6. Code của thầy.
7. Một paper model gần SQLi nhất.

Tạm hoãn:

- Diffusion.
- Cloud WAF.
- Nhiều WAF cùng lúc.
- Nhiều mô hình GAN nâng cao.
- Defense contribution đầy đủ.

## 18. Kết luận

Hướng triển khai đúng nhất lúc này là biến đề tài thành một chuỗi khảo sát và tái triển khai có bằng chứng:

> Paper nói gì -> mình tái hiện được gì -> baseline cho thấy gì -> code của thầy cho kết quả gì -> mô hình paper cho kết quả gì -> metric kết luận hướng nào đáng đi tiếp.

Mỗi bước phải tạo ra một artifact. Khi có đủ artifact, đề tài sẽ không còn là kế hoạch hoặc ý tưởng, mà trở thành một nghiên cứu có dữ liệu, kết quả, so sánh và phân tích rõ ràng.

