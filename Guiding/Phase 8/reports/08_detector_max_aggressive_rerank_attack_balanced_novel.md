# 08 - Detector Evasion Proxy Report

Scope: deterministic offline SQLi detector proxy. Raw payloads are intentionally omitted.

## Inputs

- Samples: `Guiding\Phase 8\outputs\classifier_oracle_rerank\max_aggressive_candidates_top400_attack_balanced_novel.jsonl`
- Detector results CSV: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\detector_results\max_aggressive_rerank_attack_balanced_novel_detector_results.csv`
- Threshold: `3.0`
- Strict threshold: `5.0`
- Samples evaluated: `400`

## Summary

- Detected rate: `0.6225`
- Bypass rate: `0.3775`
- Strict detected rate: `0.3000`

## By Technique

| Technique | Samples | Detected | Bypass | Strict Detected |
|---|---:|---:|---:|---:|
| boolean_blind | 52 | 0.5577 | 0.4423 | 0.0962 |
| error_based | 138 | 0.5362 | 0.4638 | 0.3478 |
| time_blind | 84 | 0.6190 | 0.3810 | 0.2143 |
| union_based | 126 | 0.7460 | 0.2540 | 0.3889 |

## Top Reasons

| Reason | Count |
|---|---:|
| placeholder_density | 362 |
| keyword_density | 247 |
| comment_marker | 210 |
| keyword_comment_combo | 192 |
| time_function | 73 |
| suspicious_operator | 62 |
| boolean_condition | 40 |
| keyword_boolean_combo | 40 |
| union_select | 33 |
| error_function | 29 |
| union_comment_combo | 29 |

## Interpretation

- This is an evasion proxy, not a real WAF result.
- Use the CSV with `phase08_03_evaluator_contract.py --detector-results`.
- A main thesis claim still needs a stronger held-out WAF/classifier oracle.
