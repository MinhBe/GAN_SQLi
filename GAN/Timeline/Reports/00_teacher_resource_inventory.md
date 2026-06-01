# Teacher Resource Inventory

## Source

- Online source URL: `https://github.com/swisskyrepo/PayloadsAllTheThings`
- SQL Injection README URL: `https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/README.md`
- Raw source path: `GAN/Data/raw/payloadsallthethings`
- Downloaded commit/hash: `e961fef231d8327bae83b563fab50aec2e6b77c0`
- License: MIT License
- Role: teacher-provided seed/taxonomy/operator source for phase 1
- Dataset status: practical replacement seed corpus, not a paper-original dataset

## Generated Artifacts

- `GAN/Data/manifests/payloadsallthethings_sqli_source_card.md`
- `GAN/Data/manifests/teacher_seed_inventory.csv`
- `GAN/Data/processed/teacher_seed_sqli_normalized.csv`
- `GAN/Reproduction/baselines/payloadsallthethings_rule_baseline.md`

## Seed Statistics

- Intruder source files: 21
- Nonblank normalized rows: 1465
- Unique payload hashes: 1359
- Duplicate rows by payload hash: 106

## Taxonomy Coverage

| Group | Status | Purpose |
| --- | --- | --- |
| Entry point detection | covered | Initial fuzz/detection seeds |
| DBMS identification | covered | DBMS-specific labels |
| Authentication bypass | covered | Auth-bypass category |
| UNION based | covered | Union category |
| Error based | covered | Error category |
| Blind and boolean based | covered | Blind category |
| Time based | covered | Time category |
| OAST | taxonomy-only | Deferred until controlled evaluator |
| Stacked/piggybacked | covered | Stacked query category |
| Polyglot | covered | Polyglot category |
| Routed and second-order | taxonomy-only | Deferred until evaluator supports scenario labels |
| Generic WAF bypass | operator-only | Mutation planning, no payload detail in report |
| Labs | reference-only | Safe practice context |

## Baseline Readiness

The Week 1 baseline is a rule/template baseline definition, not an evaluated baseline. It is ready to feed the Week 4 evaluator once split rules and WAF smoke tests exist.

## Risk Notes

- Detailed payload strings are not printed in reports.
- The processed CSV stores strings in encoded form plus hashes for reproducibility.
- Duplicate tracking is exact-hash based at this stage; near-duplicate handling belongs to the Week 3 split rule.
