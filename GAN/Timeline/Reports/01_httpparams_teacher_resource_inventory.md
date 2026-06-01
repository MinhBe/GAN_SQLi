# HttpParamsDataset Teacher Resource Inventory

## Source

- Online source URL: `https://github.com/Morzeux/HttpParamsDataset`
- Raw source path: `GAN/Data/raw/httpparamsdataset`
- Downloaded commit/hash: `926670a710283f87c05b554680facf3f9530548c`

## Generated Artifacts

- `GAN/Data/manifests/httpparamsdataset_sqli_source_card.md`
- `GAN/Data/manifests/httpparams_sqli_inventory.csv`
- `GAN/Data/processed/httpparams_sqli_normalized.csv`
- `GAN/Data/processed/teacher_seed_sqli_normalized_combined.csv`
- `GAN/Reproduction/baselines/httpparamsdataset_rule_baseline.md`

## Seed Statistics

- Total source records: 31067
- SQLi rows selected: 10852
- Non-SQLi rows skipped: 20215
- Unique HttpParams SQLi hashes: 10852
- Duplicate HttpParams SQLi rows by payload hash: 0
- Combined normalized rows: 12317
- Combined unique payload hashes: 12208
- Combined duplicate rows by payload hash: 109

## Rows By Category

| Category | Rows |
| --- | ---: |
| Blind Injection | 4924 |
| Entry Point Detection | 417 |
| Error Based Injection | 129 |
| Stacked Based Injection | 1112 |
| Time Based Injection | 2318 |
| UNION Based Injection | 1952 |

## Rows By DBMS

| DBMS | Rows |
| --- | ---: |
| generic | 7019 |
| mssql | 796 |
| mysql | 2112 |
| oracle | 925 |

## Notes

- This report contains aggregate counts only.
- Detailed seed strings are base64-encoded in processed CSV artifacts.
- No offline source was used.
