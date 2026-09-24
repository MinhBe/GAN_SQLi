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

from .models import Discriminator, Generator
from .tokenizer import CharCodec
from .validators import static_validate


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def configure_torch(device: str, *, allow_tf32: bool = True):
    if device.startswith("cuda") and torch.cuda.is_available():
        torch.backends.cudnn.benchmark = True
        torch.backends.cuda.matmul.allow_tf32 = allow_tf32
        torch.backends.cudnn.allow_tf32 = allow_tf32
        try:
            torch.set_float32_matmul_precision("high")
        except Exception:
            pass


def load_lines(path: str | Path, limit: int | None = None) -> list[str]:
    lines = [x.rstrip("\n") for x in Path(path).read_text(encoding="utf-8").splitlines() if x.strip()]
    return lines[:limit] if limit else lines


def make_loader(texts: list[str], codec: CharCodec, batch_size: int, shuffle: bool = True,
                num_workers: int = 2, pin_memory: bool | None = None) -> DataLoader:
    arr = torch.tensor([codec.encode(x) for x in texts], dtype=torch.long)
    pin_memory = torch.cuda.is_available() if pin_memory is None else pin_memory
    kwargs = {
        "batch_size": batch_size,
        "shuffle": shuffle,
        "drop_last": False,
        "num_workers": max(int(num_workers), 0),
        "pin_memory": bool(pin_memory),
    }
    if kwargs["num_workers"] > 0:
        kwargs["persistent_workers"] = True
        kwargs["prefetch_factor"] = 2
    return DataLoader(TensorDataset(arr), **kwargs)


def _autocast_context(device: str, amp: bool):
    if amp and device.startswith("cuda"):
        return torch.amp.autocast("cuda", dtype=torch.float16)
    return torch.amp.autocast("cpu", enabled=False)


def mle_epoch(gen: Generator, loader: DataLoader, opt, pad_id: int, device: str, *, amp: bool = True) -> float:
    gen.train()
    total_loss = 0.0
    total_tok = 0
    loss_fn = nn.CrossEntropyLoss(ignore_index=pad_id, reduction="sum")
    scaler = torch.amp.GradScaler("cuda", enabled=(amp and device.startswith("cuda")))
    for (x,) in loader:
        x = x.to(device, non_blocking=True)
        inp = x[:, :-1]
        tgt = x[:, 1:]
        opt.zero_grad(set_to_none=True)
        with _autocast_context(device, amp):
            logits = gen(inp)
            loss_sum = loss_fn(logits.reshape(-1, logits.size(-1)), tgt.reshape(-1))
            ntok = tgt.ne(pad_id).sum().item()
            loss = loss_sum / max(ntok, 1)
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(gen.parameters(), 5.0)
        scaler.step(opt)
        scaler.update()
        total_loss += float(loss_sum.detach().item())
        total_tok += int(ntok)
    return total_loss / max(total_tok, 1)


@torch.no_grad()
def sample_texts(gen: Generator, codec: CharCodec, n: int, batch_size: int, temperature: float, device: str) -> list[str]:
    rows = []
    for start in range(0, n, batch_size):
        b = min(batch_size, n - start)
        ids = gen.sample(b, codec.max_len, codec.bos_id, codec.eos_id, temperature=temperature, device=device)
        rows.extend(codec.decode(row.tolist()) for row in ids.cpu())
    return rows


def train_discriminator_epoch(disc: Discriminator, gen: Generator, real_loader: DataLoader, codec: CharCodec, opt, device: str,
                              temperature: float, *, amp: bool = True) -> float:
    disc.train()
    gen.eval()
    bce = nn.BCEWithLogitsLoss()
    losses = []
    scaler = torch.amp.GradScaler("cuda", enabled=(amp and device.startswith("cuda")))
    for (real,) in real_loader:
        real = real.to(device, non_blocking=True)
        with torch.no_grad():
            fake = gen.sample(real.size(0), codec.max_len, codec.bos_id, codec.eos_id, temperature=temperature, device=device)
            if fake.size(1) < codec.max_len:
                pad = torch.full((fake.size(0), codec.max_len - fake.size(1)), codec.pad_id, dtype=torch.long, device=device)
                fake = torch.cat([fake, pad], dim=1)
            fake = fake[:, :codec.max_len]
        opt.zero_grad(set_to_none=True)
        with _autocast_context(device, amp):
            logits_real = disc(real)
            logits_fake = disc(fake.detach())
            loss = bce(logits_real, torch.ones_like(logits_real)) + bce(logits_fake, torch.zeros_like(logits_fake))
        scaler.scale(loss).backward()
        scaler.step(opt)
        scaler.update()
        losses.append(float(loss.detach().item()))
    return float(np.mean(losses)) if losses else 0.0


