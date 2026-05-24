# -*- coding: utf-8 -*-
"""
Phase 06 - Script 4: audit generated samples for condition consistency.

This is a heuristic aggregate audit for generated JSONL samples. It does not
execute payloads and does not print raw sample text into the report.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any


PHASE_DIR = Path(__file__).resolve().parent
DEFAULT_SAMPLE_DIR = PHASE_DIR / "outputs" / "gumbel_seqgan_smoke_balanced"
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"

SQL_SIGNAL_RE = re.compile(
    r"\b(select|union|from|where|insert|update|delete|drop|exec|alter|create|sleep|benchmark|waitfor)\b",
    re.IGNORECASE,
)

TECHNIQUE_HINTS: dict[str, re.Pattern[str]] = {
    "union_based": re.compile(r"\bunion\b|\bunion\s+all\b|\bselect\b", re.IGNORECASE),
    "time_blind": re.compile(r"\bsleep\b|\bbenchmark\b|\bwaitfor\b|\bdelay\b|\bpg_sleep\b", re.IGNORECASE),
    "boolean_blind": re.compile(r"\b(and|or)\b\s+[\w'\"_()]+\s*(=|>|<|like)\s*[\w'\"_()]+", re.IGNORECASE),
    "error_based": re.compile(r"\b(extractvalue|updatexml|floor|rand|group\s+by|having|convert|cast)\b", re.IGNORECASE),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Phase 6 generated samples for condition consistency.")
    parser.add_argument("--sample-dir", type=Path, default=DEFAULT_SAMPLE_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--report-name", default="06_gumbel_condition_audit_report.md")
    parser.add_argument("--title", default="06 - Condition Audit")
    parser.add_argument("--pattern", default="samples_step_*.jsonl")
    return parser.parse_args()


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, line in enumerate(handle, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON at {path}:{line_no}") from exc
            rows.append(row)
    return rows


def hint_match(technique: str, text: str) -> bool | None:
    if technique == "benign" or technique == "unknown":
        return None
    pattern = TECHNIQUE_HINTS.get(technique)
    if pattern is None:
        return None
    return bool(pattern.search(text))


def pct(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def audit_file(path: Path) -> dict[str, Any]:
    rows = load_jsonl(path)
    by_technique: dict[str, Counter[str]] = defaultdict(Counter)
    total = Counter()

    for row in rows:
        technique = str(row.get("technique", "unknown"))
        text = str(row.get("text", ""))
        has_sql_signal = bool(SQL_SIGNAL_RE.search(text))
        hint = hint_match(technique, text)

        total["samples"] += 1
        if has_sql_signal:
            total["sql_signal"] += 1
        if technique == "benign" and has_sql_signal:
            total["benign_sql_signal"] += 1
        if hint is True:
            total["technique_hint"] += 1
        if hint is not None:
            total["technique_hint_applicable"] += 1

        bucket = by_technique[technique]
        bucket["samples"] += 1
        if has_sql_signal:
            bucket["sql_signal"] += 1
        if technique == "benign" and has_sql_signal:
            bucket["benign_sql_signal"] += 1
        if hint is True:
            bucket["technique_hint"] += 1
        if hint is not None:
            bucket["technique_hint_applicable"] += 1

    step_match = re.search(r"(\d+)", path.stem)
    step = int(step_match.group(1)) if step_match else -1
    return {
        "path": str(path),
        "step": step,
        "samples": total["samples"],
        "sql_signal_rate": pct(total["sql_signal"], total["samples"]),
        "benign_sql_signal_rate": pct(total["benign_sql_signal"], by_technique.get("benign", Counter())["samples"]),
        "technique_hint_rate": pct(total["technique_hint"], total["technique_hint_applicable"]),
        "by_technique": {
            technique: {
                "samples": counts["samples"],
                "sql_signal_rate": pct(counts["sql_signal"], counts["samples"]),
                "benign_sql_signal_rate": pct(counts["benign_sql_signal"], counts["samples"]) if technique == "benign" else None,
                "technique_hint_rate": pct(counts["technique_hint"], counts["technique_hint_applicable"])
                if counts["technique_hint_applicable"]
                else None,
            }
            for technique, counts in sorted(by_technique.items())
        },
    }


def write_report(path: Path, audits: list[dict[str, Any]], title: str) -> None:
    latest = audits[-1] if audits else {}
    lines = [
        f"# {title}",
        "",
        "Scope: aggregate heuristic audit of generated sample JSONL files.",
        "Raw generated texts are intentionally omitted from this report.",
        "",
    ]
    if latest:
        lines.extend(
            [
                "## Latest Sample File",
                "",
                f"- Step: `{latest['step']}`",
                f"- Samples: `{latest['samples']}`",
                f"- SQL signal rate: `{latest['sql_signal_rate']:.4f}`",
                f"- Benign SQL signal rate: `{latest['benign_sql_signal_rate']:.4f}`",
                f"- Technique hint rate: `{latest['technique_hint_rate']:.4f}`",
                "",
            ]
        )

    lines.extend(
        [
            "## Step Trend",
            "",
            "| Step | Samples | SQL Signal | Benign SQL Signal | Technique Hint |",
            "|---:|---:|---:|---:|---:|",
        ]
    )
    for audit in audits:
        lines.append(
            "| {step} | {samples} | {sql:.4f} | {benign:.4f} | {hint:.4f} |".format(
                step=audit["step"],
                samples=audit["samples"],
                sql=audit["sql_signal_rate"],
                benign=audit["benign_sql_signal_rate"],
                hint=audit["technique_hint_rate"],
            )
        )

    if latest:
        lines.extend(["", "## Latest By Technique", "", "| Technique | Samples | SQL Signal | Benign SQL Signal | Technique Hint |", "|---|---:|---:|---:|---:|"])
        for technique, counts in latest["by_technique"].items():
            benign_rate = counts["benign_sql_signal_rate"]
            hint_rate = counts["technique_hint_rate"]
            lines.append(
                "| {technique} | {samples} | {sql:.4f} | {benign} | {hint} |".format(
                    technique=technique,
                    samples=counts["samples"],
                    sql=counts["sql_signal_rate"],
                    benign="n/a" if benign_rate is None else f"{benign_rate:.4f}",
                    hint="n/a" if hint_rate is None else f"{hint_rate:.4f}",
                )
            )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- High `benign_sql_signal_rate` means the generator is not cleanly separating benign conditioning from SQL-like payload generation.",
            "- Low `technique_hint_rate` means technique conditioning may be weak or the heuristic needs refinement.",
            "- This audit is advisory; use it with manual review before extending adversarial training.",
            "",
        ]
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    sample_paths = sorted(args.sample_dir.glob(args.pattern))
    if not sample_paths:
        raise FileNotFoundError(f"No sample files matched {args.sample_dir / args.pattern}")
    audits = [audit_file(path) for path in sample_paths]
    report_path = args.report_dir / args.report_name
    write_report(report_path, audits, args.title)
    latest = audits[-1]
    print(
        "condition_audit step={} samples={} benign_sql_signal_rate={:.4f} technique_hint_rate={:.4f}".format(
            latest["step"],
            latest["samples"],
            latest["benign_sql_signal_rate"],
            latest["technique_hint_rate"],
        )
    )
    print(f"report={report_path}")


if __name__ == "__main__":
    main()
