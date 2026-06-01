from __future__ import annotations

import csv
import hashlib
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("Timeline")
DATA = ROOT / "Data"
MANIFESTS = DATA / "manifests"
PROCESSED = DATA / "processed"
SPLITS = DATA / "splits"
REPORTS = ROOT / "Reports"
RECOVERY = ROOT / "RECOVERY.md"
TIMELINE = ROOT / "TIMELINE.md"
AUDIT = ROOT / "TRAJECTORY_AUDIT.md"

COMBINED = PROCESSED / "teacher_seed_sqli_normalized_combined.csv"

PATT_COMMIT = "e961fef231d8327bae83b563fab50aec2e6b77c0"
HTTPPARAMS_COMMIT = "926670a710283f87c05b554680facf3f9530548c"
SQLIV3_COMMIT = "486e182221e48d2cadab63edc217dfd46eb67405"


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def split_for_hash(normalized_sha256: str) -> str:
    bucket = int(hashlib.sha256(("phase1:" + normalized_sha256).encode("ascii")).hexdigest()[:8], 16) % 100
    if bucket < 80:
        return "train"
    if bucket < 90:
        return "validation"
    return "test"


def combined_stats() -> dict[str, object]:
    rows = read_csv(COMBINED)
    hash_counts = Counter(row["normalized_sha256"] for row in rows)
    source_counts = Counter(row["source_id"] for row in rows)
    unique_by_source: dict[str, set[str]] = defaultdict(set)
    category_counts = Counter(row["category"] for row in rows)
    dbms_counts = Counter(row["dbms"] for row in rows)
    for row in rows:
        unique_by_source[row["source_id"]].add(row["normalized_sha256"])
    return {
        "rows": rows,
        "total": len(rows),
        "unique": len(hash_counts),
        "duplicates": sum(v - 1 for v in hash_counts.values() if v > 1),
        "source_counts": source_counts,
        "unique_by_source": {k: len(v) for k, v in unique_by_source.items()},
        "category_counts": category_counts,
        "dbms_counts": dbms_counts,
    }


def dataset_inventory(stats: dict[str, object]) -> list[dict[str, str]]:
    source_counts: Counter[str] = stats["source_counts"]  # type: ignore[assignment]
    unique_by_source: dict[str, int] = stats["unique_by_source"]  # type: ignore[assignment]
    return [
        {
            "source": "PayloadsAllTheThings SQL Injection",
            "paper_or_origin": "Teacher-provided resource",
            "role": "Seed corpus, taxonomy, operator baseline",
            "source_url": "https://github.com/swisskyrepo/PayloadsAllTheThings",
            "commit_hash": PATT_COMMIT,
            "local_file": "Timeline/Data/raw/payloadsallthethings/SQL Injection/Intruder",
            "raw_rows": "1465",
            "usable_rows": str(unique_by_source.get("payloadsallthethings_sqli_intruder", 0)),
            "duplicate_rows": str(source_counts.get("payloadsallthethings_sqli_intruder", 0) - unique_by_source.get("payloadsallthethings_sqli_intruder", 0)),
            "invalid_rows": "not_checked",
            "skipped_rows": "0",
            "license": "MIT",
            "label_source": "README taxonomy and source filenames",
            "status": "ingested",
        },
        {
            "source": "HttpParams Dataset",
            "paper_or_origin": "Le 2024 GSQLi dataset reference",
            "role": "Paper train/eval comparison source",
            "source_url": "https://github.com/Morzeux/HttpParamsDataset",
            "commit_hash": HTTPPARAMS_COMMIT,
            "local_file": "Timeline/Data/raw/httpparamsdataset/payload_full.csv",
            "raw_rows": "31067",
            "usable_rows": str(unique_by_source.get("httpparamsdataset_sqli_payload_full", 0)),
            "duplicate_rows": str(source_counts.get("httpparamsdataset_sqli_payload_full", 0) - unique_by_source.get("httpparamsdataset_sqli_payload_full", 0)),
            "invalid_rows": "not_checked",
            "skipped_rows": "20215",
            "license": "MIT",
            "label_source": "attack_type/label fields",
            "status": "ingested",
        },
        {
            "source": "SQLiV3 mirror",
            "paper_or_origin": "SSHS/Kaggle SQL Injection Dataset mirror",
            "role": "Paper eval comparison source",
            "source_url": "https://github.com/nidnogg/sqliv5-dataset",
            "commit_hash": SQLIV3_COMMIT,
            "local_file": "Timeline/Data/raw/sqliv5-dataset/SQLiV3_clean.json",
            "raw_rows": "30864",
            "usable_rows": str(unique_by_source.get("sqliv3_mirror_sqli_clean", 0)),
            "duplicate_rows": str(source_counts.get("sqliv3_mirror_sqli_clean", 0) - unique_by_source.get("sqliv3_mirror_sqli_clean", 0)),
            "invalid_rows": "not_checked",
            "skipped_rows": "19517",
            "license": "MIT",
            "label_source": "type field",
            "status": "ingested",
        },
        {
            "source": "WAF-A-MoLE dataset",
            "paper_or_origin": "Demetrio 2020",
            "role": "ML-WAF/guided mutation baseline dataset",
            "source_url": "https://github.com/blindusername/wafamole-dataset",
            "commit_hash": "pending",
            "local_file": "pending",
            "raw_rows": "pending",
            "usable_rows": "pending",
            "duplicate_rows": "pending",
            "invalid_rows": "pending",
            "skipped_rows": "pending",
            "license": "pending",
            "label_source": "paper labels",
            "status": "todo",
        },
        {
            "source": "SQLMap tamper scripts",
            "paper_or_origin": "Teacher/Lu/Demetrio reference",
            "role": "Mutation operator source, not a dataset",
            "source_url": "https://github.com/sqlmapproject/sqlmap",
            "commit_hash": "pending",
            "local_file": "pending",
            "raw_rows": "not_applicable",
            "usable_rows": "not_applicable",
            "duplicate_rows": "not_applicable",
            "invalid_rows": "not_applicable",
            "skipped_rows": "not_applicable",
            "license": "pending",
            "label_source": "operator source",
            "status": "todo",
        },
    ]


