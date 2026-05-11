import argparse
import csv
import logging
import sys
from collections import defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from rules import ALL_RULES, Correction


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("validator")


def read_csv(path: str) -> tuple[list[dict], list[str]]:
    with open(path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = []
        for i, row in enumerate(reader):
            cleaned = {}
            for k, v in row.items():
                key = k.strip().strip('"').strip("'")
                cleaned[key] = v
            if "row_index" not in cleaned or not cleaned["row_index"]:
                cleaned["row_index"] = str(i)
            rows.append(cleaned)
        fieldnames = reader.fieldnames or []
        fieldnames = [f.strip().strip('"').strip("'") for f in fieldnames]
        if "row_index" not in fieldnames:
            fieldnames = ["row_index"] + fieldnames
    return rows, fieldnames


def write_csv(path: str, rows: list[dict], fieldnames: list[str]):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_validation(rows: list[dict]) -> list[Correction]:
    corrections = []
    for row in rows:
        for rule_fn in ALL_RULES:
            try:
                corr = rule_fn(row)
                if corr:
                    corrections.append(corr)
            except Exception as e:
                logger.warning("Error in rule %s for row %s: %s",
                               rule_fn.__name__, row.get("row_index"), e)
    return corrections


def apply_corrections(rows: list[dict], corrections: list[Correction]) -> list[dict]:
    corr_map = defaultdict(dict)
    for c in corrections:
        corr_map[c.row_index][c.field] = c.new_value

    updated = []
    for row in rows:
        row_idx = int(row["row_index"])
        if row_idx in corr_map:
            row = dict(row)
            for field, new_val in corr_map[row_idx].items():
                if new_val:
                    row[field] = new_val
        updated.append(row)
    return updated


def cmd_validate(args):
    rows, fieldnames = read_csv(args.input)
    logger.info("Loaded %d rows from %s", len(rows), args.input)
    corrections = run_validation(rows)
    logger.info("Found %d corrections", len(corrections))

    if args.output:
        corr_fieldnames = ["row_index", "field", "old_value", "new_value", "rule", "reason"]
        write_csv(args.output, [
            {"row_index": c.row_index, "field": c.field, "old_value": c.old_value,
             "new_value": c.new_value, "rule": c.rule, "reason": c.reason}
            for c in corrections
        ], corr_fieldnames)
        logger.info("Wrote corrections to %s", args.output)


def cmd_normalize(args):
    rows, fieldnames = read_csv(args.input)
    logger.info("Loaded %d rows from %s", len(rows), args.input)
    corrections = run_validation(rows)
    logger.info("Found %d corrections", len(corrections))

    updated = apply_corrections(rows, corrections)
    write_csv(args.output, updated, fieldnames)
    logger.info("Wrote normalized dataset (%d rows) to %s", len(updated), args.output)

    if args.corrections:
        corr_fieldnames = ["row_index", "field", "old_value", "new_value", "rule", "reason"]
        write_csv(args.corrections, [
            {"row_index": c.row_index, "field": c.field, "old_value": c.old_value,
             "new_value": c.new_value, "rule": c.rule, "reason": c.reason}
            for c in corrections
        ], corr_fieldnames)
        logger.info("Wrote corrections to %s", args.corrections)


def cmd_report(args):
    rows, fieldnames = read_csv(args.input)
    corrections = run_validation(rows)

    rule_counts = defaultdict(int)
    field_counts = defaultdict(int)
    for c in corrections:
        rule_counts[c.rule] += 1
        field_counts[c.field] += 1

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    report_lines = [
        "# Validation Report",
        f"Generated from: {args.input}",
        f"Total rows: {len(rows)}",
        f"Total corrections: {len(corrections)}",
        "",
        "## Corrections by Rule",
    ]
    for rule, count in sorted(rule_counts.items()):
        report_lines.append(f"- {rule}: {count}")
    report_lines.extend(["", "## Corrections by Field"])
    for field, count in sorted(field_counts.items()):
        report_lines.append(f"- {field}: {count}")

    report_path = output_dir / "validation_report.md"
    report_path.write_text("\n".join(report_lines), encoding="utf-8")
    logger.info("Wrote report to %s", report_path)


def main():
    parser = argparse.ArgumentParser(description="SQLi Label Validator")
    sub = parser.add_subparsers(dest="command", required=True)

    p_validate = sub.add_parser("validate", help="Find corrections without applying")
    p_validate.add_argument("input", help="Input CSV path")
    p_validate.add_argument("--output", "-o", default="corrections.csv")

    p_normalize = sub.add_parser("normalize", help="Apply corrections and output clean CSV")
    p_normalize.add_argument("input", help="Input CSV path")
    p_normalize.add_argument("--output", "-o", required=True, help="Output CSV path")
    p_normalize.add_argument("--corrections", help="Optional corrections output path")

    p_report = sub.add_parser("report", help="Generate validation report")
    p_report.add_argument("input", help="Input CSV path")
    p_report.add_argument("--output-dir", default="./report")

    args = parser.parse_args()
    if args.command == "validate":
        cmd_validate(args)
    elif args.command == "normalize":
        cmd_normalize(args)
    elif args.command == "report":
        cmd_report(args)


if __name__ == "__main__":
    main()
