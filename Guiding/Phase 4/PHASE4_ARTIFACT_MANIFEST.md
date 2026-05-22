# Phase 4 Artifact Manifest

> Cleanup date: 2026-05-22
> Purpose: keep every Phase 4 generated artifact under `Guiding/Phase 4` for later summary.

## Full Run Outputs

Directory:

```text
Guiding/Phase 4/outputs/full/
```

Files:

| File | Rows / note |
|---|---:|
| `phase04_payload_foundation.parquet` | 12,753,953 rows, 23 columns |
| `exact_dedup_map.parquet` | 12,753,951 rows |
| `near_dup_clusters.parquet` | 4,131,974 rows |
| `relex_map.parquet` | 268,272 rows |
| `literal_pools.json` | literal pools |
| `splits_cluster_safe.json` | split summary, cluster leakage = 0 |
| `04_data_foundation_report.md` | full Phase 4 report |

## Logs

Directory:

```text
Guiding/Phase 4/logs/
```

Files:

```text
phase04_full_run.log
phase04_full_run.err.log
phase04_full_progress.json
phase04_sanity_progress.json
```

## Sanity Outputs

Directory:

```text
Guiding/Phase 4/outputs/sanity/
```

Contains previous 10k-row and 1k-row sanity artifacts.

## Path Change Notice

Phase 5 should read Phase 4 full artifacts from:

```text
Guiding/Phase 4/outputs/full/
```

The previous temporary locations were cleaned:

```text
data/phase04/
reports/04_data_foundation_report.md
```
