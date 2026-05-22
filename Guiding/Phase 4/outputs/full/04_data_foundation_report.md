# 04 - Full Data Foundation Report

**Run mode:** full
**Rows processed:** 12,753,953
**Elapsed seconds:** 7667.5

## Lane Distribution

| Lane | Count | % |
|---|---:|---:|
| D | 116 | 0.001% |
| M | 1,469 | 0.012% |
| N | 12,749,451 | 99.965% |
| R | 2,744 | 0.022% |
| X | 173 | 0.001% |

## Deduplication

- Exact unique canonical payloads: `12,753,951`
- Exact duplicate rows: `2`
- Near-duplicate cluster buckets: `4,131,974`
- Delex template keys: `268,272`

## Split Summary

| Split | Rows | Clusters |
|---|---:|---:|
| train | 10,217,352 | 3,304,093 |
| val | 1,265,681 | 414,126 |
| test | 1,021,820 | 330,946 |
| verified_candidate | 249,100 | 82,809 |

Cluster leakage between splits: `0` by deterministic cluster assignment.

## Literal Pools

| Pool | Stored unique values |
|---|---:|
| STR | 20,000 |
| NUM | 20,000 |
| TIME | 259 |
| ID | 20,000 |
| TABLE | 20,000 |
| COMMENT | 20,000 |

## Top Delex Templates

| Count | Template sample |
|---:|---|
| 130,436 | `update __TABLE__ set __ID__ = __STR__ where __ID__ = __STR__` |
| 122,509 | `update __TABLE__ set __ID__ = __STR__ where __ID__ = __STR__ ;` |
| 106,020 | `select * from __TABLE__ where __ID__ = __STR__ or __ID__ = __STR__` |
| 102,702 | `select __STR__ as __ID__ , __ID__ as __ID__ , __ID__ as __ID__ , __ID__ as __ID__ , __ID__ as __ID__ , __ID__ , __ID__ , __ID__ from __TABLE__ af join __TABLE__` |
| 102,015 | `select __ID__ , __ID__ , __ID__ , __ID__ from __TABLE__ a where __ID__ in ( select id from __TABLE__ where __ID__ like __STR__ ) or __ID__ like __STR__` |
| 101,206 | `select __ID__ , __STR__ as __ID__ from __TABLE__ where __ID__ like concat ( __STR__ , __STR__ , __STR__ ) union select __ID__ , __STR__ as __ID__ from __TABLE__` |
| 100,547 | `select __ID__ , __STR__ as __ID__ from __TABLE__ where __ID__ like concat ( __STR__ , __STR__ , __STR__ ) union select __ID__ , __STR__ from __TABLE__ where __I` |
| 99,799 | `select __ID__ as __ID__ , __ID__ , __ID__ ( __ID__ ) as __ID__ , cast ( __ID__ ( __ID__ ) as __ID__ ) as __ID__ from __TABLE__ a join __TABLE__ r on __ID__ = __` |
| 97,681 | `select id , __ID__ , __ID__ from __TABLE__ where __ID__ between __NUM__ and __NUM__` |
| 96,031 | `delete from __TABLE__ where __ID__ = __STR__ ;` |

## Outputs

- `C:\Users\Admin\Documents\GAN_SQLi\data\phase04\phase04_payload_foundation.parquet`
- `C:\Users\Admin\Documents\GAN_SQLi\data\phase04\exact_dedup_map.parquet`
- `C:\Users\Admin\Documents\GAN_SQLi\data\phase04\near_dup_clusters.parquet`
- `C:\Users\Admin\Documents\GAN_SQLi\data\phase04\relex_map.parquet`
- `C:\Users\Admin\Documents\GAN_SQLi\data\phase04\literal_pools.json`
- `C:\Users\Admin\Documents\GAN_SQLi\data\phase04\splits_cluster_safe.json`

## Notes

- `round_trip_status` is `not_evaluated`; DB/WAF execution belongs to later evaluator phases.
- Near-dedup is approximate SimHash-prefix bucketing, chosen to fit 20GB RAM.
- `payload_input` is preserved; canonical/delex columns are derived views.
