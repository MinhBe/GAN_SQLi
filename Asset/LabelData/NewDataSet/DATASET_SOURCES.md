# Dataset Sources — `NewDataSet/` (Bổ sung)

> **Mục đích:** Ghi lại toàn bộ nguồn dữ liệu **mới** đã thu thập trong thư mục `Asset/LabelData/NewDataSet/`, kèm số liệu thực đo, schema, mục đích sử dụng trong project **SeqGAN-SQLi**, phục vụ trích dẫn học thuật & reproducibility.
>
> **Tham chiếu file gốc:** `Asset/LabelData/DATASET_SOURCES.md` (5 nguồn ban đầu: Kaggle sajid576, sqliv5-dataset, sqlmap payloads, SecLists, ExploitDB). File này **không thay thế** mà **bổ sung** cho file gốc.

**Ngày cập nhật:** 2026-05-18
**Thư mục gốc:** `C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\NewDataSet\`
**File hợp nhất hiện tại (đã tự gán nhãn type/db_engine):** `../combined_labeled_data.csv` (40,860 dòng, schema `payload_norm, sqli_type, db_engine, confidence, reasoning`).

> **Cập nhật 2026-05-18 (bổ sung lần 2):** Đã tải thêm 11 nguồn mới (xem mục [Phần II](#phần-ii--nguồn-bổ-sung-lần-2-tải-2026-05-18) bên dưới): CSIC 2010 + ECML/PKDD 2007 combined, PayloadsAllTheThings, fuzzdb, payloadbox, Spider eval, b-mc2/sql-create-context, Gretelai synthetic SQL, chatML SQLi, Zenodo NetFlow (2 file). **Tổng benign SQL bổ sung: ~192,000 dòng** (giải quyết gap mất cân bằng class).

---

## Tổng Quan

| # | Tên nguồn | Loại | Rows (đo thực tế) | Có nhãn attack type? | Trạng thái |
|---|-----------|------|------------------:|----------------------|------------|
| 1 | `bccc_sfu/` — BCCC-SFU-SQLInj-2023 | CSV (raw payload) | 11,011 | Không (chỉ payload SQLi) | ✅ Đã tải |
| 2 | `gist_johntroony/` — Troony SQLi Payloads | TXT wordlist | 622 | Không | ✅ Đã tải |
| 3 | `github_ajinmathew/` — SQL-data | CSV `Sentence,Label` | 37,961 (4,200 + 33,761) | Không (binary) | ✅ Đã tải — *có thể trùng nội dung với #6, #13* |
| 4 | `github_http_params/` — HttpParamsDataset | CSV multi-class | 31,067 (full) | **Có** (norm/sqli/xss/cmdi/path-traversal) | ✅ Đã tải |
| 5 | `github_rbsqli/` — RbSQLi Notebooks | Jupyter notebooks | — (chỉ code, không có csv kèm) | — | ⚠️ Chỉ tải notebooks, dataset csv tham chiếu nằm ở `rbsqli_dataset.csv` (#15) |
| 6 | `github_sqliv5/` — nidnogg/sqliv5-dataset | CSV + JSON | 68,879 (CSV); JSON V4/V5 thêm ~162k dòng JSON | Không (binary) | ✅ Đã tải đầy đủ — *trùng tên file với #3, #13* |
| 7 | `github_wafamole/` — WAF-A-MoLE | (Jekyll site, KHÔNG phải dataset) | 0 | — | ❌ **Clone nhầm** repo — chỉ có site, cần clone lại |
| 8 | `github_yogsec_payloads/` — SQL-Injection-Payloads | 13 file TXT theo attack type | 3,926 (tổng) | **Có** (12 loại — qua tên file) | ✅ Đã tải |
| 9 | `huggingface/` — sharegpt_sqli_v2 | CSV (ShareGPT JSON) | 4,312 | — (Q&A, không phải payload) | ✅ Đã tải |
| 10 | `kaggle/ayahkhaldi_sql-injection-dataset/` | CSV `Query,Label` | 171,986 (Train 103,168 + Test 34,388 + Val 34,430) | Không (binary) | ✅ Đã tải |
| 11 | `kaggle/gambleryu_biggest-sql-injection-dataset/` | CSV `Query,Label` | 156,875 | Không (binary) | ✅ Đã tải |
| 12 | `kaggle/sajid576_sql-injection-dataset/` | CSV `Query,Label` | 30,919 | Không (binary) | ✅ Đã tải (đã có ở `DATASET_SOURCES.md` gốc) |
| 13 | `kaggle/syedsaqlainhussain_sql-injection-dataset/` | CSV `Sentence,Label` (UTF-16 BOM) | 68,880 (4,200 + 33,761 + 30,919) | Không (binary) | ✅ Đã tải — *trùng tên file với #3, #6* |
| 14 | `mendeley_SQLI_Dataset.csv` | CSV feature-engineered (19 cột) | 47,463 | Có (binary `label`) — không có payload thô | ✅ Đã tải |
| 15 | `rbsqli_dataset.csv` | CSV rule-based multi-class | **10,190,450** | **Có (7 lớp `injection_type`)** | ✅ Đã tải |
| 16 | `zenodo_dataset.csv` | CSV multi-class + split sẵn | **3,741,069** | **Có (`attack_technique`, `tamper_method`)** | ✅ Đã tải |
| 17 | `zenodo/` (thư mục) | (rỗng) | 0 | — | ⚠️ Thư mục rỗng — cần làm rõ |
| 18 | `anubis.pdf` | PDF tài liệu | (12 KB) | — | ⚠️ Không phải dataset — có thể là paper đặt nhầm chỗ |

**Tổng rows raw (trước dedup):** ~14.4 triệu — chủ yếu từ `rbsqli_dataset.csv` (10.2M) + `zenodo_dataset.csv` (3.7M).
**Tổng có nhãn loại tấn công (multi-class) cộng dồn:** ~14.0 triệu mẫu (rbsqli + zenodo + http_params + yogsec).

⚠️ **Lưu ý quan trọng về trùng lặp:** Các thư mục `github_ajinmathew/`, `github_sqliv5/`, `kaggle/syedsaqlainhussain_*/` đều chứa file tên `sqli.csv` (4,200 dòng) và `sqliv2.csv` (33,761 dòng). **Số dòng trùng khớp** ⇒ có khả năng cao là cùng dataset, nhưng **nội dung có thể khác nhau** (thứ tự dòng, encoding, escape ký tự). **Hiện chưa dedup** — giữ nguyên cả 3 để so sánh sau bằng script chuẩn hoá.

---

## Chi Tiết Từng Nguồn

### 1. `bccc_sfu/` — BCCC-SFU-SQLInj-2023
| Trường | Thông tin |
|--------|----------|
| **URL** | https://www.unb.ca/cic/datasets/sqli-2023.html (BCCC-SFU @ University of New Brunswick) |
| **File** | `BCCC-SFU-SQLInj-2023.csv` (11,011 dòng) |
| **Schema** | `,Data` — cột `Data` chứa raw SQLi query (nhiều dòng cực dài, có escape phức tạp) |
| **Mục đích** | Pretrain corpus payload thô — query thực tế dài, đa dạng cú pháp |
| **Trích dẫn** | BCCC-SFU SQL Injection Dataset 2023, University of New Brunswick / Simon Fraser University |

### 2. `gist_johntroony/` — Troony SQLi Payloads
| Trường | Thông tin |
|--------|----------|
| **URL** | https://gist.github.com/johntroony |
| **File** | `Troony_SQLi_Payloads.txt` (622 dòng) |
| **Schema** | Plaintext, mỗi dòng = 1 payload |
| **Mục đích** | Seed payload bổ sung cho rollout/pretrain |
| **Trích dẫn** | johntroony, "SQLi Payloads", GitHub Gist |

### 3. `github_ajinmathew/` — SQL-data
| Trường | Thông tin |
|--------|----------|
| **URL** | https://github.com/ajinmathew/SQL-data |
| **Files** | `sqli.csv` (4,200), `sqliv2.csv` (33,761) — **tổng 37,961** |
| **Schema** | `Sentence,Label` (binary 0/1) |
| **Mục đích** | Pretrain corpus binary classification |
| **Ghi chú** | Tên file trùng với #6, #13 — chưa dedup, kiểm tra sau bằng script |

### 4. `github_http_params/` — HttpParamsDataset
| Trường | Thông tin |
|--------|----------|
| **URL** | https://github.com/Morzeux/HttpParamsDataset |
| **Files** | `payload_full.csv` (31,067), `payload_train.csv` (20,712), `payload_test.csv` (10,355), `payload_test_lexical.csv` |
| **Schema** | `payload,length,attack_type,label` |
| **Phân bố** | norm: 19,304 — sqli: 10,852 — xss: 532 — cmdi: 89 — path-traversal: 290 |
| **Mục đích** | **Multi-class web attack baseline** — gold label cho attack type (sqli/xss/cmdi/path), có cả benign |
| **Nguồn gốc** | Tổng hợp từ CSIC2010 (benign), sqlmap (SQLi), xssya (XSS), Vega + FuzzDB (cmdi/path-traversal) |
| **Trích dẫn** | Š. Morzeux, "HttpParamsDataset", luận văn tốt nghiệp |

### 5. `github_rbsqli/` — RbSQLi-Dataset (Notebooks)
| Trường | Thông tin |
|--------|----------|
| **URL** | https://github.com/(RbSQLi-Dataset repo) |
| **Files** | 3 notebook trong `cross_validation_binary_sql_injection/`, `EDA/Total_Appearance_of_SQL_Keywords.ipynb`, `Model Train/Stratified_Model_Train.ipynb`, `Model Train/model_comparison_nb_rf_knn_lr.ipynb` |
| **Mục đích** | Tham khảo pipeline ML baseline (NB/RF/SVC/KNN/LR) — code, không có csv kèm |
| **Ghi chú** | Dataset csv của repo nằm tách ở `rbsqli_dataset.csv` (#15) |

### 6. `github_sqliv5/` — nidnogg/sqliv5-dataset
| Trường | Thông tin |
|--------|----------|
| **URL** | https://github.com/nidnogg/sqliv5-dataset |
| **Files CSV** | `sqli.csv` (4,200), `sqliv2.csv` (33,761), `SQLiV3.csv` (30,918) — **tổng 68,879** |
| **Files JSON** | `SQLiV3.json`, `SQLiV3_clean.json`, `SQLiV4.json`, `SQLiV5.json` (V5 ~162k dòng, mới nhất) |
| **Schema** | CSV: `Sentence,Label`; JSON: mảng object |
| **Mục đích** | Pretrain corpus — V5 chứa cả adversarial examples sinh bởi WAF-A-MoLE |
| **Trích dẫn** | nidnogg, "sqliv5-dataset", GitHub. Bản gốc V3 trên Kaggle bởi Syed Saqlain Hussain |
| **Ghi chú** | Trùng tên file với #3, #13 — chưa dedup |

### 7. `github_wafamole/` — ⚠️ CLONE NHẦM
| Trường | Thông tin |
|--------|----------|
| **Tình trạng** | Repo hiện tại **không phải** mã nguồn WAF-A-MoLE thật. Nội dung chỉ là site Jekyll: `_config.yml`, `404.html`, `Gemfile`, `assets/`, `index.md`, `info.md`, `leaders.md`, `tab_example.md`, `LICENSE.md`, `CONTRIBUTING.md`, `SECURITY.md`. Không có code Python `wafamole/`, không có dataset adversarial. |
| **URL đúng cần clone lại** | https://github.com/AvalZ/WAF-A-MoLE (repo gốc của Valenza & Demetrio) |
| **URL thay thế** | https://github.com/nidnogg/wafamole-plusplus (bản mở rộng) |
| **Mục đích dự kiến** | Sinh adversarial SQLi payload bypass WAF — dùng làm hard-negative cho training hoặc baseline so sánh chất lượng payload do SeqGAN sinh ra |
| **TODO** | (1) Xóa thư mục clone nhầm hiện tại; (2) `git clone https://github.com/AvalZ/WAF-A-MoLE.git github_wafamole`; (3) Chạy `wafamole.cli` để sinh adversarial dataset; (4) Cập nhật lại mục này khi hoàn tất |
| **Trích dẫn** | A. Valenza, L. Demetrio, "WAF-A-MoLE: Evading Web Application Firewalls through Adversarial Machine Learning" |

