from __future__ import annotations

import argparse
import json
import os
from pathlib import Path

import pandas as pd

from .data import build_unique_corpus_file, load_corpus, materialize_dataset, module_dir
from .evaluate import evaluate_payload_file
from .generate import generate
from .train_seqgan import train


def run_one_module(data: str, out: str, module_id: str, *, use_unique: bool = True,
                   limit: int | None = None, mle_epochs: int = 8, d_epochs: int = 2,
                   adv_epochs: int = 0, generate_n: int = 1000, batch_size: int = 128,
                   max_len: int = 192, emb_dim: int = 96, hidden_dim: int = 192,
                   adv_steps: int = 100, lr: float = 1e-3, temperature: float = 0.9,
                   static_weight: float = 0.35, device: str | None = None, num_workers: int = 2,
                   amp: bool = True, compile_model: bool = False, smoke: bool = False) -> dict:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if smoke:
        limit = limit or 512
        mle_epochs = min(mle_epochs, 1)
        d_epochs = min(d_epochs, 1)
        adv_epochs = min(adv_epochs, 0)
        generate_n = min(generate_n, 128)
        batch_size = min(batch_size, 64)
    paths = materialize_dataset(data, out / "_dataset")
    src_corpus = module_dir(paths, module_id) / "seqgan_accepted_corpus.txt"
    corpus = out / "seqgan_accepted_unique_corpus.txt" if use_unique else src_corpus
    if use_unique:
        dedup = build_unique_corpus_file(paths, module_id, corpus)
    else:
        dedup = {"module_id": module_id, "input": len(load_corpus(paths, module_id, accepted=True)), "unique": None, "duplicates": None}
    train_rep = train(
        corpus=corpus,
        out_dir=out / "checkpoint",
        module_id=module_id,
        max_len=max_len,
        limit=limit,
        batch_size=batch_size,
        mle_epochs=mle_epochs,
        d_epochs=d_epochs,
        adv_epochs=adv_epochs,
        adv_steps=adv_steps,
        emb_dim=emb_dim,
        hidden_dim=hidden_dim,
        lr=lr,
        temperature=temperature,
        static_weight=static_weight,
        device=device,
        num_workers=num_workers,
        amp=amp,
        compile_model=compile_model,
    )
    gen_csv = out / "generated_static_scored.csv"
    gen_rep = generate(out / "checkpoint", gen_csv, n=generate_n, batch_size=batch_size, temperature=temperature)
    eval_rep = evaluate_payload_file(gen_csv)
    summary = {"module_id": module_id, "dedup": dedup, "train": train_rep, "generate": gen_rep, "evaluate": eval_rep}
    (out / "module_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.json_normalize([summary]).to_csv(out / "module_summary.csv", index=False)
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description="Train one SQLGAN module. Designed for one-process-per-GPU Kaggle runs.")
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--module-id", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--mle-epochs", type=int, default=8)
    ap.add_argument("--d-epochs", type=int, default=2)
    ap.add_argument("--adv-epochs", type=int, default=0)
    ap.add_argument("--adv-steps", type=int, default=100)
    ap.add_argument("--generate-n", type=int, default=1000)
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--max-len", type=int, default=192)
    ap.add_argument("--emb-dim", type=int, default=96)
    ap.add_argument("--hidden-dim", type=int, default=192)
    ap.add_argument("--lr", type=float, default=1e-3)
    ap.add_argument("--temperature", type=float, default=0.9)
    ap.add_argument("--static-weight", type=float, default=0.35)
    ap.add_argument("--device", default=None)
    ap.add_argument("--num-workers", type=int, default=2)
    ap.add_argument("--no-unique", action="store_true")
    ap.add_argument("--no-amp", action="store_true")
    ap.add_argument("--compile", action="store_true", dest="compile_model")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args(argv)
    rep = run_one_module(
        data=args.data,
        out=args.out,
        module_id=args.module_id,
        use_unique=not args.no_unique,
        limit=args.limit,
        mle_epochs=args.mle_epochs,
        d_epochs=args.d_epochs,
        adv_epochs=args.adv_epochs,
        adv_steps=args.adv_steps,
        generate_n=args.generate_n,
        batch_size=args.batch_size,
        max_len=args.max_len,
        emb_dim=args.emb_dim,
        hidden_dim=args.hidden_dim,
        lr=args.lr,
        temperature=args.temperature,
        static_weight=args.static_weight,
        device=args.device,
        num_workers=args.num_workers,
        amp=not args.no_amp,
        compile_model=args.compile_model,
        smoke=args.smoke,
    )
    print(json.dumps({"module_id": args.module_id, "out": args.out, "summary": rep}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
