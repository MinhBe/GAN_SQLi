# Real WAF Smoke Test

## Summary

The Week 4 evaluator sample was rerun against a real local WAF engine: ModSecurity with OWASP CRS in Docker. Payload text is decoded only in memory for HTTP requests and is not written to reports or logs.

## Metrics

| Metric | Value |
| --- | ---: |
| Samples | 45 |
| Real WAF blocked | 41 |
| Real WAF allowed | 4 |
| Real WAF errors | 0 |
| Local-rule blocked | 27 |
| Local-rule allowed | 18 |
| Local/real agreement | 29 |
| Local/real disagreement | 16 |

## Configuration

- Config: `Timeline/Reproduction/configs/real_waf_smoke_config.yaml`
- Samples: `Timeline/Reproduction/results/evaluator_smoke_samples.csv`
- WAF image: `owasp/modsecurity-crs:nginx`
- WAF mode: `modsecurity_crs_docker`
- Payload text in reports/logs: no
- Rule IDs: not collected, to avoid storing WAF logs that may include request payload text

## Outputs

- `Timeline/Reproduction/results/real_waf_smoke_metrics.csv`
- `Timeline/Reproduction/results/real_waf_smoke_samples.csv`
- `Timeline/Reproduction/logs/real_waf_smoke_test.log`

## Next Step

Use these real-WAF decisions as the Week 5 baseline evaluator path. If rule-level attribution is needed later, add a sanitizer that strips payload-bearing request lines before persisting audit logs.
