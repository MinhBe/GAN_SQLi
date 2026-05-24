# -*- coding: utf-8 -*-
"""
Phase 08 - Script 10: rerank GAN candidates with classifier-oracle scores plus
validity/novelty guardrails.

Input generated candidates stay in JSONL. Detector/classifier results must use
the evaluator-compatible CSV schema and may include an optional `score` column.
The output is another JSONL sample source for phase08_03_evaluator_contract.py.
"""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import phase08_03_evaluator_contract as evaluator


PHASE_DIR = Path(__file__).resolve().parent
ROOT = PHASE_DIR.parent.parent
DEFAULT_REFERENCE = ROOT / "Guiding" / "Phase 5" / "outputs" / "full" / "gold.parquet"
DEFAULT_OUT_DIR = PHASE_DIR / "outputs" / "classifier_oracle_rerank"
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Rerank GAN candidates with classifier-oracle and evaluator guardrails.")
    parser.add_argument("--samples", action="append", required=True, metavar="NAME=PATH")
    parser.add_argument("--detector-results", action="append", required=True, metavar="NAME=CSV")
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--reference-text-col", default="payload_delex_v5")
    parser.add_argument("--reference-batch-size", type=int, default=100000)
    parser.add_argument("--reference-limit", type=int, default=None)
    parser.add_argument("--top-n", type=int, default=400)
    parser.add_argument("--require-novel", action="store_true")
    parser.add_argument("--require-balanced", action="store_true")
    parser.add_argument("--require-technique-hint", action="store_true")
    parser.add_argument("--exclude-technique", action="append", default=[])
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--name", default="gan_classifier_oracle_reranked")
    return parser.parse_args()


def ensure_under_phase(path: Path) -> Path:
    resolved = path.resolve()
    phase = PHASE_DIR.resolve()
    if resolved != phase and phase not in resolved.parents:
        raise ValueError(f"Refusing to write outside Phase 8: {resolved}")
    return resolved


def parse_specs(specs: list[str]) -> dict[str, Path]:
    out: dict[str, Path] = {}
    for spec in specs:
        if "=" not in spec:
            raise ValueError(f"Expected NAME=PATH, got: {spec}")
        name, raw_path = spec.split("=", 1)
        name = name.strip()
        path = Path(raw_path.strip())
        if not name:
            raise ValueError(f"Missing name in {spec}")
        if not path.exists():
            raise FileNotFoundError(path)
        out[name] = path
    return out


