from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .data import CORE_MODULES, build_unique_corpus_file, materialize_dataset, module_dir
from .evaluate import evaluate_payload_file
from .generate import generate
from .renderers import render_many
from .train_seqgan import train
from .validators import static_validate


def _accepted_payloads_from_generated(path: Path) -> list[str]:
    df = pd.read_csv(path)
    if "static_accept" in df.columns:
        df = df[df["static_accept"].astype(int) == 1].copy()
    return df["payload_raw"].dropna().astype(str).drop_duplicates().tolist()


def run_branch_b(data: str, out: str, *, use_unique: bool = True, limit: int | None = None,
                 mle_epochs: int = 4, d_epochs: int = 1, adv_epochs: int = 0,
                 generate_n: int = 500, batch_size: int = 64, max_len: int = 192,
                 per_parent: int = 1, smoke: bool = False) -> dict:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    paths = materialize_dataset(data, out / "_dataset")
    if smoke:
        limit = limit or 512
        mle_epochs = min(mle_epochs, 1)
        d_epochs = min(d_epochs, 1)
        generate_n = min(generate_n, 64)
        batch_size = min(batch_size, 32)
    core_reports = []
    accepted_core_payloads = []
    for module_id in CORE_MODULES:
        mod_out = out / module_id
        mod_out.mkdir(parents=True, exist_ok=True)
        src_corpus = module_dir(paths, module_id) / "seqgan_accepted_corpus.txt"
        corpus = mod_out / "seqgan_accepted_unique_corpus.txt" if use_unique else src_corpus
        if use_unique:
            dedup = build_unique_corpus_file(paths, module_id, corpus)
        else:
            dedup = {"module_id": module_id}
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
        gen_csv = mod_out / "generated_core_static_scored.csv"
        gen_rep = generate(mod_out / "checkpoint", gen_csv, n=generate_n, batch_size=batch_size)
        eval_rep = evaluate_payload_file(gen_csv)
        core_payloads = _accepted_payloads_from_generated(gen_csv)
        accepted_core_payloads.extend(core_payloads)
        core_reports.append({"module_id": module_id, "dedup": dedup, "train": train_rep, "generate": gen_rep, "evaluate": eval_rep, "accepted_core_generated": len(core_payloads)})

    # Renderer layer: build Y3/Y4 from accepted generated core payloads.
    accepted_core_payloads = list(dict.fromkeys(accepted_core_payloads))
    renderer_reports = []
    for level, name in [("Y3", "Y3_encoded_from_core"), ("Y4", "Y4_obfuscated_from_core")]:
        rows = render_many(accepted_core_payloads, derived_level=level, per_parent=per_parent)
        df = pd.DataFrame(rows)
        if len(df):
            vals = [static_validate(x).final_accept for x in df["payload_normalized" if level == "Y4" else "payload_decoded"].astype(str)]
            df["static_accept_after_reverse"] = [int(x) for x in vals]
        else:
            df["static_accept_after_reverse"] = []
        csv_path = out / name / "rendered_payloads.csv"
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_path, index=False)
        # Evaluate visible representation and normalized/decoded view separately.
        visible_eval = evaluate_payload_file(csv_path, payload_col="derived_payload") if len(df) else {"rows": 0}
        reverse_col = "payload_decoded" if level == "Y3" else "payload_normalized"
        reverse_eval = evaluate_payload_file(csv_path, payload_col=reverse_col) if len(df) else {"rows": 0}
        renderer_reports.append({
            "module_id": name,
            "rows": int(len(df)),
            "roundtrip_rate": float(df["roundtrip_valid"].mean()) if len(df) else 0.0,
            "semantic_preserved_rate": float(df["semantic_preserved"].mean()) if len(df) else 0.0,
            "static_accept_after_reverse_rate": float(df["static_accept_after_reverse"].mean()) if len(df) else 0.0,
            "visible_evaluate": visible_eval,
            "reverse_evaluate": reverse_eval,
            "csv": str(csv_path),
        })
    summary = {"branch": "B_core_plus_renderers", "core_reports": core_reports, "renderer_reports": renderer_reports, "accepted_core_payloads": len(accepted_core_payloads)}
    (out / "branch_b_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    pd.json_normalize(core_reports + renderer_reports).to_csv(out / "branch_b_summary.csv", index=False)
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description="Branch B: train Y1/Y2 core, then render Y3/Y4 from accepted core generations.")
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--mle-epochs", type=int, default=4)
    ap.add_argument("--d-epochs", type=int, default=1)
    ap.add_argument("--adv-epochs", type=int, default=0)
    ap.add_argument("--generate-n", type=int, default=500)
    ap.add_argument("--batch-size", type=int, default=64)
    ap.add_argument("--max-len", type=int, default=192)
    ap.add_argument("--per-parent", type=int, default=1)
    ap.add_argument("--no-unique", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args(argv)
    rep = run_branch_b(
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
        per_parent=args.per_parent,
        smoke=args.smoke,
    )
    print(json.dumps({"branch": rep["branch"], "out": args.out}, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
