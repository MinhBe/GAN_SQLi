from __future__ import annotations

import csv
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


GAN = Path("GAN")
REPORTS = GAN / "Reports"
SURVEY = GAN / "Survey"
PAPER_CARDS = SURVEY / "paper_cards"
TABLES = SURVEY / "tables"
MANIFESTS = GAN / "Data" / "manifests"
PROCESSED = GAN / "Data" / "processed"
BASELINES = GAN / "Reproduction" / "baselines"
RECOVERY = GAN / "RECOVERY.md"

PATT_COMMIT = "e961fef231d8327bae83b563fab50aec2e6b77c0"
HTTPPARAMS_COMMIT = "926670a710283f87c05b554680facf3f9530548c"
SQLIV3_COMMIT = "486e182221e48d2cadab63edc217dfd46eb67405"

PAPER_ROOT = Path.home() / "Documents" / "GAN_SQLi" / "GAN" / "Paper" / "Analyst" / "Cap thiet"

PATT_URL = "https://github.com/swisskyrepo/PayloadsAllTheThings"
PATT_README_URL = "https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/README.md"


PAPERS = [
    {
        "id": "le_2024_gsqli",
        "file": "Le_2024_GSQLi.md",
        "title": "GSQLi: A GAN-based Approach for Adversarial SQL Injection Sample Generation against WAF",
        "short_title": "Le 2024 - GSQLi",
        "label": "core_sqli_generation",
        "role": "Core paper for SQLi payload mutation against WAF and ML detectors.",
        "datasets": "HttpParams Dataset; SSHS/Kaggle SQL Injection Dataset",
        "code_or_testbed": "RNN, GRU, BiLSTM detectors; ModSecurity; OWASP CRS",
        "method": "Token parser, mutation vector, GAN generator, payload transformer, attack classifier, discriminator/evaluator.",
        "metrics": "TPR/FNR in paper; project should add validity, uniqueness, novelty, diversity, duplicate rate, and failure labels.",
        "priority": "first_reproduction_target",
        "reproduction_level": "partial_or_conceptual_until exact code/config are available",
        "relation": "Uses paper datasets for comparison after the teacher seed corpus has been built from PayloadsAllTheThings.",
        "phase1_action": "Use as the main GSQLi reproduction plan after evaluator and baselines exist.",
        "status": "screened",
    },
    {
        "id": "lu_2022_gan_sqli",
        "file": "Lu_2022_GAN_SQLi.md",
        "title": "GAN-based SQL Injection Payload Generation and Mutation",
        "short_title": "Lu 2022 - GAN SQLi",
        "label": "core_sqli_generation",
        "role": "Secondary core paper for GAN/GA style SQLi generation and mutation operators.",
        "datasets": "CVE, CNVD, exploit-db payload collection described by the paper",
        "code_or_testbed": "SQLParse; phpstudy2018; sqli-lab Range; SafeDog V4.0",
        "method": "GAN/improved DCGAN/Wasserstein-inspired generation plus mutation variants.",
        "metrics": "Syntax usability, WAF interception behavior, and generation quality described by the paper.",
        "priority": "operator_source_and_conceptual_reproduction",
        "reproduction_level": "conceptual_if original dataset is not public",
        "relation": "Adds mutation/tamper ideas to the PayloadsAllTheThings baseline.",
        "phase1_action": "Extract operator families for the mutation baseline after evaluator is available.",
        "status": "screened",
    },
    {
        "id": "demetrio_2020_waf_a_mole",
        "file": "Demetrio_2020_WAF_A_MoLE.md",
        "title": "WAF-A-MoLE: Evading Web Application Firewalls through Adversarial Machine Learning",
        "short_title": "Demetrio 2020 - WAF-A-MoLE",
        "label": "waf_evasion_baseline",
        "role": "Strong guided mutation baseline for WAF/ML-WAF evasion experiments.",
        "datasets": "wafamole-dataset; generated benign SQL queries and injection queries",
        "code_or_testbed": "WAF-A-MoLE; WAF-Brain; ModSecurity CRS; SQLMap; MariaDB randgen",
        "method": "Guided syntactic mutation that tries to reduce WAF classifier confidence while preserving malicious semantics.",
        "metrics": "Accuracy, recall, precision, evasion success over ML-based WAFs.",
        "priority": "strong_baseline_after_evaluator",
        "reproduction_level": "partial_if code and dataset run locally",
        "relation": "Complements PayloadsAllTheThings by providing a guided mutation baseline rather than only a seed taxonomy.",
        "phase1_action": "Smoke test or write failure report after the common evaluator exists.",
        "status": "screened",
    },
    {
        "id": "chowdhary_2023_gan_pentesting",
        "file": "Chowdhary_2023_GAN_Pentesting.md",
        "title": "GAN-based Penetration Testing for Web Application Firewalls",
        "short_title": "Chowdhary 2023 - GAN Pentesting",
        "label": "gan_pentesting_related",
        "role": "Related work for conditional sequence GAN and WAF testing context.",
        "datasets": "PayloadBox XSS payload list",
        "code_or_testbed": "ModSecurity; AWS WAF; commercial WAF rules",
        "method": "Conditional GAN style payload generation for WAF testing.",
        "metrics": "Bypass and detection behavior reported for web payload experiments.",
        "priority": "related_work_only",
        "reproduction_level": "not_prioritized_for_sqli_phase1",
        "relation": "Useful analogy for sequence GAN difficulty, but not a SQLi corpus source.",
        "phase1_action": "Use only for literature framing unless phase 2 expands beyond SQLi.",
        "status": "screened",
    },
    {
        "id": "dasari_2025_enhancing_sqli",
        "file": "Dasari_2025_Enhancing_SQLi.md",
        "title": "Enhancing SQL Injection Detection with Synthetic Data",
        "short_title": "Dasari 2025 - Enhancing SQLi Detection",
        "label": "synthetic_detection_related",
        "role": "Related work for synthetic SQLi detection augmentation.",
        "datasets": "Kaggle sqli.csv; Modified SQL Dataset.csv",
        "code_or_testbed": "XGBoost, LightGBM, Random Forest, KNN, SVM style detector comparison",
        "method": "VAE, U-Net, CWGAN-GP, pseudo-labeling, and classical detection models.",
        "metrics": "Accuracy, precision, recall, F1, MSE, R2, PCA-style synthetic quality checks.",
        "priority": "related_work_only",
        "reproduction_level": "not_prioritized_for_waf_payload_phase1",
        "relation": "Detection augmentation focus, not primary WAF payload evasion.",
        "phase1_action": "Mention as related work and avoid mixing its tabular/query augmentation objective into GSQLi reproduction.",
        "status": "screened",
    },
    {
        "id": "agrawal_2024_genai_synthetic",
        "file": "Agrawal_2024_GenAI_Synthetic.md",
        "title": "Generative AI for Synthetic Attack Detection Using an Imbalanced Dataset",
        "short_title": "Agrawal 2024 - GenAI Synthetic",
        "label": "synthetic_detection_related",
        "role": "Context paper for synthetic cyber attack data under class imbalance.",
        "datasets": "CICIDS2017; IDS web attack and brute force minority classes",
        "code_or_testbed": "CTGAN; Random Forest; XGBoost",
        "method": "CTGAN augmentation of minority IDS classes followed by classifier training.",
        "metrics": "Accuracy, precision, recall, F1, and class-specific recall.",
        "priority": "context_only",
        "reproduction_level": "not_applicable_to_sqli_payload_corpus",
        "relation": "Supports the motivation for synthetic data, but should not be used as a SQLi payload corpus.",
        "phase1_action": "Use as background when discussing class imbalance and synthetic data limits.",
        "status": "screened",
    },
    {
        "id": "attack_model_2012_penetration_sqli",
        "file": "Attack_Model_2012_Penetration_SQLi.md",
        "title": "Attack Model for Penetration Testing SQL Injection",
        "short_title": "Attack Model 2012 - Penetration SQLi",
        "label": "taxonomy_foundation",
        "role": "Taxonomy foundation for SQLi intent and failure analysis.",
        "datasets": "No public payload dataset used as a corpus source",
        "code_or_testbed": "Taxonomy reference only",
        "method": "Classifies SQLi attack intent and families such as tautology, illegal query, piggybacked query, and first/second-order injection.",
        "metrics": "Not a model metric paper; useful for taxonomy and failure labels.",
        "priority": "taxonomy_support",
        "reproduction_level": "not_a_model",
        "relation": "Strengthens the taxonomy derived from PayloadsAllTheThings.",
        "phase1_action": "Use for evaluator failure labels and taxonomy normalization.",
        "status": "screened",
    },
]


