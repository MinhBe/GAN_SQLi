from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .data import export_training_jsonl, materialize_dataset
from .evaluate import evaluate_payload_file
from .generate import generate
from .train_seqgan import train


def run_one_module(data: str, out: str, module_id: str, *, surface: str = "validation", unique: bool = True, limit: int | None = None, mle_epochs: int = 8, d_epochs: int = 2, adv_epochs: int = 0, adv_steps: int = 50, rollouts: int = 4, generate_n: int = 1000, batch_size: int = 128, max_len: int = 192, emb_dim: int = 96, hidden_dim: int = 192, static_weight: float = 0.35, temperature: float = 0.9, device: str | None = None, smoke: bool = False) -> dict:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    if smoke:
        limit = limit or 128
        mle_epochs = min(mle_epochs, 1)
        d_epochs = min(d_epochs, 1)
        adv_epochs = min(adv_epochs, 1)
        adv_steps = min(adv_steps, 2)
        rollouts = min(rollouts, 1)
        generate_n = min(generate_n, 32)
        batch_size = min(batch_size, 16)
    paths = materialize_dataset(data, out / "_dataset")
    train_jsonl = out / "training_payloads.jsonl"
    prep = export_training_jsonl(paths, module_id, train_jsonl, accepted_only=True, surface=surface, unique=unique)
    train_rep = train(train_jsonl, out / "checkpoint", module_id=module_id, max_len=max_len, limit=limit, batch_size=batch_size, mle_epochs=mle_epochs, d_epochs=d_epochs, adv_epochs=adv_epochs, adv_steps=adv_steps, rollouts=rollouts, emb_dim=emb_dim, hidden_dim=hidden_dim, static_weight=static_weight, temperature=temperature, device=device)
    gen_csv = out / "generated_static_scored.csv"
    gen_rep = generate(out / "checkpoint", gen_csv, n=generate_n, batch_size=batch_size, temperature=temperature)
    eval_rep = evaluate_payload_file(gen_csv)
    summary = {"module_id": module_id, "prepare": prep, "train": train_rep, "generate": gen_rep, "evaluate": eval_rep}
    (out / "module_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.json_normalize([summary]).to_csv(out / "module_summary.csv", index=False)
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--module-id", required=True)
    ap.add_argument("--surface", choices=["validation", "canonical", "raw"], default="validation")
    ap.add_argument("--no-unique", action="store_true")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--mle-epochs", type=int, default=8)
    ap.add_argument("--d-epochs", type=int, default=2)
    ap.add_argument("--adv-epochs", type=int, default=0)
    ap.add_argument("--adv-steps", type=int, default=50)
    ap.add_argument("--rollouts", type=int, default=4)
    ap.add_argument("--generate-n", type=int, default=1000)
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--max-len", type=int, default=192)
    ap.add_argument("--emb-dim", type=int, default=96)
    ap.add_argument("--hidden-dim", type=int, default=192)
    ap.add_argument("--static-weight", type=float, default=0.35)
    ap.add_argument("--temperature", type=float, default=0.9)
    ap.add_argument("--device", default=None)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args(argv)
    print(json.dumps(run_one_module(data=args.data, out=args.out, module_id=args.module_id, surface=args.surface, unique=not args.no_unique, limit=args.limit, mle_epochs=args.mle_epochs, d_epochs=args.d_epochs, adv_epochs=args.adv_epochs, adv_steps=args.adv_steps, rollouts=args.rollouts, generate_n=args.generate_n, batch_size=args.batch_size, max_len=args.max_len, emb_dim=args.emb_dim, hidden_dim=args.hidden_dim, static_weight=args.static_weight, temperature=args.temperature, device=args.device, smoke=args.smoke), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
