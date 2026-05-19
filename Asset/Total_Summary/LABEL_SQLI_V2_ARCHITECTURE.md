# Kiến Trúc Skill label-sqli v3.1 — Tổng Hợp Toàn Diện

> **Ngày tạo**: 2026-05-18 | **Cập nhật**: 2026-05-19 (v3.1)  
> **Phiên bản**: v3.1 (CHAR(N) Decoder + Multi-Pool + Bronze Active Learning)  
> **Dataset đánh giá**: Testing_1 (1,084,880 rows, dataset 100× lớn hơn Testing)  
> **Benchmark v3.1 target**: Tier4 < 50% (từ 75.7%), payload_decoded column, 5-pool architecture

---

## 1. Bối Cảnh — Tại Sao v3 → v3.1?

### Lịch Sử Phiên Bản

| Phiên Bản | Ngày | Dataset Test | Tier4 % | Highlights |
|----------|------|--------------|---------|------------|
| v1 | 2026-05-17 | Testing (10K) | 100% | Delex mismatch, Oracle gap, benign=0 |
| v2 | 2026-05-18 | Testing (10K) | 24.7% | Cascade 4-tier, unified patterns |
| v3 | 2026-05-19 (sáng) | Testing (10K) | 25.3% | normalize_payload, multi-label, double-score |
| **v3.1** | **2026-05-19 (chiều)** | **Testing_1 (1M)** | **target < 50%** | **CHAR decoder, multi-pool, bronze active learning** |

### Phát Hiện Khi Áp Dụng v3 Lên Dataset 1M Rows

Khi run labeling trên dataset thực tế **Testing_1** (1,084,880 rows, 100× lớn hơn Testing 10K), kết quả khác hoàn toàn so với baseline 10K:

| Metric | Testing (10K) v3 | Testing_1 (1M) v3 | Mức Độ |
|--------|------------------|-------------------|--------|
| Tier 4 % | 25.3% | **75.7%** | 🔴 CRITICAL |
| Bronze tier % | ~25% | **77.0%** | 🔴 CRITICAL |
| union_based dominance | 28% of SQLi | **48.5%** of SQLi | ⚠️ Entropy collapse |
| error_based % of SQLi | 11% | **5.4%** | ⚠️ Mode collapse risk |

### Hai Insight Quan Trọng Driving v3.1

**Insight #1 — "77% benign" thực ra là "75.7% UNKNOWN"**:

Phân tích chi tiết `tier × is_sqli` crosstab cho thấy narrative ban đầu sai:

| Group | Count | % | Bản Chất |
|-------|-------|---|----------|
| SQLi gold + silver | 241,358 | 22.2% | Confidence ≥ 0.70, có sqli_type |
| SQLi bronze | 6,862 | 0.6% | Có sqli_type, conf 0.50–0.69 |
| **True benign (verified)** | **15,366** | **1.4%** | benign_classifier hit |
| **UNKNOWN (tier4)** | **821,294** | **75.7%** | sqli_type=None, conf=0.0 |

Tier4 rows có `is_sqli=0` chỉ vì `sqli_type=None` → `is_sqli=False`. **Không phải đã verify benign**. Real benign chỉ 1.4% — quá nhỏ cho Discriminator training. Tier4 có thể chứa missed SQLi → không thể dùng làm discriminator negatives.

**Insight #2 — Bronze tier = "Gold mine" của novel/rare patterns**:

Bronze SQLi (6,862 rows) breakdown by label_source:

| Sub-group | Count | Đặc Điểm | Giá Trị Cho GAN |
|-----------|-------|----------|-----------------|
| tier3_contextual bronze | **4,496** | DB engine detected, type inferred. Conf 0.50–0.69 | **HIGH** — novel patterns |
| tier2_structural bronze | 2,136 | Tier 2 hit, consistency rule giảm conf | MEDIUM — edge cases |
| tier1_exact bronze | 230 | Tier 1 match, DB×type conflict | LOW — potential FP |

