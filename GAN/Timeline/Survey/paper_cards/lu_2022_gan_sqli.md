# Lu 2022 - GAN SQLi

## Identity

- Paper id: `lu_2022_gan_sqli`
- Source file id: `Lu_2022_GAN_SQLi.md`
- Classification label: `core_sqli_generation`
- Phase 1 role: Secondary core paper for GAN/GA style SQLi generation and mutation operators.

## Extraction

| Field | Value |
| --- | --- |
| Dataset/source mentioned | CVE, CNVD, exploit-db payload collection described by the paper |
| Code/testbed mentioned | SQLParse; phpstudy2018; sqli-lab Range; SafeDog V4.0 |
| Method/model | GAN/improved DCGAN/Wasserstein-inspired generation plus mutation variants. |
| Metrics | Syntax usability, WAF interception behavior, and generation quality described by the paper. |
| Reproduction priority | `operator_source_and_conceptual_reproduction` |
| Reproduction level candidate | `conceptual_if original dataset is not public` |

## Relation To Teacher Resource

Adds mutation/tamper ideas to the PayloadsAllTheThings baseline.

## Phase 1 Action

Extract operator families for the mutation baseline after evaluator is available.
