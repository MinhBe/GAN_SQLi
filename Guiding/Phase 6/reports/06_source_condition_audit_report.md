# 06 - Source Condition Audit

Scope: aggregate audit of Phase 5 parquet sources consumed by Phase 6.
Raw payload text is intentionally omitted.

## Source Summary

| Source | Rows | SQL Signal | Benign SQL Signal | Technique Hint | Mean Confidence |
|---|---:|---:|---:|---:|---:|
| gold.parquet | 1,652,331 | 0.9762 | 0.0012 | 0.8706 | 0.9154 |
| verified_dev.parquet | 165,836 | 0.9761 | 0.0009 | 0.8671 | 0.9170 |
| verified_test.parquet | 166,206 | 0.9764 | 0.0009 | 0.8677 | 0.9169 |

## gold.parquet By Technique

| Technique | Rows | SQL Signal | Benign SQL Signal | Technique Hint |
|---|---:|---:|---:|---:|
| benign | 22,309 | 0.0012 | 0.0012 | n/a |
| boolean_blind | 366,455 | 0.9850 | n/a | 0.7553 |
| error_based | 37,173 | 0.9086 | n/a | 0.4772 |
| time_blind | 515,308 | 0.9891 | n/a | 0.8434 |
| union_based | 711,086 | 0.9964 | n/a | 0.9702 |

## verified_dev.parquet By Technique

| Technique | Rows | SQL Signal | Benign SQL Signal | Technique Hint |
|---|---:|---:|---:|---:|
| benign | 2,250 | 0.0009 | 0.0009 | n/a |
| boolean_blind | 34,621 | 0.9843 | n/a | 0.7361 |
| error_based | 3,320 | 0.8967 | n/a | 0.3238 |
| time_blind | 52,418 | 0.9886 | n/a | 0.8396 |
| union_based | 73,227 | 0.9968 | n/a | 0.9734 |

## verified_test.parquet By Technique

| Technique | Rows | SQL Signal | Benign SQL Signal | Technique Hint |
|---|---:|---:|---:|---:|
| benign | 2,230 | 0.0009 | 0.0009 | n/a |
| boolean_blind | 35,030 | 0.9855 | n/a | 0.7408 |
| error_based | 3,371 | 0.8974 | n/a | 0.3352 |
| time_blind | 52,465 | 0.9888 | n/a | 0.8385 |
| union_based | 73,110 | 0.9966 | n/a | 0.9740 |

## Training Implications

- Gold benign rows: `22,309` (`1.3502%`).
- Gold non-benign rows: `1,630,022` (`98.6498%`).
- Gold benign SQL signal rate: `0.0012`.
- If generated benign samples remain SQL-like while source benign SQL signal is low, the likely issue is class imbalance or weak conditioning rather than dirty gold benign labels.
- For SQLi generation, an attack-only generator is a defensible next branch; for benign-vs-attack generation, use balanced sampling or a separate benign model.
