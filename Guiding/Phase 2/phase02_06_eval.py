"""
Phase 02 — Script 6: Final Evaluation & Report
Input : Guiding/Phase 2/eval/mle_frontier.json
        Guiding/Phase 2/eval/gan_results.json
Output: Guiding/Phase 2/02_slice_eval_report.md
"""

import json
from pathlib import Path

HERE    = Path(__file__).parent
MLE_F   = HERE / "eval" / "mle_frontier.json"
GAN_F   = HERE / "eval" / "gan_results.json"
REPORT  = HERE / "02_slice_eval_report.md"

DECISION_GATE = {
    "unique_ratio_gt_mle": True,
    "self_bleu3_lt_mle": True,
    "syntax_rate_gte_mle_x09": True,
    "no_d_shortcut": True,   # delta < 0.3
}


def load_json(path: Path) -> dict:
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def mle_best_config(mle_results: dict) -> dict:
    """Return the config with highest unique_ratio across all seeds."""
    best = {"unique_ratio": 0}
    for seed, res in mle_results.items():
        for config, m in res["frontier"].items():
            if m["unique_ratio"] > best["unique_ratio"]:
                best = {**m, "seed": seed, "config": config}
    return best


def gan_aggregate(gan_results: dict) -> dict:
    """Aggregate GAN metrics across seeds (mean ± std)."""
    import statistics
    keys = ["unique_ratio", "self_bleu3", "token_entropy", "syntax_validity_rate"]
    agg = {}
    for k in keys:
        vals = []
        for seed, res in gan_results.items():
            v = res["metrics"].get(k)
            if v is not None:
                vals.append(v)
        if vals:
            agg[k] = {
                "mean": statistics.mean(vals),
                "std": statistics.stdev(vals) if len(vals) > 1 else 0.0,
                "best": max(vals),
                "worst": min(vals),
            }
    return agg


def decision_gate(mle_best: dict, gan_agg: dict, gan_results: dict) -> tuple[bool, list[str]]:
    reasons = []
    passed = True

    mle_ur = mle_best.get("unique_ratio", 0)
    gan_ur  = gan_agg.get("unique_ratio", {}).get("best", 0)
    if gan_ur > mle_ur:
        reasons.append(f"PASS: GAN unique_ratio ({gan_ur:.3f}) > MLE ({mle_ur:.3f})")
    else:
        reasons.append(f"FAIL: GAN unique_ratio ({gan_ur:.3f}) <= MLE ({mle_ur:.3f})")
        passed = False

    mle_sb = mle_best.get("self_bleu3", 1)
    gan_sb  = gan_agg.get("self_bleu3", {}).get("best", 1)
    if gan_sb < mle_sb:
        reasons.append(f"PASS: GAN self_bleu3 ({gan_sb:.3f}) < MLE ({mle_sb:.3f})")
    else:
        reasons.append(f"FAIL: GAN self_bleu3 ({gan_sb:.3f}) >= MLE ({mle_sb:.3f})")
        passed = False

    mle_sy = mle_best.get("syntax_validity_rate", 0)
    gan_sy  = gan_agg.get("syntax_validity_rate", {}).get("mean", 0)
    threshold = mle_sy * 0.9
    if gan_sy >= threshold:
        reasons.append(f"PASS: GAN syntax_rate ({gan_sy:.3f}) >= MLE*0.9 ({threshold:.3f})")
    else:
        reasons.append(f"FAIL: GAN syntax_rate ({gan_sy:.3f}) < MLE*0.9 ({threshold:.3f})")
        passed = False

    # D shortcut check
    deltas = []
    for seed, res in gan_results.items():
        sc = res.get("d_shortcut", {})
        delta = sc.get("delta_D_real_softened")
        if delta is not None:
            deltas.append(delta)
    avg_delta = sum(deltas) / len(deltas) if deltas else 0
    if avg_delta < 0.3:
        reasons.append(f"PASS: No D shortcut (avg delta={avg_delta:.3f} < 0.3)")
    else:
        reasons.append(f"FAIL: D shortcut detected (avg delta={avg_delta:.3f} >= 0.3)")
        passed = False

    # Hard collapse check
    all_ur = [res["metrics"].get("unique_ratio", 1) for res in gan_results.values()]
    if all(ur < 0.3 for ur in all_ur):
        reasons.append("FAIL: Mode collapse in all seeds (unique_ratio < 0.3)")
        passed = False

    return passed, reasons


