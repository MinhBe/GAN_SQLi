# Dataset Sources — SeqGAN-SQLi Project
> **Mục đích:** Ghi lại toàn bộ nguồn dữ liệu đã thu thập, ngày lấy, vị trí lưu trữ và trạng thái để phục vụ trích dẫn học thuật và reproducibility.

**Ngày cập nhật lần cuối:** 2026-05-03  
**Thư mục gốc:** `C:\Users\Admin\Documents\GAN\Asset\Data\`

---

## Tổng Quan

| # | Tên nguồn | Loại | Trạng thái | Thư mục lưu |
|---|-----------|------|-----------|------------|
| 1 | Kaggle — sajid576/sql-injection-dataset | Dataset CSV | ⏳ Chờ API key | `kaggle_sajid576/` |
| 2 | GitHub — nidnogg/sqliv5-dataset | Dataset CSV+JSON | ✅ Đã tải | `sqliv5_dataset/` |
| 3 | GitHub — sqlmapproject/sqlmap | Payload XML + Tamper | ✅ Đã tải (sparse) | `sqlmap_payloads/` |
| 4 | GitHub — danielmiessler/SecLists | Wordlist TXT | ✅ Đã tải | `seclists_sqli/` |
| 5 | GitLab — exploit-database/exploitdb | CSV (filtered SQLi) | ✅ Đã tải & lọc | `exploitdb_sqli/` |

---

## Chi Tiết Từng Nguồn

---

### 1. Kaggle — `sajid576/sql-injection-dataset`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://www.kaggle.com/datasets/sajid576/sql-injection-dataset |
| **Tải bằng** | `kagglehub` Python SDK |
| **Script** | `kaggle_sajid576/download_kaggle.py` |
| **Cấu trúc** | CSV: `Sentence`, `Label` (0=clean, 1=SQLi) |
| **Ước tính** | ~30k–50k rows |
| **Trạng thái** | ⏳ Cần Kaggle API key — xem hướng dẫn bên dưới |
| **Trích dẫn** | Kaggle dataset `sajid576/sql-injection-dataset`, truy cập 2026-05-03 |

**Hướng dẫn lấy API key:**
1. Đăng nhập kaggle.com → Settings → API → "Create New Token"
2. Lưu file `kaggle.json` vào `C:\Users\Admin\.kaggle\kaggle.json`
3. Chạy: `python kaggle_sajid576\download_kaggle.py`

---

### 2. GitHub — `nidnogg/sqliv5-dataset`
| Trường | Thông tin |
|--------|----------|
| **URL** | https://github.com/nidnogg/sqliv5-dataset |
| **Tải bằng** | `git clone` |
| **Thư mục** | `sqliv5_dataset/` |
| **Files chính** | `sqli.csv` (4,200 rows), `sqliv2.csv` (33,761 rows), `SQLiV3.csv` (30,918 rows), `SQLiV4.json`, `SQLiV5.json` |
| **Cấu trúc** | CSV: `Sentence`, `Label`; JSON: array of objects |
| **Trạng thái** | ✅ Đã tải đầy đủ |
| **Lưu ý** | Phiên bản V5 (JSON, ~162k lines) là mới nhất — ưu tiên dùng |
| **Trích dẫn** | nidnogg, "sqliv5-dataset", GitHub, https://github.com/nidnogg/sqliv5-dataset, truy cập 2026-05-03 |

---

### 3. GitHub — `sqlmapproject/sqlmap` (Sparse — Payloads & Tamper)
| Trường | Thông tin |
|--------|----------|
| **URL** | https://github.com/sqlmapproject/sqlmap |
| **Tải bằng** | `git sparse-checkout` (depth=1) |
| **Thư mục** | `sqlmap_payloads/` |
| **Files chính** | `data/xml/payloads/boolean_blind.xml`, `error_based.xml`, `inline_query.xml`, `stacked_queries.xml`, `time_blind.xml`, `union_query.xml` |
| **Tamper scripts** | `tamper/` — 71 scripts Python cho obfuscation/bypass |
| **Trạng thái** | ✅ Đã tải (sparse, chỉ payload + tamper) |
| **Giá trị** | Payload XML có nhãn attack type sẵn → dùng cho annotation tập training |
| **Trích dẫn** | sqlmapproject, "sqlmap: Automatic SQL injection tool", https://github.com/sqlmapproject/sqlmap, truy cập 2026-05-03 |

**Attack types trong payload XML:**
- `boolean_blind.xml` → Boolean-based blind SQLi
- `error_based.xml` → Error-based SQLi
- `time_blind.xml` → Time-based blind SQLi
- `union_query.xml` → UNION-based SQLi
- `stacked_queries.xml` → Stacked queries
- `inline_query.xml` → Inline query

---

### 4. GitHub — `danielmiessler/SecLists` (Sparse — SQL paths)
| Trường | Thông tin |
|--------|----------|
| **URL** | https://github.com/danielmiessler/SecLists |
| **Tải bằng** | `git sparse-checkout` — chỉ `Fuzzing/SQLi/` và `Fuzzing/Databases/` |
| **Thư mục** | `seclists_sqli/` |
| **Trạng thái** | ✅ Đã tải đầy đủ |
| **Files** | `Fuzzing/Databases/SQLi/` — 11 files: Generic, MSSQL, MySQL, Oracle, Polyglots, Auth Bypass, Blind, NoSQL (~594 dòng payload) |
| **Lưu ý** | Repo gốc ~1.5GB — sparse checkout chỉ `Fuzzing/Databases/` (~few MB) |
| **Trích dẫn** | D. Miessler, J. Haddix, G. Snook, "SecLists", https://github.com/danielmiessler/SecLists, truy cập 2026-05-03 |

---

### 5. GitLab — `exploit-database/exploitdb` (Filtered SQLi)
| Trường | Thông tin |
|--------|----------|
| **URL** | https://gitlab.com/exploit-database/exploitdb |
| **Tải bằng** | `git sparse-checkout` — `files_exploits.csv` + `exploits/` |
| **Thư mục** | `exploitdb_sqli/` |
| **File gốc** | `files_exploits.csv` — 47,025 exploits |
| **File đã lọc** | `sqli_exploits.csv` — **8,696 entries SQLi** |
| **Filter regex** | `sql.?inject\|sqli\b\|union.*select\|blind.*sql\|sql.*bypass` (case-insensitive) |
| **Cấu trúc** | `id`, `file`, `description`, `date_published`, `author`, `type`, `platform`, `codes` (CVE) |
| **Trạng thái** | ✅ Đã tải & lọc xong |
| **Giá trị** | Có CVE codes → có thể link với NVD để lấy thêm context |
| **Trích dẫn** | Offensive Security, "Exploit Database", https://gitlab.com/exploit-database/exploitdb, truy cập 2026-05-03 |

---

## Tổng Kết Dữ Liệu (Ước Tính)

| Nguồn | SQLi samples (ước tính) | Có nhãn type? | Ghi chú |
|-------|------------------------|--------------|---------|
| Kaggle sajid576 | ~30k–50k | Không | Binary label 0/1 |
| sqliv5-dataset V5 | ~50k+ | Không | Phiên bản mới nhất |
| sqlmap XML payloads | ~500–2k | **Có (6 loại)** | Structured XML |
| SecLists SQLi | ~594 payloads | Không (có DB type) | Wordlist chuyên sâu theo DB engine |
| ExploitDB filtered | 8,696 | Không (có platform) | Real-world CVE |
| **Tổng** | **~95k–115k** | | Trước dedup |

---

## Cần Làm Tiếp

- [ ] Lấy Kaggle API key và chạy `download_kaggle.py`
- [ ] Xác nhận SecLists tải xong
- [ ] Viết script hợp nhất tất cả nguồn thành `unified_sqli_pool.csv`
- [ ] Dedup + gán nhãn attack type dựa trên sqlmap XML patterns
- [ ] Copy tập đã xử lý sang `SeqGAN_SQLi/data/raw/` để dùng cho training

---

## Ghi Chú Pháp Lý & Đạo Đức

> Toàn bộ dữ liệu được thu thập từ nguồn **công khai, hợp pháp** (GitHub/GitLab public repos, Kaggle public datasets).  
> Mục đích sử dụng: **nghiên cứu học thuật** về phát hiện và phòng thủ tấn công SQL Injection.  
> Không sử dụng dữ liệu hoặc model sinh ra để tấn công hệ thống thực tế.
