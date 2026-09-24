from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .evaluate import evaluate_payload_file
from .renderers import render_many
from .validators import static_validate


def load_core_payloads(paths: list[str | Path], accepted_only: bool = True) -> list[str]:
    payloads: list[str] = []
    for path in paths:
        path = Path(path)
        if path.suffix.lower() == ".txt":
            payloads.extend([x.strip() for x in path.read_text(encoding="utf-8").splitlines() if x.strip()])
            continue
        df = pd.read_csv(path)
        if accepted_only and "static_accept" in df.columns:
            df = df[df["static_accept"].astype(int) == 1].copy()
        col = "payload_raw" if "payload_raw" in df.columns else df.columns[0]
        payloads.extend(df[col].dropna().astype(str).tolist())
    return list(dict.fromkeys(payloads))


def render_from_core(core_inputs: list[str | Path], out: str | Path, *, per_parent: int = 1,
                     accepted_only: bool = True, limit: int | None = None, seed: int = 7) -> dict:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    parents = load_core_payloads(core_inputs, accepted_only=accepted_only)
    if limit:
        parents = parents[:limit]
    reports = []
    for level, name, reverse_col in [("Y3", "Y3_encoded_from_core", "payload_decoded"), ("Y4", "Y4_obfuscated_from_core", "payload_normalized")]:
        rows = render_many(parents, derived_level=level, per_parent=per_parent, seed=seed)
        df = pd.DataFrame(rows)
        if len(df):
            df["static_accept_after_reverse"] = [int(static_validate(x).final_accept) for x in df[reverse_col].fillna("").astype(str)]
        csv_path = out / name / "rendered_payloads.csv"
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_path, index=False)
        visible_eval = evaluate_payload_file(csv_path, payload_col="derived_payload") if len(df) else {"rows": 0}
        reverse_eval = evaluate_payload_file(csv_path, payload_col=reverse_col) if len(df) else {"rows": 0}
        rep = {
            "module_id": name,
            "rows": int(len(df)),
            "parents": len(parents),
            "per_parent": per_parent,
            "roundtrip_rate": float(df["roundtrip_valid"].mean()) if len(df) else 0.0,
            "semantic_preserved_rate": float(df["semantic_preserved"].mean()) if len(df) else 0.0,
            "static_accept_after_reverse_rate": float(df["static_accept_after_reverse"].mean()) if len(df) else 0.0,
            "visible_evaluate": visible_eval,
            "reverse_evaluate": reverse_eval,
            "csv": str(csv_path),
        }
        (csv_path.parent / "renderer_summary.json").write_text(json.dumps(rep, indent=2), encoding="utf-8")
        reports.append(rep)
    summary = {"parents": len(parents), "renderer_reports": reports}
    (out / "renderer_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    pd.json_normalize(reports).to_csv(out / "renderer_summary.csv", index=False)
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser(description="Render Y3/Y4 from generated or accepted Y1/Y2 core payloads.")
    ap.add_argument("--core-input", action="append", required=True, help="CSV/TXT with core payloads. Repeat for Y1 and Y2.")
    ap.add_argument("--out", required=True)
    ap.add_argument("--per-parent", type=int, default=1)
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--include-nonaccepted", action="store_true")
    args = ap.parse_args(argv)
    rep = render_from_core(args.core_input, args.out, per_parent=args.per_parent, accepted_only=not args.include_nonaccepted, limit=args.limit)
    print(json.dumps(rep, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
