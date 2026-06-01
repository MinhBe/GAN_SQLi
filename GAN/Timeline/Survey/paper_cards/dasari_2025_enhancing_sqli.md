# Dasari 2025 - Enhancing SQLi Detection

## Identity

- Paper id: `dasari_2025_enhancing_sqli`
- Source file id: `Dasari_2025_Enhancing_SQLi.md`
- Classification label: `synthetic_detection_related`
- Phase 1 role: Related work for synthetic SQLi detection augmentation.

## Extraction

| Field | Value |
| --- | --- |
| Dataset/source mentioned | Kaggle sqli.csv; Modified SQL Dataset.csv |
| Code/testbed mentioned | XGBoost, LightGBM, Random Forest, KNN, SVM style detector comparison |
| Method/model | VAE, U-Net, CWGAN-GP, pseudo-labeling, and classical detection models. |
| Metrics | Accuracy, precision, recall, F1, MSE, R2, PCA-style synthetic quality checks. |
| Reproduction priority | `related_work_only` |
| Reproduction level candidate | `not_prioritized_for_waf_payload_phase1` |

## Relation To Teacher Resource

Detection augmentation focus, not primary WAF payload evasion.

## Phase 1 Action

Mention as related work and avoid mixing its tabular/query augmentation objective into GSQLi reproduction.
