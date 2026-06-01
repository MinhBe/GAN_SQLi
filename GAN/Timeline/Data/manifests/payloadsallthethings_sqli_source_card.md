# PayloadsAllTheThings SQLi Source Card

- Source URL: `https://github.com/swisskyrepo/PayloadsAllTheThings`
- SQL Injection README URL: `https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/README.md`
- Raw source path: `GAN/Data/raw/payloadsallthethings`
- SQL Injection README path: `GAN/Data/raw/payloadsallthethings/SQL Injection/README.md`
- Intruder source path: `GAN/Data/raw/payloadsallthethings/SQL Injection/Intruder`
- Downloaded commit/hash: `e961fef231d8327bae83b563fab50aec2e6b77c0`
- Retrieval mode: online git clone
- License: MIT License, from `GAN/Data/raw/payloadsallthethings/LICENSE`
- Role in phase 1: teacher-provided practical seed/taxonomy/operator source
- Paper-dataset status: replacement seed corpus, not the original dataset of GSQLi or other papers
- Intruder file count: 21
- Nonblank seed row count: 1465
- Unique payload hashes: 1359
- Duplicate rows by payload hash: 106

## Scope

PayloadsAllTheThings SQL Injection is used first to establish practical SQLi taxonomy, seed inventory, operator families, and a minimal rule baseline. Markdown reports intentionally keep payload details out of the narrative and report only taxonomy and aggregate statistics.

## Taxonomy Presence

| Section | Present | Use |
| --- | --- | --- |
| Tools | yes | Tool references and baseline context |
| Entry Point Detection | yes | Detection/fuzz seed group |
| DBMS Identification | yes | DBMS-specific labels and evaluator taxonomy |
| Authentication Bypass | yes | Auth-bypass seed group |
| UNION Based Injection | yes | Union-based seed group |
| Error Based Injection | yes | Error-based seed group |
| Blind Injection | yes | Boolean/blind seed group |
| Time Based Injection | yes | Time-delay seed group |
| Out of Band (OAST) | yes | Taxonomy only until controlled testbed exists |
| Stacked Based Injection | yes | Piggybacked/stacked query label |
| Polyglot Injection | yes | Polyglot label |
| Routed Injection | yes | Taxonomy only |
| Second Order SQL Injection | yes | Taxonomy only |
| PDO Prepared Statements | yes | Defensive context |
| Generic WAF Bypass | yes | Operator family source, not report payload detail |
| Labs | yes | Safe-practice references |

## Operator Families For Baseline Planning

| Operator family | Phase 1 use |
| --- | --- |
| Keyword and case variation | Mutation baseline candidate |
| Whitespace and separator variation | Mutation baseline candidate |
| Comment insertion | Mutation baseline candidate |
| Encoding and escaping | Evaluator-dependent candidate |
| DBMS-specific syntax variation | Taxonomy and controlled mutation candidate |
| Boolean/logical variation | Mutation baseline candidate |
| Time/error/union family selection | Category-stratified sampling |

## Risks

| Risk | Handling |
| --- | --- |
| Duplicate or near-duplicate seeds | Track normalized hashes and duplicate counts before split |
| Dual-use payload content | Keep detailed payload strings in local processed CSV only, encoded in CSV artifacts |
| Report leakage | Publish only taxonomy, counts, hashes, source cards, and method summaries |
| Paper mismatch | Mark as teacher seed/replacement, not as a paper-original dataset |
