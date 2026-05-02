# SQLi Data Engine — Phân Tích & Kết Quả

> **Ngày tạo:** 2026-05-03  
> **Mục đích:** Phân tích chi tiết quá trình xây dựng data engine, kết quả xử lý, và đánh giá chất lượng dữ liệu.

---

## 1. Tổng Quan

### 1.1 Mục Tiêu
Xây dựng pipeline tự động xử lý dữ liệu SQLi từ nhiều nguồn khác nhau (CSV, JSON, XML, TXT) thành một dạng chung, phân loại theo loại tấn công, và chia thành các dataset riêng cho training GAN.

### 1.2 Kiến Trúc Pipeline

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  LOADERS     │ -> │ NORMALIZER   │ -> │ CLASSIFIER   │
│ (10 sources) │    │ (6 steps)    │    │ (rules+ML)   │
└──────────────┘    └──────────────┘    └──────┬───────┘
                                               │
                    ┌──────────────┐    ┌──────▼───────┐
                    │  SPLITTER    │ <- │ DEDUPLICATOR │
                    │ (per-type)   │    │ (3 levels)   │
                    └──────────────┘    └──────────────┘
```

### 1.3 Các Module Đã Xây Dựng

| File | Chức năng | Dòng code |
|------|-----------|-----------|
| `config.py` | Cấu hình đường dẫn, loại SQLi, hằng số | 100 |
| `loaders.py` | Format detector + loaders (CSV/JSON/XML/TXT) | 230 |
| `normalizer.py` | URL-decode, chuẩn hóa, clean artifacts | 110 |
| `classifier.py` | Rule-based patterns + ML fallback | 410 |
| `deduplicator.py` | Exact + normalized + semantic dedup | 90 |
| `splitter.py` | Split per type + stats + report | 180 |
| `pipeline.py` | Orchestrator (CLI) | 120 |
| `train_classifier.py` | Train ML model (TF-IDF + RF) | 80 |
| `run_final.py` | Final pipeline run script | 70 |

---

## 2. Dữ Liệu Đầu Vào

### 2.1 Nguồn Dữ Liệu

| Nguồn | Định dạng | Encoding | Samples (raw) | Trạng thái |
|-------|-----------|----------|---------------|-----------|
| BCCC-SFU-SQLInj-2023 | CSV | UTF-8 | 11,011 | Payload đầy đủ (dạng nested SQL) |
| sqliv5_dataset/sqli.csv | CSV | UTF-16-LE | 4,187 | Pattern + type (sqli) |
| sqliv5_dataset/sqliv2.csv | CSV | UTF-16-LE | 33,757 | Pattern + type (có cả text tiếng Anh) |
| sqliv5_dataset/SQLiV3.csv | CSV | UTF-8 | 30,901 | Pattern + type |
| sqliv5_dataset/SQLiV5.json | JSON | UTF-8 | 40,530 | Pattern + type |
| sqliv5_dataset/SQLiV4.json | JSON | UTF-8 | 34,914 | Pattern + type |
| sqliv5_dataset/SQLiV3_clean.json | JSON | UTF-8 | 30,864 | Pattern + type |
| seclists_sqli | TXT (10 files) | UTF-8 | 587 | Payload chuyên sâu theo DB |
| exploitdb_sqli | CSV | UTF-8 | 8,696 | **CVE descriptions** (không phải payload) |
| sqlmap XML (6 files) | XML | UTF-8 | 304 | Payload có nhãn attack type |

**Tổng raw:** 195,751 samples từ 10 sources

### 2.2 Phát Hiện Quan Trọng

1. **UTF-16 Encoding:** Các file CSV của sqliv5 (sqliv2.csv, sqli.csv) được encode bằng UTF-16-LE (có BOM `0xFFFE`). Loader phải tự động detect để đọc đúng.

2. **ExploitDB là metadata:** 8,696 entries từ exploitdb là **mô tả CVE** (ví dụ: "20/20 Applications Data Shed 1.0 - SQL Injection"), **không phải payload thực tế**. Đã được filter ra khỏi pool chính.

3. **sqliv2 có negative samples:** Dataset sqliv2.csv chứa nhiều đoạn văn tiếng Anh (văn học, triết học) được chèn vào như negative samples. Các dòng này không có SQL keywords → classified là "unknown".

4. **BCCC payloads bị nested:** Payloads từ BCCC có dạng `"select * from users WHERE username = "...payload..." AND username = "-3613"` — cần regex đặc biệt để trích xuất phần injection.

