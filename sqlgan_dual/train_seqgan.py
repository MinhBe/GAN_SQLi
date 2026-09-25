from __future__ import annotations

import argparse
import json
import math
import random
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.utils.data import DataLoader, TensorDataset
from tqdm import tqdm

from .data import load_training_jsonl, save_contracts
from .models import Discriminator, Generator
from .reward import sha256_text
from .rollout import Rollout, pad_to
from .tokenizer import CharCodec


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def configure_torch(device: str) -> None:
    if device.startswith("cuda") and torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = True
        torch.backends.cudnn.allow_tf32 = True
        try:
            torch.set_float32_matmul_precision("high")
        except Exception:
            pass


def _autocast(device: str, amp: bool):
    if amp and device.startswith("cuda"):
        return torch.amp.autocast("cuda", dtype=torch.float16)
    return torch.amp.autocast("cpu", enabled=False)


def make_loader(texts: list[str], codec: CharCodec, batch_size: int, *, shuffle: bool = True, num_workers: int = 0) -> DataLoader:
    arr = torch.tensor([codec.encode(x) for x in texts], dtype=torch.long)
    return DataLoader(TensorDataset(arr), batch_size=batch_size, shuffle=shuffle, drop_last=False, num_workers=max(0, int(num_workers)), pin_memory=torch.cuda.is_available())


def mle_epoch(gen: Generator, loader: DataLoader, opt, pad_id: int, device: str, *, amp: bool = True) -> float:
    gen.train()
    loss_fn = nn.CrossEntropyLoss(ignore_index=pad_id, reduction="sum")
    scaler = torch.amp.GradScaler("cuda", enabled=(amp and device.startswith("cuda")))
    total_loss = 0.0
    total_tok = 0
    for (x,) in loader:
        x = x.to(device, non_blocking=True)
        opt.zero_grad(set_to_none=True)
        with _autocast(device, amp):
            logits = gen(x[:, :-1])
            tgt = x[:, 1:]
            loss_sum = loss_fn(logits.reshape(-1, logits.size(-1)), tgt.reshape(-1))
            ntok = int(tgt.ne(pad_id).sum().item())
            loss = loss_sum / max(ntok, 1)
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(gen.parameters(), 5.0)
        scaler.step(opt)
        scaler.update()
        total_loss += float(loss_sum.detach().item())
        total_tok += ntok
    return total_loss / max(total_tok, 1)


def train_discriminator_epoch(disc: Discriminator, gen: Generator, loader: DataLoader, codec: CharCodec, opt, device: str, *, temperature: float, amp: bool = True) -> float:
    disc.train()
    gen.eval()
    bce = nn.BCEWithLogitsLoss()
    scaler = torch.amp.GradScaler("cuda", enabled=(amp and device.startswith("cuda")))
    losses = []
    for (real,) in loader:
        real = real.to(device, non_blocking=True)
        with torch.no_grad():
            fake = gen.sample(real.size(0), codec.max_len, codec.bos_id, codec.eos_id, temperature, device)
            fake = pad_to(fake, codec.max_len, codec.pad_id)
        opt.zero_grad(set_to_none=True)
        with _autocast(device, amp):
            real_logits = disc(real)
            fake_logits = disc(fake)
            loss = bce(real_logits, torch.ones_like(real_logits)) + bce(fake_logits, torch.zeros_like(fake_logits))
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()
        losses.append(float(loss.detach().item()))
    return float(np.mean(losses)) if losses else 0.0


def pg_epoch(
    gen: Generator,
    disc: Discriminator,
    rollout: Rollout,
    codec: CharCodec,
    opt,
    *,
    steps: int,
    batch_size: int,
    device: str,
    contracts: list[dict] | None,
    training_hashes: set[str],
    n_rollout: int,
    static_weight: float,
    temperature: float,
    amp: bool = True,
) -> float:
    gen.train()
    disc.eval()
    scaler = torch.amp.GradScaler("cuda", enabled=(amp and device.startswith("cuda")))
    losses = []
    for _ in range(max(0, int(steps))):
        seq, logps, mask = gen.sample_with_logp(batch_size, codec.max_len, codec.bos_id, codec.eos_id, temperature, device)
        with torch.no_grad():
            rewards = rollout.rewards(seq.detach(), disc, codec, contracts=contracts, training_hashes=training_hashes, n_rollout=n_rollout, static_weight=static_weight, temperature=temperature)
            rewards = rewards - rewards.mean()
        loss = -((logps * rewards * mask).sum() / mask.sum().clamp_min(1.0))
        opt.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(gen.parameters(), 5.0)
        scaler.step(opt)
        scaler.update()
        rollout.update(gen)
        losses.append(float(loss.detach().item()))
    return float(np.mean(losses)) if losses else 0.0


@torch.no_grad()
def sample_texts(gen: Generator, codec: CharCodec, n: int, batch_size: int, temperature: float, device: str) -> list[str]:
    gen.eval()
    rows = []
    for start in range(0, n, batch_size):
        b = min(batch_size, n - start)
        ids = gen.sample(b, codec.max_len, codec.bos_id, codec.eos_id, temperature, device)
        rows.extend(codec.decode(row.tolist()) for row in ids.cpu())
    return rows


