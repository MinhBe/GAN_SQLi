# Dataset Sources — GAN_SQLi Project (NewDataSet)
> **Mục đích:** Ghi lại toàn bộ nguồn dữ liệu đã thu thập trong `NewDataSet/`, ngày lấy, vị trí lưu trữ và trạng thái để phục vụ trích dẫn học thuật và reproducibility.

**Ngày cập nhật lần cuối:** 2026-05-17  
**Thư mục gốc:** `C:\Users\Admin\Documents\GAN_SQLi\Asset\LabelData\NewDataSet\`

---

## Tổng Quan

| # | Tên nguồn | Loại | Trạng thái | Thư mục lưu |
|---|-----------|------|-----------|------------|
| 1 | Kaggle — syedsaqlainhussain/sql-injection-dataset | Dataset CSV | ✅ Đã tải | `kaggle/syedsaqlainhussain_sql-injection-dataset/` |
| 2 | Kaggle — sajid576/sql-injection-dataset | Dataset CSV | ✅ Đã tải | `kaggle/sajid576_sql-injection-dataset/` |
| 3 | Kaggle — ayahkhaldi/sql-injection-dataset | Dataset CSV | ✅ Đã tải | `kaggle/ayahkhaldi_sql-injection-dataset/` |
| 4 | Kaggle — gambleryu/biggest-sql-injection-dataset | Dataset CSV | ✅ Đã tải | `kaggle/gambleryu_biggest-sql-injection-dataset/` |
| 5 | Mendeley — mmc4sdmnrc (SQL Injection Attack Dataset) | Dataset CSV | ✅ Đã tải | `mendeley_SQLI_Dataset.csv` |
| 6 | Mendeley — xz4d5zj5yw (RbSQLi Dataset) | Dataset CSV (zip) | ✅ Đã tải & extract | `mendeley_rbsqli_dataset.zip` + `rbsqli_dataset.csv` |
| 7 | Zenodo — record 17086037 | Dataset CSV | ✅ Đã tải | `zenodo_dataset.csv` |
| 8 | BCCC-SFU — SQL Injection 2023 | Dataset CSV | ✅ Đã tải | `bccc_sfu/` |
| 9 | HuggingFace — sharegpt_sqli_v2 | Dataset CSV | ✅ Đã tải | `huggingface/` |
| 10 | GitHub — nidnogg/sqliv5-dataset | Dataset CSV+JSON | ✅ Đã tải | `github_sqliv5/` |
| 11 | GitHub — OWASP/www-project-waf-a-mole | Tài liệu WAF | ✅ Đã tải | `github_wafamole/` |
| 12 | GitHub — yogsec/SQL-Injection-Payloads | Payload TXT | ✅ Đã tải | `github_yogsec_payloads/` |
| 13 | GitHub — ajinmathew/SQL-data | Dataset CSV | ✅ Đã tải | `github_ajinmathew/` |
| 14 | GitHub — Morzeux/HttpParamsDataset | Dataset CSV | ✅ Đã tải | `github_http_params/` |
| 15 | GitHub — RbSQLi-Dataset/RbSQLi-Dataset | Notebooks | ✅ Đã tải | `github_rbsqli/` |
| 16 | Gist — johntroony/Troony_SQLi_Payloads | Payload TXT | ✅ Đã tải | `gist_johntroony/` |
| 17 | Anubis — PDF tài liệu SQLi | PDF | ✅ Đã tải | `anubis.pdf` |

---

## Chi Tiết Từng Nguồn

---

### 1. Kaggle — `syedsaqlainhussain/sql-injection-dataset`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://www.kaggle.com/datasets/syedsaqlainhussain/sql-injection-dataset |
| **Tải bằng** | `kagglehub` Python SDK (không cần API key) |
| **Thư mục** | `kaggle/syedsaqlainhussain_sql-injection-dataset/` |
| **Files** | `sqli.csv` (4,201 rows), `sqliv2.csv` (33,762 rows), `SQLiV3.csv` (30,919 rows) |
| **Cấu trúc** | CSV: `Sentence`, `Label` (0=clean, 1=SQLi) |
| **Trạng thái** | ✅ Đã tải đầy đủ |
| **Trích dẫn** | Syed Saqlain Hussain, "SQL Injection Dataset", Kaggle, https://www.kaggle.com/datasets/syedsaqlainhussain/sql-injection-dataset, truy cập 2026-05-17 |

---

### 2. Kaggle — `sajid576/sql-injection-dataset`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://www.kaggle.com/datasets/sajid576/sql-injection-dataset |
| **Tải bằng** | `kagglehub` Python SDK |
| **Thư mục** | `kaggle/sajid576_sql-injection-dataset/` |
| **Files** | `Modified_SQL_Dataset.csv` (30,919 rows) |
| **Cấu trúc** | CSV: `Sentence`, `Label` (0=clean, 1=SQLi) |
| **Trạng thái** | ✅ Đã tải |
| **Trích dẫn** | Sajid576, "SQL Injection Dataset", Kaggle, https://www.kaggle.com/datasets/sajid576/sql-injection-dataset, truy cập 2026-05-17 |

---

### 3. Kaggle — `ayahkhaldi/sql-injection-dataset`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://www.kaggle.com/datasets/ayahkhaldi/sql-injection-dataset |
| **Tải bằng** | `kagglehub` Python SDK |
| **Thư mục** | `kaggle/ayahkhaldi_sql-injection-dataset/` |
| **Files** | `Train.csv` (103,822 rows), `Test.csv` (34,627 rows), `Validation.csv` (34,669 rows) |
| **Cấu trúc** | CSV: `Sentence`, `Label` (0=clean, 1=SQLi) |
| **Trạng thái** | ✅ Đã tải |
| **Trích dẫn** | Ayah Khaldi, "SQL Injection Dataset", Kaggle, https://www.kaggle.com/datasets/ayahkhaldi/sql-injection-dataset, truy cập 2026-05-17 |

---

### 4. Kaggle — `gambleryu/biggest-sql-injection-dataset`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://www.kaggle.com/datasets/gambleryu/biggest-sql-injection-dataset |
| **Tải bằng** | `kagglehub` Python SDK |
| **Thư mục** | `kaggle/gambleryu_biggest-sql-injection-dataset/` |
| **Files** | `clean_sql_dataset.csv` (158,007 rows) |
| **Cấu trúc** | CSV: `Sentence`, `Label` (0=clean, 1=SQLi) |
| **Trạng thái** | ✅ Đã tải |
| **Trích dẫn** | Gambleryu, "Biggest SQL Injection Dataset", Kaggle, https://www.kaggle.com/datasets/gambleryu/biggest-sql-injection-dataset, truy cập 2026-05-17 |

---

### 5. Mendeley — `mmc4sdmnrc` (SQL Injection Attack Dataset)
| Trường | Thông tin |
|--------|----------|
| **URL** | https://data.mendeley.com/datasets/mmc4sdmnrc/2 |
| **DOI** | 10.17632/mmc4sdmnrc.2 |
| **Tải bằng** | `requests` — Mendeley public API |
| **File** | `mendeley_SQLI_Dataset.csv` (47,463 rows) |
| **Cấu trúc** | CSV: 19 feature columns (`no_letter`, `no_digit`, `length`, `entropy`, ...) + `label` |
| **Trạng thái** | ✅ Đã tải |
| **Ghi chú** | Dataset là feature-extracted vectors, không phải raw SQL queries |
| **Trích dẫn** | Alyasiri, Hasanen, "SQL Injection Attack Dataset", Mendeley Data, V2, doi:10.17632/mmc4sdmnrc.2, truy cập 2026-05-17 |

---

### 6. Mendeley — `xz4d5zj5yw` (RbSQLi Dataset)
| Trường | Thông tin |
|--------|----------|
| **URL** | https://data.mendeley.com/datasets/xz4d5zj5yw/4 |
| **DOI** | 10.17632/xz4d5zj5yw.4 |
| **Tải bằng** | `requests` — Mendeley public API |
| **Files** | `mendeley_rbsqli_dataset.zip` (174 MB) → extracted `rbsqli_dataset.csv` (1.39 GB) |
| **Rows** | **10,190,450 rows** |
| **Cấu trúc** | CSV: `sql_query`, `injection_type`, `vulnerability_status`, `sql_command`, `target_table`, `selected_columns`, `comparison_operator`, `logical_operator`, `sql_comment_syntax` |
| **Trạng thái** | ✅ Đã tải & giải nén |
| **Ghi chú** | Dataset lớn nhất, có nhãn chi tiết (injection_type, vulnerability_status). Ưu tiên dùng cho training. |
| **Trích dẫn** | Mullick, Mohammad Abu Obaida et al., "Rule-Based SQL Injection (RbSQLi) Dataset", Mendeley Data, V4, doi:10.17632/xz4d5zj5yw.4, truy cập 2026-05-17 |

---

### 7. Zenodo — Record 17086037
| Trường | Thông tin |
|--------|----------|
| **URL** | https://zenodo.org/records/17086037 |
| **Tải bằng** | `requests` — direct download |
| **File** | `zenodo_dataset.csv` (1.05 GB) |
| **Rows** | **3,792,161 rows** |
| **Cấu trúc** | CSV (11 cột): `full_query`, `label`, `user_inputs`, `attack_stage`, `tamper_method`, `attack_status`, `statement_type`, `query_template_id`, `attack_id`, `attack_technique`, `split` |
| **Trạng thái** | ✅ Đã tải |
| **Ghi chú** | Dataset có nhãn chi tiết: attack_stage, attack_technique, tamper_method. Dung lượng lớn thứ 2. |
| **Trích dẫn** | Zenodo record 17086037, "SQL Injection Dataset", https://zenodo.org/records/17086037, truy cập 2026-05-17 |

---

### 8. BCCC-SFU — SQL Injection Dataset 2023
| Trường | Thông tin |
|--------|----------|
| **URL** | https://bccc-sfu.github.io/SQL-Injection-Dataset-2023/ |
| **Tải bằng** | `requests` — direct download |
| **Thư mục** | `bccc_sfu/` |
| **File** | `BCCC-SFU-SQLInj-2023.csv` (5.8 MB, 11,011 rows) |
| **Cấu trúc** | CSV: câu lệnh SQL được gán nhãn SQLi |
| **Trạng thái** | ✅ Đã tải |
| **Trích dẫn** | BCCC-SFU, "SQL Injection Dataset 2023", https://bccc-sfu.github.io/SQL-Injection-Dataset-2023/, truy cập 2026-05-17 |

---

### 9. HuggingFace — `sharegpt_sqli_v2`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://huggingface.co/datasets/victor2424/sharegpt_sqli_v2 |
| **Tải bằng** | `datasets` Python library |
| **Thư mục** | `huggingface/` |
| **File** | `sharegpt_sqli_v2.csv` (1.4 MB, 4,312 rows) |
| **Cấu trúc** | CSV: hội thoại SQLi từ ShareGPT |
| **Trạng thái** | ✅ Đã tải |
| **Trích dẫn** | victor2424, "sharegpt_sqli_v2", HuggingFace Datasets, https://huggingface.co/datasets/victor2424/sharegpt_sqli_v2, truy cập 2026-05-17 |

---

### 10. GitHub — `nidnogg/sqliv5-dataset`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://github.com/nidnogg/sqliv5-dataset |
| **Tải bằng** | `git clone --depth 1` |
| **Thư mục** | `github_sqliv5/` |
| **Files** | `sqli.csv` (4,201 rows), `sqliv2.csv` (33,762 rows), `SQLiV3.csv` (30,918 rows), `SQLiV3.json`, `SQLiV3_clean.json`, `SQLiV4.json`, `SQLiV5.json` |
| **Cấu trúc** | CSV: `Sentence`, `Label` (0=clean, 1=SQLi); JSON: array of objects |
| **Trạng thái** | ✅ Đã tải |
| **Ghi chú** | Bản V5 (JSON, ~162k lines) là mới nhất. Các file CSV trùng với Kaggle syedsaqlainhussain. |
| **Trích dẫn** | nidnogg, "sqliv5-dataset", GitHub, https://github.com/nidnogg/sqliv5-dataset, truy cập 2026-05-17 |

---

### 11. GitHub — `OWASP/www-project-waf-a-mole`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://github.com/OWASP/www-project-waf-a-mole |
| **Tải bằng** | `git clone --depth 1` |
| **Thư mục** | `github_wafamole/` |
| **Files** | Markdown documentation về WAF bypass techniques |
| **Trạng thái** | ✅ Đã tải |
| **Giá trị** | Tài liệu tham khảo về cơ chế WAF và kỹ thuật bypass |
| **Trích dẫn** | OWASP, "WAF-A-Mole Project", GitHub, https://github.com/OWASP/www-project-waf-a-mole, truy cập 2026-05-17 |

---

### 12. GitHub — `yogsec/SQL-Injection-Payloads`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://github.com/yogsec/SQL-Injection-Payloads |
| **Tải bằng** | `git clone --depth 1` |
| **Thư mục** | `github_yogsec_payloads/` |
| **Files** | 12 file TXT theo từng loại tấn công |
| **Các loại** | Boolean-Based, Comment-Based, DNS Exfiltration, Error-Based, Hybrid, OOB, Second Order, Stacked Queries, Stored Procedure, Time-Based, Union-Based, WAF Bypass |
| **Trạng thái** | ✅ Đã tải |
| **Giá trị** | Payload có phân loại sẵn → dùng cho gán nhãn multi-class |
| **Trích dẫn** | Yogsec, "SQL-Injection-Payloads", GitHub, https://github.com/yogsec/SQL-Injection-Payloads, truy cập 2026-05-17 |

---

### 13. GitHub — `ajinmathew/SQL-data`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://github.com/ajinmathew/SQL-data |
| **Tải bằng** | `git clone --depth 1` |
| **Thư mục** | `github_ajinmathew/` |
| **Files** | `sqli.csv` (4,201 rows), `sqliv2.csv` (33,762 rows) |
| **Cấu trúc** | CSV: `Sentence`, `Label` |
| **Trạng thái** | ✅ Đã tải |
| **Ghi chú** | Dữ liệu trùng với sqliv5-dataset và Kaggle syedsaqlainhussain |
| **Trích dẫn** | Ajin Mathew, "SQL-data", GitHub, https://github.com/ajinmathew/SQL-data, truy cập 2026-05-17 |

---

### 14. GitHub — `Morzeux/HttpParamsDataset`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://github.com/Morzeux/HttpParamsDataset |
| **Tải bằng** | `git clone --depth 1` |
| **Thư mục** | `github_http_params/` |
| **Files** | `payload_full.csv` (31,067 rows), `payload_train.csv` (20,712 rows), `payload_test.csv` (10,355 rows), `payload_test_lexical.csv` (1,106 rows) |
| **Cấu trúc** | CSV: HTTP request parameters với label SQLi |
| **Trạng thái** | ✅ Đã tải |
| **Ghi chú** | Dataset chứa HTTP params thực tế → hữu ích cho feature engineering |
| **Trích dẫn** | Morzeux, "HttpParamsDataset", GitHub, https://github.com/Morzeux/HttpParamsDataset, truy cập 2026-05-17 |

---

### 15. GitHub — `RbSQLi-Dataset/RbSQLi-Dataset`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://github.com/RbSQLi-Dataset/RbSQLi-Dataset |
| **Tải bằng** | `git clone --depth 1` |
| **Thư mục** | `github_rbsqli/` |
| **Files** | Jupyter notebooks (EDA, cross-validation, model training) |
| **Trạng thái** | ✅ Đã tải |
| **Ghi chú** | Repo chứa notebooks cho RbSQLi dataset (file dữ liệu chính ở Mendeley). Dùng làm tài liệu tham khảo. |
| **Trích dẫn** | RbSQLi-Dataset, "RbSQLi-Dataset", GitHub, https://github.com/RbSQLi-Dataset/RbSQLi-Dataset, truy cập 2026-05-17 |

---

### 16. Gist — `johntroony/Troony_SQLi_Payloads`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://gist.github.com/johntroony/7c0cf0bb1f3acd3c6ee4883ef1c0a4b7 |
| **Tải bằng** | `requests` — raw gist URL |
| **Thư mục** | `gist_johntroony/` |
| **File** | `Troony_SQLi_Payloads.txt` (19.7 KB) |
| **Trạng thái** | ✅ Đã tải |
| **Trích dẫn** | John Troony, "SQLi Payloads", GitHub Gist, https://gist.github.com/johntroony/7c0cf0bb1f3acd3c6ee4883ef1c0a4b7, truy cập 2026-05-17 |

---

### 17. Anubis — PDF Tài Liệu SQLi
| Trường | Thông tin |
|--------|----------|
| **URL** | https://www.anubis.es/articles/sql_injection.pdf |
| **Tải bằng** | `requests` — direct download |
| **File** | `anubis.pdf` (12.5 KB) |
| **Trạng thái** | ✅ Đã tải |
| **Trích dẫn** | Anubis, "SQL Injection", https://www.anubis.es/articles/sql_injection.pdf, truy cập 2026-05-17 |

---

## Tổng Kết Dữ Liệu

| Nguồn | Số rows | Có nhãn binary? | Có nhãn type? | Dung lượng |
|-------|---------|----------------|--------------|-----------|
| Kaggle syedsaqlainhussain | 68,882 | ✅ | ❌ | 6.7 MB |
| Kaggle sajid576 | 30,919 | ✅ | ❌ | 2.3 MB |
| Kaggle ayahkhaldi | 173,118 | ✅ | ❌ | 55 MB |
| Kaggle gambleryu | 158,007 | ✅ | ❌ | 55 MB |
| Mendeley mmc4sdmnrc | 47,463 | ✅ | ❌ | 2.4 MB |
| Mendeley xz4d5zj5yw (RbSQLi) | **10,190,450** | ✅ | ✅ (injection_type) | 1.39 GB |
| Zenodo 17086037 | **3,792,161** | ✅ | ✅ (attack_technique) | 1.05 GB |
| BCCC-SFU 2023 | 11,011 | ✅ | ❌ | 5.8 MB |
| HuggingFace sharegpt_sqli_v2 | 4,312 | ✅ | ❌ | 1.4 MB |
| GitHub HttpParams | 63,240 | ✅ | ❌ | 4.4 MB |
| GitHub ajinmathew | 37,963 | ✅ | ❌ | 4.3 MB |
| GitHub sqliv5 | 68,881 | ✅ | ❌ | 28 MB |
| **Tổng** | **~14,646,407** | | | **~2.59 GB** |

**Payload collections (không tính vào rows trên):**
- yogsec/SQL-Injection-Payloads: 12 files phân loại (Boolean, Error, Time, Union, WAF Bypass...)
- Gist Troony_SQLi_Payloads.txt
- Anubis PDF

---

## Cần Làm Tiếp

- [ ] Dedup các file trùng (sqli.csv, sqliv2.csv xuất hiện ở nhiều nguồn)
- [ ] Chuẩn hoá schema chung cho tất cả CSV
- [ ] Gán nhãn attack type cho các dataset binary dựa trên pattern matching
- [ ] Tạo unified dataset hợp nhất tất cả nguồn
- [ ] Train/val/test split

---

## Ghi Chú Pháp Lý & Đạo Đức

> Toàn bộ dữ liệu được thu thập từ nguồn **công khai, hợp pháp** (Kaggle public datasets, Mendeley Data, Zenodo, GitHub public repos, HuggingFace, BCCC-SFU).  
> Mục đích sử dụng: **nghiên cứu học thuật** về phát hiện và phòng thủ tấn công SQL Injection.  
> Không sử dụng dữ liệu hoặc model sinh ra để tấn công hệ thống thực tế.
