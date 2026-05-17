---
name: sqli-data-curator
description: |
  Curate, relabel, and prepare SQL injection datasets for GAN training. Use when:
  preparing a SQLi dataset for SeqGAN/GAN training, fixing label quality issues
  (vague reasoning, low confidence, type-DB mismatch), applying delex with function
  whitelist (preserve xmltype/pg_sleep/etc), stripping wrapper bias (select * from
  users WHERE...), stratified resampling to fix dataset bias, or triaging existing
  labels into Keep/Relabel/Drop. Use this skill aggressively whenever someone
  mentions SQLi data quality, mode collapse caused by data, dataset preparation
  for adversarial training, or asks to clean/label SQLi payloads — even if they
  don't explicitly say "curate" or "relabel".
  Replaces the three older skills (sqli-labeler, sqli-label-validator, sqli-label-critic).
---

# sqli-data-curator — Skill Guide

## Role & Prime Directive

Bạn là **chuyên gia làm sạch dataset SQLi** cho GAN training. Mục tiêu: biến dataset
thô (40,860 rows với label chất lượng không đều) thành 3-tier dataset (Gold/Silver/Bronze)
có thể dùng huấn luyện GAN chống mode collapse.

**Tại sao cần skill này**: Mode collapse trong SeqGAN SQLi không phải do training dynamics
mà do **dữ liệu**. Bằng chứng cụ thể:
- 71.89% payload delex thành duplicate (5,009 unique từ 17,821 rows)
- 100% function names (xmltype, pg_sleep, extractvalue, ...) bị xóa sau delex
- 53.64% payload bị bao bởi wrapper `select * from users WHERE username = "..."`
- 40% labels có reasoning < 20 chars (không thể verify)

→ Fix data trước, mới có ý nghĩa fix GAN.

---

## Architecture Overview

```
combined_labeled_data.csv (40,860 rows)
        │
        ▼
  Phase 1: TRIAGE          → Keep / Relabel / Drop verdict
        │       (scripts/critique_labels.py)
        ▼
  Phase 2: RELABEL         → 3-source validation (rule + Haiku + heuristic)
        │       (scripts/label_payload.py)
        ▼
  Phase 3: TRANSFORM       → strip wrapper + delex_v2 + signature
        │       (scripts/strip_wrapper.py, delex_v2.py)
        ▼
  Phase 4: TIER & RESAMPLE → Gold/Silver/Bronze tiers + cap per signature
        │       (scripts/resample_balanced.py — phase 4 tool, not yet built)
        ▼
  dataset_v3/
    gold.csv      (~3,000 rows, conf≥0.90, 3/3 source agree)
    silver.csv    (~5,000 rows, conf 0.70-0.89)
    bronze.csv    (~2,000 rows, low conf, D-only)
    benign.csv    (~5,000 rows, audited)
```

---

## Phase 1 — TRIAGE (script: `critique_labels.py`)

Cho mỗi row trong dataset, gán 1 verdict:

| Verdict | Khi nào | Hành động sau đó |
|---------|---------|------------------|
| **DROP** | type ∈ {ldap_injection, command_injection, second_order, inline_query, comment_based, rce, generic} HOẶC payload < 5 chars | Xóa khỏi dataset |
| **RELABEL** | type='unknown' HOẶC reasoning < 20 chars HOẶC confidence < 0.70 HOẶC rule-check disagrees | Đưa sang Phase 2 |
| **KEEP** | Passes tất cả checks trên | Đưa thẳng sang Phase 3 |

**Lý do thiết kế**: User đã quyết định DROP 134 rows long-tail (0.3% data). Reasoning < 20 chars là dấu hiệu pattern-matching cứng (top 5 reasoning chiếm 22% data, lặp lại y nguyên 2066 lần) → cần relabel với evidence chi tiết.

**Lệnh chạy**:
```bash
python Skill/sqli-data-curator/scripts/critique_labels.py \
    --input Asset/LabelData/combined_labeled_data.csv \
    --output Asset/LabelData/triaged.csv
```

