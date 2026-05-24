# -*- coding: utf-8 -*-
"""
Phase 06 - Script 5: source condition audit.

Audits Phase 5 parquet sources used by Phase 6 training/evaluation. The report
is aggregate-only and intentionally omits raw payload text.
"""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pyarrow.parquet as pq


PHASE_DIR = Path(__file__).resolve().parent
ROOT = PHASE_DIR.parent.parent
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"
DEFAULT_SOURCES = [
    ROOT / "Guiding" / "Phase 5" / "outputs" / "full" / "gold.parquet",
    ROOT / "Guiding" / "Phase 5" / "outputs" / "full" / "verified_dev.parquet",
    ROOT / "Guiding" / "Phase 5" / "outputs" / "full" / "verified_test.parquet",
]

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

COLUMNS = [
    "payload_delex_v5",
    "technique_primary",
    "is_sqli",
    "label_source",
    "syntax_validity",
    "conflict_flags",
    "quality_band",
    "confidence_score",
    "split",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit Phase 6 parquet sources for condition consistency.")
    parser.add_argument("--sources", type=Path, nargs="*", default=DEFAULT_SOURCES)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--report-name", default="06_source_condition_audit_report.md")
    parser.add_argument("--batch-size", type=int, default=100000)
    return parser.parse_args()


def pct(numerator: int, denominator: int) -> float:
    return numerator / denominator if denominator else 0.0


def hint_match(technique: str, text: str) -> bool | None:
    if technique in {"benign", "unknown"}:
        return None
    pattern = TECHNIQUE_HINTS.get(technique)
    if pattern is None:
        return None
    return bool(pattern.search(text))


def add_counter(counter: Counter[str], value: Any) -> None:
    counter.update([str(value) if value is not None else ""])


def audit_source(path: Path, batch_size: int) -> dict[str, Any]:
    parquet = pq.ParquetFile(path)
    total = Counter()
    by_technique: dict[str, Counter[str]] = defaultdict(Counter)
    counters = {
        "technique_primary": Counter(),
        "is_sqli": Counter(),
        "label_source": Counter(),
        "syntax_validity": Counter(),
        "conflict_flags": Counter(),
        "quality_band": Counter(),
        "split": Counter(),
    }
    confidence_sum = 0.0
    confidence_count = 0

    for batch in parquet.iter_batches(batch_size=batch_size, columns=COLUMNS):
        data = batch.to_pydict()
        rows = len(data["technique_primary"])
        for idx in range(rows):
            text = str(data["payload_delex_v5"][idx] or "")
            technique = str(data["technique_primary"][idx] or "unknown")
            has_sql_signal = bool(SQL_SIGNAL_RE.search(text))
            hint = hint_match(technique, text)

            total["rows"] += 1
            if has_sql_signal:
                total["sql_signal"] += 1
            if technique == "benign" and has_sql_signal:
                total["benign_sql_signal"] += 1
            if hint is True:
                total["technique_hint"] += 1
            if hint is not None:
                total["technique_hint_applicable"] += 1

            bucket = by_technique[technique]
            bucket["rows"] += 1
            if has_sql_signal:
                bucket["sql_signal"] += 1
            if technique == "benign" and has_sql_signal:
                bucket["benign_sql_signal"] += 1
            if hint is True:
                bucket["technique_hint"] += 1
            if hint is not None:
                bucket["technique_hint_applicable"] += 1

            for key, counter in counters.items():
                value = data[key][idx]
                if key == "conflict_flags":
                    flags = str(value or "none")
                    for flag in flags.split("|"):
                        counter.update([flag or "none"])
                else:
                    add_counter(counter, value)

            confidence = data["confidence_score"][idx]
            if confidence is not None:
                confidence_sum += float(confidence)
                confidence_count += 1

    return {
        "path": str(path),
        "name": path.name,
        "rows": total["rows"],
        "sql_signal_rate": pct(total["sql_signal"], total["rows"]),
        "benign_sql_signal_rate": pct(total["benign_sql_signal"], by_technique.get("benign", Counter())["rows"]),
        "technique_hint_rate": pct(total["technique_hint"], total["technique_hint_applicable"]),
        "mean_confidence": pct(int(confidence_sum * 1000000), confidence_count) / 1000000 if confidence_count else 0.0,
        "counters": {key: dict(counter.most_common()) for key, counter in counters.items()},
        "by_technique": {
            technique: {
                "rows": counts["rows"],
                "sql_signal_rate": pct(counts["sql_signal"], counts["rows"]),
                "benign_sql_signal_rate": pct(counts["benign_sql_signal"], counts["rows"]) if technique == "benign" else None,
                "technique_hint_rate": pct(counts["technique_hint"], counts["technique_hint_applicable"])
                if counts["technique_hint_applicable"]
                else None,
            }
            for technique, counts in sorted(by_technique.items())
        },
    }


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_report(path: Path, audits: list[dict[str, Any]]) -> None:
    lines = [
        "# 06 - Source Condition Audit",
        "",
        "Scope: aggregate audit of Phase 5 parquet sources consumed by Phase 6.",
        "Raw payload text is intentionally omitted.",
        "",
        "## Source Summary",
        "",
        "| Source | Rows | SQL Signal | Benign SQL Signal | Technique Hint | Mean Confidence |",
        "|---|---:|---:|---:|---:|---:|",
    ]
    for audit in audits:
        lines.append(
            "| {name} | {rows:,} | {sql:.4f} | {benign:.4f} | {hint:.4f} | {confidence:.4f} |".format(
                name=audit["name"],
                rows=audit["rows"],
                sql=audit["sql_signal_rate"],
                benign=audit["benign_sql_signal_rate"],
                hint=audit["technique_hint_rate"],
                confidence=audit["mean_confidence"],
            )
        )

    for audit in audits:
        lines.extend(
            [
                "",
                f"## {audit['name']} By Technique",
                "",
                "| Technique | Rows | SQL Signal | Benign SQL Signal | Technique Hint |",
                "|---|---:|---:|---:|---:|",
            ]
        )
        for technique, counts in audit["by_technique"].items():
            benign_rate = counts["benign_sql_signal_rate"]
            hint_rate = counts["technique_hint_rate"]
            lines.append(
                "| {technique} | {rows:,} | {sql:.4f} | {benign} | {hint} |".format(
                    technique=technique,
                    rows=counts["rows"],
                    sql=counts["sql_signal_rate"],
                    benign="n/a" if benign_rate is None else f"{benign_rate:.4f}",
                    hint="n/a" if hint_rate is None else f"{hint_rate:.4f}",
                )
            )

    gold = next((audit for audit in audits if audit["name"] == "gold.parquet"), None)
    if gold:
        gold_counts = gold["counters"]["technique_primary"]
        total = max(gold["rows"], 1)
        benign = int(gold_counts.get("benign", 0))
        attack = gold["rows"] - benign
        lines.extend(
            [
                "",
                "## Training Implications",
                "",
                f"- Gold benign rows: `{benign:,}` (`{benign / total:.4%}`).",
                f"- Gold non-benign rows: `{attack:,}` (`{attack / total:.4%}`).",
                f"- Gold benign SQL signal rate: `{gold['benign_sql_signal_rate']:.4f}`.",
                "- If generated benign samples remain SQL-like while source benign SQL signal is low, the likely issue is class imbalance or weak conditioning rather than dirty gold benign labels.",
                "- For SQLi generation, an attack-only generator is a defensible next branch; for benign-vs-attack generation, use balanced sampling or a separate benign model.",
                "",
            ]
        )

    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    audits = [audit_source(path.resolve(), args.batch_size) for path in args.sources]
    report_path = args.report_dir / args.report_name
    json_path = args.report_dir / args.report_name.replace(".md", ".json")
    write_report(report_path, audits)
    write_json(json_path, audits)
    gold = next((audit for audit in audits if audit["name"] == "gold.parquet"), audits[0])
    print(
        "source_condition_audit gold_rows={} benign_sql_signal_rate={:.4f} technique_hint_rate={:.4f}".format(
            gold["rows"],
            gold["benign_sql_signal_rate"],
            gold["technique_hint_rate"],
        )
    )
    print(f"report={report_path}")
    print(f"json={json_path}")


if __name__ == "__main__":
    main()
