# 06 - Token Shard Preparation Report

**Run mode:** full
**Cache directory:** `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 6\cache\token_shards_attack_only`
**Text column:** `payload_delex_v5`
**Condition column:** `technique_primary`
**Max length:** `128`
**Vocab size:** `1,584`
**Train rows for vocab:** `1,630,022`

## Split Shards

| Split | Rows | Shards |
|---|---:|---:|
| train | 1,630,022 | 33 |
| dev | 163,586 | 4 |
| test | 163,976 | 4 |

## Training Scope

- Train source is `gold.parquet` by default.
- `needs_ai=True`, non-gold, review queue, unknown-quality, silver, and bronze rows are not part of first-round train shards.
- Shards are fixed-length token tensors so training can stream from disk instead of loading full parquet into RAM.
