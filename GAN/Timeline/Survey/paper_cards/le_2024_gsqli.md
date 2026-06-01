# Le 2024 - GSQLi

## Identity

- Paper id: `le_2024_gsqli`
- Source file id: `Le_2024_GSQLi.md`
- Classification label: `core_sqli_generation`
- Phase 1 role: Core paper for SQLi payload mutation against WAF and ML detectors.

## Extraction

| Field | Value |
| --- | --- |
| Dataset/source mentioned | HttpParams Dataset; SSHS/Kaggle SQL Injection Dataset |
| Code/testbed mentioned | RNN, GRU, BiLSTM detectors; ModSecurity; OWASP CRS |
| Method/model | Token parser, mutation vector, GAN generator, payload transformer, attack classifier, discriminator/evaluator. |
| Metrics | TPR/FNR in paper; project should add validity, uniqueness, novelty, diversity, duplicate rate, and failure labels. |
| Reproduction priority | `first_reproduction_target` |
| Reproduction level candidate | `partial_or_conceptual_until exact code/config are available` |

## Relation To Teacher Resource

Uses paper datasets for comparison after the teacher seed corpus has been built from PayloadsAllTheThings.

## Phase 1 Action

Use as the main GSQLi reproduction plan after evaluator and baselines exist.
