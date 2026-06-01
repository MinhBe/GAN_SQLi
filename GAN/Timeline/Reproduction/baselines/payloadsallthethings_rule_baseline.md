# PayloadsAllTheThings Rule Baseline

- Source URL: `https://github.com/swisskyrepo/PayloadsAllTheThings`
- Downloaded commit/hash: `e961fef231d8327bae83b563fab50aec2e6b77c0`
- Input path: `GAN/Data/raw/payloadsallthethings/SQL Injection/Intruder`
- Normalized output: `GAN/Data/processed/teacher_seed_sqli_normalized.csv`
- Status: baseline definition only; not yet evaluated through the common evaluator

## Baseline Scope

- Reads online-downloaded Intruder text files.
- Uses source filename and README taxonomy to assign coarse labels.
- Trims leading and trailing whitespace before hashing.
- Reports aggregate counts only in markdown artifacts.

## Aggregate Counts

- Source files: 21
- Normalized rows: 1465
- Unique payload hashes: 1359
- Duplicate rows by payload hash: 106

## Minimal Rule/Mutation Plan

| Baseline component | Decision |
| --- | --- |
| Template/rule sampling | Sample by taxonomy category and DBMS label |
| Dedup rule | Exact normalized SHA-256 first; near-duplicate later in split rule |
| Mutation operator families | Case, whitespace, comment, encoding, logical variation, DBMS syntax variation |
| Evaluator dependency | Validity, uniqueness, novelty, diversity, WAF allow/block, failure labels |
| Reporting rule | Metrics only; no detailed payload strings in reports |

## Acceptance For Week 1

- Source card exists with license, scope, risks, and taxonomy.
- Seed inventory and normalized CSV exist.
- Baseline definition exists and is ready for Week 4 evaluator integration.
