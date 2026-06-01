from __future__ import annotations

import csv
import base64
import hashlib
import re
import subprocess
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


GAN = Path("GAN")
RAW = GAN / "Data" / "raw" / "payloadsallthethings"
SQLI = RAW / "SQL Injection"
INTRUDER = SQLI / "Intruder"
README = SQLI / "README.md"
MANIFESTS = GAN / "Data" / "manifests"
PROCESSED = GAN / "Data" / "processed"
REPORTS = GAN / "Reports"
BASELINES = GAN / "Reproduction" / "baselines"
RECOVERY = GAN / "RECOVERY.md"

SOURCE_URL = "https://github.com/swisskyrepo/PayloadsAllTheThings"
README_URL = "https://github.com/swisskyrepo/PayloadsAllTheThings/blob/master/SQL%20Injection/README.md"
RAW_README_URL = "https://raw.githubusercontent.com/swisskyrepo/PayloadsAllTheThings/master/SQL%20Injection/README.md"

TAXONOMY = [
    "Tools",
    "Entry Point Detection",
    "DBMS Identification",
    "Authentication Bypass",
    "UNION Based Injection",
    "Error Based Injection",
    "Blind Injection",
    "Time Based Injection",
    "Out of Band (OAST)",
    "Stacked Based Injection",
    "Polyglot Injection",
    "Routed Injection",
    "Second Order SQL Injection",
    "PDO Prepared Statements",
    "Generic WAF Bypass",
    "Labs",
]


def rel(path: Path) -> str:
    return path.as_posix()


def read_text(path: Path) -> str:
    for encoding in ("utf-8-sig", "utf-8", "latin-1"):
        try:
            return path.read_text(encoding=encoding)
        except UnicodeDecodeError:
            continue
    return path.read_text(errors="replace")


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


def classify_file(name: str) -> tuple[str, str, str]:
    lower = name.lower()
    dbms = "generic"
    for candidate in ("mssql", "mysql", "oracle", "postgres"):
        if candidate in lower:
            dbms = "postgresql" if candidate == "postgres" else candidate
            break

    if "auth" in lower:
        return "Authentication Bypass", dbms, "authentication bypass"
    if "union" in lower:
        return "UNION Based Injection", dbms, "union select"
    if "error" in lower:
        return "Error Based Injection", dbms, "error based"
    if "time" in lower:
        return "Time Based Injection", dbms, "time based"
    if "blind" in lower:
        return "Blind Injection", dbms, "blind"
    if "polyglot" in lower:
        return "Polyglot Injection", dbms, "polyglot"
    if "enum" in lower:
        return "DBMS Identification", dbms, "enumeration"
    if "readlocalfiles" in lower:
        return "DBMS Identification", dbms, "file read"
    if "fuzz" in lower:
        return "Entry Point Detection", dbms, "fuzzing"
    return "Entry Point Detection", dbms, "generic"


def extract_taxonomy(readme_text: str) -> list[dict[str, str]]:
    headings = {
        match.group(2).strip().lower(): (match.group(1), match.group(2).strip())
        for match in re.finditer(r"^(#{2,4})\s+(.+?)\s*$", readme_text, re.MULTILINE)
    }
    rows = []
    for label in TAXONOMY:
        key = label.lower()
        present = key in headings
        level = len(headings[key][0]) if present else ""
        rows.append(
            {
                "section": label,
                "present_in_readme": "yes" if present else "no",
                "heading_level": str(level),
            }
        )
    return rows