def write_source_cards(inventory: list[dict[str, str]], stats: dict[str, object]) -> None:
    lines = [
        "# Source Cards",
        "",
        "This consolidated source-card file summarizes all Week 3 dataset/source inventory entries. Detailed source-specific cards remain in `Timeline/Data/manifests`.",
        "",
    ]
    for row in inventory:
        lines.extend(
            [
                f"## {row['source']}",
                "",
                f"- Role: {row['role']}",
                f"- Origin: {row['paper_or_origin']}",
                f"- Source URL: `{row['source_url']}`",
                f"- Commit/hash: `{row['commit_hash']}`",
                f"- Local file: `{row['local_file']}`",
                f"- Raw rows: {row['raw_rows']}",
                f"- Usable rows: {row['usable_rows']}",
                f"- Duplicate rows: {row['duplicate_rows']}",
                f"- Invalid rows: {row['invalid_rows']}",
                f"- Skipped rows: {row['skipped_rows']}",
                f"- License: {row['license']}",
                f"- Label source: {row['label_source']}",
                f"- Status: `{row['status']}`",
                "",
            ]
        )
    lines.extend(
        [
            "## Combined Corpus",
            "",
            f"- Combined rows: {stats['total']}",
            f"- Combined unique normalized hashes: {stats['unique']}",
            f"- Combined duplicate rows by hash: {stats['duplicates']}",
            "- Invalid rows: not checked by semantic evaluator yet",
            "",
        ]
    )
    (MANIFESTS / "source_cards.md").write_text("\n".join(lines), encoding="utf-8")


def write_split_artifacts(stats: dict[str, object]) -> dict[str, int]:
    rows: list[dict[str, str]] = stats["rows"]  # type: ignore[assignment]
    first_by_hash: dict[str, dict[str, str]] = {}
    for row in rows:
        first_by_hash.setdefault(row["normalized_sha256"], row)

    assignments = []
    for normalized_hash, row in sorted(first_by_hash.items()):
        split = split_for_hash(normalized_hash)
        assignments.append(
            {
                "normalized_sha256": normalized_hash,
                "split": split,
                "source_id": row["source_id"],
                "category": row["category"],
                "dbms": row["dbms"],
                "payload_sha256": row["payload_sha256"],
            }
        )
    write_csv(
        SPLITS / "teacher_seed_split_assignments.csv",
        assignments,
        ["normalized_sha256", "split", "source_id", "category", "dbms", "payload_sha256"],
    )

    split_counts = Counter(row["split"] for row in assignments)
    source_split_counts = Counter((row["source_id"], row["split"]) for row in assignments)
    summary_rows = []
    for split in ("train", "validation", "test"):
        summary_rows.append(
            {
                "split": split,
                "unique_payload_hashes": str(split_counts.get(split, 0)),
                "payload_rows_after_exact_dedup": str(split_counts.get(split, 0)),
            }
        )
    write_csv(SPLITS / "split_summary.csv", summary_rows, ["split", "unique_payload_hashes", "payload_rows_after_exact_dedup"])

    source_rows = [
        {"source_id": source, "split": split, "unique_payload_hashes": str(count)}
        for (source, split), count in sorted(source_split_counts.items())
    ]
    write_csv(SPLITS / "split_by_source.csv", source_rows, ["source_id", "split", "unique_payload_hashes"])

    rule = f"""# Split Rule

## Purpose

Week 3 defines the leakage-control rule used before evaluator, baseline metrics, WAF smoke tests, or GSQLi reproduction. The split is over normalized payload hashes, not raw rows, so exact duplicates cannot cross train/validation/test boundaries.

## Current Corpus

- Combined rows before exact de-duplication: {stats['total']}
- Unique normalized payload hashes after exact de-duplication: {stats['unique']}
- Duplicate rows removed from split universe: {stats['duplicates']}

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
| train | {split_counts.get('train', 0)} |
| validation | {split_counts.get('validation', 0)} |
| test | {split_counts.get('test', 0)} |

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
"""
    (SPLITS / "split_rule.md").write_text(rule, encoding="utf-8")
    return dict(split_counts)


