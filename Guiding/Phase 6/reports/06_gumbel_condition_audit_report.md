# 06 - Gumbel Condition Audit

Scope: aggregate heuristic audit of generated sample JSONL files.
Raw generated texts are intentionally omitted from this report.

## Latest Sample File

- Step: `1500`
- Samples: `120`
- SQL signal rate: `1.0000`
- Benign SQL signal rate: `1.0000`
- Technique hint rate: `0.6354`

## Step Trend

| Step | Samples | SQL Signal | Benign SQL Signal | Technique Hint |
|---:|---:|---:|---:|---:|
| 50 | 120 | 1.0000 | 1.0000 | 0.5625 |
| 100 | 120 | 0.9833 | 1.0000 | 0.6146 |
| 150 | 120 | 1.0000 | 1.0000 | 0.6458 |
| 200 | 120 | 1.0000 | 1.0000 | 0.6458 |
| 300 | 120 | 1.0000 | 1.0000 | 0.6250 |
| 400 | 120 | 1.0000 | 1.0000 | 0.6042 |
| 500 | 120 | 1.0000 | 1.0000 | 0.6354 |
| 600 | 120 | 1.0000 | 1.0000 | 0.6875 |
| 700 | 120 | 1.0000 | 1.0000 | 0.6875 |
| 800 | 120 | 1.0000 | 1.0000 | 0.6146 |
| 900 | 120 | 1.0000 | 1.0000 | 0.6667 |
| 1000 | 120 | 1.0000 | 1.0000 | 0.6875 |
| 1100 | 120 | 1.0000 | 1.0000 | 0.6771 |
| 1200 | 120 | 1.0000 | 1.0000 | 0.6458 |
| 1300 | 120 | 1.0000 | 1.0000 | 0.6146 |
| 1400 | 120 | 1.0000 | 1.0000 | 0.6979 |
| 1500 | 120 | 1.0000 | 1.0000 | 0.6354 |

## Latest By Technique

| Technique | Samples | SQL Signal | Benign SQL Signal | Technique Hint |
|---|---:|---:|---:|---:|
| benign | 24 | 1.0000 | 1.0000 | n/a |
| boolean_blind | 24 | 1.0000 | n/a | 0.7083 |
| error_based | 24 | 1.0000 | n/a | 0.0000 |
| time_blind | 24 | 1.0000 | n/a | 0.8333 |
| union_based | 24 | 1.0000 | n/a | 1.0000 |

## Interpretation

- High `benign_sql_signal_rate` means the generator is not cleanly separating benign conditioning from SQL-like payload generation.
- Low `technique_hint_rate` means technique conditioning may be weak or the heuristic needs refinement.
- This audit is advisory; use it with manual review before extending adversarial training.
