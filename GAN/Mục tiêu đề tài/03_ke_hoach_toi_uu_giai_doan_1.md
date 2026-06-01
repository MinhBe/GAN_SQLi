# Kế hoạch tối ưu giai đoạn 1 sau khi đảo chiều theo tài nguyên thầy chỉ

Ngày cập nhật: 2026-05-29

Nguồn cập nhật chính:

```text
C:\Users\Admin\Documents\GAN_SQLi\GAN\Paper\Analyst\Cấp thiết
```

Mục tiêu của bản này là đảo chiều kế hoạch: bắt đầu từ tài nguyên/code thầy chỉ trước, cụ thể là SQL Injection README của PayloadsAllTheThings, sau đó mới đối chiếu với nhóm paper cấp thiết, dataset paper, evaluator, baseline và reproduction.

## 1. Tài nguyên sẽ có và cần có

### 1.0. Tài nguyên thầy chỉ phải xử lý đầu tiên

| Tài nguyên | Đường dẫn | Vai trò mới trong kế hoạch | Việc cần làm ngay |
|---|---|---|---|
| PayloadsAllTheThings - SQL Injection | `https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/README.md` | Nguồn seed/taxonomy/operator đầu tiên; dùng để dựng baseline và data card trước khi chạy paper | Clone/tải repo hoặc đọc README, trích Tools, Entry Point Detection, DBMS Identification, Authentication Bypass, UNION/Error/Blind/Time/Stacked, Polyglot, Routed, Second Order, Generic WAF Bypass, Labs, ghi nguồn và phân loại |

Quyết định: tài nguyên này được coi là "code/tài nguyên thầy chỉ" trong giai đoạn 1. Nó không thay thế dataset gốc của các paper, nhưng là điểm xuất phát thực tế để tạo seed corpus, taxonomy, mutation operator, evaluator smoke test và baseline rule/mutation.

### 1.1. Tài nguyên paper OCR đã có

| Nhóm | File | Vai trò trong giai đoạn 1 | Dữ liệu/testbed nhắc trong paper |
|---|---|---|---|
| Paper lõi 1 | `Le_2024_GSQLi.md` | Paper chính để tái triển khai hoặc mô phỏng pipeline sinh/mutate payload SQLi chống detector/WAF | HttpParams, SSHS/Kaggle SQL Injection Dataset, Libinjection, RNN/GRU/BiLSTM detector, ModSecurity + OWASP CRS |
| Paper lõi 2 | `Lu_2022_GAN_SQLi.md` | Paper phụ-lõi để lấy ý tưởng GA/GAN và mutation/tamper baseline | Payload từ CVE/CNVD/exploit-db, hơn 2.000 payload sau cleaning, SQLParse, sqli-lab, SafeDog V4.0 |
| WAF evasion baseline | `Demetrio_2020_WAF_A_MoLE.md` | Baseline mạnh cho guided mutation chống WAF/ML-WAF | `wafamole-dataset`, SQLMap, MariaDB randgen, WAF-Brain, ModSecurity CRS |
| GAN pentesting | `Chowdhary_2023_GAN_Pentesting.md` | Related work và baseline ý tưởng conditional sequence GAN cho payload/WAF | PayloadBox XSS payload list, ModSecurity, AWS WAF, commercial WAF rules |
| Synthetic SQLi detection | `Dasari_2025_Enhancing_SQLi.md` | Related work cho VAE/U-Net/CWGAN-GP tạo synthetic SQL query để tăng detection | Kaggle `sqli.csv`, `Modified SQL Dataset.csv`, XGBoost/LightGBM/RF/KNN/SVM |
| Synthetic IDS context | `Agrawal_2024_GenAI_Synthetic.md` | Bối cảnh synthetic attack data cho dữ liệu mất cân bằng; không thay dataset SQLi payload | CICIDS2017, Web Attacks, Brute Force, CTGAN, Random Forest, XGBoost |
| Taxonomy SQLi | `Attack_Model_2012_Penetration_SQLi.md` | Nền phân loại SQLi và attack intent để làm taxonomy/validity/failure label | Không có dataset công khai; dùng làm taxonomy: tautology, illegal query, piggybacked query, first/second-order, bypass authentication |