def write_dataset_report(inventory: list[dict[str, str]], stats: dict[str, object], split_counts: dict[str, int]) -> None:
    inv_rows = "\n".join(
        f"| {row['source']} | {row['role']} | {row['raw_rows']} | {row['usable_rows']} | {row['duplicate_rows']} | {row['invalid_rows']} | {row['status']} |"
        for row in inventory
    )
    source_counts: Counter[str] = stats["source_counts"]  # type: ignore[assignment]
    source_rows = "\n".join(f"| `{source}` | {count} |" for source, count in sorted(source_counts.items()))
    report = f"""# Dataset Inventory

## Summary

Week 3 consolidates dataset/source status and defines the first leakage-control split. Three online sources are ingested and usable for downstream evaluator preparation. WAF-A-MoLE and SQLMap remain todo sources for later baseline work.

## Inventory

| Source | Role | Raw Rows | Usable Rows | Duplicate Rows | Invalid Rows | Status |
| --- | --- | ---: | ---: | ---: | --- | --- |
{inv_rows}

## Combined Corpus

- Combined rows: {stats['total']}
- Unique normalized payload hashes: {stats['unique']}
- Duplicate rows by normalized hash: {stats['duplicates']}
- Invalid rows: not checked by semantic evaluator yet

## Rows By Source

| Source ID | Rows |
| --- | ---: |
{source_rows}

## Split Summary

| Split | Unique hashes |
| --- | ---: |
| train | {split_counts.get('train', 0)} |
| validation | {split_counts.get('validation', 0)} |
| test | {split_counts.get('test', 0)} |

## Outputs

- `Timeline/Reports/02_dataset_inventory.md`
- `Timeline/Data/manifests/dataset_inventory.csv`
- `Timeline/Data/manifests/source_cards.md`
- `Timeline/Data/splits/split_rule.md`
- `Timeline/Data/splits/teacher_seed_split_assignments.csv`
- `Timeline/Data/splits/split_summary.csv`
- `Timeline/Data/splits/split_by_source.csv`

## Next Step

Week 4 should build the evaluator smoke test over a small sample and should not run model training before evaluator metrics and split-aware sampling exist.
"""
    (REPORTS / "02_dataset_inventory.md").write_text(report, encoding="utf-8")


def update_recovery(stats: dict[str, object], split_counts: dict[str, int]) -> None:
    timestamp = datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()
    text = f"""# Recovery

- Current phase: Week 3 dataset/source inventory completed
- Last completed step: Dataset inventory, source cards, and exact-hash split rule generated under `Timeline`
- Next exact step: Begin Week 4 evaluator and WAF smoke-test setup under `Timeline`
- Updated artifacts:
  - `Timeline/RECOVERY.md`
  - `Timeline/TIMELINE.md`
  - `Timeline/TRAJECTORY_AUDIT.md`
  - `Timeline/Reports/02_dataset_inventory.md`
  - `Timeline/Data/manifests/dataset_inventory.csv`
  - `Timeline/Data/manifests/source_cards.md`
  - `Timeline/Data/splits/split_rule.md`
  - `Timeline/Data/splits/teacher_seed_split_assignments.csv`
  - `Timeline/Data/splits/split_summary.csv`
  - `Timeline/Data/splits/split_by_source.csv`
- Online source URL: `https://github.com/swisskyrepo/PayloadsAllTheThings`
- Primary SQL Injection README URL: `https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/README.md`
- Downloaded commit/hash: `{PATT_COMMIT}`
- Step 2 online source URL: `https://github.com/Morzeux/HttpParamsDataset`
- Step 2 downloaded commit/hash: `{HTTPPARAMS_COMMIT}`
- Step 3 online source URL: `https://github.com/nidnogg/sqliv5-dataset`
- Step 3 downloaded commit/hash: `{SQLIV3_COMMIT}`
- Command log summary:
  - Consolidated dataset/source inventory for ingested and todo phase-1 sources.
  - Created consolidated source cards.
  - Created exact-hash train/validation/test split rule and split assignment CSV.
  - Preserved note that near-duplicate leakage is not fully solved until canonical/fuzzy grouping is implemented.
- Row counts:
  - Combined normalized rows: {stats['total']}
  - Combined unique payload hashes: {stats['unique']}
  - Train unique hashes: {split_counts.get('train', 0)}
  - Validation unique hashes: {split_counts.get('validation', 0)}
  - Test unique hashes: {split_counts.get('test', 0)}
- Duplicate counts:
  - Combined duplicate rows by payload hash: {stats['duplicates']}
- Blockers: none
- Last updated: `{timestamp}`
"""
    RECOVERY.write_text(text, encoding="utf-8")


