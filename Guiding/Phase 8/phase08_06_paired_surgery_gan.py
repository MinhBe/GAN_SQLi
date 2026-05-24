# -*- coding: utf-8 -*-
"""
Phase 08 - Script 6: H5' paired masked surgery GAN pilot.

This is the adversarial continuation of phase08_05_surgery_baselines.py. It is
not a revival of full-sequence Gumbel/SeqGAN. The generator only edits masked
placeholder slots inside an existing delex template, while a paired
discriminator compares real and generated fills under the same frame/condition.

RTX 3050 6GB defaults:
- compact Conv generator/discriminator
- mixed precision on CUDA
- batch 64, max_len 96
- small adversarial weight and D freeze when D saturates
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
import torch.nn.functional as F


if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


PHASE_DIR = Path(__file__).resolve().parent
DEFAULT_SPLIT_DIR = PHASE_DIR / "outputs" / "delex_cluster_split_smoke"
DEFAULT_ANCHOR = PHASE_DIR / "checkpoints" / "surgery_baselines_smoke" / "anchor_only_latest.pt"
DEFAULT_OUT_DIR = PHASE_DIR / "outputs" / "paired_surgery_gan_smoke"
DEFAULT_CHECKPOINT_DIR = PHASE_DIR / "checkpoints" / "paired_surgery_gan_smoke"
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"
DEFAULT_LOG_DIR = PHASE_DIR / "logs"

SPACE_RE = re.compile(r"\s+")
TOKEN_RE = re.compile(r"__[A-Z0-9_]+__|@@|--|#|/\*|\*/|<=|>=|<>|!=|\|\||&&|[A-Za-z_][A-Za-z0-9_]*|\d+|[^\s]")
PLACEHOLDER_RE = re.compile(r"^__[a-z0-9_]+__$", re.IGNORECASE)
TECHNIQUES = ["benign", "boolean_blind", "error_based", "time_blind", "union_based", "unknown"]
OPERATOR_TOKENS = {"=", "<", ">", "<=", ">=", "<>", "!=", "like", "in", "is"}
COMMENT_TOKENS = {"--", "#", "/*", "*/", "__comment__"}
BOOLEAN_TOKENS = {"and", "or", "not", "||", "&&"}
LOCAL_SURGERY_TOKENS = OPERATOR_TOKENS | COMMENT_TOKENS | BOOLEAN_TOKENS | {"all"}
AGGRESSIVE_SURGERY_TOKENS = LOCAL_SURGERY_TOKENS | {
    "union",
    "select",
    "sleep",
    "pg_sleep",
    "benchmark",
    "waitfor",
    "delay",
    "extractvalue",
    "updatexml",
    "cast",
    "convert",
}


class SurgeryGenerator(nn.Module):
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


class PairedDiscriminator(nn.Module):
    def __init__(self, vocab_size: int, n_techniques: int, embed_dim: int, hidden_dim: int, pad_id: int, max_len: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=pad_id)
        self.cond_embedding = nn.Embedding(n_techniques, embed_dim)
        self.pos_embedding = nn.Embedding(max_len, embed_dim)
        self.encoder = nn.Sequential(
            nn.Conv1d(embed_dim * 4, hidden_dim, kernel_size=3, padding=1),
            nn.LeakyReLU(0.2),
            nn.Conv1d(hidden_dim, hidden_dim, kernel_size=3, padding=1),
            nn.LeakyReLU(0.2),
        )
        self.head = nn.Sequential(
            nn.Linear(hidden_dim * 2, hidden_dim),
            nn.LeakyReLU(0.2),
            nn.Linear(hidden_dim, 1),
        )

    def score_emb(self, frame_ids: torch.Tensor, filled_emb: torch.Tensor, cond_ids: torch.Tensor, valid_mask: torch.Tensor) -> torch.Tensor:
        frame = self.embedding(frame_ids)
        pos_ids = torch.arange(frame_ids.size(1), device=frame_ids.device).unsqueeze(0).expand_as(frame_ids)
        pos = self.pos_embedding(pos_ids)
        cond = self.cond_embedding(cond_ids).unsqueeze(1).expand(-1, frame_ids.size(1), -1)
        encoded = self.encoder(torch.cat([frame, filled_emb, cond, pos], dim=-1).transpose(1, 2)).transpose(1, 2)
        mask = valid_mask.unsqueeze(-1).to(encoded.dtype)
        masked = encoded * mask
        mean_pool = masked.sum(dim=1) / mask.sum(dim=1).clamp_min(1.0)
        max_pool = masked.masked_fill(mask.eq(0), -1e4).max(dim=1).values
        return self.head(torch.cat([mean_pool, max_pool], dim=-1)).squeeze(-1)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run H5' paired masked surgery GAN pilot.")
    parser.add_argument("--split-dir", type=Path, default=DEFAULT_SPLIT_DIR)
    parser.add_argument("--anchor-checkpoint", type=Path, default=DEFAULT_ANCHOR)
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
    parser.add_argument("--d-hidden-dim", type=int, default=128)
    parser.add_argument("--batch-size", type=int, default=64)
    parser.add_argument("--max-steps", type=int, default=300)
    parser.add_argument("--d-steps", type=int, default=1)
    parser.add_argument("--eval-every", type=int, default=50)
    parser.add_argument("--log-every", type=int, default=25)
    parser.add_argument("--g-lr", type=float, default=5e-4)
    parser.add_argument("--d-lr", type=float, default=5e-4)
    parser.add_argument("--mask-prob", type=float, default=0.8)
    parser.add_argument("--slot-mode", choices=["placeholder", "local", "aggressive", "constrained"], default="placeholder")
    parser.add_argument("--adv-weight", type=float, default=0.05)
    parser.add_argument("--anchor-weight", type=float, default=1.0)
    parser.add_argument("--entropy-weight", type=float, default=0.002)
    parser.add_argument("--sample-temperature", type=float, default=1.0)
    parser.add_argument("--sample-top-k", type=int, default=8)
    parser.add_argument("--sample-argmax", action="store_true")
    parser.add_argument("--d-freeze-acc", type=float, default=0.85)
    parser.add_argument("--collapse-unique-ratio", type=float, default=0.10)
    parser.add_argument("--seed", type=int, default=260522)
    parser.add_argument("--no-mixed-precision", action="store_true")
    parser.add_argument("--allow-cpu", action="store_true")
    parser.add_argument("--report-name", default="08_paired_surgery_gan_smoke_report.md")
    parser.add_argument("--json-name", default="08_paired_surgery_gan_smoke_report.json")
    return parser.parse_args()


def ensure_under_phase(path: Path) -> Path:
    resolved = path.resolve()
    phase = PHASE_DIR.resolve()
    if resolved != phase and phase not in resolved.parents:
        raise ValueError(f"Refusing to write outside Phase 8: {resolved}")
    return resolved


def load_tensor_file(path: Path) -> dict[str, Any]:
    try:
        return torch.load(path, map_location="cpu", weights_only=True)
    except TypeError:
        return torch.load(path, map_location="cpu")
    except Exception:
        return torch.load(path, map_location="cpu", weights_only=False)


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
    return df[df[text_col].str.len() > 0].copy()


def build_vocab(texts: list[str], max_vocab: int) -> dict[str, Any]:
    counter: Counter[str] = Counter()
    for text in texts:
        counter.update(tokenize(text))
    special = ["<PAD>", "<UNK>", "<MASK>"]
    common = [tok for tok, _ in counter.most_common(max(max_vocab - len(special), 1)) if tok not in special]
    tokens = special + common
    token_to_id = {tok: idx for idx, tok in enumerate(tokens)}
    return {"tokens": tokens, "token_to_id": token_to_id, "pad_id": 0, "unk_id": 1, "mask_id": 2}


def technique_id(name: str) -> int:
    return TECHNIQUES.index(name) if name in TECHNIQUES else TECHNIQUES.index("unknown")


def is_surgery_slot(token: str, mode: str) -> bool:
    if PLACEHOLDER_RE.match(token) is not None:
        return True
    if mode == "placeholder":
        return False
    if mode == "local":
        return token in LOCAL_SURGERY_TOKENS
    if mode == "aggressive":
        return token in AGGRESSIVE_SURGERY_TOKENS
    if mode == "constrained":
        return token in AGGRESSIVE_SURGERY_TOKENS
    raise ValueError(f"unknown slot mode: {mode}")


def is_contextual_surgery_slot(tokens: list[str], index: int, mode: str) -> bool:
    token = tokens[index]
    if mode != "constrained":
        return is_surgery_slot(token, mode)
    if PLACEHOLDER_RE.match(token) is not None:
        return True

    prev_tok = tokens[index - 1] if index > 0 else ""
    next_tok = tokens[index + 1] if index + 1 < len(tokens) else ""
    has_left = bool(prev_tok) and prev_tok not in {"(", ",", ";", "--", "#", "/*"}
    has_right = bool(next_tok) and next_tok not in {")", ",", ";", "--", "#", "*/"}

    if token in OPERATOR_TOKENS:
        return has_left and has_right
    if token in COMMENT_TOKENS:
        return True
    if token in BOOLEAN_TOKENS:
        return has_left and has_right
    if token == "all":
        return prev_tok == "union" or next_tok == "select"
    if token in {"union", "select"}:
        return "union" in {prev_tok, token, next_tok} or "select" in {prev_tok, token, next_tok}
    if token in {"sleep", "pg_sleep", "benchmark", "waitfor", "delay"}:
        return next_tok in {"(", "__time__", "__num__"} or prev_tok in {"(", "waitfor"}
    if token in {"extractvalue", "updatexml", "cast", "convert"}:
        return next_tok == "(" or prev_tok in {"(", ","}
    return False


def constrained_allowed_tokens(original_token: str) -> set[str]:
    token = original_token.lower()
    if PLACEHOLDER_RE.match(token) is not None:
        if token == "__comment__":
            return {token, "--", "#", "/*", "*/"}
        if token == "__time__":
            return {token, "__num__", "1", "3", "5"}
        return {token}
    if token in OPERATOR_TOKENS:
        return set(OPERATOR_TOKENS)
    if token in COMMENT_TOKENS:
        return set(COMMENT_TOKENS)
    if token in BOOLEAN_TOKENS:
        return {"and", "or", "not", "||", "&&"}
    if token in {"union", "select", "all"}:
        return {"union", "select", "all"}
    if token in {"sleep", "pg_sleep", "benchmark", "waitfor", "delay"}:
        return {"sleep", "pg_sleep", "benchmark", "waitfor", "delay"}
    if token in {"extractvalue", "updatexml", "cast", "convert"}:
        return {"extractvalue", "updatexml", "cast", "convert"}
    return {token}


def build_constrained_allowed_mask(vocab: dict[str, Any]) -> torch.Tensor:
    token_to_id = vocab["token_to_id"]
    vocab_size = len(vocab["tokens"])
    allowed_mask = torch.zeros((vocab_size, vocab_size), dtype=torch.bool)
    for token, token_id in token_to_id.items():
        allowed = [token_to_id[tok] for tok in sorted(constrained_allowed_tokens(token)) if tok in token_to_id]
        if token_id not in allowed:
            allowed.append(token_id)
        allowed_mask[token_id, sorted(set(allowed))] = True
    return allowed_mask


def apply_constrained_logits(
    logits: torch.Tensor,
    original_ids: torch.Tensor,
    slot_mask: torch.Tensor,
    allowed_mask_by_token: torch.Tensor | None,
) -> torch.Tensor:
    if allowed_mask_by_token is None:
        return logits
    allowed = allowed_mask_by_token.to(logits.device).index_select(0, original_ids.reshape(-1)).reshape(*original_ids.shape, -1)
    blocked = slot_mask.unsqueeze(-1) & ~allowed
    return logits.masked_fill(blocked, -1e4)


def encode_text(text: str, vocab: dict[str, Any], max_len: int, slot_mode: str) -> tuple[list[int], list[int], list[int]]:
    toks = tokenize(text)[:max_len]
    ids = [vocab["token_to_id"].get(tok, vocab["unk_id"]) for tok in toks]
    slot_mask = [int(is_contextual_surgery_slot(toks, idx, slot_mode)) for idx, _tok in enumerate(toks)]
    valid_mask = [1] * len(ids)
    pad = max_len - len(ids)
    if pad > 0:
        ids.extend([vocab["pad_id"]] * pad)
        slot_mask.extend([0] * pad)
        valid_mask.extend([0] * pad)
    return ids, slot_mask, valid_mask


def build_tensors(df: pd.DataFrame, args: argparse.Namespace, vocab: dict[str, Any]) -> dict[str, torch.Tensor]:
    encoded = [encode_text(text, vocab, args.max_len, args.slot_mode) for text in df[args.text_col].tolist()]
    ids = torch.tensor([row[0] for row in encoded], dtype=torch.long)
    slot_mask = torch.tensor([row[1] for row in encoded], dtype=torch.bool)
    valid_mask = torch.tensor([row[2] for row in encoded], dtype=torch.bool)
    cond = torch.tensor([technique_id(name) for name in df[args.technique_col].tolist()], dtype=torch.long)
    return {"ids": ids, "slot_mask": slot_mask, "valid_mask": valid_mask, "cond": cond}


def iter_batches(tensors: dict[str, torch.Tensor], batch_size: int, seed: int, step: int):
    n_rows = tensors["ids"].size(0)
    generator = torch.Generator()
    generator.manual_seed(seed + step * 1000003)
    order = torch.randperm(n_rows, generator=generator)
    for start in range(0, n_rows, batch_size):
        idx = order[start : start + batch_size]
        yield (
            tensors["ids"].index_select(0, idx),
            tensors["slot_mask"].index_select(0, idx),
            tensors["valid_mask"].index_select(0, idx),
            tensors["cond"].index_select(0, idx),
        )


def corrupt_batch(ids: torch.Tensor, slot_mask: torch.Tensor, mask_id: int, mask_prob: float) -> torch.Tensor:
    corrupted = ids.clone()
    random_mask = torch.rand_like(ids, dtype=torch.float32) < mask_prob
    corrupted[slot_mask & random_mask] = mask_id
    return corrupted


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


def save_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def load_anchor_if_compatible(generator: SurgeryGenerator, anchor_path: Path, device: torch.device) -> dict[str, Any]:
    if not anchor_path.exists():
        return {"loaded": False, "reason": "missing_anchor", "path": str(anchor_path)}
    checkpoint = load_tensor_file(anchor_path)
    source = checkpoint.get("model_state", {})
    target = generator.state_dict()
    matched = {k: v for k, v in source.items() if k in target and tuple(target[k].shape) == tuple(v.shape)}
    target.update(matched)
    generator.load_state_dict(target)
    generator.to(device)
    return {"loaded": True, "path": str(anchor_path), "matched_keys": len(matched), "total_keys": len(target)}


def real_embedding_from_ids(generator: SurgeryGenerator, ids: torch.Tensor) -> torch.Tensor:
    return generator.embedding(ids)


def fake_embedding_from_logits(generator: SurgeryGenerator, ids: torch.Tensor, logits: torch.Tensor, slot_mask: torch.Tensor) -> torch.Tensor:
    real_emb = generator.embedding(ids)
    probs = torch.softmax(logits, dim=-1)
    fake_slot_emb = probs @ generator.embedding.weight
    return torch.where(slot_mask.unsqueeze(-1), fake_slot_emb, real_emb)


def entropy_on_slots(logits: torch.Tensor, slot_mask: torch.Tensor) -> torch.Tensor:
    probs = torch.softmax(logits, dim=-1)
    log_probs = torch.log_softmax(logits, dim=-1)
    ent = -(probs * log_probs).sum(dim=-1)
    return ent.masked_select(slot_mask).mean() if slot_mask.any() else logits.new_tensor(0.0)


def d_accuracy(real_logits: torch.Tensor, fake_logits: torch.Tensor) -> float:
    real_ok = (torch.sigmoid(real_logits) >= 0.5).float().mean()
    fake_ok = (torch.sigmoid(fake_logits) < 0.5).float().mean()
    return float(((real_ok + fake_ok) * 0.5).detach().cpu())


@torch.no_grad()
def evaluate_anchor(
    generator: SurgeryGenerator,
    tensors: dict[str, torch.Tensor],
    args: argparse.Namespace,
    vocab: dict[str, Any],
    device: torch.device,
    amp_enabled: bool,
    max_batches: int = 20,
) -> dict[str, float]:
    generator.eval()
    criterion = nn.CrossEntropyLoss(ignore_index=vocab["pad_id"], reduction="sum")
    total_loss = 0.0
    total_slots = 0
    correct_slots = 0
    batches = 0
    for ids_cpu, slot_cpu, _valid_cpu, cond_cpu in iter_batches(tensors, args.batch_size, args.seed, 0):
        slot_count = int(slot_cpu.sum().item())
        if slot_count == 0:
            continue
        ids = ids_cpu.to(device)
        slot_mask = slot_cpu.to(device)
        cond = cond_cpu.to(device)
        corrupted = corrupt_batch(ids, slot_mask, vocab["mask_id"], 1.0)
        with autocast_context(device, amp_enabled):
            logits = generator(corrupted, cond)
            targets = ids.masked_fill(~slot_mask, vocab["pad_id"])
            loss = criterion(logits.reshape(-1, logits.size(-1)), targets.reshape(-1))
        preds = logits.argmax(dim=-1)
        correct_slots += int(((preds == ids) & slot_mask).sum().detach().cpu())
        total_slots += slot_count
        total_loss += float(loss.detach().cpu())
        batches += 1
        if batches >= max_batches:
            break
    generator.train()
    return {"slot_loss": total_loss / max(total_slots, 1), "slot_accuracy": correct_slots / max(total_slots, 1), "slots": float(total_slots)}


def decode(ids: list[int], vocab: dict[str, Any]) -> str:
    tokens = vocab["tokens"]
    out = [tokens[idx] if 0 <= idx < len(tokens) else "<UNK>" for idx in ids if idx != vocab["pad_id"]]
    return normalize_space(" ".join(out))


@torch.no_grad()
def generate_samples(
    generator: SurgeryGenerator,
    df: pd.DataFrame,
    args: argparse.Namespace,
    vocab: dict[str, Any],
    device: torch.device,
    amp_enabled: bool,
    allowed_mask_by_token: torch.Tensor | None = None,
) -> list[dict[str, Any]]:
    generator.eval()
    rows = df.head(args.sample_count).copy()
    tensors = build_tensors(rows, args, vocab)
    ids = tensors["ids"].to(device)
    slot_mask = tensors["slot_mask"].to(device)
    cond = tensors["cond"].to(device)
    corrupted = corrupt_batch(ids, slot_mask, vocab["mask_id"], 1.0)
    with autocast_context(device, amp_enabled):
        logits = generator(corrupted, cond)
        logits = apply_constrained_logits(logits, ids, slot_mask, allowed_mask_by_token)
    if args.sample_argmax:
        preds = logits.argmax(dim=-1)
    else:
        slot_logits = logits / max(float(args.sample_temperature), 1e-6)
        if args.sample_top_k > 0:
            kth = torch.topk(slot_logits, min(args.sample_top_k, slot_logits.size(-1)), dim=-1).values[..., -1, None]
            slot_logits = slot_logits.masked_fill(slot_logits < kth, float("-inf"))
        probs = torch.softmax(slot_logits, dim=-1)
        preds = torch.multinomial(probs.reshape(-1, probs.size(-1)), 1).reshape(probs.shape[:2])
    filled = ids.clone()
    filled[slot_mask] = preds[slot_mask]
    samples: list[dict[str, Any]] = []
    for idx, (_, row) in enumerate(rows.iterrows()):
        samples.append({"sample_id": f"h5_paired_{idx}", "technique": as_text(row[args.technique_col]) or "unknown", "text": decode(filled[idx].detach().cpu().tolist(), vocab)})
    generator.train()
    return samples


def sample_summary(samples: list[dict[str, Any]]) -> dict[str, Any]:
    texts = [sample["text"] for sample in samples]
    lengths = [len(tokenize(text)) for text in texts]
    return {"samples": len(samples), "unique_ratio": len(set(texts)) / len(texts) if texts else 0.0, "avg_tokens": float(np.mean(lengths)) if lengths else 0.0, "empty_count": sum(1 for text in texts if not text.strip())}


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row, ensure_ascii=False) + "\n")


def write_report(path: Path, result: dict[str, Any]) -> None:
    latest = result["latest"]
    lines = [
        "# 08 - H5' Paired Surgery GAN Pilot Report",
        "",
        "Scope: adversarial slot-surgery pilot, not full-sequence GAN.",
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
        f"- Slot mode: `{result['config']['slot_mode']}`",
        f"- Embed/hidden/D-hidden: `{result['config']['embed_dim']}` / `{result['config']['hidden_dim']}` / `{result['config']['d_hidden_dim']}`",
        f"- Mixed precision: `{result['config']['mixed_precision']}`",
        f"- Anchor init: `{result['anchor_load']}`",
        "",
        "## Latest Metrics",
        "",
        f"- Step: `{latest['step']}`",
        f"- Loss D: `{latest['loss_d']:.6f}`",
        f"- Loss G: `{latest['loss_g']:.6f}`",
        f"- Loss anchor: `{latest['loss_anchor']:.6f}`",
        f"- Loss adversarial: `{latest['loss_adv']:.6f}`",
        f"- Slot entropy: `{latest['slot_entropy']:.6f}`",
        f"- D accuracy: `{latest['d_acc']:.4f}`",
        f"- D frozen on latest step: `{latest['d_frozen']}`",
        f"- Dev slot loss: `{latest['dev']['slot_loss']:.6f}`",
        f"- Dev slot accuracy: `{latest['dev']['slot_accuracy']:.4f}`",
        f"- Sample unique ratio: `{result['sample_summary']['unique_ratio']:.4f}`",
        f"- Samples: `{result['samples_path']}`",
        "",
        "## Gate",
        "",
        "- Compare this report against anchor-only and mutation-engine under `phase08_03_evaluator_contract.py`.",
        "- Continue H5' only if adversarial training improves validity/novelty/evasion over anchor-only, not merely over full-sequence Gumbel.",
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

    train_df = read_split(args.split_dir / "train.parquet", args.text_col, args.technique_col, args.train_limit)
    dev_df = read_split(args.split_dir / "dev.parquet", args.text_col, args.technique_col, args.dev_limit)
    vocab = build_vocab(train_df[args.text_col].tolist(), args.max_vocab)
    allowed_mask_by_token = build_constrained_allowed_mask(vocab) if args.slot_mode == "constrained" else None
    train_tensors = build_tensors(train_df, args, vocab)
    dev_tensors = build_tensors(dev_df, args, vocab)
    train_slots = int(train_tensors["slot_mask"].sum().item())
    if train_slots == 0:
        raise RuntimeError("No placeholder slots found in train split.")

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    if device.type != "cuda" and not args.allow_cpu:
        raise RuntimeError("CUDA not visible. Use --allow-cpu for debug only.")
    amp_enabled = (not args.no_mixed_precision) and device.type == "cuda"

    generator = SurgeryGenerator(len(vocab["tokens"]), len(TECHNIQUES), args.embed_dim, args.hidden_dim, vocab["pad_id"], args.max_len).to(device)
    discriminator = PairedDiscriminator(len(vocab["tokens"]), len(TECHNIQUES), args.embed_dim, args.d_hidden_dim, vocab["pad_id"], args.max_len).to(device)
    anchor_load = load_anchor_if_compatible(generator, args.anchor_checkpoint, device)

    opt_g = torch.optim.AdamW(generator.parameters(), lr=args.g_lr)
    opt_d = torch.optim.AdamW(discriminator.parameters(), lr=args.d_lr)
    scaler_g = make_grad_scaler(amp_enabled)
    scaler_d = make_grad_scaler(amp_enabled)
    ce_sum = nn.CrossEntropyLoss(ignore_index=vocab["pad_id"], reduction="sum")

    history: list[dict[str, Any]] = []
    latest: dict[str, Any] | None = None
    started = time.time()
    step = 0
    d_frozen = False

    print("Phase 08 - H5' Paired Surgery GAN Pilot")
    print(f"device={device_summary(device)}")
    print(f"split_dir={args.split_dir}")
    print(f"anchor_load={anchor_load}")
    print(f"train_rows={len(train_df):,} dev_rows={len(dev_df):,} vocab={len(vocab['tokens']):,} train_slots={train_slots:,}")
    print(
        "config batch_size={} max_steps={} max_len={} slot_mode={} adv_weight={} anchor_weight={} entropy_weight={} amp={}".format(
            args.batch_size,
            args.max_steps,
            args.max_len,
            args.slot_mode,
            args.adv_weight,
            args.anchor_weight,
            args.entropy_weight,
            amp_enabled,
        )
    )

    while step < args.max_steps:
        for ids_cpu, slot_cpu, valid_cpu, cond_cpu in iter_batches(train_tensors, args.batch_size, args.seed, step):
            slot_count = int(slot_cpu.sum().item())
            if slot_count == 0:
                continue
            ids = ids_cpu.to(device)
            slot_mask = slot_cpu.to(device)
            valid_mask = valid_cpu.to(device)
            cond = cond_cpu.to(device)
            frame = corrupt_batch(ids, slot_mask, vocab["mask_id"], args.mask_prob)

            d_acc_value = math.nan
            loss_d_value = 0.0
            for _ in range(args.d_steps):
                if d_frozen:
                    break
                opt_d.zero_grad(set_to_none=True)
                with autocast_context(device, amp_enabled):
                    with torch.no_grad():
                        g_logits_detached = generator(frame, cond)
                        g_logits_detached = apply_constrained_logits(g_logits_detached, ids, slot_mask, allowed_mask_by_token)
                        fake_emb_detached = fake_embedding_from_logits(generator, ids, g_logits_detached, slot_mask).detach()
                    real_emb = real_embedding_from_ids(generator, ids).detach()
                    real_logits = discriminator.score_emb(frame, real_emb, cond, valid_mask)
                    fake_logits = discriminator.score_emb(frame, fake_emb_detached, cond, valid_mask)
                    loss_d = F.binary_cross_entropy_with_logits(real_logits, torch.ones_like(real_logits) * 0.9)
                    loss_d = loss_d + F.binary_cross_entropy_with_logits(fake_logits, torch.zeros_like(fake_logits) + 0.1)
                if not torch.isfinite(loss_d):
                    raise RuntimeError(f"Non-finite D loss: {float(loss_d.detach().cpu())}")
                scaler_d.scale(loss_d).backward()
                scaler_d.unscale_(opt_d)
                nn.utils.clip_grad_norm_(discriminator.parameters(), 1.0)
                scaler_d.step(opt_d)
                scaler_d.update()
                loss_d_value = float(loss_d.detach().cpu())
                d_acc_value = d_accuracy(real_logits, fake_logits)
                d_frozen = d_acc_value >= args.d_freeze_acc

            opt_g.zero_grad(set_to_none=True)
            with autocast_context(device, amp_enabled):
                g_logits = generator(frame, cond)
                g_logits = apply_constrained_logits(g_logits, ids, slot_mask, allowed_mask_by_token)
                targets = ids.masked_fill(~slot_mask, vocab["pad_id"])
                loss_anchor = ce_sum(g_logits.reshape(-1, g_logits.size(-1)), targets.reshape(-1)) / max(slot_count, 1)
                fake_emb = fake_embedding_from_logits(generator, ids, g_logits, slot_mask)
                fake_logits_for_g = discriminator.score_emb(frame, fake_emb, cond, valid_mask)
                loss_adv = F.binary_cross_entropy_with_logits(fake_logits_for_g, torch.ones_like(fake_logits_for_g))
                slot_entropy = entropy_on_slots(g_logits, slot_mask)
                loss_g = args.anchor_weight * loss_anchor + args.adv_weight * loss_adv - args.entropy_weight * slot_entropy
            if not torch.isfinite(loss_g):
                raise RuntimeError(f"Non-finite G loss: {float(loss_g.detach().cpu())}")
            scaler_g.scale(loss_g).backward()
            scaler_g.unscale_(opt_g)
            nn.utils.clip_grad_norm_(generator.parameters(), 1.0)
            scaler_g.step(opt_g)
            scaler_g.update()

            step += 1
            if step % args.log_every == 0 or step == args.max_steps:
                elapsed = time.time() - started
                print(
                    "step={}/{} loss_d={:.5f} loss_g={:.5f} anchor={:.5f} adv={:.5f} ent={:.5f} d_acc={} frozen={} elapsed={:.1f}s".format(
                        step,
                        args.max_steps,
                        loss_d_value,
                        float(loss_g.detach().cpu()),
                        float(loss_anchor.detach().cpu()),
                        float(loss_adv.detach().cpu()),
                        float(slot_entropy.detach().cpu()),
                        "nan" if math.isnan(d_acc_value) else f"{d_acc_value:.3f}",
                        d_frozen,
                        elapsed,
                    ),
                    flush=True,
                )
                save_json(
                    args.log_dir / "phase08_paired_surgery_gan_progress.json",
                    {
                        "stage": "training",
                        "step": step,
                        "max_steps": args.max_steps,
                        "loss_d": loss_d_value,
                        "loss_g": float(loss_g.detach().cpu()),
                        "loss_anchor": float(loss_anchor.detach().cpu()),
                        "loss_adv": float(loss_adv.detach().cpu()),
                        "slot_entropy": float(slot_entropy.detach().cpu()),
                        "d_acc": d_acc_value,
                        "d_frozen": d_frozen,
                        "elapsed_sec": elapsed,
                        "device": device_summary(device),
                    },
                )
            if step % args.eval_every == 0 or step == args.max_steps:
                dev = evaluate_anchor(generator, dev_tensors, args, vocab, device, amp_enabled)
                latest = {
                    "step": step,
                    "loss_d": loss_d_value,
                    "loss_g": float(loss_g.detach().cpu()),
                    "loss_anchor": float(loss_anchor.detach().cpu()),
                    "loss_adv": float(loss_adv.detach().cpu()),
                    "slot_entropy": float(slot_entropy.detach().cpu()),
                    "d_acc": d_acc_value,
                    "d_frozen": d_frozen,
                    "dev": dev,
                    "elapsed_sec": time.time() - started,
                }
                history.append(latest)
                print(f"eval step={step} dev_slot_loss={dev['slot_loss']:.5f} dev_slot_acc={dev['slot_accuracy']:.4f}", flush=True)
                d_frozen = d_frozen and d_acc_value >= args.d_freeze_acc
            if step >= args.max_steps:
                break

    if latest is None:
        dev = evaluate_anchor(generator, dev_tensors, args, vocab, device, amp_enabled)
        latest = {"step": step, "loss_d": 0.0, "loss_g": 0.0, "loss_anchor": 0.0, "loss_adv": 0.0, "slot_entropy": 0.0, "d_acc": math.nan, "d_frozen": d_frozen, "dev": dev, "elapsed_sec": time.time() - started}

    samples = generate_samples(generator, dev_df, args, vocab, device, amp_enabled, allowed_mask_by_token)
    samples_path = args.output_dir / "paired_surgery_gan_samples.jsonl"
    write_jsonl(samples_path, samples)
    sample_metrics = sample_summary(samples)

    checkpoint_path = args.checkpoint_dir / "paired_surgery_gan_latest.pt"
    torch.save(
        {
            "generator_state": generator.state_dict(),
            "discriminator_state": discriminator.state_dict(),
            "vocab": vocab,
            "techniques": TECHNIQUES,
            "args": vars(args),
            "global_step": step,
            "history": history,
            "anchor_load": anchor_load,
        },
        checkpoint_path,
    )

    result = {
        "split_dir": str(args.split_dir),
        "rows": {"train": len(train_df), "dev": len(dev_df)},
        "device": device_summary(device),
        "config": {
            "batch_size": args.batch_size,
            "max_steps": args.max_steps,
            "max_len": args.max_len,
            "slot_mode": args.slot_mode,
            "embed_dim": args.embed_dim,
            "hidden_dim": args.hidden_dim,
            "d_hidden_dim": args.d_hidden_dim,
            "mixed_precision": amp_enabled,
            "adv_weight": args.adv_weight,
            "anchor_weight": args.anchor_weight,
            "entropy_weight": args.entropy_weight,
            "sample_temperature": args.sample_temperature,
            "sample_top_k": args.sample_top_k,
            "sample_argmax": args.sample_argmax,
            "train_limit": args.train_limit,
            "dev_limit": args.dev_limit,
            "constrained_logits": allowed_mask_by_token is not None,
        },
        "anchor_load": anchor_load,
        "latest": latest,
        "history": history,
        "checkpoint": str(checkpoint_path),
        "samples_path": str(samples_path),
        "sample_summary": sample_metrics,
        "elapsed_sec": time.time() - started,
    }
    json_path = args.report_dir / args.json_name
    report_path = args.report_dir / args.report_name
    save_json(json_path, result)
    write_report(report_path, result)
    save_json(args.log_dir / "phase08_paired_surgery_gan_progress.json", {"stage": "done", "step": step, "elapsed_sec": result["elapsed_sec"], "device": result["device"]})
    print("Phase 08 H5' paired surgery GAN complete")
    print(f"samples={samples_path}")
    print(f"checkpoint={checkpoint_path}")
    print(f"report={report_path}")


if __name__ == "__main__":
    main()