Output column: `verdict, critique_reasons, suggested_type, suggested_db`.

---

## Phase 2 — RELABEL (script: `label_payload.py`)

Cho rows có verdict=RELABEL, chạy **3-source validation**:

| Source | Engine | Cách hoạt động |
|--------|--------|----------------|
| **A** Rule | Regex sqlmap-style | Match patterns cứng (xmltype, sleep, union select, ...) |
| **B** Haiku | Claude Haiku 4.5 API | LLM verify với requirement "quote specific tokens" |
| **C** Heuristic | Structure analysis | Priority + DB signature + length + special cases |

**Voting**:
- 3/3 đồng ý → confidence=1.00, reasoning ghép từ 2 sources tốt nhất
- 2/3 đồng ý → confidence=0.85
- 1/3 (all disagree) → confidence=0.50, dùng priority tiebreaker → FLAG human
- Empty → confidence=0.30, DROP

**Reasoning quality**: bắt buộc ≥ 50 chars, ghép từ các source agreeing. Format:
```
"Pattern match: 'pg_sleep' → time_blind (P5); DB signature: postgresql"
 | "haiku: pg_sleep is a PostgreSQL function for time-based blind SQLi"
```

**Setup Anthropic API**:
```bash
export ANTHROPIC_API_KEY=sk-ant-...
pip install anthropic
```

**Lệnh chạy**:
```bash
# Filter RELABEL rows first
python -c "
import pandas as pd
df = pd.read_csv('triaged.csv')
df[df['verdict']=='RELABEL'].to_csv('to_relabel.csv', index=False)
"

# Run 3-source labeling
python Skill/sqli-data-curator/scripts/label_payload.py \
    --input to_relabel.csv \
    --output relabeled.csv \
    --col payload_inner \
    --sleep 0.1
```

Nếu không có ANTHROPIC_API_KEY, source B bị skip, chỉ dùng A+C (confidence cao nhất là 0.85).

---

## Phase 3 — TRANSFORM (scripts: `strip_wrapper.py`, `delex_v2.py`)

### 3a. Strip wrapper

Bóc tách 3 dạng wrapper khỏi 53.64% payload (xem `references/wrapper_patterns.md`):
```
select * from users WHERE username = "<INNER>"   → giữ <INNER>
select * from users WHERE username = '<INNER>'   → giữ <INNER>
select * from <T> WHERE <C> = "<INNER1>" OR <C> = "<INNER2>" → giữ longer
```

Sinh column `payload_inner`. Nếu không có wrapper, `payload_inner = payload_norm`.

```bash
python Skill/sqli-data-curator/scripts/strip_wrapper.py \
    --input relabeled.csv --output stripped.csv \
    --col_in payload_norm --col_out payload_inner
```

### 3b. delex_v2 với function whitelist

Khác V1 ở chỗ giữ nguyên ~30 SQLi-significant functions (xem `references/function_whitelist.md`):
```
xmltype, pg_sleep, sleep, waitfor, benchmark, extractvalue, updatexml,
dbms_pipe, randomblob, elt, rlike, chr, concat, cast, ...
```

Tất cả identifier khác → `__IDENT__`. Strings → `__STR__`. Numbers → `__INT__`.

```bash
python Skill/sqli-data-curator/scripts/delex_v2.py \
    --input stripped.csv --output delex_v2.csv \
    --col_in payload_inner --col_out payload_delex_v2 \
    --stats
```

### 3c. Compute signature

```python
signature = SHA1(payload_delex_v2)[:8]
```

Dùng cho stratified resample (Phase 4). 2 payloads cùng signature → cùng "skeleton" pattern.

---

## Phase 2 Mode B — Chat (subagent song song, không API)

Khi không có `ANTHROPIC_API_KEY` hoặc muốn dùng Claude Code session thay vì API:

### Bước 1: Pre-label A+C làm hint cho subagent

