"""
pretrain_mle_v2.py — MLE pretrain với tiered data weighting và conditional embedding.

Khác pretrain_mle.py (V1):
  - Đọc từ data/v2/ (vocab_size=89, payload_delex, type_id, tier)
  - Upweight gold tier 3× via WeightedRandomSampler
  - Truyền type_id làm conditional embedding
  - Save vào checkpoints/v2/
"""
import argparse
import json
import math
import os
import sys
from pathlib import Path

import pandas as pd
import torch
import torch.nn as nn
import torch.nn.functional as F
import yaml
from torch.utils.data import DataLoader, Dataset, WeightedRandomSampler

sys.path.insert(0, str(Path(__file__).parent))

from src.generator import GeneratorLSTM
from src.tokenizer import SQLTokenizer
from src.utils import set_seed, pad_sequences, save_checkpoint, get_device


def load_tokenizer(path: str) -> SQLTokenizer:
    """Load tokenizer supporting both flat {token:id} and {token2id:{...}} formats."""
    import json
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    vocab = data.get("token2id", data)  # handle both formats
    return SQLTokenizer(vocab)

try:
    from torch.utils.tensorboard import SummaryWriter
    HAS_TB = True
except ImportError:
    HAS_TB = False


class TieredSQLiDataset(Dataset):
    """Dataset với gold/silver/bronze tier filtering và type_id conditioning."""

    def __init__(self, csv_path: str, tokenizer: SQLTokenizer, max_len: int = 80):
        df = pd.read_csv(csv_path)

        # Payload column
        if "payload_delex" in df.columns:
            payload_col = "payload_delex"
        elif "payload_norm" in df.columns:
            payload_col = "payload_norm"
        else:
            payload_col = "payload"

        # Tier filter: chỉ train gold + silver
        if "tier" in df.columns:
            df = df[df["tier"].isin(["gold", "silver"])].copy()
        else:
            df["tier"] = "silver"

        # Type id
        if "type_id" in df.columns:
            type_ids = df["type_id"].fillna(0).astype(int).tolist()
        else:
            type_ids = [0] * len(df)

        self.payloads = df[payload_col].fillna("").astype(str).tolist()
        self.type_ids = type_ids
        self.tiers = df["tier"].tolist() if "tier" in df.columns else ["silver"] * len(df)
        self.tokenizer = tokenizer
        self.max_len = max_len

    def __len__(self):
        return len(self.payloads)

    def __getitem__(self, idx):
        tokens = self.tokenizer.encode(
            self.payloads[idx], add_sos=True, add_eos=True
        )[: self.max_len + 2]
        weight = 3.0 if self.tiers[idx] == "gold" else 1.0
        return tokens, self.type_ids[idx], weight


def collate_fn(batch, pad_id: int):
    tokens_list = [b[0] for b in batch]
    type_ids = torch.tensor([b[1] for b in batch], dtype=torch.long)
    padded = pad_sequences(tokens_list, pad_id)
    return padded, type_ids


