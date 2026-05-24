# -*- coding: utf-8 -*-
"""
Phase 08 - Script 5: anchor-only and mutation-engine surgery baselines.

This script deliberately stays below the H5' adversarial step. It provides:

1. Anchor-only masked infiller:
   a small conditional denoising LSTM trained with cross entropy on delex-space
   payload templates. Placeholder tokens are masked and reconstructed.

2. Mutation-engine baseline:
   deterministic, non-learned delex-space transformations used as a sanity
   baseline before claiming any GAN value.

The default settings are sized for an RTX 3050 6GB and 20GB RAM: small model,
mixed precision only when CUDA is available, bounded sequence length, and
explicit row/step limits for smoke runs.
"""

from __future__ import annotations

import argparse
import io
import json
import math
import random
import re
import sys
import time
from collections import Counter
from contextlib import nullcontext
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
import torch.nn as nn


if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


PHASE_DIR = Path(__file__).resolve().parent
DEFAULT_SPLIT_DIR = PHASE_DIR / "outputs" / "delex_cluster_split_smoke"
DEFAULT_OUT_DIR = PHASE_DIR / "outputs" / "surgery_baselines_smoke"
DEFAULT_CHECKPOINT_DIR = PHASE_DIR / "checkpoints" / "surgery_baselines_smoke"
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"
DEFAULT_LOG_DIR = PHASE_DIR / "logs"

SPACE_RE = re.compile(r"\s+")
TOKEN_RE = re.compile(r"__[A-Z0-9_]+__|@@|--|#|/\*|\*/|<=|>=|<>|!=|\|\||&&|[A-Za-z_][A-Za-z0-9_]*|\d+|[^\s]")
PLACEHOLDER_RE = re.compile(r"^__[a-z0-9_]+__$", re.IGNORECASE)
TECHNIQUES = ["benign", "boolean_blind", "error_based", "time_blind", "union_based", "unknown"]


class AnchorInfiller(nn.Module):
    def __init__(self, vocab_size: int, n_techniques: int, embed_dim: int, hidden_dim: int, pad_id: int, max_len: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_id)
        self.cond_embedding = nn.Embedding(n_techniques, embed_dim)
        self.pos_embedding = nn.Embedding(max_len, embed_dim)
        self.encoder = nn.Sequential(
            nn.Conv1d(embed_dim * 3, hidden_dim, kernel_size=3, padding=1),
            nn.GELU(),
            nn.Conv1d(hidden_dim, hidden_dim, kernel_size=3, padding=1),
            nn.GELU(),
        )
        self.head = nn.Sequential(
            nn.Linear(hidden_dim, hidden_dim),
            nn.GELU(),
            nn.Linear(hidden_dim, vocab_size),
        )

    def forward(self, input_ids: torch.Tensor, cond_ids: torch.Tensor) -> torch.Tensor:
        emb = self.embedding(input_ids)
        pos_ids = torch.arange(input_ids.size(1), device=input_ids.device).unsqueeze(0).expand_as(input_ids)
        pos = self.pos_embedding(pos_ids)
        cond = self.cond_embedding(cond_ids).unsqueeze(1).expand(-1, input_ids.size(1), -1)
        encoded = self.encoder(torch.cat([emb, cond, pos], dim=-1).transpose(1, 2)).transpose(1, 2)
        return self.head(encoded)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 8 surgery baselines before H5'.")
    parser.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--checkpoint-dir", type=Path, default=DEFAULT_CHECKPOINT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--text-col", default="payload_delex_v5")
    parser.add_argument("--technique-col", default="technique_primary")
    parser.add_argument("--train-limit", type=int, default=50000)
    parser.add_argument("--dev-limit", type=int, default=5000)
    parser.add_argument("--sample-count", type=int, default=120)
    parser.add_argument("--max-len", type=int, default=96)
    parser.add_argument("--max-vocab", type=int, default=2500)
    parser.add_argument("--embed-dim", type=int, default=64)
    parser.add_argument("--hidden-dim", type=int, default=128)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--max-steps", type=int, default=200)
    parser.add_argument("--eval-every", type=int, default=50)
    parser.add_argument("--log-every", type=int, default=25)
    parser.add_argument("--lr", type=float, default=2e-3)
    parser.add_argument("--mask-prob", type=float, default=0.8)
    parser.add_argument("--seed", type=int, default=260522)
    parser.add_argument("--no-mixed-precision", action="store_true")
    parser.add_argument("--allow-cpu", action="store_true")
    parser.add_argument("--report-name", default="08_surgery_baselines_smoke_report.md")
    parser.add_argument("--json-name", default="08_surgery_baselines_smoke_report.json")
    return parser.parse_args()


