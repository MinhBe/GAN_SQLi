# -*- coding: utf-8 -*-
"""
Phase 08 - Script 11: oracle-aware candidate search.

This is a bounded post-generation search, not live exploitation. It mutates
existing delex-space GAN candidates, scores them with the held-out classifier
oracle, and keeps only candidates that pass evaluator-style guardrails.

Outputs:
  - JSONL samples for phase08_03_evaluator_contract.py
  - CSV sample_id,detected,score compatible with evaluator --detector-results
"""

from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np

import phase08_03_evaluator_contract as evaluator
import phase08_08_heldout_classifier_oracle as oracle


PHASE_DIR = Path(__file__).resolve().parent
ROOT = PHASE_DIR.parent.parent
DEFAULT_REFERENCE = ROOT / "Guiding" / "Phase 5" / "outputs" / "full" / "gold.parquet"
DEFAULT_OUT_DIR = PHASE_DIR / "outputs" / "oracle_aware_search"
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run classifier-oracle-aware search over generated candidates.")
    parser.add_argument("--samples", type=Path, required=True)
    parser.add_argument("--split-dir", type=Path, default=oracle.DEFAULT_SPLIT_DIR)
    parser.add_argument("--train", type=Path, default=None)
    parser.add_argument("--dev", type=Path, default=None)
    parser.add_argument("--test", type=Path, default=None)
    parser.add_argument("--reference", type=Path, default=DEFAULT_REFERENCE)
    parser.add_argument("--reference-text-col", default="payload_delex_v5")
    parser.add_argument("--text-col", default="payload_delex_v5")
    parser.add_argument("--label-col", default="is_sqli")
    parser.add_argument("--max-positive", type=int, default=150000)
    parser.add_argument("--max-negative", type=int, default=50000)
    parser.add_argument("--target-benign-fpr", type=float, default=0.05)
    parser.add_argument("--max-iter", type=int, default=12)
    parser.add_argument("--seed", type=int, default=110823)
    parser.add_argument("--variants-per-sample", type=int, default=16)
    parser.add_argument("--top-n", type=int, default=400)
    parser.add_argument("--require-novel", action="store_true")
    parser.add_argument("--require-balanced", action="store_true")
    parser.add_argument("--require-technique-hint", action="store_true")
    parser.add_argument("--exclude-technique", action="append", default=["benign"])
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--name", default="oracle_aware_search")
    return parser.parse_args()


def ensure_under_phase(path: Path) -> Path:
    resolved = path.resolve()
    phase = PHASE_DIR.resolve()
    if resolved != phase and phase not in resolved.parents:
        raise ValueError(f"Refusing to write outside Phase 8: {resolved}")
    return resolved


