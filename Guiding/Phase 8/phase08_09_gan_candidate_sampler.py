# -*- coding: utf-8 -*-
"""
Phase 08 - Script 9: sample many stochastic candidates from a trained H5'
paired surgery GAN checkpoint.

This is a generation-only utility. It does not train. It loads a checkpoint
from phase08_06_paired_surgery_gan.py, repeatedly samples from the same dev
frames, and writes a larger candidate pool for oracle reranking.
"""

from __future__ import annotations

import argparse
import io
import json
import sys
from pathlib import Path
from typing import Any

import torch

import phase08_06_paired_surgery_gan as gan


PHASE_DIR = Path(__file__).resolve().parent
DEFAULT_CHECKPOINT = PHASE_DIR / "checkpoints" / "paired_surgery_gan_max_aggressive" / "paired_surgery_gan_latest.pt"
DEFAULT_SPLIT_DIR = PHASE_DIR / "outputs" / "delex_cluster_split"
DEFAULT_OUT_DIR = PHASE_DIR / "outputs" / "gan_candidate_pools"
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Sample many candidates from a trained H5' checkpoint.")
    parser.add_argument("--checkpoint", type=Path, default=DEFAULT_CHECKPOINT)
    parser.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--name", default="paired_surgery_gan_max_aggressive_candidates")
    parser.add_argument("--row-count", type=int, default=1000)
    parser.add_argument("--rounds", type=int, default=8)
    parser.add_argument("--temperature", type=float, default=1.7)
    parser.add_argument("--top-k", type=int, default=24)
    parser.add_argument("--seed", type=int, default=230526)
    parser.add_argument("--allow-cpu", action="store_true")
    return parser.parse_args()


def ensure_under_phase(path: Path) -> Path:
    resolved = path.resolve()
    phase = PHASE_DIR.resolve()
    if resolved != phase and phase not in resolved.parents:
        raise ValueError(f"Refusing to write outside Phase 8: {resolved}")
    return resolved


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def main() -> None:
    args = parse_args()
    args.output_dir = ensure_under_phase(args.output_dir)
    args.report_dir = ensure_under_phase(args.report_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)

    checkpoint = gan.load_tensor_file(args.checkpoint)
    ck_args = checkpoint["args"]
    vocab = checkpoint["vocab"]
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type != "cuda" and not args.allow_cpu:
        raise RuntimeError("CUDA not visible. Use --allow-cpu for debug only.")
    amp_enabled = (not ck_args.get("no_mixed_precision", False)) and device.type == "cuda"

    model = gan.SurgeryGenerator(
        len(vocab["tokens"]),
        len(gan.TECHNIQUES),
        int(ck_args["embed_dim"]),
        int(ck_args["hidden_dim"]),
        int(vocab["pad_id"]),
        int(ck_args["max_len"]),
    ).to(device)
    model.load_state_dict(checkpoint["generator_state"])
    model.eval()

    slot_mode = str(ck_args.get("slot_mode", "aggressive"))
    sample_args = argparse.Namespace(
        text_col=str(ck_args.get("text_col", "payload_delex_v5")),
        technique_col=str(ck_args.get("technique_col", "technique_primary")),
        max_len=int(ck_args.get("max_len", 96)),
        slot_mode=slot_mode,
        sample_count=args.row_count,
        sample_temperature=args.temperature,
        sample_top_k=args.top_k,
        sample_argmax=False,
        seed=args.seed,
    )
    allowed_mask = gan.build_constrained_allowed_mask(vocab) if slot_mode == "constrained" else None
    dev_df = gan.read_split(args.split_dir / "dev.parquet", sample_args.text_col, sample_args.technique_col, args.row_count)

    all_rows: list[dict[str, Any]] = []
    for round_idx in range(args.rounds):
        gan.set_seed(args.seed + round_idx * 1009)
        rows = gan.generate_samples(model, dev_df, sample_args, vocab, device, amp_enabled, allowed_mask)
        for row_idx, row in enumerate(rows):
            row["sample_id"] = f"{args.name}_r{round_idx:02d}_{row_idx:05d}"
            row["candidate_round"] = round_idx
            row["candidate_source"] = args.name
            all_rows.append(row)

    samples_path = args.output_dir / f"{args.name}.jsonl"
    write_jsonl(samples_path, all_rows)
    summary = {
        "checkpoint": str(args.checkpoint),
        "samples": str(samples_path),
        "name": args.name,
        "rows_per_round": args.row_count,
        "rounds": args.rounds,
        "total_candidates": len(all_rows),
        "temperature": args.temperature,
        "top_k": args.top_k,
        "slot_mode": slot_mode,
        "sample_summary": gan.sample_summary(all_rows),
    }
    json_path = args.report_dir / f"08_candidate_sampler_{args.name}.json"
    md_path = args.report_dir / f"08_candidate_sampler_{args.name}.md"
    json_path.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    md_path.write_text(
        "\n".join(
            [
                "# 08 - GAN Candidate Sampler Report",
                "",
                f"- Checkpoint: `{summary['checkpoint']}`",
                f"- Samples: `{summary['samples']}`",
                f"- Total candidates: `{summary['total_candidates']:,}`",
                f"- Rows per round: `{summary['rows_per_round']:,}`",
                f"- Rounds: `{summary['rounds']}`",
                f"- Temperature/top-k: `{summary['temperature']}` / `{summary['top_k']}`",
                f"- Slot mode: `{summary['slot_mode']}`",
                f"- Unique ratio: `{summary['sample_summary']['unique_ratio']:.4f}`",
                "",
            ]
        ),
        encoding="utf-8",
    )
    print(f"samples={samples_path}")
    print(f"report={md_path}")
    print(f"json={json_path}")


if __name__ == "__main__":
    main()