def clean_state_dict(model: nn.Module) -> dict:
    sd = model.state_dict()
    if any(k.startswith("_orig_mod.") for k in sd):
        return {k.replace("_orig_mod.", "", 1): v for k, v in sd.items()}
    return sd


def train(
    training_jsonl: str | Path,
    out_dir: str | Path,
    *,
    module_id: str = "module",
    max_len: int = 192,
    limit: int | None = None,
    batch_size: int = 64,
    mle_epochs: int = 8,
    d_epochs: int = 2,
    adv_epochs: int = 0,
    adv_steps: int = 50,
    rollouts: int = 4,
    emb_dim: int = 96,
    hidden_dim: int = 192,
    lr: float = 1e-3,
    seed: int = 7,
    temperature: float = 0.9,
    static_weight: float = 0.35,
    device: str | None = None,
    num_workers: int = 0,
    amp: bool = True,
) -> dict:
    set_seed(seed)
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    configure_torch(device)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    texts, contracts = load_training_jsonl(training_jsonl, limit=limit)
    texts = [x for x in texts if x]
    if not texts:
        raise ValueError(f"Empty training data: {training_jsonl}")
    codec = CharCodec.fit(texts, max_len=max_len)
    loader = make_loader(texts, codec, batch_size, shuffle=True, num_workers=num_workers)
    gen = Generator(codec.vocab_size, emb_dim=emb_dim, hidden_dim=hidden_dim, pad_id=codec.pad_id).to(device)
    disc = Discriminator(codec.vocab_size, emb_dim=emb_dim, pad_id=codec.pad_id).to(device)
    opt_g = torch.optim.AdamW(gen.parameters(), lr=lr)
    opt_d = torch.optim.AdamW(disc.parameters(), lr=lr)
    training_hashes = {sha256_text(x) for x in texts}
    history = []
    best = math.inf
    for ep in range(1, mle_epochs + 1):
        nll = mle_epoch(gen, loader, opt_g, codec.pad_id, device, amp=amp)
        history.append({"phase": "mle", "epoch": ep, "nll": nll})
        if nll < best:
            best = nll
            torch.save(clean_state_dict(gen), out_dir / "generator_mle_best.pt")
    for ep in range(1, d_epochs + 1):
        d_loss = train_discriminator_epoch(disc, gen, loader, codec, opt_d, device, temperature=temperature, amp=amp)
        history.append({"phase": "discriminator", "epoch": ep, "d_loss": d_loss})
    rollout = Rollout(gen)
    for ep in range(1, adv_epochs + 1):
        pg_loss = pg_epoch(gen, disc, rollout, codec, opt_g, steps=adv_steps, batch_size=batch_size, device=device, contracts=contracts, training_hashes=training_hashes, n_rollout=rollouts, static_weight=static_weight, temperature=temperature, amp=amp)
        d_loss = train_discriminator_epoch(disc, gen, loader, codec, opt_d, device, temperature=temperature, amp=amp)
        history.append({"phase": "adv", "epoch": ep, "pg_loss": pg_loss, "d_loss": d_loss})
    codec.save(out_dir / "codec.json")
    save_contracts(contracts, out_dir / "contracts.jsonl")
    torch.save({
        "module_id": module_id,
        "generator_state_dict": clean_state_dict(gen),
        "discriminator_state_dict": clean_state_dict(disc),
        "config": {"max_len": max_len, "emb_dim": emb_dim, "hidden_dim": hidden_dim, "batch_size": batch_size, "mle_epochs": mle_epochs, "d_epochs": d_epochs, "adv_epochs": adv_epochs, "rollouts": rollouts, "static_weight": static_weight},
    }, out_dir / "checkpoint.pt")
    (out_dir / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    preview = sample_texts(gen, codec, min(64, max(8, batch_size)), batch_size, temperature, device)
    pd.DataFrame({"payload_raw": preview}).to_csv(out_dir / "sample_preview.csv", index=False)
    return {"module_id": module_id, "corpus_size": len(texts), "vocab_size": codec.vocab_size, "best_mle_nll": best, "out_dir": str(out_dir), "device": device, "adv_mode": "monte_carlo_rollout" if adv_epochs else "mle_or_discriminator_only"}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--training-jsonl", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--module-id", default="module")
    ap.add_argument("--max-len", type=int, default=192)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--mle-epochs", type=int, default=8)
    ap.add_argument("--d-epochs", type=int, default=2)
    ap.add_argument("--adv-epochs", type=int, default=0)
    ap.add_argument("--adv-steps", type=int, default=50)
    ap.add_argument("--rollouts", type=int, default=4)
    ap.add_argument("--emb-dim", type=int, default=96)
    ap.add_argument("--hidden-dim", type=int, default=192)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--temperature", type=float, default=0.9)
    ap.add_argument("--static-weight", type=float, default=0.35)
    ap.add_argument("--device", default=None)
    ap.add_argument("--num-workers", type=int, default=0)
    ap.add_argument("--no-amp", action="store_true")
    args = ap.parse_args(argv)
    kwargs = vars(args)
    kwargs["out_dir"] = kwargs.pop("out")
    kwargs["amp"] = not kwargs.pop("no_amp")
    print(json.dumps(train(**kwargs), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