def load_seed_samples(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with path.open("r", encoding="utf-8") as handle:
        for idx, line in enumerate(handle):
            line = line.strip()
            if not line:
                continue
            payload = json.loads(line)
            rows.append(
                {
                    "source_sample_id": str(payload.get("sample_id", idx)),
                    "technique": str(payload.get("technique", "unknown")),
                    "text": str(payload.get("text", "")),
                }
            )
    return rows


def mutate_once(text: str, technique: str, rng: random.Random) -> str:
    out = evaluator.normalize_template(text)
    replacements = [
        (" union select ", " union/**/select "),
        (" union all select ", " union/**/all/**/select "),
        (" select ", " select/**/"),
        (" from ", "/**/from "),
        (" where ", "/**/where "),
        (" and ", "/**/and/**/"),
        (" or ", "/**/or/**/"),
        (" = ", rng.choice([" = ", " like ", " <> "])),
        ("__comment__", rng.choice(["__comment__", "--", "#", "/* */"])),
    ]
    rng.shuffle(replacements)
    changes = rng.randint(1, min(4, len(replacements)))
    for src, dst in replacements[:changes]:
        if src in out and rng.random() < 0.85:
            out = out.replace(src, dst, 1)

    if technique == "time_blind":
        for src, dst in [("sleep", "benchmark"), ("pg_sleep", "sleep"), ("waitfor", "delay")]:
            if src in out and rng.random() < 0.4:
                out = out.replace(src, dst, 1)
                break
    elif technique == "error_based":
        for src, dst in [("extractvalue", "updatexml"), ("updatexml", "extractvalue"), ("cast", "convert")]:
            if src in out and rng.random() < 0.4:
                out = out.replace(src, dst, 1)
                break
    elif technique == "boolean_blind":
        if "__num__ = __num__" in out and rng.random() < 0.5:
            out = out.replace("__num__ = __num__", "__num__ <> __num__", 1)
    return evaluator.normalize_template(out)


def candidate_variants(row: dict[str, Any], variants_per_sample: int, rng: random.Random) -> list[dict[str, Any]]:
    variants = [
        {
            "source_sample_id": row["source_sample_id"],
            "technique": row["technique"],
            "text": evaluator.normalize_template(row["text"]),
            "mutation_round": 0,
        }
    ]
    current = row["text"]
    for idx in range(1, variants_per_sample + 1):
        if rng.random() < 0.65:
            current = mutate_once(current, row["technique"], rng)
        else:
            current = mutate_once(row["text"], row["technique"], rng)
        variants.append(
            {
                "source_sample_id": row["source_sample_id"],
                "technique": row["technique"],
                "text": current,
                "mutation_round": idx,
            }
        )
    return variants


def train_oracle(args: argparse.Namespace) -> tuple[Any, float, dict[str, Any]]:
    train_path, dev_path, test_path = oracle.resolve_split_paths(args)
    train_df = oracle.load_split(train_path, args.text_col, args.label_col)
    train_sample = oracle.sample_training_rows(
        train_df,
        args.label_col,
        args.max_positive,
        args.max_negative,
        args.seed,
    )
    dev_df = oracle.load_split(dev_path, args.text_col, args.label_col)
    test_df = oracle.load_split(test_path, args.text_col, args.label_col)
    model = oracle.build_model(args.max_iter, args.seed)
    model.fit(train_sample[args.text_col].tolist(), train_sample[args.label_col].to_numpy())
    dev_y = dev_df[args.label_col].to_numpy()
    test_y = test_df[args.label_col].to_numpy()
    dev_scores = oracle.score_texts(model, dev_df[args.text_col].tolist())
    test_scores = oracle.score_texts(model, test_df[args.text_col].tolist())
    threshold = oracle.choose_threshold(dev_y, dev_scores, args.target_benign_fpr)
    quality = {
        "train_rows_used": int(len(train_sample)),
        "positives_used": int((train_sample[args.label_col] == 1).sum()),
        "negatives_used": int((train_sample[args.label_col] == 0).sum()),
        "threshold": threshold,
        "dev": oracle.binary_metrics(dev_y, dev_scores, threshold),
        "test": oracle.binary_metrics(test_y, test_scores, threshold),
    }
    return model, threshold, quality


def passes_filters(row: dict[str, Any], args: argparse.Namespace) -> tuple[bool, str | None]:
    if row["technique"] in set(args.exclude_technique):
        return False, "excluded_technique"
    if args.require_novel and not row["novel"]:
        return False, "not_novel"
    if args.require_balanced and not row["balanced"]:
        return False, "not_balanced"
    if args.require_technique_hint and row["technique_hint"] is False:
        return False, "technique_hint_failed"
    return True, None


def utility(row: dict[str, Any]) -> float:
    score = 0.0
    score += 2.0 if row["novel"] else -2.0
    score += 1.5 if row["balanced"] else -1.0
    if row["technique_hint"] is True:
        score += 0.8
    elif row["technique_hint"] is False:
        score -= 0.8
    score += 2.5 if not row["detected"] else -0.5
    score -= float(row["oracle_score"])
    score -= 0.05 * int(row["mutation_round"])
    return score


def summarize(rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = Counter()
    by_technique: Counter[str] = Counter()
    seen: set[str] = set()
    dup = 0
    for row in rows:
        counts["samples"] += 1
        counts["balanced"] += int(row["balanced"])
        counts["novel"] += int(row["novel"])
        counts["detected"] += int(row["detected"])
        counts["hint_applicable"] += int(row["technique_hint"] is not None)
        counts["hint"] += int(row["technique_hint"] is True)
        by_technique[row["technique"]] += 1
        if row["template_hash"] in seen:
            dup += 1
        seen.add(row["template_hash"])
    n = max(counts["samples"], 1)
    return {
        "samples": counts["samples"],
        "balanced_delimiter_rate": counts["balanced"] / n,
        "novel_vs_train_template_rate": counts["novel"] / n,
        "batch_template_duplicate_rate": dup / n,
        "technique_hint_rate": counts["hint"] / max(counts["hint_applicable"], 1),
        "classifier_oracle_bypass_rate": 1.0 - counts["detected"] / n,
        "by_technique": dict(sorted(by_technique.items())),
    }


def write_outputs(args: argparse.Namespace, selected: list[dict[str, Any]], result: dict[str, Any]) -> None:
    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    samples_path = args.out_dir / f"{args.name}.jsonl"
    detector_path = args.out_dir / f"{args.name}_classifier_oracle_results.csv"
    json_path = args.report_dir / f"08_oracle_aware_search_{args.name}.json"
    md_path = args.report_dir / f"08_oracle_aware_search_{args.name}.md"

    with samples_path.open("w", encoding="utf-8") as handle:
        for idx, row in enumerate(selected):
            handle.write(
                json.dumps(
                    {
                        "sample_id": f"oracle_search_{idx}",
                        "technique": row["technique"],
                        "text": row["text"],
                        "source_sample_id": row["source_sample_id"],
                        "mutation_round": row["mutation_round"],
                    },
                    ensure_ascii=False,
                )
                + "\n"
            )
    with detector_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["sample_id", "detected", "score", "technique", "source_sample_id"])
        writer.writeheader()
        for idx, row in enumerate(selected):
            writer.writerow(
                {
                    "sample_id": f"oracle_search_{idx}",
                    "detected": "true" if row["detected"] else "false",
                    "score": f"{float(row['oracle_score']):.6f}",
                    "technique": row["technique"],
                    "source_sample_id": row["source_sample_id"],
                }
            )

    result["samples"] = str(samples_path)
    result["detector_results"] = str(detector_path)
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# 08 - Oracle-Aware Search Report",
        "",
        f"- Seed samples: `{args.samples}`",
        f"- Output samples: `{samples_path}`",
        f"- Detector results: `{detector_path}`",
        f"- Generated candidates: `{result['generated_candidates']:,}`",
        f"- Candidates after filters: `{result['candidate_count']:,}`",
        f"- Selected: `{result['selected_count']:,}`",
        f"- Rejected: `{result['rejected']}`",
        "",
        "## Selected Summary",
        "",
        f"- Balanced delimiter rate: `{result['summary']['balanced_delimiter_rate']:.4f}`",
        f"- Novel vs train template rate: `{result['summary']['novel_vs_train_template_rate']:.4f}`",
        f"- Batch template duplicate rate: `{result['summary']['batch_template_duplicate_rate']:.4f}`",
        f"- Technique hint rate: `{result['summary']['technique_hint_rate']:.4f}`",
        f"- Classifier-oracle bypass rate: `{result['summary']['classifier_oracle_bypass_rate']:.4f}`",
        f"- By technique: `{result['summary']['by_technique']}`",
        "",
        "## Oracle Quality",
        "",
        f"- Test accuracy: `{result['oracle_quality']['test']['accuracy']:.4f}`",
        f"- Test SQLi recall: `{result['oracle_quality']['test']['recall_tpr']:.4f}`",
        f"- Test benign FPR: `{result['oracle_quality']['test']['benign_fpr']:.4f}`",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"samples={samples_path}")
    print(f"detector_results={detector_path}")
    print(f"report={md_path}")
    print(f"json={json_path}")


