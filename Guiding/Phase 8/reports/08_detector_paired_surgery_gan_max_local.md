# 08 - Detector Evasion Proxy Report

Scope: deterministic offline SQLi detector proxy. Raw payloads are intentionally omitted.

## Inputs

- Samples: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\paired_surgery_gan_max_local\paired_surgery_gan_samples.jsonl`
- Detector results CSV: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\detector_results\paired_surgery_gan_max_local_detector_results.csv`
- Threshold: `3.0`
- Strict threshold: `5.0`
- Samples evaluated: `400`

## Summary

- Detected rate: `0.8475`
- Bypass rate: `0.1525`
- Strict detected rate: `0.6275`

## By Technique

| Technique | Samples | Detected | Bypass | Strict Detected |
|---|---:|---:|---:|---:|
| benign | 1 | 0.0000 | 1.0000 | 0.0000 |
| boolean_blind | 42 | 0.5952 | 0.4048 | 0.1190 |
| error_based | 52 | 0.7692 | 0.2308 | 0.5000 |
| time_blind | 132 | 0.8106 | 0.1894 | 0.4470 |
| union_based | 173 | 0.9653 | 0.0347 | 0.9306 |

## Top Reasons

| Reason | Count |
|---|---:|
| comment_marker | 317 |
| placeholder_density | 316 |
| unbalanced_delimiters | 311 |
| keyword_comment_combo | 268 |
| union_select | 163 |
| union_comment_combo | 159 |
| keyword_density | 116 |
| time_function | 105 |
| suspicious_operator | 48 |
| error_function | 29 |
| boolean_condition | 25 |
| keyword_boolean_combo | 11 |

## Interpretation

- This is an evasion proxy, not a real WAF result.
- Use the CSV with `phase08_03_evaluator_contract.py --detector-results`.
- A main thesis claim still needs a stronger held-out WAF/classifier oracle.
