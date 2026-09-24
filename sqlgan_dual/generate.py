from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd
import torch

from .data import read_jsonl
from .models import Generator
from .reward import score_payload
from .tokenizer import CharCodec
from .train_seqgan import sample_texts


def load_generator(checkpoint_dir: str | Path, device: str | None = None):
    checkpoint_dir = Path(checkpoint_dir)
    device = device or ("cuda" if torch.cuda.is_available() else "cpu")
    codec = CharCodec.load(checkpoint_dir / "codec.json")
    ckpt = torch.load(checkpoint_dir / "checkpoint.pt", map_location=device)
    cfg = ckpt.get("config", {})
    gen = Generator(codec.vocab_size, emb_dim=cfg.get("emb_dim", 96), hidden_dim=cfg.get("hidden_dim", 192), pad_id=codec.pad_id).to(device)
    gen.load_state_dict(ckpt["generator_state_dict"])
    gen.eval()
    contracts = read_jsonl(checkpoint_dir / "contracts.jsonl") if (checkpoint_dir / "contracts.jsonl").exists() else []
    return gen, codec, ckpt, contracts, device


def generate(checkpoint_dir: str | Path, out_csv: str | Path, *, n: int = 1000, batch_size: int = 128, temperature: float = 0.85, min_static_score: float = 0.82, accepted_only: bool = False) -> dict:
    gen, codec, ckpt, contracts, device = load_generator(checkpoint_dir)
    payloads = sample_texts(gen, codec, n=n, batch_size=batch_size, temperature=temperature, device=device)
    rows = []
    seen = set()
    for i, payload in enumerate(payloads):
        dup = payload in seen
        seen.add(payload)
        scored = score_payload(payload, contracts)
        v = scored.validation
        accept = v.final_accept and scored.reward >= min_static_score and not dup
        matched = contracts[scored.matched_contract_index] if scored.matched_contract_index is not None and contracts else {}
        rows.append({
            "generation_index": i,
            "module_id": ckpt.get("module_id", "module"),
            "payload_raw": payload,
            "raw_duplicate_in_generation": int(dup),
            "static_score": v.static_score,
            "reward": scored.reward,
            "matched_contract_index": scored.matched_contract_index,
            "matched_structure_cell_id": matched.get("structure_cell_id") or matched.get("cell_id"),
            "matched_root_id": matched.get("root_id") or matched.get("root_grammar_id"),
            "validation_view": v.validation_view,
            "delimiter_valid": int(v.delimiter_valid),
            "quote_valid": int(v.quote_valid),
            "boolean_signal_valid": int(v.boolean_signal_valid),
            "required_tokens_valid": int(v.required_tokens_valid),
            "skeleton_valid": int(v.skeleton_valid),
            "representation_valid": int(v.representation_valid),
            "safe_scope_valid": int(v.safe_scope_valid),
            "slot_sanity_valid": int(v.slot_sanity_valid),
            "static_accept": int(accept),
            "error_class": v.error_class,
        })
    df = pd.DataFrame(rows)
    if accepted_only:
        df = df[df["static_accept"] == 1].copy()
    out_csv = Path(out_csv)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    return {"checkpoint_dir": str(checkpoint_dir), "out_csv": str(out_csv), "generated": len(rows), "written": len(df), "static_accept_rate": float(pd.DataFrame(rows)["static_accept"].mean()) if rows else 0.0, "unique_rate": float(1 - pd.DataFrame(rows)["raw_duplicate_in_generation"].mean()) if rows else 0.0}


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--checkpoint-dir", required=True)
    ap.add_argument("--out-csv", required=True)
    ap.add_argument("--n", type=int, default=1000)
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--temperature", type=float, default=0.85)
    ap.add_argument("--min-static-score", type=float, default=0.82)
    ap.add_argument("--accepted-only", action="store_true")
    args = ap.parse_args(argv)
    print(json.dumps(generate(**vars(args)), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
