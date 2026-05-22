# 03 Decision Gate Report

## Decision

- Decision: `MLE_MAIN`
- Reason: Conditional MLE passed floors and adversarial action generation did not beat simpler baselines.
- Seeds: 1729, 1730, 1731
- Samples per seed: 5000

## Mean/Std/CI

| Baseline | Seeds | Floor pass rate | Composite mean | Std | CI95 |
| --- | ---: | ---: | ---: | ---: | ---: |
| H1_conditional_mle | 3 | 1.000 | 0.7840 | 0.0022 | 0.0025 |
| H2_mle_d_scorer | 3 | 1.000 | 0.7828 | 0.0006 | 0.0007 |
| H3_anchor_only_action_infiller | 3 | 1.000 | 0.7827 | 0.0023 | 0.0026 |
| H4_gumbel_action_surgery_gan | 3 | 1.000 | 0.7328 | 0.0138 | 0.0156 |
| H5_rule_tamper_baseline | 3 | 1.000 | 0.7840 | 0.0025 | 0.0028 |