RESOURCES = [
    ("PayloadsAllTheThings SQL Injection", "teacher_seed", PATT_URL, "ingested", "Seed/taxonomy first source"),
    ("HttpParams Dataset", "paper_dataset", "https://github.com/Morzeux/HttpParamsDataset", "ingested", "Le 2024 train/eval comparison source"),
    ("SSHS/Kaggle SQL Injection Dataset", "paper_dataset", "https://www.kaggle.com/syedsaqlainhussain/sql-injection-dataset", "mirrored_via_sqliv3", "Le 2024 comparison source"),
    ("SQLiV3 mirror", "paper_dataset_mirror", "https://github.com/nidnogg/sqliv5-dataset", "ingested", "Online mirror used for SSHS/SQLiV3 records"),
    ("WAF-A-MoLE dataset", "baseline_dataset", "https://github.com/blindusername/wafamole-dataset", "todo", "Demetrio 2020 ML-WAF baseline source"),
    ("SQLMap", "operator_source", "https://github.com/sqlmapproject/sqlmap", "todo", "Mutation/tamper operator reference"),
    ("SecLists", "reference_payloads", "https://github.com/danielmiessler/SecLists", "todo", "Optional payload reference, not mixed into corpus yet"),
    ("OWASP CRS", "waf_rules", "https://github.com/coreruleset/coreruleset", "todo", "Primary WAF ruleset for smoke test"),
    ("ModSecurity", "waf_engine", "https://github.com/owasp-modsecurity/ModSecurity", "todo", "Primary WAF engine"),
    ("Coraza", "waf_engine_fallback", "https://github.com/corazawaf/coraza", "todo", "Fallback WAF engine if ModSecurity is slow"),
]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def count_rows(path: Path) -> int:
    return sum(1 for _ in read_csv(path))