def compute_perplexity(model, loader, device, pad_id):
    model.eval()
    total_loss = 0.0
    total_tokens = 0
    with torch.no_grad():
        for batch, type_ids in loader:
            batch = batch.to(device)
            type_ids = type_ids.to(device)
            inp, tgt = batch[:, :-1], batch[:, 1:]
            logits, _ = model(inp, cond=type_ids)
            B, T, V = logits.shape
            loss = F.cross_entropy(
                logits.reshape(B * T, V),
                tgt.reshape(B * T),
                ignore_index=pad_id,
                reduction="sum",
            )
            total_loss += loss.item()
            total_tokens += (tgt != pad_id).sum().item()
    return math.exp(total_loss / max(total_tokens, 1))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="SeqGAN_SQLi/configs/seqgan_v2.yaml")
    parser.add_argument("--data_dir", default=None)
    parser.add_argument("--ckpt_dir", default=None)
    parser.add_argument("--epochs", type=int, default=None)
    parser.add_argument("--steps", type=int, default=None, help="Max steps (smoke test)")
    args = parser.parse_args()

    cfg_path = args.config
    if not os.path.exists(cfg_path):
        cfg_path = os.path.join(os.path.dirname(__file__), args.config)
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    set_seed(cfg["seed"])
    device = get_device()
    print(f"Device: {device}")

    data_dir = Path(args.data_dir or cfg["data_dir"])
    ckpt_dir = Path(args.ckpt_dir or cfg["ckpt_dir"])
    ckpt_dir.mkdir(parents=True, exist_ok=True)

    tok = load_tokenizer(str(data_dir / "tokenizer_vocab.json"))
    print(f"Vocab size: {tok.vocab_size}")

    num_conditions = cfg.get("num_attack_types", 4)
    type_embed_dim = cfg.get("type_embed_dim", 32)
    embed_dim = cfg["embed_dim"]

    # cond_embed_dim distinct from embed_dim → concatenate mode
    model = GeneratorLSTM(
        vocab_size=tok.vocab_size,
        embed_dim=embed_dim,
        hidden_dim=cfg["hidden_dim"],
        num_layers=cfg["num_layers"],
        dropout=cfg["dropout"],
        num_conditions=num_conditions,
        cond_embed_dim=type_embed_dim,
    ).to(device)

    n_params = sum(p.numel() for p in model.parameters())
    print(f"Model params: {n_params:,}")

    optimizer = torch.optim.Adam(model.parameters(), lr=cfg["lr_mle"])

    pad_fn = lambda b: collate_fn(b, tok.pad_id)
    train_ds = TieredSQLiDataset(data_dir / "train.csv", tok, cfg["max_seq_len"])
    val_ds   = TieredSQLiDataset(data_dir / "val.csv",   tok, cfg["max_seq_len"])

    weights = [item[2] for item in train_ds]
    sampler = WeightedRandomSampler(weights, len(weights), replacement=True)

    train_loader = DataLoader(
        train_ds, batch_size=cfg["batch_size"], sampler=sampler, collate_fn=pad_fn
    )
    val_loader = DataLoader(
        val_ds, batch_size=cfg["batch_size"], shuffle=False, collate_fn=pad_fn
    )

    print(f"Train: {len(train_ds)} | Val: {len(val_ds)}")

    writer = None
    log_dir = Path(cfg.get("log_dir", "SeqGAN_SQLi/logs/v2"))
    if HAS_TB:
        log_dir.mkdir(parents=True, exist_ok=True)
        writer = SummaryWriter(str(log_dir / "pretrain"))

    n_epochs = args.epochs if args.epochs is not None else cfg["mle_epochs"]
    best_ppl = float("inf")
    patience = 0
    global_step = 0

    for epoch in range(1, n_epochs + 1):
        model.train()
        epoch_loss = 0.0
        n_batches = 0

        for batch, type_ids in train_loader:
            if args.steps and global_step >= args.steps:
                break

            batch = batch.to(device)
            type_ids = type_ids.to(device)
            inp, tgt = batch[:, :-1], batch[:, 1:]

            logits, _ = model(inp, cond=type_ids)
            B, T, V = logits.shape
            loss = F.cross_entropy(
                logits.reshape(B * T, V),
                tgt.reshape(B * T),
                ignore_index=tok.pad_id,
            )

            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), cfg["grad_clip"])
            optimizer.step()

            epoch_loss += loss.item()
            n_batches += 1
            global_step += 1

            if writer and global_step % 100 == 0:
                writer.add_scalar("train/loss", loss.item(), global_step)

        avg_loss = epoch_loss / max(n_batches, 1)
        val_ppl = compute_perplexity(model, val_loader, device, tok.pad_id)
        print(f"Epoch {epoch}/{n_epochs} | loss={avg_loss:.4f} | val_ppl={val_ppl:.2f}")

        if writer:
            writer.add_scalar("val/perplexity", val_ppl, epoch)

        if val_ppl < best_ppl:
            best_ppl = val_ppl
            patience = 0
            save_checkpoint(
                str(ckpt_dir / "mle_best.pt"),
                model, optimizer, global_step,
                {"epoch": epoch, "val_ppl": val_ppl},
            )
            print(f"  >> Best saved (ppl={best_ppl:.2f})")
        else:
            patience += 1
            if patience >= cfg.get("patience", 3):
                print(f"Early stop (patience={patience})")
                break

        if args.steps and global_step >= args.steps:
            print("Reached step limit (smoke test).")
            break

    save_checkpoint(
        str(ckpt_dir / "mle_final.pt"),
        model, optimizer, global_step,
        {"best_val_ppl": best_ppl},
    )
    print(f"\nPretraining done. Best val_ppl={best_ppl:.2f}")
    if writer:
        writer.close()


if __name__ == "__main__":
    main()
