from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

from .data import CORE_MODULES
from .evaluate import evaluate_payload_file
from .renderers import render_many
from .train_module import run_one_module


def _accepted_payloads(path: Path) -> list[str]:
    df = pd.read_csv(path)
    if "static_accept" in df.columns:
        df = df[df["static_accept"].astype(int).eq(1)]
    return df["payload_raw"].dropna().astype(str).drop_duplicates().tolist()


def run_branch_b(data: str, out: str, *, surface: str = "validation", limit: int | None = None, mle_epochs: int = 8, d_epochs: int = 2, adv_epochs: int = 0, adv_steps: int = 50, rollouts: int = 4, generate_n: int = 1000, batch_size: int = 128, max_len: int = 192, per_parent: int = 1, smoke: bool = False) -> dict:
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    reports = []
    core_payloads: list[str] = []
    for module_id in CORE_MODULES:
        mod_out = out / module_id
        rep = run_one_module(data, str(mod_out), module_id, surface=surface, limit=limit, mle_epochs=mle_epochs, d_epochs=d_epochs, adv_epochs=adv_epochs, adv_steps=adv_steps, rollouts=rollouts, generate_n=generate_n, batch_size=batch_size, max_len=max_len, smoke=smoke)
        reports.append(rep)
        core_payloads.extend(_accepted_payloads(mod_out / "generated_static_scored.csv"))
    core_payloads = list(dict.fromkeys(core_payloads))
    renderer_reports = []
    for level, name in [("Y3", "Y3_encoded_from_core"), ("Y4", "Y4_obfuscated_from_core")]:
        rows = render_many(core_payloads, level, per_parent=per_parent)
        df = pd.DataFrame(rows)
        csv_path = out / name / "rendered_payloads.csv"
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(csv_path, index=False)
        visible_eval = evaluate_payload_file(csv_path, "derived_payload") if len(df) else {"rows": 0}
        reverse_col = "payload_decoded" if level == "Y3" else "payload_normalized"
        reverse_eval = evaluate_payload_file(csv_path, reverse_col) if len(df) else {"rows": 0}
        renderer_reports.append({
            "module_id": name,
            "rows": int(len(df)),
            "roundtrip_rate": float(df["roundtrip_valid"].mean()) if len(df) else 0.0,
            "semantic_preserved_rate": float(df["semantic_preserved"].mean()) if len(df) else 0.0,
            "visible_evaluate": visible_eval,
            "reverse_evaluate": reverse_eval,
            "csv": str(csv_path),
        })
    summary = {"branch": "B_CGR_core_plus_renderers", "core_reports": reports, "renderer_reports": renderer_reports, "accepted_core_payloads": len(core_payloads)}
    (out / "branch_b_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    pd.json_normalize(renderer_reports).to_csv(out / "branch_b_renderer_summary.csv", index=False)
    return summary


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--data", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--surface", choices=["validation", "canonical", "raw"], default="validation")
    ap.add_argument("--limit", type=int, default=None)
    ap.add_argument("--mle-epochs", type=int, default=8)
    ap.add_argument("--d-epochs", type=int, default=2)
    ap.add_argument("--adv-epochs", type=int, default=0)
    ap.add_argument("--adv-steps", type=int, default=50)
    ap.add_argument("--rollouts", type=int, default=4)
    ap.add_argument("--generate-n", type=int, default=1000)
    ap.add_argument("--batch-size", type=int, default=128)
    ap.add_argument("--max-len", type=int, default=192)
    ap.add_argument("--per-parent", type=int, default=1)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args(argv)
    print(json.dumps(run_branch_b(**vars(args)), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
