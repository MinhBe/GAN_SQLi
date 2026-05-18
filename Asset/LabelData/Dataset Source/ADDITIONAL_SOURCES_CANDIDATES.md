# Dataset Candidates — Đề xuất bổ sung để làm giàu corpus SeqGAN-SQLi

> **Ngày tạo:** 2026-05-18
> **Trạng thái:** 📝 Đề xuất — chưa tải. Cần user duyệt từng mục trước khi download.
> **Tham chiếu:** `DATASET_SOURCES.md` (file gốc, 5 nguồn cũ) + `NewDataSet/DATASET_SOURCES.md` (18 nguồn đã tải).

## Phân tích gap hiện tại

Sau khi rà soát 18 nguồn đã có ở `NewDataSet/`, **4 khoảng trống lớn** cần làm giàu:

| Gap | Mô tả | Hiện trạng |
|-----|-------|-----------|
| **G1. Real-world HTTP traffic** | Toàn bộ request HTTP gồm header + path + body, không phải chỉ payload | ❌ Chưa có (`http_params` chỉ lấy giá trị parameter, mất context) |
| **G2. Benign SQL phong phú** | SQL hợp lệ đa dạng schema để D học tốt biên giới SQLi vs SQL bình thường | ⚠️ Rất thiếu — `huggingface/sharegpt` chỉ là Q&A; binary datasets phần lớn benign là "câu tự nhiên" không phải SQL hợp lệ |
| **G3. Fine-grained labeled payload theo DBMS** | Tách MySQL/MSSQL/Oracle/PostgreSQL/SQLite cho conditional generation | ⚠️ Chỉ có `combined_labeled_data.csv` (40k, tự gán) — chưa có nguồn gốc nhãn DBMS chuẩn |
| **G4. Network-flow / source-code modality** | Mở rộng modality để D đánh giá payload ở context khác | ❌ Hoàn toàn chưa có |

Liên hệ đến vấn đề **mode collapse** đã thấy ở V3 (composite=0.471): bổ sung G2 + G3 sẽ giúp D phân biệt sắc hơn ⇒ tín hiệu reward cho G đa dạng hơn ⇒ giảm collapse.

---

## Tier 1 — KHUYẾN NGHỊ MẠNH (giải quyết gap chưa từng có)

### T1.1 — CSIC 2010 HTTP Dataset (filling G1)
| Trường | Thông tin |
|--------|-----------|
| **URL nguồn gốc** | http://www.isi.csic.es/dataset/ (paywall/dead) |
| **Mirror đang dùng được** | https://github.com/Kiinitix/HTTP-CSIC-2010 |
| **Mirror combined** | https://github.com/msudol/Web-Application-Attack-Datasets (CSIC 2010 + ECML/PKDD 2007) |
| **Quy mô** | 36,000 normal HTTP requests + 25,065 anomalous (gồm SQLi, XSS, buffer overflow, CRLF, file disclosure, SSI, parameter tampering) |
| **Format** | Raw HTTP request (full method + URI + headers + body) |
| **Gap fill** | **G1** — đây là benchmark academic duy nhất có request HTTP đầy đủ |
| **Đánh giá** | ⭐⭐⭐⭐⭐ Phải có — benchmark chuẩn của lĩnh vực, hầu hết paper detection dùng làm baseline |
| **Cmd tải** | `git clone https://github.com/Kiinitix/HTTP-CSIC-2010.git github_csic_2010` |
| **Trùng lặp với hiện có** | ~10k SQLi payloads của `http_params` được trích từ CSIC2010 → có overlap nhưng CSIC2010 có **toàn bộ context HTTP** |
| **License** | Public research dataset |

### T1.2 — IEEE DataPort SQL Injection Detection Dataset (2025) (filling G2)
| Trường | Thông tin |
|--------|-----------|
| **URL** | https://ieee-dataport.org/documents/sql-injection-detection-dataset |
| **Tác giả** | Md Mehedi Hassan, Antu Roy Chowdhury, Rubaeat Ahammed (8/2025) |
| **Quy mô** | **244,068 rows** = 136,740 SQLi + 107,328 benign |
| **Schema** | `Query, Label` |
| **Gap fill** | **G2** — bộ benign **107k** là nguồn benign SQL/query lớn nhất, mới nhất |
| **Đánh giá** | ⭐⭐⭐⭐⭐ Mới (2025), tỉ lệ benign/SQLi cân bằng (44/56), schema tương thích với pipeline hiện tại |
| **Cảnh báo** | Cần đăng ký IEEE DataPort (free academic). Có thể overlap với Kaggle sajid576 (~13% kích thước) |