### 1.2. Dataset và nguồn dữ liệu cần kiểm tra/tải

| Nguồn | Paper dùng/nhắc | Vai trò | Link/đường dẫn cần ghi vào inventory | Trạng thái giai đoạn 1 |
|---|---|---|---|---|
| HttpParams Dataset | `Le_2024_GSQLi.md` | Dataset chính để train GSQLi; paper nêu 19.304 normal và 5.557 SQLi | `https://github.com/Morzeux/HttpParamsDataset` | Tải sau khi đã xử lý PayloadsAllTheThings để đối chiếu paper |
| SSHS SQL Injection Dataset | `Le_2024_GSQLi.md` | Dataset đánh giá phụ; paper nêu 19.573 normal và 6.217 SQLi | `https://www.kaggle.com/syedsaqlainhussain/sql-injection-dataset` | Tải sau HttpParams nếu Kaggle truy cập được |
| WAF-A-MoLE dataset | `Demetrio_2020_WAF_A_MoLE.md` | Dataset SQL query benign/injection cho ML-WAF baseline | `https://github.com/blindusername/wafamole-dataset` | Dùng cho baseline WAF-A-MoLE/ML-WAF nếu tải được |
| SQLMap | `Demetrio_2020_WAF_A_MoLE.md`, `Lu_2022_GAN_SQLi.md` | Tham chiếu payload/tamper/mutation operators | `https://github.com/sqlmapproject/sqlmap` | Dùng làm nguồn mutation operator, không gọi là dataset paper |
| MariaDB randgen | `Demetrio_2020_WAF_A_MoLE.md` | Sinh query benign cho dataset SQL query | `https://github.com/MariaDB/randgen` | Tùy chọn nếu cần tạo benign SQL query |
| WAF-Brain | `Demetrio_2020_WAF_A_MoLE.md` | ML-WAF tham chiếu | `https://github.com/BBVA/waf-brain` | Tùy chọn, chỉ smoke test nếu nhanh |
| CVE/CNVD/exploit-db payload | `Lu_2022_GAN_SQLi.md` | Nguồn payload gốc trong paper Lu; paper không đưa dataset hoàn chỉnh | CVE, CNVD, exploit-db | Reproduction level nhiều khả năng là conceptual |
| Kaggle `sqli.csv` | `Dasari_2025_Enhancing_SQLi.md` | Dataset detection augmentation | Cần xác định trang Kaggle cụ thể từ paper/reference | Related work, không ưu tiên hơn HttpParams |
| `Modified SQL Dataset.csv` | `Dasari_2025_Enhancing_SQLi.md` | Dataset detection augmentation | Cần xác định link tải cụ thể | Related work, chỉ kiểm kê nếu tìm được |
| PayloadBox XSS payload list | `Chowdhary_2023_GAN_Pentesting.md` | Nguồn XSS payload cho GAN pentesting | `https://github.com/payloadbox/xss-payload-list` | Không trộn vào SQLi; chỉ làm analog cho sequence GAN/WAF |
| CICIDS2017 | `Agrawal_2024_GenAI_Synthetic.md` | IDS flow dataset cho Web Attacks/Brute Force | `https://www.unb.ca/cic/datasets/ids-2017.html` | Không dùng làm corpus SQLi payload; chỉ dùng bối cảnh synthetic IDS |

### 1.3. Đường dẫn thầy gợi ý cần đưa vào kế hoạch

Các link dưới đây lấy từ bản `Ke_hoach_trien_khai_GAN_SQLi_theo_gop_y_thay.md` và được dùng như tài nguyên triển khai, baseline hoặc testbed:

| Tài nguyên | Đường dẫn | Cách dùng trong giai đoạn 1 |
|---|---|---|
| PayloadsAllTheThings SQL Injection README | `https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/README.md` | Tài nguyên thầy chỉ, xử lý đầu tiên; seed corpus/taxonomy/operator thực tế cho SQLi |
| SecLists | `https://github.com/danielmiessler/SecLists` | Wordlist/payload tham chiếu cho baseline rule/mutation |
| SQLMap | `https://github.com/sqlmapproject/sqlmap` | Tham khảo tamper scripts và mutation operator |
| WAF-A-MoLE | `https://github.com/AvalZ/WAF-A-MoLE` | Baseline guided mutation nếu code chạy được |
| OWASP CRS | `https://github.com/coreruleset/coreruleset` | Rule set chính cho WAF local |
| ModSecurity | `https://github.com/owasp-modsecurity/ModSecurity` | WAF engine chính |
| Coraza | `https://github.com/corazawaf/coraza` | WAF engine thay thế nếu ModSecurity setup chậm |
| OWASP Juice Shop | `https://github.com/juice-shop/juice-shop` | Web app lab trong container nếu cần request-level test |
| CTGAN | `https://github.com/sdv-dev/CTGAN` | Baseline synthetic tabular cho IDS/detection, không thay GSQLi |
| TabDDPM | `https://github.com/yandex-research/tab-ddpm` | Diffusion baseline tham khảo, tạm hoãn giai đoạn 1 |
| CIC-IDS2017 | `https://www.unb.ca/cic/datasets/ids-2017.html` | Chỉ dùng khi nói synthetic IDS/Web Attacks, không trộn với SQLi payload |
| UNSW-NB15 | `https://research.unsw.edu.au/projects/unsw-nb15-dataset` | Dataset IDS tham khảo, không dùng làm SQLi payload corpus |
| Papers With Code | `https://paperswithcode.com/` | Tìm code phụ cho paper nếu repo chính thiếu |
| OWASP | `https://owasp.org/` | Chuẩn an toàn, Top 10, CRS, disclosure guidance |

### 1.4. Tài nguyên local cần tạo

```text
GAN/Data/raw/
GAN/Data/processed/
GAN/Data/manifests/dataset_inventory.csv
GAN/Data/manifests/source_cards.md
GAN/Data/splits/split_rule.md
GAN/Reports/01_paper_screening.md
GAN/Reports/02_dataset_inventory.md
GAN/Reports/03_baseline_results.md
GAN/Reports/04_reproduction_results.md
GAN/Reports/05_final_analysis.md
GAN/Reproduction/configs/evaluation_config.yaml
GAN/Reproduction/paper_models/selected_paper_reproduction_plan.md
GAN/Reproduction/results/
GAN/Reproduction/logs/
```

## 2. Quyết định thiết kế sau khi đọc nhóm cấp thiết

| Thành phần | Quyết định cập nhật |
|---|---|
| Đóng góp giai đoạn 1 | Protocol đánh giá tái lập cho sinh/mutate payload SQLi bằng generative hoặc mutation-guided methods |
| Chạy trước | PayloadsAllTheThings SQL Injection README do thầy chỉ |
| Paper đối chiếu sau | `Le_2024_GSQLi.md` |
| Baseline paper mạnh | `Demetrio_2020_WAF_A_MoLE.md` và mutation/tamper từ `Lu_2022_GAN_SQLi.md` |
| Related work không chạy trước | `Chowdhary_2023_GAN_Pentesting.md`, `Dasari_2025_Enhancing_SQLi.md`, `Agrawal_2024_GenAI_Synthetic.md` |
| Taxonomy/validity | `Attack_Model_2012_Penetration_SQLi.md` + OWASP + PayloadsAllTheThings |
| Dataset/seed chính ban đầu | PayloadsAllTheThings SQL Injection trước; HttpParams và SSHS/Kaggle dùng để đối chiếu/tái lập paper sau |
| Testbed chính | ModSecurity + OWASP CRS local; Coraza là phương án dự phòng |
| Baseline tối thiểu | Template/rule baseline từ PayloadsAllTheThings, mutation/tamper baseline, WAF-A-MoLE nếu chạy được |
| Metric tối thiểu | Validity, ASR/FNR theo WAF, uniqueness, novelty, duplicate rate, diversity, failure distribution |
| Tạm hoãn | Cloud WAF, nhiều WAF thương mại, CTGAN/TabDDPM full reproduction, IDS flow datasets không phải payload |