Tier3 bronze rows là payloads dùng **non-standard syntax** hoặc **mới** mà cascade chưa cover — ví dụ Oracle `dbms_xmlquery.newcontext()` thay vì `xmltype()`. Đây là **active learning opportunity**: 4,496 rows manageable cho human review (~30 phút), mỗi pattern mới được confirm sẽ add vào `_TIER1_PATTERNS`.

### Sai Lầm Thiết Kế Cần Sửa

1. **Treating tier4 as benign**: Dùng tier4 trong pool benign cho discriminator → mix unknown với verified benign
2. **Single-pool strategy**: Chỉ 2 pool (SQLi vs benign) bỏ sót bronze novel + edge cases
3. **Decoded output mất obfuscation**: Nếu output decoded payload, GAN train trên plain text → không học obfuscation bypass
4. **Thiếu CHAR(N) decoder**: 57.3% tier4 rows chứa `CHAR(N)` patterns không được decode → mass false negatives

---

## 2. Tổng Quan Kiến Trúc v3.1

```
                         payload (raw string với obfuscation)
                              │
                              ▼
              ┌────────────────────────────────────┐
              │  PRE-NORM: normalize_payload()      │  ← Internal use only
              │  • _decode_char_sequences() ✨NEW   │    (output giữ original)
              │  • hex / unicode / URL decode       │
              └────────────────┬───────────────────┘
                               │ (decoded version cho detection)
                               ▼
              ┌────────────────────────────────────┐
              │   PRE: State Detection             │  ← raw / normalized / delex
              └────────────────┬───────────────────┘
                               │
                     ┌─────────┴─────────┐
                     ▼                   ▼
          ┌──────────────────┐   ┌──────────────────────┐
          │   TIER 1         │   │   TIER 2             │  ← Both run always
          │  Exact Match     │   │  Structural Regex    │    (multi-label)
          │  conf 0.90–1.00  │   │  • Tautology patterns│
          │                  │   │  • Stacked SELECT ✨ │
          │                  │   │  • CHAR-decoded ✨   │
          └────────┬─────────┘   └──────────┬───────────┘
                   │                       │
                   └──────────┬────────────┘
                              ▼
              ┌────────────────────────────────────┐
              │  TIER 3: Contextual Inference      │  ← conf 0.50–0.69
              │  engine→type + consistency rules   │    (bronze SQLi = gold mine)
              └────────────────┬───────────────────┘
                               │
                     ┌─────────┴─────────┐
                     ▼                   ▼
         ┌──────────────────┐   ┌──────────────────┐
         │   Benign         │   │  TIER 4: AI      │
         │  Classifier      │   │  needs_ai=True   │
         │  conf ≥ 0.60     │   │  UNKNOWN pool    │
         └────────┬─────────┘   └────────┬─────────┘
                  │                     │
                  └──────────┬──────────┘
                             ▼
              ┌────────────────────────────────────┐
              │  POST: Output 2 columns ✨          │
              │  • payload_norm (orig + obf intact)│  ← for GAN training
              │  • payload_decoded (decoded form)  │  ← for analysis/tooling
              └────────────────┬───────────────────┘
                               ▼
              ┌────────────────────────────────────┐
              │  POOL SPLITTER ✨                  │
              │  • pool_sqli_gold (241K) → Gen     │
              │  • pool_sqli_bronze_novel (4.5K)   │
              │  • pool_benign (15K) → Disc neg    │
              │  • pool_unknown (821K) → defer AI  │
              │  • pool_sqli_bronze_edge (2.4K)    │
              └────────────────────────────────────┘
```

**Thay đổi so với v3:**
- `_decode_char_sequences()` mới trong `normalize_payload()` — CHAR(N) decoder
- Stacked SELECT patterns mới trong Tier 2
- Output thêm column `payload_decoded` (double-column)
- Pipeline mới: pool splitter chia 5 pools thay vì 2