### T1.3 — SQL Injection Netflow Dataset (Zenodo 6907252) (filling G4)
| Trường | Thông tin |
|--------|-----------|
| **URL** | https://zenodo.org/records/6907252 (DOI 10.5281/zenodo.6907252) |
| **Tác giả** | I. Crespo, A. Campazas (2022) |
| **Quy mô** | **457,242 NetFlow v5 records** (D1 train 400,003 + D2 test 57,239) — 50/50 benign/malicious |
| **Format** | CSV NetFlow v5; generated bằng sqlmap (Union + Blind) qua DOROTHEA framework |
| **Gap fill** | **G4** — modality hoàn toàn mới (flow-level, không phải payload). Dùng cho thí nghiệm cross-modal hoặc D phụ |
| **Đánh giá** | ⭐⭐⭐ Optional — không trực tiếp giúp G generator, nhưng giá trị cho phân tích detection ở tầng network |
| **License** | CC-BY-4.0 — free, có DOI để cite |
| **Size** | 63 MB total |
| **Cmd tải** | `curl -L -o zenodo_netflow_d1.csv "https://zenodo.org/records/6907252/files/SLQ%20Injection%20Attack%20for%20training%20%28D1%29.csv?download=1"` |

### T1.4 — Spider 1.0 + BIRD-SQL (Yale Lily) (filling G2)
| Trường | Thông tin |
|--------|-----------|
| **Spider URL** | https://yale-lily.github.io/spider — 10,181 NL questions + 5,693 unique complex SQL trên 200 DBs / 138 domains |
| **BIRD URL** | https://bird-bench.github.io/ — 9,428 train + 1,534 dev SQL queries, 95 DBs / 37 domains, "dirty" real-world |
| **Schema** | JSON: `{question, query, db_id, …}` |
| **Gap fill** | **G2** — SQL hợp lệ phức tạp (JOIN nhiều bảng, subquery, aggregation) — chính là loại benign mà detection model hay nhầm lẫn với SQLi |
| **Đánh giá** | ⭐⭐⭐⭐⭐ Phải có — fix bất cân bằng "benign quá đơn giản" trong các Kaggle dataset hiện tại |
| **License** | CC BY-SA 4.0 (Spider) |
| **Cmd tải Spider** | Tải qua Google Drive link trên site, hoặc `kaggle datasets download jeromeblanchet/yale-universitys-spider-10-nlp-dataset` |

---

## Tier 2 — KHUYẾN NGHỊ (curated payload theo DBMS / type — fill G3)

### T2.1 — PayloadsAllTheThings/SQL Injection (swisskyrepo) ⭐ canonical
| Trường | Thông tin |
|--------|-----------|
| **URL** | https://github.com/swisskyrepo/PayloadsAllTheThings/tree/master/SQL%20Injection |
| **Cấu trúc** | Markdown files theo DBMS: `MySQL Injection.md`, `MSSQL Injection.md`, `OracleSQL Injection.md`, `PostgreSQL Injection.md`, `SQLite Injection.md`, `DB2 Injection.md`, `Cassandra Injection.md`, `MongoDB Injection.md`, `OData Injection.md`, `ORM Injection.md`, `SQLmap.md`, `README.md` (generic) |
| **Schema** | Payload nhúng trong markdown — cần parser regex để extract code blocks |
| **Gap fill** | **G3** — nhãn DBMS chuẩn từ community canonical |
| **Đánh giá** | ⭐⭐⭐⭐⭐ Phải có — đây là payload collection được tham chiếu nhiều nhất trong community |
| **Cmd tải sparse** | `git clone --depth 1 --filter=blob:none --sparse https://github.com/swisskyrepo/PayloadsAllTheThings.git github_payloadsallthethings && cd github_payloadsallthethings && git sparse-checkout set "SQL Injection"` |
| **Ước lượng số payload sau parse** | ~1,500–2,500 unique payloads, chia ~10 DBMS |

