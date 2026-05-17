"""
train_adversarial_v4.py — V4 Anti-Collapse SeqGAN

V3 vẫn collapse sau step 2500 do:
  - entropy_coeff_adversarial quá yếu (0.03)
  - temperature_adversarial=1.1 không đủ thoát local optimum
  - EMA baseline alpha=0.05 quá chậm → advantage→0 khi collapse
  - 88.6% Oracle XMLTYPE bias → type collapse

V4 fixes (6 layers):
  Fix-1: entropy_coeff_adversarial = 0.10 (3.3x mạnh hơn)
  Fix-2: temperature_adversarial = 1.30 (thoát peaked policy)
  Fix-3: ema_baseline_alpha = 0.20 (4x faster, advantage không→0)
  Fix-4: type-balanced batch sampling (force diversity across 14 types)
  Fix-5: diversity_bonus reward (jaccard novelty vs recent 256 payloads)
  Fix-6: dynamic D steps (giảm khi G collapse, tránh D dominance)
  Fix-7: benign SQL data cho Discriminator (teacher request)
  Fix-8: GeneratorBiLSTMEncoder (teacher request: "3LSTM, BBI")
"""
import argparse
import json
import random
import re
import sys
from collections import deque
from itertools import cycle
from pathlib import Path

import numpy as np
import pandas as pd
import torch
import torch.nn.functional as F
import yaml

sys.path.insert(0, str(Path(__file__).parent))

from src.discriminator import DiscriminatorCNN
from src.generator import GeneratorLSTM, GeneratorBiLSTMEncoder
from src.losses import reinforce_loss_with_entropy, wgan_gp_loss
from src.reward_v2 import CompositeRewardV2
from src.tokenizer import SQLTokenizer
from src.utils import set_seed, pad_sequences, save_checkpoint, load_checkpoint, get_device

try:
    from torch.utils.tensorboard import SummaryWriter
    HAS_TB = True
except ImportError:
    HAS_TB = False


# ── Data Loading ─────────────────────────────────────────────────────────────

def load_tokenizer(path: str) -> SQLTokenizer:
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    vocab = data.get("token2id", data)
    return SQLTokenizer(vocab)


def load_relex_dict(path: str) -> dict:
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def relex(payload: str, relex_dict: dict) -> str:
    if not relex_dict:
        return payload

    def replace(match):
        key = match.group(0)
        choices = relex_dict.get(key)
        return random.choice(choices) if choices else key

    return re.sub(r"__\w+__", replace, payload)