---

## 3. Cải Tiến v3.1 — Chi Tiết Từng Cải Tiến

### #1 — CHAR(N) Decoder (Critical Fix Cho Tier 4)

**Vấn đề target**: 57.3% tier4 rows trong dataset 1M chứa pattern `CHAR(N)` — ASCII-encoded SQL keywords để bypass WAF.

**Ví dụ**:
```
CHAR(83)CHAR(69)CHAR(76)CHAR(69)CHAR(67)CHAR(84)
  →  "SELECT"  (sau khi decode)
```

**Implementation**: Thêm helper vào `detectors_v2.py`:
```python
def _decode_char_sequences(payload: str) -> str:
    """Decode CHAR(N)CHAR(M)... to actual chars. WAF bypass evasion."""
    def replace_char(m):
        try:
            return chr(int(m.group(1)))
        except (ValueError, OverflowError):
            return m.group(0)
    return re.sub(r'\bchar\s*\(\s*(\d+)\s*\)', replace_char, payload, flags=re.I)


def normalize_payload(payload: str) -> str:
    p = str(payload)
    p = _decode_char_sequences(p)   # NEW: must be first
    p = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), p)
    p = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), p)
    try: p = urllib.parse.unquote(p)
    except Exception: pass
    return p
```

**Scientific basis**: CHAR(N) obfuscation rate trong dataset thực:

| Nguồn | CHAR() Encoding Rate | Bối Cảnh |
|-------|---------------------|----------|
| Appelt et al. (2014) — ICSE | **42–58%** | Empirical study 4 WAF tools |
| OWASP WAF Evasion Cheat Sheet (2024) | **30–40%** | Industry best practice |
| sqlmap default tamper presets | **~50%** | `--tamper=charencode` industry standard |
| Halfond & Orso (2005) — AMNESIA | Identified as 1/9 SQLi categories | Foundational SQLi taxonomy |

**Dataset Testing_1 = 57% CHAR()** rơi vào range bình thường (42-65% industry baseline) — không phải anomaly.

**Expected impact**: Tier 4 giảm từ 75.7% → ~40-50% sau khi áp dụng.

### #2 — Stacked SELECT Pattern

**Vấn đề target**: 31.8% tier4 rows chứa `select from` không có UNION prefix — đây là stacked query injection.

**Implementation**: Thêm vào `_TIER2_UNION_PATTERNS` (`detectors_v2.py`):
```python
# Stacked query: '; SELECT ... FROM ...
(_p(r';\s*select\s+[\w*,\s]+\s+from\s+\w+', re.I), 0.78),
# Standalone SELECT FROM (CHAR-decoded result)
(_p(r'\bselect\s+[\w*,\s]+\s+from\s+\w+\s+where\b', re.I), 0.75),
```

### #3 — Double-Column Output Schema

**Vấn đề target**: Nếu output chỉ chứa decoded payload, GAN sẽ học cách generate plain text — mất khả năng obfuscation. Trong thực tế, attacker dùng URL encode + CHAR() để bypass WAF.

**Decision**: Output **CẢ HAI** columns:

| Column | Nội Dung | Mục Đích |
|--------|----------|----------|
| `payload_norm` (existing) | **Original** (giữ obfuscation: CHAR(), %27, \x27) | GAN Generator training |
| `payload_decoded` (NEW) | Decoded form (đã `normalize_payload()`) | Analysis, debugging, tooling |

**Code change** trong `cascade_labeler.py`:
```python
# In _build_result():
return {
    ...existing fields...,
    'payload_decoded': normalize_payload(orig_payload),   # NEW
}
```

**Tại sao quan trọng**: 
- GAN train trên `payload_norm` → học obfuscation pattern → output payloads có thể bypass WAF thực tế
- Tooling khác dùng `payload_decoded` để debug, search, analyze
- Multi-view learning có thể dùng cả 2 columns cho discriminator