### 8. `github_yogsec_payloads/` — SQL-Injection-Payloads
| Trường | Thông tin |
|--------|----------|
| **URL** | https://github.com/yogsec/SQL-Injection-Payloads |
| **Files (13 × TXT, ~3,926 dòng tổng)** | `Boolean_Based` 299 · `Comment_Based` 299 · `DNS_Exfiltration` 299 · `Error_Based` 319 · `Hybrid` 299 · `OOB` 299 · `Second_Order` 299 · `Stacked_Queries` 299 · `Stored_Procedure` 299 · `Time_Based` 299 · `Union_Based` 319 · `WAF_Bypass` 299 |
| **Schema** | Plaintext, mỗi dòng = 1 payload; **nhãn loại tấn công nằm ở tên file** |
| **Mục đích** | **Gold label seed** cho 12 loại attack type — rất giá trị để khởi tạo type classifier hoặc gán nhãn semi-supervised |
| **Trích dẫn** | yogsec (Abhinav Singwal), "SQL-Injection-Payloads", GitHub |

### 9. `huggingface/` — sharegpt_sqli_v2
| Trường | Thông tin |
|--------|----------|
| **URL** | https://huggingface.co/datasets/ (sharegpt_sqli_v2) |
| **File** | `sharegpt_sqli_v2.csv` (4,312 dòng) |
| **Schema** | `conversations` — JSON ShareGPT format `[{from, value}, ...]` |
| **Mục đích** | **Không phải payload pool** — dataset Q&A để fine-tune LLM giải thích/giảng dạy SQLi. Có thể dùng cho rationale generation hoặc instruction tuning, không trực tiếp cho SeqGAN |
| **Trích dẫn** | Hugging Face dataset hub |