def policy_gradient_epoch(gen: Generator, disc: Discriminator, codec: CharCodec, opt, steps: int, batch_size: int, device: str,
                          static_weight: float, temperature: float, *, amp: bool = True) -> float:
    """SeqGAN-lite update: whole-sequence discriminator reward + static reward.

    This is deliberately conservative. It is intended for controlled offline
    comparison, not as proof of runtime SQL validity.
    """
    gen.train()
    disc.eval()
    losses = []
    scaler = torch.amp.GradScaler("cuda", enabled=(amp and device.startswith("cuda")))
    for _ in range(steps):
        x = torch.full((batch_size, 1), codec.bos_id, dtype=torch.long, device=device)
        hidden = None
        seq = []
        logps = []
        finished = torch.zeros(batch_size, dtype=torch.bool, device=device)
        for _t in range(codec.max_len - 1):
            with _autocast_context(device, amp):
                emb = gen.emb(x[:, -1:])
                y, hidden = gen.rnn(emb, hidden)
                logits = gen.out(y[:, -1]) / max(temperature, 1e-6)
            # Avoid in-place writes on tensors participating in autograd.
            # The previous implementation used in-place logits masking and
            # `finished |= ...`, which can trip PyTorch's version counter during
            # REINFORCE backward on Kaggle/PyTorch 2.x. Keep every mask immutable
            # within the current graph step.
            banned = torch.zeros(logits.size(-1), dtype=torch.bool, device=device)
            banned[codec.pad_id] = True
            banned[codec.bos_id] = True
            logits = logits.masked_fill(banned.unsqueeze(0), -1e9)
            probs = torch.softmax(logits.float(), dim=-1)
            dist = torch.distributions.Categorical(probs=probs)
            nxt_sample = dist.sample()
            lp_sample = dist.log_prob(nxt_sample)

            was_finished = finished.clone()
            nxt = torch.where(was_finished, torch.full_like(nxt_sample, codec.eos_id), nxt_sample)
            lp = torch.where(was_finished, torch.zeros_like(lp_sample), lp_sample)
            seq.append(nxt)
            logps.append(lp)
            finished = finished | nxt.eq(codec.eos_id)
            x = torch.cat([x, nxt[:, None]], dim=1)
            if bool(finished.all().item()):
                break
        seq_t = torch.stack(seq, dim=1)
        if seq_t.size(1) < codec.max_len:
            pad = torch.full((batch_size, codec.max_len - seq_t.size(1)), codec.pad_id, dtype=torch.long, device=device)
            disc_seq = torch.cat([seq_t, pad], dim=1)
        else:
            disc_seq = seq_t[:, :codec.max_len]
        with torch.no_grad():
            with _autocast_context(device, amp):
                d_reward = torch.sigmoid(disc(disc_seq)).float()
            decoded = [codec.decode(row.tolist()) for row in seq_t.detach().cpu()]
            s_reward = torch.tensor([static_validate(x).static_score for x in decoded], dtype=torch.float32, device=device)
            reward = (1.0 - static_weight) * d_reward + static_weight * s_reward
            reward = reward - reward.mean()
        logp = torch.stack(logps, dim=1).sum(dim=1)
        loss = -(reward * logp).mean()
        opt.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(gen.parameters(), 5.0)
        scaler.step(opt)
        scaler.update()
        losses.append(float(loss.detach().item()))
    return float(np.mean(losses)) if losses else 0.0


def maybe_compile(model: nn.Module, enabled: bool):
    if not enabled:
        return model
    try:
        return torch.compile(model)
    except Exception:
        return model


