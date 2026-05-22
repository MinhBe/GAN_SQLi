# 01 Slot/Action Audit

Generated: 2026-05-22

## G0 Decision

- Decision: `S2_TAMPER_ACTION`
- Reason: Action audit found enough non-literal tamper/action signal; use S2 tamper-action as the main path before any Gumbel GAN pilot.
- Source payload rows: 10000
- Action candidate rows: 84756
- Non-literal coverage: 1.000

## Action Family Counts

| Family | Count |
| --- | ---: |
| comment | 4756 |
| encoding | 19854 |
| function | 3579 |
| keyword_variant | 19688 |
| none | 9 |
| operator | 16986 |
| tamper_candidate | 9905 |
| whitespace | 9979 |

## Technique x DB Hint Coverage

| Technique | DB hint | Rows | Non-literal rate |
| --- | --- | ---: | ---: |
| benign | unlabeled_db_hint | 5558 | 0.997 |
| boolean_blind | mysql | 2055 | 1.000 |
| boolean_blind | oracle | 1561 | 1.000 |
| boolean_blind | sqlite | 153 | 1.000 |
| boolean_blind | unlabeled_db_hint | 12602 | 1.000 |
| error_based | mssql | 990 | 1.000 |
| error_based | mysql | 5662 | 1.000 |
| error_based | oracle | 3877 | 1.000 |
| time_blind | mssql | 957 | 1.000 |
| time_blind | mysql | 9410 | 1.000 |
| time_blind | oracle | 1963 | 1.000 |
| time_blind | postgres | 2069 | 1.000 |
| time_blind | unlabeled_db_hint | 1580 | 1.000 |
| union_based | mssql | 8 | 1.000 |
| union_based | mysql | 1334 | 1.000 |
| union_based | oracle | 424 | 1.000 |
| union_based | unlabeled_db_hint | 12836 | 1.000 |
| unlabeled_technique | mysql | 826 | 1.000 |
| unlabeled_technique | unlabeled_db_hint | 20891 | 1.000 |

## Registered Risks


