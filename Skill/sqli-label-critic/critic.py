import argparse
import csv
import json
import logging
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from reviewer import run_basic_checks, VerdictResult
from extended_checks import check_c6_confidence_calibration, check_c7_structural_integrity, check_c8_historical_consistency
from auditor import benign_audit, find_conflicts, AuditReport, ConflictGroup


logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("critic")


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


def review_row(row: dict, extended_checks: list[str] | None = None) -> dict:
    output_row = dict(row)

    verdict, check_results = run_basic_checks(row)
    evidence_parts = []
    corrections = {}

    for r in check_results:
        if r.verdict != "PASS":
            evidence_parts.append(f"[{r.check}] {r.evidence}")
        if r.correction:
            corrections.update(r.correction)

    if extended_checks:
        extended_fns = {
            "confidence": check_c6_confidence_calibration,
            "structure": check_c7_structural_integrity,
            "historical": check_c8_historical_consistency,
        }
        for ec_name in extended_checks:
            fn = extended_fns.get(ec_name)
            if fn:
                try:
                    ec_result = fn(row)
                    if ec_result:
                        evidence_parts.append(f"[{ec_result.check}] {ec_result.evidence}")
                        if ec_result.verdict == "REJECT" and verdict != "REJECT":
                            verdict = "REJECT"
                        if ec_result.correction:
                            corrections.update(ec_result.correction)
                except Exception as e:
                    logger.warning("Extended check %s failed for row %s: %s",
                                   ec_name, row.get("row_index"), e)

    output_row["verdict"] = verdict
    output_row["critic_evidence"] = " | ".join(evidence_parts) if evidence_parts else "All checks passed"
    output_row["correction_json"] = json.dumps(corrections) if corrections else ""

    return output_row


def cmd_review(args):
    rows, fieldnames = read_csv(args.input)
    logger.info("Loaded %d rows from %s", len(rows), args.input)

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    extended = []
    if args.extended_checks:
        extended = [c.strip() for c in args.extended_checks.split(",")]

    reviewed = []
    for row in rows:
        reviewed.append(review_row(row, extended))

    output_fields = fieldnames + ["verdict", "critic_evidence", "correction_json"]

    results_path = output_dir / "critic_results.csv"
    write_csv(str(results_path), reviewed, output_fields)
    logger.info("Wrote %d rows to %s", len(reviewed), results_path)

    rejected = [r for r in reviewed if r.get("verdict") == "REJECT"]
    flagged = [r for r in reviewed if r.get("verdict") == "FLAG"]

    if rejected:
        rejected_path = output_dir / "critic_rejected.csv"
        write_csv(str(rejected_path), rejected, output_fields)
        logger.info("Wrote %d rejected rows to %s", len(rejected), rejected_path)

    if flagged:
        flagged_path = output_dir / "critic_flagged.csv"
        write_csv(str(flagged_path), flagged, output_fields)
        logger.info("Wrote %d flagged rows to %s", len(flagged), flagged_path)

    verdict_counts = Counter(r.get("verdict", "UNKNOWN") for r in reviewed)

    if args.audit_sample > 0:
        audit = benign_audit(reviewed, sample_size=args.audit_sample)
        _write_audit_report(output_dir, audit)

    conflicts = find_conflicts(reviewed)
    if conflicts:
        _write_conflicts(output_dir, conflicts, output_fields)

    summary_lines = [
        "# Critic Review Summary",
        f"Generated from: {args.input}",
        f"Total rows: {len(reviewed)}",
        "",
        "## Verdict Distribution",
    ]
    for verdict, count in sorted(verdict_counts.items()):
        pct = count / len(reviewed) * 100
        summary_lines.append(f"- **{verdict}**: {count} ({pct:.1f}%)")
    summary_lines.extend([
        "",
        "## Key Metrics",
        f"- REJECT rate: {verdict_counts.get('REJECT', 0) / len(reviewed) * 100:.1f}%",
        f"- FLAG rate: {verdict_counts.get('FLAG', 0) / len(reviewed) * 100:.1f}%",
        f"- PASS rate: {verdict_counts.get('PASS', 0) / len(reviewed) * 100:.1f}%",
        "",
        "## Recommendations",
    ])
    if verdict_counts.get("REJECT", 0) > len(reviewed) * 0.1:
        summary_lines.append("- High REJECT rate (>10%): consider re-running sqli-labeler")
    if verdict_counts.get("PASS", 0) / len(reviewed) < 0.9:
        summary_lines.append("- PASS rate < 90%: quality issues detected, review flagged rows")

    if args.audit_sample > 0:
        summary_lines.extend([
            "",
            f"## Benign Audit (sample={args.audit_sample})",
            f"- Total benign: {audit.total_benign}",
            f"- False negative rate: {audit.fn_rate:.1f}%",
            f"- Recommendation: {audit.recommendation}",
        ])

    if conflicts:
        summary_lines.extend([
            "",
            f"## Conflict Duplicates ({len(conflicts)})",
        ])
        for c in conflicts[:10]:
            summary_lines.append(f"- Payload: {c.payload[:50]}... Rows: {c.rows} Verdict: {c.verdict}")

    summary_path = output_dir / "critic_summary.md"
    summary_path.write_text("\n".join(summary_lines), encoding="utf-8")
    logger.info("Wrote summary to %s", summary_path)


