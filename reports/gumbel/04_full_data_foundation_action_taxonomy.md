# 04 Full Data Foundation + Action Taxonomy

## Scope

This is the Gumbel namespace foundation under `data/gumbel/full`.
It does not reuse `Guiding/Phase 5` as a Gumbel phase. External artifacts may be
used only when explicitly passed as `--input`.

## Gate

- Result: `FULL_FOUNDATION_READY`
- Reason: Gumbel full foundation has train/dev/test payloads and enough non-literal action families.

## Rows

- Action rows: 268479
- Unique payloads: 39000
- Cluster/split policy: deterministic hash over `payload_id`
- Split leakage by payload_id: `0`

## Split Payload Counts

| Split | Unique payloads |
| --- | ---: |
| dev | 3898 |
| test | 3019 |
| train | 31282 |
| verified_candidate | 801 |

## Action Families

| Family | Rows |
| --- | ---: |
| keyword_variant | 63578 |
| encoding | 54832 |
| operator | 44596 |
| whitespace | 34309 |
| tamper_candidate | 31864 |
| comment | 23187 |
| function | 11452 |
| none | 4661 |
