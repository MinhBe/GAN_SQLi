# 08 - Delex Cluster Split Report

Rows sharing a normalized delex-template hash are assigned to the same split.

- Output dir: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\delex_cluster_split_smoke`
- Percentages: train=80, dev=10, test=10

| Split | Rows | Unique Templates | Duplicate Template Row Rate |
|---|---:|---:|---:|
| train | 122,076 | 19,778 | 0.8380 |
| dev | 12,847 | 2,526 | 0.8034 |
| test | 15,077 | 2,610 | 0.8269 |

## Template Overlaps

- train/dev: `0`
- train/test: `0`
- dev/test: `0`

Any non-zero overlap here is a bug in the split builder or hash assignment.
