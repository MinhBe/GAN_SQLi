"""
train_adversarial_v3.py — V3 với 3 fixes chống mode collapse:

  1. Entropy regularization: g_loss = pg_loss - entropy_coeff * H(logits)
     Buộc generator duy trì distribution đa dạng, tránh collapse 1 payload.

  2. EMA baseline: reward_ema = alpha * batch_mean + (1-alpha) * reward_ema
     Cung cấp gradient ngay cả khi tất cả samples trong batch đều có reward cao.

  3. Temperature sampling: temperature > 1.0 trong warmup/adversarial
     Tăng entropy khi sampling để khuyến khích exploration.

Giống V2 về: kiến trúc, reward, data loading, discriminator.
Khác V2:    reinforce_loss_with_entropy(), EMA baseline, temperature.
"""
import argparse
import json
import random
import re
import sys
from pathlib import Path

import pandas as pd
import torch
import torch.nn.functional as F
import yaml

sys.path.insert(0, str(Path(__file__).parent))

from src.discriminator import DiscriminatorCNN
from src.generator import GeneratorLSTM
from src.losses import reinforce_loss_with_entropy, wgan_gp_loss
from src.reward_v2 import CompositeRewardV2
from src.tokenizer import SQLTokenizer
from src.utils import set_seed, pad_sequences, save_checkpoint, load_checkpoint, get_device

try:
    from torch.utils.tensorboard import SummaryWriter
    HAS_TB = True
except ImportError:
    HAS_TB = False


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


class V3Dataset(torch.utils.data.Dataset):
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

    def __len__(self):
        return len(self.seqs)

    def __getitem__(self, idx):
        return self.seqs[idx], self.type_ids[idx]


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


def determine_phase(step: int, cfg: dict) -> str:
    warmup_end = cfg.get("warmup_steps", 2000)
    adv_end = warmup_end + cfg.get("adversarial_steps", 10000)
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


def sample_with_logits(gen, B: int, max_len: int, device, tok, cond, temperature: float):
    """
    Sample from generator collecting logits for entropy computation.
    Uses gen.forward() to respect _merge_cond() logic correctly.
    Returns (token_ids, log_probs, logits) — (B,T), (B,T), (B,T,V).
    """
    hidden = gen.init_hidden(B, device)
    token = torch.full((B, 1), tok.sos_id, dtype=torch.long, device=device)
    tokens_list, logprob_list, logits_list = [], [], []
    finished = torch.zeros(B, dtype=torch.bool, device=device)

    for _ in range(max_len):
        step_logits_full, hidden = gen.forward(token, hidden, cond)  # (B, 1, V)
        step_logits = step_logits_full[:, -1, :]  # (B, V) — unscaled, used for entropy

        scaled = step_logits / max(temperature, 1e-6)
        probs = torch.softmax(scaled, dim=-1)
        next_token = torch.multinomial(probs, 1)  # (B, 1)
        step_log_prob = torch.log_softmax(scaled, dim=-1).gather(1, next_token).squeeze(1)

        step_log_prob = step_log_prob.masked_fill(finished, 0.0)
        next_token_stored = next_token.masked_fill(finished.unsqueeze(1), tok.pad_id)

        tokens_list.append(next_token_stored)
        logprob_list.append(step_log_prob)
        logits_list.append(step_logits)  # unscaled logits for entropy

        finished = finished | (next_token.squeeze(1) == tok.eos_id)
        token = next_token_stored

        if finished.all():
            break

    token_ids = torch.cat(tokens_list, dim=1)      # (B, T)
    log_probs = torch.stack(logprob_list, dim=1)   # (B, T)
    logits = torch.stack(logits_list, dim=1)       # (B, T, V)
    return token_ids, log_probs, logits


