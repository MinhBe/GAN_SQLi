# 08 - Detector Evasion Proxy Report

Scope: deterministic offline SQLi detector proxy. Raw payloads are intentionally omitted.

## Inputs

- Samples: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\paired_surgery_gan_max_aggressive\paired_surgery_gan_samples.jsonl`
- Detector results CSV: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\detector_results\paired_surgery_gan_max_aggressive_detector_results.csv`
- Threshold: `3.0`
- Strict threshold: `5.0`
- Samples evaluated: `400`

## Summary

- Detected rate: `0.7675`
- Bypass rate: `0.2325`
- Strict detected rate: `0.4950`

## By Technique

| Technique | Samples | Detected | Bypass | Strict Detected |
|---|---:|---:|---:|---:|
| benign | 1 | 0.0000 | 1.0000 | 0.0000 |
| boolean_blind | 42 | 0.4286 | 0.5714 | 0.0238 |
| error_based | 52 | 0.6538 | 0.3462 | 0.3654 |
| time_blind | 132 | 0.6970 | 0.3030 | 0.4167 |
| union_based | 173 | 0.9422 | 0.0578 | 0.7110 |

## Top Reasons

| Reason | Count |
|---|---:|
| placeholder_density | 323 |
| comment_marker | 320 |
| unbalanced_delimiters | 311 |
| keyword_comment_combo | 257 |
| union_select | 106 |
| union_comment_combo | 105 |
| time_function | 101 |
| keyword_density | 98 |
| suspicious_operator | 48 |
| error_function | 20 |
| boolean_condition | 16 |
| keyword_boolean_combo | 11 |

## Interpretation

- This is an evasion proxy, not a real WAF result.
- Use the CSV with `phase08_03_evaluator_contract.py --detector-results`.
- A main thesis claim still needs a stronger held-out WAF/classifier oracle.
