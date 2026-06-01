# Dasari 2025 CWGAN-GP Reproduction Smoke

## Status

- Reproduction level: `partial_smoke`
- Selected source: `sqliv5_sqli_csv_fallback`
- Source status: `fallback_mirror_not_exact`
- Official Kaggle `sqli.csv` present locally: `False`
- `Modified SQL Dataset.csv` present locally: `False`
- WAF-A-MoLE remains frozen at `threshold_reached=0`; this run does not reopen it.

## Artifacts

- Config: `Timeline/Reproduction/configs/dasari_cwgangp_config.yaml`
- Prepared data: `Timeline/Data/processed/dasari_cwgangp_prepared.csv`
- Checkpoint: `Timeline/Reproduction/checkpoints/dasari_cwgangp_smoke.pt`
- Metrics: `Timeline/Reproduction/results/dasari_cwgangp_metrics.csv`
- Detection uplift smoke: `Timeline/Reproduction/results/dasari_cwgangp_detection_uplift.csv`
- Synthetic samples: `Timeline/Reproduction/results/dasari_cwgangp_synthetic_samples.csv`
- Data status: `Timeline/Data/manifests/dasari_cwgangp_data_status.csv`

## Data Summary

| Metric | Value |
| --- | ---: |
| Prepared rows | 3936 |
| Unique query hashes | 3936 |
| Label 0 rows | 2999 |
| Label 1 rows | 937 |
| Train rows | 3134 |
| Validation rows | 384 |
| Test rows | 418 |
| Synthetic samples | 80 |
| Non-empty synthetic samples | 79 |
| Unique synthetic hashes | 78 |

## Detection Uplift Smoke

| Training set | Accuracy | Precision | Recall | F1 |
| --- | ---: | ---: | ---: | ---: |
| real_train_only | 0.9641 | 1.0000 | 0.8855 | 0.9393 |
| real_train_plus_cwgangp_synthetic_smoke | 0.9665 | 1.0000 | 0.8931 | 0.9435 |

## Interpretation

This is a smoke implementation to start the Dasari reproduction path and verify the required artifact contract: config, checkpoint, log, metrics, and report. It must not be cited as an exact paper reproduction until the official Kaggle snapshot and modified dataset status are resolved.

No raw payload strings are printed in this report.