def ensure_under_phase(path: Path) -> Path:
    resolved = path.resolve()
    phase = PHASE_DIR.resolve()
    if resolved != phase and phase not in resolved.parents:
        raise ValueError(f"Refusing to write outside Phase 8: {resolved}")
    return resolved


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def as_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value)


def normalize_space(text: str) -> str:
    return SPACE_RE.sub(" ", text.strip())


def tokenize(text: str) -> list[str]:
    return TOKEN_RE.findall(normalize_space(text.lower()))


def read_split(path: Path, text_col: str, technique_col: str, limit: int | None) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(path)
    df = pd.read_parquet(path, columns=[text_col, technique_col])
    if limit is not None:
        df = df.head(limit)
    df[text_col] = df[text_col].map(as_text)
    df[technique_col] = df[technique_col].map(as_text).replace("", "unknown")
    df = df[df[text_col].str.len() > 0].copy()
    return df


def build_vocab(texts: list[str], max_vocab: int) -> dict[str, Any]:
    counter: Counter[str] = Counter()
    for text in texts:
        counter.update(tokenize(text))
    special = ["<PAD>", "<UNK>", "<MASK>"]
    common = [tok for tok, _ in counter.most_common(max(max_vocab - len(special), 1)) if tok not in special]
    tokens = special + common
    token_to_id = {tok: idx for idx, tok in enumerate(tokens)}
    return {
        "tokens": tokens,
        "token_to_id": token_to_id,
        "pad_id": token_to_id["<PAD>"],
        "unk_id": token_to_id["<UNK>"],
        "mask_id": token_to_id["<MASK>"],
    }


def technique_id(name: str) -> int:
    return TECHNIQUES.index(name) if name in TECHNIQUES else TECHNIQUES.index("unknown")


def encode_text(text: str, vocab: dict[str, Any], max_len: int) -> tuple[list[int], list[int]]:
    token_to_id = vocab["token_to_id"]
    ids = [token_to_id.get(tok, vocab["unk_id"]) for tok in tokenize(text)[:max_len]]
    placeholder_mask = [int(PLACEHOLDER_RE.match(tok) is not None) for tok in tokenize(text)[:max_len]]
    pad = max_len - len(ids)
    if pad > 0:
        ids.extend([vocab["pad_id"]] * pad)
        placeholder_mask.extend([0] * pad)
    return ids, placeholder_mask


def build_tensors(df: pd.DataFrame, args: argparse.Namespace, vocab: dict[str, Any]) -> dict[str, torch.Tensor]:
    encoded = [encode_text(text, vocab, args.max_len) for text in df[args.text_col].tolist()]
    ids = torch.tensor([row[0] for row in encoded], dtype=torch.long)
    placeholder_mask = torch.tensor([row[1] for row in encoded], dtype=torch.bool)
    cond = torch.tensor([technique_id(name) for name in df[args.technique_col].tolist()], dtype=torch.long)
    return {"ids": ids, "placeholder_mask": placeholder_mask, "cond": cond}


def corrupt_batch(ids: torch.Tensor, placeholder_mask: torch.Tensor, mask_id: int, mask_prob: float) -> torch.Tensor:
    corrupted = ids.clone()
    random_mask = torch.rand_like(ids, dtype=torch.float32) < mask_prob
    corrupted[placeholder_mask & random_mask] = mask_id
    return corrupted


def iter_batches(tensors: dict[str, torch.Tensor], batch_size: int, seed: int, step: int):
    n_rows = tensors["ids"].size(0)
    generator = torch.Generator()
    generator.manual_seed(seed + step * 1000003)
    order = torch.randperm(n_rows, generator=generator)
    for start in range(0, n_rows, batch_size):
        idx = order[start : start + batch_size]
        yield tensors["ids"].index_select(0, idx), tensors["placeholder_mask"].index_select(0, idx), tensors["cond"].index_select(0, idx)


