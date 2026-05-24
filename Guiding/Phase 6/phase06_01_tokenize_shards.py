# -*- coding: utf-8 -*-
"""
Phase 06 - Script 1: token shard preparation for the MLE baseline.

Default contract:
  - Train source: Guiding/Phase 5/outputs/full/gold.parquet
  - Eval source : Guiding/Phase 5/outputs/full/verified_dev.parquet
  - Test source : Guiding/Phase 5/outputs/full/verified_test.parquet
  - Output      : Guiding/Phase 6/cache/token_shards

The script intentionally streams parquet batches and writes fixed-length token
shards so Phase 6 does not load the full labeled parquet into RAM.
"""

from __future__ import annotations

import argparse
import io
import json
import shutil
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import pyarrow.parquet as pq
import torch


if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


PHASE_DIR = Path(__file__).resolve().parent
ROOT = PHASE_DIR.parent.parent

DEFAULT_TRAIN = ROOT / "Guiding" / "Phase 5" / "outputs" / "full" / "gold.parquet"
DEFAULT_DEV = ROOT / "Guiding" / "Phase 5" / "outputs" / "full" / "verified_dev.parquet"
DEFAULT_TEST = ROOT / "Guiding" / "Phase 5" / "outputs" / "full" / "verified_test.parquet"
DEFAULT_CACHE_DIR = PHASE_DIR / "cache" / "token_shards"
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"
DEFAULT_LOG_DIR = PHASE_DIR / "logs"

PAD, BOS, EOS, UNK = "<pad>", "<bos>", "<eos>", "<unk>"
SPECIAL_TOKENS = [PAD, BOS, EOS, UNK]
DEFAULT_TECHNIQUES = [
    "benign",
    "boolean_blind",
    "time_blind",
    "union_based",
    "error_based",
    "generic_sqli",
    "unknown",
]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Prepare Phase 6 token shards.")
    parser.add_argument("--train-source", type=Path, default=DEFAULT_TRAIN)
    parser.add_argument("--dev-source", type=Path, default=DEFAULT_DEV)
    parser.add_argument("--test-source", type=Path, default=DEFAULT_TEST)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--report-name", default="06_token_shard_report.md")
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--progress-name", default="phase06_tokenize_progress.json")
    parser.add_argument("--text-col", default="payload_delex_v5")
    parser.add_argument("--cond-col", default="technique_primary")
    parser.add_argument("--batch-size", type=int, default=50000)
    parser.add_argument("--shard-rows", type=int, default=50000)
    parser.add_argument("--max-len", type=int, default=128)
    parser.add_argument("--min-freq", type=int, default=3)
    parser.add_argument("--max-vocab", type=int, default=64000)
    parser.add_argument("--limit-train", type=int, default=None)
    parser.add_argument("--limit-dev", type=int, default=None)
    parser.add_argument("--limit-test", type=int, default=None)
    parser.add_argument("--include-techniques", default="")
    parser.add_argument("--exclude-techniques", default="")
    parser.add_argument("--allow-non-gold", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    return parser.parse_args()


def ensure_under_phase(path: Path) -> Path:
    resolved = path.resolve()
    phase = PHASE_DIR.resolve()
    if resolved != phase and phase not in resolved.parents:
        raise ValueError(f"Refusing to write outside Phase 6: {resolved}")
    return resolved


def reset_output_dir(path: Path, overwrite: bool) -> None:
    path = ensure_under_phase(path)
    if path.exists():
        if not overwrite:
            raise FileExistsError(f"{path} already exists. Pass --overwrite to rebuild shards.")
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def as_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value)


def parse_technique_set(raw: str) -> set[str] | None:
    values = {item.strip() for item in raw.split(",") if item.strip()}
    return values or None


def load_columns(path: Path, text_col: str, cond_col: str) -> list[str]:
    names = set(pq.ParquetFile(path).schema_arrow.names)
    required = [text_col, cond_col]
    missing = [name for name in required if name not in names]
    if missing:
        raise KeyError(f"{path} is missing required columns: {missing}")
    optional = ["row_id", "quality_band", "needs_ai", "split"]
    return required + [name for name in optional if name in names and name not in required]