### 10. `kaggle/ayahkhaldi_sql-injection-dataset/`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://www.kaggle.com/datasets/ayahkhaldi/sql-injection-dataset |
| **Files** | `Train.csv` (103,168), `Test.csv` (34,388), `Validation.csv` (34,430) — **tổng 171,986** |
| **Schema** | `Query,Label` (binary) |
| **Mục đích** | **Pretrain corpus lớn nhất** — đã có sẵn 3-way split |
| **Trích dẫn** | Ayah Khaldi, Kaggle, truy cập 2026-05 |

### 11. `kaggle/gambleryu_biggest-sql-injection-dataset/`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://www.kaggle.com/datasets/gambleryu/biggest-sql-injection-dataset |
| **File** | `clean_sql_dataset.csv` (156,875) |
| **Schema** | `Query,Label` (binary) |
| **Mục đích** | Pretrain corpus binary — nguồn lớn thứ 2 |
| **Trích dẫn** | Gambleryu, Kaggle |

### 12. `kaggle/sajid576_sql-injection-dataset/`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://www.kaggle.com/datasets/sajid576/sql-injection-dataset |
| **File** | `Modified_SQL_Dataset.csv` (30,919) |
| **Schema** | `Query,Label` (binary) |
| **Mục đích** | Pretrain corpus — đã đề cập trong `DATASET_SOURCES.md` gốc, nay tải về thực |
| **Trích dẫn** | sajid576, Kaggle |

