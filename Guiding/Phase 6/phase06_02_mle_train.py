# -*- coding: utf-8 -*-
"""
Phase 06 - Script 2: MLE/Warmup baseline training.

The trainer consumes token shards from phase06_01_tokenize_shards.py, uses a
small conditional LSTM, mixed precision on CUDA, gradient accumulation, and
checkpoint/resume. Gumbel-SeqGAN should only start after this baseline passes
the gates documented in 00_Nhan_Dinh_Phase_6.md.
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
from typing import Any, Iterable

import numpy as np
import torch
import torch.nn as nn


if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


PHASE_DIR = Path(__file__).resolve().parent
DEFAULT_CONFIG = PHASE_DIR / "configs" / "mle_baseline.json"
DEFAULT_CACHE_DIR = PHASE_DIR / "cache" / "token_shards"
DEFAULT_CHECKPOINT_DIR = PHASE_DIR / "checkpoints" / "mle_baseline"
DEFAULT_OUTPUT_DIR = PHASE_DIR / "outputs" / "mle_baseline"
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"
DEFAULT_LOG_DIR = PHASE_DIR / "logs"

SQL_RE = re.compile(
    r"\b(select|union|from|where|insert|update|delete|drop|exec|alter|create|sleep|benchmark)\b",
    re.IGNORECASE,
)


class ConditionalLSTM(nn.Module):
    def __init__(self, vocab_size: int, n_techniques: int, embed_dim: int, hidden_dim: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.cond_embed = nn.Embedding(n_techniques, embed_dim)
        self.lstm = nn.LSTM(embed_dim * 2, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        emb = self.embedding(x)
        cond_emb = self.cond_embed(cond).unsqueeze(1).expand(-1, x.size(1), -1)
        out, _ = self.lstm(torch.cat([emb, cond_emb], dim=-1))
        return self.fc(out)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train Phase 6 MLE baseline.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--checkpoint-dir", type=Path, default=DEFAULT_CHECKPOINT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--resume", type=Path, default=None)
    parser.add_argument("--resume-latest", action="store_true")
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--grad-accum", type=int, default=None)
    parser.add_argument("--eval-every", type=int, default=None)
    parser.add_argument("--save-every", type=int, default=None)
    parser.add_argument("--log-every", type=int, default=None)
    parser.add_argument("--eval-max-batches", type=int, default=None)
    parser.add_argument("--sample-count", type=int, default=None)
    parser.add_argument("--no-mixed-precision", action="store_true")
    return parser.parse_args()


def ensure_under_phase(path: Path) -> Path:
    resolved = path.resolve()
    phase = PHASE_DIR.resolve()
    if resolved != phase and phase not in resolved.parents:
        raise ValueError(f"Refusing to write outside Phase 6: {resolved}")
    return resolved


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_tensor_file(path: Path) -> dict[str, Any]:
    try:
        return torch.load(path, map_location="cpu", weights_only=True)
    except TypeError:
        return torch.load(path, map_location="cpu")


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def merged_config(args: argparse.Namespace) -> dict[str, Any]:
    cfg = load_json(args.config)
    overrides = {
        "epochs": args.epochs,
        "max_steps": args.max_steps,
        "batch_size": args.batch_size,
        "grad_accum": args.grad_accum,
        "eval_every": args.eval_every,
        "save_every": args.save_every,
        "log_every": args.log_every,
        "eval_max_batches": args.eval_max_batches,
        "sample_count": args.sample_count,
    }
    for key, value in overrides.items():
        if value is not None:
            cfg[key] = value
    if args.no_mixed_precision:
        cfg["mixed_precision"] = False
    return cfg


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def shard_paths(cache_dir: Path, split: str) -> list[Path]:
    paths = sorted((cache_dir / split).glob("shard_*.pt"))
    if not paths:
        raise FileNotFoundError(f"No token shards found for split={split}: {cache_dir / split}")
    return paths


def iter_shard_batches(
    paths: list[Path],
    batch_size: int,
    shuffle: bool,
    seed: int,
    epoch: int,
) -> Iterable[tuple[torch.Tensor, torch.Tensor]]:
    local_paths = list(paths)
    rng = random.Random(seed + epoch)
    if shuffle:
        rng.shuffle(local_paths)

    for shard_idx, path in enumerate(local_paths):
        payload = load_tensor_file(path)
        x = payload["input_ids"].long()
        cond = payload["cond_ids"].long()
        n_rows = x.size(0)
        if shuffle:
            generator = torch.Generator()
            generator.manual_seed(seed + epoch * 1000003 + shard_idx)
            order = torch.randperm(n_rows, generator=generator)
        else:
            order = torch.arange(n_rows)
        for start in range(0, n_rows, batch_size):
            idx = order[start : start + batch_size]
            yield x.index_select(0, idx), cond.index_select(0, idx)


def make_grad_scaler(enabled: bool):
    try:
        return torch.amp.GradScaler("cuda", enabled=enabled)
    except (AttributeError, TypeError):
        return torch.cuda.amp.GradScaler(enabled=enabled)


def autocast_context(device: torch.device, enabled: bool):
    if not enabled:
        return nullcontext()
    try:
        return torch.amp.autocast(device_type=device.type, enabled=True)
    except (AttributeError, TypeError):
        return torch.cuda.amp.autocast(enabled=True)


def top_k_top_p_filter(logits: torch.Tensor, top_k: int, top_p: float) -> torch.Tensor:
    logits = logits.clone()
    if top_k > 0:
        kth = torch.topk(logits, min(top_k, logits.size(-1))).values[..., -1, None]
        logits = logits.masked_fill(logits < kth, float("-inf"))
    if top_p < 1.0:
        sorted_logits, sorted_idx = torch.sort(logits, descending=True)
        probs = torch.softmax(sorted_logits, dim=-1)
        cum_probs = torch.cumsum(probs, dim=-1)
        remove = cum_probs - probs > top_p
        sorted_logits[remove] = float("-inf")
        logits.scatter_(-1, sorted_idx, sorted_logits)
    return logits


@torch.no_grad()
def generate_samples(
    model: ConditionalLSTM,
    vocab: dict[str, Any],
    techniques: list[str],
    device: torch.device,
    cfg: dict[str, Any],
) -> list[dict[str, Any]]:
    model.eval()
    tokens = vocab["tokens"]
    bos_id = int(vocab["bos_id"])
    eos_id = int(vocab["eos_id"])
    pad_id = int(vocab["pad_id"])
    samples: list[dict[str, Any]] = []
    technique_ids = [(idx, name) for idx, name in enumerate(techniques) if name != "unknown"]
    per_tech = max(int(cfg["sample_count"]) // max(len(technique_ids), 1), 1)
    max_len = int(cfg["max_len"])

    for tech_id, tech_name in technique_ids:
        cond = torch.tensor([tech_id], device=device)
        for _ in range(per_tech):
            ids = [bos_id]
            hidden = None
            for _step in range(max_len - 1):
                x = torch.tensor([[ids[-1]]], dtype=torch.long, device=device)
                emb = model.embedding(x)
                cond_emb = model.cond_embed(cond).unsqueeze(1)
                out, hidden = model.lstm(torch.cat([emb, cond_emb], dim=-1), hidden)
                logits = model.fc(out[:, -1, :])[0] / float(cfg["sample_temperature"])
                logits = top_k_top_p_filter(logits, int(cfg["sample_top_k"]), float(cfg["sample_top_p"]))
                prob = torch.softmax(logits, dim=-1)
                next_id = torch.multinomial(prob, 1).item()
                if next_id == eos_id:
                    break
                ids.append(next_id)
            text_tokens = [tokens[i] for i in ids if i not in (bos_id, eos_id, pad_id) and i < len(tokens)]
            samples.append({"technique": tech_name, "text": " ".join(text_tokens)})
    return samples


def sample_metrics(samples: list[dict[str, Any]]) -> dict[str, Any]:
    texts = [sample["text"] for sample in samples]
    unique = set(texts)
    token_counter: Counter[str] = Counter()
    lengths = []
    for text in texts:
        toks = text.split()
        lengths.append(len(toks))
        token_counter.update(toks)
    total_tokens = sum(token_counter.values())
    entropy = 0.0
    if total_tokens:
        entropy = float(-sum((c / total_tokens) * math.log2(c / total_tokens) for c in token_counter.values()))
    return {
        "n_total": len(texts),
        "unique_ratio": len(unique) / len(texts) if texts else 0.0,
        "syntax_validity_rate": sum(1 for text in texts if SQL_RE.search(text)) / len(texts) if texts else 0.0,
        "token_entropy": entropy,
        "avg_len": float(np.mean(lengths)) if lengths else 0.0,
        "empty_count": sum(1 for text in texts if not text.strip()),
    }


@torch.no_grad()
def evaluate_loss(
    model: ConditionalLSTM,
    paths: list[Path],
    batch_size: int,
    device: torch.device,
    pad_id: int,
    vocab_size: int,
    amp_enabled: bool,
    max_batches: int | None,
) -> float:
    model.eval()
    criterion = nn.CrossEntropyLoss(ignore_index=pad_id, reduction="sum")
    total_loss = 0.0
    total_tokens = 0
    for batch_idx, (x_cpu, cond_cpu) in enumerate(iter_shard_batches(paths, batch_size, False, 0, 0), start=1):
        x = x_cpu.to(device, non_blocking=True)
        cond = cond_cpu.to(device, non_blocking=True)
        with autocast_context(device, amp_enabled):
            logits = model(x[:, :-1], cond)
            target = x[:, 1:]
            loss = criterion(logits.reshape(-1, vocab_size), target.reshape(-1))
        total_loss += float(loss.detach().cpu())
        total_tokens += int((target != pad_id).sum().detach().cpu())
        if max_batches is not None and batch_idx >= max_batches:
            break
    return total_loss / max(total_tokens, 1)


def checkpoint_payload(
    model: ConditionalLSTM,
    optimizer: torch.optim.Optimizer,
    scaler: Any,
    cfg: dict[str, Any],
    epoch: int,
    global_step: int,
    best_val_loss: float,
    manifest: dict[str, Any],
) -> dict[str, Any]:
    return {
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "scaler_state": scaler.state_dict() if scaler is not None else None,
        "config": cfg,
        "epoch": epoch,
        "global_step": global_step,
        "best_val_loss": best_val_loss,
        "manifest": {
            "cache_dir": manifest.get("cache_dir"),
            "max_len": manifest.get("max_len"),
            "vocab_size": manifest.get("vocab", {}).get("vocab_size"),
            "techniques": manifest.get("techniques"),
        },
    }


def save_checkpoint(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(payload, path)


def find_latest_checkpoint(checkpoint_dir: Path) -> Path | None:
    latest = checkpoint_dir / "latest.pt"
    if latest.exists():
        return latest
    candidates = sorted(checkpoint_dir.glob("step_*.pt"))
    return candidates[-1] if candidates else None


def write_samples(path: Path, samples: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for sample in samples:
            handle.write(json.dumps(sample, ensure_ascii=False) + "\n")


def write_report(
    path: Path,
    cfg: dict[str, Any],
    manifest: dict[str, Any],
    device: torch.device,
    history: list[dict[str, Any]],
    metrics: dict[str, Any] | None,
    checkpoint_dir: Path,
) -> None:
    latest = history[-1] if history else {}
    gate_lines = []
    if latest:
        val_ok = latest.get("val_loss") is not None and math.isfinite(float(latest.get("val_loss")))
        gate_lines.append(f"- Loss finite: `{'yes' if val_ok else 'no'}`")
    if metrics:
        gate_lines.append(f"- Unique ratio: `{metrics['unique_ratio']:.4f}`")
        gate_lines.append(f"- Syntax validity rate: `{metrics['syntax_validity_rate']:.4f}`")
        gate_lines.append(f"- Empty sample count: `{metrics['empty_count']}`")
    gate_lines.extend(
        [
            f"- Latest checkpoint: `{checkpoint_dir / 'latest.pt'}`",
            f"- Best checkpoint: `{checkpoint_dir / 'best.pt'}`",
        ]
    )

    lines = [
        "# 06 - MLE Baseline Report",
        "",
        f"**Device:** `{device}`",
        f"**Train rows:** `{manifest['splits']['train']['rows']:,}`",
        f"**Dev rows:** `{manifest['splits']['dev']['rows']:,}`",
        f"**Test rows:** `{manifest['splits']['test']['rows']:,}`",
        f"**Vocab size:** `{manifest['vocab']['vocab_size']:,}`",
        f"**Batch/grad accum:** `{cfg['batch_size']}` / `{cfg['grad_accum']}`",
        f"**Max len:** `{cfg['max_len']}`",
        f"**Embed/hidden:** `{cfg['embed_dim']}` / `{cfg['hidden_dim']}`",
        f"**Mixed precision:** `{cfg['mixed_precision']}`",
        "",
        "## Latest Progress",
        "",
        f"- Global step: `{latest.get('global_step', 0)}`",
        f"- Epoch: `{latest.get('epoch', 0)}`",
        f"- Train loss: `{latest.get('train_loss', 'n/a')}`",
        f"- Val loss: `{latest.get('val_loss', 'n/a')}`",
        "",
        "## Gate Snapshot",
        "",
        *gate_lines,
        "",
        "## Scope Note",
        "",
        "This is still the MLE/Warmup baseline stage. Do not start Gumbel-SeqGAN until OOM, loss, checkpoint/resume, and diversity gates pass on a representative run.",
        "",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines), encoding="utf-8")


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


def format_eta(done_steps: int, total_steps: int | None, started: float) -> str:
    elapsed = max(time.time() - started, 1e-6)
    rate = done_steps / elapsed
    if not total_steps or rate <= 0:
        return "unknown"
    remaining = max(total_steps - done_steps, 0) / rate
    return f"{remaining / 60:.1f}m"


def main() -> None:
    args = parse_args()
    cfg = merged_config(args)
    args.cache_dir = args.cache_dir.resolve()
    args.checkpoint_dir = ensure_under_phase(args.checkpoint_dir)
    args.output_dir = ensure_under_phase(args.output_dir)
    args.report_dir = ensure_under_phase(args.report_dir)
    args.log_dir = ensure_under_phase(args.log_dir)
    args.checkpoint_dir.mkdir(parents=True, exist_ok=True)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    args.log_dir.mkdir(parents=True, exist_ok=True)

    set_seed(int(cfg["seed"]))
    manifest = load_json(args.cache_dir / "manifest.json")
    vocab = load_json(args.cache_dir / "vocab.json")
    techniques_payload = load_json(args.cache_dir / "techniques.json")
    techniques = techniques_payload["techniques"]
    vocab_size = len(vocab["tokens"])
    pad_id = int(vocab["pad_id"])

    cfg["max_len"] = int(manifest["max_len"])
    train_paths = shard_paths(args.cache_dir, "train")
    dev_paths = shard_paths(args.cache_dir, "dev")
    test_paths = shard_paths(args.cache_dir, "test")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    amp_enabled = bool(cfg["mixed_precision"]) and device.type == "cuda"
    cfg["mixed_precision"] = amp_enabled

    model = ConditionalLSTM(vocab_size, len(techniques), int(cfg["embed_dim"]), int(cfg["hidden_dim"])).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=float(cfg["lr"]))
    scaler = make_grad_scaler(amp_enabled)
    criterion = nn.CrossEntropyLoss(ignore_index=pad_id)

    start_epoch = 0
    global_step = 0
    best_val_loss = float("inf")
    resume_path = args.resume
    if args.resume_latest and resume_path is None:
        resume_path = find_latest_checkpoint(args.checkpoint_dir)
    if resume_path:
        checkpoint = load_tensor_file(resume_path)
        model.load_state_dict(checkpoint["model_state"])
        optimizer.load_state_dict(checkpoint["optimizer_state"])
        if checkpoint.get("scaler_state") and scaler is not None:
            scaler.load_state_dict(checkpoint["scaler_state"])
        start_epoch = int(checkpoint.get("epoch", 0))
        global_step = int(checkpoint.get("global_step", 0))
        best_val_loss = float(checkpoint.get("best_val_loss", best_val_loss))
        print(f"Resumed checkpoint: {resume_path} step={global_step} epoch={start_epoch}")

    train_rows = int(manifest["splits"]["train"]["rows"])
    batches_per_epoch = math.ceil(train_rows / int(cfg["batch_size"]))
    steps_per_epoch = math.ceil(batches_per_epoch / int(cfg["grad_accum"]))
    total_steps = int(cfg["max_steps"]) if cfg.get("max_steps") else int(cfg["epochs"]) * steps_per_epoch
    progress_file = args.log_dir / "phase06_mle_progress.json"
    history_file = args.output_dir / "history.jsonl"
    history: list[dict[str, Any]] = []
    latest_metrics: dict[str, Any] | None = None
    started = time.time()

    print("Phase 06 - MLE/Warmup Baseline")
    print(f"device={device_summary(device)}")
    print(f"cache_dir={args.cache_dir}")
    print(f"checkpoint_dir={args.checkpoint_dir}")
    print(f"train_rows={train_rows:,} dev_rows={manifest['splits']['dev']['rows']:,} test_rows={manifest['splits']['test']['rows']:,}")
    print(
        "config batch_size={} grad_accum={} max_len={} embed_dim={} hidden_dim={} amp={}".format(
            cfg["batch_size"],
            cfg["grad_accum"],
            cfg["max_len"],
            cfg["embed_dim"],
            cfg["hidden_dim"],
            amp_enabled,
        )
    )
    print(f"estimated_total_steps={total_steps:,} starting_step={global_step:,}")

    optimizer.zero_grad(set_to_none=True)
    try:
        for epoch in range(start_epoch, int(cfg["epochs"])):
            model.train()
            running_loss = 0.0
            running_batches = 0
            accum_count = 0
            for x_cpu, cond_cpu in iter_shard_batches(
                train_paths,
                int(cfg["batch_size"]),
                shuffle=True,
                seed=int(cfg["seed"]),
                epoch=epoch,
            ):
                x = x_cpu.to(device, non_blocking=True)
                cond = cond_cpu.to(device, non_blocking=True)
                with autocast_context(device, amp_enabled):
                    logits = model(x[:, :-1], cond)
                    target = x[:, 1:]
                    loss = criterion(logits.reshape(-1, vocab_size), target.reshape(-1))
                    scaled_loss = loss / int(cfg["grad_accum"])
                if not torch.isfinite(loss):
                    raise RuntimeError(f"Non-finite loss detected: {float(loss.detach().cpu())}")

                scaler.scale(scaled_loss).backward()
                running_loss += float(loss.detach().cpu())
                running_batches += 1
                accum_count += 1

                if accum_count >= int(cfg["grad_accum"]):
                    scaler.unscale_(optimizer)
                    nn.utils.clip_grad_norm_(model.parameters(), float(cfg["clip_grad"]))
                    scaler.step(optimizer)
                    scaler.update()
                    optimizer.zero_grad(set_to_none=True)
                    accum_count = 0
                    global_step += 1

                    should_log = global_step % int(cfg["log_every"]) == 0
                    should_eval = global_step % int(cfg["eval_every"]) == 0
                    should_save = global_step % int(cfg["save_every"]) == 0
                    reached_max = bool(cfg.get("max_steps")) and global_step >= int(cfg["max_steps"])

                    if should_log or should_eval or should_save or reached_max:
                        avg_train_loss = running_loss / max(running_batches, 1)
                        eta = format_eta(global_step, total_steps, started)
                        elapsed = time.time() - started
                        progress = {
                            "stage": "training",
                            "epoch": epoch,
                            "global_step": global_step,
                            "total_steps": total_steps,
                            "train_loss": avg_train_loss,
                            "elapsed_sec": elapsed,
                            "eta": eta,
                            "device": device_summary(device),
                        }
                        print(
                            f"epoch={epoch} step={global_step:,}/{total_steps:,} train_loss={avg_train_loss:.5f} eta={eta}",
                            flush=True,
                        )
                        save_json(progress_file, progress)

                    if should_eval or reached_max:
                        val_loss = evaluate_loss(
                            model,
                            dev_paths,
                            int(cfg["batch_size"]),
                            device,
                            pad_id,
                            vocab_size,
                            amp_enabled,
                            int(cfg["eval_max_batches"]) if cfg.get("eval_max_batches") else None,
                        )
                        samples = generate_samples(model, vocab, techniques, device, cfg)
                        latest_metrics = sample_metrics(samples)
                        sample_path = args.output_dir / f"samples_step_{global_step:08d}.jsonl"
                        write_samples(sample_path, samples)
                        event = {
                            "epoch": epoch,
                            "global_step": global_step,
                            "train_loss": avg_train_loss,
                            "val_loss": val_loss,
                            "sample_metrics": latest_metrics,
                            "sample_path": str(sample_path),
                            "elapsed_sec": time.time() - started,
                        }
                        history.append(event)
                        with history_file.open("a", encoding="utf-8") as handle:
                            handle.write(json.dumps(event, ensure_ascii=False) + "\n")
                        print(
                            "eval step={} val_loss={:.6f} unique_ratio={:.4f} syntax={:.4f}".format(
                                global_step,
                                val_loss,
                                latest_metrics["unique_ratio"],
                                latest_metrics["syntax_validity_rate"],
                            ),
                            flush=True,
                        )
                        if val_loss < best_val_loss:
                            best_val_loss = val_loss
                            save_checkpoint(
                                args.checkpoint_dir / "best.pt",
                                checkpoint_payload(model, optimizer, scaler, cfg, epoch, global_step, best_val_loss, manifest),
                            )
                        write_report(
                            args.report_dir / "06_mle_baseline_report.md",
                            cfg,
                            manifest,
                            device,
                            history,
                            latest_metrics,
                            args.checkpoint_dir,
                        )
                        model.train()

                    if should_save or should_eval or reached_max:
                        payload = checkpoint_payload(model, optimizer, scaler, cfg, epoch, global_step, best_val_loss, manifest)
                        save_checkpoint(args.checkpoint_dir / "latest.pt", payload)
                        if should_save:
                            save_checkpoint(args.checkpoint_dir / f"step_{global_step:08d}.pt", payload)

                    if reached_max:
                        break

            if accum_count:
                scaler.unscale_(optimizer)
                nn.utils.clip_grad_norm_(model.parameters(), float(cfg["clip_grad"]))
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad(set_to_none=True)
                global_step += 1

            if bool(cfg.get("max_steps")) and global_step >= int(cfg["max_steps"]):
                break

        if not history:
            val_loss = evaluate_loss(
                model,
                dev_paths,
                int(cfg["batch_size"]),
                device,
                pad_id,
                vocab_size,
                amp_enabled,
                int(cfg["eval_max_batches"]) if cfg.get("eval_max_batches") else None,
            )
            samples = generate_samples(model, vocab, techniques, device, cfg)
            latest_metrics = sample_metrics(samples)
            sample_path = args.output_dir / f"samples_step_{global_step:08d}.jsonl"
            write_samples(sample_path, samples)
            history.append(
                {
                    "epoch": start_epoch,
                    "global_step": global_step,
                    "train_loss": None,
                    "val_loss": val_loss,
                    "sample_metrics": latest_metrics,
                    "sample_path": str(sample_path),
                    "elapsed_sec": time.time() - started,
                }
            )

        payload = checkpoint_payload(model, optimizer, scaler, cfg, start_epoch, global_step, best_val_loss, manifest)
        save_checkpoint(args.checkpoint_dir / "latest.pt", payload)
        write_report(args.report_dir / "06_mle_baseline_report.md", cfg, manifest, device, history, latest_metrics, args.checkpoint_dir)
        save_json(
            progress_file,
            {
                "stage": "done",
                "global_step": global_step,
                "best_val_loss": best_val_loss,
                "elapsed_sec": time.time() - started,
                "device": device_summary(device),
            },
        )
        print("Phase 06 MLE baseline complete")
        print(f"global_step={global_step:,} best_val_loss={best_val_loss:.6f}")
        print(f"latest_checkpoint={args.checkpoint_dir / 'latest.pt'}")
        print(f"report={args.report_dir / '06_mle_baseline_report.md'}")

    except RuntimeError as exc:
        if "out of memory" in str(exc).lower() and torch.cuda.is_available():
            torch.cuda.empty_cache()
            print("CUDA OOM detected. Recommended reduction order: batch_size, max_len, hidden_dim, embed_dim.", file=sys.stderr)
        raise


if __name__ == "__main__":
    main()
