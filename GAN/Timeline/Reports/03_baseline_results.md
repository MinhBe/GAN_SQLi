# Week 5 Baseline Results

## Summary

Week 5 evaluates two minimum baselines through the real local ModSecurity + OWASP CRS WAF path. Reports and logs contain metrics and hashes only; detailed payload text is not printed in markdown or logs.

## Metrics

| Baseline | Samples | Valid | Unique | Novel exact | Real WAF blocked | Real WAF allowed | Errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| deterministic_mutation | 60 | 52 | 60 | 60 | 36 | 24 | 0 |
| template_rule | 60 | 57 | 60 | 0 | 43 | 17 | 0 |

## Outputs

- `Timeline/Reproduction/configs/week5_baseline_config.yaml`
- `Timeline/Reproduction/baselines/week5_baseline_definitions.md`
- `Timeline/Reproduction/results/baseline_metrics.csv`
- `Timeline/Reproduction/results/baseline_samples.csv`
- `Timeline/Reproduction/logs/baseline_run.log`

## Interpretation

`template_rule` is the non-generative seed/template baseline. `deterministic_mutation` is the first mutation baseline and provides the minimum comparison point before WAF-A-MoLE or GSQLi reproduction work.