### T2.2 — fuzzdb-project/fuzzdb (G3)
| Trường | Thông tin |
|--------|-----------|
| **URL** | https://github.com/fuzzdb-project/fuzzdb |
| **Cấu trúc** | `attack/sql-injection/detect/` (MySQL.fuzz.txt, MSSQL.fuzz.txt, xplatform.fuzz.txt) + `attack/sql-injection/payloads-sql-blind/` |
| **Gap fill** | **G3** — payload theo platform |
| **Đánh giá** | ⭐⭐⭐⭐ Có — bổ trợ cho T2.1, nhiều primitives fuzz |
| **Cmd tải sparse** | `git clone --depth 1 --filter=blob:none --sparse https://github.com/fuzzdb-project/fuzzdb.git github_fuzzdb && cd github_fuzzdb && git sparse-checkout set "attack/sql-injection"` |
| **Lưu ý** | Một phần đã được `http_params` hấp thụ — kiểm tra dedup |

### T2.3 — payloadbox/sql-injection-payload-list (G3)
| Trường | Thông tin |
|--------|-----------|
| **URL** | https://github.com/payloadbox/sql-injection-payload-list |
| **Cấu trúc** | `Intruder/` (text payload lists) + `Generic/` + theo authentication-bypass / error-based / time-based / union-based |
| **Gap fill** | **G3** — payload theo technique type |
| **Đánh giá** | ⭐⭐⭐⭐ Có — nguồn được SafeSQL-v1 dùng để train |
| **Cmd tải** | `git clone --depth 1 https://github.com/payloadbox/sql-injection-payload-list.git github_payloadbox` |

---

## Tier 3 — TÙY CHỌN (chất lượng cao, có overlap)

### T3.1 — SafeSQL-v1 train.csv (HuggingFace)
| Trường | Thông tin |
|--------|-----------|
| **URL** | https://huggingface.co/deathsaber93/SafeSQL-v1/blob/main/dataset/train.csv |
| **Quy mô** | ~167,000 rows, balance benign/malicious gần 50/50 |
| **Nguồn gốc tổng hợp** | gambleryu (đã có) + b-mc2/sql-create-context + payloadbox + ChrisHayduk/Llama-2-SQL + philikai/Spider-SQL-LLAMA2 |
| **Đánh giá** | ⭐⭐⭐ — chất lượng đã được curate. **Nhưng** trùng ~30-50% với gambleryu (156k) đã có → giá trị thực chỉ ~80-100k mới |
| **License** | Apache 2.0 |
| **Cmd tải** | `curl -L -o huggingface/safesql_v1_train.csv "https://huggingface.co/deathsaber93/SafeSQL-v1/resolve/main/dataset/train.csv"` |