def main() -> None:
    args = parse_args()
    args.out_dir = ensure_under_phase(args.out_dir)
    args.report_dir = ensure_under_phase(args.report_dir)
    rng = random.Random(args.seed)

    model, threshold, quality = train_oracle(args)
    reference_hashes = evaluator.load_reference_hashes(
        args.reference,
        args.reference_text_col,
        100000,
        None,
    )
    seeds = load_seed_samples(args.samples)
    generated: list[dict[str, Any]] = []
    for row in seeds:
        generated.extend(candidate_variants(row, args.variants_per_sample, rng))

    scores = oracle.score_texts(model, [row["text"] for row in generated])
    candidates: list[dict[str, Any]] = []
    rejected = Counter()
    for row, score in zip(generated, scores):
        row["oracle_score"] = float(score)
        row["detected"] = bool(score >= threshold)
        row["template_hash"] = evaluator.hash_template(row["text"])
        row["novel"] = row["template_hash"] not in reference_hashes
        row["balanced"] = evaluator.balanced_delimiters(row["text"])
        row["technique_hint"] = evaluator.technique_hint(row["technique"], row["text"])
        keep, reason = passes_filters(row, args)
        if not keep:
            rejected[str(reason)] += 1
            continue
        row["utility"] = utility(row)
        candidates.append(row)

    candidates.sort(key=lambda item: item["utility"], reverse=True)
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

    result = {
        "generated_candidates": len(generated),
        "candidate_count": len(candidates),
        "selected_count": len(selected),
        "rejected": dict(rejected),
        "filters": {
            "require_novel": args.require_novel,
            "require_balanced": args.require_balanced,
            "require_technique_hint": args.require_technique_hint,
            "exclude_technique": args.exclude_technique,
        },
        "threshold": threshold,
        "summary": summarize(selected),
        "oracle_quality": quality,
    }
    write_outputs(args, selected, result)


if __name__ == "__main__":
    main()