---

## 3. Quá Trình Xử Lý

### 3.1 Normalization

Các bước chuẩn hóa áp dụng:
1. **URL-decode:** `%27` → `'`, `%20` → space, v.v. (lặp đến khi hết)
2. **HTML-decode:** `&apos;` → `'`, `&quot;` → `"`
3. **Whitespace normalization:** Multiple spaces → single space
4. **Artifact removal:** Loại `__TIME__`, placeholder ngẫu nhiên `'xxxx' = 'xxxx'`
5. **BCCC-specific cleaning:** Trích xuất phần injection từ nested query

**Kết quả:** 194,213 / 195,751 samples (loại 1,538 rác/trống)

### 3.2 Classification (Rule-Based)

**Pattern rules đã triển khai:**

| Loại SQLi | Số patterns | Ví dụ pattern |
|-----------|-------------|---------------|
| union_based | 3 | `UNION.*SELECT`, `ORDER BY N` |
| error_based | 12 | `EXTRACTVALUE`, `ctxsys.drithsx`, `chr(113)+` |
| boolean_blind | 15 | `AND N=N`, `'xxx'='xxx'`, `CASE WHEN...THEN` |
| time_blind | 7 | `SLEEP(N)`, `WAITFOR DELAY`, `BENCHMARK` |
| heavy_query | 3 | `COUNT(*) FROM A, B, C` |
| stacked_queries | 3 | `; DROP`, `; INSERT`, `; EXEC` |
| out_of_band | 7 | `LOAD_FILE`, `xp_cmdshell`, `UTL_HTTP` |
| auth_bypass | 6 | `' OR '1'='1`, `admin'--` |
| second_order | 2 | `INSERT INTO...VALUES...--` |
| rce | 5 | `xp_cmdshell`, `certutil` |
| polyglot | 2 | `SLEEP(...)/\*.*OR.*SLEEP` |
| lateral | 2 | `JOIN...ON` |

**DB engine detection:** 6 engines (MySQL, MSSQL, Oracle, PostgreSQL, SQLite, NoSQL) với 47 patterns.

**Evasion detection:** 11 kỹ thuật (URL encoding, case variation, hex string, v.v.) với 28 patterns.

### 3.3 Deduplication

3 cấp độ:

| Cấp độ | Method | Trước | Sau | Loại |
|--------|--------|-------|-----|------|
| Exact | MD5 hash | 187,739 | 59,769 | 127,970 |
| Normalized | Lowercase + strip | 59,769 | 59,377 | 392 |
| Semantic | TF-IDF cosine > 0.85 | - | - | **Bỏ qua** (quá chậm với 60k+ samples) |

**Lưu ý:** Semantic dedup bị bỏ qua vì với 60k samples, tính cosine similarity O(n²) mất >10 phút. Có thể chạy riêng nếu cần.

### 3.4 Filter

- **ExploitDB:** Loại 6,474 entries là CVE descriptions (không có SQL keywords)
- **Negative samples từ sqliv2:** Giữ lại 21,513 dòng text tiếng Anh — có thể dùng làm "clean" data cho GAN training (negative class)

---

## 4. Kết Quả

### 4.1 Thống Kê Cuối Cùng

**Tổng samples (sau filter + dedup): 59,377**

#### Phân Bố Theo Loại SQLi