def autocast_context(device: torch.device, enabled: bool):
    if not enabled:
        return nullcontext()
    try:
        return torch.amp.autocast(device_type=device.type, enabled=True)
    except (AttributeError, TypeError):
        return torch.cuda.amp.autocast(enabled=True)


def make_grad_scaler(enabled: bool):
    try:
        return torch.amp.GradScaler("cuda", enabled=enabled)
    except (AttributeError, TypeError):
        return torch.cuda.amp.GradScaler(enabled=enabled)


def device_summary(device: torch.device) -> dict[str, Any]:
    summary: dict[str, Any] = {"device": str(device), "cuda_available": torch.cuda.is_available()}
    if device.type == "cuda":
        props = torch.cuda.get_device_properties(device)
        summary.update(
            {
                "name": torch.cuda.get_device_name(device),
                "total_vram_gb": round(props.total_memory / 1024**3, 3),
                "allocated_gb": round(torch.cuda.memory_allocated(device) / 1024**3, 3),
                "reserved_gb": round(torch.cuda.memory_reserved(device) / 1024**3, 3),
            }
        )
    return summary


@torch.no_grad()
def evaluate_anchor(
    model: AnchorInfiller,
    tensors: dict[str, torch.Tensor],
    args: argparse.Namespace,
    vocab: dict[str, Any],
    device: torch.device,
    amp_enabled: bool,
    max_batches: int = 20,
) -> dict[str, float]:
    model.eval()
    criterion = nn.CrossEntropyLoss(ignore_index=vocab["pad_id"], reduction="sum")
    total_loss = 0.0
    total_slots = 0
    correct_slots = 0
    batches = 0
    for ids_cpu, placeholder_cpu, cond_cpu in iter_batches(tensors, args.batch_size, args.seed, 0):
        ids = ids_cpu.to(device)
        placeholder_mask = placeholder_cpu.to(device)
        cond = cond_cpu.to(device)
        corrupted = corrupt_batch(ids, placeholder_mask, vocab["mask_id"], 1.0)
        with autocast_context(device, amp_enabled):
            logits = model(corrupted, cond)
            targets = ids.masked_fill(~placeholder_mask, vocab["pad_id"])
            loss = criterion(logits.reshape(-1, logits.size(-1)), targets.reshape(-1))
        preds = logits.argmax(dim=-1)
        slot_count = int(placeholder_mask.sum().detach().cpu())
        correct_slots += int(((preds == ids) & placeholder_mask).sum().detach().cpu())
        total_slots += slot_count
        total_loss += float(loss.detach().cpu())
        batches += 1
        if batches >= max_batches:
            break
    model.train()
    return {
        "slot_loss": total_loss / max(total_slots, 1),
        "slot_accuracy": correct_slots / max(total_slots, 1),
        "slots": float(total_slots),
    }


def decode(ids: list[int], vocab: dict[str, Any]) -> str:
    tokens = vocab["tokens"]
    out = [tokens[idx] if 0 <= idx < len(tokens) else "<UNK>" for idx in ids if idx != vocab["pad_id"]]
    return normalize_space(" ".join(out))


@torch.no_grad()
def generate_anchor_samples(
    model: AnchorInfiller,
    df: pd.DataFrame,
    args: argparse.Namespace,
    vocab: dict[str, Any],
    device: torch.device,
    amp_enabled: bool,
) -> list[dict[str, Any]]:
    model.eval()
    rows = df.head(args.sample_count).copy()
    tensors = build_tensors(rows, args, vocab)
    ids = tensors["ids"].to(device)
    placeholder_mask = tensors["placeholder_mask"].to(device)
    cond = tensors["cond"].to(device)
    corrupted = corrupt_batch(ids, placeholder_mask, vocab["mask_id"], 1.0)
    with autocast_context(device, amp_enabled):
        logits = model(corrupted, cond)
    preds = logits.argmax(dim=-1)
    filled = ids.clone()
    filled[placeholder_mask] = preds[placeholder_mask]
    samples: list[dict[str, Any]] = []
    for idx, (_, row) in enumerate(rows.iterrows()):
        samples.append(
            {
                "sample_id": f"anchor_{idx}",
                "technique": as_text(row[args.technique_col]) or "unknown",
                "text": decode(filled[idx].detach().cpu().tolist(), vocab),
            }
        )
    model.train()
    return samples


