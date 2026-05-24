# 08 - Detector Evasion Proxy Report

Scope: deterministic offline SQLi detector proxy. Raw payloads are intentionally omitted.

## Inputs

- Samples: `Guiding\Phase 8\outputs\classifier_oracle_rerank\max_aggressive_candidates_top400_attack_balanced_novel_hint.jsonl`
- Detector results CSV: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\detector_results\max_aggressive_rerank_attack_balanced_novel_hint_detector_results.csv`
- Threshold: `3.0`
- Strict threshold: `5.0`
- Samples evaluated: `245`

## Summary

- Detected rate: `0.7469`
- Bypass rate: `0.2531`
- Strict detected rate: `0.3796`

## By Technique

| Technique | Samples | Detected | Bypass | Strict Detected |
|---|---:|---:|---:|---:|
| boolean_blind | 6 | 1.0000 | 0.0000 | 1.0000 |
| error_based | 11 | 1.0000 | 0.0000 | 0.8182 |
| time_blind | 61 | 0.9180 | 0.0820 | 0.2951 |
| union_based | 167 | 0.6587 | 0.3413 | 0.3593 |

## Top Reasons

| Reason | Count |
|---|---:|
| placeholder_density | 220 |
| comment_marker | 172 |
| keyword_comment_combo | 168 |
| keyword_density | 155 |
| time_function | 73 |
| union_select | 44 |
| union_comment_combo | 40 |
| error_function | 26 |
| suspicious_operator | 16 |
| boolean_condition | 8 |
| keyword_boolean_combo | 8 |

## Interpretation

- This is an evasion proxy, not a real WAF result.
- Use the CSV with `phase08_03_evaluator_contract.py --detector-results`.
- A main thesis claim still needs a stronger held-out WAF/classifier oracle.