def train(cfg: dict, args):
    set_seed(cfg["seed"])
    device = get_device()
    print(f"Device: {device}")

    data_dir = Path(cfg["data_dir"])
    ckpt_dir = Path(cfg["ckpt_dir"])
    ckpt_dir.mkdir(parents=True, exist_ok=True)
    log_dir = Path(cfg.get("log_dir", "SeqGAN_SQLi/logs/v3"))

    tok = load_tokenizer(str(data_dir / "tokenizer_vocab.json"))
    print(f"Vocab size: {tok.vocab_size}")

    num_attack_types = cfg.get("num_attack_types", 4)
    type_embed_dim = cfg.get("type_embed_dim", 32)

    gen = GeneratorLSTM(
        vocab_size=tok.vocab_size,
        embed_dim=cfg["embed_dim"],
        hidden_dim=cfg["hidden_dim"],
        num_layers=cfg["num_layers"],
        dropout=cfg["dropout"],
        num_conditions=num_attack_types,
        cond_embed_dim=type_embed_dim,
    ).to(device)

    disc = DiscriminatorCNN(
        vocab_size=tok.vocab_size,
        embed_dim=cfg["d_embed_dim"],
        kernel_sizes=cfg["d_kernel_sizes"],
        num_filters=cfg["d_filters"],
        num_conditions=num_attack_types,
        cond_embed_dim=type_embed_dim,
    ).to(device)

    # Load MLE checkpoint (V2 mle_best.pt — same architecture)
    mle_ckpt = data_dir.parent.parent / "SeqGAN_SQLi" / "checkpoints" / "v2" / "mle_best.pt"
    if not mle_ckpt.exists():
        mle_ckpt = Path("SeqGAN_SQLi/checkpoints/v2/mle_best.pt")
    if mle_ckpt.exists():
        _, metrics = load_checkpoint(str(mle_ckpt), gen)
        print(f"Loaded MLE checkpoint (val_ppl={metrics.get('val_ppl', '?')})")
    else:
        print("WARNING: MLE checkpoint not found")

    entropy_coeff, temperature, lr_g_init = get_phase_params("warmup", cfg)
    opt_g = torch.optim.Adam(gen.parameters(), lr=lr_g_init, betas=(cfg["beta1"], cfg["beta2"]))
    opt_d = torch.optim.Adam(disc.parameters(), lr=cfg["lr_d"], betas=(cfg["beta1"], cfg["beta2"]))

    pad_fn = lambda b: collate_fn(b, tok.pad_id)
    train_ds = V3Dataset(str(data_dir / "train.csv"), tok, cfg["max_seq_len"])
    train_loader = torch.utils.data.DataLoader(
        train_ds, batch_size=cfg["batch_size"], shuffle=True,
        collate_fn=pad_fn, drop_last=True,
    )
    data_iter = iter(train_loader)

    def next_batch():
        nonlocal data_iter
        try:
            return next(data_iter)
        except StopIteration:
            data_iter = iter(train_loader)
            return next(data_iter)

    relex_dict_path = cfg.get("relex_dict_path", "SeqGAN_SQLi/data/relex_dictionary.json")
    relex_dict = load_relex_dict(relex_dict_path)
    if relex_dict:
        print(f"Re-lex dict loaded: {list(relex_dict.keys())}")
    else:
        print("WARNING: Re-lex dict not found")

    reward_fn = CompositeRewardV2(
        phase="warmup",
        waf_url=cfg.get("waf_url", "http://localhost:8080"),
        boundary_threshold=cfg.get("boundary_threshold", 5),
        use_waf=False,
        cache_size=cfg.get("cache_size", 100000),
    )

    writer = None
    if HAS_TB:
        log_dir.mkdir(parents=True, exist_ok=True)
        writer = SummaryWriter(str(log_dir / "adversarial_v3"))

    total_steps = (
        cfg.get("warmup_steps", 2000)
        + cfg.get("adversarial_steps", 10000)
        + cfg.get("refinement_steps", 8000)
    )
    current_phase = "warmup"
    entropy_coeff = cfg.get("entropy_coeff_warmup", 0.05)
    temperature = cfg.get("sample_temperature_warmup", 1.2)
    gp_lambda = 10.0

    # EMA baseline (V3 fix #2)
    ema_alpha = cfg.get("ema_baseline_alpha", 0.05)
    reward_ema = 0.0
    ema_initialized = False

    print(f"Total adversarial steps: {total_steps}")
    print(f"Entropy coeff: warmup={cfg.get('entropy_coeff_warmup')} adv={cfg.get('entropy_coeff_adversarial')} ref={cfg.get('entropy_coeff_refinement')}")
    print(f"Temperature: warmup={cfg.get('sample_temperature_warmup')} adv={cfg.get('sample_temperature_adversarial')} ref={cfg.get('sample_temperature_refinement')}")

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
                use_waf = cfg.get("use_waf", True)
                if use_waf:
                    try:
                        from src.waf_oracle import WAFOracle
                        reward_fn.waf = WAFOracle(url=cfg.get("waf_url", "http://localhost:8080"))
                        reward_fn.use_waf = True
                    except Exception as e:
                        print(f"  WAF init failed: {e} — continuing without WAF")

            for pg in opt_g.param_groups:
                pg["lr"] = new_lr
            print(f"\n[Step {step}] Phase -> {current_phase} | lr_g={new_lr} | entropy_coeff={entropy_coeff:.3f} | temp={temperature:.1f}")

        if current_phase == "refinement" and step % 1000 == 0:
            reward_fn.reset_ast_cache()

        real_batch, real_types = next_batch()
        real_batch = real_batch.to(device)
        real_types = real_types.to(device)
        B = real_batch.size(0)

        # ── Discriminator update ──────────────────────────────────────────────
        for _ in range(cfg.get("d_per_g_ratio", 1)):
            with torch.no_grad():
                fake_seqs, _, _ = sample_with_logits(
                    gen, B, cfg["max_seq_len"], device, tok, real_types, temperature=1.0
                )

            real_inp = real_batch[:, 1:]
            T_real = real_inp.size(1)
            fake_inp = fake_seqs[:, :T_real]
            if fake_inp.size(1) < T_real:
                pad = torch.full((B, T_real - fake_inp.size(1)), tok.pad_id, dtype=torch.long, device=device)
                fake_inp = torch.cat([fake_inp, pad], dim=1)

            d_real = disc(real_inp, cond=real_types)
            d_fake = disc(fake_inp.detach(), cond=real_types)
            gp = disc.gradient_penalty(real_inp, fake_inp.detach(), gp_lambda=gp_lambda, cond=real_types)
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
                pad = torch.full((B, T_real - fake_inp_g.size(1)), tok.pad_id, dtype=torch.long, device=device)
                fake_inp_g = torch.cat([fake_inp_g, pad], dim=1)
            d_score = disc(fake_inp_g, cond=real_types).detach()
            d_score_norm = torch.sigmoid(d_score) * 0.2
            rewards = oracle_rewards + d_score_norm

        # V3 fix #2: EMA baseline
        batch_mean = rewards.mean().item()
        if not ema_initialized:
            reward_ema = batch_mean
            ema_initialized = True
        else:
            reward_ema = ema_alpha * batch_mean + (1 - ema_alpha) * reward_ema

        advantages = rewards - reward_ema

        T = log_probs.size(1)
        pad_mask = (fake_seqs[:, :T] != tok.pad_id)

        # V3 fix #1: entropy regularization
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
            print(
                f"[{step:5d}/{total_steps}] phase={current_phase} "
                f"g={g_loss.item():.4f} pg={pg_loss.item():.4f} "
                f"H={-entropy_loss.item():.3f} "
                f"r={avg_r:.4f} ema={reward_ema:.4f} "
                f"adv_std={adv_std:.4f} unique={n_unique}/{B}"
            )
            if writer:
                writer.add_scalar("v3/g_loss", g_loss.item(), step)
                writer.add_scalar("v3/pg_loss", pg_loss.item(), step)
                writer.add_scalar("v3/entropy", -entropy_loss.item(), step)
                writer.add_scalar("v3/avg_reward", avg_r, step)
                writer.add_scalar("v3/ema_baseline", reward_ema, step)
                writer.add_scalar("v3/adv_std", adv_std, step)
                writer.add_scalar("v3/unique_per_batch", n_unique, step)
                writer.add_scalar("v3/d_loss", d_loss.item(), step)

        if step % 1000 == 0:
            ckpt_path = str(ckpt_dir / f"adv_step{step}.pt")
            save_checkpoint(ckpt_path, gen, opt_g, step, {"phase": current_phase})
            print(f"  Checkpoint: {ckpt_path}")
            print(f"  Reward stats: {reward_fn.get_stats()}")

    save_checkpoint(str(ckpt_dir / "adv_final.pt"), gen, opt_g, total_steps, {"phase": current_phase})
    print(f"\nTraining done. Final: {ckpt_dir}/adv_final.pt")
    if writer:
        writer.close()
    reward_fn.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--config", default="SeqGAN_SQLi/configs/seqgan_v3.yaml")
    parser.add_argument("--steps", type=int, default=None, help="Max steps (smoke test)")
    parser.add_argument("--no_waf", action="store_true", help="Disable WAF Oracle")
    args = parser.parse_args()

    cfg_path = args.config
    if not Path(cfg_path).exists():
        cfg_path = str(Path(__file__).parent / args.config)
    with open(cfg_path, encoding="utf-8") as f:
        cfg = yaml.safe_load(f)

    if args.no_waf:
        cfg["use_waf"] = False
        print("WAF disabled (--no_waf)")

    train(cfg, args)


if __name__ == "__main__":
    main()