### T3.2 — PurpleAILAB/chatML_SQL_injection_dataset (HF)
| Trường | Thông tin |
|--------|-----------|
| **URL** | https://huggingface.co/datasets/PurpleAILAB/chatML_SQL_injection_dataset |
| **Quy mô** | 1,996 rows ChatML format `[{from, value}, …]` — Q&A có **payload thật trong response** (union/blind/error variations) |
| **Gap fill** | Giống `sharegpt_sqli_v2` (#9) nhưng có payload thật trong câu trả lời |
| **Đánh giá** | ⭐⭐ Tùy chọn — nhỏ, format khó parse, chủ yếu cho instruction-tuning LLM |
| **Cmd tải** | `huggingface-cli download PurpleAILAB/chatML_SQL_injection_dataset --repo-type dataset --local-dir huggingface/chatml_sqli` |

### T3.3 — CVEfixes / MoreFixes (Zenodo)
| Trường | Thông tin |
|--------|-----------|
| **CVEfixes URL** | https://zenodo.org/records/13138703 (v1.0.8, latest, 7/2024) |
| **MoreFixes URL** | https://zenodo.org/records/13983082 (superset, 29,203 CVEs) |
| **Quy mô** | 12,107 vulnerability-fixing commits, 11,873 CVEs, 272 CWE types — filter `CWE-89` → ~500–800 SQLi cases |
| **Format** | SQLite DB dump |
| **Gap fill** | **G4** — source-code modality, real exploits từ CVE thật |
| **Đánh giá** | ⭐⭐⭐ Optional — không dùng trực tiếp cho SeqGAN payload-level, nhưng giá trị cho phần "thảo luận" trong luận văn |
| **License** | CC BY 4.0 |
| **Size** | ~500 MB compressed |

### T3.4 — NIST SARD Juliet Test Suite (CWE-89)
| Trường | Thông tin |
|--------|-----------|
| **URL** | https://samate.nist.gov/SARD/test-suites |
| **Java 1.3 suite** | https://samate.nist.gov/SARD/test-suites/111 (25,477 Java programs cho ~200 CWE; filter CWE-89) |
| **PHP SQLi suite** | https://samate.nist.gov/SARD/test-suites/114 (42,212 test cases cho XSS + SQLi) |
| **Gap fill** | **G4** — code-level synthetic với good/bad pairs đã đánh dấu |
| **Đánh giá** | ⭐⭐ Optional — chủ yếu cho static analyzer benchmark, không hữu ích cho payload generation |
| **License** | Public domain |

---

## Tier 4 — KHÔNG KHUYẾN NGHỊ (đã đánh giá nhưng skip)

| Nguồn | Lý do skip |
|-------|-----------|
| T-Pot / Cowrie honeypot logs | Cowrie = SSH/Telnet, không phải HTTP SQLi. T-Pot Tanner mimic có thể, nhưng **không có public dataset đã curate** — chỉ là raw logs của các deployment cá nhân. ROI quá thấp |
| ModSecurity OWASP CRS rules | Là **regex pattern detection**, không phải payload thực. Có thể reverse-engineer nhưng noisy |
| ExploitDB CVE codes (đã có) | Đã ghi trong `DATASET_SOURCES.md` cũ |
| WikiSQL | Quá đơn giản (single table, SELECT only) — Spider/BIRD đã đủ |

---

## Kế hoạch tải khuyến nghị (theo thứ tự ưu tiên)

**Bước 1 — Phải có (3 nguồn, ~0.5 GB):**
1. CSIC 2010 (T1.1) — `github_csic_2010/` — fill G1
2. Spider 1.0 (T1.4) — `spider/` — fill G2
3. PayloadsAllTheThings SQL Injection (T2.1) — `github_payloadsallthethings/` — fill G3

**Bước 2 — Nên có (3 nguồn, ~0.3 GB):**
4. IEEE DataPort SQLi Detection 2025 (T1.2) — `ieee_dataport_2025/` — fill G2 quy mô lớn
5. fuzzdb SQL injection (T2.2) — `github_fuzzdb/` — fill G3 platform
6. payloadbox/sql-injection-payload-list (T2.3) — `github_payloadbox/` — fill G3 technique

**Bước 3 — Tùy chọn (3 nguồn, ~1 GB):**
7. SQL Injection Netflow Zenodo (T1.3) — modality mới
8. SafeSQL-v1 train.csv (T3.1) — sau khi dedup với gambleryu
9. CVEfixes/MoreFixes (T3.3) — bối cảnh CVE thật cho luận văn

**Tổng cộng nếu lấy hết:** ~1.8 GB, ước lượng **+450k–600k mẫu chất lượng cao** sau dedup (đặc biệt 107k benign Spider+BIRD+IEEE giúp cân bằng class — yếu tố lớn nhất giúp giảm mode collapse).

---

## Việc cần làm tiếp sau khi tải

1. Cập nhật `NewDataSet/DATASET_SOURCES.md` với mỗi nguồn mới tải (theo format có sẵn).
2. Viết script chuẩn hoá schema chung `{payload, label, attack_type, db_engine, source, split}` áp dụng cho **tất cả 18 nguồn cũ + nguồn mới**.
3. Dedup theo hash MD5(normalized payload) trên toàn bộ corpus.
4. Đo lại class balance + diversity (n-gram entropy) trước/sau khi bổ sung — quyết định có dùng để retrain G/D không.