Kết quả cuối của giai đoạn 1 phải trả lời được:

> Từ tài nguyên thầy chỉ, mình dựng được seed corpus, taxonomy, baseline và evaluator đến mức nào; sau đó khi đối chiếu với GSQLi/paper thì paper model có tốt hơn baseline này ở đâu, kém ở đâu, và có đủ căn cứ để phát triển thành đề tài chính không?

## 3. Paper card rút gọn cần đưa vào báo cáo

### 3.1. Le 2024 - GSQLi

- Vai trò: paper lõi trực tiếp nhất cho SQLi payload mutation chống WAF/detector.
- Dữ liệu: HttpParams và SSHS/Kaggle; chọn normal và SQLi payload, ưu tiên payload ngắn hơn 100 ký tự do giới hạn Libinjection.
- Pipeline: Token Parser -> Mutation Vector -> Generator sinh mutation actions -> Payload Transformer -> Attack Classifier -> Discriminator/evaluator.
- Testbed: RNN/GRU/BiLSTM detector và ModSecurity + OWASP rule set.
- Metric paper: TPR/FNR. Metric đề tài phải bổ sung validity, novelty, uniqueness, diversity và failure label.
- Quyết định: tái triển khai/mô phỏng đầu tiên.

### 3.2. Lu 2022 - GAN SQLi

- Vai trò: paper phụ-lõi về sinh SQLi bằng GA + GAN/improved DCGAN/Wasserstein idea.
- Dữ liệu: payload từ CVE/CNVD/exploit-db, hơn 2.000 payload sau cleaning.
- Công cụ/testbed: SQLParse, phpstudy2018, sqli-lab Range, SafeDog V4.0.
- Giá trị cho đề tài: lấy mutation/tamper operators như base64, keyword case confusion, comment/space, overlong UTF-8, unicode-url, MySQL versioned comment.
- Quyết định: dùng để xây mutation baseline và conceptual reproduction nếu thiếu code/dataset.

### 3.3. Demetrio 2020 - WAF-A-MoLE

- Vai trò: baseline guided mutation rất quan trọng cho WAF/ML-WAF evasion.
- Dữ liệu/code: paper nêu dataset công khai `https://github.com/blindusername/wafamole-dataset`; code thầy gợi ý `https://github.com/AvalZ/WAF-A-MoLE`.
- Nguồn phụ: SQLMap, MariaDB randgen, WAF-Brain.
- Testbed: ML-based WAF, ModSecurity CRS.
- Quyết định: kiểm tra chạy code/dataset sau khi có evaluator; nếu chạy được thì đưa vào bảng so sánh chính.

### 3.4. Chowdhary 2023 - GAN Pentesting

- Vai trò: related work cho conditional sequence GAN và autonomous pentesting trên WAF.
- Dữ liệu: PayloadBox XSS payload list, không phải SQLi corpus chính.
- Testbed: ModSecurity, AWS WAF, commercial rules.
- Kết quả đáng chú ý: CGAN tốt hơn vanilla GAN, nhưng paper chủ yếu XSS và bypass thương mại thấp.
- Quyết định: dùng làm luận cứ rằng GAN sequence payload khó train và cần semantic tokenization; không chạy trước GSQLi.

### 3.5. Dasari 2025 - Enhancing SQLi Detection

- Vai trò: related work cho synthetic SQL query augmentation.
- Dữ liệu: Kaggle `sqli.csv`, `Modified SQL Dataset.csv`.
- Mô hình: VAE, U-Net, CWGAN-GP, pseudo-labeling, XGBoost.
- Metric: accuracy, precision, recall, F1, synthetic quality như MSE/R2/PCA.
- Quyết định: không ưu tiên tái triển khai vì trọng tâm là detection augmentation, không phải WAF payload evasion.

### 3.6. Agrawal 2024 - GenAI Synthetic Attack Detection

- Vai trò: bối cảnh synthetic data cho class imbalance trong IDS.
- Dữ liệu: CICIDS2017, Web Attacks và Brute Force minority classes.
- Mô hình: CTGAN + Random Forest/XGBoost.
- Quyết định: chỉ dùng để giải thích synthetic augmentation; không dùng CICIDS2017 làm dataset SQLi payload chính.