def append_timeline(stats: dict[str, object], split_counts: dict[str, int]) -> None:
    addition = f"""

### Week 3 Completion

- Consolidated dataset/source inventory.
- Created `Timeline/Data/manifests/dataset_inventory.csv`.
- Created `Timeline/Data/manifests/source_cards.md`.
- Created `Timeline/Reports/02_dataset_inventory.md`.
- Created exact-hash split rule and split assignment files under `Timeline/Data/splits`.
- Split counts: train {split_counts.get('train', 0)}, validation {split_counts.get('validation', 0)}, test {split_counts.get('test', 0)} unique hashes.
- Combined corpus remains {stats['total']} rows, {stats['unique']} unique hashes, {stats['duplicates']} duplicate rows by hash.
"""
    with TIMELINE.open("a", encoding="utf-8") as f:
        f.write(addition)


def update_audit(split_counts: dict[str, int]) -> None:
    text = AUDIT.read_text(encoding="utf-8")
    if "Timeline/Data/splits/split_rule.md" not in text:
        text = text.replace(
            "7. `Timeline/Survey/tables/teacher_vs_paper_mapping.csv`\n8. `Timeline/Data/manifests/teacher_seed_inventory.csv`",
            "7. `Timeline/Survey/tables/teacher_vs_paper_mapping.csv`\n8. `Timeline/Data/manifests/dataset_inventory.csv`\n9. `Timeline/Data/splits/split_rule.md`\n10. `Timeline/Data/manifests/teacher_seed_inventory.csv`",
        )
    text = text.replace(
        "- Week 3 next: dataset/source inventory and split rule.",
        "- Week 3: dataset/source inventory and exact-hash split rule completed.",
    )
    text = text.replace(
        "- Do not jump to evaluator, WAF smoke test, baseline metrics, GSQLi reproduction, or GAN training before Week 3 dataset inventory and split rule are complete.",
        "- Week 4 next: evaluator and WAF smoke test. Do not jump to baseline metrics, GSQLi reproduction, or GAN training before evaluator smoke results exist.",
    )
    text = text.replace(
        "| Next step | Week 3 dataset/source inventory and split rule | Work jumps to Week 4+ without split/inventory |",
        "| Next step | Week 4 evaluator and WAF smoke test | Work jumps to baseline metrics, reproduction, or training without evaluator smoke results |",
    )
    insert = f"\n- Split counts: train {split_counts.get('train', 0)}, validation {split_counts.get('validation', 0)}, test {split_counts.get('test', 0)} unique hashes\n"
    if "- Split counts:" not in text:
        text = text.replace("- Teacher-paper mapping rows expected: 7\n", "- Teacher-paper mapping rows expected: 7\n" + insert)
    text = text.replace("`2026-05-29T01:18:31+07:00`", f"`{datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()}`")
    AUDIT.write_text(text, encoding="utf-8")


def main() -> None:
    for path in (MANIFESTS, SPLITS, REPORTS):
        path.mkdir(parents=True, exist_ok=True)
    stats = combined_stats()
    inventory = dataset_inventory(stats)
    write_csv(
        MANIFESTS / "dataset_inventory.csv",
        inventory,
        [
            "source",
            "paper_or_origin",
            "role",
            "source_url",
            "commit_hash",
            "local_file",
            "raw_rows",
            "usable_rows",
            "duplicate_rows",
            "invalid_rows",
            "skipped_rows",
            "license",
            "label_source",
            "status",
        ],
    )
    write_source_cards(inventory, stats)
    split_counts = write_split_artifacts(stats)
    write_dataset_report(inventory, stats, split_counts)
    update_recovery(stats, split_counts)
    append_timeline(stats, split_counts)
    update_audit(split_counts)
    print(f"combined_rows={stats['total']}")
    print(f"combined_unique_hashes={stats['unique']}")
    print(f"combined_duplicate_rows={stats['duplicates']}")
    print(f"train={split_counts.get('train', 0)}")
    print(f"validation={split_counts.get('validation', 0)}")
    print(f"test={split_counts.get('test', 0)}")


if __name__ == "__main__":
    main()
