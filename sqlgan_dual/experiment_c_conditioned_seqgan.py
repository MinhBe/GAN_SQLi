from __future__ import annotations

import argparse
import json
import math
import os
import random
import time
from collections import Counter, defaultdict
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from torch import nn
from torch.nn.utils.rnn import pack_padded_sequence
from torch.utils.data import DataLoader, TensorDataset

from .cseqgan_data import (
    CORE_MODULES,
    export_training_jsonl_for_legacy_train,
    load_cseqgan_training_jsonl,
    load_ruleset_contracts,
    materialize_cseqgan_dataset,
)
from .models import Discriminator, Generator
from .reward import sha256_text
from .reward_v2 import parse_condition_prefix, score_many_v2, score_payload_v2
from .tokenizer import CharCodec


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def configure_torch(device: str, *, cpu_threads: int = 2) -> None:
    torch.set_num_threads(max(1, int(cpu_threads)))
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
    return DataLoader(
        TensorDataset(arr),
        batch_size=batch_size,
        shuffle=shuffle,
        drop_last=False,
        num_workers=max(0, int(num_workers)),
        pin_memory=torch.cuda.is_available(),
    )


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


def _ids_for_text(codec: CharCodec, text: str) -> list[int]:
    return [codec.stoi.get(ch, codec.unk_id) for ch in str(text)]


def _pad_full_sequences(full_ids: list[list[int]], width: int, eos_id: int, pad_id: int, device: str) -> torch.Tensor:
    rows = []
    for ids in full_ids:
        seq = ids[: width]
        if not seq or seq[-1] != eos_id:
            if len(seq) >= width:
                seq[-1] = eos_id
            else:
                seq = seq + [eos_id]
        seq = seq[:width]
        seq = seq + [pad_id] * (width - len(seq))
        rows.append(seq)
    return torch.tensor(rows, dtype=torch.long, device=device)


def sample_conditioned_with_logp(
    gen: Generator,
    codec: CharCodec,
    prefixes: list[str],
    *,
    max_new_tokens: int,
    temperature: float,
    device: str,
) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, list[str]]:
    """Sample continuations after fixed text prefixes.

    Returns full token IDs padded to codec.max_len, continuation log-probs and masks,
    and decoded full strings. The fixed prefix is not included in the PG loss mask.
    """
    gen.train()
    batch = len(prefixes)
    prefix_ids = [_ids_for_text(codec, p) for p in prefixes]
    # Keep space for at least EOS and a few generated chars.
    prefix_ids = [ids[: max(0, codec.max_len - 8)] for ids in prefix_ids]
    lengths = [len(ids) + 1 for ids in prefix_ids]  # + BOS
    max_pref = max(lengths)
    inp = torch.full((batch, max_pref), codec.pad_id, dtype=torch.long, device=device)
    for i, ids in enumerate(prefix_ids):
        row = [codec.bos_id] + ids
        inp[i, : len(row)] = torch.tensor(row, dtype=torch.long, device=device)
    emb = gen.emb(inp)
    packed = pack_padded_sequence(emb, lengths, batch_first=True, enforce_sorted=False)
    _, hidden = gen.rnn(packed)
    last = torch.tensor([ids[-1] if ids else codec.bos_id for ids in prefix_ids], dtype=torch.long, device=device)
    banned = torch.zeros(gen.vocab_size, dtype=torch.bool, device=device)
    banned[codec.pad_id] = True
    banned[codec.bos_id] = True
    seq_tokens: list[torch.Tensor] = []
    logps: list[torch.Tensor] = []
    masks: list[torch.Tensor] = []
    finished = torch.zeros(batch, dtype=torch.bool, device=device)
    max_steps = max(1, min(int(max_new_tokens), codec.max_len - min(len(x) for x in prefix_ids) - 1))
    for _ in range(max_steps):
        logits, hidden = gen.step(last, hidden)
        logits = logits / max(float(temperature), 1e-6)
        logits = logits.masked_fill(banned.unsqueeze(0), -1e9)
        probs = torch.softmax(logits.float(), dim=-1)
        dist = torch.distributions.Categorical(probs=probs)
        sampled = dist.sample()
        logp = dist.log_prob(sampled)
        active = ~finished
        token = torch.where(active, sampled, torch.full_like(sampled, codec.eos_id))
        seq_tokens.append(token)
        logps.append(torch.where(active, logp, torch.zeros_like(logp)))
        masks.append(active.float())
        finished = finished | token.eq(codec.eos_id)
        last = token
        if bool(finished.all().item()):
            break
    if not seq_tokens:
        seq_tokens.append(torch.full((batch,), codec.eos_id, dtype=torch.long, device=device))
        logps.append(torch.zeros(batch, dtype=torch.float32, device=device))
        masks.append(torch.zeros(batch, dtype=torch.float32, device=device))
    sampled_matrix = torch.stack(seq_tokens, dim=1)
    full_lists: list[list[int]] = []
    for i in range(batch):
        full_lists.append(prefix_ids[i] + sampled_matrix[i].detach().cpu().tolist())
    full = _pad_full_sequences(full_lists, codec.max_len, codec.eos_id, codec.pad_id, device)
    decoded = [codec.decode(row.tolist()) for row in full.detach().cpu()]
    return full, torch.stack(logps, dim=1), torch.stack(masks, dim=1), decoded


