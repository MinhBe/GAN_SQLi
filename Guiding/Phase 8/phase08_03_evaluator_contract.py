# -*- coding: utf-8 -*-
"""
Phase 08 - Script 3: evaluator contract smoke implementation.

This script evaluates sample files without treating weak proxy metrics as
ground truth. It separates validity, novelty, and evasion axes. Evasion is
reported as missing unless detector results are supplied.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq


if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


PHASE_DIR = Path(__file__).resolve().parent
ROOT = PHASE_DIR.parent.parent
DEFAULT_REFERENCE = ROOT / "Guiding" / "Phase 5" / "outputs" / "full" / "gold.parquet"
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"

SPACE_RE = re.compile(r"\s+")
SQL_SIGNAL_RE = re.compile(
    r"\b(select|union|from|where|insert|update|delete|drop|exec|alter|create|sleep|benchmark|waitfor|and|or)\b",
    re.IGNORECASE,
)
TECHNIQUE_HINTS: dict[str, re.Pattern[str]] = {
    "union_based": re.compile(r"\bunion\b|\bunion\s+all\b|\bselect\b", re.IGNORECASE),
    "time_blind": re.compile(r"\bsleep\b|\bbenchmark\b|\bwaitfor\b|\bdelay\b|\bpg_sleep\b", re.IGNORECASE),
    "boolean_blind": re.compile(r"\b(and|or)\b\s+[\w'\"_()]+\s*(=|>|<|like|!=|<>)\s*[\w'\"_()]+", re.IGNORECASE),
    "error_based": re.compile(r"\b(extractvalue|updatexml|floor|rand|group\s+by|having|convert|cast|exp)\b", re.IGNORECASE),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Evaluate samples under the Phase 8 contract.")
    parser.add_argument("--samples", type=Path, required=True, help="JSONL samples with `text` and optional `technique`.")
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE, help="Train reference parquet for novelty checks.")
    parser.add_argument("--reference-text-col", default="payload_delex_v5")
    parser.add_argument("--reference-batch-size", type=int, default=100000)
    parser.add_argument("--reference-limit", type=int, default=None)
    parser.add_argument("--detector-results", type=Path, default=None, help="Optional CSV with columns sample_id,detected.")
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--report-name", default="08_evaluator_contract_report.md")
    parser.add_argument("--json-name", default="08_evaluator_contract_report.json")
    return parser.parse_args()


def normalize_template(text: str) -> str:
    return SPACE_RE.sub(" ", text.strip().lower())


def hash_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:20]


def hash_template(text: str) -> str:
    return hash_text(normalize_template(text))


def pct(num: int, den: int) -> float:
    return num / den if den else 0.0


def load_samples(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle):
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            text = str(row.get("text", ""))
            rows.append(
                {
                    "sample_id": str(row.get("sample_id", idx)),
                    "technique": str(row.get("technique", "unknown")),
                    "text": text,
                    "raw_hash": hash_text(text),
                    "template_hash": hash_template(text),
                }
            )
    return rows


def balanced_delimiters(text: str) -> bool:
    pairs = {"(": ")", "[": "]", "{": "}"}
    stack: list[str] = []
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


def technique_hint(technique: str, text: str) -> bool | None:
    if technique in {"benign", "unknown"}:
        return None
    pattern = TECHNIQUE_HINTS.get(technique)
    if pattern is None:
        return None
    return bool(pattern.search(text))


def maybe_sqlglot_parse(text: str) -> tuple[bool | None, str]:
    try:
        import sqlglot  # type: ignore
    except Exception:
        return None, "sqlglot_not_available"
    try:
        sqlglot.parse_one(text)
        return True, "parse_ok"
    except Exception:
        return False, "parse_failed"


def load_reference_hashes(path: Path, text_col: str, batch_size: int, limit: int | None) -> set[str]:
    if not path.exists():
        raise FileNotFoundError(path)
    names = set(pq.ParquetFile(path).schema_arrow.names)
    if text_col not in names:
        raise KeyError(f"{path} missing reference text column {text_col}")
    hashes: set[str] = set()
    seen = 0
    parquet = pq.ParquetFile(path)
    for batch in parquet.iter_batches(batch_size=batch_size, columns=[text_col]):
        df = batch.to_pandas()
        if limit is not None:
            remaining = limit - seen
            if remaining <= 0:
                break
            df = df.head(remaining)
        seen += len(df)
        for text in df[text_col].fillna("").astype(str).tolist():
            if text:
                hashes.add(hash_template(text))
        if limit is not None and seen >= limit:
            break
    return hashes


def load_detector_results(path: Path | None) -> dict[str, bool] | None:
    if path is None:
        return None
    out: dict[str, bool] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"sample_id", "detected"}
        if not required.issubset(reader.fieldnames or set()):
            raise KeyError(f"{path} must contain columns: {sorted(required)}")
        for row in reader:
            value = str(row["detected"]).strip().lower()
            out[str(row["sample_id"])] = value in {"1", "true", "yes", "detected", "blocked"}
    return out


def evaluate(args: argparse.Namespace) -> dict[str, Any]:
    samples = load_samples(args.samples)
    reference_hashes = load_reference_hashes(
        args.reference,
        args.reference_text_col,
        args.reference_batch_size,
        args.reference_limit,
    )
    detector = load_detector_results(args.detector_results)

    totals = Counter()
    by_technique: dict[str, Counter[str]] = defaultdict(Counter)
    parse_reasons = Counter()
    seen_sample_templates: set[str] = set()

    for row in samples:
        text = row["text"]
        technique = row["technique"]
        sql_signal = bool(SQL_SIGNAL_RE.search(text))
        delimiter_ok = balanced_delimiters(text)
        parse_ok, parse_reason = maybe_sqlglot_parse(text)
        hint = technique_hint(technique, text)
        in_train_template = row["template_hash"] in reference_hashes
        duplicate_in_batch = row["template_hash"] in seen_sample_templates
        seen_sample_templates.add(row["template_hash"])

        totals["samples"] += 1
        totals["sql_signal"] += int(sql_signal)
        totals["delimiter_ok"] += int(delimiter_ok)
        totals["train_template_duplicate"] += int(in_train_template)
        totals["batch_template_duplicate"] += int(duplicate_in_batch)
        if parse_ok is True:
            totals["sqlglot_parse_ok"] += 1
        if parse_ok is not None:
            totals["sqlglot_parse_applicable"] += 1
        parse_reasons[parse_reason] += 1
        if hint is True:
            totals["technique_hint"] += 1
        if hint is not None:
            totals["technique_hint_applicable"] += 1

        if detector is not None and row["sample_id"] in detector:
            totals["detector_applicable"] += 1
            detected = detector[row["sample_id"]]
            totals["detector_detected"] += int(detected)
            totals["detector_bypassed"] += int(not detected)

        bucket = by_technique[technique]
        bucket["samples"] += 1
        bucket["sql_signal"] += int(sql_signal)
        bucket["delimiter_ok"] += int(delimiter_ok)
        bucket["train_template_duplicate"] += int(in_train_template)
        if hint is True:
            bucket["technique_hint"] += 1
        if hint is not None:
            bucket["technique_hint_applicable"] += 1

    return {
        "samples_path": str(args.samples),
        "reference_path": str(args.reference),
        "reference_templates": len(reference_hashes),
        "samples": totals["samples"],
        "validity": {
            "sql_signal_rate_debug_only": pct(totals["sql_signal"], totals["samples"]),
            "balanced_delimiter_rate": pct(totals["delimiter_ok"], totals["samples"]),
            "sqlglot_parse_rate": pct(totals["sqlglot_parse_ok"], totals["sqlglot_parse_applicable"]),
            "sqlglot_parse_applicable": totals["sqlglot_parse_applicable"],
            "parse_reasons": dict(parse_reasons),
        },
        "novelty": {
            "train_template_duplicate_rate": pct(totals["train_template_duplicate"], totals["samples"]),
            "batch_template_duplicate_rate": pct(totals["batch_template_duplicate"], totals["samples"]),
            "novel_vs_train_template_rate": 1.0 - pct(totals["train_template_duplicate"], totals["samples"]),
        },
        "conditioning_debug": {
            "technique_hint_rate": pct(totals["technique_hint"], totals["technique_hint_applicable"]),
            "technique_hint_applicable": totals["technique_hint_applicable"],
        },
        "evasion": {
            "status": "provided" if detector is not None else "missing_detector_results",
            "detector_applicable": totals["detector_applicable"],
            "detector_bypass_rate": pct(totals["detector_bypassed"], totals["detector_applicable"]),
            "detector_detection_rate": pct(totals["detector_detected"], totals["detector_applicable"]),
        },
        "by_technique": {
            technique: {
                "samples": counts["samples"],
                "sql_signal_rate_debug_only": pct(counts["sql_signal"], counts["samples"]),
                "balanced_delimiter_rate": pct(counts["delimiter_ok"], counts["samples"]),
                "train_template_duplicate_rate": pct(counts["train_template_duplicate"], counts["samples"]),
                "technique_hint_rate": pct(counts["technique_hint"], counts["technique_hint_applicable"])
                if counts["technique_hint_applicable"]
                else None,
            }
            for technique, counts in sorted(by_technique.items())
        },
    }


def write_outputs(args: argparse.Namespace, result: dict[str, Any]) -> None:
    args.report_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.report_dir / args.json_name
    md_path = args.report_dir / args.report_name
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# 08 - Evaluator Contract Report",
        "",
        "Scope: separated validity, novelty, conditioning-debug, and evasion axes. Raw payloads are intentionally omitted.",
        "",
        "## Inputs",
        "",
        f"- Samples: `{result['samples_path']}`",
        f"- Reference: `{result['reference_path']}`",
        f"- Reference templates loaded: `{result['reference_templates']:,}`",
        f"- Samples evaluated: `{result['samples']:,}`",
        "",
        "## Axis Summary",
        "",
        "| Axis | Metric | Value | Notes |",
        "|---|---|---:|---|",
        f"| Validity | Balanced delimiter rate | {result['validity']['balanced_delimiter_rate']:.4f} | structural sanity, not ground truth |",
        f"| Validity | sqlglot parse rate | {result['validity']['sqlglot_parse_rate']:.4f} | applicable={result['validity']['sqlglot_parse_applicable']} |",
        f"| Novelty | Novel vs train template rate | {result['novelty']['novel_vs_train_template_rate']:.4f} | normalized delex-template hash |",
        f"| Novelty | Batch template duplicate rate | {result['novelty']['batch_template_duplicate_rate']:.4f} | generated-sample self duplication |",
        f"| Conditioning | Technique hint rate | {result['conditioning_debug']['technique_hint_rate']:.4f} | debug only |",
        f"| Evasion | Detector bypass rate | {result['evasion']['detector_bypass_rate']:.4f} | status={result['evasion']['status']} |",
        "",
        "## By Technique",
        "",
        "| Technique | Samples | Balanced Delimiters | Train Template Dup | Technique Hint |",
        "|---|---:|---:|---:|---:|",
    ]
    for technique, counts in result["by_technique"].items():
        hint = counts["technique_hint_rate"]
        lines.append(
            "| {technique} | {samples:,} | {delim:.4f} | {dup:.4f} | {hint} |".format(
                technique=technique,
                samples=counts["samples"],
                delim=counts["balanced_delimiter_rate"],
                dup=counts["train_template_duplicate_rate"],
                hint="n/a" if hint is None else f"{hint:.4f}",
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation Rules",
            "",
            "- Evasion is not inferred unless detector results are supplied.",
            "- `sql_signal_rate_debug_only` and technique hints are retained for continuity with Phase 6 but must not be used as checkpoint gates.",
            "- A sample should count toward a main claim only when validity, novelty, and evasion are all measurable.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"report={md_path}")
    print(f"json={json_path}")


def main() -> None:
    args = parse_args()
    result = evaluate(args)
    write_outputs(args, result)


if __name__ == "__main__":
    main()