def clean_batch(
    df: pd.DataFrame,
    text_col: str,
    cond_col: str,
    require_gold: bool,
    include_techniques: set[str] | None,
    exclude_techniques: set[str],
) -> pd.DataFrame:
    df = df.copy()
    df[text_col] = df[text_col].map(as_text)
    df[cond_col] = df[cond_col].map(as_text).replace("", "unknown")
    mask = df[text_col].str.len() > 0
    if require_gold and "quality_band" in df.columns:
        mask &= df["quality_band"].map(as_text).str.lower().eq("gold")
    if "needs_ai" in df.columns:
        mask &= ~df["needs_ai"].fillna(False).astype(bool)
    if include_techniques is not None:
        mask &= df[cond_col].isin(include_techniques)
    if exclude_techniques:
        mask &= ~df[cond_col].isin(exclude_techniques)
    return df.loc[mask].reset_index(drop=True)


def iter_clean_batches(
    path: Path,
    text_col: str,
    cond_col: str,
    batch_size: int,
    limit: int | None,
    require_gold: bool,
    include_techniques: set[str] | None,
    exclude_techniques: set[str],
):
    columns = load_columns(path, text_col, cond_col)
    rows_out = 0
    parquet = pq.ParquetFile(path)
    for batch in parquet.iter_batches(batch_size=batch_size, columns=columns):
        df = clean_batch(
            batch.to_pandas(),
            text_col,
            cond_col,
            require_gold=require_gold,
            include_techniques=include_techniques,
            exclude_techniques=exclude_techniques,
        )
        if df.empty:
            continue
        if limit is not None:
            remaining = limit - rows_out
            if remaining <= 0:
                break
            df = df.head(remaining)
        rows_out += len(df)
        yield df
        if limit is not None and rows_out >= limit:
            break


def format_eta(done: int, total: int | None, started: float) -> str:
    elapsed = max(time.time() - started, 1e-6)
    rate = done / elapsed
    if not total or rate <= 0:
        return "unknown"
    remaining = max(total - done, 0) / rate
    return f"{remaining / 60:.1f}m"