def mutation_variants(text: str, rng: random.Random) -> str:
    out = normalize_space(text)
    if "__COMMENT__" in out:
        out = out.replace("__COMMENT__", rng.choice(["__COMMENT__", "--", "#", "/* */"]), 1)
    if "__NUM__ = __NUM__" in out and rng.random() < 0.5:
        out = out.replace("__NUM__ = __NUM__", "__NUM__ <> __NUM__", 1)
    if " union select " in out and rng.random() < 0.5:
        out = out.replace(" union select ", " union all select ", 1)
    if " or " in out and rng.random() < 0.5:
        out = out.replace(" or ", rng.choice([" OR ", " oR ", "/**/or/**/"]), 1)
    if " and " in out and rng.random() < 0.5:
        out = out.replace(" and ", rng.choice([" AND ", " aNd ", "/**/and/**/"]), 1)
    if "__TIME__" in out and rng.random() < 0.5:
        out = out.replace("__TIME__", rng.choice(["1", "3", "5"]), 1)
    return normalize_space(out)


def generate_mutation_samples(df: pd.DataFrame, args: argparse.Namespace) -> list[dict[str, Any]]:
    rng = random.Random(args.seed + 17)
    rows = df.head(args.sample_count).copy()
    samples: list[dict[str, Any]] = []
    for idx, (_, row) in enumerate(rows.iterrows()):
        samples.append(
            {
                "sample_id": f"mutation_{idx}",
                "technique": as_text(row[args.technique_col]) or "unknown",
                "text": mutation_variants(as_text(row[args.text_col]), rng),
            }
        )
    return samples


def sample_summary(samples: list[dict[str, Any]]) -> dict[str, Any]:
    texts = [sample["text"] for sample in samples]
    lengths = [len(tokenize(text)) for text in texts]
    return {
        "samples": len(samples),
        "unique_ratio": len(set(texts)) / len(texts) if texts else 0.0,
        "avg_tokens": float(np.mean(lengths)) if lengths else 0.0,
        "empty_count": sum(1 for text in texts if not text.strip()),
    }


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def progress(args: argparse.Namespace, stage: str, **payload: Any) -> None:
    save_json(
        args.log_dir / "phase08_surgery_baselines_progress.json",
        {"stage": stage, "time": time.time(), **payload},
    )


