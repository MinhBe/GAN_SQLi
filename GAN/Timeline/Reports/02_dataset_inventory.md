# Dataset Inventory

## Summary

Week 3 consolidates dataset/source status and defines the first leakage-control split. Three online sources are ingested and usable for downstream evaluator preparation. WAF-A-MoLE and SQLMap remain todo sources for later baseline work.

## Inventory

| Source | Role | Raw Rows | Usable Rows | Duplicate Rows | Invalid Rows | Status |
| --- | --- | ---: | ---: | ---: | --- | --- |
| PayloadsAllTheThings SQL Injection | Seed corpus, taxonomy, operator baseline | 1465 | 1359 | 106 | not_checked | ingested |
| HttpParams Dataset | Paper train/eval comparison source | 31067 | 10852 | 0 | not_checked | ingested |
| SQLiV3 mirror | Paper eval comparison source | 30864 | 11288 | 59 | not_checked | ingested |
| WAF-A-MoLE dataset | ML-WAF/guided mutation baseline dataset | pending | pending | pending | pending | todo |
| SQLMap tamper scripts | Mutation operator source, not a dataset | not_applicable | not_applicable | not_applicable | not_applicable | todo |

## Combined Corpus

- Combined rows: 23664
- Unique normalized payload hashes: 23082
- Duplicate rows by normalized hash: 582
- Invalid rows: not checked by semantic evaluator yet

## Rows By Source

| Source ID | Rows |
| --- | ---: |
| `httpparamsdataset_sqli_payload_full` | 10852 |
| `payloadsallthethings_sqli_intruder` | 1465 |
| `sqliv3_mirror_sqli_clean` | 11347 |

## Split Summary

| Split | Unique hashes |
| --- | ---: |
| train | 18516 |
| validation | 2274 |
| test | 2292 |

## Outputs

- `Timeline/Reports/02_dataset_inventory.md`
- `Timeline/Data/manifests/dataset_inventory.csv`
- `Timeline/Data/manifests/source_cards.md`
- `Timeline/Data/splits/split_rule.md`
- `Timeline/Data/splits/teacher_seed_split_assignments.csv`
- `Timeline/Data/splits/split_summary.csv`
- `Timeline/Data/splits/split_by_source.csv`

## Next Step

Week 4 should build the evaluator smoke test over a small sample and should not run model training before evaluator metrics and split-aware sampling exist.
