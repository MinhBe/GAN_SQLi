# 03 - Decision Gate Report

> Recreated from Phase 02 artifacts. This phase is gate-only and performs no training.

## Decision

- Decision: `MLE_MAIN`
- Gate passed: `false`
- Reason: GAN failed 4/6 Phase 03 gates: G1_unique_ratio, G2_self_bleu3, G5_no_collapse, G6_frontier_dominance. Tie-break/default path is MLE_MAIN.
- Recommended path: Conditional MLE + evaluator-guided search.

## Source Artifacts

- `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 2\eval\mle_frontier.json`
- `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 2\eval\gan_results.json`

## Key Metrics

| Metric | MLE reference | GAN reference |
|---|---:|---:|
| unique_ratio | 0.803 | 0.497 |
| self_bleu3 | 0.012 | 0.037 |
| syntax_validity_rate | 0.710 | 0.832 |

GAN seed means:

| Metric | Mean | Std | CI95 low | CI95 high |
|---|---:|---:|---:|---:|
| unique_ratio | 0.291 | 0.252 | -0.335 | 0.918 |
| self_bleu3 | 0.436 | 0.457 | -0.699 | 1.571 |
| token_entropy | 2.069 | 1.778 | -2.349 | 6.487 |
| syntax_validity_rate | 0.615 | 0.296 | -0.120 | 1.350 |

## Gate Results

| Gate | Evidence | Result |
|---|---|---|
| G1 unique_ratio | GAN 0.497 vs MLE 0.803 | FAIL |
| G2 self_bleu3 | GAN 0.037 vs MLE 0.012 | FAIL |
| G3 syntax guard | GAN 0.832 vs threshold 0.639 | PASS |
| G4 D-shortcut | mean delta 0.000650 vs threshold 0.300 | PASS |
| G5 no-collapse | collapsed 3/3 seeds | FAIL |
| G6 frontier dominance | dominating pairs 0 | FAIL |

## Collapse Check

| Seed | unique_ratio | self_bleu3 | syntax_validity_rate | collapse_detected |
|---|---:|---:|---:|---|
| 42 | 0.010 | 0.934 | 0.832 | True |
| 123 | 0.367 | 0.037 | 0.735 | True |
| 456 | 0.497 | 0.336 | 0.278 | True |

## Notes

- `type_accuracy` is unavailable in Phase 02 artifacts, so it is not scored here.
- G3 is a formal syntax guard; the best-syntax GAN seed is still collapse-tagged.
- G4 passes, meaning the available D-shortcut diagnostic does not explain the failure.
- The failure is driven by diversity/frontier/collapse gates.

## Outputs

- `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 3\eval\phase03\decision.json`
- `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 3\eval\phase03\statistical_summary.json`
- `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 3\eval\phase03\mle_vs_gan_frontier.png`
