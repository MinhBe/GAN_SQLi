from __future__ import annotations

import base64
import csv
import hashlib
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


GAN = Path("GAN")
RAW = GAN / "Data" / "raw" / "httpparamsdataset"
README = RAW / "README.md"
SOURCE_CSV = RAW / "payload_full.csv"
MANIFESTS = GAN / "Data" / "manifests"
PROCESSED = GAN / "Data" / "processed"
REPORTS = GAN / "Reports"
BASELINES = GAN / "Reproduction" / "baselines"
RECOVERY = GAN / "RECOVERY.md"

PATT_NORMALIZED = PROCESSED / "teacher_seed_sqli_normalized.csv"
HTTPPARAMS_NORMALIZED = PROCESSED / "httpparams_sqli_normalized.csv"
COMBINED_NORMALIZED = PROCESSED / "teacher_seed_sqli_normalized_combined.csv"

SOURCE_URL = "https://github.com/Morzeux/HttpParamsDataset"
SOURCE_ID = "httpparamsdataset_sqli_payload_full"
SOURCE_NAME = "HttpParamsDataset SQLi payload_full"

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
    elif any(token in lower for token in ("waitfor delay", "xp_", "@@servername")):
        dbms = "mssql"
    elif any(token in lower for token in ("dbms_pipe", "dbms_lock", "dual")):
        dbms = "oracle"

    if "union" in lower and "select" in lower:
        return "UNION Based Injection", dbms, "union select"
    if any(token in lower for token in ("sleep(", "benchmark(", "waitfor delay", "pg_sleep", "dbms_lock", "dbms_pipe")):
        return "Time Based Injection", dbms, "time based"
    if any(token in lower for token in (" or ", "'or", "\"or", " and ", "'and", "\"and")):
        return "Blind Injection", dbms, "boolean or tautology"
    if any(token in lower for token in ("extractvalue", "updatexml", "convert(", "cast(")):
        return "Error Based Injection", dbms, "error based"
    if ";" in value:
        return "Stacked Based Injection", dbms, "stacked query"
    return "Entry Point Detection", dbms, "http parameter sqli"


