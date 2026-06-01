# Evaluator Smoke Test

## Summary

Week 4 smoke-tested the evaluator over a split-aware sample. The run uses lightweight SQLi-like validity rules, exact-hash novelty checks against the train split, simple diversity features, and a local deterministic WAF-rule smoke check.

This is not a final WAF evaluation. `local_rule_smoke` is a placeholder until ModSecurity plus OWASP CRS or Coraza is installed and configured.

## Configuration

- Config: `Timeline/Reproduction/configs/evaluation_config.yaml`
- Input corpus: `Timeline/Data/processed/teacher_seed_sqli_normalized_combined.csv`
- Split assignments: `Timeline/Data/splits/teacher_seed_split_assignments.csv`
- Samples per split: 15
- Payload text in reports/logs: no

## Metrics

| Metric | Value |
| --- | ---: |
| Samples | 45 |
| SQLi-like validity hits | 45 |
| Needs review | 0 |
| Unique hashes | 45 |
| Local WAF-rule blocked | 27 |
| Local WAF-rule allowed | 18 |
| Average length | 107.33 |
| Average token count | 37.60 |
| Average character entropy | 4.0132 |

## Split Coverage

| Split | Samples |
| --- | ---: |
| train | 15 |
| validation | 15 |
| test | 15 |

## Local WAF-Rule Smoke

| Decision | Samples |
| --- | ---: |
| block | 27 |
| allow | 18 |

## Outputs

- `Timeline/Reproduction/results/evaluator_smoke_metrics.csv`
- `Timeline/Reproduction/results/evaluator_smoke_samples.csv`
- `Timeline/Reproduction/logs/waf_smoke_test.log`

## Next Step

Install or configure a real WAF engine and rerun the same sample path. Until then, do not report ASR/FNR as real WAF metrics.
