# 08 - Evaluator Contract Report

Scope: separated validity, novelty, conditioning-debug, and evasion axes. Raw payloads are intentionally omitted.

## Inputs

- Samples: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 6\outputs\gumbel_seqgan_smoke_balanced\samples_step_00001500.jsonl`
- Reference: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 5\outputs\full\gold.parquet`
- Reference templates loaded: `77,804`
- Samples evaluated: `120`

## Axis Summary

| Axis | Metric | Value | Notes |
|---|---|---:|---|
| Validity | Balanced delimiter rate | 0.4583 | structural sanity, not ground truth |
| Validity | sqlglot parse rate | 0.0000 | applicable=0 |
| Novelty | Novel vs train template rate | 0.3333 | normalized delex-template hash |
| Novelty | Batch template duplicate rate | 0.0167 | generated-sample self duplication |
| Conditioning | Technique hint rate | 0.6354 | debug only |
| Evasion | Detector bypass rate | 0.0000 | status=missing_detector_results |

## By Technique

| Technique | Samples | Balanced Delimiters | Train Template Dup | Technique Hint |
|---|---:|---:|---:|---:|
| benign | 24 | 0.2917 | 0.3333 | n/a |
| boolean_blind | 24 | 0.7917 | 0.9167 | 0.7083 |
| error_based | 24 | 0.2083 | 0.3750 | 0.0000 |
| time_blind | 24 | 0.5417 | 0.8333 | 0.8333 |
| union_based | 24 | 0.4583 | 0.8750 | 1.0000 |

## Interpretation Rules

- Evasion is not inferred unless detector results are supplied.
- `sql_signal_rate_debug_only` and technique hints are retained for continuity with Phase 6 but must not be used as checkpoint gates.
- A sample should count toward a main claim only when validity, novelty, and evasion are all measurable.