def write_report(path: Path, result: dict[str, Any]) -> None:
    lines = [
        "# 08 - Surgery Baselines Report",
        "",
        "Scope: pre-H5' baselines only. Anchor-only uses CE reconstruction; mutation-engine is non-learned.",
        "",
        "## Hardware-Aware Config",
        "",
        f"- Device: `{result['device']['device']}`",
        f"- CUDA available: `{result['device']['cuda_available']}`",
        f"- Train rows used: `{result['rows']['train']:,}`",
        f"- Dev rows used: `{result['rows']['dev']:,}`",
        f"- Batch size: `{result['config']['batch_size']}`",
        f"- Max steps: `{result['config']['max_steps']}`",
        f"- Max len: `{result['config']['max_len']}`",
        f"- Embed/hidden: `{result['config']['embed_dim']}` / `{result['config']['hidden_dim']}`",
        f"- Mixed precision: `{result['config']['mixed_precision']}`",
        "",
        "## Anchor-Only",
        "",
        f"- Final step: `{result['anchor']['final_step']}`",
        f"- Final train loss: `{result['anchor']['final_train_loss']:.6f}`",
        f"- Dev slot loss: `{result['anchor']['dev']['slot_loss']:.6f}`",
        f"- Dev slot accuracy: `{result['anchor']['dev']['slot_accuracy']:.4f}`",
        f"- Samples: `{result['anchor']['samples_path']}`",
        f"- Unique ratio: `{result['anchor']['sample_summary']['unique_ratio']:.4f}`",
        "",
        "## Mutation Engine",
        "",
        f"- Samples: `{result['mutation']['samples_path']}`",
        f"- Unique ratio: `{result['mutation']['sample_summary']['unique_ratio']:.4f}`",
        "",
        "## Next Gate",
        "",
        "Run `phase08_03_evaluator_contract.py` on both sample files before H5'. H5' should only be trained after these baselines are visible in the same validity/novelty/evasion table.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    args = parse_args()
    set_seed(args.seed)
    args.output_dir = ensure_under_phase(args.output_dir)
    args.checkpoint_dir = ensure_under_phase(args.checkpoint_dir)
    args.report_dir = ensure_under_phase(args.report_dir)
    args.log_dir = ensure_under_phase(args.log_dir)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    args.log_dir.mkdir(parents=True, exist_ok=True)
    progress(args, "start", split_dir=str(args.split_dir))

    train_df = read_split(args.split_dir / "train.parquet", args.text_col, args.technique_col, args.train_limit)
    dev_df = read_split(args.split_dir / "dev.parquet", args.text_col, args.technique_col, args.dev_limit)
    progress(args, "loaded_data", train_rows=len(train_df), dev_rows=len(dev_df))
    vocab = build_vocab(train_df[args.text_col].tolist(), args.max_vocab)
    progress(args, "built_vocab", vocab_size=len(vocab["tokens"]))
    train_tensors = build_tensors(train_df, args, vocab)
    dev_tensors = build_tensors(dev_df, args, vocab)
    train_slots = int(train_tensors["placeholder_mask"].sum().item())
    dev_slots = int(dev_tensors["placeholder_mask"].sum().item())
    if train_slots == 0:
        raise RuntimeError("No placeholder slots found in train split; check tokenization and placeholder regex.")
    progress(args, "built_tensors", train_rows=int(train_tensors["ids"].size(0)), dev_rows=int(dev_tensors["ids"].size(0)), train_slots=train_slots, dev_slots=dev_slots)

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type != "cuda" and not args.allow_cpu:
        raise RuntimeError("CUDA not visible. Use --allow-cpu for a debug smoke run.")
    amp_enabled = (not args.no_mixed_precision) and device.type == "cuda"
    model = AnchorInfiller(len(vocab["tokens"]), len(TECHNIQUES), args.embed_dim, args.hidden_dim, vocab["pad_id"], args.max_len).to(device)
    progress(args, "model_ready", device=device_summary(device), mixed_precision=amp_enabled)
    optimizer = torch.optim.AdamW(model.parameters(), lr=args.lr)
    scaler = make_grad_scaler(amp_enabled)
    criterion = nn.CrossEntropyLoss(ignore_index=vocab["pad_id"], reduction="sum")
    progress(args, "optimizer_ready", device=device_summary(device), mixed_precision=amp_enabled)
    started = time.time()
    history: list[dict[str, Any]] = []
    final_train_loss = math.nan

    print("Phase 08 - Surgery Baselines")
    print(f"device={device_summary(device)}")
    print(f"split_dir={args.split_dir}")
    print(f"train_rows={len(train_df):,} dev_rows={len(dev_df):,} vocab={len(vocab['tokens']):,}")
    print(
        "config batch_size={} max_steps={} max_len={} embed_dim={} hidden_dim={} amp={}".format(
            args.batch_size,
            args.max_steps,
            args.max_len,
            args.embed_dim,
            args.hidden_dim,
            amp_enabled,
        )
    )

    step = 0
    progress(args, "training_loop_start", max_steps=args.max_steps)
    while step < args.max_steps:
        for ids_cpu, placeholder_cpu, cond_cpu in iter_batches(train_tensors, args.batch_size, args.seed, step):
            slot_count = int(placeholder_cpu.sum().item())
            if slot_count == 0:
                continue
            ids = ids_cpu.to(device)
            placeholder_mask = placeholder_cpu.to(device)
            cond = cond_cpu.to(device)
            corrupted = corrupt_batch(ids, placeholder_mask, vocab["mask_id"], args.mask_prob)
            targets = ids.masked_fill(~placeholder_mask, vocab["pad_id"])

            optimizer.zero_grad(set_to_none=True)
            with autocast_context(device, amp_enabled):
                logits = model(corrupted, cond)
                loss = criterion(logits.reshape(-1, logits.size(-1)), targets.reshape(-1)) / max(slot_count, 1)
            if not torch.isfinite(loss):
                raise RuntimeError(f"Non-finite anchor loss: {float(loss.detach().cpu())}")
            scaler.scale(loss).backward()
            scaler.unscale_(optimizer)
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            scaler.step(optimizer)
            scaler.update()

            step += 1
            final_train_loss = float(loss.detach().cpu())
            if step % args.log_every == 0 or step == args.max_steps:
                elapsed = time.time() - started
                print(f"step={step}/{args.max_steps} train_slot_ce={final_train_loss:.5f} elapsed={elapsed:.1f}s", flush=True)
                save_json(
                    args.log_dir / "phase08_surgery_baselines_progress.json",
                    {
                        "stage": "training",
                        "step": step,
                        "max_steps": args.max_steps,
                        "train_slot_ce": final_train_loss,
                        "elapsed_sec": elapsed,
                        "device": device_summary(device),
                    },
                )
            if step % args.eval_every == 0 or step == args.max_steps:
                dev_metrics = evaluate_anchor(model, dev_tensors, args, vocab, device, amp_enabled)
                event = {"step": step, "train_slot_ce": final_train_loss, "dev": dev_metrics, "elapsed_sec": time.time() - started}
                history.append(event)
                print(
                    "eval step={} dev_slot_loss={:.5f} dev_slot_acc={:.4f}".format(
                        step,
                        dev_metrics["slot_loss"],
                        dev_metrics["slot_accuracy"],
                    ),
                    flush=True,
                )
            if step >= args.max_steps:
                break

    checkpoint_path = args.checkpoint_dir / "anchor_only_latest.pt"
    torch.save(
        {
            "model_state": model.state_dict(),
            "vocab": vocab,
            "techniques": TECHNIQUES,
            "args": vars(args),
            "global_step": step,
            "history": history,
        },
        checkpoint_path,
    )
    dev_metrics = history[-1]["dev"] if history else evaluate_anchor(model, dev_tensors, args, vocab, device, amp_enabled)
    anchor_samples = generate_anchor_samples(model, dev_df, args, vocab, device, amp_enabled)
    mutation_samples = generate_mutation_samples(dev_df, args)
    anchor_path = args.output_dir / "anchor_only_samples.jsonl"
    mutation_path = args.output_dir / "mutation_engine_samples.jsonl"
    write_jsonl(anchor_path, anchor_samples)
    write_jsonl(mutation_path, mutation_samples)

    result = {
        "split_dir": str(args.split_dir),
        "rows": {"train": len(train_df), "dev": len(dev_df)},
        "device": device_summary(device),
        "config": {
            "batch_size": args.batch_size,
            "max_steps": args.max_steps,
            "max_len": args.max_len,
            "embed_dim": args.embed_dim,
            "hidden_dim": args.hidden_dim,
            "mixed_precision": amp_enabled,
            "train_limit": args.train_limit,
            "dev_limit": args.dev_limit,
        },
        "anchor": {
            "final_step": step,
            "final_train_loss": final_train_loss,
            "dev": dev_metrics,
            "checkpoint": str(checkpoint_path),
            "samples_path": str(anchor_path),
            "sample_summary": sample_summary(anchor_samples),
        },
        "mutation": {
            "samples_path": str(mutation_path),
            "sample_summary": sample_summary(mutation_samples),
        },
        "history": history,
        "elapsed_sec": time.time() - started,
    }
    json_path = args.report_dir / args.json_name
    report_path = args.report_dir / args.report_name
    save_json(json_path, result)
    write_report(report_path, result)
    save_json(
        args.log_dir / "phase08_surgery_baselines_progress.json",
        {"stage": "done", "step": step, "elapsed_sec": result["elapsed_sec"], "device": result["device"]},
    )
    print("Phase 08 surgery baselines complete")
    print(f"anchor_samples={anchor_path}")
    print(f"mutation_samples={mutation_path}")
    print(f"checkpoint={checkpoint_path}")
    print(f"report={report_path}")


if __name__ == "__main__":
    main()
