# 08 - Detector Evasion Proxy Report

Scope: deterministic offline SQLi detector proxy. Raw payloads are intentionally omitted.

## Inputs

- Samples: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\surgery_baselines_full_lite\anchor_only_samples.jsonl`
- Detector results CSV: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\detector_results\anchor_only_full_lite_detector_results.csv`
- Threshold: `3.0`
- Strict threshold: `5.0`
- Samples evaluated: `400`

## Summary

- Detected rate: `0.8950`
- Bypass rate: `0.1050`
- Strict detected rate: `0.7200`

## By Technique

| Technique | Samples | Detected | Bypass | Strict Detected |
|---|---:|---:|---:|---:|
| benign | 1 | 0.0000 | 1.0000 | 0.0000 |
| boolean_blind | 42 | 0.9524 | 0.0476 | 0.2619 |
| error_based | 52 | 0.7885 | 0.2115 | 0.6346 |
| time_blind | 132 | 0.8106 | 0.1894 | 0.5606 |
| union_based | 173 | 0.9827 | 0.0173 | 0.9827 |

## Top Reasons

| Reason | Count |
|---|---:|
| placeholder_density | 316 |
| comment_marker | 314 |
| unbalanced_delimiters | 311 |
| keyword_comment_combo | 262 |
| union_select | 170 |
| union_comment_combo | 166 |
| keyword_density | 116 |
| time_function | 105 |
| boolean_condition | 82 |
| suspicious_operator | 48 |
| keyword_boolean_combo | 45 |
| error_function | 29 |

## Interpretation

- This is an evasion proxy, not a real WAF result.
- Use the CSV with `phase08_03_evaluator_contract.py --detector-results`.
- A main thesis claim still needs a stronger held-out WAF/classifier oracle.
