# -*- coding: utf-8 -*-
"""
Phase 08 - Script 4: build deterministic delex-template cluster splits.

Rows sharing the same normalized delex template are assigned to the same split.
The script streams Phase 5 parquet sources and writes train/dev/test parquet
files under Phase 8 outputs.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


PHASE_DIR = Path(__file__).resolve().parent
ROOT = PHASE_DIR.parent.parent
DEFAULT_SOURCES = [
    ROOT / "Guiding" / "Phase 5" / "outputs" / "full" / "gold.parquet",
    ROOT / "Guiding" / "Phase 5" / "outputs" / "full" / "verified_dev.parquet",
    ROOT / "Guiding" / "Phase 5" / "outputs" / "full" / "verified_test.parquet",
]
DEFAULT_OUT_DIR = PHASE_DIR / "outputs" / "delex_cluster_split"
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"
SPACE_RE = re.compile(r"\s+")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Build delex-template cluster train/dev/test splits.")
    parser.add_argument("--sources", type=Path, nargs="*", default=DEFAULT_SOURCES)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--text-col", default="payload_delex_v5")
    parser.add_argument("--quality-col", default="quality_band")
    parser.add_argument("--needs-ai-col", default="needs_ai")
    parser.add_argument("--batch-size", type=int, default=100000)
    parser.add_argument("--limit-per-source", type=int, default=None)
    parser.add_argument("--train-pct", type=int, default=80)
    parser.add_argument("--dev-pct", type=int, default=10)
    parser.add_argument("--test-pct", type=int, default=10)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--report-name", default="08_delex_cluster_split_report.md")
    parser.add_argument("--json-name", default="08_delex_cluster_split_report.json")
    return parser.parse_args()


def ensure_under_phase(path: Path) -> Path:
    resolved = path.resolve()
    phase = PHASE_DIR.resolve()
    if resolved != phase and phase not in resolved.parents:
        raise ValueError(f"Refusing to write outside Phase 8: {resolved}")
    return resolved


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
    return hashlib.sha256(normalize_template(text).encode("utf-8", errors="replace")).hexdigest()


def split_for_hash(hash_value: str, train_pct: int, dev_pct: int) -> str:
    bucket = int(hash_value[:16], 16) % 100
    if bucket < train_pct:
        return "train"
    if bucket < train_pct + dev_pct:
        return "dev"
    return "test"


def load_columns(path: Path, args: argparse.Namespace) -> list[str]:
    names = set(pq.ParquetFile(path).schema_arrow.names)
    if args.text_col not in names:
        raise KeyError(f"{path} missing text column: {args.text_col}")
    return list(pq.ParquetFile(path).schema_arrow.names)


def iter_filtered_batches(path: Path, args: argparse.Namespace):
    columns = load_columns(path, args)
    parquet = pq.ParquetFile(path)
    seen = 0
    for batch in parquet.iter_batches(batch_size=args.batch_size, columns=columns):
        df = batch.to_pandas()
        if args.limit_per_source is not None:
            remaining = args.limit_per_source - seen
            if remaining <= 0:
                break
            df = df.head(remaining)
        seen += len(df)

        df[args.text_col] = df[args.text_col].map(as_text)
        mask = df[args.text_col].str.len() > 0
        if args.quality_col in df.columns:
            mask &= df[args.quality_col].map(as_text).str.lower().eq("gold")
        if args.needs_ai_col in df.columns:
            mask &= ~df[args.needs_ai_col].fillna(False).astype(bool)
        out = df.loc[mask].copy()
        if not out.empty:
            yield out
        if args.limit_per_source is not None and seen >= args.limit_per_source:
            break


def validate_ratios(args: argparse.Namespace) -> None:
    total = args.train_pct + args.dev_pct + args.test_pct
    if total != 100:
        raise ValueError(f"split percentages must sum to 100, got {total}")
    if min(args.train_pct, args.dev_pct, args.test_pct) < 0:
        raise ValueError("split percentages must be non-negative")


def main() -> None:
    args = parse_args()
    validate_ratios(args)
    out_dir = ensure_under_phase(args.out_dir)
    if out_dir.exists():
        if not args.overwrite:
            raise FileExistsError(f"{out_dir} exists. Pass --overwrite to rebuild.")
        shutil.rmtree(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)

    writers: dict[str, pq.ParquetWriter] = {}
    stats: dict[str, Counter[str]] = {name: Counter() for name in ["train", "dev", "test"]}
    template_sets: dict[str, set[str]] = {name: set() for name in ["train", "dev", "test"]}
    source_counts: Counter[str] = Counter()

    try:
        for source in args.sources:
            source_name = source.stem
            print(f"source={source}", flush=True)
            for df in iter_filtered_batches(source, args):
                hashes = [template_hash(text) for text in df[args.text_col].tolist()]
                splits = [split_for_hash(h, args.train_pct, args.dev_pct) for h in hashes]
                df["phase08_template_hash"] = [h[:20] for h in hashes]
                df["phase08_split"] = splits
                df["phase08_source_file"] = source_name

                for split in ["train", "dev", "test"]:
                    part = df.loc[df["phase08_split"].eq(split)].copy()
                    if part.empty:
                        continue
                    table = pa.Table.from_pandas(part, preserve_index=False)
                    if split not in writers:
                        writers[split] = pq.ParquetWriter(out_dir / f"{split}.parquet", table.schema, compression="snappy")
                    writers[split].write_table(table)
                    stats[split]["rows"] += len(part)
                    source_counts[f"{split}:{source_name}"] += len(part)
                    for h in part["phase08_template_hash"].tolist():
                        template_sets[split].add(h)
                print(
                    "  rows_out train={:,} dev={:,} test={:,}".format(
                        stats["train"]["rows"],
                        stats["dev"]["rows"],
                        stats["test"]["rows"],
                    ),
                    flush=True,
                )
    finally:
        for writer in writers.values():
            writer.close()

    overlaps = {
        "train_dev": len(template_sets["train"] & template_sets["dev"]),
        "train_test": len(template_sets["train"] & template_sets["test"]),
        "dev_test": len(template_sets["dev"] & template_sets["test"]),
    }
    payload = {
        "out_dir": str(out_dir),
        "sources": [str(p) for p in args.sources],
        "split_percentages": {"train": args.train_pct, "dev": args.dev_pct, "test": args.test_pct},
        "splits": {
            split: {
                "rows": stats[split]["rows"],
                "unique_templates": len(template_sets[split]),
                "duplicate_template_row_rate": (stats[split]["rows"] - len(template_sets[split])) / stats[split]["rows"]
                if stats[split]["rows"]
                else 0.0,
            }
            for split in ["train", "dev", "test"]
        },
        "template_overlaps": overlaps,
        "source_counts": dict(source_counts),
    }
    json_path = args.report_dir / args.json_name
    md_path = args.report_dir / args.report_name
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# 08 - Delex Cluster Split Report",
        "",
        "Rows sharing a normalized delex-template hash are assigned to the same split.",
        "",
        f"- Output dir: `{out_dir}`",
        f"- Percentages: train={args.train_pct}, dev={args.dev_pct}, test={args.test_pct}",
        "",
        "| Split | Rows | Unique Templates | Duplicate Template Row Rate |",
        "|---|---:|---:|---:|",
    ]
    for split, row in payload["splits"].items():
        lines.append(f"| {split} | {row['rows']:,} | {row['unique_templates']:,} | {row['duplicate_template_row_rate']:.4f} |")
    lines.extend(
        [
            "",
            "## Template Overlaps",
            "",
            f"- train/dev: `{overlaps['train_dev']}`",
            f"- train/test: `{overlaps['train_test']}`",
            f"- dev/test: `{overlaps['dev_test']}`",
            "",
            "Any non-zero overlap here is a bug in the split builder or hash assignment.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"report={md_path}")
    print(f"json={json_path}")


if __name__ == "__main__":
    main()

