"""
Phase 02 — Script 5: Mini Gumbel-SeqGAN Challenger
Input : Guiding/Phase 2/slice_labeled.parquet
        Guiding/Phase 2/models/mle_baseline/seed_42/best.pt  (pretrain init)
Output: Guiding/Phase 2/models/gumbel_seqgan/seed_{seed}/
        Guiding/Phase 2/eval/gan_results.json
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
import torch.nn.functional as F
from torch.utils.data import Dataset, DataLoader

HERE   = Path(__file__).parent
SRC    = HERE / "slice_labeled.parquet"
OUT_M  = HERE / "models" / "gumbel_seqgan"
OUT_E  = HERE / "eval" / "gan_results.json"
MLE_PT = HERE / "models" / "mle_baseline" / "seed_42" / "best.pt"

SEEDS      = [42, 123, 456]
MAX_STEPS  = 5000
BATCH_SIZE = 64
LR_G       = 1e-4
LR_D       = 1e-4
D_STEPS    = 5
TAU_START  = 1.0
TAU_END    = 0.1
EMBED_DIM  = 64
HIDDEN_DIM = 256
MAX_LEN    = 64
MIN_FREQ   = 3
GEN_SAMPLES = 1000

TECHNIQUES = ["benign", "boolean_blind", "time_blind", "union_based",
              "error_based", "generic_sqli", "unknown"]

PAD, BOS, EOS, UNK = "<pad>", "<bos>", "<eos>", "<unk>"

# ── Reuse tokenizer from MLE ───────────────────────────────────────────────────
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


# ── Generator ──────────────────────────────────────────────────────────────────
class ConditionalGumbelGenerator(nn.Module):
    def __init__(self, vocab_size: int, n_techniques: int):
        super().__init__()
        self.embedding = nn.Embedding(vocab_size, EMBED_DIM, padding_idx=0)
        self.cond_embed = nn.Embedding(n_techniques, EMBED_DIM)
        self.lstm = nn.LSTM(EMBED_DIM * 2, HIDDEN_DIM, batch_first=True)
        self.fc = nn.Linear(HIDDEN_DIM, vocab_size)
        self.vocab_size = vocab_size

    def forward(self, x: torch.Tensor, cond: torch.Tensor, tau: float = 1.0, hard: bool = False):
        emb = self.embedding(x)
        c = self.cond_embed(cond).unsqueeze(1).expand(-1, x.size(1), -1)
        inp = torch.cat([emb, c], dim=-1)
        out, _ = self.lstm(inp)
        logits = self.fc(out)
        # Gumbel-softmax
        soft = F.gumbel_softmax(logits, tau=tau, hard=False, dim=-1)
        return soft  # [B, T, V]

    def generate_soft(self, cond: torch.Tensor, max_len: int, tau: float, device):
        B = cond.size(0)
        ids = torch.full((B, 1), fill_value=1, dtype=torch.long, device=device)  # BOS=1
        soft_outputs = []
        hidden = None
        for _ in range(max_len):
            emb = self.embedding(ids[:, -1:])
            c = self.cond_embed(cond).unsqueeze(1)
            inp = torch.cat([emb, c], dim=-1)
            out, hidden = self.lstm(inp, hidden)
            logits = self.fc(out)
            soft = F.gumbel_softmax(logits, tau=tau, hard=False, dim=-1)
            soft_outputs.append(soft)
            # argmax for next input (soft path)
            ids_next = soft.argmax(dim=-1)
            ids = torch.cat([ids, ids_next], dim=1)
        return torch.cat(soft_outputs, dim=1)  # [B, max_len, V]


# ── Discriminator ──────────────────────────────────────────────────────────────
class Discriminator(nn.Module):
    """Accepts embedding representations (compatible with soft tokens)."""
    def __init__(self, embed_dim: int, hidden_dim: int):
        super().__init__()
        self.lstm = nn.LSTM(embed_dim, hidden_dim, batch_first=True, bidirectional=True)
        self.fc = nn.Sequential(
            nn.Linear(hidden_dim * 2, 128),
            nn.ReLU(),
            nn.Linear(128, 1),
        )

    def forward(self, emb: torch.Tensor) -> torch.Tensor:
        # emb: [B, T, E]
        out, (h, _) = self.lstm(emb)
        h = torch.cat([h[-2], h[-1]], dim=-1)  # bidirectional last hidden
        return self.fc(h).squeeze(-1)  # [B]


# ── Technique classifier (for consistency loss) ────────────────────────────────
class TechniqueClassifier(nn.Module):
    def __init__(self, embed_dim: int, n_techniques: int):
        super().__init__()
        self.lstm = nn.LSTM(embed_dim, 128, batch_first=True)
        self.fc = nn.Linear(128, n_techniques)

    def forward(self, emb: torch.Tensor) -> torch.Tensor:
        _, (h, _) = self.lstm(emb)
        return self.fc(h.squeeze(0))  # [B, n_tech]


# ── D Shortcut Diagnostic ──────────────────────────────────────────────────────
def d_shortcut_diagnostic(D: Discriminator, embed_matrix: nn.Embedding,
                           real_ids: torch.Tensor, device) -> dict:
    D.eval()
    with torch.no_grad():
        real_emb = embed_matrix(real_ids)
        d_real = torch.sigmoid(D(real_emb)).mean().item()

        # Softened real: add small noise to embedding
        noise = torch.randn_like(real_emb) * 0.1
        d_softened = torch.sigmoid(D(real_emb + noise)).mean().item()

        # Noisy real: more noise
        noise2 = torch.randn_like(real_emb) * 0.5
        d_noisy = torch.sigmoid(D(real_emb + noise2)).mean().item()

    delta = abs(d_real - d_softened)
    shortcut_detected = delta > 0.3
    return {
        "D_real": d_real,
        "D_softened": d_softened,
        "D_noisy": d_noisy,
        "delta_D_real_softened": delta,
        "shortcut_detected": shortcut_detected,
    }


# ── Metrics ───────────────────────────────────────────────────────────────────
RE_SQL = __import__("re").compile(
    r"\b(SELECT|UNION|FROM|WHERE|INSERT|UPDATE|DELETE|DROP|EXEC|ALTER|CREATE)\b",
    __import__("re").IGNORECASE,
)

def compute_metrics(samples: list[str]) -> dict:
    if not samples:
        return {"unique_ratio": 0, "self_bleu3": 0, "token_entropy": 0,
                "syntax_validity_rate": 0, "n_total": 0}
    unique = list(set(samples))
    counter: Counter = Counter()
    for s in samples:
        counter.update(s.split())
    total = sum(counter.values())
    entropy = float(-sum((c / total) * math.log2(c / total)
                         for c in counter.values())) if total else 0.0
    syntax = sum(1 for s in samples if RE_SQL.search(s)) / len(samples)

    # Self-BLEU-3 (sampled)
    def _sb3():
        if len(samples) < 2:
            return 0.0
        scores = []
        indices = random.sample(range(len(samples)), min(200, len(samples)))
        pairs = [(indices[i], indices[j])
                 for i in range(len(indices)) for j in range(i+1, len(indices))]
        for a, b in random.sample(pairs, min(300, len(pairs))):
            ref = samples[a].split()
            hyp = samples[b].split()
            if len(ref) < 3 or not hyp:
                continue
            ng_ref = Counter(zip(*[ref[k:] for k in range(3)]))
            ng_hyp = Counter(zip(*[hyp[k:] for k in range(3)]))
            match = sum(min(ng_ref[g], ng_hyp[g]) for g in ng_hyp)
            tot = sum(ng_hyp.values())
            scores.append(match / tot if tot else 0.0)
        return float(np.mean(scores)) if scores else 0.0

    return {
        "n_total": len(samples),
        "unique_ratio": len(unique) / len(samples),
        "self_bleu3": _sb3(),
        "token_entropy": entropy,
        "syntax_validity_rate": syntax,
    }


# ── Training ───────────────────────────────────────────────────────────────────
def tau_schedule(step: int, max_steps: int) -> float:
    ratio = step / max(max_steps, 1)
    return TAU_START + (TAU_END - TAU_START) * ratio


def set_seed(seed: int):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)


def train_one_seed(seed: int, df: pd.DataFrame, tokenizer: Tokenizer, device) -> dict:
    set_seed(seed)
    out_dir = OUT_M / f"seed_{seed}"
    out_dir.mkdir(parents=True, exist_ok=True)

    n_tech = len(TECHNIQUES)
    technique2id = {t: i for i, t in enumerate(TECHNIQUES)}

    ds = PayloadDataset(df, tokenizer)
    dl = DataLoader(ds, batch_size=BATCH_SIZE, shuffle=True,
                    collate_fn=lambda b: collate_fn(b, tokenizer.pad_id))

    G = ConditionalGumbelGenerator(tokenizer.vocab_size, n_tech).to(device)
    D = Discriminator(EMBED_DIM, HIDDEN_DIM).to(device)
    C = TechniqueClassifier(EMBED_DIM, n_tech).to(device)

    # Initialize G weights from MLE if available
    if MLE_PT.exists():
        mle_state = torch.load(MLE_PT, map_location=device)
        # Load matching keys only
        g_state = G.state_dict()
        matched = {k: v for k, v in mle_state.items() if k in g_state and g_state[k].shape == v.shape}
        g_state.update(matched)
        G.load_state_dict(g_state)
        print(f"  Loaded {len(matched)}/{len(g_state)} keys from MLE checkpoint")

    opt_G = torch.optim.Adam(G.parameters(), lr=LR_G)
    opt_D = torch.optim.Adam(D.parameters(), lr=LR_D)
    opt_C = torch.optim.Adam(C.parameters(), lr=LR_D)

    data_iter = iter(dl)
    step = 0
    collapse_detected = False
    log = []

    while step < MAX_STEPS:
        # ── Train D ──
        for _ in range(D_STEPS):
            try:
                real_ids, cond = next(data_iter)
            except StopIteration:
                data_iter = iter(dl)
                real_ids, cond = next(data_iter)
            real_ids, cond = real_ids.to(device), cond.to(device)

            tau = tau_schedule(step, MAX_STEPS)
            fake_soft = G.generate_soft(cond, real_ids.size(1) - 1, tau, device)

            real_emb = G.embedding(real_ids[:, 1:])   # skip BOS
            fake_emb = fake_soft @ G.embedding.weight  # soft embedding

            # Pad to same length
            T = min(real_emb.size(1), fake_emb.size(1))
            real_emb = real_emb[:, :T, :]
            fake_emb = fake_emb[:, :T, :]

            D_real = D(real_emb.detach())
            D_fake = D(fake_emb.detach())

            loss_D = F.binary_cross_entropy_with_logits(
                D_real, torch.ones_like(D_real)) + \
                F.binary_cross_entropy_with_logits(
                D_fake, torch.zeros_like(D_fake))

            opt_D.zero_grad()
            loss_D.backward()
            opt_D.step()

        # ── Train G ──
        try:
            real_ids, cond = next(data_iter)
        except StopIteration:
            data_iter = iter(dl)
            real_ids, cond = next(data_iter)
        real_ids, cond = real_ids.to(device), cond.to(device)

        tau = tau_schedule(step, MAX_STEPS)
        fake_soft = G.generate_soft(cond, MAX_LEN, tau, device)
        fake_emb = fake_soft @ G.embedding.weight

        D_fake = D(fake_emb[:, :MAX_LEN, :])
        loss_adv = F.binary_cross_entropy_with_logits(D_fake, torch.ones_like(D_fake))

        # Consistency loss: fake_soft → soft_embedding → classifier → CE
        C_logits = C(fake_emb[:, :MAX_LEN, :])
        loss_consist = F.cross_entropy(C_logits, cond)

        loss_G = loss_adv + 0.5 * loss_consist

        opt_G.zero_grad()
        opt_C.zero_grad()
        loss_G.backward()
        nn.utils.clip_grad_norm_(G.parameters(), 1.0)
        opt_G.step()
        opt_C.step()

        step += 1

        if step % 500 == 0:
            # Generate samples for monitoring
            G.eval()
            with torch.no_grad():
                mon_cond = torch.zeros(50, dtype=torch.long, device=device)
                soft = G.generate_soft(mon_cond, MAX_LEN, tau, device)
                ids = soft.argmax(dim=-1).cpu().tolist()
                samples = [tokenizer.decode(row) for row in ids]
            G.train()
            ur = len(set(samples)) / max(len(samples), 1)
            print(f"  Seed {seed} Step {step:4d}: D={loss_D.item():.4f} G={loss_G.item():.4f} "
                  f"tau={tau:.3f} unique_ratio={ur:.3f}")
            log.append({"step": step, "unique_ratio": ur, "tau": tau})

            if ur < 0.1 and step > 1000:
                print(f"  Collapse detected at step {step}! Stopping.")
                collapse_detected = True
                break

    # Save checkpoint
    torch.save({"G": G.state_dict(), "D": D.state_dict()}, out_dir / "checkpoint.pt")

    # Generate final eval samples
    G.eval()
    all_samples = []
    with torch.no_grad():
        for tech_id in range(n_tech - 1):
            cond = torch.full((GEN_SAMPLES // (n_tech - 1),), tech_id,
                              dtype=torch.long, device=device)
            soft = G.generate_soft(cond, MAX_LEN, TAU_END, device)
            ids = soft.argmax(dim=-1).cpu().tolist()
            all_samples += [tokenizer.decode(row) for row in ids]

    metrics = compute_metrics(all_samples)

    # D shortcut diagnostic on a real batch
    try:
        real_ids_diag, _ = next(iter(dl))
        real_ids_diag = real_ids_diag[:32, 1:].to(device)
        shortcut = d_shortcut_diagnostic(D, G.embedding, real_ids_diag, device)
    except Exception as e:
        shortcut = {"error": str(e)}

    return {
        "collapse_detected": collapse_detected,
        "metrics": metrics,
        "d_shortcut": shortcut,
        "training_log": log,
    }


def main():
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"Phase 02 — Gumbel-SeqGAN  (device={device})")

    df = pd.read_parquet(SRC)
    df = df[df["lane"] != "M"].copy()
    df["payload_delex"] = df["payload_delex"].fillna("").astype(str)
    df = df[df["payload_delex"].str.len() > 5]
    print(f"Training rows: {len(df):,}")

    tokenizer = Tokenizer(df["payload_delex"].tolist())
    print(f"Vocab size: {tokenizer.vocab_size}")

    all_results = {}
    for seed in SEEDS:
        print(f"\n== Seed {seed} ==")
        result = train_one_seed(seed, df, tokenizer, device)
        all_results[str(seed)] = result

    OUT_E.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_E, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2)
    print(f"\nGAN results saved: {OUT_E}")

    print("\n-- GAN Results Summary --")
    for seed, res in all_results.items():
        m = res["metrics"]
        sc = res.get("d_shortcut", {})
        print(f"  Seed {seed}: unique={m.get('unique_ratio', 0):.3f}  "
              f"bleu3={m.get('self_bleu3', 0):.3f}  "
              f"syntax={m.get('syntax_validity_rate', 0):.3f}  "
              f"delta_D={sc.get('delta_D_real_softened', '?')}")


if __name__ == "__main__":
    main()
