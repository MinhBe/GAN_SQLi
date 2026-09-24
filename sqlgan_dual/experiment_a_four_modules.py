from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .data import MODULES, build_unique_corpus_file, load_corpus, materialize_dataset, module_dir
from .evaluate import evaluate_payload_file
from .generate import generate
from .train_seqgan import train


def run_branch_a(data: str, out: str, *, use_unique: bool = True, limit: int | None = None,
                 mle_epochs: int = 4, d_epochs: int = 1, adv_epochs: int = 0,
                 generate_n: int = 500, batch_size: int = 64, max_len: int = 192,
                 smoke: bool = False) -> dict:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    paths = materialize_dataset(data, out / "_dataset")
    modules = MODULES
    if smoke:
        limit = limit or 512
        mle_epochs = min(mle_epochs, 1)
        d_epochs = min(d_epochs, 1)
        generate_n = min(generate_n, 64)
        batch_size = min(batch_size, 32)
    reports = []
    for module_id in modules:
        mod_out = out / module_id
        mod_out.mkdir(parents=True, exist_ok=True)
        src_corpus = module_dir(paths, module_id) / "seqgan_accepted_corpus.txt"
        corpus = mod_out / "seqgan_accepted_unique_corpus.txt" if use_unique else src_corpus
        if use_unique:
            dedup = build_unique_corpus_file(paths, module_id, corpus)
        else:
            dedup = {"module_id": module_id, "input": len(load_corpus(paths, module_id, accepted=True)), "unique": None, "duplicates": None}
        train_rep = train(
            corpus=corpus,
            out_dir=mod_out / "checkpoint",
            module_id=module_id,
            max_len=max_len,
            limit=limit,
            batch_size=batch_size,
            mle_epochs=mle_epochs,
            d_epochs=d_epochs,
            adv_epochs=adv_epochs,
        )
        gen_csv = mod_out / "generated_static_scored.csv"
        gen_rep = generate(mod_out / "checkpoint", gen_csv, n=generate_n, batch_size=batch_size)
        eval_rep = evaluate_payload_file(gen_csv)
        reports.append({"module_id": module_id, "dedup": dedup, "train": train_rep, "generate": gen_rep, "evaluate": eval_rep})
    summary = {"branch": "A_four_independent_modules", "reports": reports}
    (out / "branch_a_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    pd.json_normalize(reports).to_csv(out / "branch_a_summary.csv", index=False)
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description="Branch A: train four independent SeqGAN modules Y1/Y2/Y3/Y4.")
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--mle-epochs", type=int, default=4)
    ap.add_argument("--d-epochs", type=int, default=1)
    ap.add_argument("--adv-epochs", type=int, default=0)
    ap.add_argument("--generate-n", type=int, default=500)
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--max-len", type=int, default=192)
    ap.add_argument("--no-unique", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args(argv)
    rep = run_branch_a(
        data=args.data,
        out=args.out,
        use_unique=not args.no_unique,
        limit=args.limit,
        mle_epochs=args.mle_epochs,
        d_epochs=args.d_epochs,
        adv_epochs=args.adv_epochs,
        generate_n=args.generate_n,
        batch_size=args.batch_size,
        max_len=args.max_len,
        smoke=args.smoke,
    )
    print(json.dumps({"branch": rep["branch"], "out": args.out}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
