# 08 - Delex Cluster Split Report

Rows sharing a normalized delex-template hash are assigned to the same split.

- Output dir: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 8\outputs\delex_cluster_split`
- Percentages: train=80, dev=10, test=10

| Split | Rows | Unique Templates | Duplicate Template Row Rate |
|---|---:|---:|---:|
| train | 1,561,364 | 62,208 | 0.9602 |
| dev | 150,694 | 7,707 | 0.9489 |
| test | 272,315 | 7,889 | 0.9710 |

## Template Overlaps

- train/dev: `0`
- train/test: `0`
- dev/test: `0`

Any non-zero overlap here is a bug in the split builder or hash assignment.