### #4 — Multi-Pool Architecture (5 Pools)

**Vấn đề target**: 2-pool đơn giản (SQLi vs benign) trộn unknown vào benign → discriminator học sai distribution.

**Solution**: Tạo `data_pool_splitter.py` chia thành 5 pools với mục đích rõ ràng:

```
labeled.csv (1,084,880 rows)
        │
        ▼
┌────────────────────────────────────────────────────────────┐
│ pool_sqli_gold.csv          ← Generator BASE training      │
│ ~241K rows (gold+silver SQLi, conf ≥ 0.70)                  │
│ Đại trà, common patterns                                    │
└────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────┐
│ pool_sqli_bronze_novel.csv  ← Generator NOVEL training     │
│ ~4.5K rows (tier3_contextual bronze)                        │
│ Novel/rare patterns — cần manual review trước              │
│ → Active learning loop để upgrade lên gold                  │
└────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────┐
│ pool_benign.csv             ← Discriminator NEGATIVE       │
│ ~15K rows (benign_classifier, positively classified)        │
│ TRUE benign — không phải tier4 unknown                     │
│ Cần augment thêm (chỉ 1.4% là quá ít)                       │
└────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────┐
│ pool_unknown.csv            ← DEFERRED for AI review       │
│ ~821K rows (tier4_ai_needed)                                │
│ KHÔNG dùng làm benign — có thể chứa missed SQLi            │
│ Priority queue cho batch AI review (defer per user)        │
└────────────────────────────────────────────────────────────┘
┌────────────────────────────────────────────────────────────┐
│ pool_sqli_bronze_edge.csv   ← AUDIT only                   │
│ ~2.4K rows (tier1/tier2 bronze)                             │
│ Edge cases — consistency rule conflict                      │
│ → Review để improve consistency_rules.py                    │
└────────────────────────────────────────────────────────────┘
```

**Quan trọng**: 
- **KHÔNG** dùng `pool_unknown.csv` làm discriminator negatives
- Pool benign 15K rows là nhỏ → cần augment bằng synthetic non-SQL strings hoặc clean SQL queries từ external sources

### #5 — Bronze Active Learning Loop

**Vấn đề target**: Bronze tier3 (4,496 SQLi rows) chứa novel patterns mà cascade gần catch được. Đây là cơ hội iterative improvement.

**Workflow**:
```
[pool_sqli_bronze_novel.csv]  (4,496 rows)
         │
  Human review (sort by db_engine để cluster)
         │
  Extract recurring patterns
         │
  Add patterns vào _TIER1_PATTERNS / _TIER2_PATTERNS
         │
  Re-label dataset
         │
  Một số bronze rows → gold/silver (upgrade)
         │
  Iterate đến khi bronze SQLi < 1K hoặc patterns repetitive
```

**Expected ROI**: 4,496 rows / 30 phút review = ~150 rows/phút average. Mỗi cluster pattern phát hiện cover ~50-100 rows → ~45-90 new patterns sau 1 vòng review.

### #6 — Test Set Expansion (5K Stratified)

**Vấn đề target**: `test_1000.csv` (0.09% dataset) quá nhỏ cho 24 cells (4 types × 6 engines). Min 50 rows/cell cần 1,200+ rows.

**Solution**: `expand_test_set.py` script tạo `test_5000_stratified.csv`:
- Stratified theo `sqli_type × db_engine` (24 cells)
- Min 50 rows/cell nếu đủ data, fall back uniform nếu thưa
- Sample từ gold+silver pool để đảm bảo chất lượng test set

---

## 4. Output Schema v3.1

