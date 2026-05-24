# 08 - Held-Out Classifier Oracle Report

Scope: local SQLi-vs-benign classifier trained only on the Phase 8 train split, thresholded on dev, and audited on held-out test. Raw payloads are intentionally omitted.

## Training

- Train split: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\delex_cluster_split\train.parquet`
- Dev split: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\delex_cluster_split\dev.parquet`
- Test split: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\delex_cluster_split\test.parquet`
- Training rows used: `174,956`
- Positives used: `150,000`
- Benign used: `24,956`
- Threshold: `0.021311`
- Target benign FPR on dev: `0.0500`

## Oracle Quality

| Split | N | Accuracy | Precision | SQLi Recall | Benign FPR | ROC-AUC | AP |
|---|---:|---:|---:|---:|---:|---:|---:|
| dev | 150,694 | 0.9999 | 0.9999 | 1.0000 | 0.0281 | 1.0000 | 1.0000 |
| test | 272,315 | 0.9999 | 0.9999 | 1.0000 | 0.0190 | 1.0000 | 1.0000 |

## Generated Samples

| Source | Samples | Detected | Bypass | Score P50 | Score P90 | CSV |
|---|---:|---:|---:|---:|---:|---|
| anchor_only_full_lite | 400 | 0.9950 | 0.0050 | 0.9986 | 0.9999 | `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\classifier_oracle_results\anchor_only_full_lite_classifier_oracle_results.csv` |
| mutation_engine_full_lite | 400 | 1.0000 | 0.0000 | 0.9803 | 0.9987 | `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\classifier_oracle_results\mutation_engine_full_lite_classifier_oracle_results.csv` |
| paired_surgery_gan_max_local | 400 | 1.0000 | 0.0000 | 0.9987 | 0.9999 | `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\classifier_oracle_results\paired_surgery_gan_max_local_classifier_oracle_results.csv` |
| paired_surgery_gan_max_aggressive | 400 | 0.9950 | 0.0050 | 0.9988 | 0.9999 | `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\classifier_oracle_results\paired_surgery_gan_max_aggressive_classifier_oracle_results.csv` |

## Interpretation

- This is stronger than the deterministic signature proxy because the detector is fit on held-out Phase 8 data and audited on the untouched test split.
- It is still an offline classifier oracle, not a live WAF.
- Use the generated CSVs with `phase08_03_evaluator_contract.py --detector-results`.