def sample_conditioned_texts(
    gen: Generator,
    codec: CharCodec,
    prefixes: list[str],
    *,
    max_new_tokens: int,
    temperature: float,
    device: str,
) -> list[str]:
    gen.eval()
    with torch.no_grad():
        _, _, _, decoded = sample_conditioned_with_logp(
            gen,
            codec,
            prefixes,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            device=device,
        )
    return decoded


def train_discriminator_epoch_conditioned(
    disc: Discriminator,
    gen: Generator,
    loader: DataLoader,
    contracts: list[dict[str, Any]],
    codec: CharCodec,
    opt,
    device: str,
    *,
    batch_size: int,
    max_new_tokens: int,
    temperature: float,
    amp: bool = True,
) -> float:
    disc.train()
    gen.eval()
    bce = nn.BCEWithLogitsLoss()
    scaler = torch.amp.GradScaler("cuda", enabled=(amp and device.startswith("cuda")))
    losses: list[float] = []
    n_contracts = len(contracts)
    for (real,) in loader:
        real = real.to(device, non_blocking=True)
        idx = np.random.randint(0, n_contracts, size=real.size(0)).tolist()
        prefixes = [contracts[i].get("prefix", "") + " " for i in idx]
        with torch.no_grad():
            fake_txt = sample_conditioned_texts(
                gen,
                codec,
                prefixes,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                device=device,
            )
            fake = torch.tensor([codec.encode(x) for x in fake_txt], dtype=torch.long, device=device)
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


def pg_epoch_fast_conditioned(
    gen: Generator,
    disc: Discriminator,
    codec: CharCodec,
    opt,
    contracts: list[dict[str, Any]],
    training_hashes: set[str],
    *,
    steps: int,
    batch_size: int,
    max_new_tokens: int,
    device: str,
    static_weight: float,
    temperature: float,
    amp: bool = True,
) -> float:
    gen.train()
    disc.eval()
    scaler = torch.amp.GradScaler("cuda", enabled=(amp and device.startswith("cuda")))
    losses: list[float] = []
    recent: list[str] = []
    coverage_counts: Counter[str] = Counter()
    n_contracts = len(contracts)
    for _ in range(max(0, int(steps))):
        idx = np.random.randint(0, n_contracts, size=int(batch_size)).tolist()
        batch_contracts = [contracts[i] for i in idx]
        prefixes = [str(c.get("prefix", "")) + " " for c in batch_contracts]
        full, logps, mask, decoded = sample_conditioned_with_logp(
            gen,
            codec,
            prefixes,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            device=device,
        )
        with torch.no_grad():
            d_reward = torch.sigmoid(disc(full)).float()
            v2 = score_many_v2(
                decoded,
                batch_contracts,
                training_hashes=training_hashes,
                recent_payloads=recent,
                coverage_counts=coverage_counts,
                max_len=codec.max_len,
            )
            s_reward = torch.tensor([r.reward for r in v2], dtype=torch.float32, device=device)
            reward = (1.0 - float(static_weight)) * d_reward + float(static_weight) * s_reward
            reward = reward - reward.mean()
        loss = -((logps * reward[:, None] * mask).sum() / mask.sum().clamp_min(1.0))
        opt.zero_grad(set_to_none=True)
        scaler.scale(loss).backward()
        scaler.unscale_(opt)
        torch.nn.utils.clip_grad_norm_(gen.parameters(), 5.0)
        scaler.step(opt)
        scaler.update()
        losses.append(float(loss.detach().item()))
        for text, result in zip(decoded, v2):
            recent.append(text)
            if result.hard_gate_pass and not result.off_ruleset:
                coverage_counts[str(result.target_ruleset_id)] += 1
        recent = recent[-512:]
    return float(np.mean(losses)) if losses else 0.0


