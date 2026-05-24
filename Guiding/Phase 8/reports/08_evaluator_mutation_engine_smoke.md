# 08 - Evaluator Contract Report

Scope: separated validity, novelty, conditioning-debug, and evasion axes. Raw payloads are intentionally omitted.

## Inputs

- Samples: `Guiding\Phase 8\outputs\surgery_baselines_smoke\mutation_engine_samples.jsonl`
- Reference: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 5\outputs\full\gold.parquet`
- Reference templates loaded: `77,804`
- Samples evaluated: `120`

## Axis Summary

| Axis | Metric | Value | Notes |
|---|---|---:|---|
| Validity | Balanced delimiter rate | 0.2917 | structural sanity, not ground truth |
| Validity | sqlglot parse rate | 0.0000 | applicable=0 |
| Novelty | Novel vs train template rate | 0.6833 | normalized delex-template hash |
| Novelty | Batch template duplicate rate | 0.0583 | generated-sample self duplication |
| Conditioning | Technique hint rate | 0.8824 | debug only |
| Evasion | Detector bypass rate | 0.0000 | status=missing_detector_results |

## By Technique

| Technique | Samples | Balanced Delimiters | Train Template Dup | Technique Hint |
|---|---:|---:|---:|---:|
| benign | 1 | 1.0000 | 1.0000 | n/a |
| boolean_blind | 18 | 0.3333 | 0.2222 | 0.9444 |
| error_based | 11 | 0.2727 | 0.5455 | 0.6364 |
| time_blind | 31 | 0.3548 | 0.3871 | 0.7097 |
| union_based | 59 | 0.2373 | 0.2542 | 1.0000 |

## Interpretation Rules

- Evasion is not inferred unless detector results are supplied.
- `sql_signal_rate_debug_only` and technique hints are retained for continuity with Phase 6 but must not be used as checkpoint gates.
- A sample should count toward a main claim only when validity, novelty, and evasion are all measurable.
