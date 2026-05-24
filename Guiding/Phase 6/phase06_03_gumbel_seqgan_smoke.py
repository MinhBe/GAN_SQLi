# -*- coding: utf-8 -*-
"""
Phase 06 - Script 3: Gumbel-SeqGAN smoke run.

This is intentionally a small adversarial smoke test, not a full GAN run.
It starts from the Phase 6 MLE best checkpoint, streams token shards, keeps an
MLE anchor loss, and writes collapse/diversity diagnostics.
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
import torch.nn.functional as F


if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


PHASE_DIR = Path(__file__).resolve().parent
ROOT = PHASE_DIR.parent.parent
DEFAULT_CONFIG = PHASE_DIR / "configs" / "gumbel_seqgan_smoke.json"
DEFAULT_CACHE_DIR = PHASE_DIR / "cache" / "token_shards"
DEFAULT_CHECKPOINT_DIR = PHASE_DIR / "checkpoints" / "gumbel_seqgan_smoke"
DEFAULT_OUTPUT_DIR = PHASE_DIR / "outputs" / "gumbel_seqgan_smoke"
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"
DEFAULT_LOG_DIR = PHASE_DIR / "logs"

SQL_RE = re.compile(
    r"\b(select|union|from|where|insert|update|delete|drop|exec|alter|create|sleep|benchmark)\b",
    re.IGNORECASE,
)


class ConditionalGumbelGenerator(nn.Module):
    def __init__(self, vocab_size: int, n_techniques: int, embed_dim: int, hidden_dim: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.cond_embed = nn.Embedding(n_techniques, embed_dim)
        self.lstm = nn.LSTM(embed_dim * 2, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)
        self.vocab_size = vocab_size

    def forward_logits(self, x: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        emb = self.embedding(x)
        cond_emb = self.cond_embed(cond).unsqueeze(1).expand(-1, x.size(1), -1)
        out, _ = self.lstm(torch.cat([emb, cond_emb], dim=-1))
        return self.fc(out)

    def generate_soft(self, cond: torch.Tensor, length: int, tau: float, bos_id: int) -> torch.Tensor:
        batch_size = cond.size(0)
        ids = torch.full((batch_size, 1), bos_id, dtype=torch.long, device=cond.device)
        hidden = None
        outputs: list[torch.Tensor] = []
        for _ in range(length):
            emb = self.embedding(ids[:, -1:])
            cond_emb = self.cond_embed(cond).unsqueeze(1)
            out, hidden = self.lstm(torch.cat([emb, cond_emb], dim=-1), hidden)
            logits = self.fc(out[:, -1, :])
            soft = F.gumbel_softmax(logits, tau=tau, hard=False, dim=-1)
            outputs.append(soft.unsqueeze(1))
            ids = torch.cat([ids, soft.argmax(dim=-1, keepdim=True)], dim=1)
        return torch.cat(outputs, dim=1)


class ConditionalDiscriminator(nn.Module):
    def __init__(self, embed_dim: int, hidden_dim: int, n_techniques: int):
        super().__init__()
        self.cond_embed = nn.Embedding(n_techniques, embed_dim)
        self.lstm = nn.LSTM(embed_dim * 2, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, 1),
        )

    def forward(self, emb: torch.Tensor, cond: torch.Tensor) -> torch.Tensor:
        cond_emb = self.cond_embed(cond).unsqueeze(1).expand(-1, emb.size(1), -1)
        _, (h, _) = self.lstm(torch.cat([emb, cond_emb], dim=-1))
        h_last = torch.cat([h[-2], h[-1]], dim=-1)
        return self.fc(h_last).squeeze(-1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Phase 6 Gumbel-SeqGAN smoke test.")
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--cache-dir", type=Path, default=DEFAULT_CACHE_DIR)
    parser.add_argument("--checkpoint-dir", type=Path, default=DEFAULT_CHECKPOINT_DIR)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--mle-checkpoint", type=Path, default=None)
    parser.add_argument("--resume", type=Path, default=None)
    parser.add_argument("--resume-latest", action="store_true")
    parser.add_argument("--max-steps", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--eval-every", type=int, default=None)
    parser.add_argument("--save-every", type=int, default=None)
    parser.add_argument("--log-every", type=int, default=None)
    parser.add_argument("--sample-count", type=int, default=None)
    parser.add_argument("--no-mixed-precision", action="store_true")
    parser.add_argument("--allow-cpu", action="store_true")
    return parser.parse_args()


def ensure_under_phase(path: Path) -> Path:
    resolved = path.resolve()
    phase = PHASE_DIR.resolve()
    if resolved != phase and phase not in resolved.parents:
        raise ValueError(f"Refusing to write outside Phase 6: {resolved}")
    return resolved


def resolve_repo_path(path: str | Path) -> Path:
    p = Path(path)
    if p.is_absolute():
        return p
    return ROOT / p


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_tensor_file(path: Path) -> dict[str, Any]:
    try:
        return torch.load(path, map_location="cpu", weights_only=True)
    except TypeError:
        return torch.load(path, map_location="cpu")


def merged_config(args: argparse.Namespace) -> dict[str, Any]:
    cfg = load_json(args.config)
    for key in ["max_steps", "batch_size", "eval_every", "save_every", "log_every", "sample_count"]:
        value = getattr(args, key.replace("-", "_"), None)
        if value is not None:
            cfg[key] = value
    if args.mle_checkpoint is not None:
        cfg["mle_checkpoint"] = str(args.mle_checkpoint)
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
    max_len: int,
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
        x = payload["input_ids"].long()[:, :max_len]
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


def move_optimizer_state_to_device(optimizer: torch.optim.Optimizer, device: torch.device) -> None:
    for state in optimizer.state.values():
        for key, value in list(state.items()):
            if torch.is_tensor(value):
                state[key] = value.to(device)


def set_optimizer_lr(optimizer: torch.optim.Optimizer, lr: float) -> None:
    for group in optimizer.param_groups:
        group["lr"] = lr


def load_mle_weights(generator: ConditionalGumbelGenerator, checkpoint_path: Path, device: torch.device) -> dict[str, Any]:
    checkpoint = load_tensor_file(checkpoint_path)
    source_state = checkpoint.get("model_state", checkpoint)
    target_state = generator.state_dict()
    matched = {
        key: value
        for key, value in source_state.items()
        if key in target_state and tuple(target_state[key].shape) == tuple(value.shape)
    }
    target_state.update(matched)
    generator.load_state_dict(target_state)
    generator.to(device)
    return {
        "checkpoint": str(checkpoint_path),
        "source_step": int(checkpoint.get("global_step", -1)) if isinstance(checkpoint, dict) else -1,
        "matched_keys": len(matched),
        "total_keys": len(target_state),
    }


def find_latest_checkpoint(checkpoint_dir: Path) -> Path | None:
    latest = checkpoint_dir / "latest.pt"
    if latest.exists():
        return latest
    candidates = sorted(checkpoint_dir.glob("step_*.pt"))
    return candidates[-1] if candidates else None


def tau_schedule(step: int, max_steps: int, start: float, end: float) -> float:
    ratio = min(max(step / max(max_steps, 1), 0.0), 1.0)
    return start + (end - start) * ratio


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
def sample_generator(
    generator: ConditionalGumbelGenerator,
    vocab: dict[str, Any],
    techniques: list[str],
    cfg: dict[str, Any],
    device: torch.device,
) -> list[dict[str, Any]]:
    generator.eval()
    tokens = vocab["tokens"]
    bos_id = int(vocab["bos_id"])
    eos_id = int(vocab["eos_id"])
    pad_id = int(vocab["pad_id"])
    technique_ids = [(idx, name) for idx, name in enumerate(techniques) if name != "unknown"]
    per_tech = max(int(cfg["sample_count"]) // max(len(technique_ids), 1), 1)
    results: list[dict[str, Any]] = []
    for tech_id, tech_name in technique_ids:
        cond = torch.tensor([tech_id], dtype=torch.long, device=device)
        for _ in range(per_tech):
            ids = [bos_id]
            hidden = None
            for _step in range(int(cfg["max_len"]) - 1):
                x = torch.tensor([[ids[-1]]], dtype=torch.long, device=device)
                emb = generator.embedding(x)
                cond_emb = generator.cond_embed(cond).unsqueeze(1)
                out, hidden = generator.lstm(torch.cat([emb, cond_emb], dim=-1), hidden)
                logits = generator.fc(out[:, -1, :])[0] / float(cfg["sample_temperature"])
                logits = top_k_top_p_filter(logits, int(cfg["sample_top_k"]), float(cfg["sample_top_p"]))
                probs = torch.softmax(logits, dim=-1)
                next_id = torch.multinomial(probs, 1).item()
                if next_id == eos_id:
                    break
                ids.append(next_id)
            text_tokens = [tokens[i] for i in ids if i not in (bos_id, eos_id, pad_id) and i < len(tokens)]
            results.append({"technique": tech_name, "text": " ".join(text_tokens)})
    generator.train()
    return results


def sample_metrics(samples: list[dict[str, Any]]) -> dict[str, Any]:
    texts = [sample["text"] for sample in samples]
    unique = set(texts)
    token_counter: Counter[str] = Counter()
    lengths: list[int] = []
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
def d_diagnostic(
    discriminator: ConditionalDiscriminator,
    generator: ConditionalGumbelGenerator,
    real_ids: torch.Tensor,
    cond: torch.Tensor,
    tau: float,
    bos_id: int,
) -> dict[str, Any]:
    discriminator.eval()
    generator.eval()
    real_seq = real_ids[:, 1:]
    real_emb = generator.embedding(real_seq)
    fake_soft = generator.generate_soft(cond, real_seq.size(1), tau, bos_id)
    fake_emb = fake_soft @ generator.embedding.weight
    softened_real = real_emb + torch.randn_like(real_emb) * 0.05
    d_real = torch.sigmoid(discriminator(real_emb, cond)).mean().item()
    d_fake = torch.sigmoid(discriminator(fake_emb, cond)).mean().item()
    d_softened = torch.sigmoid(discriminator(softened_real, cond)).mean().item()
    discriminator.train()
    generator.train()
    return {
        "d_real": d_real,
        "d_fake": d_fake,
        "d_softened_real": d_softened,
        "delta_real_softened": abs(d_real - d_softened),
        "shortcut_suspected": abs(d_real - d_softened) > 0.3,
    }


def real_embedding_from_ids(generator: ConditionalGumbelGenerator, ids: torch.Tensor, smoothing: float) -> torch.Tensor:
    if smoothing <= 0:
        return generator.embedding(ids)
    one_hot = F.one_hot(ids, num_classes=generator.vocab_size).to(dtype=generator.embedding.weight.dtype)
    soft = one_hot.mul(1.0 - smoothing).add(smoothing / generator.vocab_size)
    return soft @ generator.embedding.weight


def write_samples(path: Path, samples: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for sample in samples:
            handle.write(json.dumps(sample, ensure_ascii=False) + "\n")


def save_checkpoint(
    path: Path,
    generator: ConditionalGumbelGenerator,
    discriminator: ConditionalDiscriminator,
    opt_g: torch.optim.Optimizer,
    opt_d: torch.optim.Optimizer,
    scaler_g: Any,
    scaler_d: Any,
    cfg: dict[str, Any],
    step: int,
    best_unique_ratio: float,
    best_score: float,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "generator_state": generator.state_dict(),
            "discriminator_state": discriminator.state_dict(),
            "optimizer_g_state": opt_g.state_dict(),
            "optimizer_d_state": opt_d.state_dict(),
            "scaler_g_state": scaler_g.state_dict() if scaler_g is not None else None,
            "scaler_d_state": scaler_d.state_dict() if scaler_d is not None else None,
            "config": cfg,
            "global_step": step,
            "best_unique_ratio": best_unique_ratio,
            "best_score": best_score,
        },
        path,
    )


def write_report(
    path: Path,
    cfg: dict[str, Any],
    manifest: dict[str, Any],
    mle_load: dict[str, Any],
    history: list[dict[str, Any]],
    latest: dict[str, Any],
    checkpoint_dir: Path,
) -> None:
    metrics = latest.get("sample_metrics", {})
    diag = latest.get("d_diagnostic", {})
    lines = [
        "# 06 - Gumbel-SeqGAN Smoke Report",
        "",
        "**Scope:** small adversarial smoke run, not full GAN training.",
        f"**Train source:** `gold.parquet` token shards",
        f"**Train rows available:** `{manifest['splits']['train']['rows']:,}`",
        f"**MLE init checkpoint:** `{mle_load.get('checkpoint')}`",
        f"**MLE init source step:** `{mle_load.get('source_step')}`",
        f"**Loaded MLE keys:** `{mle_load.get('matched_keys')}` / `{mle_load.get('total_keys')}`",
        f"**Batch size:** `{cfg['batch_size']}`",
        f"**Max len:** `{cfg['max_len']}`",
        f"**Max steps:** `{cfg['max_steps']}`",
        f"**Mixed precision:** `{cfg['mixed_precision']}`",
        "",
        "## Latest Metrics",
        "",
        f"- Step: `{latest.get('step', 0)}`",
        f"- Loss D: `{latest.get('loss_d', 'n/a')}`",
        f"- Loss G: `{latest.get('loss_g', 'n/a')}`",
        f"- Loss adversarial: `{latest.get('loss_adv', 'n/a')}`",
        f"- Loss MLE anchor: `{latest.get('loss_mle', 'n/a')}`",
        f"- Tau: `{latest.get('tau', 'n/a')}`",
        f"- Unique ratio: `{metrics.get('unique_ratio', 'n/a')}`",
        f"- Syntax validity rate: `{metrics.get('syntax_validity_rate', 'n/a')}`",
        f"- Empty sample count: `{metrics.get('empty_count', 'n/a')}`",
        f"- D real/fake: `{diag.get('d_real', 'n/a')}` / `{diag.get('d_fake', 'n/a')}`",
        f"- D shortcut suspected: `{diag.get('shortcut_suspected', 'n/a')}`",
        "",
        "## Gate",
        "",
        f"- Latest checkpoint: `{checkpoint_dir / 'latest.pt'}`",
        f"- Best checkpoint: `{checkpoint_dir / 'best.pt'}`",
        "- Continue only if there is no OOM, no non-finite loss, no severe unique-ratio collapse, and D shortcut is not suspected.",
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


def format_eta(step: int, max_steps: int, started: float) -> str:
    elapsed = max(time.time() - started, 1e-6)
    rate = step / elapsed
    if rate <= 0:
        return "unknown"
    remaining = max(max_steps - step, 0) / rate
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
    techniques = load_json(args.cache_dir / "techniques.json")["techniques"]
    vocab_size = len(vocab["tokens"])
    pad_id = int(vocab["pad_id"])
    bos_id = int(vocab["bos_id"])
    cfg["max_len"] = min(int(cfg["max_len"]), int(manifest["max_len"]))

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if bool(cfg.get("require_cuda", False)) and device.type != "cuda" and not args.allow_cpu:
        raise RuntimeError("CUDA is required for Gumbel-SeqGAN smoke, but PyTorch does not see CUDA.")
    amp_enabled = bool(cfg["mixed_precision"]) and device.type == "cuda"
    cfg["mixed_precision"] = amp_enabled

    generator = ConditionalGumbelGenerator(
        vocab_size,
        len(techniques),
        int(cfg["embed_dim"]),
        int(cfg["hidden_dim"]),
    ).to(device)
    discriminator = ConditionalDiscriminator(
        int(cfg["embed_dim"]),
        int(cfg["discriminator_hidden_dim"]),
        len(techniques),
    ).to(device)

    opt_g = torch.optim.Adam(generator.parameters(), lr=float(cfg["g_lr"]))
    opt_d = torch.optim.Adam(discriminator.parameters(), lr=float(cfg["d_lr"]))
    scaler_g = make_grad_scaler(amp_enabled)
    scaler_d = make_grad_scaler(amp_enabled)
    criterion = nn.CrossEntropyLoss(ignore_index=pad_id)

    mle_checkpoint = resolve_repo_path(cfg["mle_checkpoint"])
    mle_load = load_mle_weights(generator, mle_checkpoint, device)
    step = 0
    best_unique_ratio = 0.0
    best_score = -float("inf")

    resume_path = args.resume
    if args.resume_latest and resume_path is None:
        resume_path = find_latest_checkpoint(args.checkpoint_dir)
    if resume_path:
        checkpoint = load_tensor_file(resume_path)
        generator.load_state_dict(checkpoint["generator_state"])
        discriminator.load_state_dict(checkpoint["discriminator_state"])
        opt_g.load_state_dict(checkpoint["optimizer_g_state"])
        opt_d.load_state_dict(checkpoint["optimizer_d_state"])
        move_optimizer_state_to_device(opt_g, device)
        move_optimizer_state_to_device(opt_d, device)
        set_optimizer_lr(opt_g, float(cfg["g_lr"]))
        set_optimizer_lr(opt_d, float(cfg["d_lr"]))
        if checkpoint.get("scaler_g_state"):
            scaler_g.load_state_dict(checkpoint["scaler_g_state"])
        if checkpoint.get("scaler_d_state"):
            scaler_d.load_state_dict(checkpoint["scaler_d_state"])
        step = int(checkpoint.get("global_step", 0))
        best_unique_ratio = float(checkpoint.get("best_unique_ratio", 0.0))
        best_score = float(checkpoint.get("best_score", best_score))
        print(f"Resumed GAN checkpoint: {resume_path} step={step}")

    train_paths = shard_paths(args.cache_dir, "train")
    data_iter = iter_shard_batches(train_paths, int(cfg["batch_size"]), int(cfg["max_len"]), True, int(cfg["seed"]), 0)
    progress_file = args.log_dir / "phase06_gumbel_seqgan_progress.json"
    history_file = args.output_dir / "history.jsonl"
    history: list[dict[str, Any]] = []
    latest_event: dict[str, Any] = {}
    started = time.time()

    print("Phase 06 - Gumbel-SeqGAN Smoke")
    print(f"device={device_summary(device)}")
    print(f"cache_dir={args.cache_dir}")
    print(f"checkpoint_dir={args.checkpoint_dir}")
    print(f"mle_init={mle_load}")
    print(
        "config batch_size={} max_len={} max_steps={} d_steps={} tau={}->{} amp={}".format(
            cfg["batch_size"],
            cfg["max_len"],
            cfg["max_steps"],
            cfg["d_steps"],
            cfg["tau_start"],
            cfg["tau_end"],
            amp_enabled,
        )
    )

    while step < int(cfg["max_steps"]):
        generator.train()
        discriminator.train()
        tau = tau_schedule(step, int(cfg["max_steps"]), float(cfg["tau_start"]), float(cfg["tau_end"]))
        loss_d_value = 0.0

        for _ in range(int(cfg["d_steps"])):
            try:
                real_cpu, cond_cpu = next(data_iter)
            except StopIteration:
                data_iter = iter_shard_batches(train_paths, int(cfg["batch_size"]), int(cfg["max_len"]), True, int(cfg["seed"]), step)
                real_cpu, cond_cpu = next(data_iter)
            real_ids = real_cpu.to(device, non_blocking=True)
            cond = cond_cpu.to(device, non_blocking=True)
            real_seq = real_ids[:, 1:]

            with autocast_context(device, amp_enabled):
                with torch.no_grad():
                    fake_soft = generator.generate_soft(cond, real_seq.size(1), tau, bos_id)
                    fake_emb = fake_soft @ generator.embedding.weight
                    real_emb = real_embedding_from_ids(generator, real_seq, float(cfg.get("real_soft_smoothing", 0.0)))
                    noise_std = float(cfg.get("d_input_noise_std", 0.0))
                    if noise_std > 0:
                        real_emb = real_emb + torch.randn_like(real_emb) * noise_std
                        fake_emb = fake_emb + torch.randn_like(fake_emb) * noise_std
                d_real = discriminator(real_emb.detach(), cond)
                d_fake = discriminator(fake_emb.detach(), cond)
                real_label = torch.full_like(d_real, float(cfg.get("d_real_label", 1.0)))
                fake_label = torch.full_like(d_fake, float(cfg.get("d_fake_label", 0.0)))
                loss_d = F.binary_cross_entropy_with_logits(d_real, real_label) + F.binary_cross_entropy_with_logits(d_fake, fake_label)
            if not torch.isfinite(loss_d):
                raise RuntimeError(f"Non-finite D loss: {float(loss_d.detach().cpu())}")
            opt_d.zero_grad(set_to_none=True)
            scaler_d.scale(loss_d).backward()
            scaler_d.unscale_(opt_d)
            nn.utils.clip_grad_norm_(discriminator.parameters(), float(cfg["clip_grad"]))
            scaler_d.step(opt_d)
            scaler_d.update()
            loss_d_value = float(loss_d.detach().cpu())

        try:
            real_cpu, cond_cpu = next(data_iter)
        except StopIteration:
            data_iter = iter_shard_batches(train_paths, int(cfg["batch_size"]), int(cfg["max_len"]), True, int(cfg["seed"]), step)
            real_cpu, cond_cpu = next(data_iter)
        real_ids = real_cpu.to(device, non_blocking=True)
        cond = cond_cpu.to(device, non_blocking=True)
        real_seq = real_ids[:, 1:]

        with autocast_context(device, amp_enabled):
            fake_soft = generator.generate_soft(cond, real_seq.size(1), tau, bos_id)
            fake_emb = fake_soft @ generator.embedding.weight
            d_fake_for_g = discriminator(fake_emb, cond)
            loss_adv = F.binary_cross_entropy_with_logits(d_fake_for_g, torch.ones_like(d_fake_for_g))
            logits = generator.forward_logits(real_ids[:, :-1], cond)
            loss_mle = criterion(logits.reshape(-1, vocab_size), real_ids[:, 1:].reshape(-1))
            loss_g = float(cfg["adv_weight"]) * loss_adv + float(cfg["mle_weight"]) * loss_mle
        if not torch.isfinite(loss_g):
            raise RuntimeError(f"Non-finite G loss: {float(loss_g.detach().cpu())}")
        opt_g.zero_grad(set_to_none=True)
        scaler_g.scale(loss_g).backward()
        scaler_g.unscale_(opt_g)
        nn.utils.clip_grad_norm_(generator.parameters(), float(cfg["clip_grad"]))
        scaler_g.step(opt_g)
        scaler_g.update()

        step += 1
        should_log = step % int(cfg["log_every"]) == 0
        should_eval = step % int(cfg["eval_every"]) == 0 or step == int(cfg["max_steps"])
        should_save = step % int(cfg["save_every"]) == 0 or should_eval

        if should_log:
            eta = format_eta(step, int(cfg["max_steps"]), started)
            print(
                "step={}/{} loss_d={:.5f} loss_g={:.5f} adv={:.5f} mle={:.5f} tau={:.3f} eta={}".format(
                    step,
                    cfg["max_steps"],
                    loss_d_value,
                    float(loss_g.detach().cpu()),
                    float(loss_adv.detach().cpu()),
                    float(loss_mle.detach().cpu()),
                    tau,
                    eta,
                ),
                flush=True,
            )
            save_json(
                progress_file,
                {
                    "stage": "training",
                    "step": step,
                    "max_steps": cfg["max_steps"],
                    "loss_d": loss_d_value,
                    "loss_g": float(loss_g.detach().cpu()),
                    "loss_adv": float(loss_adv.detach().cpu()),
                    "loss_mle": float(loss_mle.detach().cpu()),
                    "tau": tau,
                    "eta": eta,
                    "device": device_summary(device),
                },
            )

        if should_eval:
            samples = sample_generator(generator, vocab, techniques, cfg, device)
            metrics = sample_metrics(samples)
            diag = d_diagnostic(discriminator, generator, real_ids[: min(16, real_ids.size(0))], cond[: min(16, cond.size(0))], tau, bos_id)
            sample_path = args.output_dir / f"samples_step_{step:08d}.jsonl"
            write_samples(sample_path, samples)
            score = metrics["unique_ratio"] + metrics["syntax_validity_rate"] - metrics["empty_count"] * 0.01
            latest_event = {
                "step": step,
                "loss_d": loss_d_value,
                "loss_g": float(loss_g.detach().cpu()),
                "loss_adv": float(loss_adv.detach().cpu()),
                "loss_mle": float(loss_mle.detach().cpu()),
                "tau": tau,
                "sample_metrics": metrics,
                "d_diagnostic": diag,
                "sample_path": str(sample_path),
                "elapsed_sec": time.time() - started,
                "device": device_summary(device),
            }
            history.append(latest_event)
            with history_file.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(latest_event, ensure_ascii=False) + "\n")
            print(
                "eval step={} unique_ratio={:.4f} syntax={:.4f} empty={} d_real={:.3f} d_fake={:.3f}".format(
                    step,
                    metrics["unique_ratio"],
                    metrics["syntax_validity_rate"],
                    metrics["empty_count"],
                    diag["d_real"],
                    diag["d_fake"],
                ),
                flush=True,
            )
            if metrics["unique_ratio"] < float(cfg["collapse_unique_ratio"]):
                latest_event["collapse_detected"] = True
                save_json(progress_file, {"stage": "collapse_detected", **latest_event})
                break
            if score > best_score:
                best_score = score
                best_unique_ratio = metrics["unique_ratio"]
                save_checkpoint(args.checkpoint_dir / "best.pt", generator, discriminator, opt_g, opt_d, scaler_g, scaler_d, cfg, step, best_unique_ratio, best_score)
            write_report(args.report_dir / "06_gumbel_seqgan_smoke_report.md", cfg, manifest, mle_load, history, latest_event, args.checkpoint_dir)

        if should_save:
            payload_path = args.checkpoint_dir / "latest.pt"
            save_checkpoint(payload_path, generator, discriminator, opt_g, opt_d, scaler_g, scaler_d, cfg, step, best_unique_ratio, best_score)
            if step % int(cfg["save_every"]) == 0:
                save_checkpoint(args.checkpoint_dir / f"step_{step:08d}.pt", generator, discriminator, opt_g, opt_d, scaler_g, scaler_d, cfg, step, best_unique_ratio, best_score)

    save_json(
        progress_file,
        {
            "stage": "done",
            "step": step,
            "best_unique_ratio": best_unique_ratio,
            "best_score": best_score,
            "elapsed_sec": time.time() - started,
            "device": device_summary(device),
        },
    )
    if latest_event:
        write_report(args.report_dir / "06_gumbel_seqgan_smoke_report.md", cfg, manifest, mle_load, history, latest_event, args.checkpoint_dir)
    print("Phase 06 Gumbel-SeqGAN smoke complete")
    print(f"step={step} best_unique_ratio={best_unique_ratio:.4f} best_score={best_score:.4f}")
    print(f"latest_checkpoint={args.checkpoint_dir / 'latest.pt'}")
    print(f"report={args.report_dir / '06_gumbel_seqgan_smoke_report.md'}")


if __name__ == "__main__":
    main()
