# 08 - Detector Evasion Proxy Report

Scope: deterministic offline SQLi detector proxy. Raw payloads are intentionally omitted.

## Inputs

- Samples: `Guiding\Phase 8\outputs\classifier_oracle_rerank\max_aggressive_candidates_top400_balanced_novel.jsonl`
- Detector results CSV: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\detector_results\max_aggressive_rerank_balanced_novel_detector_results.csv`
- Threshold: `3.0`
- Strict threshold: `5.0`
- Samples evaluated: `400`

## Summary

- Detected rate: `0.4650`
- Bypass rate: `0.5350`
- Strict detected rate: `0.2175`

## By Technique

| Technique | Samples | Detected | Bypass | Strict Detected |
|---|---:|---:|---:|---:|
| benign | 107 | 0.0187 | 0.9813 | 0.0000 |
| boolean_blind | 27 | 0.2222 | 0.7778 | 0.1852 |
| error_based | 64 | 0.5000 | 0.5000 | 0.2344 |
| time_blind | 77 | 0.6753 | 0.3247 | 0.2338 |
| union_based | 125 | 0.7520 | 0.2480 | 0.3920 |

## Top Reasons

| Reason | Count |
|---|---:|
| placeholder_density | 314 |
| comment_marker | 168 |
| keyword_density | 162 |
| keyword_comment_combo | 156 |
| time_function | 69 |
| suspicious_operator | 50 |
| union_select | 33 |
| error_function | 31 |
| union_comment_combo | 29 |
| boolean_condition | 10 |
| keyword_boolean_combo | 10 |

## Interpretation

- This is an evasion proxy, not a real WAF result.
- Use the CSV with `phase08_03_evaluator_contract.py --detector-results`.
- A main thesis claim still needs a stronger held-out WAF/classifier oracle.
