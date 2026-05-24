# -*- coding: utf-8 -*-
"""
Phase 08 - Script 7: offline detector/WAF-style evasion scoring.

This is a deterministic local evaluator, not a live WAF attack harness. It
reads generated sample JSONL, applies a small ensemble of SQLi-oriented
detectors, and writes a CSV compatible with phase08_03_evaluator_contract.py:

    sample_id,detected

The detector is intentionally conservative and transparent. It should be used
as an evasion proxy until a real held-out WAF/classifier oracle is wired in.
Raw payload text is not written to reports.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


PHASE_DIR = Path(__file__).resolve().parent
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"
DEFAULT_OUT_DIR = PHASE_DIR / "outputs" / "detector_results"

SPACE_RE = re.compile(r"\s+")
COMMENT_RE = re.compile(r"(--|#|/\*|\*/|__comment__)", re.IGNORECASE)
ENCODING_RE = re.compile(r"(%[0-9a-f]{2}|&#?[a-z0-9]+;|\\x[0-9a-f]{2})", re.IGNORECASE)
SQL_KEYWORD_RE = re.compile(
    r"\b(select|union|from|where|insert|update|delete|drop|exec|execute|alter|create|join|having|group|order|limit)\b",
    re.IGNORECASE,
)
BOOLEAN_RE = re.compile(
    r"\b(and|or)\b\s+([_\w'\"()]+|\d+)\s*(=|<>|!=|>|<|>=|<=|like)\s*([_\w'\"()]+|\d+)",
    re.IGNORECASE,
)
TIME_RE = re.compile(r"\b(sleep|pg_sleep|benchmark|waitfor|delay|dbms_pipe)\b", re.IGNORECASE)
ERROR_RE = re.compile(r"\b(extractvalue|updatexml|utl_inaddr|floor|rand|group\s+by|cast|convert|exp)\b", re.IGNORECASE)
UNION_RE = re.compile(r"\bunion\b(?:\s+all)?\s+\bselect\b", re.IGNORECASE)
STACKED_RE = re.compile(r";\s*(select|insert|update|delete|drop|exec|alter|create)\b", re.IGNORECASE)
PLACEHOLDER_RE = re.compile(r"__[a-z0-9_]+__", re.IGNORECASE)
SUSPICIOUS_OP_RE = re.compile(r"(@@|\|\||&&|/\*\*/|char\s*\(|chr\s*\(|concat\s*\()", re.IGNORECASE)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Score generated samples with a deterministic SQLi detector proxy.")
    parser.add_argument("--samples", type=Path, required=True, help="JSONL samples with sample_id/text/technique.")
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--name", default=None, help="Base output name. Defaults to sample file stem.")
    parser.add_argument("--threshold", type=float, default=3.0, help="Detection score threshold.")
    parser.add_argument("--strict-threshold", type=float, default=5.0, help="High-confidence threshold for report only.")
    return parser.parse_args()


def ensure_under_phase(path: Path) -> Path:
    resolved = path.resolve()
    phase = PHASE_DIR.resolve()
    if resolved != phase and phase not in resolved.parents:
        raise ValueError(f"Refusing to write outside Phase 8: {resolved}")
    return resolved


def normalize(text: str) -> str:
    text = text.replace("/**/", " ")
    text = SPACE_RE.sub(" ", text.strip().lower())
    return text


def load_samples(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            rows.append(
                {
                    "sample_id": str(payload.get("sample_id", idx)),
                    "technique": str(payload.get("technique", "unknown")),
                    "text": str(payload.get("text", "")),
                }
            )
    return rows


def balanced_delimiters(text: str) -> bool:
    stack: list[str] = []
    pairs = {"(": ")", "[": "]", "{": "}"}
    single_quotes = 0
    double_quotes = 0
    for ch in text:
        if ch in pairs:
            stack.append(pairs[ch])
        elif ch in pairs.values():
            if not stack or stack.pop() != ch:
                return False
        elif ch == "'":
            single_quotes += 1
        elif ch == '"':
            double_quotes += 1
    return not stack and single_quotes % 2 == 0 and double_quotes % 2 == 0


def score_sample(text: str) -> tuple[float, list[str]]:
    norm = normalize(text)
    reasons: list[str] = []
    score = 0.0

    def add(condition: bool, points: float, reason: str) -> None:
        nonlocal score
        if condition:
            score += points
            reasons.append(reason)

    add(bool(UNION_RE.search(norm)), 3.0, "union_select")
    add(bool(BOOLEAN_RE.search(norm)), 2.0, "boolean_condition")
    add(bool(TIME_RE.search(norm)), 2.5, "time_function")
    add(bool(ERROR_RE.search(norm)), 2.5, "error_function")
    add(bool(STACKED_RE.search(norm)), 2.0, "stacked_query")
    add(bool(COMMENT_RE.search(norm)), 1.0, "comment_marker")
    add(bool(ENCODING_RE.search(norm)), 1.0, "encoding_marker")
    add(bool(SUSPICIOUS_OP_RE.search(norm)), 1.0, "suspicious_operator")
    add(len(SQL_KEYWORD_RE.findall(norm)) >= 3, 1.5, "keyword_density")
    add(len(PLACEHOLDER_RE.findall(norm)) >= 3, 0.5, "placeholder_density")
    add(not balanced_delimiters(norm), 0.5, "unbalanced_delimiters")

    # Simple interaction terms: these are closer to WAF-style signatures than
    # standalone keyword hits.
    add(bool(SQL_KEYWORD_RE.search(norm)) and bool(COMMENT_RE.search(norm)), 1.0, "keyword_comment_combo")
    add(bool(SQL_KEYWORD_RE.search(norm)) and bool(BOOLEAN_RE.search(norm)), 1.0, "keyword_boolean_combo")
    add(bool(UNION_RE.search(norm)) and bool(COMMENT_RE.search(norm)), 1.0, "union_comment_combo")

    return score, reasons


def write_outputs(args: argparse.Namespace, rows: list[dict[str, Any]], results: list[dict[str, Any]]) -> dict[str, Any]:
    out_dir = ensure_under_phase(args.out_dir)
    report_dir = ensure_under_phase(args.report_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    base = args.name or args.samples.stem

    csv_path = out_dir / f"{base}_detector_results.csv"
    json_path = report_dir / f"08_detector_{base}.json"
    md_path = report_dir / f"08_detector_{base}.md"

    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sample_id", "detected", "score", "reasons", "technique"])
        writer.writeheader()
        for row in results:
            writer.writerow(row)

    counts = Counter()
    reason_counts: Counter[str] = Counter()
    by_technique: dict[str, Counter[str]] = defaultdict(Counter)
    for result in results:
        detected = result["detected"] == "true"
        strict = float(result["score"]) >= args.strict_threshold
        technique = str(result["technique"])
        counts["samples"] += 1
        counts["detected"] += int(detected)
        counts["bypassed"] += int(not detected)
        counts["strict_detected"] += int(strict)
        by_technique[technique]["samples"] += 1
        by_technique[technique]["detected"] += int(detected)
        by_technique[technique]["strict_detected"] += int(strict)
        for reason in str(result["reasons"]).split(";"):
            if reason:
                reason_counts[reason] += 1

    payload = {
        "samples": str(args.samples),
        "detector_results": str(csv_path),
        "threshold": args.threshold,
        "strict_threshold": args.strict_threshold,
        "n_samples": counts["samples"],
        "detected_rate": counts["detected"] / max(counts["samples"], 1),
        "bypass_rate": counts["bypassed"] / max(counts["samples"], 1),
        "strict_detected_rate": counts["strict_detected"] / max(counts["samples"], 1),
        "top_reasons": reason_counts.most_common(20),
        "by_technique": {
            technique: {
                "samples": c["samples"],
                "detected_rate": c["detected"] / max(c["samples"], 1),
                "bypass_rate": 1.0 - c["detected"] / max(c["samples"], 1),
                "strict_detected_rate": c["strict_detected"] / max(c["samples"], 1),
            }
            for technique, c in sorted(by_technique.items())
        },
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# 08 - Detector Evasion Proxy Report",
        "",
        "Scope: deterministic offline SQLi detector proxy. Raw payloads are intentionally omitted.",
        "",
        "## Inputs",
        "",
        f"- Samples: `{args.samples}`",
        f"- Detector results CSV: `{csv_path}`",
        f"- Threshold: `{args.threshold}`",
        f"- Strict threshold: `{args.strict_threshold}`",
        f"- Samples evaluated: `{payload['n_samples']:,}`",
        "",
        "## Summary",
        "",
        f"- Detected rate: `{payload['detected_rate']:.4f}`",
        f"- Bypass rate: `{payload['bypass_rate']:.4f}`",
        f"- Strict detected rate: `{payload['strict_detected_rate']:.4f}`",
        "",
        "## By Technique",
        "",
        "| Technique | Samples | Detected | Bypass | Strict Detected |",
        "|---|---:|---:|---:|---:|",
    ]
    for technique, data in payload["by_technique"].items():
        lines.append(
            f"| {technique} | {data['samples']:,} | {data['detected_rate']:.4f} | {data['bypass_rate']:.4f} | {data['strict_detected_rate']:.4f} |"
        )
    lines.extend(["", "## Top Reasons", "", "| Reason | Count |", "|---|---:|"])
    for reason, count in payload["top_reasons"]:
        lines.append(f"| {reason} | {count:,} |")
    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- This is an evasion proxy, not a real WAF result.",
            "- Use the CSV with `phase08_03_evaluator_contract.py --detector-results`.",
            "- A main thesis claim still needs a stronger held-out WAF/classifier oracle.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"detector_results={csv_path}")
    print(f"report={md_path}")
    print(f"json={json_path}")
    return payload


def main() -> None:
    args = parse_args()
    samples = load_samples(args.samples)
    results: list[dict[str, Any]] = []
    for row in samples:
        score, reasons = score_sample(row["text"])
        detected = score >= args.threshold
        results.append(
            {
                "sample_id": row["sample_id"],
                "detected": "true" if detected else "false",
                "score": f"{score:.3f}",
                "reasons": ";".join(reasons),
                "technique": row["technique"],
            }
        )
    write_outputs(args, samples, results)


if __name__ == "__main__":
    main()
