from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .validators import static_validate


def evaluate_payload_file(path: str | Path, payload_col: str = "payload_raw") -> dict:
    path = Path(path)
    if path.suffix.lower() == ".txt":
        payloads = [x.rstrip("\n") for x in path.read_text(encoding="utf-8").splitlines() if x.strip()]
        df = pd.DataFrame({payload_col: payloads})
    else:
        df = pd.read_csv(path)
    if payload_col not in df.columns:
        # common fallback for branch B rendered files
        for c in ["derived_payload", "payload", "validation_payload", "payload_raw"]:
            if c in df.columns:
                payload_col = c
                break
    rows = []
    for p in df[payload_col].fillna("").astype(str):
        v = static_validate(p)
        rows.append(v.__dict__)
    res = pd.DataFrame(rows)
    raw_unique = df[payload_col].nunique(dropna=False)
    return {
        "file": str(path),
        "rows": int(len(df)),
        "raw_unique": int(raw_unique),
        "raw_duplicate_count": int(len(df) - raw_unique),
        "delimiter_valid_rate": float(res["delimiter_valid"].mean()) if len(res) else 0.0,
        "quote_valid_rate": float(res["quote_valid"].mean()) if len(res) else 0.0,
        "boolean_signal_valid_rate": float(res["boolean_signal_valid"].mean()) if len(res) else 0.0,
        "dangerous_family_excluded_rate": float(res["dangerous_family_excluded"].mean()) if len(res) else 0.0,
        "slot_sanity_valid_rate": float(res["slot_sanity_valid"].mean()) if len(res) else 0.0,
        "static_accept_rate": float(res["final_accept"].mean()) if len(res) else 0.0,
        "mean_static_score": float(res["static_score"].mean()) if len(res) else 0.0,
    }


def compare_reports(report_a: dict, report_b: dict) -> pd.DataFrame:
    keys = sorted(set(report_a) | set(report_b))
    rows = []
    for k in keys:
        if isinstance(report_a.get(k), (int, float)) or isinstance(report_b.get(k), (int, float)):
            rows.append({"metric": k, "branch_a": report_a.get(k), "branch_b": report_b.get(k)})
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--payload-col", default="payload_raw")
    ap.add_argument("--out-json", default=None)
    args = ap.parse_args(argv)
    rep = evaluate_payload_file(args.input, args.payload_col)
    if args.out_json:
        Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.out_json).write_text(json.dumps(rep, indent=2), encoding="utf-8")
    print(json.dumps(rep, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
