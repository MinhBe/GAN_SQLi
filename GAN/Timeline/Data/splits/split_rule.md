# Split Rule

## Purpose

Week 3 defines the leakage-control rule used before evaluator, baseline metrics, WAF smoke tests, or GSQLi reproduction. The split is over normalized payload hashes, not raw rows, so exact duplicates cannot cross train/validation/test boundaries.

## Current Corpus

- Combined rows before exact de-duplication: 23664
- Unique normalized payload hashes after exact de-duplication: 23082
- Duplicate rows removed from split universe: 582

## Deterministic Assignment

- Split key: `normalized_sha256`
- Hash rule: SHA-256 over `phase1:` plus `normalized_sha256`
- Bucket: first 32 bits of the hash modulo 100
- Train: buckets 0-79
- Validation: buckets 80-89
- Test: buckets 90-99

## Produced Files

- `Timeline/Data/splits/teacher_seed_split_assignments.csv`
- `Timeline/Data/splits/split_summary.csv`
- `Timeline/Data/splits/split_by_source.csv`

## Split Counts

| Split | Unique hashes |
| --- | ---: |
| train | 18516 |
| validation | 2274 |
| test | 2292 |

## Near-Duplicate Policy

Exact duplicates are handled now. Near-duplicate leakage must be handled before model training or final evaluation by adding canonicalization and similarity grouping. Until that grouping exists, reports must describe this split as exact-hash leakage control rather than full semantic leakage control.

Minimum near-duplicate rule for the next implementation step:

- Decode payload strings only inside controlled processing scripts.
- Canonicalize case, whitespace, comments, common URL encodings, and quote variants.
- Build a secondary `canonical_sha256`.
- Keep all rows sharing `canonical_sha256` in one split.
- For fuzzy near-duplicates, use token 3-gram similarity and assign each connected component to one split.

## Guardrails

- Do not train or evaluate a model on raw rows without this split assignment.
- Do not report novelty unless the comparison is against the train split only.
- Do not report WAF ASR/FNR as final if payloads were selected from validation/test after seeing WAF outcomes.