def source_stats() -> dict[str, int]:
    teacher = read_csv(PROCESSED / "teacher_seed_sqli_normalized.csv")
    httpparams = read_csv(PROCESSED / "httpparams_sqli_normalized.csv")
    sqliv3 = read_csv(PROCESSED / "sqliv3_sqli_normalized.csv")
    combined = read_csv(PROCESSED / "teacher_seed_sqli_normalized_combined.csv")
    combined_hashes = Counter(row["normalized_sha256"] for row in combined)
    teacher_hashes = Counter(row["normalized_sha256"] for row in teacher)
    return {
        "patt_rows": len(teacher),
        "patt_unique": len(teacher_hashes),
        "patt_duplicates": sum(v - 1 for v in teacher_hashes.values() if v > 1),
        "httpparams_rows": len(httpparams),
        "sqliv3_rows": len(sqliv3),
        "combined_rows": len(combined),
        "combined_unique": len(combined_hashes),
        "combined_duplicates": sum(v - 1 for v in combined_hashes.values() if v > 1),
    }


def write_week1(stats: dict[str, int]) -> None:
    source_card = f"""# PayloadsAllTheThings SQLi Source Card

- Source URL: `{PATT_URL}`
- SQL Injection README URL: `{PATT_README_URL}`
- Raw source path: `GAN/Data/raw/payloadsallthethings`
- SQL Injection README path: `GAN/Data/raw/payloadsallthethings/SQL Injection/README.md`
- Intruder source path: `GAN/Data/raw/payloadsallthethings/SQL Injection/Intruder`
- Downloaded commit/hash: `{PATT_COMMIT}`
- Retrieval mode: online git clone
- License: MIT License, from `GAN/Data/raw/payloadsallthethings/LICENSE`
- Role in phase 1: teacher-provided practical seed/taxonomy/operator source
- Paper-dataset status: replacement seed corpus, not the original dataset of GSQLi or other papers
- Intruder file count: 21
- Nonblank seed row count: {stats['patt_rows']}
- Unique payload hashes: {stats['patt_unique']}
- Duplicate rows by payload hash: {stats['patt_duplicates']}

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
"""
    (MANIFESTS / "payloadsallthethings_sqli_source_card.md").write_text(source_card, encoding="utf-8")

    report = f"""# Teacher Resource Inventory

## Source

- Online source URL: `{PATT_URL}`
- SQL Injection README URL: `{PATT_README_URL}`
- Raw source path: `GAN/Data/raw/payloadsallthethings`
- Downloaded commit/hash: `{PATT_COMMIT}`
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
- Nonblank normalized rows: {stats['patt_rows']}
- Unique payload hashes: {stats['patt_unique']}
- Duplicate rows by payload hash: {stats['patt_duplicates']}

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
"""
    (REPORTS / "00_teacher_resource_inventory.md").write_text(report, encoding="utf-8")

    baseline = f"""# PayloadsAllTheThings Rule Baseline

- Source URL: `{PATT_URL}`
- Downloaded commit/hash: `{PATT_COMMIT}`
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
- Normalized rows: {stats['patt_rows']}
- Unique payload hashes: {stats['patt_unique']}
- Duplicate rows by payload hash: {stats['patt_duplicates']}

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
"""
    (BASELINES / "payloadsallthethings_rule_baseline.md").write_text(baseline, encoding="utf-8")


