from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .data import MODULES, load_payload_rows, materialize_dataset


def audit_lengths(data: str, out_json: str | None = None, *, surface: str = "validation", max_len: int = 192) -> dict:
    paths = materialize_dataset(data, Path(out_json or ".").parent / "_audit_dataset")
    rows = []
    for module in MODULES:
        payloads = [r["training_payload"] for r in load_payload_rows(paths, module, accepted_only=True, surface=surface)]
        lens = pd.Series([len(x) for x in payloads], dtype="int64")
        rows.append({
            "module_id": module,
            "rows": int(len(lens)),
            "max": int(lens.max()) if len(lens) else 0,
            "p95": float(lens.quantile(0.95)) if len(lens) else 0.0,
            "p99": float(lens.quantile(0.99)) if len(lens) else 0.0,
            "truncation_rate_at_max_len": float((lens + 2 > max_len).mean()) if len(lens) else 0.0,
            "recommended_max_len": int(max(max_len, (lens.quantile(0.99) if len(lens) else 0) + 2)),
        })
    rep = {"surface": surface, "max_len_checked": max_len, "modules": rows}
    if out_json:
        Path(out_json).parent.mkdir(parents=True, exist_ok=True)
        Path(out_json).write_text(json.dumps(rep, ensure_ascii=False, indent=2), encoding="utf-8")
    return rep


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out-json", default=None)
    ap.add_argument("--surface", choices=["validation", "canonical", "raw"], default="validation")
    ap.add_argument("--max-len", type=int, default=192)
    args = ap.parse_args(argv)
    print(json.dumps(audit_lengths(**vars(args)), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