```bash
python scripts/label_payload.py --mode chat_queue \
    --input to_relabel.csv --output chat_queue.csv
```

Output `chat_queue.csv` có thêm columns `a_type, a_db, a_signals, c_type, c_db, c_signals`.

### Bước 2: Chia chunks + sinh prompts.json

```bash
python scripts/chat_label_coordinator.py \
    --input chat_queue.csv \
    --chunk_size 200 \
    --temp_dir Asset/LabelData/_chunks/
```

Output:
- `_chunks/chunk_001.csv`, `chunk_002.csv`, ... (N chunks)
- `_chunks/prompts.json` — orchestration plan

### Bước 3: Main Claude session spawn subagents

Main session đọc `prompts.json` rồi dùng tool **Agent** (`subagent_type=general-purpose`)
spawn song song (parallel 10/đợt). Mỗi subagent đọc SKILL.md + taxonomy.md + chunk CSV,
label từng row, ghi `chunk_NNN_labeled.csv`.

### Bước 4: Merge tất cả chunks

```bash
python scripts/merge_chunks.py \
    --temp_dir Asset/LabelData/_chunks/ \
    --output Asset/LabelData/relabeled_chat.csv
```

Tự động validate schema, dedup id, in quality report.

---

## Phase 4 — TIER & RESAMPLE (scripts: `resample_balanced.py`, `tier_split.py`)

### 4a. Resample balanced

Cap mỗi `signature` ≤ 30 rows + mỗi `(sqli_type, db_engine)` ≤ 300 rows:

```bash
python scripts/resample_balanced.py \
    --input dataset_v3.csv \
    --output dataset_v3_balanced.csv \
    --cap_signature 30 --cap_type_db 300
```

Tự compute `signature` column nếu chưa có.

### 4b. Tier split

Chia thành Gold / Silver / Bronze theo `confidence` + `sources_agree`:

```bash
python scripts/tier_split.py \
    --input dataset_v3_balanced.csv \
    --output_dir SeqGAN_SQLi/data/v3/
```

Output:
- `gold.csv`: `conf ≥ 0.90 AND sources_agree == 3` → dùng cho MLE + RL real
- `silver.csv`: `conf ≥ 0.70 AND sources_agree ≥ 2` → augment cho RL
- `bronze.csv`: rest → chỉ làm negative cho D

### Synthetic augment (optional, chưa code)
Cho cells (type × db) < 50 rows, sinh thêm từ templates trong `assets/synthetic_templates.json`.

---

## Output Schema (final)

```csv
id, payload_norm, payload_inner, payload_delex_v2, signature,
sqli_type, db_engine, confidence, reasoning, tier, sources_agree,
verdict
```

| Column | Mô tả |
|--------|-------|
| `payload_norm`     | Payload gốc (cho evaluate.py, WAF test) |
| `payload_inner`    | Đã strip wrapper (cho GAN training input) |
| `payload_delex_v2` | Delex giữ function names |
| `signature`        | SHA1(delex_v2)[:8] cho stratified sampling |
| `sources_agree`    | 0/1/2/3 — bao nhiêu source đồng ý |
| `tier`             | gold/silver/bronze |
| `verdict`          | KEEP/RELABEL/DROP từ Phase 1 |
| `reasoning`        | ≥ 50 chars với evidence cụ thể |

---

## Quick-Start: Prototype 1000 rows

Test pipeline đầy đủ Phase 1-3 trên 1000 rows trước khi chạy full 40,860:

```bash
python Skill/sqli-data-curator/scripts/run_prototype.py \
    --input Asset/LabelData/combined_labeled_data.csv \
    --n_samples 1000 \
    --seed 42 \
    --output Asset/LabelData/prototype_v3.csv
```

**Success criteria** (kiểm tra output):
- `delex_v2 collision rate < 30%` (vs original 71.89%)
- `vocab size 100-180 tokens` (vs original 89)
- `top-100 signatures cover < 25% data` (vs original 42.82%)
- `function preservation rate > 95%` cho xmltype, pg_sleep, extractvalue, ...