### 13. `kaggle/syedsaqlainhussain_sql-injection-dataset/`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://www.kaggle.com/datasets/syedsaqlainhussain/sql-injection-dataset |
| **Files** | `sqli.csv` (4,200), `sqliv2.csv` (33,761), `SQLiV3.csv` (30,919) — **tổng 68,880** |
| **Schema** | `Sentence,Label` (binary). File gốc encoding UTF-16 BOM với khoảng trắng giữa ký tự — cần re-encode khi load |
| **Mục đích** | Bản gốc SQLi-v1/v2/v3 (nguồn upstream của #3, #6) |
| **Trích dẫn** | Syed Saqlain Hussain, Kaggle |
| **Ghi chú** | Trùng tên file với #3, #6 — chưa dedup |

### 14. `mendeley_SQLI_Dataset.csv`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://data.mendeley.com/ (SQLi Dataset — feature-engineered) |
| **File** | `mendeley_SQLI_Dataset.csv` (47,463 dòng) |
| **Schema (19 cột)** | `no_letter, no_digit, no_special_char, no_keyword, length, entropy, no_semicolon, no_single_qout, no_double_qout, no_percentage, whit_space, no_punctuation, no_logical_operat, no_operat, no_or, no_and, no_comment, no_nullValue, label` |
| **Mục đích** | **Không phải payload thô** — đã extract feature. Dùng cho tabular ML baseline (Decision Tree, XGBoost) để so sánh với phương pháp deep learning. Không dùng trực tiếp cho SeqGAN |
| **Trích dẫn** | Mendeley Data dataset |

### 15. `rbsqli_dataset.csv`
| Trường | Thông tin |
|--------|----------|
| **File** | `rbsqli_dataset.csv` (**10,190,450 dòng** — ~800 MB+) |
| **Nguồn** | RbSQLi-Dataset repo (xem #5) — dataset rule-based generated |
| **Schema (9 cột)** | `sql_query, injection_type, vulnerability_status, sql_command, target_table, selected_columns, comparison_operator, logical_operator, sql_comment_syntax` |
| **Phân bố `injection_type`** (đo trên 200k dòng đầu) | None_Type: 147,143 · Error-Based: 16,140 · Time-Based: 11,108 · meta_based: 9,407 · Union-Based: 7,746 · stackqueries_based: 4,378 · boolean-based: 4,078 — **7 lớp** |
| **Mục đích** | **Gold label nguồn chính cho multi-class type classifier** (Error/Time/Union/Boolean/Stacked/Meta/None). Cực kỳ giá trị; cần subsample do quá lớn |
| **Trích dẫn** | RbSQLi-Dataset, GitHub |

### 16. `zenodo_dataset.csv`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://zenodo.org/ (SQLi dataset với attack_technique + tamper) |
| **File** | `zenodo_dataset.csv` (**3,741,069 dòng**) |
| **Schema (11 cột)** | `full_query, label, user_inputs, attack_stage, tamper_method, attack_status, statement_type, query_template_id, attack_id, attack_technique, split` |
| **Mục đích** | **Gold label multi-class** với cả `attack_technique` (boolean, equaltolike, …) và `tamper_method` (sqlmap-style obfuscation). Có **`split` train/test sẵn**. Dùng cho type classifier + đánh giá tamper diversity của payload sinh bởi SeqGAN |
| **Trích dẫn** | Zenodo dataset |

### 17. `zenodo/` (thư mục rỗng)
| Trường | Thông tin |
|--------|----------|
| **Trạng thái** | Thư mục tồn tại nhưng **rỗng** |
| **TODO** | (1) Kiểm tra có script tải dở dang không; (2) Quyết định xóa thư mục hoặc tải bổ sung dataset Zenodo khác |

### 18. `anubis.pdf` (root)
| Trường | Thông tin |
|--------|----------|
| **File** | `anubis.pdf` (12 KB) |
| **Trạng thái** | ⚠️ **Không phải dataset** — có thể là paper/tài liệu tham khảo đặt nhầm chỗ |
| **TODO** | Di chuyển sang `Asset/paper/` hoặc xác minh có phải Anubis dataset (Android malware?) đặt nhầm không |

---

## Phân Loại Theo Vai Trò Trong Project SeqGAN-SQLi

### A. Pretrain corpus — SQLi payload thô, nhãn nhị phân
*Dùng để train generator (G) ở giai đoạn MLE pretraining và discriminator (D) phân biệt SQLi/benign.*
- `kaggle/ayahkhaldi` (171,986) — có split sẵn
- `kaggle/gambleryu` (156,875)
- `github_sqliv5` (68,879 CSV + JSON V4/V5)
- `kaggle/syedsaqlainhussain` (68,880) — gốc upstream
- `mendeley` (47,463 — **features only**, không dùng trực tiếp cho G)
- `github_ajinmathew` (37,961) — mirror
- `kaggle/sajid576` (30,919)
- `bccc_sfu` (11,011)
- `github_http_params` (31,067 — đa nhãn, có thể filter SQLi only ~10,852)
- `gist_johntroony` (622)

**≈ 470k–625k mẫu khả dụng (trước dedup).**

### B. Multi-class attack type labeling — Gold label
*Dùng cho type classifier hoặc gán nhãn cho generator có điều kiện (conditional SeqGAN).*
- `rbsqli_dataset.csv` (10.2M, 7 lớp `injection_type`)
- `zenodo_dataset.csv` (3.7M, `attack_technique` + `tamper_method` + split sẵn)
- `github_http_params` (31k, 5 lớp: norm/sqli/xss/cmdi/path)
- `github_yogsec_payloads` (3,926, 12 lớp qua tên file)
- *(File cũ)* `sqlmap_payloads` (XML 6 lớp) — xem `DATASET_SOURCES.md` gốc

### C. Feature-engineered (tabular baseline)
- `mendeley_SQLI_Dataset.csv` — 19 hand-crafted features, không có payload thô

### D. Q&A / instruction tuning (không phải payload)
- `huggingface/sharegpt_sqli_v2.csv` — dataset hội thoại về SQLi cho LLM

### E. Cần xử lý / không sử dụng trực tiếp
- `github_wafamole/` — clone nhầm, cần re-clone
- `zenodo/` — rỗng
- `anubis.pdf` — không phải dataset

---

## Tổng Kết Số Liệu

| Nhóm | Tổng rows (raw) | Có nhãn type? |
|------|----------------:|---------------|
| A. Pretrain binary (SQLi) | ~625,000 | Không (binary) |
| B. Multi-class type | ~14,000,000 | **Có** |
| C. Feature-engineered | 47,463 | Có (binary) |
| D. Q&A | 4,312 | — |
| **[MỚI] E. Benign SQL** | **192,462** | Không (label=0) |
| **[MỚI] F. Full HTTP requests** | **84,957** | Có (Valid/Anomalous) |
| **[MỚI] G. NetFlow** | **457,232** | Có (binary 50/50) |
| **[MỚI] H. Curated payload by DBMS** | ~2,500 (MD+TXT) | **Có (DBMS type)** |
| **Tổng** | **~15.4 triệu** | |

---

## Việc Cần Làm Tiếp

**Còn thiếu (chưa tải được):**
- [ ] **IEEE DataPort 2025** (244k) — đăng ký free tại ieee-dataport.org rồi tải `SQL_Injection_Detection_Dataset.csv`
- [ ] **BIRD-SQL** (9,428 benign SQL) — tải tại https://bird-bench.github.io/
- [ ] **Re-clone WAF-A-MoLE thật** từ `https://github.com/AvalZ/WAF-A-MoLE`

**Dọn dẹp:**
- [ ] **Xóa hoặc note** `github_csic_2010/` (chỉ có README, thay thế bởi #19 `github_csic_ecml_combined/`)
- [ ] **Di chuyển `anubis.pdf`** sang `Asset/paper/`
- [ ] **Làm rõ `zenodo/`** rỗng — xóa nếu không cần

**Xử lý data:**
- [ ] **Viết script chuẩn hoá schema** chung `{payload, binary_label, attack_type, db_engine, source, split}` áp dụng cho tất cả nguồn
- [ ] **Dedup** giữa `github_ajinmathew/`, `github_sqliv5/`, `kaggle/syedsaqlainhussain/` (sqli.csv / sqliv2.csv cùng số dòng)
- [ ] **Subsample** `rbsqli_dataset.csv` (10.2M) và `zenodo_dataset.csv` (3.7M) — stratified theo `injection_type`/`attack_technique`
- [ ] **Merge benign SQL** (192,462 dòng từ #23-25) vào balanced corpus với SQLi
- [ ] **Parse PayloadsAllTheThings markdown** (regex extract code blocks) → CSV per DBMS

---

## Ghi Chú Pháp Lý & Đạo Đức

> Toàn bộ dữ liệu được thu thập từ nguồn **công khai, hợp pháp** (GitHub/Kaggle/Hugging Face/Zenodo/Mendeley public). Một số nguồn payload (yogsec, johntroony, sqlmap) thuộc loại "offensive security tools" — chỉ phục vụ **nghiên cứu học thuật** về detection & defense.
>
> **Không** sử dụng dataset hay model sinh ra để tấn công hệ thống thật. Mọi báo cáo/luận văn phát sinh từ dữ liệu này cần trích dẫn đầy đủ nguồn gốc tại bảng trên.