def payload_rows(commit: str) -> tuple[list[dict[str, str]], list[dict[str, str]], Counter[str]]:
    payloads: list[dict[str, str]] = []
    inventory: list[dict[str, str]] = []
    per_file_hashes: Counter[str] = Counter()

    source_files = sorted(path for path in INTRUDER.iterdir() if path.is_file())
    for source_file in source_files:
        text = read_text(source_file)
        lines = text.splitlines()
        category, dbms, technique = classify_file(source_file.name)
        file_hash = file_sha256(source_file)
        nonblank_rows = []

        for idx, line in enumerate(lines, start=1):
            normalized = line.strip()
            if not normalized:
                continue
            payload_hash = sha256_text(normalized)
            nonblank_rows.append(payload_hash)
            payloads.append(
                {
                    "source_id": "payloadsallthethings_sqli_intruder",
                    "source_name": "PayloadsAllTheThings SQL Injection Intruder",
                    "source_url": README_URL,
                    "commit_hash": commit,
                    "relative_path": rel(source_file),
                    "file_name": source_file.name,
                    "line_number": str(idx),
                    "category": category,
                    "dbms": dbms,
                    "technique": technique,
                    "payload_base64": b64_text(line),
                    "payload_sha256": payload_hash,
                    "normalized_payload_base64": b64_text(normalized),
                    "normalized_sha256": payload_hash,
                }
            )

        unique_hashes = set(nonblank_rows)
        duplicate_lines = len(nonblank_rows) - len(unique_hashes)
        per_file_hashes.update(nonblank_rows)
        inventory.append(
            {
                "source_id": "payloadsallthethings_sqli_intruder",
                "source_name": "PayloadsAllTheThings SQL Injection Intruder",
                "source_url": README_URL,
                "commit_hash": commit,
                "relative_path": rel(source_file),
                "file_name": source_file.name,
                "category": category,
                "dbms": dbms,
                "technique": technique,
                "nonblank_row_count": str(len(nonblank_rows)),
                "unique_payload_hash_count": str(len(unique_hashes)),
                "duplicate_line_count": str(duplicate_lines),
                "file_sha256": file_hash,
            }
        )

    return inventory, payloads, per_file_hashes


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def write_source_card(commit: str, taxonomy_rows: list[dict[str, str]], inventory: list[dict[str, str]]) -> None:
    total_files = len(inventory)
    total_rows = sum(int(row["nonblank_row_count"]) for row in inventory)
    text = [
        "# PayloadsAllTheThings SQLi Source Card",
        "",
        f"- Source URL: `{SOURCE_URL}`",
        f"- SQL Injection README URL: `{README_URL}`",
        f"- Raw source path: `GAN/Data/raw/payloadsallthethings`",
        f"- SQL Injection README path: `GAN/Data/raw/payloadsallthethings/SQL Injection/README.md`",
        f"- Intruder source path: `GAN/Data/raw/payloadsallthethings/SQL Injection/Intruder`",
        f"- Downloaded commit/hash: `{commit}`",
        f"- Retrieval mode: online git clone",
        f"- Intruder file count: {total_files}",
        f"- Nonblank seed row count: {total_rows}",
        "",
        "## Taxonomy Presence",
        "",
        "| Section | Present | Heading Level |",
        "| --- | --- | --- |",
    ]
    for row in taxonomy_rows:
        text.append(f"| {row['section']} | {row['present_in_readme']} | {row['heading_level']} |")
    text.append("")
    path = MANIFESTS / "payloadsallthethings_sqli_source_card.md"
    path.write_text("\n".join(text), encoding="utf-8")


def write_report(commit: str, taxonomy_rows: list[dict[str, str]], inventory: list[dict[str, str]], payloads: list[dict[str, str]], hash_counts: Counter[str]) -> None:
    by_category = Counter(row["category"] for row in payloads)
    by_dbms = Counter(row["dbms"] for row in payloads)
    duplicate_rows = sum(count - 1 for count in hash_counts.values() if count > 1)
    unique_rows = len(hash_counts)

    lines = [
        "# Teacher Resource Inventory",
        "",
        "## Source",
        "",
        f"- Online source URL: `{SOURCE_URL}`",
        f"- SQL Injection README URL: `{README_URL}`",
        f"- Raw source path: `GAN/Data/raw/payloadsallthethings`",
        f"- Downloaded commit/hash: `{commit}`",
        "",
        "## Generated Artifacts",
        "",
        "- `GAN/Data/manifests/payloadsallthethings_sqli_source_card.md`",
        "- `GAN/Data/manifests/teacher_seed_inventory.csv`",
        "- `GAN/Data/processed/teacher_seed_sqli_normalized.csv`",
        "- `GAN/Reproduction/baselines/payloadsallthethings_rule_baseline.md`",
        "",
        "## Taxonomy",
        "",
        "| Section | Present In README | Heading Level |",
        "| --- | --- | --- |",
    ]
    for row in taxonomy_rows:
        lines.append(f"| {row['section']} | {row['present_in_readme']} | {row['heading_level']} |")

    lines.extend(
        [
            "",
            "## Seed Statistics",
            "",
            f"- Intruder source files: {len(inventory)}",
            f"- Nonblank normalized rows: {len(payloads)}",
            f"- Unique payload hashes: {unique_rows}",
            f"- Duplicate rows by payload hash: {duplicate_rows}",
            "",
            "## Rows By Category",
            "",
            "| Category | Rows |",
            "| --- | ---: |",
        ]
    )
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
            "- This report contains taxonomy and aggregate counts only.",
            "- Detailed seed strings are stored only in `GAN/Data/processed/teacher_seed_sqli_normalized.csv`.",
            "- No offline source was used.",
            "",
        ]
    )
    (REPORTS / "00_teacher_resource_inventory.md").write_text("\n".join(lines), encoding="utf-8")