def card_text(paper: dict[str, str]) -> str:
    return f"""# {paper['short_title']}

## Identity

- Paper id: `{paper['id']}`
- Source file id: `{paper['file']}`
- Classification label: `{paper['label']}`
- Phase 1 role: {paper['role']}

## Extraction

| Field | Value |
| --- | --- |
| Dataset/source mentioned | {paper['datasets']} |
| Code/testbed mentioned | {paper['code_or_testbed']} |
| Method/model | {paper['method']} |
| Metrics | {paper['metrics']} |
| Reproduction priority | `{paper['priority']}` |
| Reproduction level candidate | `{paper['reproduction_level']}` |

## Relation To Teacher Resource

{paper['relation']}

## Phase 1 Action

{paper['phase1_action']}
"""


def write_week2(stats: dict[str, int]) -> None:
    PAPER_CARDS.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    for paper in PAPERS:
        (PAPER_CARDS / f"{paper['id']}.md").write_text(card_text(paper), encoding="utf-8")

    write_csv(
        TABLES / "paper_inventory.csv",
        [
            {
                "paper_id": p["id"],
                "short_title": p["short_title"],
                "classification_label": p["label"],
                "role": p["role"],
                "datasets_or_sources": p["datasets"],
                "code_or_testbed": p["code_or_testbed"],
                "metrics": p["metrics"],
                "priority": p["priority"],
                "reproduction_level_candidate": p["reproduction_level"],
                "status": p["status"],
            }
            for p in PAPERS
        ],
        [
            "paper_id",
            "short_title",
            "classification_label",
            "role",
            "datasets_or_sources",
            "code_or_testbed",
            "metrics",
            "priority",
            "reproduction_level_candidate",
            "status",
        ],
    )

    write_csv(
        TABLES / "resource_inventory.csv",
        [
            {
                "resource": name,
                "resource_type": kind,
                "url": url,
                "status": status,
                "phase1_use": use,
            }
            for name, kind, url, status, use in RESOURCES
        ],
        ["resource", "resource_type", "url", "status", "phase1_use"],
    )

    write_csv(
        TABLES / "teacher_vs_paper_mapping.csv",
        [
            {
                "paper_id": p["id"],
                "teacher_first_decision": "PayloadsAllTheThings first",
                "overlap_with_teacher": p["relation"],
                "phase1_decision": p["phase1_action"],
                "run_order": {
                    "le_2024_gsqli": "after evaluator and baselines",
                    "lu_2022_gan_sqli": "after evaluator as mutation baseline support",
                    "demetrio_2020_waf_a_mole": "after evaluator as strong baseline",
                    "attack_model_2012_penetration_sqli": "use during taxonomy/evaluator design",
                }.get(p["id"], "related work only in phase 1"),
            }
            for p in PAPERS
        ],
        ["paper_id", "teacher_first_decision", "overlap_with_teacher", "phase1_decision", "run_order"],
    )

    label_counts = Counter(p["label"] for p in PAPERS)
    paper_rows = "\n".join(
        f"| {p['short_title']} | `{p['label']}` | {p['priority']} | {p['reproduction_level']} |"
        for p in PAPERS
    )
    label_rows = "\n".join(f"| `{label}` | {count} |" for label, count in sorted(label_counts.items()))
    report = f"""# Paper Screening

## Summary

Week 2 screens the seven urgent OCR papers and assigns each paper a phase-1 role. The order is fixed: PayloadsAllTheThings remains the first teacher resource; paper datasets and models are used afterward for comparison, evaluator design, baseline selection, or related-work framing.

## Screening Table

| Paper | Label | Priority | Reproduction Level Candidate |
| --- | --- | --- | --- |
{paper_rows}

## Label Counts

| Label | Papers |
| --- | ---: |
{label_rows}

## Teacher Resource Mapping

- PayloadsAllTheThings provides the initial seed corpus, taxonomy, operator families, and baseline definition.
- Le 2024 GSQLi is the first paper reproduction target after evaluator and baseline metrics exist.
- Demetrio 2020 WAF-A-MoLE is the strongest guided mutation baseline candidate.
- Lu 2022 contributes mutation/tamper operator families and likely remains conceptual unless its original dataset can be reconstructed.
- Chowdhary 2023, Dasari 2025, and Agrawal 2024 are related/context papers for phase 1, not primary SQLi payload reproduction targets.
- Attack Model 2012 supports taxonomy and failure labels.

## Current Data Context

- PayloadsAllTheThings rows: {stats['patt_rows']}
- HttpParams SQLi rows: {stats['httpparams_rows']}
- SQLiV3 mirror SQLi rows: {stats['sqliv3_rows']}
- Combined rows: {stats['combined_rows']}
- Combined unique hashes: {stats['combined_unique']}
- Combined duplicate rows by hash: {stats['combined_duplicates']}

## Outputs

- `GAN/Survey/paper_cards/*.md`
- `GAN/Survey/tables/paper_inventory.csv`
- `GAN/Survey/tables/resource_inventory.csv`
- `GAN/Survey/tables/teacher_vs_paper_mapping.csv`

## Next Step

Proceed to Week 3 dataset/source inventory: consolidate raw/usable/duplicate/invalid counts, source status, license fields, and split rule for leakage control.
"""
    (REPORTS / "01_paper_screening.md").write_text(report, encoding="utf-8")


