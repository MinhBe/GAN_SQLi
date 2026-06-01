# Paper Screening

## Summary

Week 2 screens the seven urgent OCR papers and assigns each paper a phase-1 role. The order is fixed: PayloadsAllTheThings remains the first teacher resource; paper datasets and models are used afterward for comparison, evaluator design, baseline selection, or related-work framing.

## Screening Table

| Paper | Label | Priority | Reproduction Level Candidate |
| --- | --- | --- | --- |
| Le 2024 - GSQLi | `core_sqli_generation` | first_reproduction_target | partial_or_conceptual_until exact code/config are available |
| Lu 2022 - GAN SQLi | `core_sqli_generation` | operator_source_and_conceptual_reproduction | conceptual_if original dataset is not public |
| Demetrio 2020 - WAF-A-MoLE | `waf_evasion_baseline` | strong_baseline_after_evaluator | partial_if code and dataset run locally |
| Chowdhary 2023 - GAN Pentesting | `gan_pentesting_related` | related_work_only | not_prioritized_for_sqli_phase1 |
| Dasari 2025 - Enhancing SQLi Detection | `synthetic_detection_related` | related_work_only | not_prioritized_for_waf_payload_phase1 |
| Agrawal 2024 - GenAI Synthetic | `synthetic_detection_related` | context_only | not_applicable_to_sqli_payload_corpus |
| Attack Model 2012 - Penetration SQLi | `taxonomy_foundation` | taxonomy_support | not_a_model |

## Label Counts

| Label | Papers |
| --- | ---: |
| `core_sqli_generation` | 2 |
| `gan_pentesting_related` | 1 |
| `synthetic_detection_related` | 2 |
| `taxonomy_foundation` | 1 |
| `waf_evasion_baseline` | 1 |

## Teacher Resource Mapping

- PayloadsAllTheThings provides the initial seed corpus, taxonomy, operator families, and baseline definition.
- Le 2024 GSQLi is the first paper reproduction target after evaluator and baseline metrics exist.
- Demetrio 2020 WAF-A-MoLE is the strongest guided mutation baseline candidate.
- Lu 2022 contributes mutation/tamper operator families and likely remains conceptual unless its original dataset can be reconstructed.
- Chowdhary 2023, Dasari 2025, and Agrawal 2024 are related/context papers for phase 1, not primary SQLi payload reproduction targets.
- Attack Model 2012 supports taxonomy and failure labels.

## Current Data Context

- PayloadsAllTheThings rows: 1465
- HttpParams SQLi rows: 10852
- SQLiV3 mirror SQLi rows: 11347
- Combined rows: 23664
- Combined unique hashes: 23082
- Combined duplicate rows by hash: 582

## Outputs

- `GAN/Survey/paper_cards/*.md`
- `GAN/Survey/tables/paper_inventory.csv`
- `GAN/Survey/tables/resource_inventory.csv`
- `GAN/Survey/tables/teacher_vs_paper_mapping.csv`

## Next Step

Proceed to Week 3 dataset/source inventory: consolidate raw/usable/duplicate/invalid counts, source status, license fields, and split rule for leakage control.