### 3.7. Attack Model 2012 - Penetration SQLi

- Vai trò: taxonomy nền cho SQLi và failure analysis.
- Nội dung dùng được: attack intent, first-order/second-order, tautology, illegal/logically incorrect query, piggybacked query, bypass authentication.
- Quyết định: dùng để gắn nhãn payload/failure và viết phần bối cảnh, không phải paper model.

## 4. Sản phẩm đầu ra bắt buộc

```text
GAN/Reports/01_paper_screening.md
GAN/Reports/00_teacher_resource_inventory.md
GAN/Survey/paper_cards/
GAN/Reports/02_dataset_inventory.md
GAN/Data/manifests/dataset_inventory.csv
GAN/Data/manifests/source_cards.md
GAN/Data/splits/split_rule.md
GAN/Reproduction/configs/evaluation_config.yaml
GAN/Reproduction/results/evaluator_smoke_test.md
GAN/Reports/03_baseline_results.md
GAN/Reproduction/results/baseline_metrics.csv
GAN/Reproduction/paper_models/selected_paper_reproduction_plan.md
GAN/Reports/04_reproduction_results.md
GAN/Reproduction/results/final_comparison_table.csv
GAN/Reports/05_final_analysis.md
```

## 5. Tuần 1 - Kiểm kê tài nguyên thầy chỉ trước

Mục tiêu: biến link thầy chỉ thành seed corpus, taxonomy, operator list và baseline đầu tiên.

Việc cần làm:

1. Xử lý `https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/README.md`.
2. Lập source card cho PayloadsAllTheThings SQL Injection:
   - repo/link
   - phạm vi nội dung
   - license nếu xác định được
   - loại payload/taxonomy có trong README
   - rủi ro trùng lặp và rủi ro dual-use
3. Trích các nhóm taxonomy ban đầu:
   - tools: sqlmap, ghauri và công cụ liên quan nếu có
   - entry point detection
   - DBMS identification
   - authentication bypass
   - union-based
   - error-based
   - boolean-based blind
   - time-based blind
   - out-of-band/OAST nếu có thể ghi nhận ở mức taxonomy
   - stacked/piggybacked query
   - polyglot injection
   - routed injection
   - second-order SQL injection
   - DBMS-specific payload
   - WAF/bypass/encoding/comment tricks
   - labs/thực hành an toàn nếu README dẫn ra
4. Tạo seed corpus bản đầu từ README nhưng không công bố payload bypass chi tiết trong báo cáo chính; báo cáo chỉ dùng thống kê/taxonomy.
5. Lập baseline rule/mutation tối thiểu từ taxonomy này.

Output:

```text
GAN/Reports/00_teacher_resource_inventory.md
GAN/Data/manifests/payloadsallthethings_sqli_source_card.md
GAN/Data/manifests/teacher_seed_inventory.csv
GAN/Data/processed/teacher_seed_sqli_normalized.csv
GAN/Reproduction/baselines/payloadsallthethings_rule_baseline.md
```

Tiêu chí đạt:

- Có bảng taxonomy từ link thầy chỉ.
- Có thống kê số payload/nhóm sau normalize/de-dup.
- Có baseline rule/mutation đầu tiên xuất phát từ PayloadsAllTheThings.
- Ghi rõ đây là seed/taxonomy thực tế, không phải dataset gốc của paper.

## 6. Tuần 2 - Kiểm kê paper cấp thiết và đối chiếu với tài nguyên thầy chỉ

Mục tiêu: biết paper nào bổ sung gì cho seed/taxonomy/baseline đã dựng từ link thầy chỉ.

Việc cần làm:

1. Lập paper card cho 7 file trong `GAN\Paper\Analyst\Cấp thiết`.
2. Tạo bảng đối chiếu: paper cần dataset nào, có trùng/khác gì so với PayloadsAllTheThings SQL Injection.
3. Gắn nhãn paper:
   - `core_sqli_generation`: Le 2024, Lu 2022.
   - `waf_evasion_baseline`: Demetrio 2020.
   - `gan_pentesting_related`: Chowdhary 2023.
   - `synthetic_detection_related`: Dasari 2025, Agrawal 2024.
   - `taxonomy_foundation`: Attack Model 2012.
4. Ghi rõ paper nào chạy sau và vì sao.

Output:

```text
GAN/Reports/01_paper_screening.md
GAN/Survey/paper_cards/*.md
GAN/Survey/tables/paper_inventory.csv
GAN/Survey/tables/resource_inventory.csv
GAN/Survey/tables/teacher_vs_paper_mapping.csv
```

Tiêu chí đạt:

- 7 paper cấp thiết có paper card.
- Có bảng link dataset/code/testbed.
- Chốt thứ tự mới: PayloadsAllTheThings trước, GSQLi là paper đối chiếu/tái lập sau.

## 7. Tuần 3 - Dataset/source inventory

Mục tiêu: biết nguồn nào dùng được thật và nguồn nào chỉ là related work.

Thứ tự kiểm tra:

1. PayloadsAllTheThings SQL Injection README và repo liên quan.
2. SecLists và SQLMap tamper scripts.
3. HttpParams Dataset.
4. SSHS/Kaggle SQL Injection Dataset.
5. WAF-A-MoLE dataset.
6. Nguồn CVE/CNVD/exploit-db theo Lu 2022, nếu không tái dựng được thì đánh dấu conceptual.
7. Kaggle `sqli.csv` và `Modified SQL Dataset.csv` của Dasari, nếu tìm được link.

Bảng inventory tối thiểu:

| Source | Paper/nguồn | Vai trò | Local file | Raw rows | Usable rows | Duplicate | Invalid | License | Label source | Status |
|---|---|---|---|---:|---:|---:|---:|---|---|---|
| PayloadsAllTheThings | Thầy gợi ý | Seed/taxonomy replacement | TBD | TBD | TBD | TBD | TBD | Repo | Rule/manual | TODO |
| SQLMap tamper | Thầy gợi ý/Lu/Demetrio | Mutation operators | TBD | N/A | N/A | N/A | N/A | Repo | Operator source | TODO |
| HttpParams | Le 2024 | Train/eval GSQLi | TBD | TBD | TBD | TBD | TBD | TBD | Paper labels | TODO |
| SSHS/Kaggle | Le 2024 | Eval GSQLi | TBD | TBD | TBD | TBD | TBD | TBD | Paper labels | TODO |
| WAF-A-MoLE dataset | Demetrio 2020 | ML-WAF/baseline | TBD | TBD | TBD | TBD | TBD | TBD | Paper labels | TODO |

Output:

```text
GAN/Reports/02_dataset_inventory.md
GAN/Data/manifests/dataset_inventory.csv
GAN/Data/manifests/source_cards.md
GAN/Data/splits/split_rule.md
```

Tiêu chí đạt:

- Có ít nhất một SQLi payload corpus chạy được.
- Có số raw/usable/duplicate/invalid.
- Có split rule tránh leakage: train/validation/test tách theo normalized payload và near-duplicate.
- Ghi rõ nguồn nào là dataset paper, nguồn nào là replacement/seed.

## 8. Tuần 4 - Evaluator và WAF smoke test

Mục tiêu: mọi phương pháp sinh payload đều được đo bằng cùng bộ đo.

Evaluator tối thiểu:

| Thành phần | Chức năng |
|---|---|
| Normalize/de-dup | Chuẩn hóa payload và loại trùng exact |
| Validity checker | Kiểm tra SQLi-like syntax/taxonomy bằng rule nhẹ, SQLParse/libinjection nếu dùng được |
| Novelty checker | So với train/seed bằng exact và near-duplicate |
| Diversity checker | Unique ratio, token entropy hoặc distance |
| WAF runner | Gửi payload vào ModSecurity + OWASP CRS local và ghi allow/block/rule hit |
| Failure labeler | Gắn nhãn theo taxonomy: invalid SQLi-like, duplicate, blocked by WAF, too long, parser fail |
| Aggregator | Xuất metric thống nhất |