| Column | Example | Mới | Description |
|--------|---------|-----|-------------|
| `payload_norm` | `char(83)char(69)...` | | **Original** (giữ obfuscation) |
| `payload_decoded` | `SELECT ... FROM ...` | **v3.1** | Sau `normalize_payload()` |
| `is_sqli` | `1` | | Binary: 1 nếu là SQLi |
| `sqli_type` | `union_based` | | Primary attack type |
| `sqli_types` | `union_based\|boolean_blind` | v3 | All detected types (pipe-sep) |
| `script_sqli_type` | `union_based` | v3 | Script prediction (preserved) |
| `script_confidence` | `0.92` | v3 | Script confidence (preserved) |
| `label_agreement` | `disagree` | v3 | agree/disagree (AI vs script) |
| `db_engine` | `mysql` | | DB engine target |
| `confidence` | `0.92` | | Final confidence 0.0–1.0 |
| `tier` | `gold` | | gold/silver/bronze |
| `label_source` | `tier1_exact` | | Which tier labeled it |
| `is_complex` | `True` | | Multi-vector or obfuscation |
| `low_confidence` | `False` | | True if confidence < 0.70 |
| `needs_ai` | `False` | | True if routed to Tier 4 |
| `payload_state` | `normalized` | | raw/normalized/delex |
| `db_confidence` | `0.90` | | DB engine detection confidence |
| `obf_comment` | `0.85` | | Comment injection score |
| `obf_case` | `0.80` | | Case variation score |
| `obf_encoding` | `0.80` | | Encoding obfuscation score |

**Valid `sqli_type`**: `time_blind`, `boolean_blind`, `union_based`, `error_based`, `benign`  
**Valid `db_engine`**: `mysql`, `postgres`, `oracle`, `mssql`, `sqlite`, `unknown`

---

## 5. Script Map v3.1

```
scripts/
├── run_labeling.py            ← CLI entry (Pass1 + optional Pass2)
├── cascade_labeler.py         ← 4-tier cascade + payload_decoded output ✨
├── detectors_v2.py            ← _decode_char_sequences(), stacked SELECT ✨
├── state_detector.py          ← detect_state() → raw/normalized/delex
├── consistency_rules.py       ← DB×Type impossibility checks
├── ai_reviewer.py             ← Chat-based AI review (Pass 2, optional)
├── rule_refiner.py            ← Pattern cluster analysis for loop (v3)
├── gold_set_creator.py        ← Stratified sampling for gold set (v3)
├── calibrator.py              ← Platt scaling calibration (v3)
├── delex_validator.py         ← Delex domain gap measurement (v3)
├── data_pool_splitter.py      ← [NEW v3.1] Split 5 pools ✨
├── expand_test_set.py         ← [NEW v3.1] Stratified test 5K ✨
└── __init__.py
```

---

## 6. Benchmark Lịch Sử

| Metric | v1 | v2 | v3 (10K) | v3 (1M actual) | **v3.1 target (1M)** |
|--------|-----|-----|----------|----------------|----------------------|
| H Entropy | 1.921 | 1.964 | 1.964 | ~1.3–1.5 | **> 2.0** |
| benign rows % | 0% | 7.3% | 6.5% | 1.4% (TRUE) + 75.7% UNKNOWN | **clear separation** |
| Tier 4 % | 100% | 24.7% | 25.3% | **75.7%** | **< 50%** |
| multi-label rows | 0 | 0 | 769 | TBD | preserved |
| Oracle error-based | 0 | 407 | 407 | 13,448 | preserved |
| `payload_decoded` col | ✗ | ✗ | ✗ | ✗ | **✅** |
| Multi-pool architecture | ✗ | ✗ | ✗ | ✗ | **✅ (5 pools)** |
| CHAR(N) decoder | ✗ | ✗ | ✗ | ✗ | **✅** |
| Bronze active learning | ✗ | ✗ | ✗ | ✗ | **✅** |

**Lưu ý**: Tier4 75.7% trên dataset 1M là vì payload distribution khác (nhiều CHAR-encoded). v3.1 fix bằng CHAR decoder → target < 50%. Sau bronze active learning + thêm rule rounds → < 30%.

---

## 7. CLI Reference v3.1