def cmd_audit_benign(args):
    rows, _ = read_csv(args.input)
    audit = benign_audit(rows, sample_size=args.sample)

    print(f"Total benign rows: {audit.total_benign}")
    print(f"Sample size: {audit.sample_size}")
    print(f"False negatives found: {len(audit.false_negatives)}")
    print(f"False negative rate: {audit.fn_rate:.1f}%")
    print(f"Recommendation: {audit.recommendation}")

    if audit.false_negatives:
        print("\nFalse negatives (first 20):")
        for fn in audit.false_negatives[:20]:
            print(f"  Row {fn['row_index']}: keywords={fn['keywords']}")


def cmd_find_conflicts(args):
    rows, _ = read_csv(args.input)
    conflicts = find_conflicts(rows)

    if not conflicts:
        print("No conflicts found")
        return

    print(f"Found {len(conflicts)} conflict groups:")
    for c in conflicts:
        print(f"\n  Payload: {c.payload[:60]}...")
        print(f"  Rows: {c.rows}")
        print(f"  Types: {c.conflict_types}")
        print(f"  Verdict: {c.verdict}")
        print(f"  Resolution: {c.resolution}")


def cmd_export_master(args):
    rows, fieldnames = read_csv(args.input)
    passed = [r for r in rows if r.get("verdict") in ("PASS", "FLAG")]

    output_fields = [f for f in fieldnames if f not in ("verdict", "critic_evidence", "correction_json")]

    cleaned = []
    for row in passed:
        clean = {k: v for k, v in row.items() if k in output_fields}
        if "correction_json" in row and row["correction_json"]:
            try:
                corrections = json.loads(row["correction_json"])
                for field, value in corrections.items():
                    if field in output_fields and value:
                        clean[field] = value
            except json.JSONDecodeError:
                pass
        cleaned.append(clean)

    write_csv(args.output, cleaned, output_fields)
    logger.info("Exported master dataset (%d rows) to %s", len(cleaned), args.output)


def _write_audit_report(output_dir: Path, audit: AuditReport):
    lines = [
        "# Benign Audit Report",
        f"Total benign: {audit.total_benign}",
        f"Sample size: {audit.sample_size}",
        f"False negatives: {len(audit.false_negatives)}",
        f"FN rate: {audit.fn_rate:.1f}%",
        f"Recommendation: {audit.recommendation}",
        "",
    ]
    if audit.false_negatives:
        lines.append("## False Negatives")
        for fn in audit.false_negatives:
            lines.append(f"- Row {fn['row_index']}: keywords={fn['keywords']} | {fn['payload']}")

    report_path = output_dir / "critic_audit_benign.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info("Wrote benign audit to %s", report_path)


def _write_conflicts(output_dir: Path, conflicts: list[ConflictGroup],
                     output_fields: list[str]):
    rows = []
    for c in conflicts:
        for row_idx in c.rows:
            rows.append({
                "row_index": row_idx,
                "payload": c.payload,
                "conflict_types": ", ".join(c.conflict_types),
                "verdict": c.verdict,
                "resolution": c.resolution,
            })

    if rows:
        conflict_fields = ["row_index", "payload", "conflict_types", "verdict", "resolution"]
        conflict_path = output_dir / "critic_conflicts.csv"
        write_csv(str(conflict_path), rows, conflict_fields)
        logger.info("Wrote %d conflict rows to %s", len(rows), conflict_path)


def main():
    parser = argparse.ArgumentParser(description="SQLi Label Critic")
    sub = parser.add_subparsers(dest="command", required=True)

    p_review = sub.add_parser("review", help="Run full critic review")
    p_review.add_argument("input", help="Input CSV path")
    p_review.add_argument("--output-dir", default="./output")
    p_review.add_argument("--extended-checks",
                         help="Comma-separated: confidence,structure,historical")
    p_review.add_argument("--audit-sample", type=int, default=500,
                         help="Benign audit sample size (0 to skip)")

    p_audit = sub.add_parser("audit-benign", help="Run benign audit only")
    p_audit.add_argument("input", help="Input CSV path")
    p_audit.add_argument("--sample", type=int, default=500)

    p_conflicts = sub.add_parser("find-conflicts", help="Find conflict duplicates")
    p_conflicts.add_argument("input", help="Input CSV path")

    p_export = sub.add_parser("export-master", help="Export master dataset from critic results")
    p_export.add_argument("input", help="Critic results CSV path")
    p_export.add_argument("--output", "-o", required=True, help="Output master CSV path")

    args = parser.parse_args()
    if args.command == "review":
        cmd_review(args)
    elif args.command == "audit-benign":
        cmd_audit_benign(args)
    elif args.command == "find-conflicts":
        cmd_find_conflicts(args)
    elif args.command == "export-master":
        cmd_export_master(args)


if __name__ == "__main__":
    main()
