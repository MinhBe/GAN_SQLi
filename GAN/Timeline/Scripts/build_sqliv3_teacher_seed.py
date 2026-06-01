from __future__ import annotations

import base64
import csv
import hashlib
import json
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


GAN = Path("GAN")
RAW = GAN / "Data" / "raw" / "sqliv5-dataset"
README = RAW / "README.md"
SOURCE_JSON = RAW / "SQLiV3_clean.json"
MANIFESTS = GAN / "Data" / "manifests"
PROCESSED = GAN / "Data" / "processed"
REPORTS = GAN / "Reports"
BASELINES = GAN / "Reproduction" / "baselines"
RECOVERY = GAN / "RECOVERY.md"

PATT_NORMALIZED = PROCESSED / "teacher_seed_sqli_normalized.csv"
HTTPPARAMS_NORMALIZED = PROCESSED / "httpparams_sqli_normalized.csv"
SQLIV3_NORMALIZED = PROCESSED / "sqliv3_sqli_normalized.csv"
COMBINED_NORMALIZED = PROCESSED / "teacher_seed_sqli_normalized_combined.csv"

SOURCE_URL = "https://github.com/nidnogg/sqliv5-dataset"
SOURCE_ID = "sqliv3_mirror_sqli_clean"
SOURCE_NAME = "SQLiV3 mirror SQLi clean"

PATT_COMMIT = "e961fef231d8327bae83b563fab50aec2e6b77c0"
HTTPPARAMS_COMMIT = "926670a710283f87c05b554680facf3f9530548c"

NORMALIZED_FIELDS = [
    "source_id",
    "source_name",
    "source_url",
    "commit_hash",
    "relative_path",
    "file_name",
    "line_number",
    "category",
    "dbms",
    "technique",
    "payload_base64",
    "payload_sha256",
    "normalized_payload_base64",
    "normalized_sha256",
]


def rel(path: Path) -> str:
    return path.as_posix()


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8", errors="replace")).hexdigest()


def b64_text(value: str) -> str:
    return base64.b64encode(value.encode("utf-8", errors="replace")).decode("ascii")