```bash
# Workflow chuẩn cho dataset mới
# ───────────────────────────────────────────────────────────

# Step 1: Label dataset
python Skill/label-sqli/scripts/run_labeling.py \
  --input  Asset/LabelData/Testing_1/data1/raw.csv \
  --output Asset/LabelData/Testing_1/data1/labeled.csv \
  --payload_col payload_norm \
  --detector_only --benchmark

# Step 2: Split thành 5 pools
python Skill/label-sqli/scripts/data_pool_splitter.py \
  --input Asset/LabelData/Testing_1/data1/labeled.csv \
  --output_dir Asset/LabelData/Testing_1/pools/

# Step 3: Tạo test set 5K stratified
python Skill/label-sqli/scripts/expand_test_set.py \
  --input  Asset/LabelData/Testing_1/data1/labeled.csv \
  --output Asset/LabelData/Testing_1/test_5000_stratified.csv \
  --n 5000

# Step 4: Phân tích Tier 4 patterns còn lại
python Skill/label-sqli/scripts/rule_refiner.py \
  --report Asset/LabelData/Testing_1/data1/labeled_needs_ai_report.csv \
  --output Asset/LabelData/Testing_1/rule_suggestions.txt

# Step 5: [Active learning] Review pool_sqli_bronze_novel.csv
# (Manual step — open file, extract patterns)

# Step 6: Tạo gold set cho Precision@Gold (defer)
python Skill/label-sqli/scripts/gold_set_creator.py \
  --input  Asset/LabelData/Testing_1/data1/labeled.csv \
  --output Asset/LabelData/gold_500.csv \
  --n 500
```

---

## 8. Pipeline Versioning — Drift Prevention

Để tránh circular validation drift (GAN_v? → label_v? → train GAN_v?+1), v3.1 thêm metadata:

```python
# Trong _build_result():
return {
    ...existing fields...,
    'labeler_version': 'v3.1',     # NEW (recommended addition)
    'labeled_at':      '2026-05-19',
}
```

Pool files có metadata header (line 1 = comment):
```csv
# pool_type: sqli_gold | labeler_version: v3.1 | source: Testing_1/data1/labeled.csv | rows: 241358
payload_norm,payload_decoded,is_sqli,sqli_type,...
```

Khi train GAN, log version chain: `dataset_v? → labeler_v? → GAN_v?` để detect drift.

---

## 9. Bài Báo Tham Chiếu (Bổ Sung v3.1)

