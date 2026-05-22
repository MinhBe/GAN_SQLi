# 02 De-risk Action-Surgery Slice

Generated: 2026-05-22

## Slice Decision

- Decision: `D_SCORER_MAIN`
- Reason: D-as-scorer is the strongest available passing baseline.

## Split Sizes

| Split | Rows |
| --- | ---: |
| train | 5000 |
| dev | 1000 |
| test | 1000 |

## Evaluator Metrics

| Metric | Value |
| --- | ---: |
| round_trip_success | 1.0000 |
| parse_success | 0.9759 |
| sqlite_execution_safety | 0.2328 |
| action_validity | 1.0000 |
| unique_ratio | 1.0000 |
| self_bleu3 | 0.7341 |
| template_entropy | 8.9508 |
| template_entropy_norm | 0.9401 |
| action_entropy | 3.2460 |
| action_entropy_norm | 0.9771 |
| near_copy_rate | 0.2913 |
| condition_accuracy | 1.0000 |

Composite floors pass: `True`