class V4Dataset(torch.utils.data.Dataset):
    """Attack payload dataset with per-row type_id.
    Supports stratified sampling for type-balanced batches (Fix-4).
    """
    def __init__(self, csv_path: str, tokenizer: SQLTokenizer, max_len: int = 80):
        df = pd.read_csv(csv_path)
        payload_col = next(
            (c for c in ["payload_delex", "payload_norm", "payload"] if c in df.columns),
            df.columns[0],
        )
        if "tier" in df.columns:
            df = df[df["tier"].isin(["gold", "silver"])].copy()
        self.seqs = [
            tokenizer.encode(row, add_sos=True, add_eos=True)[:max_len + 2]
            for row in df[payload_col].fillna("").astype(str).tolist()
        ]
        self.type_ids = (
            df["type_id"].fillna(0).astype(int).tolist()
            if "type_id" in df.columns
            else [0] * len(df)
        )
        # Build type → indices map for stratified sampling
        self.type_to_indices: dict[int, list] = {}
        for i, t in enumerate(self.type_ids):
            self.type_to_indices.setdefault(t, []).append(i)

    def __len__(self):
        return len(self.seqs)

    def __getitem__(self, idx):
        return self.seqs[idx], self.type_ids[idx]

    def stratified_sample(self, n: int) -> list:
        """Return n indices sampled equally from all available types."""
        types = list(self.type_to_indices.keys())
        n_types = len(types)
        per_type = max(1, n // n_types)
        indices = []
        for t in types:
            pool = self.type_to_indices[t]
            sampled = random.choices(pool, k=per_type)
            indices.extend(sampled)
        # Trim or pad to exactly n
        random.shuffle(indices)
        if len(indices) >= n:
            return indices[:n]
        # Pad by cycling
        while len(indices) < n:
            indices.append(random.choice(indices))
        return indices[:n]


class BenignDataset(torch.utils.data.Dataset):
    """Benign SQL queries for Discriminator negative class (Fix-7)."""
    def __init__(self, csv_path: str, tokenizer: SQLTokenizer, max_len: int = 80):
        try:
            df = pd.read_csv(csv_path)
            payload_col = next(
                (c for c in ["payload_norm", "payload", "query"] if c in df.columns),
                df.columns[0],
            )
            self.seqs = [
                tokenizer.encode(row, add_sos=True, add_eos=True)[:max_len + 2]
                for row in df[payload_col].fillna("").astype(str).tolist()
            ]
        except Exception as e:
            print(f"  WARNING: benign data not loaded ({e}) — proceeding without")
            self.seqs = []

    def __len__(self):
        return len(self.seqs)

    def __getitem__(self, idx):
        return self.seqs[idx], 0  # type_id=0 (benign)


def collate_fn(batch, pad_id: int):
    seqs = [b[0] for b in batch]
    type_ids = torch.tensor([b[1] for b in batch], dtype=torch.long)
    return pad_sequences(seqs, pad_id), type_ids


def decode_batch(token_ids: torch.Tensor, tokenizer: SQLTokenizer) -> list:
    payloads = []
    for row in token_ids.cpu().tolist():
        tokens = [t for t in row if t not in (tokenizer.pad_id, tokenizer.sos_id, tokenizer.eos_id)]
        if tokenizer.eos_id in row:
            eos_pos = row.index(tokenizer.eos_id)
            tokens = [t for t in row[:eos_pos] if t not in (tokenizer.pad_id, tokenizer.sos_id)]
        payloads.append(tokenizer.decode(tokens))
    return payloads


# ── Phase Management ─────────────────────────────────────────────────────────

def determine_phase(step: int, cfg: dict) -> str:
    warmup_end = cfg.get("warmup_steps", 2000)
    adv_end = warmup_end + cfg.get("adversarial_steps", 12000)
    if step < warmup_end:
        return "warmup"
    elif step < adv_end:
        return "adversarial"
    else:
        return "refinement"


def get_phase_params(phase: str, cfg: dict) -> tuple:
    """Returns (entropy_coeff, temperature, lr_g)."""
    entropy_coeff = cfg.get(f"entropy_coeff_{phase}", 0.03)
    temperature = cfg.get(f"sample_temperature_{phase}", 1.0)
    lr_g = cfg[f"lr_g_{phase}"]
    return entropy_coeff, temperature, lr_g


# ── Anti-Collapse: Diversity Bonus (Fix-5) ───────────────────────────────────

def _char_trigrams(text: str) -> set:
    return set(text[i:i+3] for i in range(max(0, len(text) - 2)))


def compute_diversity_bonus(payloads: list, recent_buffer: deque) -> np.ndarray:
    """Jaccard novelty vs recent 256 unique payloads.
    Returns array in [0, 1]; higher = more novel = higher reward.
    """
    if not recent_buffer:
        return np.ones(len(payloads), dtype=np.float32)

    buf_trigrams = [_char_trigrams(b) for b in recent_buffer]
    bonuses = []
    for p in payloads:
        p_trig = _char_trigrams(p)
        if not p_trig:
            bonuses.append(0.0)
            continue
        max_sim = max(
            len(p_trig & bt) / max(len(p_trig | bt), 1)
            for bt in buf_trigrams
        )
        bonuses.append(1.0 - max_sim)
    return np.array(bonuses, dtype=np.float32)


def update_diversity_buffer(
    payloads: list, buffer: deque, seen_set: set, maxsize: int = 256
) -> None:
    for p in payloads:
        if p and p not in seen_set:
            buffer.append(p)
            seen_set.add(p)
    # Keep buffer bounded (deque maxlen handles this but seen_set grows)
    # Prune seen_set to stay in sync with buffer
    if len(seen_set) > maxsize * 2:
        # Remove oldest entries not in buffer
        current = set(buffer)
        seen_set.intersection_update(current)


# ── Health Monitor ────────────────────────────────────────────────────────────

def check_health(step, unique_per_batch, adv_std, entropy_val,
                 cfg, writer=None) -> list:
    """Log warnings for collapse indicators. Returns list of triggered flags."""
    flags = []
    if unique_per_batch < cfg.get("health_unique_min", 10):
        flags.append(f"COLLAPSE_UNIQUE (unique={unique_per_batch})")
    if adv_std < cfg.get("health_adv_std_min", 0.05):
        flags.append(f"COLLAPSE_ADVANTAGE (std={adv_std:.4f})")
    if entropy_val < cfg.get("health_entropy_min", 1.5):
        flags.append(f"COLLAPSE_ENTROPY (H={entropy_val:.3f})")
    if flags:
        print(f"  [HEALTH] [{step}]: {' | '.join(flags)}")
    if writer:
        writer.add_scalar("v4/health_unique", unique_per_batch, step)
        writer.add_scalar("v4/health_adv_std", adv_std, step)
        writer.add_scalar("v4/health_entropy", entropy_val, step)
    return flags


# ── Sample with Logits (same as V3) ──────────────────────────────────────────

def sample_with_logits(gen, B: int, max_len: int, device, tok, cond, temperature: float):
    """Sample from generator collecting logits for entropy computation.
    Returns (token_ids, log_probs, logits) — (B,T), (B,T), (B,T,V).
    """
    hidden = gen.init_hidden(B, device)
    token = torch.full((B, 1), tok.sos_id, dtype=torch.long, device=device)
    tokens_list, logprob_list, logits_list = [], [], []
    finished = torch.zeros(B, dtype=torch.bool, device=device)

    for _ in range(max_len):
        step_logits_full, hidden = gen.forward(token, hidden, cond)
        step_logits = step_logits_full[:, -1, :]  # (B, V) unscaled

        scaled = step_logits / max(temperature, 1e-6)
        probs = torch.softmax(scaled, dim=-1)
        next_token = torch.multinomial(probs, 1)
        step_log_prob = torch.log_softmax(scaled, dim=-1).gather(1, next_token).squeeze(1)

        step_log_prob = step_log_prob.masked_fill(finished, 0.0)
        next_token_stored = next_token.masked_fill(finished.unsqueeze(1), tok.pad_id)

        tokens_list.append(next_token_stored)
        logprob_list.append(step_log_prob)
        logits_list.append(step_logits)

        finished = finished | (next_token.squeeze(1) == tok.eos_id)
        token = next_token_stored

        if finished.all():
            break

    token_ids = torch.cat(tokens_list, dim=1)
    log_probs = torch.stack(logprob_list, dim=1)
    logits = torch.stack(logits_list, dim=1)
    return token_ids, log_probs, logits


# ── Main Training Loop ────────────────────────────────────────────────────────

def train(cfg: dict, args):
    set_seed(cfg["seed"])
    device = get_device()
    print(f"Device: {device}")

    data_dir = Path(cfg["data_dir"])
    ckpt_dir = Path(cfg["ckpt_dir"])
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    log_dir = Path(cfg.get("log_dir", "SeqGAN_SQLi/logs/v4"))

    tok = load_tokenizer(str(data_dir / "tokenizer_vocab.json"))
    print(f"Vocab size: {tok.vocab_size}")

    num_attack_types = cfg.get("num_attack_types", 14)
    type_embed_dim = cfg.get("type_embed_dim", 64)

    # ── Build Generator (Fix-8: BiLSTM or LSTM) ──────────────────────────────
    use_bilstm = cfg.get("use_bilstm", True)
    if use_bilstm:
        gen = GeneratorBiLSTMEncoder(
            vocab_size=tok.vocab_size,
            embed_dim=cfg["embed_dim"],
            hidden_dim=cfg["hidden_dim"],
            enc_layers=cfg.get("enc_layers", 2),
            dec_layers=cfg.get("num_layers", 2),
            dropout=cfg["dropout"],
            num_conditions=num_attack_types,
            cond_embed_dim=type_embed_dim,
        ).to(device)
        print("Generator: BiLSTMEncoder (teacher request)")
    else:
        gen = GeneratorLSTM(
            vocab_size=tok.vocab_size,
            embed_dim=cfg["embed_dim"],
            hidden_dim=cfg["hidden_dim"],
            num_layers=cfg["num_layers"],
            dropout=cfg["dropout"],
            num_conditions=num_attack_types,
            cond_embed_dim=type_embed_dim,
        ).to(device)
        print("Generator: LSTM (fallback)")

    disc = DiscriminatorCNN(
        vocab_size=tok.vocab_size,
        embed_dim=cfg["d_embed_dim"],
        kernel_sizes=cfg["d_kernel_sizes"],
        num_filters=cfg["d_filters"],
        num_conditions=num_attack_types,
        cond_embed_dim=type_embed_dim,
    ).to(device)

    # ── Load MLE checkpoint ───────────────────────────────────────────────────
    mle_ckpt_candidates = [
        ckpt_dir / "mle_best.pt",
        data_dir.parent.parent / "SeqGAN_SQLi" / "checkpoints" / "v2" / "mle_best.pt",
        Path("SeqGAN_SQLi/checkpoints/v2/mle_best.pt"),
        Path("checkpoints/v2/mle_best.pt"),
    ]
    for mle_ckpt in mle_ckpt_candidates:
        if mle_ckpt.exists():
            try:
                _, metrics = load_checkpoint(str(mle_ckpt), gen)
                print(f"Loaded MLE checkpoint (val_ppl={metrics.get('val_ppl', '?')})")
            except Exception as e:
                print(f"MLE checkpoint shape mismatch ({e}) — training from scratch")
            break
    else:
        print("WARNING: MLE checkpoint not found — starting from random init")

    entropy_coeff, temperature, lr_g_init = get_phase_params("warmup", cfg)
    opt_g = torch.optim.Adam(gen.parameters(), lr=lr_g_init,
                              betas=(cfg["beta1"], cfg["beta2"]))
    opt_d = torch.optim.Adam(disc.parameters(), lr=cfg["lr_d"],
                              betas=(cfg["beta1"], cfg["beta2"]))

    # ── Dataset (Fix-4: type-balanced) ───────────────────────────────────────
    type_balanced = cfg.get("type_balanced_sampling", True)
    pad_fn = lambda b: collate_fn(b, tok.pad_id)

    train_ds = V4Dataset(str(data_dir / "train.csv"), tok, cfg["max_seq_len"])
    print(f"Train dataset: {len(train_ds)} rows, {len(train_ds.type_to_indices)} types")

    if type_balanced:
        print("Fix-4: Type-balanced sampling enabled")
        train_loader = torch.utils.data.DataLoader(
            train_ds, batch_size=cfg["batch_size"], shuffle=True,
            collate_fn=pad_fn, drop_last=True,
        )
    else:
        train_loader = torch.utils.data.DataLoader(
            train_ds, batch_size=cfg["batch_size"], shuffle=True,
            collate_fn=pad_fn, drop_last=True,
        )
    data_iter = iter(train_loader)

    def next_batch_balanced():
        """Type-balanced batch: equal representation from all attack types."""
        indices = train_ds.stratified_sample(cfg["batch_size"])
        batch = [train_ds[i] for i in indices]
        return collate_fn(batch, tok.pad_id)

    def next_batch():
        nonlocal data_iter
        try:
            return next(data_iter)
        except StopIteration:
            data_iter = iter(train_loader)
            return next(data_iter)

    get_batch = next_batch_balanced if type_balanced else next_batch

    # ── Benign dataset (Fix-7) ────────────────────────────────────────────────
    use_benign = cfg.get("use_benign_data", False)
    benign_loader_iter = None
    benign_batch_frac = cfg.get("benign_batch_fraction", 0.25)
    benign_B = max(1, int(cfg["batch_size"] * benign_batch_frac))
    if use_benign:
        benign_path = cfg.get("benign_data_path", "SeqGAN_SQLi/data/benign_sql.csv")
        benign_ds = BenignDataset(benign_path, tok, cfg["max_seq_len"])
        if len(benign_ds) > 0:
            benign_loader = torch.utils.data.DataLoader(
                benign_ds, batch_size=benign_B, shuffle=True,
                collate_fn=pad_fn, drop_last=True,
            )
            benign_loader_iter = cycle(benign_loader)
            print(f"Fix-7: Benign data loaded: {len(benign_ds)} rows, {benign_B}/batch")
        else:
            use_benign = False
            print("Fix-7: Benign data empty — proceeding without")

    # ── Relex dict ────────────────────────────────────────────────────────────
    relex_dict_path = cfg.get("relex_dict_path", "SeqGAN_SQLi/data/relex_dictionary.json")
    relex_dict = load_relex_dict(relex_dict_path)
    print(f"Re-lex dict: {'loaded' if relex_dict else 'not found (using raw delex)'}")

    # ── Reward ────────────────────────────────────────────────────────────────
    reward_fn = CompositeRewardV2(
        phase="warmup",
        waf_url=cfg.get("waf_url", "http://localhost:8080"),
        boundary_threshold=cfg.get("boundary_threshold", 5),
        use_waf=False,
        cache_size=cfg.get("cache_size", 100000),
    )

    # ── TensorBoard ───────────────────────────────────────────────────────────
    writer = None
    if HAS_TB:
        log_dir.mkdir(parents=True, exist_ok=True)
        writer = SummaryWriter(str(log_dir / "adversarial_v4"))

    # ── Training state ────────────────────────────────────────────────────────
    total_steps = (
        cfg.get("warmup_steps", 2000)
        + cfg.get("adversarial_steps", 12000)
        + cfg.get("refinement_steps", 6000)
    )
    current_phase = "warmup"
    entropy_coeff = cfg.get("entropy_coeff_warmup", 0.05)
    temperature = cfg.get("sample_temperature_warmup", 1.20)
    gp_lambda = 10.0

    # Fix-3: EMA baseline with faster alpha
    ema_alpha = cfg.get("ema_baseline_alpha", 0.20)
    reward_ema = 0.0
    ema_initialized = False

    # Fix-5: Diversity buffer
    div_weight = cfg.get("diversity_weight", 0.15)
    buf_maxsize = cfg.get("diversity_buffer_size", 256)
    recent_buffer = deque(maxlen=buf_maxsize)
    seen_set: set = set()

    # Fix-6: Dynamic D steps thresholds
    d_collapse_thr = cfg.get("d_steps_collapse_threshold", 8)
    d_warning_thr = cfg.get("d_steps_warning_threshold", 20)
    d_per_g_base = cfg.get("d_per_g_ratio", 3)

    print(f"\nV4 config:")
    print(f"  entropy: warmup={cfg.get('entropy_coeff_warmup')} adv={cfg.get('entropy_coeff_adversarial')} ref={cfg.get('entropy_coeff_refinement')}")
    print(f"  temperature: warmup={cfg.get('sample_temperature_warmup')} adv={cfg.get('sample_temperature_adversarial')} ref={cfg.get('sample_temperature_refinement')}")
    print(f"  ema_alpha={ema_alpha}  div_weight={div_weight}  d_per_g_base={d_per_g_base}")
    print(f"  total_steps={total_steps}  use_bilstm={use_bilstm}")

    for step in range(1, total_steps + 1):
        if args.steps and step > args.steps:
            break

        # ── Phase transition ──────────────────────────────────────────────────
        new_phase = determine_phase(step, cfg)
        if new_phase != current_phase:
            current_phase = new_phase
            reward_fn.set_phase(current_phase)
            entropy_coeff, temperature, new_lr = get_phase_params(current_phase, cfg)

            if current_phase == "adversarial" and not reward_fn.use_waf:
                use_waf = cfg.get("use_waf", True) and not args.no_waf
                if use_waf:
                    try:
                        from src.waf_oracle import WAFOracle
                        reward_fn.waf = WAFOracle(url=cfg.get("waf_url", "http://localhost:8080"))
                        reward_fn.use_waf = True
                        print(f"  WAF enabled at step {step}")
                    except Exception as e:
                        print(f"  WAF init failed: {e} — continuing without WAF")

            for pg in opt_g.param_groups:
                pg["lr"] = new_lr
            print(f"\n[Step {step}] Phase -> {current_phase} | lr_g={new_lr} | "
                  f"entropy={entropy_coeff:.3f} | temp={temperature:.2f}")

        if current_phase == "refinement" and step % 1000 == 0:
            reward_fn.reset_ast_cache()

        # Fix-4: Type-balanced batch
        real_batch, real_types = get_batch()
        real_batch = real_batch.to(device)
        real_types = real_types.to(device)
        B = real_batch.size(0)

        real_inp = real_batch[:, 1:]  # strip SOS
        T_real = real_inp.size(1)

        # ── Fix-6: Dynamic D steps ────────────────────────────────────────────
        # Will be computed after we have unique_per_batch from last step.
        # For first step, use base ratio.
        # We compute it before D update using a quick no-grad sample.
        with torch.no_grad():
            probe_seqs, _, _ = sample_with_logits(
                gen, B, cfg["max_seq_len"], device, tok, real_types, temperature=temperature
            )
        probe_payloads = decode_batch(probe_seqs, tok)
        unique_per_batch = len(set(probe_payloads))

        if unique_per_batch < d_collapse_thr:
            effective_d_steps = 1
        elif unique_per_batch < d_warning_thr:
            effective_d_steps = 2
        else:
            effective_d_steps = d_per_g_base

        # ── Discriminator update ──────────────────────────────────────────────
        for _ in range(effective_d_steps):
            with torch.no_grad():
                fake_seqs_d, _, _ = sample_with_logits(
                    gen, B, cfg["max_seq_len"], device, tok, real_types, temperature=1.0
                )

            fake_inp = fake_seqs_d[:, :T_real]
            if fake_inp.size(1) < T_real:
                pad = torch.full((B, T_real - fake_inp.size(1)), tok.pad_id,
                                 dtype=torch.long, device=device)
                fake_inp = torch.cat([fake_inp, pad], dim=1)

            # Fix-7: Add benign data to fake pile
            if use_benign and benign_loader_iter is not None:
                benign_batch, _ = next(benign_loader_iter)
                benign_batch = benign_batch.to(device)
                benign_inp = benign_batch[:, 1:]  # strip SOS
                if benign_inp.size(1) > T_real:
                    benign_inp = benign_inp[:, :T_real]
                elif benign_inp.size(1) < T_real:
                    pad_b = torch.full(
                        (benign_inp.size(0), T_real - benign_inp.size(1)),
                        tok.pad_id, dtype=torch.long, device=device,
                    )
                    benign_inp = torch.cat([benign_inp, pad_b], dim=1)
                # WGAN: real_attack = high score; [fake_generated + benign] = low score
                d_real = disc(real_inp, cond=real_types)
                d_fake = disc(fake_inp.detach(), cond=real_types)
                d_benign = disc(benign_inp.detach(),
                                cond=torch.zeros(benign_inp.size(0), dtype=torch.long, device=device))
                d_loss_fake = -d_real.mean() + d_fake.mean() + 0.5 * d_benign.mean()
                gp = disc.gradient_penalty(real_inp, fake_inp.detach(),
                                           gp_lambda=gp_lambda, cond=real_types)
                d_loss = d_loss_fake + gp
            else:
                d_real = disc(real_inp, cond=real_types)
                d_fake = disc(fake_inp.detach(), cond=real_types)
                gp = disc.gradient_penalty(real_inp, fake_inp.detach(),
                                           gp_lambda=gp_lambda, cond=real_types)
                d_loss = wgan_gp_loss(d_real, d_fake, gp)

            opt_d.zero_grad()
            d_loss.backward()
            torch.nn.utils.clip_grad_norm_(disc.parameters(), cfg["grad_clip"])
            opt_d.step()

        # ── Generator update (REINFORCE + entropy) ────────────────────────────
        fake_seqs, log_probs, logits = sample_with_logits(
            gen, B, cfg["max_seq_len"], device, tok, real_types, temperature=temperature
        )

        with torch.no_grad():
            raw_payloads = decode_batch(fake_seqs, tok)
            payloads = [relex(p, relex_dict) for p in raw_payloads]

            oracle_rewards = torch.tensor(
                [reward_fn(p) for p in payloads], dtype=torch.float32, device=device
            )

            fake_inp_g = fake_seqs[:, :T_real]
            if fake_inp_g.size(1) < T_real:
                pad = torch.full((B, T_real - fake_inp_g.size(1)), tok.pad_id,
                                 dtype=torch.long, device=device)
                fake_inp_g = torch.cat([fake_inp_g, pad], dim=1)
            d_score = disc(fake_inp_g, cond=real_types).detach()
            d_score_norm = torch.sigmoid(d_score) * 0.2

            # Fix-5: Diversity bonus
            div_bonuses = compute_diversity_bonus(raw_payloads, recent_buffer)
            div_bonus_t = torch.tensor(div_bonuses, dtype=torch.float32, device=device)

            rewards = oracle_rewards + d_score_norm + div_weight * div_bonus_t

        # Fix-5: Update buffer with unique payloads
        update_diversity_buffer(raw_payloads, recent_buffer, seen_set, buf_maxsize)

        # Fix-3: EMA baseline (faster alpha)
        batch_mean = rewards.mean().item()
        if not ema_initialized:
            reward_ema = batch_mean
            ema_initialized = True
        else:
            reward_ema = ema_alpha * batch_mean + (1 - ema_alpha) * reward_ema

        advantages = rewards - reward_ema

        T = log_probs.size(1)
        pad_mask = (fake_seqs[:, :T] != tok.pad_id)

        # Fix-1: Stronger entropy regularization
        g_loss, pg_loss, entropy_loss = reinforce_loss_with_entropy(
            log_probs, advantages, logits[:, :T, :],
            entropy_coeff=entropy_coeff,
            pad_mask=pad_mask,
        )

        opt_g.zero_grad()
        g_loss.backward()
        torch.nn.utils.clip_grad_norm_(gen.parameters(), cfg["grad_clip"])
        opt_g.step()

        # ── Logging ───────────────────────────────────────────────────────────
        if step % 50 == 0:
            avg_r = oracle_rewards.mean().item()
            adv_std = advantages.std().item()
            n_unique = len(set(raw_payloads))
            # Compute logit entropy for health check
            with torch.no_grad():
                probs = torch.softmax(logits[:, :T, :], dim=-1)
                entropy_val = (-(probs * torch.log(probs + 1e-9)).sum(-1) * pad_mask).sum() / pad_mask.sum()
                entropy_val = entropy_val.item()

            print(
                f"[{step:5d}/{total_steps}] phase={current_phase} "
                f"g={g_loss.item():.4f} pg={pg_loss.item():.4f} "
                f"H={-entropy_loss.item():.3f} "
                f"r={avg_r:.4f} ema={reward_ema:.4f} "
                f"adv_std={adv_std:.4f} unique={n_unique}/{B} "
                f"d_steps={effective_d_steps}"
            )
            check_health(step, n_unique, adv_std, entropy_val, cfg, writer)

            if writer:
                writer.add_scalar("v4/g_loss", g_loss.item(), step)
                writer.add_scalar("v4/pg_loss", pg_loss.item(), step)
                writer.add_scalar("v4/entropy", -entropy_loss.item(), step)
                writer.add_scalar("v4/avg_reward", avg_r, step)
                writer.add_scalar("v4/div_bonus_mean", float(div_bonuses.mean()), step)
                writer.add_scalar("v4/ema_baseline", reward_ema, step)
                writer.add_scalar("v4/adv_std", adv_std, step)
                writer.add_scalar("v4/unique_per_batch", n_unique, step)
                writer.add_scalar("v4/d_loss", d_loss.item(), step)
                writer.add_scalar("v4/d_steps_used", effective_d_steps, step)
                writer.add_scalar("v4/buffer_size", len(recent_buffer), step)

        if step % 1000 == 0:
            ckpt_path = str(ckpt_dir / f"adv_step{step}.pt")
            save_checkpoint(ckpt_path, gen, opt_g, step, {"phase": current_phase})
            print(f"  Checkpoint: {ckpt_path}")
            print(f"  Reward stats: {reward_fn.get_stats()}")
            print(f"  Buffer size: {len(recent_buffer)} unique payloads")

    save_checkpoint(str(ckpt_dir / "adv_final.pt"), gen, opt_g, total_steps,
                    {"phase": current_phase})
    print(f"\nV4 training done. Final: {ckpt_dir}/adv_final.pt")
    if writer:
        writer.close()
    reward_fn.close()


def main():
    parser = argparse.ArgumentParser(description="SeqGAN V4 Anti-Collapse Training")
    parser.add_argument("--config", default="SeqGAN_SQLi/configs/seqgan_v4.yaml")
    parser.add_argument("--steps", type=int, default=None, help="Max steps (smoke test)")
    parser.add_argument("--no_waf", action="store_true", help="Disable WAF Oracle")
    parser.add_argument("--no_bilstm", action="store_true",
                        help="Force GeneratorLSTM (disable BiLSTM encoder)")
    args = parser.parse_args()

    cfg_path = args.config
    if not Path(cfg_path).exists():
        cfg_path = str(Path(__file__).parent / args.config)
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if args.no_waf:
        cfg["use_waf"] = False
        print("WAF disabled (--no_waf)")
    if args.no_bilstm:
        cfg["use_bilstm"] = False
        print("BiLSTM disabled (--no_bilstm) → using GeneratorLSTM")

    train(cfg, args)


if __name__ == "__main__":
    main()
