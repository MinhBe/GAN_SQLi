# 08 - Detector Evasion Proxy Report

Scope: deterministic offline SQLi detector proxy. Raw payloads are intentionally omitted.

## Inputs

- Samples: `Guiding\Phase 8\outputs\paired_surgery_gan_constrained\paired_surgery_gan_samples.jsonl`
- Detector results CSV: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\detector_results\paired_surgery_gan_constrained_detector_results.csv`
- Threshold: `3.0`
- Strict threshold: `5.0`
- Samples evaluated: `400`

## Summary

- Detected rate: `0.8900`
- Bypass rate: `0.1100`
- Strict detected rate: `0.6675`

## By Technique

| Technique | Samples | Detected | Bypass | Strict Detected |
|---|---:|---:|---:|---:|
| benign | 1 | 0.0000 | 1.0000 | 0.0000 |
| boolean_blind | 42 | 0.9524 | 0.0476 | 0.2619 |
| error_based | 52 | 0.7885 | 0.2115 | 0.5962 |
| time_blind | 132 | 0.8106 | 0.1894 | 0.5530 |
| union_based | 173 | 0.9711 | 0.0289 | 0.8786 |

## Top Reasons

| Reason | Count |
|---|---:|
| placeholder_density | 316 |
| unbalanced_delimiters | 311 |
| comment_marker | 308 |
| keyword_comment_combo | 260 |
| union_select | 149 |
| union_comment_combo | 147 |
| keyword_density | 130 |
| time_function | 105 |
| boolean_condition | 75 |
| suspicious_operator | 48 |
| keyword_boolean_combo | 39 |
| error_function | 29 |

## Interpretation

- This is an evasion proxy, not a real WAF result.
- Use the CSV with `phase08_03_evaluator_contract.py --detector-results`.
- A main thesis claim still needs a stronger held-out WAF/classifier oracle.