def write_progress(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_vocab(args: argparse.Namespace, progress_file: Path) -> tuple[list[str], list[str], dict[str, Any]]:
    counter: Counter[str] = Counter()
    technique_counter: Counter[str] = Counter()
    rows = 0
    started = time.time()
    total_hint = args.limit_train or pq.ParquetFile(args.train_source).metadata.num_rows
    include_techniques = parse_technique_set(args.include_techniques)
    exclude_techniques = parse_technique_set(args.exclude_techniques) or set()

    print("Building vocab from gold train source")
    print(f"train_source={args.train_source}")
    for df in iter_clean_batches(
        args.train_source,
        args.text_col,
        args.cond_col,
        args.batch_size,
        args.limit_train,
        require_gold=not args.allow_non_gold,
        include_techniques=include_techniques,
        exclude_techniques=exclude_techniques,
    ):
        rows += len(df)
        technique_counter.update(df[args.cond_col].tolist())
        for text in df[args.text_col].tolist():
            counter.update(text.split())
        if rows % max(args.batch_size, 1) == 0 or rows >= total_hint:
            elapsed = time.time() - started
            rate = rows / elapsed if elapsed > 0 else 0.0
            eta = format_eta(rows, total_hint, started)
            print(f"vocab rows={rows:,}/{total_hint:,} rate={rate:.0f}/s eta={eta}", flush=True)
            write_progress(
                progress_file,
                {
                    "stage": "build_vocab",
                    "rows": rows,
                    "rows_total_hint": total_hint,
                    "rate_rows_per_sec": rate,
                    "eta": eta,
                    "elapsed_sec": elapsed,
                },
            )

    words = [w for w, c in counter.most_common() if c >= args.min_freq and w not in SPECIAL_TOKENS]
    if args.max_vocab and len(words) > args.max_vocab - len(SPECIAL_TOKENS):
        words = words[: args.max_vocab - len(SPECIAL_TOKENS)]
    vocab = SPECIAL_TOKENS + words

    seen_techniques = [t for t, _ in technique_counter.most_common()]
    techniques = [t for t in DEFAULT_TECHNIQUES if t in seen_techniques or t == "unknown"]
    techniques.extend(sorted(t for t in seen_techniques if t not in techniques))
    if "unknown" not in techniques:
        techniques.append("unknown")

    stats = {
        "train_rows_for_vocab": rows,
        "raw_token_types": len(counter),
        "vocab_size": len(vocab),
        "min_freq": args.min_freq,
        "max_vocab": args.max_vocab,
        "technique_counts": dict(technique_counter),
        "techniques": techniques,
        "include_techniques": sorted(include_techniques) if include_techniques is not None else None,
        "exclude_techniques": sorted(exclude_techniques),
    }
    return vocab, techniques, stats


def encode_fixed(text: str, token2id: dict[str, int], max_len: int) -> list[int]:
    ids = [token2id.get(tok, token2id[UNK]) for tok in text.split()]
    ids = ids[: max_len - 2]
    return [token2id[BOS], *ids, token2id[EOS]]


def flush_shard(
    split_dir: Path,
    split_name: str,
    shard_idx: int,
    input_rows: list[list[int]],
    cond_rows: list[int],
    row_ids: list[int],
    max_len: int,
    pad_id: int,
) -> dict[str, Any]:
    n_rows = len(input_rows)
    arr = np.full((n_rows, max_len), pad_id, dtype=np.int32)
    for idx, ids in enumerate(input_rows):
        arr[idx, : len(ids)] = ids
    path = split_dir / f"shard_{shard_idx:05d}.pt"
    torch.save(
        {
            "input_ids": torch.from_numpy(arr),
            "cond_ids": torch.tensor(cond_rows, dtype=torch.int16),
            "row_ids": torch.tensor(row_ids, dtype=torch.int64),
            "split": split_name,
            "max_len": max_len,
        },
        path,
    )
    return {"path": str(path), "rows": n_rows}


def write_split(
    split_name: str,
    source: Path,
    limit: int | None,
    args: argparse.Namespace,
    token2id: dict[str, int],
    technique2id: dict[str, int],
    progress_file: Path,
) -> dict[str, Any]:
    split_dir = args.cache_dir / split_name
    split_dir.mkdir(parents=True, exist_ok=True)
    pad_id = token2id[PAD]
    default_cond = technique2id.get("unknown", len(technique2id) - 1)
    total_hint = limit or pq.ParquetFile(source).metadata.num_rows
    started = time.time()
    rows = 0
    shard_idx = 0
    shards: list[dict[str, Any]] = []
    input_buffer: list[list[int]] = []
    cond_buffer: list[int] = []
    row_buffer: list[int] = []
    include_techniques = parse_technique_set(args.include_techniques)
    exclude_techniques = parse_technique_set(args.exclude_techniques) or set()

    print(f"Writing {split_name} token shards from {source}")
    for df in iter_clean_batches(
        source,
        args.text_col,
        args.cond_col,
        args.batch_size,
        limit,
        require_gold=not args.allow_non_gold,
        include_techniques=include_techniques,
        exclude_techniques=exclude_techniques,
    ):
        for rec in df.to_dict(orient="records"):
            row_id = int(rec.get("row_id", rows))
            text = as_text(rec.get(args.text_col))
            cond = as_text(rec.get(args.cond_col)) or "unknown"
            ids = encode_fixed(text, token2id, args.max_len)
            input_buffer.append(ids)
            cond_buffer.append(technique2id.get(cond, default_cond))
            row_buffer.append(row_id)
            rows += 1
            if len(input_buffer) >= args.shard_rows:
                shard = flush_shard(
                    split_dir,
                    split_name,
                    shard_idx,
                    input_buffer,
                    cond_buffer,
                    row_buffer,
                    args.max_len,
                    pad_id,
                )
                shards.append(shard)
                shard_idx += 1
                input_buffer, cond_buffer, row_buffer = [], [], []

        elapsed = time.time() - started
        rate = rows / elapsed if elapsed > 0 else 0.0
        eta = format_eta(rows, total_hint, started)
        print(f"{split_name} rows={rows:,}/{total_hint:,} shards={len(shards)} rate={rate:.0f}/s eta={eta}", flush=True)
        write_progress(
            progress_file,
            {
                "stage": f"write_{split_name}",
                "rows": rows,
                "rows_total_hint": total_hint,
                "shards": len(shards),
                "rate_rows_per_sec": rate,
                "eta": eta,
                "elapsed_sec": elapsed,
            },
        )

    if input_buffer:
        shard = flush_shard(
            split_dir,
            split_name,
            shard_idx,
            input_buffer,
            cond_buffer,
            row_buffer,
            args.max_len,
            pad_id,
        )
        shards.append(shard)

    return {
        "source": str(source),
        "rows": rows,
        "shards": shards,
        "shard_count": len(shards),
    }


def write_report(report_path: Path, manifest: dict[str, Any]) -> None:
    split_lines = []
    for split_name in ["train", "dev", "test"]:
        split = manifest["splits"][split_name]
        split_lines.append(f"| {split_name} | {split['rows']:,} | {split['shard_count']} |")

    lines = [
        "# 06 - Token Shard Preparation Report",
        "",
        f"**Run mode:** {manifest['run_mode']}",
        f"**Cache directory:** `{manifest['cache_dir']}`",
        f"**Text column:** `{manifest['text_col']}`",
        f"**Condition column:** `{manifest['cond_col']}`",
        f"**Max length:** `{manifest['max_len']}`",
        f"**Vocab size:** `{manifest['vocab']['vocab_size']:,}`",
        f"**Train rows for vocab:** `{manifest['vocab']['train_rows_for_vocab']:,}`",
        "",
        "## Split Shards",
        "",
        "| Split | Rows | Shards |",
        "|---|---:|---:|",
        *split_lines,
        "",
        "## Training Scope",
        "",
        "- Train source is `gold.parquet` by default.",
        "- `needs_ai=True`, non-gold, review queue, unknown-quality, silver, and bronze rows are not part of first-round train shards.",
        "- Shards are fixed-length token tensors so training can stream from disk instead of loading full parquet into RAM.",
        "",
    ]
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    args.cache_dir = ensure_under_phase(args.cache_dir)
    args.report_dir = ensure_under_phase(args.report_dir)
    args.log_dir = ensure_under_phase(args.log_dir)
    args.log_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    progress_file = args.log_dir / args.progress_name

    started = time.time()
    reset_output_dir(args.cache_dir, args.overwrite)
    run_mode = "full"
    if args.limit_train or args.limit_dev or args.limit_test:
        run_mode = "limited"

    vocab, techniques, vocab_stats = build_vocab(args, progress_file)
    token2id = {token: idx for idx, token in enumerate(vocab)}
    technique2id = {name: idx for idx, name in enumerate(techniques)}

    (args.cache_dir / "vocab.json").write_text(
        json.dumps(
            {
                "tokens": vocab,
                "token2id": token2id,
                "special_tokens": SPECIAL_TOKENS,
                "pad_id": token2id[PAD],
                "bos_id": token2id[BOS],
                "eos_id": token2id[EOS],
                "unk_id": token2id[UNK],
            },
            indent=2,
            ensure_ascii=False,
        )
        + "\n",
        encoding="utf-8",
    )
    (args.cache_dir / "techniques.json").write_text(
        json.dumps({"techniques": techniques, "technique2id": technique2id}, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    splits = {
        "train": write_split("train", args.train_source, args.limit_train, args, token2id, technique2id, progress_file),
        "dev": write_split("dev", args.dev_source, args.limit_dev, args, token2id, technique2id, progress_file),
        "test": write_split("test", args.test_source, args.limit_test, args, token2id, technique2id, progress_file),
    }

    elapsed = time.time() - started
    manifest = {
        "phase": 6,
        "run_mode": run_mode,
        "created_at_unix": time.time(),
        "elapsed_sec": elapsed,
        "cache_dir": str(args.cache_dir),
        "text_col": args.text_col,
        "cond_col": args.cond_col,
        "max_len": args.max_len,
        "shard_rows": args.shard_rows,
        "vocab": vocab_stats,
        "techniques": techniques,
        "splits": splits,
    }
    (args.cache_dir / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(args.report_dir / args.report_name, manifest)
    write_progress(
        progress_file,
        {
            "stage": "done",
            "elapsed_sec": elapsed,
            "cache_dir": str(args.cache_dir),
            "train_rows": splits["train"]["rows"],
            "dev_rows": splits["dev"]["rows"],
            "test_rows": splits["test"]["rows"],
        },
    )

    print("Phase 06 token shard preparation complete")
    print(f"elapsed={elapsed / 60:.1f}m")
    print(f"manifest={args.cache_dir / 'manifest.json'}")
    print(f"report={args.report_dir / args.report_name}")


if __name__ == "__main__":
    main()