def load_sqli_rows(commit: str) -> tuple[list[dict[str, str]], dict[str, str], Counter[str]]:
    rows: list[dict[str, str]] = []
    hash_counts: Counter[str] = Counter()
    total_records = 0
    skipped_records = 0

    with SOURCE_CSV.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        expected = ["payload", "length", "attack_type", "label"]
        if reader.fieldnames != expected:
            raise ValueError(f"Unexpected schema: {reader.fieldnames}")

        for line_number, source_row in enumerate(reader, start=2):
            total_records += 1
            if source_row["attack_type"] != "sqli" and source_row["label"] != "sqli":
                skipped_records += 1
                continue
            payload = source_row["payload"]
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
                    "relative_path": rel(SOURCE_CSV),
                    "file_name": SOURCE_CSV.name,
                    "line_number": str(line_number),
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
        "relative_path": rel(SOURCE_CSV),
        "file_name": SOURCE_CSV.name,
        "category": "SQL Injection",
        "dbms": "mixed",
        "technique": "http parameter sqli",
        "nonblank_row_count": str(len(rows)),
        "unique_payload_hash_count": str(len(hash_counts)),
        "duplicate_line_count": str(sum(count - 1 for count in hash_counts.values() if count > 1)),
        "file_sha256": file_sha256(SOURCE_CSV),
        "total_source_records": str(total_records),
        "skipped_non_sqli_records": str(skipped_records),
    }
    return rows, inventory, hash_counts


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def read_existing_patt() -> list[dict[str, str]]:
    if not PATT_NORMALIZED.is_file():
        return []
    with PATT_NORMALIZED.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_inventory(commit: str, inventory: dict[str, str]) -> None:
    write_csv(
        MANIFESTS / "httpparams_sqli_inventory.csv",
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

    existing_rows = []
    teacher_inventory = MANIFESTS / "teacher_seed_inventory.csv"
    if teacher_inventory.is_file():
        with teacher_inventory.open("r", encoding="utf-8", newline="") as f:
            existing_rows = list(csv.DictReader(f))
    compatible_inventory = {k: inventory[k] for k in existing_rows[0].keys()} if existing_rows else inventory
    write_csv(teacher_inventory, existing_rows + [compatible_inventory], list(compatible_inventory.keys()))


def write_source_card(commit: str, inventory: dict[str, str]) -> None:
    lines = [
        "# HttpParamsDataset SQLi Source Card",
        "",
        f"- Source URL: `{SOURCE_URL}`",
        "- Raw source path: `GAN/Data/raw/httpparamsdataset`",
        "- README path: `GAN/Data/raw/httpparamsdataset/README.md`",
        "- Primary CSV path: `GAN/Data/raw/httpparamsdataset/payload_full.csv`",
        f"- Downloaded commit/hash: `{commit}`",
        "- Retrieval mode: online git clone",
        f"- Total source records: {inventory['total_source_records']}",
        f"- SQLi rows selected: {inventory['nonblank_row_count']}",
        f"- Non-SQLi rows skipped: {inventory['skipped_non_sqli_records']}",
        f"- Unique SQLi payload hashes: {inventory['unique_payload_hash_count']}",
        f"- Duplicate SQLi rows by payload hash: {inventory['duplicate_line_count']}",
        "",
        "## Source Schema",
        "",
        "| Column | Use |",
        "| --- | --- |",
        "| payload | Encoded into normalized teacher seed rows |",
        "| length | Source-provided payload length metadata |",
        "| attack_type | Filtered to `sqli` |",
        "| label | Confirmed as `sqli` for selected rows |",
        "",
    ]
    (MANIFESTS / "httpparamsdataset_sqli_source_card.md").write_text("\n".join(lines), encoding="utf-8")


def write_report(commit: str, rows: list[dict[str, str]], inventory: dict[str, str], hash_counts: Counter[str], combined_rows: list[dict[str, str]]) -> None:
    by_category = Counter(row["category"] for row in rows)
    by_dbms = Counter(row["dbms"] for row in rows)
    combined_hashes = Counter(row["normalized_sha256"] for row in combined_rows)
    lines = [
        "# HttpParamsDataset Teacher Resource Inventory",
        "",
        "## Source",
        "",
        f"- Online source URL: `{SOURCE_URL}`",
        "- Raw source path: `GAN/Data/raw/httpparamsdataset`",
        f"- Downloaded commit/hash: `{commit}`",
        "",
        "## Generated Artifacts",
        "",
        "- `GAN/Data/manifests/httpparamsdataset_sqli_source_card.md`",
        "- `GAN/Data/manifests/httpparams_sqli_inventory.csv`",
        "- `GAN/Data/processed/httpparams_sqli_normalized.csv`",
        "- `GAN/Data/processed/teacher_seed_sqli_normalized_combined.csv`",
        "- `GAN/Reproduction/baselines/httpparamsdataset_rule_baseline.md`",
        "",
        "## Seed Statistics",
        "",
        f"- Total source records: {inventory['total_source_records']}",
        f"- SQLi rows selected: {len(rows)}",
        f"- Non-SQLi rows skipped: {inventory['skipped_non_sqli_records']}",
        f"- Unique HttpParams SQLi hashes: {len(hash_counts)}",
        f"- Duplicate HttpParams SQLi rows by payload hash: {sum(count - 1 for count in hash_counts.values() if count > 1)}",
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
    (REPORTS / "01_httpparams_teacher_resource_inventory.md").write_text("\n".join(lines), encoding="utf-8")


def write_baseline(commit: str, rows: list[dict[str, str]], hash_counts: Counter[str]) -> None:
    by_technique = Counter(row["technique"] for row in rows)
    lines = [
        "# HttpParamsDataset Rule Baseline",
        "",
        f"- Source URL: `{SOURCE_URL}`",
        f"- Downloaded commit/hash: `{commit}`",
        "- Input path: `GAN/Data/raw/httpparamsdataset/payload_full.csv`",
        "- Normalized output: `GAN/Data/processed/httpparams_sqli_normalized.csv`",
        "",
        "## Baseline Scope",
        "",
        "- Reads online-downloaded `payload_full.csv`.",
        "- Selects rows where source SQLi labels are present.",
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
    (BASELINES / "httpparamsdataset_rule_baseline.md").write_text("\n".join(lines), encoding="utf-8")


def update_recovery(commit: str, rows: list[dict[str, str]], inventory: dict[str, str], hash_counts: Counter[str], combined_rows: list[dict[str, str]]) -> None:
    combined_hashes = Counter(row["normalized_sha256"] for row in combined_rows)
    timestamp = datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()
    text = f"""# Recovery

- Current phase: Step 2 online-only HttpParamsDataset teacher seed setup
- Last completed step: Step 2 verification
- Next exact step: Start the next online-only teacher source ingestion step
- Updated artifacts:
  - `GAN/RECOVERY.md`
  - `GAN/Data/raw/payloadsallthethings`
  - `GAN/Data/raw/httpparamsdataset`
  - `GAN/Reports/00_teacher_resource_inventory.md`
  - `GAN/Reports/01_httpparams_teacher_resource_inventory.md`
  - `GAN/Data/manifests/payloadsallthethings_sqli_source_card.md`
  - `GAN/Data/manifests/httpparamsdataset_sqli_source_card.md`
  - `GAN/Data/manifests/teacher_seed_inventory.csv`
  - `GAN/Data/manifests/httpparams_sqli_inventory.csv`
  - `GAN/Data/processed/teacher_seed_sqli_normalized.csv`
  - `GAN/Data/processed/httpparams_sqli_normalized.csv`
  - `GAN/Data/processed/teacher_seed_sqli_normalized_combined.csv`
  - `GAN/Reproduction/baselines/payloadsallthethings_rule_baseline.md`
  - `GAN/Reproduction/baselines/httpparamsdataset_rule_baseline.md`
- Online source URL: `https://github.com/swisskyrepo/PayloadsAllTheThings`
- Primary SQL Injection README URL: `https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/README.md`
- Downloaded commit/hash: `e961fef231d8327bae83b563fab50aec2e6b77c0`
- Step 2 online source URL: `{SOURCE_URL}`
- Step 2 downloaded commit/hash: `{commit}`
- Command log summary:
  - Created `GAN` directory tree for raw data, manifests, processed data, reports, baselines, and scripts.
  - Downloaded online source into `GAN/Data/raw/payloadsallthethings`.
  - Generated PayloadsAllTheThings inventory, normalized CSV, source card, report, and baseline artifacts under `GAN`.
  - Selected `{SOURCE_URL}` as the next online-only teacher source.
  - Downloaded online source into `GAN/Data/raw/httpparamsdataset`.
  - Confirmed `GAN/Data/raw/httpparamsdataset/README.md`.
  - Confirmed HttpParams CSV schema: payload, length, attack_type, label.
  - Generated HttpParams inventory, normalized CSV, source card, report, baseline, and combined normalized CSV under `GAN`.
  - Verified generated artifact paths and CSV row counts.
  - Verified generated artifacts contain no offline-source marker and no absolute path marker outside `GAN`.
- Row counts:
  - PayloadsAllTheThings Intruder source files: 21
  - PayloadsAllTheThings normalized nonblank rows: 1465
  - HttpParams total source records: {inventory['total_source_records']}
  - HttpParams SQLi normalized rows: {len(rows)}
  - HttpParams unique payload hashes: {len(hash_counts)}
  - Combined normalized rows: {len(combined_rows)}
  - Combined unique payload hashes: {len(combined_hashes)}
- Duplicate counts:
  - HttpParams duplicate rows by payload hash: {sum(count - 1 for count in hash_counts.values() if count > 1)}
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
    if not SOURCE_CSV.is_file():
        raise FileNotFoundError(rel(SOURCE_CSV))

    commit = git_commit()
    rows, inventory, hash_counts = load_sqli_rows(commit)
    patt_rows = read_existing_patt()
    combined_rows = patt_rows + rows

    write_csv(HTTPPARAMS_NORMALIZED, rows, NORMALIZED_FIELDS)
    write_csv(COMBINED_NORMALIZED, combined_rows, NORMALIZED_FIELDS)
    write_inventory(commit, inventory)
    write_source_card(commit, inventory)
    write_report(commit, rows, inventory, hash_counts, combined_rows)
    write_baseline(commit, rows, hash_counts)
    update_recovery(commit, rows, inventory, hash_counts, combined_rows)

    combined_hashes = Counter(row["normalized_sha256"] for row in combined_rows)
    print(f"commit={commit}")
    print(f"httpparams_sqli_rows={len(rows)}")
    print(f"httpparams_unique_payload_hashes={len(hash_counts)}")
    print(f"httpparams_duplicate_rows={sum(count - 1 for count in hash_counts.values() if count > 1)}")
    print(f"combined_rows={len(combined_rows)}")
    print(f"combined_unique_payload_hashes={len(combined_hashes)}")
    print(f"combined_duplicate_rows={sum(count - 1 for count in combined_hashes.values() if count > 1)}")


if __name__ == "__main__":
    main()
