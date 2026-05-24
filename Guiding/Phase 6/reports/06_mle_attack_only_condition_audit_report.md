# 06 - MLE Attack-Only Condition Audit

Scope: aggregate heuristic audit of generated sample JSONL files.
Raw generated texts are intentionally omitted from this report.

## Latest Sample File

- Step: `1000`
- Samples: `120`
- SQL signal rate: `1.0000`
- Benign SQL signal rate: `0.0000`
- Technique hint rate: `0.6250`

## Step Trend

| Step | Samples | SQL Signal | Benign SQL Signal | Technique Hint |
|---:|---:|---:|---:|---:|
| 100 | 120 | 0.9917 | 0.0000 | 0.2500 |
| 200 | 120 | 0.9917 | 0.0000 | 0.2500 |
| 300 | 120 | 1.0000 | 0.0000 | 0.2500 |
| 400 | 120 | 0.9667 | 0.0000 | 0.2750 |
| 500 | 120 | 1.0000 | 0.0000 | 0.6417 |
| 600 | 120 | 1.0000 | 0.0000 | 0.3333 |
| 700 | 120 | 1.0000 | 0.0000 | 0.3250 |
| 800 | 120 | 1.0000 | 0.0000 | 0.3333 |
| 900 | 120 | 1.0000 | 0.0000 | 0.5833 |
| 1000 | 120 | 1.0000 | 0.0000 | 0.6250 |

## Latest By Technique

| Technique | Samples | SQL Signal | Benign SQL Signal | Technique Hint |
|---|---:|---:|---:|---:|
| boolean_blind | 30 | 1.0000 | n/a | 0.8333 |
| error_based | 30 | 1.0000 | n/a | 0.0000 |
| time_blind | 30 | 1.0000 | n/a | 0.7333 |
| union_based | 30 | 1.0000 | n/a | 0.9333 |

## Interpretation

- High `benign_sql_signal_rate` means the generator is not cleanly separating benign conditioning from SQL-like payload generation.
- Low `technique_hint_rate` means technique conditioning may be weak or the heuristic needs refinement.
- This audit is advisory; use it with manual review before extending adversarial training.
