# 08 - Detector Evasion Proxy Report

Scope: deterministic offline SQLi detector proxy. Raw payloads are intentionally omitted.

## Inputs

- Samples: `Guiding\Phase 8\outputs\oracle_aware_search\attack_balanced_novel_oracle_search.jsonl`
- Detector results CSV: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\detector_results\oracle_search_attack_balanced_novel_detector_results.csv`
- Threshold: `3.0`
- Strict threshold: `5.0`
- Samples evaluated: `400`

## Summary

- Detected rate: `0.8475`
- Bypass rate: `0.1525`
- Strict detected rate: `0.4425`

## By Technique

| Technique | Samples | Detected | Bypass | Strict Detected |
|---|---:|---:|---:|---:|
| boolean_blind | 9 | 1.0000 | 0.0000 | 1.0000 |
| error_based | 36 | 0.9722 | 0.0278 | 0.8611 |
| time_blind | 100 | 0.9500 | 0.0500 | 0.3500 |
| union_based | 255 | 0.7843 | 0.2157 | 0.4000 |

## Top Reasons

| Reason | Count |
|---|---:|
| placeholder_density | 353 |
| comment_marker | 291 |
| keyword_density | 276 |
| keyword_comment_combo | 275 |
| time_function | 124 |
| error_function | 69 |
| union_select | 67 |
| union_comment_combo | 59 |
| suspicious_operator | 42 |
| boolean_condition | 15 |
| keyword_boolean_combo | 15 |

## Interpretation

- This is an evasion proxy, not a real WAF result.
- Use the CSV with `phase08_03_evaluator_contract.py --detector-results`.
- A main thesis claim still needs a stronger held-out WAF/classifier oracle.
