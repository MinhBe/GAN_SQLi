# 08 - Evaluator Contract Report

Scope: separated validity, novelty, conditioning-debug, and evasion axes. Raw payloads are intentionally omitted.

## Inputs

- Samples: `Guiding\Phase 8\outputs\paired_surgery_gan_full_lite\paired_surgery_gan_samples.jsonl`
- Reference: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 5\outputs\full\gold.parquet`
- Reference templates loaded: `77,804`
- Samples evaluated: `400`

## Axis Summary

| Axis | Metric | Value | Notes |
|---|---|---:|---|
| Validity | Balanced delimiter rate | 0.2225 | structural sanity, not ground truth |
| Validity | sqlglot parse rate | 0.0000 | applicable=0 |
| Novelty | Novel vs train template rate | 0.1325 | normalized delex-template hash |
| Novelty | Batch template duplicate rate | 0.4275 | generated-sample self duplication |
| Conditioning | Technique hint rate | 0.8346 | debug only |
| Evasion | Detector bypass rate | 0.0000 | status=missing_detector_results |

## By Technique

| Technique | Samples | Balanced Delimiters | Train Template Dup | Technique Hint |
|---|---:|---:|---:|---:|
| benign | 1 | 1.0000 | 1.0000 | n/a |
| boolean_blind | 42 | 0.2143 | 0.8810 | 0.9762 |
| error_based | 52 | 0.3077 | 0.7115 | 0.4231 |
| time_blind | 132 | 0.3182 | 0.8636 | 0.7500 |
| union_based | 173 | 0.1214 | 0.9133 | 0.9884 |

## Interpretation Rules

- Evasion is not inferred unless detector results are supplied.
- `sql_signal_rate_debug_only` and technique hints are retained for continuity with Phase 6 but must not be used as checkpoint gates.
- A sample should count toward a main claim only when validity, novelty, and evasion are all measurable.
