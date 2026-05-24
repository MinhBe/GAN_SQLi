# 08 - Evaluator Contract Report

Scope: separated validity, novelty, conditioning-debug, and evasion axes. Raw payloads are intentionally omitted.

## Inputs

- Samples: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 6\outputs\mle_attack_only_smoke\samples_step_00001000.jsonl`
- Reference: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 5\outputs\full\gold.parquet`
- Reference templates loaded: `77,804`
- Samples evaluated: `120`

## Axis Summary

| Axis | Metric | Value | Notes |
|---|---|---:|---|
| Validity | Balanced delimiter rate | 0.5333 | structural sanity, not ground truth |
| Validity | sqlglot parse rate | 0.0000 | applicable=0 |
| Novelty | Novel vs train template rate | 0.5333 | normalized delex-template hash |
| Novelty | Batch template duplicate rate | 0.0167 | generated-sample self duplication |
| Conditioning | Technique hint rate | 0.6250 | debug only |
| Evasion | Detector bypass rate | 0.0000 | status=missing_detector_results |

## By Technique

| Technique | Samples | Balanced Delimiters | Train Template Dup | Technique Hint |
|---|---:|---:|---:|---:|
| boolean_blind | 30 | 0.7667 | 0.6000 | 0.8333 |
| error_based | 30 | 0.2667 | 0.1333 | 0.0000 |
| time_blind | 30 | 0.5333 | 0.6333 | 0.7333 |
| union_based | 30 | 0.5667 | 0.5000 | 0.9333 |

## Interpretation Rules

- Evasion is not inferred unless detector results are supplied.
- `sql_signal_rate_debug_only` and technique hints are retained for continuity with Phase 6 but must not be used as checkpoint gates.
- A sample should count toward a main claim only when validity, novelty, and evasion are all measurable.