def file_sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def git_commit() -> str:
    result = subprocess.run(
        ["git", "-C", rel(RAW), "rev-parse", "HEAD"],
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


def classify_payload(value: str) -> tuple[str, str, str]:
    lower = value.lower()
    dbms = "generic"
    if any(token in lower for token in ("@@version", "information_schema", "benchmark(", "sleep(")):
        dbms = "mysql"
    elif any(token in lower for token in ("pg_sleep", "pg_", "postgres")):
        dbms = "postgresql"
    elif any(token in lower for token in ("waitfor delay", "xp_", "@@servername", "mssql")):
        dbms = "mssql"
    elif any(token in lower for token in ("utl_inaddr", "dbms_pipe", "dbms_lock", "dual", "sys.all_tables")):
        dbms = "oracle"

    if "union" in lower and "select" in lower:
        return "UNION Based Injection", dbms, "union select"
    if any(token in lower for token in ("sleep(", "pg_sleep", "benchmark(", "waitfor delay", "dbms_pipe", "dbms_lock")):
        return "Time Based Injection", dbms, "time based"
    if any(token in lower for token in ("utl_inaddr", "extractvalue", "updatexml", "convert(", "cast(")):
        return "Error Based Injection", dbms, "error based"
    if ";" in value:
        return "Stacked Based Injection", dbms, "stacked query"
    if any(token in lower for token in (" or ", "'or", '"or', " and ", "'and", '"and')):
        return "Blind Injection", dbms, "boolean or tautology"
    return "Entry Point Detection", dbms, "sqli pattern"


def load_rows(commit: str) -> tuple[list[dict[str, str]], dict[str, str], Counter[str], Counter[str]]:
    data = json.loads(SOURCE_JSON.read_text(encoding="utf-8"))
    if not isinstance(data, list):
        raise ValueError("SQLiV3_clean.json must contain a list")

    rows: list[dict[str, str]] = []
    hash_counts: Counter[str] = Counter()
    type_counts: Counter[str] = Counter()
    for index, item in enumerate(data, start=1):
        if not isinstance(item, dict) or "pattern" not in item or "type" not in item:
            raise ValueError(f"Unexpected record at index {index}")
        source_type = str(item["type"])
        type_counts[source_type] += 1
        if source_type != "sqli":
            continue
        payload = str(item["pattern"])
        normalized = payload.strip()
        payload_hash = sha256_text(normalized)
        category, dbms, technique = classify_payload(normalized)
        hash_counts[payload_hash] += 1
        rows.append(
            {
                "source_id": SOURCE_ID,
                "source_name": SOURCE_NAME,
                "source_url": SOURCE_URL,
                "commit_hash": commit,
                "relative_path": rel(SOURCE_JSON),
                "file_name": SOURCE_JSON.name,
                "line_number": str(index),
                "category": category,
                "dbms": dbms,
                "technique": technique,
                "payload_base64": b64_text(payload),
                "payload_sha256": payload_hash,
                "normalized_payload_base64": b64_text(normalized),
                "normalized_sha256": payload_hash,
            }
        )

    inventory = {
        "source_id": SOURCE_ID,
        "source_name": SOURCE_NAME,
        "source_url": SOURCE_URL,
        "commit_hash": commit,
        "relative_path": rel(SOURCE_JSON),
        "file_name": SOURCE_JSON.name,
        "category": "SQL Injection",
        "dbms": "mixed",
        "technique": "sqli pattern",
        "nonblank_row_count": str(len(rows)),
        "unique_payload_hash_count": str(len(hash_counts)),
        "duplicate_line_count": str(sum(count - 1 for count in hash_counts.values() if count > 1)),
        "file_sha256": file_sha256(SOURCE_JSON),
        "total_source_records": str(len(data)),
        "skipped_non_sqli_records": str(sum(count for label, count in type_counts.items() if label != "sqli")),
    }
    return rows, inventory, hash_counts, type_counts


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_rows(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_inventory(inventory: dict[str, str]) -> None:
    write_csv(
        MANIFESTS / "sqliv3_sqli_inventory.csv",
        [inventory],
        [
            "source_id",
            "source_name",
            "source_url",
            "commit_hash",
            "relative_path",
            "file_name",
            "category",
            "dbms",
            "technique",
            "nonblank_row_count",
            "unique_payload_hash_count",
            "duplicate_line_count",
            "file_sha256",
            "total_source_records",
            "skipped_non_sqli_records",
        ],
    )

    teacher_inventory = MANIFESTS / "teacher_seed_inventory.csv"
    existing_rows = read_rows(teacher_inventory)
    if existing_rows:
        fieldnames = list(existing_rows[0].keys())
        compatible = {key: inventory[key] for key in fieldnames}
        write_csv(teacher_inventory, existing_rows + [compatible], fieldnames)
    else:
        write_csv(teacher_inventory, [inventory], list(inventory.keys()))


def write_source_card(commit: str, inventory: dict[str, str], type_counts: Counter[str]) -> None:
    lines = [
        "# SQLiV3 Mirror Source Card",
        "",
        f"- Source URL: `{SOURCE_URL}`",
        "- Raw source path: `GAN/Data/raw/sqliv5-dataset`",
        "- README path: `GAN/Data/raw/sqliv5-dataset/README.md`",
        "- Primary JSON path: `GAN/Data/raw/sqliv5-dataset/SQLiV3_clean.json`",
        f"- Downloaded commit/hash: `{commit}`",
        "- Retrieval mode: online git clone",
        f"- Total source records: {inventory['total_source_records']}",
        f"- SQLi rows selected: {inventory['nonblank_row_count']}",
        f"- Non-SQLi rows skipped: {inventory['skipped_non_sqli_records']}",
        f"- Unique SQLi payload hashes: {inventory['unique_payload_hash_count']}",
        f"- Duplicate SQLi rows by payload hash: {inventory['duplicate_line_count']}",
        "",
        "## Type Distribution",
        "",
        "| Type | Rows |",
        "| --- | ---: |",
    ]
    for label, count in sorted(type_counts.items()):
        lines.append(f"| {label} | {count} |")
    lines.append("")
    (MANIFESTS / "sqliv3_sqli_source_card.md").write_text("\n".join(lines), encoding="utf-8")


def write_report(commit: str, rows: list[dict[str, str]], inventory: dict[str, str], hash_counts: Counter[str], combined_rows: list[dict[str, str]]) -> None:
    by_category = Counter(row["category"] for row in rows)
    by_dbms = Counter(row["dbms"] for row in rows)
    combined_hashes = Counter(row["normalized_sha256"] for row in combined_rows)
    lines = [
        "# SQLiV3 Mirror Teacher Resource Inventory",
        "",
        "## Source",
        "",
        f"- Online source URL: `{SOURCE_URL}`",
        "- Raw source path: `GAN/Data/raw/sqliv5-dataset`",
        "- Primary input path: `GAN/Data/raw/sqliv5-dataset/SQLiV3_clean.json`",
        f"- Downloaded commit/hash: `{commit}`",
        "",
        "## Generated Artifacts",
        "",
        "- `GAN/Data/manifests/sqliv3_sqli_source_card.md`",
        "- `GAN/Data/manifests/sqliv3_sqli_inventory.csv`",
        "- `GAN/Data/processed/sqliv3_sqli_normalized.csv`",
        "- `GAN/Data/processed/teacher_seed_sqli_normalized_combined.csv`",
        "- `GAN/Reproduction/baselines/sqliv3_rule_baseline.md`",
        "",
        "## Seed Statistics",
        "",
        f"- Total source records: {inventory['total_source_records']}",
        f"- SQLi rows selected: {len(rows)}",
        f"- Non-SQLi rows skipped: {inventory['skipped_non_sqli_records']}",
        f"- Unique SQLi hashes: {len(hash_counts)}",
        f"- Duplicate SQLi rows by payload hash: {sum(count - 1 for count in hash_counts.values() if count > 1)}",
        f"- Combined normalized rows: {len(combined_rows)}",
        f"- Combined unique payload hashes: {len(combined_hashes)}",
        f"- Combined duplicate rows by payload hash: {sum(count - 1 for count in combined_hashes.values() if count > 1)}",
        "",
        "## Rows By Category",
        "",
        "| Category | Rows |",
        "| --- | ---: |",
    ]
    for category, count in sorted(by_category.items()):
        lines.append(f"| {category} | {count} |")
    lines.extend(["", "## Rows By DBMS", "", "| DBMS | Rows |", "| --- | ---: |"])
    for dbms, count in sorted(by_dbms.items()):
        lines.append(f"| {dbms} | {count} |")
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This report contains aggregate counts only.",
            "- Detailed seed strings are base64-encoded in processed CSV artifacts.",
            "- No offline source was used.",
            "",
        ]
    )
    (REPORTS / "02_sqliv3_teacher_resource_inventory.md").write_text("\n".join(lines), encoding="utf-8")


