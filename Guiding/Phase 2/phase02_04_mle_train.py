"""
Phase 02 — Script 4: MLE Baseline (Conditional LSTM)
Input : Guiding/Phase 2/slice_labeled.parquet
Output: Guiding/Phase 2/models/mle_baseline/seed_{seed}/
        Guiding/Phase 2/eval/mle_frontier.json
"""

import json
import random
import math
from pathlib import Path
from collections import Counter

import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

HERE   = Path(__file__).parent
SRC    = HERE / "slice_labeled.parquet"
OUT_M  = HERE / "models" / "mle_baseline"
OUT_E  = HERE / "eval" / "mle_frontier.json"

SEEDS       = [42, 123, 456]
MAX_EPOCHS  = 50
PATIENCE    = 5
BATCH_SIZE  = 64
LR          = 1e-3
EMBED_DIM   = 64
HIDDEN_DIM  = 256
MAX_LEN     = 64
MIN_FREQ    = 3

GEN_SAMPLES = 1000
TEMPERATURES = [0.7, 1.0, 1.2]
TOP_KS       = [10, 20, 50]
TOP_PS       = [0.9, 0.95]

# ── Tokenizer ──────────────────────────────────────────────────────────────────
PAD, BOS, EOS, UNK = "<pad>", "<bos>", "<eos>", "<unk>"

class Tokenizer:
    def __init__(self, texts: list[str], min_freq: int = MIN_FREQ):
        counter: Counter = Counter()
        for t in texts:
            counter.update(t.split())
        vocab = [PAD, BOS, EOS, UNK] + [w for w, c in counter.items() if c >= min_freq]
        self.token2id = {t: i for i, t in enumerate(vocab)}
        self.id2token = vocab
        self.pad_id = self.token2id[PAD]
        self.bos_id = self.token2id[BOS]
        self.eos_id = self.token2id[EOS]
        self.unk_id = self.token2id[UNK]

    def encode(self, text: str, max_len: int = MAX_LEN) -> list[int]:
        ids = [self.token2id.get(t, self.unk_id) for t in text.split()]
        ids = ids[:max_len - 2]
        return [self.bos_id] + ids + [self.eos_id]

    def decode(self, ids: list[int]) -> str:
        tokens = []
        for i in ids:
            if i == self.eos_id:
                break
            if i not in (self.bos_id, self.pad_id):
                tokens.append(self.id2token[i])
        return " ".join(tokens)

    @property
    def vocab_size(self):
        return len(self.id2token)


# ── Dataset ────────────────────────────────────────────────────────────────────
TECHNIQUES = ["benign", "boolean_blind", "time_blind", "union_based",
              "error_based", "generic_sqli", "unknown"]

class PayloadDataset(Dataset):
    def __init__(self, df: pd.DataFrame, tokenizer: Tokenizer):
        self.tokenizer = tokenizer
        self.technique2id = {t: i for i, t in enumerate(TECHNIQUES)}
        self.data = []
        for _, row in df.iterrows():
            ids = tokenizer.encode(str(row["payload_delex"]))
            if len(ids) < 3:
                continue
            cond = self.technique2id.get(row["technique_primary"], len(TECHNIQUES) - 1)
            self.data.append((ids, cond))

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        return self.data[idx]


def collate_fn(batch, pad_id: int):
    ids_list, conds = zip(*batch)
    max_l = max(len(x) for x in ids_list)
    padded = torch.zeros(len(ids_list), max_l, dtype=torch.long)
    for i, ids in enumerate(ids_list):
        padded[i, :len(ids)] = torch.tensor(ids)
    return padded, torch.tensor(conds, dtype=torch.long)


# ── Model ──────────────────────────────────────────────────────────────────────
class ConditionalLSTM(nn.Module):
    def __init__(self, vocab_size: int, n_techniques: int,
                 embed_dim: int = EMBED_DIM, hidden_dim: int = HIDDEN_DIM):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.cond_embed = nn.Embedding(n_techniques, embed_dim)
        self.lstm = nn.LSTM(embed_dim * 2, hidden_dim, batch_first=True)
        self.fc = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x: torch.Tensor, cond: torch.Tensor):
        emb = self.embedding(x)                          # [B, T, E]
        c   = self.cond_embed(cond).unsqueeze(1)         # [B, 1, E]
        c   = c.expand(-1, x.size(1), -1)               # [B, T, E]
        inp = torch.cat([emb, c], dim=-1)                # [B, T, 2E]
        out, _ = self.lstm(inp)                          # [B, T, H]
        return self.fc(out)                              # [B, T, V]


