# SQLiV3 Mirror Teacher Resource Inventory

## Source

- Online source URL: `https://github.com/nidnogg/sqliv5-dataset`
- Raw source path: `GAN/Data/raw/sqliv5-dataset`
- Primary input path: `GAN/Data/raw/sqliv5-dataset/SQLiV3_clean.json`
- Downloaded commit/hash: `486e182221e48d2cadab63edc217dfd46eb67405`

## Generated Artifacts

- `GAN/Data/manifests/sqliv3_sqli_source_card.md`
- `GAN/Data/manifests/sqliv3_sqli_inventory.csv`
- `GAN/Data/processed/sqliv3_sqli_normalized.csv`
- `GAN/Data/processed/teacher_seed_sqli_normalized_combined.csv`
- `GAN/Reproduction/baselines/sqliv3_rule_baseline.md`

## Seed Statistics

- Total source records: 30864
- SQLi rows selected: 11347
- Non-SQLi rows skipped: 19517
- Unique SQLi hashes: 11288
- Duplicate SQLi rows by payload hash: 59
- Combined normalized rows: 23664
- Combined unique payload hashes: 23082
- Combined duplicate rows by payload hash: 582

## Rows By Category

| Category | Rows |
| --- | ---: |
| Blind Injection | 5833 |
| Entry Point Detection | 2129 |
| Error Based Injection | 528 |
| Stacked Based Injection | 28 |
| Time Based Injection | 610 |
| UNION Based Injection | 2219 |

## Rows By DBMS

| DBMS | Rows |
| --- | ---: |
| generic | 9206 |
| mssql | 642 |
| mysql | 322 |
| oracle | 939 |
| postgresql | 238 |

## Notes

- This report contains aggregate counts only.
- Detailed seed strings are base64-encoded in processed CSV artifacts.
- No offline source was used.