def train(corpus: str | Path, out_dir: str | Path, *, module_id: str = "module", max_len: int = 192,
          limit: int | None = None, batch_size: int = 64, mle_epochs: int = 8, d_epochs: int = 2,
          adv_epochs: int = 0, adv_steps: int = 100, emb_dim: int = 96, hidden_dim: int = 192,
          lr: float = 1e-3, seed: int = 7, temperature: float = 0.9, static_weight: float = 0.35,
          device: str | None = None, num_workers: int = 2, amp: bool = True, compile_model: bool = False,
          allow_tf32: bool = True) -> dict:
    set_seed(seed)
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    configure_torch(device, allow_tf32=allow_tf32)
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    texts = load_lines(corpus, limit=limit)
    if not texts:
        raise ValueError(f"Empty corpus: {corpus}")
    codec = CharCodec.fit(texts, max_len=max_len)
    loader = make_loader(texts, codec, batch_size=batch_size, shuffle=True, num_workers=num_workers)
    gen = Generator(codec.vocab_size, emb_dim=emb_dim, hidden_dim=hidden_dim, pad_id=codec.pad_id).to(device)
    disc = Discriminator(codec.vocab_size, emb_dim=emb_dim, pad_id=codec.pad_id).to(device)
    gen = maybe_compile(gen, compile_model)
    disc = maybe_compile(disc, compile_model)
    opt_g = torch.optim.AdamW(gen.parameters(), lr=lr)
    opt_d = torch.optim.AdamW(disc.parameters(), lr=lr)
    history = []
    best = math.inf
    for ep in range(1, mle_epochs + 1):
        nll = mle_epoch(gen, loader, opt_g, codec.pad_id, device, amp=amp)
        history.append({"phase": "mle", "epoch": ep, "nll": nll})
        if nll < best:
            best = nll
            torch.save(gen.state_dict(), out_dir / "generator_mle_best.pt")
    for ep in range(1, d_epochs + 1):
        d_loss = train_discriminator_epoch(disc, gen, loader, codec, opt_d, device, temperature, amp=amp)
        history.append({"phase": "discriminator", "epoch": ep, "d_loss": d_loss})
    for ep in range(1, adv_epochs + 1):
        pg_loss = policy_gradient_epoch(gen, disc, codec, opt_g, adv_steps, batch_size, device, static_weight, temperature, amp=amp)
        d_loss = train_discriminator_epoch(disc, gen, loader, codec, opt_d, device, temperature, amp=amp)
        history.append({"phase": "adv", "epoch": ep, "pg_loss": pg_loss, "d_loss": d_loss})
    # In case model was compiled, state_dict remains loadable with possible _orig_mod prefix. Strip it.
    def clean_state_dict(m):
        sd = m.state_dict()
        if any(k.startswith("_orig_mod.") for k in sd):
            sd = {k.replace("_orig_mod.", "", 1): v for k, v in sd.items()}
        return sd
    codec.save(out_dir / "codec.json")
    torch.save({
        "module_id": module_id,
        "generator_state_dict": clean_state_dict(gen),
        "discriminator_state_dict": clean_state_dict(disc),
        "config": {
            "max_len": max_len, "emb_dim": emb_dim, "hidden_dim": hidden_dim,
            "batch_size": batch_size, "mle_epochs": mle_epochs, "d_epochs": d_epochs,
            "adv_epochs": adv_epochs, "static_weight": static_weight,
            "num_workers": num_workers, "amp": amp, "compile_model": compile_model,
        },
    }, out_dir / "checkpoint.pt")
    (out_dir / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    sample = sample_texts(gen, codec, n=64, batch_size=batch_size, temperature=temperature, device=device)
    pd.DataFrame({"payload_raw": sample}).to_csv(out_dir / "sample_preview.csv", index=False)
    device_name = torch.cuda.get_device_name(device) if str(device).startswith("cuda") and torch.cuda.is_available() else str(device)
    return {"module_id": module_id, "corpus_size": len(texts), "vocab_size": codec.vocab_size, "best_mle_nll": best, "out_dir": str(out_dir), "device": str(device), "device_name": device_name, "amp": bool(amp)}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--module-id", default="module")
    ap.add_argument("--max-len", type=int, default=192)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--mle-epochs", type=int, default=8)
    ap.add_argument("--d-epochs", type=int, default=2)
    ap.add_argument("--adv-epochs", type=int, default=0)
    ap.add_argument("--adv-steps", type=int, default=100)
    ap.add_argument("--emb-dim", type=int, default=96)
    ap.add_argument("--hidden-dim", type=int, default=192)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--temperature", type=float, default=0.9)
    ap.add_argument("--static-weight", type=float, default=0.35)
    ap.add_argument("--device", default=None)
    ap.add_argument("--num-workers", type=int, default=2)
    ap.add_argument("--no-amp", action="store_true")
    ap.add_argument("--compile", action="store_true", dest="compile_model")
    args = ap.parse_args(argv)
    kwargs = vars(args)
    kwargs["amp"] = not kwargs.pop("no_amp")
    print(json.dumps(train(**kwargs), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