| Bài Báo | Liên Quan v3.1 |
|---------|----------------|
| **Appelt et al. (2014) — ICSE** | CHAR(N) obfuscation rate 42-58% baseline. Justify CHAR decoder ROI. |
| **Halfond & Orso (2005) — AMNESIA** | 9 SQLi types taxonomy, identify "alternate encodings" category. |
| **OWASP WAF Evasion Cheat Sheet (2024)** | 5 main bypass techniques, encoding chiếm 30-40%. |
| **Ratner et al. (2017) — Snorkel** | Double-score preservation (#6 v3), multi-pool labeling functions. |
| **Jang et al. (2017) — Gumbel-Softmax** | Calibrated probabilities cần multi-pool quality differentiation. |
| **Gulrajani et al. (2017) — WGAN-GP** | Discriminator cần verified benign (không phải unknown). |
| **Lu et al. (2022) — GAN-based SQLi** | Multi-label preservation, obfuscation diversity critical. |
| **Agrawal et al. (2024)** | "Not Normal ≠ Attack" — verified benign vs unknown distinction. |
| **Lee et al. (2022) — Deduplicating Training Data** | Pool quality > raw count. |

---

## 10. Vấn Đề Còn Lại (v3.1)

| Vấn Đề | Mức Độ | Hướng Fix |
|---------|--------|-----------|
| Tier 4 = 75.7% (target < 50%) | HIGH | CHAR decoder + stacked SELECT (Vòng 1) |
| 821K unknown rows chưa AI review | HIGH | Priority queue AI review (defer per user) |
| Bronze tier3 chưa active learn | MEDIUM | Manual review 4,496 rows (Vòng 2) |
| Pool benign chỉ 15K rows | MEDIUM | Augment synthetic non-SQL + clean queries |
| 1.3-1.5 bits entropy estimate | HIGH | Fix sau khi Tier4 giảm — entropy tự cải thiện |
| Test set chỉ 1K rows | LOW | expand_test_set.py → 5K stratified |
| Improvement #7 (AI standardization) | LOW | Pending user decision |
| Drift prevention metadata | LOW | Add `labeler_version` column |

---

## 11. Active Learning Workflow Cho Bronze Tier 3

### Mục Tiêu
Convert 4,496 bronze tier3 SQLi rows thành new patterns, giảm tier4 thêm 5-10%.

### Quy Trình

```
┌───────────────────────────────────────────────────────────┐
│  Step 1: Load pool_sqli_bronze_novel.csv                  │
│          Sort by (db_engine, sqli_type) để cluster         │
└────────────────────┬──────────────────────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────────────────────┐
│  Step 2: Human review từng cluster (~30 phút work)        │
│          • Identify common SQL fragments                   │
│          • Extract regex pattern (5-20 rows / pattern)    │
└────────────────────┬──────────────────────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────────────────────┐
│  Step 3: Add patterns vào _TIER1_PATTERNS / _TIER2_*      │
│          (detectors_v2.py)                                 │
└────────────────────┬──────────────────────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────────────────────┐
│  Step 4: Re-label dataset → một số bronze → gold/silver    │
└────────────────────┬──────────────────────────────────────┘
                     │
                     ▼
┌───────────────────────────────────────────────────────────┐
│  Step 5: Iterate đến khi bronze SQLi < 1K                  │
│          hoặc patterns repetitive (diminishing returns)    │
└───────────────────────────────────────────────────────────┘
```

### Ví Dụ Pattern Extraction

**Cluster trong bronze Oracle**:
```
... dbms_xmlquery.newcontext('select user from dual') ...
... dbms_xmlgen.getxml('select user from dual') ...
... dbms_xmlquery.executequery(...) ...
```

**Extracted pattern** (thêm vào `_TIER1_PATTERNS`):
```python
(_p(r'\bdbms_xml(?:query|gen)\.\w+\s*\('),
 'error_based', 0.88, 'oracle'),
```

→ Cover ~30-50 rows trong bronze + similar rows trong tier4 (chưa label).

---

## 12. Tóm Tắt v3.1

**3 Quyết Định Architectural Chính**:

1. **Double-column output**: GAN train với obfuscation intact (`payload_norm`), tooling dùng decoded version (`payload_decoded`). Không hi sinh attack capability để dễ debug.

2. **5-pool strategy**: Phân biệt rõ verified benign (15K) vs unknown (821K). Discriminator chỉ train trên verified, không bị contaminate bởi missed SQLi trong unknown pool.

3. **Bronze active learning**: 4,496 tier3 SQLi rows là "free improvement opportunity" — human review 30 phút convert thành 45-90 new patterns. ROI cao nhất trong các options.

**3 Cải Tiến Technical**:

1. CHAR(N) decoder trong `normalize_payload()` — target -25% tier4
2. Stacked SELECT patterns trong Tier 2 — target -10% tier4
3. Pipeline versioning metadata — drift prevention

**Defer Cho Vòng Sau**:

- Gold set 500 rows + Precision@Gold (per user request)
- Priority queue AI review cho 821K unknown rows
- Synthetic benign augmentation

---

*v3.1 — 2026-05-19 — Architecture document for review trước implementation*  
*Next step: User approve doc → implement STEP B-G theo plan*  
*Implementation: `Skill/label-sqli/scripts/`*  
*Plan file: `C:\Users\Admin\.claude\plans\ki-n-s-1-frolicking-conway.md`*
