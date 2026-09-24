from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def aggregate_modules(run_dir: str | Path, out_prefix: str = "branch_summary") -> dict:
    run_dir = Path(run_dir)
    rows = []
    for p in sorted(run_dir.glob("*/module_summary.json")):
        rep = read_json(p)
        flat = pd.json_normalize([rep]).iloc[0].to_dict()
        flat["summary_file"] = str(p)
        rows.append(flat)
    for p in sorted(run_dir.glob("*/renderer_summary.json")):
        rep = read_json(p)
        if "module_id" in rep:
            flat = pd.json_normalize([rep]).iloc[0].to_dict()
            flat["summary_file"] = str(p)
            rows.append(flat)
    df = pd.DataFrame(rows)
    csv_path = run_dir / f"{out_prefix}.csv"
    json_path = run_dir / f"{out_prefix}.json"
    df.to_csv(csv_path, index=False)
    summary = {"run_dir": str(run_dir), "rows": len(df), "csv": str(csv_path)}
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out-prefix", default="branch_summary")
    args = ap.parse_args(argv)
    print(json.dumps(aggregate_modules(args.run_dir, args.out_prefix), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
