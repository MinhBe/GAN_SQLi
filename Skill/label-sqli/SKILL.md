---
name: label-sqli
description: |
  4-tier cascade labeler cho SQL injection payloads. Dùng khi cần gán nhãn
  sqli_type (time_blind/boolean_blind/union_based/error_based/benign),
  db_engine (mysql/postgres/oracle/mssql/sqlite), confidence, tier, và
  feature vector đầy đủ cho training data của GAN/SeqGAN. Dùng ngay khi
  user hỏi về labeling SQLi, phân loại injection type, phát hiện DB engine
  từ payload syntax, hoặc xây dựng training data — kể cả khi họ không dùng
  từ "label" hay "SQLi" một cách tường minh.
---

# Skill: label-sqli

Multi-dimensional SQL injection payload labeler cho GAN training data. Pipeline chạy hoàn toàn offline (detector-only), không gọi AI trong quá trình labeling chính — AI review được export ra file riêng sau khi hoàn tất.

---

## Architecture

```
payload (string)
      |
 detect_state()          ← raw / normalized / delex
      |
 ┌────▼────────────────────────────────────────────────┐
 │  Tier 1: exact function match  (confidence ≥ 0.85)  │
 │  tier1_score() — SLEEP/BENCHMARK/UNION SELECT/etc.  │
 └────┬────────────────────────────────────────────────┘
      │ fallthrough if < 0.85
 ┌────▼────────────────────────────────────────────────┐
 │  Tier 2: structural patterns + sqlparse              │
 │  tier2_score() — OR 1=1, quote imbalance, etc.      │
 └────┬────────────────────────────────────────────────┘
      │ fallthrough if < 0.70
 ┌────▼────────────────────────────────────────────────┐
 │  Tier 3: contextual inference                        │
 │  engine→type inference, consistency_rules()          │
 └────┬────────────────────────────────────────────────┘
      │ fallthrough if < 0.50
 ┌────▼────────────────────────────────────────────────┐
 │  Benign classifier  (score_benign ≥ 0.60)            │
 └────┬────────────────────────────────────────────────┘
      │ fallthrough
 ┌────▼────────────────────────────────────────────────┐
 │  Tier 4: needs_ai = True  →  export to report       │
 └─────────────────────────────────────────────────────┘
```

---

## Script Map

```
scripts/
├── run_labeling.py        ← CLI entry point (Pass 1 + optional Pass 2)
├── cascade_labeler.py     ← 4-tier cascade engine + _build_result()
├── detectors_v2.py        ← tier1_score(), tier2_score(), detect_db_engine(),
│                             score_benign(), is_complex_payload()
├── state_detector.py      ← detect_state() → raw/normalized/delex
├── consistency_rules.py   ← DB×Type impossibility checks
├── ai_reviewer.py         ← Chat-based AI review (Pass 2, optional)
└── __init__.py
```

---

## CLI Usage

```bash
# ── Detector-only (recommended, no API calls) ──────────────────────────
python Skill/label-sqli/scripts/run_labeling.py \
  --input  Asset/LabelData/raw.csv \
  --output Asset/LabelData/labeled.csv \
  --payload_col payload_norm \
  --detector_only
# Outputs:
#   labeled.csv                   — full labeled dataset
#   labeled_needs_ai_report.csv   — rows flagged for optional AI review

# ── Với AI review cho tier4 rows ──────────────────────────────────────
python Skill/label-sqli/scripts/run_labeling.py \
  --input  Asset/LabelData/raw.csv \
  --output Asset/LabelData/labeled.csv \
  --payload_col payload_norm \
  --ai_cap 5000

# ── Dry run (mock AI, không gọi API) ──────────────────────────────────
python Skill/label-sqli/scripts/run_labeling.py \
  --input raw.csv --output labeled.csv --dry_run

# ── Quick test tích hợp ────────────────────────────────────────────────
python Skill/label-sqli/scripts/cascade_labeler.py
python Skill/label-sqli/scripts/detectors_v2.py
```

---

## Output Schema