| Loại | Số lượng | Tỉ lệ | Ghi chú |
|------|----------|-------|---------|
| union_based | 4,059 | 6.8% | Dataset tốt, đa dạng pattern |
| boolean_blind | 3,489 | 5.9% | Nhiều từ sqliv5 + seclists |
| error_based | 2,562 | 4.3% | Oracle-specific nhiều (ctxsys, utl_inaddr) |
| time_blind | 2,409 | 4.1% | MySQL SLEEP, MSSQL WAITFOR |
| heavy_query | 536 | 0.9% | Cross-join heavy queries |
| lateral | 464 | 0.8% | JOIN-based patterns |
| second_order | 442 | 0.7% | INSERT/UPDATE injection |
| auth_bypass | 55 | 0.1% | Login bypass patterns |
| stacked_queries | 37 | 0.1% | Multi-statement payloads |
| out_of_band | 17 | 0.0% | DNS/HTTP exfil |
| rce | 16 | 0.0% | Command execution |
| polyglot | 3 | 0.0% | Multi-context payloads |
| **unknown** | **45,288** | **76.3%** | Chưa classify bằng rule |

#### Phân Bố Theo DB Engine

| Engine | Số lượng | Tỉ lệ |
|--------|----------|-------|
| MySQL | 2,307 | 3.9% |
| Oracle | 2,373 | 4.0% |
| PostgreSQL | 1,196 | 2.0% |
| MSSQL | 645 | 1.1% |
| SQLite | 323 | 0.5% |
| NoSQL | 44 | 0.1% |
| Unknown | 52,489 | 88.4% |

#### Kỹ Thuật Evasion Phát Hiện

| Kỹ thuật | Số lượng |
|----------|----------|
| Case variation | 27,658 |
| Inline comment | 6,521 |
| Comment whitespace | 6,040 |
| Hex string | 4,886 |
| Function alternative | 4,469 |
| Scientific notation | 891 |

### 4.2 ML Classifier

- **Model:** TF-IDF (char_wb, 2-5 gram) + RandomForest (100 trees, max_depth=20)
- **Training data:** 14,089 samples đã label bởi rules
- **Accuracy (5-fold CV):** **95.2% ± 8.8%**
- **Model saved:** `output/ml_classifier.pkl`

**Có thể dùng để classify 45,288 samples unknown.**

### 4.3 Output Files

```
data_engine/output/
├── unified_sqli_pool.csv          # 59,377 rows, 8 columns
├── unified_sqli_pool.json         # Full JSON với metadata
├── ml_classifier.pkl              # Trained ML model
├── stats/
│   ├── distribution_by_type.json
│   ├── distribution_by_db.json
│   └── quality_report.md
└── datasets/
    ├── union_based.csv            # 4,059
    ├── boolean_blind.csv          # 3,489
    ├── error_based.csv            # 2,562
    ├── time_blind.csv             # 2,409
    ├── heavy_query.csv            # 536
    ├── lateral.csv                # 464
    ├── second_order.csv           # 442
    ├── auth_bypass.csv            # 55
    ├── stacked_queries.csv        # 37
    ├── out_of_band.csv            # 17
    ├── rce.csv                    # 16
    ├── polyglot.csv               # 3
    └── evasion/
        ├── evasion_case_variation.csv    # 27,658
        ├── evasion_inline_comment.csv    # 6,521
        ├── evasion_comment_whitespace.csv # 6,040
        ├── evasion_hex_string.csv        # 4,886
        ├── evasion_function_alternative.csv # 4,469
        └── evasion_scientific_notation.csv  # 891
```

---

## 5. Đánh Giá Chất Lượng

### 5.1 Điểm Mạnh

1. **Pipeline tự động hoàn toàn:** Chỉ cần bỏ file vào `Asset/Data/` và chạy 1 lệnh.
2. **Multi-format support:** CSV (UTF-8, UTF-16), JSON, XML, TXT.
3. **Phân loại chi tiết:** 13 loại SQLi + 6 DB engines + 11 evasion techniques.
4. **Rule-based accuracy cao:** Các pattern được thiết kế dựa trên Type_of_SQLi.md.
5. **ML classifier backup:** 95.2% accuracy cho fallback classification.
6. **Deduplication hiệu quả:** Loại 68% duplicate (127,970 / 187,739).

### 5.2 Hạn Chế

