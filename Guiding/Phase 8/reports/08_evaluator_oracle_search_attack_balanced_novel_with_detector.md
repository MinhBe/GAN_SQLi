# 08 - Evaluator Contract Report

Scope: separated validity, novelty, conditioning-debug, and evasion axes. Raw payloads are intentionally omitted.

## Inputs

- Samples: `Guiding\Phase 8\outputs\oracle_aware_search\attack_balanced_novel_oracle_search.jsonl`
- Reference: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 5\outputs\full\gold.parquet`
- Reference templates loaded: `77,804`
- Samples evaluated: `400`

## Axis Summary

| Axis | Metric | Value | Notes |
|---|---|---:|---|
| Validity | Balanced delimiter rate | 1.0000 | structural sanity, not ground truth |
| Validity | sqlglot parse rate | 0.0000 | applicable=0 |
| Novelty | Novel vs train template rate | 1.0000 | normalized delex-template hash |
| Novelty | Batch template duplicate rate | 0.0000 | generated-sample self duplication |
| Conditioning | Technique hint rate | 0.9950 | debug only |
| Evasion | Detector bypass rate | 0.1525 | status=provided |

## By Technique

| Technique | Samples | Balanced Delimiters | Train Template Dup | Technique Hint |
|---|---:|---:|---:|---:|
| boolean_blind | 9 | 1.0000 | 0.0000 | 1.0000 |
| error_based | 36 | 1.0000 | 0.0000 | 0.9722 |
| time_blind | 100 | 1.0000 | 0.0000 | 0.9900 |
| union_based | 255 | 1.0000 | 0.0000 | 1.0000 |

## Interpretation Rules

- Evasion is not inferred unless detector results are supplied.
- `sql_signal_rate_debug_only` and technique hints are retained for continuity with Phase 6 but must not be used as checkpoint gates.
- A sample should count toward a main claim only when validity, novelty, and evasion are all measurable.
