# -*- coding: utf-8 -*-
"""
Phase 08 - Script 1: audit delex-template leakage across train/dev/test.

This checks whether Phase 5 splits share the same normalized delex template.
It intentionally reports only hashes and aggregate counts, not raw payload text.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import time
from collections import Counter
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
DEFAULT_TRAIN = ROOT / "Guiding" / "Phase 5" / "outputs" / "full" / "gold.parquet"
DEFAULT_DEV = ROOT / "Guiding" / "Phase 5" / "outputs" / "full" / "verified_dev.parquet"
DEFAULT_TEST = ROOT / "Guiding" / "Phase 5" / "outputs" / "full" / "verified_test.parquet"
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"
DEFAULT_LOG_DIR = PHASE_DIR / "logs"

SPACE_RE = re.compile(r"\s+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit delex-template split leakage.")
    parser.add_argument("--train-source", type=Path, default=DEFAULT_TRAIN)
    parser.add_argument("--dev-source", type=Path, default=DEFAULT_DEV)
    parser.add_argument("--test-source", type=Path, default=DEFAULT_TEST)
    parser.add_argument("--text-col", default="payload_delex_v5")
    parser.add_argument("--cond-col", default="technique_primary")
    parser.add_argument("--quality-col", default="quality_band")
    parser.add_argument("--needs-ai-col", default="needs_ai")
    parser.add_argument("--batch-size", type=int, default=100000)
    parser.add_argument("--limit", type=int, default=None, help="Optional per-source row limit for smoke runs.")
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--report-name", default="08_delex_template_leakage_audit.md")
    parser.add_argument("--json-name", default="08_delex_template_leakage_audit.json")
    return parser.parse_args()


def as_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value)


def normalize_template(text: str) -> str:
    return SPACE_RE.sub(" ", text.strip().lower())


def template_hash(text: str) -> str:
    return hashlib.sha256(normalize_template(text).encode("utf-8", errors="replace")).hexdigest()[:20]


def pct(num: int, den: int) -> float:
    return num / den if den else 0.0


def load_columns(path: Path, args: argparse.Namespace) -> list[str]:
    names = set(pq.ParquetFile(path).schema_arrow.names)
    required = [args.text_col, args.cond_col]
    missing = [name for name in required if name not in names]
    if missing:
        raise KeyError(f"{path} missing required columns: {missing}")
    optional = [args.quality_col, args.needs_ai_col]
    return required + [name for name in optional if name in names and name not in required]


def iter_filtered_batches(path: Path, args: argparse.Namespace):
    columns = load_columns(path, args)
    rows_seen = 0
    parquet = pq.ParquetFile(path)
    for batch in parquet.iter_batches(batch_size=args.batch_size, columns=columns):
        df = batch.to_pandas()
        if args.limit is not None:
            remaining = args.limit - rows_seen
            if remaining <= 0:
                break
            df = df.head(remaining)
        rows_seen += len(df)

        df[args.text_col] = df[args.text_col].map(as_text)
        df[args.cond_col] = df[args.cond_col].map(as_text).replace("", "unknown")
        mask = df[args.text_col].str.len() > 0
        if args.quality_col in df.columns:
            mask &= df[args.quality_col].map(as_text).str.lower().eq("gold")
        if args.needs_ai_col in df.columns:
            mask &= ~df[args.needs_ai_col].fillna(False).astype(bool)
        filtered = df.loc[mask, [args.text_col, args.cond_col]].reset_index(drop=True)
        if not filtered.empty:
            yield filtered
        if args.limit is not None and rows_seen >= args.limit:
            break


def scan_source(name: str, path: Path, args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    key_counts: Counter[str] = Counter()
    technique_counts: Counter[str] = Counter()
    key_technique_counts: Counter[tuple[str, str]] = Counter()
    rows = 0

    for df in iter_filtered_batches(path, args):
        rows += len(df)
        for text, technique in zip(df[args.text_col].tolist(), df[args.cond_col].tolist(), strict=False):
            key = template_hash(text)
            key_counts[key] += 1
            technique_counts[technique] += 1
            key_technique_counts[(key, technique)] += 1
        if rows and rows % max(args.batch_size, 1) == 0:
            elapsed = max(time.time() - started, 1e-6)
            print(f"{name}: rows={rows:,} unique_templates={len(key_counts):,} rate={rows / elapsed:.0f}/s", flush=True)

    return {
        "name": name,
        "path": str(path),
        "rows": rows,
        "unique_templates": len(key_counts),
        "key_counts": key_counts,
        "technique_counts": technique_counts,
        "key_technique_counts": key_technique_counts,
    }


def overlap_rows(source: dict[str, Any], other_keys: set[str]) -> int:
    return sum(count for key, count in source["key_counts"].items() if key in other_keys)


def pair_summary(left: dict[str, Any], right: dict[str, Any]) -> dict[str, Any]:
    left_keys = set(left["key_counts"])
    right_keys = set(right["key_counts"])
    shared = left_keys & right_keys
    top = sorted(
        (
            {
                "template_hash": key,
                f"{left['name']}_rows": left["key_counts"][key],
                f"{right['name']}_rows": right["key_counts"][key],
                "total_rows": left["key_counts"][key] + right["key_counts"][key],
            }
            for key in shared
        ),
        key=lambda row: row["total_rows"],
        reverse=True,
    )[:20]
    return {
        "pair": f"{left['name']}__{right['name']}",
        "shared_templates": len(shared),
        f"{left['name']}_rows_on_shared_templates": overlap_rows(left, shared),
        f"{right['name']}_rows_on_shared_templates": overlap_rows(right, shared),
        f"{left['name']}_row_overlap_rate": pct(overlap_rows(left, shared), left["rows"]),
        f"{right['name']}_row_overlap_rate": pct(overlap_rows(right, shared), right["rows"]),
        "top_shared_template_hashes": top,
    }


def compact_source(source: dict[str, Any]) -> dict[str, Any]:
    return {
        "name": source["name"],
        "path": source["path"],
        "rows": source["rows"],
        "unique_templates": source["unique_templates"],
        "duplicate_template_row_rate": pct(source["rows"] - source["unique_templates"], source["rows"]),
        "technique_counts": dict(source["technique_counts"]),
    }


def write_outputs(args: argparse.Namespace, sources: list[dict[str, Any]], pairs: list[dict[str, Any]]) -> None:
    args.report_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.report_dir / args.json_name
    md_path = args.report_dir / args.report_name

    all_keys = [set(src["key_counts"]) for src in sources]
    all_three = set.intersection(*all_keys) if len(all_keys) == 3 else set()
    payload = {
        "scope": "delex-template leakage audit; raw payload text omitted",
        "text_col": args.text_col,
        "sources": [compact_source(src) for src in sources],
        "pair_overlaps": pairs,
        "all_three_shared_templates": len(all_three),
        "all_three_rows": {src["name"]: overlap_rows(src, all_three) for src in sources},
    }
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# 08 - Delex Template Leakage Audit",
        "",
        "Scope: split overlap in normalized delex-template space. Raw payloads are intentionally omitted.",
        "",
        "## Source Summary",
        "",
        "| Source | Rows | Unique Templates | Duplicate Template Row Rate |",
        "|---|---:|---:|---:|",
    ]
    for src in payload["sources"]:
        lines.append(
            f"| {src['name']} | {src['rows']:,} | {src['unique_templates']:,} | {src['duplicate_template_row_rate']:.4f} |"
        )

    lines.extend(["", "## Pair Overlap", "", "| Pair | Shared Templates | Left Rows On Shared | Right Rows On Shared | Left Rate | Right Rate |", "|---|---:|---:|---:|---:|---:|"])
    for pair in pairs:
        left_name, right_name = pair["pair"].split("__", 1)
        lines.append(
            "| {pair} | {shared:,} | {left_rows:,} | {right_rows:,} | {left_rate:.4f} | {right_rate:.4f} |".format(
                pair=pair["pair"],
                shared=pair["shared_templates"],
                left_rows=pair[f"{left_name}_rows_on_shared_templates"],
                right_rows=pair[f"{right_name}_rows_on_shared_templates"],
                left_rate=pair[f"{left_name}_row_overlap_rate"],
                right_rate=pair[f"{right_name}_row_overlap_rate"],
            )
        )

    lines.extend(
        [
            "",
            "## All Three Splits",
            "",
            f"- Shared templates across train/dev/test: `{payload['all_three_shared_templates']:,}`",
        ]
    )
    for name, rows in payload["all_three_rows"].items():
        total = next(src["rows"] for src in payload["sources"] if src["name"] == name)
        lines.append(f"- {name} rows on all-three templates: `{rows:,}` (`{pct(rows, total):.4f}`)")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- High dev/test overlap with train means token CE loss, novelty, and generated uniqueness can be inflated.",
            "- If overlap is high, Phase 8 claims should use a new delex-template cluster split or explicitly scope old Phase 6 numbers as contaminated by template leakage.",
            "- The JSON sidecar contains top shared template hashes for forensic tracing without exposing payload text.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"report={md_path}")
    print(f"json={json_path}")


def main() -> None:
    args = parse_args()
    sources = [
        scan_source("train", args.train_source, args),
        scan_source("dev", args.dev_source, args),
        scan_source("test", args.test_source, args),
    ]
    pairs = [
        pair_summary(sources[0], sources[1]),
        pair_summary(sources[0], sources[2]),
        pair_summary(sources[1], sources[2]),
    ]
    write_outputs(args, sources, pairs)


if __name__ == "__main__":
    main()