def load_samples(name: str, path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            text = str(payload.get("text", ""))
            sample_id = str(payload.get("sample_id", idx))
            rows.append(
                {
                    "source": name,
                    "source_sample_id": sample_id,
                    "sample_id": f"{name}::{sample_id}",
                    "technique": str(payload.get("technique", "unknown")),
                    "text": text,
                    "template_hash": evaluator.hash_template(text),
                }
            )
    return rows


def load_detector_results(name: str, path: Path) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        if not {"sample_id", "detected"}.issubset(reader.fieldnames or set()):
            raise KeyError(f"{path} must contain sample_id,detected")
        for row in reader:
            value = str(row["detected"]).strip().lower()
            detected = value in {"1", "true", "yes", "detected", "blocked"}
            score = row.get("score")
            out[f"{name}::{row['sample_id']}"] = {
                "detected": detected,
                "detector_score": float(score) if score not in {None, ""} else (1.0 if detected else 0.0),
            }
    return out


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def row_quality(row: dict[str, Any], reference_hashes: set[str]) -> dict[str, Any]:
    text = row["text"]
    hint = evaluator.technique_hint(row["technique"], text)
    balanced = evaluator.balanced_delimiters(text)
    novel = row["template_hash"] not in reference_hashes
    return {
        "balanced": balanced,
        "novel": novel,
        "technique_hint": hint,
    }


def utility(row: dict[str, Any]) -> float:
    detector_score = float(row.get("detector_score", 1.0))
    detected = bool(row.get("detected", True))
    score = 0.0
    score += 2.0 if row["novel"] else -2.0
    score += 1.5 if row["balanced"] else -1.0
    if row["technique_hint"] is True:
        score += 0.75
    elif row["technique_hint"] is False:
        score -= 0.75
    score += 2.0 if not detected else -0.5
    score -= detector_score
    return score


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter()
    by_source: Counter[str] = Counter()
    seen_templates: set[str] = set()
    dup = 0
    for row in rows:
        counts["samples"] += 1
        counts["balanced"] += int(row.get("balanced", False))
        counts["novel"] += int(row.get("novel", False))
        counts["detected"] += int(row.get("detected", True))
        counts["hint_applicable"] += int(row.get("technique_hint") is not None)
        counts["hint"] += int(row.get("technique_hint") is True)
        by_source[str(row["source"])] += 1
        if row["template_hash"] in seen_templates:
            dup += 1
        seen_templates.add(row["template_hash"])
    n = max(counts["samples"], 1)
    return {
        "samples": counts["samples"],
        "balanced_delimiter_rate": counts["balanced"] / n,
        "novel_vs_train_template_rate": counts["novel"] / n,
        "detector_bypass_rate": 1.0 - counts["detected"] / n,
        "technique_hint_rate": counts["hint"] / max(counts["hint_applicable"], 1),
        "batch_template_duplicate_rate": dup / n,
        "by_source": dict(sorted(by_source.items())),
    }


def main() -> None:
    args = parse_args()
    args.out_dir = ensure_under_phase(args.out_dir)
    args.report_dir = ensure_under_phase(args.report_dir)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)

    sample_specs = parse_specs(args.samples)
    detector_specs = parse_specs(args.detector_results)
    missing = sorted(set(sample_specs) - set(detector_specs))
    if missing:
        raise KeyError(f"Missing detector results for sample sources: {missing}")

    reference_hashes = evaluator.load_reference_hashes(
        args.reference,
        args.reference_text_col,
        args.reference_batch_size,
        args.reference_limit,
    )
    detector_rows: dict[str, dict[str, Any]] = {}
    for name, path in detector_specs.items():
        detector_rows.update(load_detector_results(name, path))

    candidates: list[dict[str, Any]] = []
    rejected = Counter()
    for name, path in sample_specs.items():
        for row in load_samples(name, path):
            detector = detector_rows.get(row["sample_id"])
            if detector is None:
                rejected["missing_detector"] += 1
                continue
            row.update(detector)
            row.update(row_quality(row, reference_hashes))
            if row["technique"] in set(args.exclude_technique):
                rejected["excluded_technique"] += 1
                continue
            if args.require_novel and not row["novel"]:
                rejected["not_novel"] += 1
                continue
            if args.require_balanced and not row["balanced"]:
                rejected["not_balanced"] += 1
                continue
            if args.require_technique_hint and row["technique_hint"] is False:
                rejected["technique_hint_failed"] += 1
                continue
            row["utility"] = utility(row)
            candidates.append(row)

    candidates.sort(key=lambda row: row["utility"], reverse=True)
    selected: list[dict[str, Any]] = []
    seen_templates: set[str] = set()
    for row in candidates:
        if row["template_hash"] in seen_templates:
            continue
        seen_templates.add(row["template_hash"])
        selected.append(row)
        if len(selected) >= args.top_n:
            break
    if len(selected) < args.top_n:
        for row in candidates:
            if row in selected:
                continue
            selected.append(row)
            if len(selected) >= args.top_n:
                break

    output_rows = [
        {
            "sample_id": f"reranked_{idx}",
            "technique": row["technique"],
            "text": row["text"],
            "source": row["source"],
            "source_sample_id": row["source_sample_id"],
            "detected": row["detected"],
            "detector_score": row["detector_score"],
            "utility": row["utility"],
        }
        for idx, row in enumerate(selected)
    ]
    samples_path = args.out_dir / f"{args.name}.jsonl"
    write_jsonl(samples_path, output_rows)
    detector_path = args.out_dir / f"{args.name}_classifier_oracle_results.csv"
    with detector_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sample_id", "detected", "score", "technique", "source_sample_id"])
        writer.writeheader()
        for row in output_rows:
            writer.writerow(
                {
                    "sample_id": row["sample_id"],
                    "detected": "true" if row["detected"] else "false",
                    "score": f"{float(row['detector_score']):.6f}",
                    "technique": row["technique"],
                    "source_sample_id": row["source_sample_id"],
                }
            )

    result = {
        "samples": str(samples_path),
        "detector_results": str(detector_path),
        "top_n": args.top_n,
        "candidate_count": len(candidates),
        "selected_count": len(selected),
        "rejected": dict(rejected),
        "filters": {
            "require_novel": args.require_novel,
            "require_balanced": args.require_balanced,
            "require_technique_hint": args.require_technique_hint,
            "exclude_technique": args.exclude_technique,
        },
        "summary": summarize(selected),
    }
    json_path = args.report_dir / f"08_rerank_{args.name}.json"
    md_path = args.report_dir / f"08_rerank_{args.name}.md"
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    summary = result["summary"]
    lines = [
        "# 08 - Classifier Oracle Rerank Report",
        "",
        f"- Output samples: `{samples_path}`",
        f"- Detector results: `{detector_path}`",
        f"- Candidates after filters: `{len(candidates):,}`",
        f"- Selected: `{len(selected):,}`",
        f"- Rejected: `{dict(rejected)}`",
        "",
        "## Selected Summary",
        "",
        f"- Balanced delimiter rate: `{summary['balanced_delimiter_rate']:.4f}`",
        f"- Novel vs train template rate: `{summary['novel_vs_train_template_rate']:.4f}`",
        f"- Batch template duplicate rate: `{summary['batch_template_duplicate_rate']:.4f}`",
        f"- Technique hint rate: `{summary['technique_hint_rate']:.4f}`",
        f"- Detector bypass rate: `{summary['detector_bypass_rate']:.4f}`",
        f"- By source: `{summary['by_source']}`",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"samples={samples_path}")
    print(f"report={md_path}")
    print(f"json={json_path}")


if __name__ == "__main__":
    main()