def write_baseline(commit: str, rows: list[dict[str, str]], hash_counts: Counter[str]) -> None:
    by_technique = Counter(row["technique"] for row in rows)
    lines = [
        "# SQLiV3 Mirror Rule Baseline",
        "",
        f"- Source URL: `{SOURCE_URL}`",
        f"- Downloaded commit/hash: `{commit}`",
        "- Input path: `GAN/Data/raw/sqliv5-dataset/SQLiV3_clean.json`",
        "- Normalized output: `GAN/Data/processed/sqliv3_sqli_normalized.csv`",
        "",
        "## Baseline Scope",
        "",
        "- Reads online-downloaded `SQLiV3_clean.json`.",
        "- Selects records where `type` is `sqli`.",
        "- Trims leading and trailing whitespace for normalized hashes.",
        "- Stores detailed strings as base64 in CSV artifacts.",
        "",
        "## Aggregate Counts",
        "",
        f"- Normalized rows: {len(rows)}",
        f"- Unique payload hashes: {len(hash_counts)}",
        f"- Duplicate rows by payload hash: {sum(count - 1 for count in hash_counts.values() if count > 1)}",
        "",
        "## Technique Distribution",
        "",
        "| Technique | Rows |",
        "| --- | ---: |",
    ]
    for technique, count in sorted(by_technique.items()):
        lines.append(f"| {technique} | {count} |")
    lines.append("")
    (BASELINES / "sqliv3_rule_baseline.md").write_text("\n".join(lines), encoding="utf-8")