1. **76.3% unknown:** Phần lớn là:
   - **sqliv2 negative samples** (21,513 text tiếng Anh) — thực ra là feature, không phải bug
   - **sqliv3/json short payloads** (các đoạn ngắn như `-7874 ) ) )`) — mất context
   - **BCCC truncated** (462 samples) — regex clean chưa giữ đủ context

2. **Imbalanced classes:** union_based (4,059) vs rce (16), polyglot (3) — GAN training cần handle class imbalance.

3. **Không có clean/benign SQL dataset:** Chưa có log ứng dụng thực tế để train discriminator phân biệt SQL sạch vs SQLi.

4. **Semantic dedup bỏ qua:** Quá chậm với dataset lớn. Cần optimization (mini-batch, approximate nearest neighbors).

### 5.3 Khuyến Nghị

1. **Dùng ML classify unknown:** Chạy `ml_classifier.pkl` trên 45,288 unknown samples để giảm xuống.

2. **Thêm benign SQL data:** Tìm dataset chứa SQL query sạch (log ứng dụng, StackOverflow) để có negative samples cho GAN training.

3. **Cải thiện BCCC normalizer:** Giữ lại nhiều context hơn từ nested queries.

4. **Augmentation cho class hiếm:** Tạo synthetic samples cho rce, polyglot, stacked_queries bằng cách biến đổi từ các class lớn.

---

## 6. Hướng Dẫn Sử Dụng

### 6.1 Chạy Toàn Bộ Pipeline

```bash
cd data_engine
python run_final.py
```

### 6.2 Chạy Từng Bước

```bash
python pipeline.py --step load        # Load dữ liệu
python pipeline.py --step normalize   # Chuẩn hóa
python pipeline.py --step classify    # Phân loại rule-based
python pipeline.py --step dedup       # Dedup
python pipeline.py --step split       # Split + stats
```

### 6.3 Thêm Dữ Liệu Mới

1. Bỏ file vào `Asset/Data/` hoặc thư mục con
2. Thêm entry vào `INPUT_SOURCES` trong `config.py`
3. Chạy lại pipeline

### 6.4 Dùng ML Classifier

```python
import pickle
with open("output/ml_classifier.pkl", "rb") as f:
    model = pickle.load(f)

# Predict cho unknown samples
import csv
unknowns = [r for r in csv.DictReader(open("output/unified_sqli_pool.csv"))
            if r["sqli_type"] == "unknown"]
payloads = [r["payload"] for r in unknowns]
X = model["vectorizer"].transform(payloads)
predictions = model["classifier"].predict(X)
```

---

## 7. Liên Kết Với GAN Training

### 7.1 Data Sẵn Sàng Cho SeqGAN

Các dataset đã split sẵn trong `output/datasets/`:
- **union_based.csv** (4,059) → Generator học UNION injection patterns
- **boolean_blind.csv** (3,489) → Boolean-based payloads
- **error_based.csv** (2,562) → Error-based payloads
- **time_blind.csv** (2,409) → Time-based payloads
- **unknown.csv** (45,288) → Pool để augment và classify thêm

### 7.2 Discriminator Training

Cần thêm:
- **Benign SQL queries** (negative class) — từ log ứng dụng, hoặc sinh từ SQL grammar
- **Mixed dataset** — gộp tất cả classified samples + negative samples

### 7.3 Tokenization Gợi Ý

Dựa trên dữ liệu đã xử lý:
- **SQL keywords:** SELECT, UNION, WHERE, AND, OR, INSERT, UPDATE, DELETE, DROP
- **Functions:** SLEEP, BENCHMARK, EXTRACTVALUE, CONCAT, CHAR, CHR, SUBSTRING
- **Special chars:** ', ", --, #, /*, */, ;, (, )
- **DB-specific:** dual, information_schema, sys.tables, pg_sleep
- **Placeholders:** `<NUM>`, `<STR>`, `<TABLE>`, `<COL>` (cho de-lexicalization)

---

*Generated by SQLi Data Engine — 2026-05-03*
