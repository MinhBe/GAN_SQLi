# V4 Pipeline Guide — Phase 2 (Subagent) → Phase 3 (Transform) → Phase 4 (Tier)

> **Mục đích**: Tài liệu cách hoạt động của pipeline xử lý dataset từ Phase 2 đến Phase 4.
> **Output cuối**: Gold/Silver/Bronze tiers cho V4 training.

---

## 1. TỔNG QUAN PIPELINE

Pipeline xử lý **22,401 RELABEL rows** + **18,144 KEEP rows** từ Phase 1 (TRIAGE)
thành 3-tier dataset (Gold/Silver/Bronze) cho V4 training.

```
  to_relabel.csv (22,401 rows)     keep.csv (18,144 rows)
       │
       ▼
  [P2a] Pre-label A+C → chat_queue.csv
    label_payload.py --mode chat_queue
       │
       ▼
  [P2b] Chia chunks (200 rows/chunk)
    chat_label_coordinator.py --chunk_size 200
       │
       ├── chunk_001.csv  ...  chunk_NNN.csv
       ▼
  [P2c] Subagent labeling (Rule + Heuristic)
    113 chunks × ~200 rows
    Mỗi chunk → chunk_NNN_labeled.csv
       │
       ▼
  [P2d] Merge chunks → relabeled_chat.csv
    merge_chunks.py
       │
       ▼
  [P3a] Concat: keep.csv + relabeled_chat.csv → merged_final.csv
       │
       ▼
  [P3b] Strip wrapper → payload_inner
    strip_wrapper.py
       │
       ▼
  [P3c] Delex v2 → payload_delex_v2 + signature
    delex_v2.py --stats
       │
       ▼
  [P4a] Resample balanced
    resample_balanced.py --cap_signature 30 --cap_type_db 300
       │
       ▼
  [P4b] Tier split
    tier_split.py
       │
       ├── gold.csv    (conf≥0.90, sources_agree=3)
       ├── silver.csv  (conf≥0.70, sources_agree≥2)
       └── bronze.csv  (rest)
```

## 2. INPUT/OUTPUT SCHEMA TỪNG BƯỚC

### P2a: label_payload.py --mode chat_queue

| | Chi tiết |
|---|---|
| **Input** | `to_relabel.csv` |
| **Columns input** | id, payload_norm, sqli_type, db_engine, confidence, reasoning, verdict, critique_reasons |
| **Output** | `chat_queue.csv` |
| **Columns thêm** | a_type, a_db, a_signals, c_type, c_db, c_signals |
| **Cách chạy** | `python Skill/sqli-data-curator/scripts/label_payload.py --mode chat_queue --input to_relabel.csv --output chat_queue.csv` |
| **Thời gian** | ~2 phút |

### P2b: chat_label_coordinator.py

| | Chi tiết |
|---|---|
| **Input** | `chat_queue.csv` |
| **Output** | `_chunks/chunk_001.csv` ... `chunk_NNN.csv`, `_chunks/prompts.json` |
| **Số chunks** | ceil(22,401 / 200) = **113 chunks** |
| **Cách chạy** | `python Skill/sqli-data-curator/scripts/chat_label_coordinator.py --input chat_queue.csv --chunk_size 200 --temp_dir _chunks/` |
| **Thời gian** | ~30 giây |

### P2c: Subagent labeling

| | Chi tiết |
|---|---|
| **Input** | `chunk_NNN.csv` (9 columns) |
| **Output** | `chunk_NNN_labeled.csv` (7 columns, exact order) |
| **Schema output** | `id, payload_inner, sqli_type, db_engine, confidence, reasoning, sources_agree` |
| **Cách chạy** | Batch Python script hoặc Task subagent |
| **Subagent cần đọc** | SKILL.md, taxonomy.md, function_whitelist.md |
| **Thời gian** | ~1-1.5 giờ (parallel) |

### P2d: merge_chunks.py

| | Chi tiết |
|---|---|
| **Input** | `_chunks/chunk_*_labeled.csv` |
| **Output** | `relabeled_chat.csv` |
| **Validation** | Schema đúng, sqli_type ∈ taxonomy, db_engine ∈ valid, confidence ∈ [0,1], reasoning ≥ 10 chars |
| **Dedup** | Theo `id`, giữ first |
| **Cách chạy** | `python Skill/sqli-data-curator/scripts/merge_chunks.py --temp_dir _chunks/ --output relabeled_chat.csv` |
| **Thời gian** | ~1 phút |

### P3a: Concat KEEP + RELABELED

| | Chi tiết |
|---|---|
| **Input** | `keep.csv` + `relabeled_chat.csv` |
| **Logic** | `pd.concat([keep, relabeled]).drop_duplicates(subset='id')` |
| **Output** | `merged_final.csv` (~40,000 rows) |
| **Cách chạy** | Python one-liner |
| **Thời gian** | ~10 giây |

### P3b: strip_wrapper.py

| | Chi tiết |
|---|---|
| **Input** | `merged_final.csv` (cột `payload_norm`) |
| **Output** | `stripped.csv` (thêm cột `payload_inner`) |
| **Logic** | Regex strip 3 patterns wrapper (xem wrapper_patterns.md) |
| **Cách chạy** | `python Skill/sqli-data-curator/scripts/strip_wrapper.py --input merged_final.csv --output stripped.csv --col_in payload_norm --col_out payload_inner` |
| **Thời gian** | ~1 phút |

### P3c: delex_v2.py

