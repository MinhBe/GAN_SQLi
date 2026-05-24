# 06 - MLE Condition Audit

Scope: aggregate heuristic audit of generated sample JSONL files.
Raw generated texts are intentionally omitted from this report.

## Latest Sample File

- Step: `2000`
- Samples: `120`
- SQL signal rate: `1.0000`
- Benign SQL signal rate: `1.0000`
- Technique hint rate: `0.6771`

## Step Trend

| Step | Samples | SQL Signal | Benign SQL Signal | Technique Hint |
|---:|---:|---:|---:|---:|
| 10 | 60 | 0.6333 | 0.8333 | 0.3750 |
| 20 | 60 | 0.6667 | 0.9167 | 0.2708 |
| 25 | 60 | 0.8167 | 0.9167 | 0.2292 |
| 50 | 60 | 0.9500 | 1.0000 | 0.3750 |
| 75 | 60 | 1.0000 | 1.0000 | 0.4583 |
| 100 | 60 | 0.9833 | 1.0000 | 0.5000 |
| 200 | 120 | 0.9917 | 1.0000 | 0.5729 |
| 300 | 120 | 1.0000 | 1.0000 | 0.5938 |
| 400 | 120 | 1.0000 | 1.0000 | 0.6458 |
| 500 | 120 | 1.0000 | 1.0000 | 0.5729 |
| 600 | 120 | 1.0000 | 1.0000 | 0.6562 |
| 700 | 120 | 1.0000 | 1.0000 | 0.6250 |
| 800 | 120 | 1.0000 | 1.0000 | 0.5729 |
| 900 | 120 | 1.0000 | 1.0000 | 0.6146 |
| 1000 | 120 | 1.0000 | 1.0000 | 0.6771 |
| 1250 | 120 | 1.0000 | 1.0000 | 0.6042 |
| 1500 | 120 | 1.0000 | 1.0000 | 0.6042 |
| 1750 | 120 | 1.0000 | 1.0000 | 0.6354 |
| 2000 | 120 | 1.0000 | 1.0000 | 0.6771 |

## Latest By Technique

| Technique | Samples | SQL Signal | Benign SQL Signal | Technique Hint |
|---|---:|---:|---:|---:|
| benign | 24 | 1.0000 | 1.0000 | n/a |
| boolean_blind | 24 | 1.0000 | n/a | 0.9583 |
| error_based | 24 | 1.0000 | n/a | 0.0000 |
| time_blind | 24 | 1.0000 | n/a | 0.7917 |
| union_based | 24 | 1.0000 | n/a | 0.9583 |

## Interpretation

- High `benign_sql_signal_rate` means the generator is not cleanly separating benign conditioning from SQL-like payload generation.
- Low `technique_hint_rate` means technique conditioning may be weak or the heuristic needs refinement.
- This audit is advisory; use it with manual review before extending adversarial training.
