from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .reward import score_many


def evaluate_payload_file(path: str | Path, payload_col: str = "payload_raw") -> dict:
    path = Path(path)
    if path.suffix.lower() == ".txt":
        payloads = [x.rstrip("\n") for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        df = pd.DataFrame({payload_col: payloads})
    else:
        df = pd.read_csv(path)
    if payload_col not in df.columns:
        for c in ["payload_raw", "derived_payload", "payload_decoded", "payload_normalized", "validation_payload", "payload"]:
            if c in df.columns:
                payload_col = c
                break
    payloads = df[payload_col].fillna("").astype(str).tolist()
    res = [r.validation.__dict__ for r in score_many(payloads)]
    vdf = pd.DataFrame(res)
    raw_unique = df[payload_col].nunique(dropna=False)
    return {
        "file": str(path),
        "payload_col": payload_col,
        "rows": int(len(df)),
        "raw_unique": int(raw_unique),
        "raw_duplicate_count": int(len(df) - raw_unique),
        "delimiter_valid_rate": float(vdf["delimiter_valid"].mean()) if len(vdf) else 0.0,
        "quote_valid_rate": float(vdf["quote_valid"].mean()) if len(vdf) else 0.0,
        "boolean_signal_valid_rate": float(vdf["boolean_signal_valid"].mean()) if len(vdf) else 0.0,
        "required_tokens_valid_rate": float(vdf["required_tokens_valid"].mean()) if len(vdf) else 0.0,
        "skeleton_valid_rate": float(vdf["skeleton_valid"].mean()) if len(vdf) else 0.0,
        "safe_scope_valid_rate": float(vdf["safe_scope_valid"].mean()) if len(vdf) else 0.0,
        "static_accept_rate": float(vdf["final_accept"].mean()) if len(vdf) else 0.0,
        "mean_static_score": float(vdf["static_score"].mean()) if len(vdf) else 0.0,
    }


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--payload-col", default="payload_raw")
    ap.add_argument("--out-json", default=None)
    args = ap.parse_args(argv)
    rep = evaluate_payload_file(args.input, args.payload_col)
    if args.out_json:
        Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out_json).write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(rep, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