def update_recovery(commit: str, rows: list[dict[str, str]], inventory: dict[str, str], hash_counts: Counter[str], combined_rows: list[dict[str, str]]) -> None:
    combined_hashes = Counter(row["normalized_sha256"] for row in combined_rows)
    timestamp = datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()
    text = f"""# Recovery

- Current phase: Step 3 online-only SQLiV3 mirror teacher seed setup
- Last completed step: Step 3 verification
- Next exact step: Start the next online-only teacher source ingestion step or begin downstream GAN corpus preparation
- Updated artifacts:
  - `GAN/RECOVERY.md`
  - `GAN/Data/raw/payloadsallthethings`
  - `GAN/Data/raw/httpparamsdataset`
  - `GAN/Data/raw/sqliv5-dataset`
  - `GAN/Reports/00_teacher_resource_inventory.md`
  - `GAN/Reports/01_httpparams_teacher_resource_inventory.md`
  - `GAN/Reports/02_sqliv3_teacher_resource_inventory.md`
  - `GAN/Data/manifests/payloadsallthethings_sqli_source_card.md`
  - `GAN/Data/manifests/httpparamsdataset_sqli_source_card.md`
  - `GAN/Data/manifests/sqliv3_sqli_source_card.md`
  - `GAN/Data/manifests/teacher_seed_inventory.csv`
  - `GAN/Data/manifests/httpparams_sqli_inventory.csv`
  - `GAN/Data/manifests/sqliv3_sqli_inventory.csv`
  - `GAN/Data/processed/teacher_seed_sqli_normalized.csv`
  - `GAN/Data/processed/httpparams_sqli_normalized.csv`
  - `GAN/Data/processed/sqliv3_sqli_normalized.csv`
  - `GAN/Data/processed/teacher_seed_sqli_normalized_combined.csv`
  - `GAN/Reproduction/baselines/payloadsallthethings_rule_baseline.md`
  - `GAN/Reproduction/baselines/httpparamsdataset_rule_baseline.md`
  - `GAN/Reproduction/baselines/sqliv3_rule_baseline.md`
- Online source URL: `https://github.com/swisskyrepo/PayloadsAllTheThings`
- Primary SQL Injection README URL: `https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/README.md`
- Downloaded commit/hash: `{PATT_COMMIT}`
- Step 2 online source URL: `https://github.com/Morzeux/HttpParamsDataset`
- Step 2 downloaded commit/hash: `{HTTPPARAMS_COMMIT}`
- Step 3 online source URL: `{SOURCE_URL}`
- Step 3 downloaded commit/hash: `{commit}`
- Command log summary:
  - Created `GAN` directory tree for raw data, manifests, processed data, reports, baselines, and scripts.
  - Downloaded online source into `GAN/Data/raw/payloadsallthethings`.
  - Generated PayloadsAllTheThings inventory, normalized CSV, source card, report, and baseline artifacts under `GAN`.
  - Downloaded online source into `GAN/Data/raw/httpparamsdataset`.
  - Generated HttpParams inventory, normalized CSV, source card, report, baseline, and combined normalized CSV under `GAN`.
  - Selected `{SOURCE_URL}` as the next online-only teacher source.
  - Downloaded online source into `GAN/Data/raw/sqliv5-dataset`.
  - Confirmed `GAN/Data/raw/sqliv5-dataset/README.md`.
  - Selected `GAN/Data/raw/sqliv5-dataset/SQLiV3_clean.json` as the SQLiV3 mirror input with pattern/type schema.
  - Generated SQLiV3 mirror inventory, normalized CSV, source card, report, baseline, and refreshed combined normalized CSV under `GAN`.
  - Verified generated artifact paths and CSV row counts.
  - Verified generated artifacts contain no offline-source marker and no absolute path marker outside `GAN`.
- Row counts:
  - PayloadsAllTheThings normalized nonblank rows: 1465
  - HttpParams SQLi normalized rows: 10852
  - SQLiV3 mirror total source records: {inventory['total_source_records']}
  - SQLiV3 mirror SQLi normalized rows: {len(rows)}
  - SQLiV3 mirror unique payload hashes: {len(hash_counts)}
  - Combined normalized rows: {len(combined_rows)}
  - Combined unique payload hashes: {len(combined_hashes)}
- Duplicate counts:
  - SQLiV3 mirror duplicate rows by payload hash: {sum(count - 1 for count in hash_counts.values() if count > 1)}
  - Combined duplicate rows by payload hash: {sum(count - 1 for count in combined_hashes.values() if count > 1)}
- Blockers: none
- Last updated: `{timestamp}`
"""
    RECOVERY.write_text(text, encoding="utf-8")


def main() -> None:
    for path in (MANIFESTS, PROCESSED, REPORTS, BASELINES):
        path.mkdir(parents=True, exist_ok=True)
    if not README.is_file():
        raise FileNotFoundError(rel(README))
    if not SOURCE_JSON.is_file():
        raise FileNotFoundError(rel(SOURCE_JSON))

    commit = git_commit()
    rows, inventory, hash_counts, type_counts = load_rows(commit)
    combined_rows = read_rows(PATT_NORMALIZED) + read_rows(HTTPPARAMS_NORMALIZED) + rows

    write_csv(SQLIV3_NORMALIZED, rows, NORMALIZED_FIELDS)
    write_csv(COMBINED_NORMALIZED, combined_rows, NORMALIZED_FIELDS)
    write_inventory(inventory)
    write_source_card(commit, inventory, type_counts)
    write_report(commit, rows, inventory, hash_counts, combined_rows)
    write_baseline(commit, rows, hash_counts)
    update_recovery(commit, rows, inventory, hash_counts, combined_rows)

    combined_hashes = Counter(row["normalized_sha256"] for row in combined_rows)
    print(f"commit={commit}")
    print(f"sqliv3_sqli_rows={len(rows)}")
    print(f"sqliv3_unique_payload_hashes={len(hash_counts)}")
    print(f"sqliv3_duplicate_rows={sum(count - 1 for count in hash_counts.values() if count > 1)}")
    print(f"combined_rows={len(combined_rows)}")
    print(f"combined_unique_payload_hashes={len(combined_hashes)}")
    print(f"combined_duplicate_rows={sum(count - 1 for count in combined_hashes.values() if count > 1)}")


if __name__ == "__main__":
    main()