def clean_state_dict(model: nn.Module) -> dict[str, torch.Tensor]:
    sd = model.state_dict()
    if any(k.startswith("_orig_mod.") for k in sd):
        return {k.replace("_orig_mod.", "", 1): v for k, v in sd.items()}
    return sd


def _write_candidates(
    rows: list[dict[str, Any]],
    path: Path,
    *,
    accepted_threshold: float,
) -> dict[str, Any]:
    df = pd.DataFrame(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    if not df.empty:
        accepted = df[df["accepted_for_next_stage"].astype(bool)].copy()
        rejected = df[~df["accepted_for_next_stage"].astype(bool)].copy()
        accepted.to_csv(path.parent / "accepted_for_next_stage.csv", index=False)
        rejected.to_csv(path.parent / "rejected_for_next_stage.csv", index=False)
        per = (
            df.groupby("target_ruleset_id")
            .agg(
                generated_count=("sample_id", "count"),
                accepted_count=("accepted_for_next_stage", "sum"),
                mean_reward_total=("reward_total", "mean"),
                ruleset_match_rate=("ruleset_match_score", "mean"),
                skeleton_match_rate=("skeleton_match_score", "mean"),
                slot_match_rate=("slot_match_score", "mean"),
                off_ruleset_rate=("off_ruleset", "mean"),
            )
            .reset_index()
        )
        per.to_csv(path.parent / "per_ruleset_metrics.csv", index=False)
    return {"candidate_rows": len(rows), "accepted_threshold": accepted_threshold, "output": str(path)}


def generate_candidates(
    gen: Generator,
    codec: CharCodec,
    contracts: list[dict[str, Any]],
    out_dir: Path,
    *,
    module_id: str,
    n_per_ruleset: int,
    ruleset_limit: int | None,
    batch_size: int,
    max_new_tokens: int,
    temperature: float,
    device: str,
    accepted_threshold: float,
    seed: int,
) -> dict[str, Any]:
    gen.eval()
    unique_contracts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for c in contracts:
        rid = str(c.get("ruleset_id") or c.get("target_ruleset_id") or "")
        if not rid or rid in seen:
            continue
        seen.add(rid)
        unique_contracts.append(c)
        if ruleset_limit and len(unique_contracts) >= int(ruleset_limit):
            break
    targets = []
    for c in unique_contracts:
        for _ in range(max(1, int(n_per_ruleset))):
            targets.append(c)
    rows: list[dict[str, Any]] = []
    recent: list[str] = []
    coverage_counts: Counter[str] = Counter()
    run_id = f"CSEQGAN_{module_id}_{int(time.time())}"
    with torch.no_grad():
        for start in range(0, len(targets), batch_size):
            batch_contracts = targets[start : start + batch_size]
            prefixes = [str(c.get("prefix", "")) + " " for c in batch_contracts]
            decoded = sample_conditioned_texts(
                gen,
                codec,
                prefixes,
                max_new_tokens=max_new_tokens,
                temperature=temperature,
                device=device,
            )
            scored = score_many_v2(decoded, batch_contracts, recent_payloads=recent, coverage_counts=coverage_counts, max_len=codec.max_len)
            for i, (text, c, s) in enumerate(zip(decoded, batch_contracts, scored), start=len(rows)):
                meta, stripped = parse_condition_prefix(text)
                accepted = bool(s.reward >= accepted_threshold and s.hard_gate_pass and not s.off_ruleset)
                rid = str(c.get("ruleset_id") or "")
                if accepted:
                    coverage_counts[rid] += 1
                recent.append(text)
                row = {
                    "sample_id": f"GEN_{module_id}_{i:08d}",
                    "run_id": run_id,
                    "generation_index": i,
                    "model_name": "C-SeqGAN-Minimal",
                    "candidate_generation_status": "model_generated",
                    "branch": "C_conditioned_seqgan_minimal",
                    "seed": seed,
                    "target_ruleset_id": c.get("ruleset_id", ""),
                    "target_root_id": c.get("root_id", ""),
                    "target_structure_cell_id": c.get("structure_cell_id", ""),
                    "target_module_id": c.get("module_id", module_id),
                    "target_y_level": c.get("y_level", ""),
                    "target_semantic_family": c.get("semantic_family", ""),
                    "target_ruleset_family": c.get("ruleset_family", ""),
                    "target_skeleton_reference": c.get("skeleton_reference", ""),
                    "target_required_tokens": c.get("required_tokens", ""),
                    "target_slot_schema_id": c.get("slot_schema_id", ""),
                    "prompt_prefix": str(c.get("prefix", "")),
                    "payload_raw": text,
                    "payload_stripped": stripped,
                    "payload_hash": "sha256:" + sha256_text(text),
                    "payload_length_chars": len(text),
                    "matched_ruleset_id": s.matched_ruleset_id,
                    "matched_structure_cell_id": s.matched_structure_cell_id,
                    "match_source": "algorithmic_match",
                    "ruleset_match_score": s.ruleset_score,
                    "skeleton_match_score": s.skeleton_score,
                    "slot_match_score": s.slot_score,
                    "off_ruleset": s.off_ruleset,
                    "reward_total": s.reward,
                    "reward_stage": "cseqgan_minimal_generate",
                    "r_ruleset": s.ruleset_score,
                    "r_skeleton": s.skeleton_score,
                    "r_slot": s.slot_score,
                    "r_structure": s.structure_score,
                    "r_diversity": s.diversity_score,
                    "r_coverage": s.coverage_score,
                    "r_length": s.length_score,
                    "p_duplicate": s.duplicate_penalty,
                    "p_near_duplicate": s.near_duplicate_penalty,
                    "p_off_ruleset": s.off_ruleset_penalty,
                    "reward_version": s.reward_version,
                    "delimiter_valid": s.delimiter_valid,
                    "quote_valid": s.quote_valid,
                    "boolean_signal_valid": s.boolean_signal_valid,
                    "required_tokens_valid": s.required_tokens_valid,
                    "skeleton_valid": s.skeleton_valid,
                    "slot_sanity_valid": s.slot_sanity_valid,
                    "static_score": s.static_score,
                    "static_error_class": s.error_class,
                    "accepted_for_next_stage": accepted,
                    "accepted_reason": "reward_v2_pass" if accepted else "",
                    "rejected_reason": "" if accepted else s.error_class,
                    "runtime_claim_allowed": False,
                }
                rows.append(row)
            recent = recent[-512:]
    return _write_candidates(rows, out_dir / "generated_candidates.csv", accepted_threshold=accepted_threshold)


def train_one_module(
    *,
    data: str,
    out: str,
    module_id: str,
    work_dir: str,
    use_full_coverage: bool,
    limit: int | None,
    max_len: int,
    batch_size: int,
    mle_epochs: int,
    d_epochs: int,
    adv_epochs: int,
    adv_steps: int,
    emb_dim: int,
    hidden_dim: int,
    lr: float,
    seed: int,
    temperature: float,
    static_weight: float,
    generate_per_ruleset: int,
    generate_ruleset_limit: int | None,
    accepted_threshold: float,
    device: str,
    num_workers: int,
    amp: bool,
    cpu_threads: int,
) -> dict[str, Any]:
    set_seed(seed)
    configure_torch(device, cpu_threads=cpu_threads)
    paths = materialize_cseqgan_dataset(data, Path(work_dir) / "dataset")
    texts, contracts, train_src = load_cseqgan_training_jsonl(
        paths,
        module_id,
        use_full_coverage=use_full_coverage,
        limit=limit,
        unique=True,
    )
    out_dir = Path(out) / module_id
    out_dir.mkdir(parents=True, exist_ok=True)
    export_training_jsonl_for_legacy_train(texts, contracts, out_dir / "cseqgan_training_effective.jsonl")
    codec = CharCodec.fit(texts, max_len=max_len)
    loader = make_loader(texts, codec, batch_size, shuffle=True, num_workers=num_workers)
    gen = Generator(codec.vocab_size, emb_dim=emb_dim, hidden_dim=hidden_dim, pad_id=codec.pad_id).to(device)
    disc = Discriminator(codec.vocab_size, emb_dim=emb_dim, pad_id=codec.pad_id).to(device)
    opt_g = torch.optim.AdamW(gen.parameters(), lr=lr)
    opt_d = torch.optim.AdamW(disc.parameters(), lr=lr)
    training_hashes = {sha256_text(t) for t in texts}
    history: list[dict[str, Any]] = []
    best = math.inf
    max_new_tokens = max(32, max_len // 2)
    start_time = time.time()
    print(f"[{module_id}] device={device} texts={len(texts)} vocab={codec.vocab_size} src={train_src}", flush=True)
    for ep in range(1, mle_epochs + 1):
        t0 = time.time()
        nll = mle_epoch(gen, loader, opt_g, codec.pad_id, device, amp=amp)
        history.append({"phase": "mle", "epoch": ep, "nll": nll, "seconds": round(time.time() - t0, 3)})
        print(f"[{module_id}] MLE {ep}/{mle_epochs} nll={nll:.4f} sec={time.time()-t0:.1f}", flush=True)
        if nll < best:
            best = nll
            torch.save(clean_state_dict(gen), out_dir / "generator_mle_best.pt")
    for ep in range(1, d_epochs + 1):
        t0 = time.time()
        d_loss = train_discriminator_epoch_conditioned(
            disc,
            gen,
            loader,
            contracts,
            codec,
            opt_d,
            device,
            batch_size=batch_size,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            amp=amp,
        )
        history.append({"phase": "discriminator", "epoch": ep, "d_loss": d_loss, "seconds": round(time.time() - t0, 3)})
        print(f"[{module_id}] D {ep}/{d_epochs} loss={d_loss:.4f} sec={time.time()-t0:.1f}", flush=True)
    for ep in range(1, adv_epochs + 1):
        t0 = time.time()
        pg_loss = pg_epoch_fast_conditioned(
            gen,
            disc,
            codec,
            opt_g,
            contracts,
            training_hashes,
            steps=adv_steps,
            batch_size=batch_size,
            max_new_tokens=max_new_tokens,
            device=device,
            static_weight=static_weight,
            temperature=temperature,
            amp=amp,
        )
        d_loss = train_discriminator_epoch_conditioned(
            disc,
            gen,
            loader,
            contracts,
            codec,
            opt_d,
            device,
            batch_size=batch_size,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
            amp=amp,
        )
        history.append({"phase": "adv_fast_pg", "epoch": ep, "pg_loss": pg_loss, "d_loss": d_loss, "seconds": round(time.time() - t0, 3)})
        print(f"[{module_id}] ADV {ep}/{adv_epochs} pg={pg_loss:.4f} d={d_loss:.4f} sec={time.time()-t0:.1f}", flush=True)
    codec.save(out_dir / "codec.json")
    torch.save(
        {
            "module_id": module_id,
            "generator_state_dict": clean_state_dict(gen),
            "discriminator_state_dict": clean_state_dict(disc),
            "config": {
                "max_len": max_len,
                "batch_size": batch_size,
                "emb_dim": emb_dim,
                "hidden_dim": hidden_dim,
                "mle_epochs": mle_epochs,
                "d_epochs": d_epochs,
                "adv_epochs": adv_epochs,
                "adv_steps": adv_steps,
                "temperature": temperature,
                "static_weight": static_weight,
                "use_full_coverage": use_full_coverage,
            },
        },
        out_dir / "checkpoint.pt",
    )
    gen_summary = generate_candidates(
        gen,
        codec,
        contracts,
        out_dir / "generated_candidates",
        module_id=module_id,
        n_per_ruleset=generate_per_ruleset,
        ruleset_limit=generate_ruleset_limit,
        batch_size=batch_size,
        max_new_tokens=max_new_tokens,
        temperature=temperature,
        device=device,
        accepted_threshold=accepted_threshold,
        seed=seed,
    )
    summary = {
        "module_id": module_id,
        "corpus_size": len(texts),
        "contract_count": len(contracts),
        "vocab_size": codec.vocab_size,
        "best_mle_nll": best,
        "device": device,
        "train_source": str(train_src),
        "out_dir": str(out_dir),
        "seconds_total": round(time.time() - start_time, 3),
        "generated": gen_summary,
    }
    (out_dir / "history.json").write_text(json.dumps(history, indent=2), encoding="utf-8")
    (out_dir / "run_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2), flush=True)
    return summary


def _resolve_devices(requested: str | None, n_modules: int, parallel: bool) -> list[str]:
    if requested and requested != "auto":
        if "," in requested:
            devs = [x.strip() for x in requested.split(",") if x.strip()]
            return (devs * ((n_modules + len(devs) - 1) // len(devs)))[:n_modules]
        return [requested] * n_modules
    if torch.cuda.is_available():
        n = torch.cuda.device_count()
        if parallel and n >= 2:
            return [f"cuda:{i % n}" for i in range(n_modules)]
        return ["cuda:0"] * n_modules
    return ["cpu"] * n_modules


def run_experiment(args) -> dict[str, Any]:
    modules = args.modules or CORE_MODULES
    parallel = args.parallel_modules == "on" or (args.parallel_modules == "auto" and torch.cuda.is_available() and torch.cuda.device_count() >= 2 and len(modules) >= 2)
    devices = _resolve_devices(args.device, len(modules), parallel)
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    common = dict(
        data=args.data,
        out=str(out),
        work_dir=args.work_dir or str(out / "_work"),
        use_full_coverage=not args.reward_positive_only,
        limit=args.limit,
        max_len=args.max_len,
        batch_size=args.batch_size,
        mle_epochs=args.mle_epochs,
        d_epochs=args.d_epochs,
        adv_epochs=args.adv_epochs,
        adv_steps=args.adv_steps,
        emb_dim=args.emb_dim,
        hidden_dim=args.hidden_dim,
        lr=args.lr,
        seed=args.seed,
        temperature=args.temperature,
        static_weight=args.static_weight,
        generate_per_ruleset=args.generate_per_ruleset,
        generate_ruleset_limit=args.generate_ruleset_limit,
        accepted_threshold=args.accepted_threshold,
        num_workers=args.num_workers,
        amp=not args.no_amp,
        cpu_threads=args.cpu_threads,
    )
    summaries = []
    if parallel and len(modules) > 1:
        print(f"[experiment] parallel module mode: {list(zip(modules, devices))}", flush=True)
        with ProcessPoolExecutor(max_workers=len(modules)) as ex:
            futs = []
            for module_id, device in zip(modules, devices):
                futs.append(ex.submit(train_one_module, module_id=module_id, device=device, **common))
            for fut in as_completed(futs):
                summaries.append(fut.result())
    else:
        print(f"[experiment] sequential mode: {list(zip(modules, devices))}", flush=True)
        for module_id, device in zip(modules, devices):
            summaries.append(train_one_module(module_id=module_id, device=device, **common))
    summary = {
        "experiment": "C-SeqGAN-Minimal",
        "modules": modules,
        "parallel_modules": parallel,
        "devices": devices,
        "summaries": summaries,
        "out": str(out),
    }
    (out / "experiment_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description="Branch C: minimal ruleset-conditioned SeqGAN for V5/V5.1 corpus")
    ap.add_argument("--data", required=True, help="Path to SQLGAN_PostgreSQL_Boolean_CSeqGAN_V5_1_CoverageFixed.zip or extracted root")
    ap.add_argument("--out", required=True)
    ap.add_argument("--work-dir", default=None)
    ap.add_argument("--modules", nargs="+", default=CORE_MODULES)
    ap.add_argument("--reward-positive-only", action="store_true", help="Use cseqgan_train.jsonl instead of full coverage MLE file")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--max-len", type=int, default=256)
    ap.add_argument("--batch-size", type=int, default=160)
    ap.add_argument("--mle-epochs", type=int, default=8)
    ap.add_argument("--d-epochs", type=int, default=1)
    ap.add_argument("--adv-epochs", type=int, default=1)
    ap.add_argument("--adv-steps", type=int, default=25)
    ap.add_argument("--emb-dim", type=int, default=128)
    ap.add_argument("--hidden-dim", type=int, default=256)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--temperature", type=float, default=0.85)
    ap.add_argument("--static-weight", type=float, default=0.45)
    ap.add_argument("--generate-per-ruleset", type=int, default=2)
    ap.add_argument("--generate-ruleset-limit", type=int, default=100)
    ap.add_argument("--accepted-threshold", type=float, default=0.72)
    ap.add_argument("--device", default="auto")
    ap.add_argument("--parallel-modules", choices=["auto", "on", "off"], default="auto")
    ap.add_argument("--num-workers", type=int, default=0)
    ap.add_argument("--cpu-threads", type=int, default=2)
    ap.add_argument("--no-amp", action="store_true")
    args = ap.parse_args(argv)
    print(json.dumps(run_experiment(args), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