Output:

```text
GAN/Reproduction/configs/evaluation_config.yaml
GAN/Reproduction/results/evaluator_smoke_test.md
GAN/Reproduction/logs/waf_smoke_test.log
```

Tiêu chí đạt:

- Chạy được evaluator trên 20-50 payload.
- Có log WAF allow/block.
- Có config để chạy lại.

## 9. Tuần 5 - Baseline từ tài nguyên thầy chỉ, sau đó mới mở rộng WAF-A-MoLE

Mục tiêu: có mốc so sánh xuất phát từ link thầy chỉ trước khi chạy GSQLi.

Baseline bắt buộc:

1. Template/rule baseline từ PayloadsAllTheThings SQL Injection.
2. Mutation baseline từ PayloadsAllTheThings + SQLMap tamper scripts.
3. Bổ sung operator từ Lu 2022.
4. WAF-A-MoLE guided mutation nếu code/dataset chạy được trong thời gian hợp lý.

Nhóm mutation operator tối thiểu:

- Case swapping.
- Inline comment/comment insertion.
- Whitespace swapping.
- Logical operator swapping.
- Encoding: URL/unicode/base64 nếu evaluator xử lý được.
- MySQL versioned comment.
- String/number representation variation.

Output:

```text
GAN/Reports/03_baseline_results.md
GAN/Reproduction/results/baseline_metrics.csv
GAN/Reproduction/logs/baseline_run_<date>.log
```

Tiêu chí đạt:

- Ít nhất 2 baseline chạy qua cùng evaluator.
- Có số liệu thật.
- Có failure analysis ngắn cho từng baseline.

## 10. Tuần 6 - Kiểm kê code/model thầy chỉ còn lại

Mục tiêu: sau khi đã xử lý link PayloadsAllTheThings, kiểm kê các code/model khác nếu thầy còn chỉ thêm.

Việc cần làm:

1. Xác định chính xác thư mục/link/code thầy chỉ.
2. Lập inventory:
   - train script
   - generate script
   - evaluate script
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

## 11. Tuần 7-8 - Tái triển khai/mô phỏng GSQLi 2024

Mục tiêu: dùng baseline từ tài nguyên thầy chỉ làm mốc, sau đó tạo ít nhất một output từ pipeline paper lõi và đo bằng evaluator chung.

Reproduction level:

| Level | Khi dùng |
|---|---|
| Exact | Có code, dataset, config đủ |
| Partial | Có dataset hoặc mô tả đủ nhưng thiếu một số chi tiết |
| Conceptual | Chỉ có mô tả paper, phải tự dựng pipeline tương đương |

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

- Dựng mutation-action ablation theo đúng mutation set của paper.
- Ghi rõ đây là conceptual/ablation reproduction, chưa phải GAN đầy đủ.
- Vẫn đo bằng cùng evaluator với baseline.

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

## 12. Tuần 9 - So sánh tổng hợp

Mục tiêu: kết luận bằng số liệu, không chỉ bằng nhận xét.

Bảng chính:

| Method | Source | Validity | ASR/FNR | Uniqueness | Novelty | Diversity | Duplicate rate | Runtime | Main failure |
|---|---|---:|---:|---:|---:|---:|---:|---:|---|
| Template/rule | PayloadsAllTheThings | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Mutation/tamper | PayloadsAllTheThings + SQLMap | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| WAF-A-MoLE | Demetrio baseline | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| Teacher code | Internal | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |
| GSQLi reproduction | Le 2024 | TBD | TBD | TBD | TBD | TBD | TBD | TBD | TBD |

Câu hỏi kết luận:

1. Dataset nào tải được và dataset nào chỉ mô phỏng được?
2. Method nào tái lập được?
3. Method nào không tái lập được và vì sao?
4. Method nào thắng baseline ở metric nào?
5. Method nào chỉ copy/near-copy seed?
6. Method nào bị mode collapse hoặc duplicate cao?
7. Method nào có failure đáng học để phát triển phase 2?

Output:

```text
GAN/Reproduction/results/final_comparison_table.csv
GAN/Reports/05_final_analysis.md
```

## 13. Tuần 10 - Báo cáo trình bày

Cấu trúc báo cáo:

1. Bài toán đã thu hẹp.
2. Tài nguyên thầy chỉ: PayloadsAllTheThings SQL Injection, đã trích gì và dùng thế nào.
3. Tài nguyên và dataset paper: có gì, cần gì, lấy từ paper nào.
4. Paper cấp thiết và vai trò từng paper.
5. Dataset/source inventory.
6. Evaluator và WAF testbed.
7. Baseline từ tài nguyên thầy chỉ.
8. Code thầy/model paper.
9. Bảng so sánh.
10. Failure analysis.
11. Hướng giai đoạn 2.

Output:

```text
GAN/Reports/final_reproduction_report.md
GAN/Reports/final_slide_outline.md
```

## 14. Ngưỡng nghiệm thu giai đoạn 1

| Hạng mục | Ngưỡng đạt |
|---|---|
| Tài nguyên thầy chỉ | PayloadsAllTheThings SQL Injection có source card, taxonomy, seed inventory và baseline đầu tiên |
| Paper inventory | 7 paper cấp thiết có paper card và vai trò rõ |
| Resource inventory | Có bảng dataset/code/testbed/link/status |
| Dataset inventory | Có raw/usable/duplicate/invalid cho ít nhất một SQLi corpus |
| Evaluator | Chạy được sample nhỏ và xuất metric |
| WAF testbed | Có log allow/block local |
| Baseline | Ít nhất 2 baseline có kết quả |
| WAF-A-MoLE | Có smoke test hoặc failure report cụ thể |
| Code thầy/paper model | Có smoke test hoặc reproduction result/failure report |
| So sánh | Có bảng chung giữa baseline, code thầy và GSQLi |
| Phân tích | Có failure analysis và giới hạn |

## 15. Rủi ro và phương án xử lý

| Rủi ro | Cách xử lý |
|---|---|
| PayloadsAllTheThings quá rộng và nhiều payload nhạy cảm | Chỉ trích metadata/taxonomy/thống kê, lưu payload local có kiểm soát, không đưa payload bypass chi tiết vào báo cáo |
| HttpParams/SSHS không tải được | Dùng PayloadsAllTheThings/SecLists làm replacement corpus, ghi rõ không phải exact reproduction |
| Dataset Lu 2022 không công khai | Tái dựng conceptual từ CVE/CNVD/exploit-db hoặc dùng mutation operators làm baseline |
| WAF-A-MoLE code không chạy | Lấy operator/algorithm làm baseline tự dựng và ghi failure report |
| GAN không train ổn | Báo cáo duplicate/entropy/loss; dùng mutation-action ablation để giữ tiến độ |
| ModSecurity setup chậm | Dùng Coraza hoặc evaluator offline trước, WAF smoke test sau |
| Metric ASR/FNR gây hiểu nhầm dual-use | Báo cáo thống kê tổng hợp, không công bố payload bypass chi tiết |
| Scope phình rộng | Giữ đúng 1 paper chính, 2-3 baseline, 1 WAF chính |

## 16. Kết luận kế hoạch

Giai đoạn 1 không cố chứng minh ngay "GAN tốt hơn". Giai đoạn này phải chứng minh được năng lực nghiên cứu:

- Biết chọn paper đúng và phân vai paper.
- Biết bắt đầu từ tài nguyên thầy chỉ, rồi mới đối chiếu paper.
- Biết dataset đến từ đâu và có dùng được thật không.
- Biết phân biệt dataset paper với seed corpus thay thế.
- Biết chạy baseline trước khi nói model tốt.
- Biết đo mọi method bằng cùng evaluator.
- Biết tái triển khai hoặc báo cáo failure trung thực.
- Biết kết luận hướng tiếp theo dựa trên số liệu.

Sau giai đoạn 1, đề tài nên chuyển từ "có kế hoạch" sang "có bằng chứng ban đầu": dataset inventory, evaluator, baseline, reproduction/failure report và bảng so sánh.
