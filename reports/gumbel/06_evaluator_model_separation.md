# 06 Evaluator And Model Separation

Generated: 2026-05-22

The evaluator is stored independently at `eval/gumbel/evaluator_config.json`.
Composite scoring is vetoed by metric floors before weights are applied.

```json
{
  "floors": {
    "round_trip_success": 0.95,
    "parse_success": 0.7,
    "action_validity": 0.7,
    "unique_ratio": 0.1,
    "near_copy_rate": 0.95
  },
  "weights": {
    "round_trip_success": 0.2,
    "parse_success": 0.2,
    "action_validity": 0.15,
    "unique_ratio": 0.15,
    "self_bleu3_diversity": 0.1,
    "template_entropy_norm": 0.1,
    "action_entropy_norm": 0.1
  },
  "near_copy_threshold": 0.92
}
```