Nếu fail bất kỳ tiêu chí nào → adjust whitelist trong `function_whitelist.md` và rerun.

---

## Pre-flight Checklist

Verify trước khi chạy full pipeline:

- [ ] `Asset/LabelData/combined_labeled_data.csv` tồn tại (40,860 rows)
- [ ] `pip install anthropic pandas numpy sqlparse`
- [ ] `ANTHROPIC_API_KEY` exported (cho source B Haiku)
- [ ] `references/` đã đọc: taxonomy.md, function_whitelist.md, wrapper_patterns.md
- [ ] Smoke test prototype 1000 rows → mọi metric đạt target
- [ ] Backup dataset gốc trước khi overwrite

---

## Reference Files

| File | Khi nào đọc |
|------|-------------|
| `references/taxonomy.md` | Khi không chắc về type/DB taxonomy hoặc cần xác định priority |
| `references/function_whitelist.md` | Khi thiết kế delex hoặc thấy function không được preserve |
| `references/wrapper_patterns.md` | Khi gặp wrapper pattern lạ hoặc cần debug strip_wrapper.py |

---

## Architecture Decisions

| Quyết định | Lý do |
|------------|-------|
| 1 skill thay 3 (labeler+validator+critic) | Overlap workflow lớn; user yêu cầu gộp |
| 3-source voting | Không tin 1 nguồn duy nhất; majority vote chống bias |
| Drop 134 long-tail rows | Đồng ý của user: rce/ldap/inline → out of scope SQLi |
| Function whitelist (30 funcs) | Bảng chứng minh: 100% xmltype/pg_sleep/extractvalue bị mất sau delex V1 |
| Strip wrapper | 53.64% bias → mode collapse |
| Cap signature ≤ 30 rows | Top-100 patterns chiếm 42.82% data → cần cân bằng |
| Claude Haiku 4.5 cho source B | User chọn; rate limit OK cho 40k rows |

---

## Pipeline Tổng Thể (end-to-end)

```bash
# Phase 1: Triage
python scripts/critique_labels.py \
    --input Asset/LabelData/combined_labeled_data.csv \
    --output Asset/LabelData/triaged.csv

# Filter rows by verdict
python -c "
import pandas as pd
df = pd.read_csv('Asset/LabelData/triaged.csv')
df[df['verdict']=='KEEP'].to_csv('Asset/LabelData/keep.csv', index=False)
df[df['verdict']=='RELABEL'].to_csv('Asset/LabelData/to_relabel.csv', index=False)
print(df['verdict'].value_counts())
"

# Phase 2: Relabel uncertain rows
python scripts/label_payload.py \
    --input Asset/LabelData/to_relabel.csv \
    --output Asset/LabelData/relabeled.csv \
    --col payload_norm --sleep 0.1

# Merge KEEP + RELABELED
python -c "
import pandas as pd
keep = pd.read_csv('Asset/LabelData/keep.csv')
relabeled = pd.read_csv('Asset/LabelData/relabeled.csv')
# Apply new labels from Phase 2
relabeled['sqli_type'] = relabeled['new_sqli_type']
relabeled['db_engine'] = relabeled['new_db_engine']
relabeled['confidence'] = relabeled['new_confidence']
relabeled['reasoning'] = relabeled['new_reasoning']
merged = pd.concat([keep, relabeled], ignore_index=True)
merged.to_csv('Asset/LabelData/merged.csv', index=False)
"

# Phase 3: Strip wrapper + delex_v2
python scripts/strip_wrapper.py \
    --input Asset/LabelData/merged.csv \
    --output Asset/LabelData/stripped.csv

python scripts/delex_v2.py \
    --input Asset/LabelData/stripped.csv \
    --output Asset/LabelData/dataset_v3.csv \
    --col_in payload_inner --stats

# (Phase 4 TIER+RESAMPLE coming later)
```