def update_recovery(stats: dict[str, int]) -> None:
    timestamp = datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()
    text = f"""# Recovery

- Current phase: Week 2 paper screening completed
- Last completed step: Week 1 and Week 2 artifact verification
- Next exact step: Complete Week 3 dataset/source inventory and split rule under `GAN`
- Updated artifacts:
  - `GAN/RECOVERY.md`
  - `GAN/Reports/00_teacher_resource_inventory.md`
  - `GAN/Reports/01_paper_screening.md`
  - `GAN/Data/manifests/payloadsallthethings_sqli_source_card.md`
  - `GAN/Reproduction/baselines/payloadsallthethings_rule_baseline.md`
  - `GAN/Survey/paper_cards`
  - `GAN/Survey/tables/paper_inventory.csv`
  - `GAN/Survey/tables/resource_inventory.csv`
  - `GAN/Survey/tables/teacher_vs_paper_mapping.csv`
  - `GAN/Data/raw/payloadsallthethings`
  - `GAN/Data/raw/httpparamsdataset`
  - `GAN/Data/raw/sqliv5-dataset`
  - `GAN/Data/processed/teacher_seed_sqli_normalized_combined.csv`
- Online source URL: `{PATT_URL}`
- Primary SQL Injection README URL: `{PATT_README_URL}`
- Downloaded commit/hash: `{PATT_COMMIT}`
- Step 2 online source URL: `https://github.com/Morzeux/HttpParamsDataset`
- Step 2 downloaded commit/hash: `{HTTPPARAMS_COMMIT}`
- Step 3 online source URL: `https://github.com/nidnogg/sqliv5-dataset`
- Step 3 downloaded commit/hash: `{SQLIV3_COMMIT}`
- Paper screening source: local OCR paper text, summarized into `GAN/Survey` without local absolute paths
- Command log summary:
  - Completed Week 1 teacher resource source card, taxonomy, risk notes, and baseline definition.
  - Completed Week 2 screening for seven urgent papers.
  - Generated seven paper cards and three survey tables under `GAN/Survey`.
  - Verified generated artifact counts and path-marker scan.
- Row counts:
  - PayloadsAllTheThings normalized nonblank rows: {stats['patt_rows']}
  - PayloadsAllTheThings unique payload hashes: {stats['patt_unique']}
  - HttpParams SQLi normalized rows: {stats['httpparams_rows']}
  - SQLiV3 mirror SQLi normalized rows: {stats['sqliv3_rows']}
  - Combined normalized rows: {stats['combined_rows']}
  - Combined unique payload hashes: {stats['combined_unique']}
  - Paper cards: 7
  - Paper inventory rows: 7
  - Teacher-paper mapping rows: 7
- Duplicate counts:
  - PayloadsAllTheThings duplicate rows by payload hash: {stats['patt_duplicates']}
  - Combined duplicate rows by payload hash: {stats['combined_duplicates']}
- Blockers: none
- Last updated: `{timestamp}`
"""
    RECOVERY.write_text(text, encoding="utf-8")


def main() -> None:
    for path in (REPORTS, PAPER_CARDS, TABLES, MANIFESTS, BASELINES):
        path.mkdir(parents=True, exist_ok=True)
    stats = source_stats()
    write_week1(stats)
    write_week2(stats)
    update_recovery(stats)
    print(f"patt_rows={stats['patt_rows']}")
    print(f"combined_rows={stats['combined_rows']}")
    print("paper_cards=7")
    print("paper_inventory_rows=7")
    print("teacher_vs_paper_mapping_rows=7")


if __name__ == "__main__":
    main()
