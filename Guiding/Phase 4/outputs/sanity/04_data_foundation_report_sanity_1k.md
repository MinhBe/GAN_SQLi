# 04 - Full Data Foundation Report

**Run mode:** limit=1000
**Rows processed:** 1,000
**Elapsed seconds:** 0.8

## Lane Distribution

| Lane | Count | % |
|---|---:|---:|
| D | 5 | 0.500% |
| M | 2 | 0.200% |
| N | 988 | 98.800% |
| X | 5 | 0.500% |

## Deduplication

- Exact unique canonical payloads: `1,000`
- Exact duplicate rows: `0`
- Near-duplicate cluster buckets: `910`
- Delex template keys: `679`

## Split Summary

| Split | Rows | Clusters |
|---|---:|---:|
| train | 804 | 735 |
| val | 96 | 90 |
| test | 74 | 63 |
| verified_candidate | 26 | 22 |

Cluster leakage between splits: `0` by deterministic cluster assignment.

## Literal Pools

| Pool | Stored unique values |
|---|---:|
| STR | 282 |
| NUM | 696 |
| TIME | 1 |
| ID | 413 |
| TABLE | 28 |
| COMMENT | 47 |

## Top Delex Templates

| Count | Template sample |
|---:|---|
| 76 | `__NUM__ __STR__ __ID__ __STR__ __ID__` |
| 44 | `select * from __TABLE__ where id = __NUM__ or __STR__ or __NUM__ = __NUM__ __COMMENT__` |
| 26 | `__NUM__ % __STR__ % __STR__` |
| 19 | `select * from __TABLE__ where id = __NUM__ or __NUM__ __COMMENT__` |
| 14 | `__NUM__ __STR__ __ID__ __STR__` |
| 13 | `and __NUM__ = __ID__ ( ( select distinct ( __ID__ ) from ( select distinct ( __ID__ ) , __ID__ as limit from __TABLE__ ) where limit = __NUM__ ) ) and __STR__ =` |
| 13 | `- __NUM__ __STR__ __ID__ __STR__ __ID__` |
| 10 | `select ( case when ( __NUM__ = __NUM__ ) then __NUM__ else __NUM__ * ( select __NUM__ from __TABLE__ ) end ) __COMMENT__` |
| 7 | `__STR__` |
| 7 | `- __NUM__ % __STR__ % __STR__` |

## Outputs

- `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 4\phase04_sanity_progress\phase04_payload_foundation.parquet`
- `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 4\phase04_sanity_progress\exact_dedup_map.parquet`
- `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 4\phase04_sanity_progress\near_dup_clusters.parquet`
- `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 4\phase04_sanity_progress\relex_map.parquet`
- `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 4\phase04_sanity_progress\literal_pools.json`
- `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 4\phase04_sanity_progress\splits_cluster_safe.json`

## Notes

- `round_trip_status` is `not_evaluated`; DB/WAF execution belongs to later evaluator phases.
- Near-dedup is approximate SimHash-prefix bucketing, chosen to fit 20GB RAM.
- `payload_input` is preserved; canonical/delex columns are derived views.
