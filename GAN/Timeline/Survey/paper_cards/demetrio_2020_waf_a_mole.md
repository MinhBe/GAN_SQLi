# Demetrio 2020 - WAF-A-MoLE

## Identity

- Paper id: `demetrio_2020_waf_a_mole`
- Source file id: `Demetrio_2020_WAF_A_MoLE.md`
- Classification label: `waf_evasion_baseline`
- Phase 1 role: Strong guided mutation baseline for WAF/ML-WAF evasion experiments.

## Extraction

| Field | Value |
| --- | --- |
| Dataset/source mentioned | wafamole-dataset; generated benign SQL queries and injection queries |
| Code/testbed mentioned | WAF-A-MoLE; WAF-Brain; ModSecurity CRS; SQLMap; MariaDB randgen |
| Method/model | Guided syntactic mutation that tries to reduce WAF classifier confidence while preserving malicious semantics. |
| Metrics | Accuracy, recall, precision, evasion success over ML-based WAFs. |
| Reproduction priority | `strong_baseline_after_evaluator` |
| Reproduction level candidate | `partial_if code and dataset run locally` |

## Relation To Teacher Resource

Complements PayloadsAllTheThings by providing a guided mutation baseline rather than only a seed taxonomy.

## Phase 1 Action

Smoke test or write failure report after the common evaluator exists.
