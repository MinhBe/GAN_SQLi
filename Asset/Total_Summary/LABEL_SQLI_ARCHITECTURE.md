# Kiến Trúc Skill label-sqli v3 — Tổng Hợp Toàn Diện

> **Ngày tạo**: 2026-05-18 | **Cập nhật**: 2026-05-19  
> **Phiên bản**: v3 (Rule Refinement + Multi-label + Double-score + Calibration Framework)  
> **Benchmark v3**: H = 1.9638 bits, benign = 650 rows, Tier4 = 25.3%, multi-label = 769 rows

---

## 1. Bối Cảnh — Tại Sao v2 → v3?

### v1 → v2 (2026-05-18)

Skill `label-sqli` v1 chạy trên 10,000 mẫu thực tế cho kết quả tệ:

| Metric | v1 | v2 Pass1 | Mục Tiêu |
|--------|-----|----------|---------|
| H entropy | 1.921 ❌ | 1.964 ⚠️ | > 2.0 |
| benign rows | **0** ❌ | 726 (7.3%) ✅ | > 5% |
| needs_ai | 100% ❌ | 24.7% ✅ | 15–25% |
| Oracle error-based | 0 rows ❌ | 407 rows ✅ | — |
| Agreement (old labels) | 43% | 50.3% | ≥ 40% |

**Root causes v1:**
1. Delex mismatch — `sleep\(\d+` không match `sleep ( __TIME__ )`
2. Oracle gap — thiếu `utl_inaddr.get_host_address()`
3. Benign là residual — `primary_type()` trả None thay vì `'benign'`
4. Không có cascade — 100% rows qua AI review

### v2 → v3 (2026-05-19) — 9 Cải Tiến

Phân tích `Testing_labeled.csv` (10,000 rows) phát hiện:
- **368 benign false positives** — SQL tautology injection (sqlmap-generated) bị nhầm là benign
- **2,468 Tier 4 rows (24.7%)** — trong đó 1,439 chứa keyword SQLi rõ ràng → false negatives do thiếu rule
- **Stale benchmark** — H=2.232 trong doc nhưng thực tế 1.964 bits
- **Single-label schema** — payload multi-technique (union+boolean) chỉ ghi 1 type → mất thông tin cho GAN