# ── Sampling utils ─────────────────────────────────────────────────────────────
def top_k_top_p_filter(logits: torch.Tensor, top_k: int, top_p: float) -> torch.Tensor:
    if top_k > 0:
        kth = torch.topk(logits, min(top_k, logits.size(-1))).values[..., -1, None]
        logits = logits.masked_fill(logits < kth, float("-inf"))
    if top_p < 1.0:
        sorted_logits, sorted_idx = torch.sort(logits, descending=True)
        cum_probs = torch.cumsum(torch.softmax(sorted_logits, dim=-1), dim=-1)
        remove = cum_probs - torch.softmax(sorted_logits, dim=-1) > top_p
        sorted_logits[remove] = float("-inf")
        logits.scatter_(-1, sorted_idx, sorted_logits)
    return logits


@torch.no_grad()
def generate(model: ConditionalLSTM, tokenizer: Tokenizer, device,
             technique_id: int, n: int,
             temperature: float, top_k: int, top_p: float) -> list[str]:
    model.eval()
    results = []
    for _ in range(n):
        ids = [tokenizer.bos_id]
        hidden = None
        cond = torch.tensor([technique_id], device=device)
        for _ in range(MAX_LEN):
            x = torch.tensor([ids[-1:]], device=device)
            emb = model.embedding(x)
            c   = model.cond_embed(cond).unsqueeze(1)
            inp = torch.cat([emb, c], dim=-1)
            out, hidden = model.lstm(inp, hidden)
            logits = model.fc(out[:, -1, :]) / temperature
            logits = top_k_top_p_filter(logits[0], top_k, top_p)
            prob = torch.softmax(logits, dim=-1)
            next_id = torch.multinomial(prob, 1).item()
            if next_id == tokenizer.eos_id:
                break
            ids.append(next_id)
        results.append(tokenizer.decode(ids))
    return results


# ── Metrics ────────────────────────────────────────────────────────────────────
def self_bleu3(samples: list[str]) -> float:
    from itertools import combinations
    if len(samples) < 2:
        return 0.0
    scores = []
    for a, b in random.sample(list(combinations(range(len(samples)), 2)), min(500, len(samples))):
        ref = samples[a].split()
        hyp = samples[b].split()
        if not hyp or len(ref) < 3:
            continue
        ngrams_ref = Counter(zip(*[ref[i:] for i in range(3)]))
        ngrams_hyp = Counter(zip(*[hyp[i:] for i in range(3)]))
        match = sum(min(ngrams_ref[g], ngrams_hyp[g]) for g in ngrams_hyp)
        total = sum(ngrams_hyp.values())
        scores.append(match / total if total else 0.0)
    return float(np.mean(scores)) if scores else 0.0


def token_entropy(samples: list[str]) -> float:
    counter: Counter = Counter()
    for s in samples:
        counter.update(s.split())
    total = sum(counter.values())
    if total == 0:
        return 0.0
    return float(-sum((c / total) * math.log2(c / total) for c in counter.values()))


RE_SQL_ANY = __import__("re").compile(
    r"\b(SELECT|UNION|FROM|WHERE|INSERT|UPDATE|DELETE|DROP|EXEC|ALTER|CREATE)\b",
    __import__("re").IGNORECASE,
)

def syntax_validity_rate(samples: list[str]) -> float:
    valid = sum(1 for s in samples if RE_SQL_ANY.search(s))
    return valid / len(samples) if samples else 0.0


def compute_metrics(samples: list[str]) -> dict:
    unique = list(set(samples))
    return {
        "n_total": len(samples),
        "unique_ratio": len(unique) / len(samples) if samples else 0,
        "self_bleu3": self_bleu3(samples),
        "token_entropy": token_entropy(samples),
        "syntax_validity_rate": syntax_validity_rate(samples),
    }


