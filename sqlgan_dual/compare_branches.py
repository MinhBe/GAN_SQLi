from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def flatten_branch_a(path: str | Path) -> pd.DataFrame:
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = []
    for r in obj.get("reports", []):
        rows.append({
            "branch": "A",
            "module_id": r["module_id"],
            "generated": r.get("generate", {}).get("generated"),
            "static_accept_rate": r.get("evaluate", {}).get("static_accept_rate"),
            "unique_rate": 1 - (r.get("evaluate", {}).get("raw_duplicate_count", 0) / max(r.get("evaluate", {}).get("rows", 1), 1)),
            "delimiter_valid_rate": r.get("evaluate", {}).get("delimiter_valid_rate"),
            "quote_valid_rate": r.get("evaluate", {}).get("quote_valid_rate"),
            "boolean_signal_valid_rate": r.get("evaluate", {}).get("boolean_signal_valid_rate"),
            "mean_static_score": r.get("evaluate", {}).get("mean_static_score"),
        })
    return pd.DataFrame(rows)


def flatten_branch_b(path: str | Path) -> pd.DataFrame:
    obj = json.loads(Path(path).read_text(encoding="utf-8"))
    rows = []
    for r in obj.get("core_reports", []):
        rows.append({
            "branch": "B_core",
            "module_id": r["module_id"],
            "generated": r.get("generate", {}).get("generated"),
            "static_accept_rate": r.get("evaluate", {}).get("static_accept_rate"),
            "unique_rate": 1 - (r.get("evaluate", {}).get("raw_duplicate_count", 0) / max(r.get("evaluate", {}).get("rows", 1), 1)),
            "delimiter_valid_rate": r.get("evaluate", {}).get("delimiter_valid_rate"),
            "quote_valid_rate": r.get("evaluate", {}).get("quote_valid_rate"),
            "boolean_signal_valid_rate": r.get("evaluate", {}).get("boolean_signal_valid_rate"),
            "mean_static_score": r.get("evaluate", {}).get("mean_static_score"),
        })
    for r in obj.get("renderer_reports", []):
        rows.append({
            "branch": "B_renderer",
            "module_id": r["module_id"],
            "generated": r.get("rows"),
            "static_accept_rate": r.get("static_accept_after_reverse_rate"),
            "roundtrip_rate": r.get("roundtrip_rate"),
            "semantic_preserved_rate": r.get("semantic_preserved_rate"),
            "mean_static_score": r.get("reverse_evaluate", {}).get("mean_static_score"),
        })
    return pd.DataFrame(rows)


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--branch-a-json", required=True)
    ap.add_argument("--branch-b-json", required=True)
    ap.add_argument("--out-csv", required=True)
    args = ap.parse_args(argv)
    df = pd.concat([flatten_branch_a(args.branch_a_json), flatten_branch_b(args.branch_b_json)], ignore_index=True)
    Path(args.out_csv).parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.out_csv, index=False)
    print(df.to_string(index=False))

if __name__ == "__main__":
    main()