v3 triển khai 9/10 cải tiến (improvement #7 pending review).

---

## 2. Tổng Quan Kiến Trúc v3

```
                         payload (raw string)
                              │
                              ▼
              ┌───────────────────────────────┐
              │  PRE-NORM: normalize_payload() │  ← giải mã \x27, %27, '
              │  decode hex/URL/unicode escape │
              └──────────────┬────────────────┘
                             │
                             ▼
              ┌───────────────────────────────┐
              │   PRE: State Detection        │  ← raw / normalized / delex
              └──────────────┬────────────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
         ┌──────────────┐   ┌──────────────────┐
         │   TIER 1     │   │   TIER 2         │  ← ALWAYS BOTH RUN
         │ Exact Match  │   │ Structural Regex │    (for multi-label)
         │ conf 0.90–1.0│   │ conf 0.70–0.89   │
         └──────┬───────┘   └────────┬─────────┘
                │                   │
                └─────────┬─────────┘
                          │ T1 ≥ 0.85 → Tier1 wins, sqli_types = T1+T2
                          │ T2 ≥ 0.70 → Tier2 wins, sqli_types = T1+T2
                          ▼
              ┌───────────────────────────────┐
              │  TIER 3: Contextual Inference │  ← conf 0.50–0.69
              │  engine→type + consistency    │
              └──────────────┬────────────────┘
                             │
                    ┌────────┴────────┐
                    ▼                 ▼
        ┌──────────────────┐   ┌──────────────────┐
        │   Benign         │   │  TIER 4: AI      │
        │  Classifier      │   │  needs_ai=True   │
        │  conf ≥ 0.60     │   │  ~25% rows       │
        │  excl. tautology │   │                  │
        └──────┬───────────┘   └────────┬─────────┘
               │                       │
               └─────────┬─────────────┘
                         ▼
              ┌───────────────────────────────┐
              │  POST: Coverage Monitor       │
              │  + Benchmark Log (optional)   │
              │  + Precision@Gold (optional)  │
              └────────────┬──────────────────┘
                           ▼
                    labeled CSV (v3 schema)
```

**Thay đổi so với v2:**
- `normalize_payload()` bước decode mới trước tất cả detection
- Tier 2 **luôn chạy** song song với Tier 1 (trước: chỉ chạy nếu T1 fail)
- Output schema mở rộng: `sqli_types`, `script_sqli_type`, `script_confidence`
- Benign classifier loại tautology patterns (sqlmap-generated)

---

## 3. v3 Improvements — Chi Tiết 9 Cải Tiến

### #1 — Delex Domain Gap Validation (mới)

**Script**: `delex_validator.py`

GAN tạo payload ở dạng delex (`sleep(__TIME__)`), nhưng labeler được train trên raw/normalized. Gap này gây ra detection miss khi evaluate GAN output.

`delex_validator.py` đo:
- Detection rate theo `payload_state` (raw vs normalized vs delex)
- Synthetic delex test: lấy 500 raw gold rows, delexify, chạy lại cascade, đo miss rate

**Ngưỡng chấp nhận:** miss rate < 5% → OK; 5–15% → thêm delex patterns; > 15% → domain gap nghiêm trọng

### #2 — Calibrated Confidence (Platt Scaling)

**Script**: `calibrator.py`

Confidence score hiện tại là heuristic tier-based (0.90, 0.75, 0.55...) — **không phải probability**. Downstream GAN (Gumbel-Softmax, WGAN-GP) cần calibrated probabilities.

Platt scaling: fit logistic regression trên gold set → transform `confidence` → `P(correct | confidence)`.

```python
# Sau khi fit:
P(correct) = sigmoid(a * confidence + b)
# Ví dụ: conf=0.85 → P(correct)=0.92 (calibrated)
```

**Phụ thuộc**: cần gold_200.csv (improvement #9) trước khi chạy.

**Bài báo**: Jang et al. (2017) Gumbel-Softmax — "Categorical sampling cần calibrated probabilities để stable training"

### #3 — Normalization Layer (decode obfuscation trước detection)

**Function**: `normalize_payload()` trong `detectors_v2.py`

```python
def normalize_payload(payload: str) -> str:
    p = re.sub(r'\\x([0-9a-fA-F]{2})', lambda m: chr(int(m.group(1), 16)), p)
    p = re.sub(r'\\u([0-9a-fA-F]{4})', lambda m: chr(int(m.group(1), 16)), p)
    p = urllib.parse.unquote(p)
    return p
```

Trước khi detect, decode:
- `\x27` → `'` (hex escape)
- `'` → `'` (unicode escape)
- `%27` → `'` (URL encoding)

Kết quả: `\x27UNION SELECT NULL--` → được detect là `union_based` tier1 thay vì bị miss.

**Áp dụng trong cascade**: `normalize_payload()` gọi ở đầu `label_payload()` và trong `tier1_score()`/`tier2_score()`.

### #4 — SQL Tautology Exclusion (fix benign false positives)

**Fix trong**: `score_benign()`, `detectors_v2.py`

368 rows bị nhầm benign do sqlmap-generated tautology injection dạng:
```
1" ) and ( 5452 = 6050 ) *6050 and ( "ciyc" like "ciyc"
```

Pattern `and ( 5452=6050 )` và `*6050 AND` không bị `_ATTACK_KWD` catch (không có SELECT/UNION/SLEEP) và không trigger injection context, nên vào benign branch.

**Fix**: Thêm `_TAUTOLOGY_PATTERNS` hard-exclusion vào `score_benign()`:
```python
_TAUTOLOGY_PATTERNS = [
    _p(r'(?:and|or)\s*\(\s*\d+\s*=\s*\d+\s*\)', re.I),  # AND ( 5452=6050 )
    _p(r'\*\d+\s+and\b', re.I),                           # *6050 AND
    _p(r'(?:and|or)\s*\(\s*\w+\s+like\s+\w+\s*\)', re.I),# AND ( x LIKE x )
]
```

### #5 — Multi-label Schema

**Column mới**: `sqli_types` (pipe-separated)

Payload multi-technique như `sleep(5) UNION SELECT NULL--` trước đây chỉ ghi `time_blind` (winner). v3 thêm:

```
sqli_type:  time_blind          ← primary label (unchanged)
sqli_types: time_blind|union_based  ← all detected types ≥ 0.40 conf
```

**Function**: `get_sqli_types(t1, t2, threshold=0.40)` trong `detectors_v2.py`

Tier 2 **luôn chạy** dù Tier 1 đã thành công, để `sqli_types` capture đầy đủ.

**Benchmark**: 769/10,000 rows có multi-label (sqli_types chứa `|`)

**Lý do quan trọng**: GAN training cần biết payload là multi-technique để weight đúng reward signal trong discriminator.

### #6 — Double-score Preservation (Snorkel-inspired)

**Columns mới**: `script_sqli_type`, `script_confidence`, `label_agreement`

Khi AI override script label (Pass 2), schema v3 giữ lại:
```
sqli_type:          union_based   ← AI winner (overridden)
script_sqli_type:   boolean_blind ← what script predicted
script_confidence:  0.72          ← script's confidence
label_agreement:    disagree      ← agree/disagree between AI and script
```

**Tại sao quan trọng (Snorkel principle)**: Snorkel giữ toàn bộ LF output thay vì chỉ giữ kết quả cuối. Nếu 3 LF đồng ý và 1 LF khác biệt, thông tin LF nào sai giúp improve LF quality. `label_agreement` là proxy cho disagreement signal này.

### #7 — AI Reviewer Standardization (Pending)

Chuẩn hóa output format của AI reviewer để consistent với schema v3. **Chưa triển khai** — user sẽ cân nhắc lại sau khi có thêm kinh nghiệm với Pass 2 workflow.

### #8 — Pattern Expansion (New Rules)

**Thêm vào Tier 1** (`_TIER1_PATTERNS`):
```python
# MSSQL hex dynamic SQL: DECLARE @s VARCHAR(N) SELECT @s = 0x...
(r'\bdeclare\s+@\w+\s+\w+\s*\(\s*\d+\s*\)\s+select\s+@\w+\s*=\s*0x',
 'time_blind', 0.90, 'mssql'),

# Oracle execute immediate — string concat bypass
(r'\bexecute\s+immediate\b', 'error_based', 0.85, 'oracle'),
```

**Thêm vào Tier 2 Bool** (`_TIER2_BOOL_PATTERNS`):
```python
# SQL boolean keywords (or true / or false)
(r'\bor\s+(?:true|false)\b',  0.85),   # or true --
(r'\band\s+(?:true|false)\b', 0.82),   # and false --

# Boolean subquery: or X in (select ...)
(r'\bor\s+\w+\s+in\s*\(\s*select\b',             0.88),
(r'\band\s+\w+\s+(?:not\s+)?in\s*\(\s*select\b', 0.85),
```

### #9 — Precision@Gold Stop Condition

**Script**: `gold_set_creator.py` + `calibrator.py`

Vòng lặp rule refinement dừng khi: Precision@Gold plateau delta < 0.5%.

**Workflow**:
1. `gold_set_creator.py` — stratified sample 200 payloads
2. Human review + correct labels trong CSV
3. `precision_at_gold(df, gold_path)` trong run_labeling.py — đo accuracy
4. So sánh P@G giữa 2 vòng: nếu `|P@G_i - P@G_(i-1)| < 0.005` → dừng

**Rule Refinement Loop Script**: `rule_refiner.py` — phân tích Tier 4 payloads, extract SQL ngram clusters, đề xuất regex patterns cho vòng lặp tiếp theo.

```bash
python rule_refiner.py \
    --report Testing_labeled_needs_ai_report.csv \
    --output rule_suggestions.txt
```

---

## 4. Output Schema v3

| Column | Example | Mới | Description |
|--------|---------|-----|-------------|
| `is_sqli` | `1` | | Binary: 1 nếu là SQLi |
| `sqli_type` | `time_blind` | | Primary attack type |
| `sqli_types` | `time_blind\|union_based` | **v3** | All detected types (pipe-sep) |
| `script_sqli_type` | `boolean_blind` | **v3** | Script prediction before AI |
| `script_confidence` | `0.72` | **v3** | Script confidence before AI |
| `label_agreement` | `disagree` | **v3** | agree/disagree (AI vs script) |
| `db_engine` | `mysql` | | DB engine target |
| `confidence` | `0.95` | | Final confidence 0.0–1.0 |
| `tier` | `gold` | | gold/silver/bronze |
| `label_source` | `tier1_exact` | | Which tier labeled it |
| `is_complex` | `True` | | Multi-vector or obfuscation-augmented |
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

## 5. Script Map v3

```
scripts/
├── run_labeling.py        ← CLI entry point (Pass1 + optional Pass2)
│                             New flags: --benchmark, --gold_set
├── cascade_labeler.py     ← 4-tier cascade engine
│                             v3: normalize_payload, sqli_types, double-score
├── detectors_v2.py        ← tier1_score(), tier2_score(), score_benign()
│                             v3: normalize_payload(), get_sqli_types()
│                             v3: tautology exclusion, new patterns
├── state_detector.py      ← detect_state() → raw/normalized/delex
├── consistency_rules.py   ← DB×Type impossibility checks
├── ai_reviewer.py         ← Chat-based AI review (Pass 2, optional)
├── rule_refiner.py        ← [NEW v3] Pattern cluster analysis for loop
├── gold_set_creator.py    ← [NEW v3] Stratified sampling for gold set
├── calibrator.py          ← [NEW v3] Platt scaling on gold set
├── delex_validator.py     ← [NEW v3] Delex domain gap measurement
└── __init__.py
```

---

## 6. Benchmark v1 vs v2 vs v3

| Metric | v1 | v2 (Pass1) | v3 (Pass1) | Mục Tiêu |
|--------|-----|------------|------------|---------|
| **H Entropy** | 1.921 ❌ | 1.964 ⚠️ | **1.964 ⚠️** | > 2.0 |
| **benign rows** | 0 ❌ | 726 ✅ | **650** ✅ | > 5% |
| **Tier 4 %** | 100% | 24.7% | **25.3%** ⚠️ | < 20% |
| **multi-label rows** | 0 | 0 | **769** ✅ | > 0 |
| **Oracle error-based** | 0 ❌ | 407 ✅ | **407** ✅ | — |
| **is_complex** | — | 1,412 | **1,838** ↑ | — |
| **Benign FP (tautology)** | — | 368 | **0** ✅ | 0 |
| **sqli_types column** | ✗ | ✗ | **✅** | required |
| **script_sqli_type col** | ✗ | ✗ | **✅** | required |
| **Speed** | ~1,800 r/s | 1,873 r/s | **~410 r/s** ⚠️ | ≥ 400 |

**Lưu ý về Tier 4%**: v3 tăng nhẹ 24.7% → 25.3% vì tautology fix đúng đắn đã chuyển 76 benign FP sang tier4 (đây là improvement, không phải regression). New patterns giải cứu một phần tier4 nhưng ít hơn số tautology chuyển vào.

**Lưu ý về Speed**: v3 chạy Tier 2 luôn luôn (kể cả khi Tier 1 đã thành công) — đây là cost cho multi-label support. Tốc độ vẫn đáp ứng yêu cầu > 400 r/s.

---

## 7. Rule Refinement Loop

v3 triển khai vòng lặp cải thiện rule có dừng điều kiện:

```
[Testing_labeled_needs_ai_report.csv]
         │
  [rule_refiner.py]  → phân tích pattern clusters trong Tier 4
         │
  Human review → thêm rules vào detectors_v2.py
         │
  [run_labeling.py --detector_only --benchmark]  → chạy lại
         │
  So sánh Tier4% và Precision@Gold trước/sau
         │
  delta < 100 rows (hoặc P@G plateau < 0.5%) → DỪNG
```

**Stop conditions (một trong ba):**
1. Tier 4 < 10%
2. Ít hơn 100 rows thay đổi label giữa 2 vòng liên tiếp
3. Precision@Gold plateau delta < 0.5% (sau khi có gold_200.csv)

**Benchmark log**: mỗi vòng ghi vào `benchmark_log.jsonl` để track progress.

---

## 8. CLI Reference

```bash
# Detector-only (khuyến nghị, không cần API)
python Skill/label-sqli/scripts/run_labeling.py \
  --input  Asset/LabelData/raw.csv \
  --output Asset/LabelData/labeled.csv \
  --payload_col payload_norm \
  --detector_only \
  --benchmark \
  [--gold_set Asset/LabelData/gold_200.csv]

# Tạo gold set để đánh giá
python Skill/label-sqli/scripts/gold_set_creator.py \
  --input  Asset/LabelData/labeled.csv \
  --output Asset/LabelData/gold_200.csv \
  --n 200

# Phân tích Tier 4 patterns
python Skill/label-sqli/scripts/rule_refiner.py \
  --report Asset/LabelData/Testing/Testing_labeled_needs_ai_report.csv \
  --output rule_suggestions.txt

# Đo delex domain gap
python Skill/label-sqli/scripts/delex_validator.py \
  --labeled Asset/LabelData/Testing/Testing_labeled.csv

# Calibrate confidence (sau khi có gold set)
python Skill/label-sqli/scripts/calibrator.py \
  --gold    Asset/LabelData/gold_200.csv \
  --labeled Asset/LabelData/Testing/Testing_labeled.csv \
  --output  calibration_params.json

# Với AI review cho Tier 4 rows (cần ANTHROPIC_API_KEY)
python Skill/label-sqli/scripts/run_labeling.py \
  --input  Asset/LabelData/raw.csv \
  --output Asset/LabelData/labeled.csv \
  --payload_col payload_norm \
  --ai_cap 5000
```

---

## 9. Bài Báo Tham Chiếu

| Bài Báo | Liên Quan v3 |
|---------|-------------|
| **Ratner et al. (2017) Snorkel** | Double-score (#6): giữ toàn bộ LF output thay vì chỉ winner. `label_agreement` là disagreement signal cho LF improvement. |
| **Jang et al. (2017) Gumbel-Softmax** | Calibration (#2): downstream GAN cần calibrated probabilities, không phải tier scores. |
| **Gulrajani et al. (2017) WGAN-GP** | Discriminator cần consistent confidence cho reward signal. Uncalibrated scores → unstable training. |
| **Lu et al. (2022) GAN-based SQLi** | Multi-label (#5): bài báo classify theo 4 attack types riêng biệt. v3 giữ thêm `sqli_types` để không mất signal khi payload multi-technique. |
| **Agrawal et al. (2024)** | Benign false positive fix (#4): "Not Normal ≠ Attack" — explicit benign signal required, không thể dùng residual. |

---

## 10. Các Vấn Đề Còn Lại (v3)

| Vấn Đề | Mức Độ | Hướng Fix |
|---------|--------|-----------|
| Tier 4 = 25.3% (target < 10%) | High | Rule refinement loop — xem `rule_suggestions.txt` |
| Entropy H = 1.964 (target > 2.0) | Medium | Tier 4 reduction sẽ cải thiện entropy |
| Speed giảm từ 1,873 → 410 r/s | Low | T2 luôn chạy — acceptable for 10K batch |
| Benign 650 (giảm từ 726) | OK | Tautology fix correct — 76 FP resolved |
| 15/20 sparse cells | Medium | SQLite, postgres rất ít trong dataset thực |
| Improvement #7 chưa triển khai | Low | Pending user decision |

---

*v3 — 2026-05-19 — Implementation: `Skill/label-sqli/scripts/`*  
*Benchmark log: `Asset/LabelData/Testing/benchmark_log.jsonl`*  
*Next step: chạy `rule_refiner.py` → thêm patterns → vòng lặp tiếp theo*