# ── Training ───────────────────────────────────────────────────────────────────
def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def train_one_seed(seed: int, df_train: pd.DataFrame, df_val: pd.DataFrame,
                   tokenizer: Tokenizer, device) -> dict:
    set_seed(seed)
    out_dir = OUT_M / f"seed_{seed}"
    out_dir.mkdir(parents=True, exist_ok=True)

    technique2id = {t: i for i, t in enumerate(TECHNIQUES)}
    n_tech = len(TECHNIQUES)

    train_ds = PayloadDataset(df_train, tokenizer)
    val_ds   = PayloadDataset(df_val,   tokenizer)
    pad_id   = tokenizer.pad_id

    train_dl = DataLoader(train_ds, batch_size=BATCH_SIZE, shuffle=True,
                          collate_fn=lambda b: collate_fn(b, pad_id))
    val_dl   = DataLoader(val_ds,   batch_size=BATCH_SIZE, shuffle=False,
                          collate_fn=lambda b: collate_fn(b, pad_id))

    model = ConditionalLSTM(tokenizer.vocab_size, n_tech).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    criterion = nn.CrossEntropyLoss(ignore_index=pad_id)

    best_val_loss = float("inf")
    patience_count = 0

    for epoch in range(MAX_EPOCHS):
        model.train()
        train_loss = 0.0
        for x, cond in train_dl:
            x, cond = x.to(device), cond.to(device)
            logits = model(x[:, :-1], cond)
            loss = criterion(logits.reshape(-1, tokenizer.vocab_size), x[:, 1:].reshape(-1))
            optimizer.zero_grad()
            loss.backward()
            nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            optimizer.step()
            train_loss += loss.item()

        model.eval()
        val_loss = 0.0
        with torch.no_grad():
            for x, cond in val_dl:
                x, cond = x.to(device), cond.to(device)
                logits = model(x[:, :-1], cond)
                loss = criterion(logits.reshape(-1, tokenizer.vocab_size), x[:, 1:].reshape(-1))
                val_loss += loss.item()

        val_loss /= max(len(val_dl), 1)
        print(f"  Seed {seed} Epoch {epoch+1:02d}: train={train_loss/max(len(train_dl),1):.4f} val={val_loss:.4f}")

        if val_loss < best_val_loss:
            best_val_loss = val_loss
            patience_count = 0
            torch.save(model.state_dict(), out_dir / "best.pt")
        else:
            patience_count += 1
            if patience_count >= PATIENCE:
                print(f"  Early stop at epoch {epoch+1}")
                break

    # Load best and generate samples for frontier
    model.load_state_dict(torch.load(out_dir / "best.pt", map_location=device))
    frontier = {}
    for temp in TEMPERATURES:
        for topk in TOP_KS:
            for topp in TOP_PS:
                config_key = f"t{temp}_k{topk}_p{topp}"
                samples = []
                for tech_id in range(n_tech - 1):  # skip unknown
                    samples += generate(model, tokenizer, device, tech_id,
                                        GEN_SAMPLES // (n_tech - 1),
                                        temp, topk, topp)
                m = compute_metrics(samples)
                m["temperature"] = temp
                m["top_k"] = topk
                m["top_p"] = topp
                frontier[config_key] = m

    return {"best_val_loss": best_val_loss, "frontier": frontier}


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Phase 02 — MLE Training  (device={device})")
    print(f"Source: {SRC}")

    df = pd.read_parquet(SRC)
    # Filter usable: Lane N/R/D/X (not M), valid technique
    df = df[df["lane"] != "M"].copy()
    df["payload_delex"] = df["payload_delex"].fillna("").astype(str)
    df = df[df["payload_delex"].str.len() > 5]
    print(f"Training rows: {len(df):,}")

    # Build tokenizer on all data (then split)
    tokenizer = Tokenizer(df["payload_delex"].tolist())
    print(f"Vocab size: {tokenizer.vocab_size}")

    # 90/10 split (stratified by technique)
    from sklearn.model_selection import train_test_split
    df_train, df_val = train_test_split(df, test_size=0.1, random_state=42,
                                        stratify=df["technique_primary"])
    print(f"Train: {len(df_train):,}  Val: {len(df_val):,}")

    all_results = {}
    for seed in SEEDS:
        print(f"\n== Seed {seed} ==")
        result = train_one_seed(seed, df_train, df_val, tokenizer, device)
        all_results[str(seed)] = result

    OUT_E.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_E, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nFrontier saved: {OUT_E}")

    # Summary
    print("\n-- MLE Results Summary --")
    for seed, res in all_results.items():
        best_config = max(res["frontier"].items(),
                          key=lambda x: x[1]["unique_ratio"])
        m = best_config[1]
        print(f"  Seed {seed}: best_unique_ratio={m['unique_ratio']:.3f}  "
              f"self_bleu3={m['self_bleu3']:.3f}  syntax={m['syntax_validity_rate']:.3f}")


if __name__ == "__main__":
    main()
