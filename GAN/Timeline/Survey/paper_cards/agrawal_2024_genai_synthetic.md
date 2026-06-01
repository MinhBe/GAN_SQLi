# Agrawal 2024 - GenAI Synthetic

## Identity

- Paper id: `agrawal_2024_genai_synthetic`
- Source file id: `Agrawal_2024_GenAI_Synthetic.md`
- Classification label: `synthetic_detection_related`
- Phase 1 role: Context paper for synthetic cyber attack data under class imbalance.

## Extraction

| Field | Value |
| --- | --- |
| Dataset/source mentioned | CICIDS2017; IDS web attack and brute force minority classes |
| Code/testbed mentioned | CTGAN; Random Forest; XGBoost |
| Method/model | CTGAN augmentation of minority IDS classes followed by classifier training. |
| Metrics | Accuracy, precision, recall, F1, and class-specific recall. |
| Reproduction priority | `context_only` |
| Reproduction level candidate | `not_applicable_to_sqli_payload_corpus` |

## Relation To Teacher Resource

Supports the motivation for synthetic data, but should not be used as a SQLi payload corpus.

## Phase 1 Action

Use as background when discussing class imbalance and synthetic data limits.
