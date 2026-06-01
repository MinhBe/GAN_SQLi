# WAF-A-MoLE Original Runtime Probe

## Summary

This probe uses an original-faithful legacy Docker runtime for WAF-A-MoLE: Python 3.7.x and scikit-learn 0.21.1, matching the upstream README and the bundled pickle provenance observed in the modern-runtime failure.

## Metrics

| Metric | Value |
| --- | ---: |
| Candidate bundled models | 9 |
| Models loaded and classified | 5 |
| Models failed | 4 |
| Guided engine smoke OK | 1 |
| Guided threshold reached | 0 |

Status: `guided_engine_smoke_no_evasion`.

## Outputs

- `Timeline/Reproduction/configs/wafamole_original_runtime_config.yaml`
- `Timeline/Reproduction/results/wafamole_original_runtime_versions.csv`
- `Timeline/Reproduction/results/wafamole_original_model_status.csv`
- `Timeline/Reproduction/results/wafamole_original_guided_smoke.csv`
- `Timeline/Reproduction/results/wafamole_original_runtime_metrics.csv`

## Claim Rule

Only claim the guided engine path is running if `guided_smoke_ok` is greater than zero. Claim evasion success only if `guided_threshold_reached` is greater than zero.