| Column | Example | Description |
|--------|---------|-------------|
| `is_sqli` | `1` | Binary: 1 nếu là SQLi (sqli_type != benign/empty) |
| `sqli_type` | `time_blind` | Primary attack type (xem valid values bên dưới) |
| `db_engine` | `mysql` | DB engine target |
| `confidence` | `0.95` | Final confidence 0.0–1.0 |
| `tier` | `gold` | gold ≥0.85 / silver ≥0.70 / bronze <0.70 |
| `label_source` | `tier1_exact` | Tier nào gán nhãn (xem bảng bên dưới) |
| `is_complex` | `True` | 2+ attack types ≥0.40, **hoặc** 1 type + obf ≥0.60 |
| `low_confidence` | `False` | True nếu confidence < 0.70 |
| `needs_ai` | `False` | True nếu route sang Tier 4 |
| `payload_state` | `normalized` | raw / normalized / delex |
| `db_confidence` | `0.90` | Độ tin cậy của db_engine detection |
| `obf_comment` | `0.85` | Comment injection score (/**/, /*!50000...*/) |
| `obf_case` | `0.80` | Case variation score (SeLeCt, UnIoN) |
| `obf_encoding` | `0.80` | Encoding obfuscation score (0x41, char(65), %27) |

**Valid `sqli_type`**: `time_blind`, `boolean_blind`, `union_based`, `error_based`, `benign`

**Valid `db_engine`**: `mysql`, `postgres`, `oracle`, `mssql`, `sqlite`, `unknown`

---

## Tier Assignment

| Tier | Confidence | Ý nghĩa |
|------|-----------|---------|
| Gold | ≥ 0.85 | High-trust, dùng trực tiếp cho GAN training |
| Silver | ≥ 0.70 | Dùng với lower weight |
| Bronze | < 0.70 | Loại khỏi training, giữ lại cho audit |

---

## Label Source Values

| label_source | Nguồn |
|-------------|-------|
| `tier1_exact` | Exact function match (SLEEP, UNION SELECT, extractvalue…) |
| `tier2_structural` | Structural pattern (OR 1=1, quote imbalance, ORDER BY…) |
| `tier3_contextual` | Engine→type inference + consistency rules |
| `benign_classifier` | score_benign() ≥ 0.60 |
| `tier4_ai_needed` | Không đủ signal, cần AI review |
| `tier4_ai` | AI reviewer đã gán nhãn (Pass 2) |

---

## Key Detectors (detectors_v2.py)

| Function | Returns | Mô tả |
|----------|---------|-------|
| `tier1_score(payload)` | dict | Score time/bool/union/error với exact patterns |
| `tier2_score(payload)` | dict | Score với structural + heuristic patterns |
| `detect_db_engine(payload)` | (str, float) | Engine + confidence |
| `score_benign(payload)` | float | Benign likelihood |
| `is_complex_payload(t1, t2)` | bool | Dùng trong _build_result() nội bộ |
| `detect_comment_injection(p)` | float | /**/, /*!N...*/ WAF bypass |
| `detect_case_variation(p)` | float | SeLeCt, UnIoN |
| `detect_encoding_obfuscation(p)` | float | 0x, char(), %27 |

---

## Oracle Error-Based Notes

Oracle error-based injection dùng `utl_inaddr.get_host_address()` (không phải `get_host_name`). Pattern hiện tại match cả hai: `utl_inaddr\.get_host_\w+\(`. Các variants được nhận diện:
- `utl_inaddr.get_host_address(...)` → `error_based`, `oracle`, confidence 0.95
- `utl_inaddr.get_host_name(...)` → như trên
- `xmltype(...)` → `error_based`, `oracle`, confidence 0.95
- `ctxsys.drithsx.sn(...)` → `error_based`, `oracle`, confidence 0.88

---

## is_complex Logic

`is_complex = True` khi:
1. **Multi-vector**: 2+ attack types score ≥ 0.40 (e.g. time_blind + boolean_blind)
2. **Obfuscation-augmented**: 1 attack type ≥ 0.40 **và** max(obf_comment, obf_case, obf_encoding) ≥ 0.60

---

## Pre-flight Checklist

Trước khi chạy trên dataset lớn:

- [ ] Smoke test: `python run_labeling.py --input smoke5.csv --detector_only`
- [ ] Kiểm tra output có cột: `is_sqli`, `sqli_type`, `db_engine`, `confidence`, `tier`
- [ ] Type entropy > 2.0 bits (không bị dominated bởi 1 type)
- [ ] Xem `_needs_ai_report.csv` — tỷ lệ `needs_ai` < 30% là ổn
- [ ] Chỉ set `ANTHROPIC_API_KEY` nếu muốn chạy Pass 2 (AI review)

---

*Skill version: 2.0 — 2026-05-19*