def write_report(mle_results: dict, gan_results: dict,
                 mle_best: dict, gan_agg: dict,
                 gate_passed: bool, gate_reasons: list[str]):
    lines = [
        "# 02 — De-risk Vertical Slice: Evaluation Report",
        "",
        f"**Decision: {'PASS — proceed to Phase 03 full scale' if gate_passed else 'FAIL — do not scale GAN'}**",
        "",
        "---",
        "",
        "## MLE Baseline Results",
        "",
        "| Seed | Best Config | unique_ratio | self_bleu3 | syntax_rate |",
        "|---|---|---:|---:|---:|",
    ]
    for seed, res in mle_results.items():
        best_cfg = max(res["frontier"].items(), key=lambda x: x[1]["unique_ratio"])
        m = best_cfg[1]
        lines.append(f"| {seed} | {best_cfg[0]} | {m['unique_ratio']:.3f} | "
                     f"{m['self_bleu3']:.3f} | {m['syntax_validity_rate']:.3f} |")

    lines += [
        "",
        f"**MLE Best Overall:** unique_ratio={mle_best.get('unique_ratio', 0):.3f}  "
        f"self_bleu3={mle_best.get('self_bleu3', 0):.3f}  "
        f"syntax={mle_best.get('syntax_validity_rate', 0):.3f}",
        "",
        "---",
        "",
        "## Gumbel-SeqGAN Results",
        "",
        "| Metric | Mean | Std | Best | Worst |",
        "|---|---:|---:|---:|---:|",
    ]
    for k, v in gan_agg.items():
        lines.append(f"| {k} | {v['mean']:.3f} | {v['std']:.3f} | {v['best']:.3f} | {v['worst']:.3f} |")

    lines += ["", "### D Shortcut Diagnostic", ""]
    for seed, res in gan_results.items():
        sc = res.get("d_shortcut", {})
        lines.append(f"- Seed {seed}: D_real={sc.get('D_real', '?')}  "
                     f"D_softened={sc.get('D_softened', '?')}  "
                     f"delta={sc.get('delta_D_real_softened', '?')}  "
                     f"shortcut={sc.get('shortcut_detected', '?')}")

    lines += [
        "",
        "---",
        "",
        "## Decision Gate",
        "",
    ]
    for r in gate_reasons:
        icon = "OK" if r.startswith("PASS") else "FAIL"
        lines.append(f"- [{icon}] {r}")

    lines += [
        "",
        f"**Overall: {'PASS' if gate_passed else 'FAIL'}**",
        "",
        "---",
        "",
        "## Collapse Check per Seed",
        "",
        "| Seed | unique_ratio | collapse_detected |",
        "|---|---:|---|",
    ]
    for seed, res in gan_results.items():
        ur = res["metrics"].get("unique_ratio", 0)
        col = res.get("collapse_detected", False)
        lines.append(f"| {seed} | {ur:.3f} | {col} |")

    lines += [
        "",
        "---",
        "",
        "## Recommendation",
        "",
    ]
    if gate_passed:
        lines += [
            "GAN architecture shows improvement over MLE in diversity metrics without collapse.",
            "Proceed to Phase 03: Full Data Foundation at scale.",
        ]
    else:
        lines += [
            "GAN does not demonstrate sufficient advantage over MLE baseline.",
            "Options:",
            "1. Fix architecture issues (D shortcut, collapse) and re-run this slice",
            "2. Proceed with MLE-only approach for Phase 03",
        ]

    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"Report saved: {REPORT}")


def main():
    print("Phase 02 — Evaluation")

    if not MLE_F.exists():
        print(f"ERROR: MLE frontier not found: {MLE_F}")
        return
    if not GAN_F.exists():
        print(f"ERROR: GAN results not found: {GAN_F}")
        return

    mle_results = load_json(MLE_F)
    gan_results  = load_json(GAN_F)

    mle_best = mle_best_config(mle_results)
    gan_agg  = gan_aggregate(gan_results)

    gate_passed, gate_reasons = decision_gate(mle_best, gan_agg, gan_results)

    print("\n-- Decision Gate --")
    for r in gate_reasons:
        print(f"  {r}")
    print(f"\nOverall: {'PASS' if gate_passed else 'FAIL'}")

    write_report(mle_results, gan_results, mle_best, gan_agg, gate_passed, gate_reasons)


if __name__ == "__main__":
    main()
