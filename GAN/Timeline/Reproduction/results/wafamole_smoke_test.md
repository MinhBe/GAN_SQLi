# WAF-A-MoLE Smoke / Failure Report

## Summary

WAF-A-MoLE code and dataset were cloned and inspected. The full guided reproduction is blocked in the current Python environment because the bundled example classifiers are old serialized sklearn/Keras artifacts and do not load or predict cleanly under the current runtime.

The SQL mutation operator layer itself was smoke-tested through the same local ModSecurity + OWASP CRS WAF path used in Week 5. This operator-only run is not reported as full guided WAF-A-MoLE evasion.

## Source Status

| Source | Commit | Status |
| --- | --- | --- |
| WAF-A-MoLE code | `4a2cb9438f874ec0d09acaa04402174cc6334880` | cloned |
| wafamole-dataset | `b8f0118b8586f8b069ac980b3909970838f69d5e` | cloned/counted |

## Dataset Counts

| File | Rows |
| --- | ---: |
| attacks.sql | 1286863 |
| sane.sql | 1000217 |

## Model Probe

| Metric | Value |
| --- | ---: |
| Candidate example models | 9 |
| Models loaded and classified probe | 0 |
| Models failed | 9 |

Failure types: `NotSklearnModelError: 8, SklearnInternalError: 1`.

## Operator-Only WAF Smoke

| Metric | Value |
| --- | ---: |
| Operator samples | 40 |
| Real WAF blocked | 23 |
| Real WAF allowed | 17 |
| Real WAF errors | 0 |

## Outputs

- `Timeline/Reproduction/configs/wafamole_smoke_config.yaml`
- `Timeline/Reproduction/results/wafamole_model_status.csv`
- `Timeline/Reproduction/results/wafamole_dataset_inventory.csv`
- `Timeline/Reproduction/results/wafamole_operator_smoke_samples.csv`
- `Timeline/Reproduction/results/wafamole_smoke_metrics.csv`
- `Timeline/Reproduction/logs/wafamole_smoke.log`

## Decision

Use WAF-A-MoLE as a documented strong baseline candidate with an operator-layer smoke result and a concrete environment blocker. Do not claim full guided WAF-A-MoLE reproduction until a compatible legacy environment is created or the bundled models are regenerated.