| | Chi tiết |
|---|---|
| **Input** | `stripped.csv` (cột `payload_inner`) |
| **Output** | `dataset_v3.csv` (thêm `payload_delex_v2`, `signature`) |
| **Logic** | Giữ ~30 function names trong whitelist, thay phần còn lại bằng `__IDENT__/__STR__/__INT__` |
| **Cách chạy** | `python Skill/sqli-data-curator/scripts/delex_v2.py --input stripped.csv --output dataset_v3.csv --col_in payload_inner --col_out payload_delex_v2 --stats` |
| **Thời gian** | ~3 phút |

### P4a: resample_balanced.py

| | Chi tiết |
|---|---|
| **Input** | `dataset_v3.csv` (~40,000 rows) |
| **Output** | `dataset_v3_balanced.csv` (~12,000-18,000 rows) |
| **Params** | `--cap_signature 30 --cap_type_db 300` |
| **Cách chạy** | `python Skill/sqli-data-curator/scripts/resample_balanced.py --input dataset_v3.csv --output OpenCode/dataset_v3_balanced.csv --cap_signature 30 --cap_type_db 300` |
| **Thời gian** | ~1 phút |

### P4b: tier_split.py

| | Chi tiết |
|---|---|
| **Input** | `dataset_v3_balanced.csv` |
| **Output** | `gold.csv`, `silver.csv`, `bronze.csv` |
| **Gold** | confidence ≥ 0.90 AND sources_agree == 3 |
| **Silver** | confidence ≥ 0.70 AND sources_agree ≥ 2 |
| **Bronze** | Rest |
| **Cách chạy** | `python Skill/sqli-data-curator/scripts/tier_split.py --input OpenCode/dataset_v3_balanced.csv --output_dir OpenCode/` |
| **Thời gian** | ~30 giây |

## 3. SUBAGENT LABELING (P2c) CHI TIẾT

### 3.1. Luồng xử lý mỗi chunk

Khi subagent nhận chunk, thực hiện:

1. **Đọc context**: SKILL.md, taxonomy.md, function_whitelist.md
2. **Đọc chunk CSV**: id, payload_norm, payload_inner, a_type, a_db, a_signals, c_type, c_db, c_signals
3. **Phân loại từng row** bằng `label_chunk_helper.py`:
   - `extract_signals()`: Tìm function names trong whitelist
   - `classify_payload()`: Dùng signals + heuristic + A/C hints → sqli_type + db_engine
   - `generate_reasoning()`: Tạo reasoning ≥ 50 chars với evidence token
   - `compute_confidence()`: Dựa trên số signals + reasoning length
   - `compute_sources_agree()`: So sánh sqli_type với a_type và c_type
4. **Ghi output**: `chunk_NNN_labeled.csv` với 7 cột chuẩn

### 3.2. 3-source signal model

| Source | Engine | Output |
|--------|--------|--------|
| **A** Rule (regex) | Regex sqlmap-style | `a_type`, `a_db`, `a_signals` |
| **C** Heuristic | Structure analysis | `c_type`, `c_db`, `c_signals` |
| **Final** (subagent) | Helper + LLM reasoning | `sqli_type`, `db_engine`, `confidence`, `reasoning` |

- **sources_agree = 3**: khớp cả A và C
- **sources_agree = 2**: khớp 1 trong 2
- **sources_agree = 1**: khác cả 2

### 3.3. Priority-based conflict resolution (từ taxonomy.md)

Khi payload có nhiều signals, dùng priority (lower = stronger):

| Priority | Type | 
|:--------:|------|
| 1 | benign |
| 2 | auth_bypass |
| 3 | boolean_blind |
| 4 | error_based / heavy_query |
| 5 | time_blind |
| 6 | out_of_band |
| 7 | union_based |
| 8 | stacked_queries |
| 9 | polyglot |

### 3.4. Cách resume nếu subagent bị dừng

1. Detect chunk nào chưa có `_labeled.csv`
2. Chỉ spawn subagent cho chunks missing
3. Các chunk đã label giữ nguyên, không cần làm lại

## 4. VERIFICATION CHECKLIST

Sau khi có gold.csv:

| Metric | Target | Cách verify |
|--------|--------|-------------|
| Gold size | ≥ 5,000 rows | `wc -l gold.csv` |
| Collision rate gold | < 15% | `1 - payload_delex_v2.nunique() / len(gold)` |
| Top-10 coverage gold | < 10% | `value_counts().head(10).sum() / len(gold)` |
| Reasoning mean | > 60 chars | `reasoning.str.len().mean()` |
| Top 5 reasoning duplicates | < 50 lần mỗi cái | `reasoning.value_counts().head(5)` |
| Type entropy gold | > 2.0 bits | `-sum(p * log2(p))` |
| Type × DB holes | < 5 cells | `pd.crosstab(sqli_type, db_engine)` |
| Subagent consistency | ≥ 90% | Rerun 100 rows, compare agreement |

## 5. THỜI GIAN DỰ KIẾN

```
P2a: Pre-label A+C          ~2 phút
P2b: Chia chunks             ~30 giây
P2c: Label chunks             1-1.5 giờ (113 chunks, batch)
P2d: Merge chunks             ~1 phút
P3a: Concat                   ~10 giây
P3b: Strip wrapper            ~1 phút
P3c: Delex v2                 ~3 phút
P4a: Resample                 ~1 phút
P4b: Tier split               ~30 giây
                              ─────────
Tổng wall-clock:             ~1.5-2 giờ
```
