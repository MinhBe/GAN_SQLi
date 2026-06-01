# Source Cards

This consolidated source-card file summarizes all Week 3 dataset/source inventory entries. Detailed source-specific cards remain in `Timeline/Data/manifests`.

## PayloadsAllTheThings SQL Injection

- Role: Seed corpus, taxonomy, operator baseline
- Origin: Teacher-provided resource
- Source URL: `https://github.com/swisskyrepo/PayloadsAllTheThings`
- Commit/hash: `e961fef231d8327bae83b563fab50aec2e6b77c0`
- Local file: `Timeline/Data/raw/payloadsallthethings/SQL Injection/Intruder`
- Raw rows: 1465
- Usable rows: 1359
- Duplicate rows: 106
- Invalid rows: not_checked
- Skipped rows: 0
- License: MIT
- Label source: README taxonomy and source filenames
- Status: `ingested`

## HttpParams Dataset

- Role: Paper train/eval comparison source
- Origin: Le 2024 GSQLi dataset reference
- Source URL: `https://github.com/Morzeux/HttpParamsDataset`
- Commit/hash: `926670a710283f87c05b554680facf3f9530548c`
- Local file: `Timeline/Data/raw/httpparamsdataset/payload_full.csv`
- Raw rows: 31067
- Usable rows: 10852
- Duplicate rows: 0
- Invalid rows: not_checked
- Skipped rows: 20215
- License: MIT
- Label source: attack_type/label fields
- Status: `ingested`

## SQLiV3 mirror

- Role: Paper eval comparison source
- Origin: SSHS/Kaggle SQL Injection Dataset mirror
- Source URL: `https://github.com/nidnogg/sqliv5-dataset`
- Commit/hash: `486e182221e48d2cadab63edc217dfd46eb67405`
- Local file: `Timeline/Data/raw/sqliv5-dataset/SQLiV3_clean.json`
- Raw rows: 30864
- Usable rows: 11288
- Duplicate rows: 59
- Invalid rows: not_checked
- Skipped rows: 19517
- License: MIT
- Label source: type field
- Status: `ingested`

## WAF-A-MoLE dataset

- Role: ML-WAF/guided mutation baseline dataset
- Origin: Demetrio 2020
- Source URL: `https://github.com/blindusername/wafamole-dataset`
- Commit/hash: `pending`
- Local file: `pending`
- Raw rows: pending
- Usable rows: pending
- Duplicate rows: pending
- Invalid rows: pending
- Skipped rows: pending
- License: pending
- Label source: paper labels
- Status: `todo`

## Dasari CWGAN-GP Source Status

- Role: CWGAN-GP augmentation reproduction source
- Origin: Dasari 2025
- Source URL: `https://www.kaggle.com/datasets/syedsaqlainhussain/sql-injection-dataset`
- Commit/hash: `pending_official_snapshot`
- Local file: `Timeline/Data/raw/dasari_2025/sqli.csv`
- Raw rows: 0
- Usable rows: 0
- Duplicate rows: 0
- Invalid rows: not_checked
- Skipped rows: 0
- License: Unknown
- Label source: Kaggle Label field
- Status: `missing_official_local_snapshot`
- Note: the current Dasari smoke used the SQLiV3 mirror fallback, so it is `partial_smoke`, not exact reproduction.

## Dasari CWGAN-GP Fallback Source

- Role: Fallback source for Dasari partial smoke only
- Origin: Dasari 2025 partial smoke
- Source URL: `https://github.com/nidnogg/sqliv5-dataset`
- Commit/hash: `486e182221e48d2cadab63edc217dfd46eb67405`
- Local file: `Timeline/Data/raw/sqliv5-dataset/sqli.csv`
- Raw rows: 4200
- Usable rows: 3936
- Duplicate rows: 251
- Invalid rows: 13
- Skipped rows: 0
- License: MIT
- Label source: Sentence/Label fields
- Status: `partial_smoke_fallback_used`

## SQLMap tamper scripts

- Role: Mutation operator source, not a dataset
- Origin: Teacher/Lu/Demetrio reference
- Source URL: `https://github.com/sqlmapproject/sqlmap`
- Commit/hash: `pending`
- Local file: `pending`
- Raw rows: not_applicable
- Usable rows: not_applicable
- Duplicate rows: not_applicable
- Invalid rows: not_applicable
- Skipped rows: not_applicable
- License: pending
- Label source: operator source
- Status: `todo`

## Combined Corpus

- Combined rows: 23664
- Combined unique normalized hashes: 23082
- Combined duplicate rows by hash: 582
- Invalid rows: not checked by semantic evaluator yet
