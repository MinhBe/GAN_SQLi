# 03 - Preregistered Decision Gate Protocol

> Recreated after Phase 3 artifact loss. This protocol is gate-only and uses the
> existing Phase 2 artifacts without retraining or tuning.

## Inputs

Required artifacts:

```text
Guiding/Phase 2/eval/mle_frontier.json
Guiding/Phase 2/eval/gan_results.json
```

## Unit Of Analysis

GAN aggregate statistics use seed as the statistical unit:

```text
GAN seeds: 42, 123, 456
```

MLE is represented as a sampling frontier over fixed Phase 2 seeds and sampling
configs. Per-seed MLE best points are reported separately from the full frontier.

## Gate Rules

GAN must pass all gates to become the main path.

| Gate | Rule |
|---|---|
| G1 unique_ratio | GAN best seed unique_ratio must exceed MLE best frontier unique_ratio |
| G2 self_bleu3 | GAN best seed self_bleu3 must be lower than MLE best frontier self_bleu3 |
| G3 syntax guard | GAN best seed syntax_validity_rate must be at least 0.9x the MLE reference syntax rate |
| G4 D-shortcut | mean delta_D_real_softened must be below 0.3 and no seed can be shortcut-flagged |
| G5 no-collapse | Most GAN seeds must not be collapse-tagged |
| G6 frontier dominance | At least one GAN seed must dominate a point on the MLE Pareto frontier in unique_ratio/syntax space |

## Tie Break

```text
MLE is the default.
If GAN ties, is inconclusive, or fails any required gate, decision = MLE_MAIN.
```

## Outputs

```text
Guiding/Phase 3/eval/phase03/decision.json
Guiding/Phase 3/eval/phase03/statistical_summary.json
Guiding/Phase 3/eval/phase03/mle_vs_gan_frontier.png
Guiding/Phase 3/reports/03_decision_gate_report.md
```

## Known Limitations

Phase 2 artifacts do not contain `type_accuracy`, so Phase 3 must not invent or
score that metric. Syntax can only be used as a formal guard when the
best-syntax GAN seed is also collapse-tagged.