def write_baseline(commit: str, inventory: list[dict[str, str]], payloads: list[dict[str, str]], hash_counts: Counter[str]) -> None:
    by_technique = Counter(row["technique"] for row in payloads)
    duplicate_rows = sum(count - 1 for count in hash_counts.values() if count > 1)
    lines = [
        "# PayloadsAllTheThings Rule Baseline",
        "",
        f"- Source URL: `{SOURCE_URL}`",
        f"- Downloaded commit/hash: `{commit}`",
        "- Input path: `GAN/Data/raw/payloadsallthethings/SQL Injection/Intruder`",
        "- Normalized output: `GAN/Data/processed/teacher_seed_sqli_normalized.csv`",
        "",
        "## Baseline Scope",
        "",
        "- Reads online-downloaded Intruder text files.",
        "- Trims leading and trailing whitespace for normalized hashes.",
        "- Assigns coarse labels from source filenames.",
        "- Reports counts only in markdown artifacts.",
        "",
        "## Aggregate Counts",
        "",
        f"- Source files: {len(inventory)}",
        f"- Normalized rows: {len(payloads)}",
        f"- Duplicate rows by payload hash: {duplicate_rows}",
        "",
        "## Technique Distribution",
        "",
        "| Technique | Rows |",
        "| --- | ---: |",
    ]
    for technique, count in sorted(by_technique.items()):
        lines.append(f"| {technique} | {count} |")
    lines.append("")
    (BASELINES / "payloadsallthethings_rule_baseline.md").write_text("\n".join(lines), encoding="utf-8")


def update_recovery(commit: str, inventory: list[dict[str, str]], payloads: list[dict[str, str]], hash_counts: Counter[str]) -> None:
    duplicate_rows = sum(count - 1 for count in hash_counts.values() if count > 1)
    timestamp = datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()
    text = f"""# Recovery

- Current phase: Step 1 online-only PayloadsAllTheThings teacher seed setup
- Last completed step: Verification
- Next exact step: Start the next online-only teacher source ingestion step
- Updated artifacts:
  - `GAN/RECOVERY.md`
  - `GAN/Data/raw/payloadsallthethings`
  - `GAN/Reports/00_teacher_resource_inventory.md`
  - `GAN/Data/manifests/payloadsallthethings_sqli_source_card.md`
  - `GAN/Data/manifests/teacher_seed_inventory.csv`
  - `GAN/Data/processed/teacher_seed_sqli_normalized.csv`
  - `GAN/Reproduction/baselines/payloadsallthethings_rule_baseline.md`
- Online source URL: `{SOURCE_URL}`
- Primary SQL Injection README URL: `{README_URL}`
- Downloaded commit/hash: `{commit}`
- Command log summary:
  - Created `GAN` directory tree for raw data, manifests, processed data, reports, baselines, and scripts.
  - Downloaded online source into `GAN/Data/raw/payloadsallthethings`.
  - Confirmed `GAN/Data/raw/payloadsallthethings/SQL Injection/README.md`.
  - Confirmed `GAN/Data/raw/payloadsallthethings/SQL Injection/Intruder` with {len(inventory)} seed files.
  - Generated inventory, normalized CSV, source card, report, and baseline artifacts under `GAN`.
  - Verified generated artifact paths and CSV row counts.
- Row counts:
  - Intruder source files: {len(inventory)}
  - Normalized nonblank rows: {len(payloads)}
  - Unique payload hashes: {len(hash_counts)}
- Duplicate counts:
  - Duplicate rows by payload hash: {duplicate_rows}
- Blockers: none
- Last updated: `{timestamp}`
"""
    RECOVERY.write_text(text, encoding="utf-8")


def main() -> None:
    for path in (MANIFESTS, PROCESSED, REPORTS, BASELINES):
        path.mkdir(parents=True, exist_ok=True)

    if not README.is_file():
        raise FileNotFoundError(rel(README))
    if not INTRUDER.is_dir():
        raise FileNotFoundError(rel(INTRUDER))

    commit = git_commit()
    readme_text = read_text(README)
    taxonomy_rows = extract_taxonomy(readme_text)
    inventory, payloads, hash_counts = payload_rows(commit)

    write_csv(
        MANIFESTS / "teacher_seed_inventory.csv",
        inventory,
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
        ],
    )
    write_csv(
        PROCESSED / "teacher_seed_sqli_normalized.csv",
        payloads,
        [
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
        ],
    )
    write_source_card(commit, taxonomy_rows, inventory)
    write_report(commit, taxonomy_rows, inventory, payloads, hash_counts)
    write_baseline(commit, inventory, payloads, hash_counts)
    update_recovery(commit, inventory, payloads, hash_counts)

    duplicate_rows = sum(count - 1 for count in hash_counts.values() if count > 1)
    print(f"commit={commit}")
    print(f"source_files={len(inventory)}")
    print(f"normalized_rows={len(payloads)}")
    print(f"unique_payload_hashes={len(hash_counts)}")
    print(f"duplicate_rows={duplicate_rows}")


if __name__ == "__main__":
    main()
