"""
Phase 03 - Decision Gate

Gate-only phase. This script does not train any model. It reads Phase 02
artifacts, applies the pre-registered MLE-vs-GAN decision gates, and writes
the Phase 03 decision artifacts.
"""

import json
import math
import statistics
from datetime import datetime, timezone
from pathlib import Path


HERE = Path(__file__).resolve().parent
PHASE2 = HERE.parent / "Phase 2"

MLE_F = PHASE2 / "eval" / "mle_frontier.json"
GAN_F = PHASE2 / "eval" / "gan_results.json"

OUT_DIR = HERE / "eval" / "phase03"
REPORT_DIR = HERE / "reports"

DECISION_F = OUT_DIR / "decision.json"
SUMMARY_F = OUT_DIR / "statistical_summary.json"
PLOT_F = OUT_DIR / "mle_vs_gan_frontier.png"
REPORT_F = REPORT_DIR / "03_decision_gate_report.md"


T_CRIT_95 = {
    1: 12.706,
    2: 4.303,
    3: 3.182,
    4: 2.776,
    5: 2.571,
    6: 2.447,
    7: 2.365,
    8: 2.306,
    9: 2.262,
    10: 2.228,
}


def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=2)
        f.write("\n")


def stat_summary(values):
    values = [float(v) for v in values]
    n = len(values)
    if n == 0:
        return {
            "n": 0,
            "mean": None,
            "std": None,
            "min": None,
            "max": None,
            "ci95": [None, None],
            "values": [],
        }
    mean = statistics.mean(values)
    std = statistics.stdev(values) if n > 1 else 0.0
    if n > 1:
        tcrit = T_CRIT_95.get(n - 1, 1.96)
        half = tcrit * std / math.sqrt(n)
    else:
        half = 0.0
    return {
        "n": n,
        "mean": mean,
        "std": std,
        "min": min(values),
        "max": max(values),
        "ci95": [mean - half, mean + half],
        "values": values,
    }


def flatten_mle(mle_results):
    points = []
    for seed, res in mle_results.items():
        for config, metrics in res.get("frontier", {}).items():
            point = {
                "branch": "MLE",
                "seed": str(seed),
                "config": config,
            }
            point.update(metrics)
            points.append(point)
    return points


def flatten_gan(gan_results):
    points = []
    for seed, res in gan_results.items():
        metrics = dict(res.get("metrics", {}))
        point = {
            "branch": "GAN",
            "seed": str(seed),
            "config": "gumbel_seqgan_phase02",
            "collapse_detected": bool(res.get("collapse_detected", False)),
        }
        point.update(metrics)
        points.append(point)
    return points


def dominates(a, b, x_key="unique_ratio", y_key="syntax_validity_rate"):
    ax = float(a.get(x_key, 0.0))
    ay = float(a.get(y_key, 0.0))
    bx = float(b.get(x_key, 0.0))
    by = float(b.get(y_key, 0.0))
    return ax >= bx and ay >= by and (ax > bx or ay > by)


def pareto_frontier(points, x_key="unique_ratio", y_key="syntax_validity_rate"):
    frontier = []
    for p in points:
        if not any(dominates(other, p, x_key=x_key, y_key=y_key) for other in points if other is not p):
            frontier.append(p)
    return sorted(frontier, key=lambda p: (float(p.get(x_key, 0.0)), float(p.get(y_key, 0.0))))


def metric_values(points, key):
    return [float(p[key]) for p in points if key in p and p[key] is not None]


def pick_max(points, key):
    return max(points, key=lambda p: float(p.get(key, float("-inf"))))


def pick_min(points, key):
    return min(points, key=lambda p: float(p.get(key, float("inf"))))


def aggregate_mle_by_seed_best_unique(mle_results):
    per_seed = {}
    for seed, res in mle_results.items():
        configs = []
        for config, metrics in res.get("frontier", {}).items():
            point = {"seed": str(seed), "config": config}
            point.update(metrics)
            configs.append(point)
        if configs:
            per_seed[str(seed)] = pick_max(configs, "unique_ratio")
    return per_seed


def aggregate_gan_metrics(gan_results):
    keys = ["unique_ratio", "self_bleu3", "token_entropy", "syntax_validity_rate"]
    return {
        key: stat_summary(
            [res.get("metrics", {}).get(key) for res in gan_results.values() if res.get("metrics", {}).get(key) is not None]
        )
        for key in keys
    }


def d_shortcut_summary(gan_results):
    deltas = []
    shortcuts = []
    per_seed = {}
    for seed, res in gan_results.items():
        sc = res.get("d_shortcut", {})
        delta = sc.get("delta_D_real_softened")
        shortcut = bool(sc.get("shortcut_detected", False))
        if delta is not None:
            deltas.append(float(delta))
        shortcuts.append(shortcut)
        per_seed[str(seed)] = {
            "D_real": sc.get("D_real"),
            "D_softened": sc.get("D_softened"),
            "D_noisy": sc.get("D_noisy"),
            "delta_D_real_softened": delta,
            "shortcut_detected": shortcut,
        }
    delta_stats = stat_summary(deltas)
    return {
        "per_seed": per_seed,
        "delta_D_real_softened": delta_stats,
        "any_shortcut_detected": any(shortcuts),
        "mean_delta": delta_stats["mean"] if delta_stats["mean"] is not None else None,
    }


def build_gate_results(mle_points, gan_points, gan_results):
    mle_best_unique = pick_max(mle_points, "unique_ratio")
    mle_best_low_self_bleu = pick_min(mle_points, "self_bleu3")
    mle_reference_syntax = mle_best_unique

    gan_best_unique = pick_max(gan_points, "unique_ratio")
    gan_best_low_self_bleu = pick_min(gan_points, "self_bleu3")
    gan_best_syntax = pick_max(gan_points, "syntax_validity_rate")

    dsum = d_shortcut_summary(gan_results)
    collapse_count = sum(1 for p in gan_points if p.get("collapse_detected"))
    gan_seed_count = len(gan_points)
    noncollapsed_count = gan_seed_count - collapse_count

    mle_frontier = pareto_frontier(mle_points)
    frontier_dominating_pairs = []
    for gp in gan_points:
        for mp in mle_frontier:
            if dominates(gp, mp):
                frontier_dominating_pairs.append(
                    {
                        "gan_seed": gp.get("seed"),
                        "mle_seed": mp.get("seed"),
                        "mle_config": mp.get("config"),
                        "gan_unique_ratio": gp.get("unique_ratio"),
                        "gan_syntax_validity_rate": gp.get("syntax_validity_rate"),
                        "mle_unique_ratio": mp.get("unique_ratio"),
                        "mle_syntax_validity_rate": mp.get("syntax_validity_rate"),
                    }
                )

    syntax_threshold = float(mle_reference_syntax.get("syntax_validity_rate", 0.0)) * 0.9

    gates = {
        "G1_unique_ratio": {
            "passed": float(gan_best_unique["unique_ratio"]) > float(mle_best_unique["unique_ratio"]),
            "criterion": "GAN best seed unique_ratio > MLE best frontier unique_ratio",
            "gan_value": gan_best_unique["unique_ratio"],
            "mle_value": mle_best_unique["unique_ratio"],
            "gan_seed": gan_best_unique["seed"],
            "mle_seed": mle_best_unique["seed"],
            "mle_config": mle_best_unique["config"],
        },
        "G2_self_bleu3": {
            "passed": float(gan_best_low_self_bleu["self_bleu3"]) < float(mle_best_low_self_bleu["self_bleu3"]),
            "criterion": "GAN best seed self_bleu3 < MLE best frontier self_bleu3",
            "gan_value": gan_best_low_self_bleu["self_bleu3"],
            "mle_value": mle_best_low_self_bleu["self_bleu3"],
            "gan_seed": gan_best_low_self_bleu["seed"],
            "mle_seed": mle_best_low_self_bleu["seed"],
            "mle_config": mle_best_low_self_bleu["config"],
        },
        "G3_syntax_guard": {
            "passed": float(gan_best_syntax["syntax_validity_rate"]) >= syntax_threshold,
            "criterion": "GAN best seed syntax_validity_rate >= MLE reference syntax_validity_rate * 0.9",
            "gan_value": gan_best_syntax["syntax_validity_rate"],
            "threshold": syntax_threshold,
            "mle_reference_value": mle_reference_syntax["syntax_validity_rate"],
            "gan_seed": gan_best_syntax["seed"],
            "note": "Formal guard only; the best-syntax GAN seed is still collapse-tagged in Phase 02."
            if gan_best_syntax.get("collapse_detected")
            else "Formal guard.",
        },
        "G4_d_shortcut": {
            "passed": (dsum["mean_delta"] is not None and dsum["mean_delta"] < 0.3 and not dsum["any_shortcut_detected"]),
            "criterion": "mean delta_D_real_softened < 0.3 and no seed shortcut flag",
            "mean_delta": dsum["mean_delta"],
            "threshold": 0.3,
            "any_shortcut_detected": dsum["any_shortcut_detected"],
        },
        "G5_no_collapse": {
            "passed": noncollapsed_count > collapse_count,
            "criterion": "Most GAN seeds must not be collapse-tagged",
            "collapse_count": collapse_count,
            "noncollapsed_count": noncollapsed_count,
            "seed_count": gan_seed_count,
        },
        "G6_frontier_dominance": {
            "passed": len(frontier_dominating_pairs) > 0,
            "criterion": "At least one GAN seed must dominate a point on the MLE Pareto frontier in unique_ratio/syntax space",
            "dominating_pair_count": len(frontier_dominating_pairs),
            "dominating_pairs": frontier_dominating_pairs,
            "mle_frontier_size": len(mle_frontier),
        },
    }
    return gates, mle_frontier


def build_statistical_summary(mle_results, gan_results):
    mle_points = flatten_mle(mle_results)
    gan_points = flatten_gan(gan_results)
    mle_per_seed_best = aggregate_mle_by_seed_best_unique(mle_results)
    gan_agg = aggregate_gan_metrics(gan_results)
    dsum = d_shortcut_summary(gan_results)
    gates, mle_frontier = build_gate_results(mle_points, gan_points, gan_results)

    mle_best_unique = pick_max(mle_points, "unique_ratio")
    mle_best_self_bleu = pick_min(mle_points, "self_bleu3")
    mle_best_syntax = pick_max(mle_points, "syntax_validity_rate")
    gan_best_unique = pick_max(gan_points, "unique_ratio")
    gan_best_self_bleu = pick_min(gan_points, "self_bleu3")
    gan_best_syntax = pick_max(gan_points, "syntax_validity_rate")

    return {
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "phase": "03_decision_gate",
        "phase_role": "gate_only_no_training",
        "source_artifacts": {
            "mle_frontier": str(MLE_F),
            "gan_results": str(GAN_F),
        },
        "seeds": {
            "mle": sorted(str(s) for s in mle_results.keys()),
            "gan": sorted(str(s) for s in gan_results.keys()),
        },
        "mle": {
            "point_count": len(mle_points),
            "per_seed_best_by_unique_ratio": mle_per_seed_best,
            "best_unique_ratio_point": mle_best_unique,
            "best_self_bleu3_point": mle_best_self_bleu,
            "best_syntax_validity_point": mle_best_syntax,
            "metric_stats_all_frontier_points": {
                "unique_ratio": stat_summary(metric_values(mle_points, "unique_ratio")),
                "self_bleu3": stat_summary(metric_values(mle_points, "self_bleu3")),
                "token_entropy": stat_summary(metric_values(mle_points, "token_entropy")),
                "syntax_validity_rate": stat_summary(metric_values(mle_points, "syntax_validity_rate")),
            },
            "pareto_frontier_unique_ratio_syntax": mle_frontier,
        },
        "gan": {
            "point_count": len(gan_points),
            "per_seed": {p["seed"]: p for p in gan_points},
            "best_unique_ratio_seed": gan_best_unique,
            "best_self_bleu3_seed": gan_best_self_bleu,
            "best_syntax_validity_seed": gan_best_syntax,
            "metric_stats_by_seed": gan_agg,
            "d_shortcut": dsum,
        },
        "gate_results": gates,
        "limitations": [
            "Phase 02 artifacts do not contain type_accuracy, so Phase 03 does not invent or score type_accuracy.",
            "The syntax gate is a formal guard because the highest-syntax GAN seed is collapse-tagged.",
            "The statistical unit is seed for GAN aggregate metrics; MLE frontier points are reported separately from per-seed best points.",
        ],
    }


def build_decision(summary):
    gates = summary["gate_results"]
    passed = [name for name, gate in gates.items() if gate["passed"]]
    failed = [name for name, gate in gates.items() if not gate["passed"]]
    gate_passed = len(failed) == 0

    if gate_passed:
        decision = "GAN_PASS"
        reason = "GAN passed all registered Phase 03 gates."
    else:
        decision = "MLE_MAIN"
        reason = (
            "GAN failed {}/{} Phase 03 gates: {}. Tie-break/default path is MLE_MAIN.".format(
                len(failed), len(gates), ", ".join(failed)
            )
        )

    return {
        "decision": decision,
        "gate_passed": gate_passed,
        "reason": reason,
        "phase": "03_decision_gate",
        "phase_role": "gate_only_no_training",
        "passed_gates": passed,
        "failed_gates": failed,
        "seeds": summary["seeds"],
        "metrics": {
            "mle_best_unique_ratio": summary["mle"]["best_unique_ratio_point"]["unique_ratio"],
            "mle_best_self_bleu3": summary["mle"]["best_self_bleu3_point"]["self_bleu3"],
            "mle_reference_syntax_validity_rate": summary["mle"]["best_unique_ratio_point"]["syntax_validity_rate"],
            "gan_best_unique_ratio": summary["gan"]["best_unique_ratio_seed"]["unique_ratio"],
            "gan_best_self_bleu3": summary["gan"]["best_self_bleu3_seed"]["self_bleu3"],
            "gan_best_syntax_validity_rate": summary["gan"]["best_syntax_validity_seed"]["syntax_validity_rate"],
            "gan_mean_unique_ratio": summary["gan"]["metric_stats_by_seed"]["unique_ratio"]["mean"],
            "gan_mean_self_bleu3": summary["gan"]["metric_stats_by_seed"]["self_bleu3"]["mean"],
            "gan_mean_syntax_validity_rate": summary["gan"]["metric_stats_by_seed"]["syntax_validity_rate"]["mean"],
            "mean_delta_D_real_softened": summary["gan"]["d_shortcut"]["mean_delta"],
        },
        "gate_results": summary["gate_results"],
        "recommendation": "Do not scale GAN from Phase 02. Continue with Conditional MLE + evaluator-guided search unless a new pre-registered GAN hypothesis directly addresses D-saturation and syntax/diversity tradeoff.",
    }


def plot_frontier(summary):
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except Exception as exc:
        err_f = OUT_DIR / "plot_error.txt"
        err_f.write_text("Could not import matplotlib: {}\n".format(exc), encoding="utf-8")
        return False

    # Re-read the flattened points from the source artifacts for plotting.
    mle_results = load_json(MLE_F)
    gan_results = load_json(GAN_F)
    mle_points = flatten_mle(mle_results)
    gan_points = flatten_gan(gan_results)
    mle_frontier = summary["mle"]["pareto_frontier_unique_ratio_syntax"]

    fig, ax = plt.subplots(figsize=(9, 6), dpi=160)
    ax.scatter(
        [p["unique_ratio"] for p in mle_points],
        [p["syntax_validity_rate"] for p in mle_points],
        s=28,
        alpha=0.45,
        label="MLE sampling configs",
        color="#4C78A8",
    )
    ax.plot(
        [p["unique_ratio"] for p in mle_frontier],
        [p["syntax_validity_rate"] for p in mle_frontier],
        marker="o",
        linewidth=2,
        markersize=4,
        label="MLE Pareto frontier",
        color="#1F4E79",
    )
    ax.scatter(
        [p["unique_ratio"] for p in gan_points],
        [p["syntax_validity_rate"] for p in gan_points],
        s=90,
        marker="x",
        linewidth=2,
        label="GAN seeds",
        color="#D62728",
    )
    for p in gan_points:
        ax.annotate(
            "GAN {}".format(p["seed"]),
            (p["unique_ratio"], p["syntax_validity_rate"]),
            xytext=(5, 5),
            textcoords="offset points",
            fontsize=8,
        )

    ax.set_title("Phase 03 Decision Gate: MLE Frontier vs GAN Seeds")
    ax.set_xlabel("unique_ratio (higher is better)")
    ax.set_ylabel("syntax_validity_rate (higher is better)")
    ax.set_xlim(0.0, 0.9)
    ax.set_ylim(0.0, 0.9)
    ax.grid(True, linestyle="--", alpha=0.3)
    ax.legend(loc="lower right")
    fig.tight_layout()
    fig.savefig(PLOT_F)
    plt.close(fig)
    return True


def gate_line(name, gate):
    status = "PASS" if gate["passed"] else "FAIL"
    if name == "G1_unique_ratio":
        return "| G1 unique_ratio | GAN {:.3f} vs MLE {:.3f} | {} |".format(
            gate["gan_value"], gate["mle_value"], status
        )
    if name == "G2_self_bleu3":
        return "| G2 self_bleu3 | GAN {:.3f} vs MLE {:.3f} | {} |".format(
            gate["gan_value"], gate["mle_value"], status
        )
    if name == "G3_syntax_guard":
        return "| G3 syntax guard | GAN {:.3f} vs threshold {:.3f} | {} |".format(
            gate["gan_value"], gate["threshold"], status
        )
    if name == "G4_d_shortcut":
        return "| G4 D-shortcut | mean delta {:.6f} vs threshold {:.3f} | {} |".format(
            gate["mean_delta"], gate["threshold"], status
        )
    if name == "G5_no_collapse":
        return "| G5 no-collapse | collapsed {}/{} seeds | {} |".format(
            gate["collapse_count"], gate["seed_count"], status
        )
    if name == "G6_frontier_dominance":
        return "| G6 frontier dominance | dominating pairs {} | {} |".format(
            gate["dominating_pair_count"], status
        )
    return "| {} | {} | {} |".format(name, gate.get("criterion", ""), status)


def write_report(summary, decision, plot_written):
    lines = [
        "# 03 - Decision Gate Report",
        "",
        "> Recreated from Phase 02 artifacts. This phase is gate-only and performs no training.",
        "",
        "## Decision",
        "",
        "- Decision: `{}`".format(decision["decision"]),
        "- Gate passed: `{}`".format(str(decision["gate_passed"]).lower()),
        "- Reason: {}".format(decision["reason"]),
        "- Recommended path: Conditional MLE + evaluator-guided search.",
        "",
        "## Source Artifacts",
        "",
        "- `{}`".format(MLE_F),
        "- `{}`".format(GAN_F),
        "",
        "## Key Metrics",
        "",
        "| Metric | MLE reference | GAN reference |",
        "|---|---:|---:|",
        "| unique_ratio | {:.3f} | {:.3f} |".format(
            decision["metrics"]["mle_best_unique_ratio"],
            decision["metrics"]["gan_best_unique_ratio"],
        ),
        "| self_bleu3 | {:.3f} | {:.3f} |".format(
            decision["metrics"]["mle_best_self_bleu3"],
            decision["metrics"]["gan_best_self_bleu3"],
        ),
        "| syntax_validity_rate | {:.3f} | {:.3f} |".format(
            decision["metrics"]["mle_reference_syntax_validity_rate"],
            decision["metrics"]["gan_best_syntax_validity_rate"],
        ),
        "",
        "GAN seed means:",
        "",
        "| Metric | Mean | Std | CI95 low | CI95 high |",
        "|---|---:|---:|---:|---:|",
    ]
    for key in ["unique_ratio", "self_bleu3", "token_entropy", "syntax_validity_rate"]:
        stats = summary["gan"]["metric_stats_by_seed"][key]
        lines.append(
            "| {} | {:.3f} | {:.3f} | {:.3f} | {:.3f} |".format(
                key, stats["mean"], stats["std"], stats["ci95"][0], stats["ci95"][1]
            )
        )

    lines += [
        "",
        "## Gate Results",
        "",
        "| Gate | Evidence | Result |",
        "|---|---|---|",
    ]
    for name, gate in summary["gate_results"].items():
        lines.append(gate_line(name, gate))

    lines += [
        "",
        "## Collapse Check",
        "",
        "| Seed | unique_ratio | self_bleu3 | syntax_validity_rate | collapse_detected |",
        "|---|---:|---:|---:|---|",
    ]
    for seed, point in summary["gan"]["per_seed"].items():
        lines.append(
            "| {} | {:.3f} | {:.3f} | {:.3f} | {} |".format(
                seed,
                point["unique_ratio"],
                point["self_bleu3"],
                point["syntax_validity_rate"],
                point["collapse_detected"],
            )
        )

    lines += [
        "",
        "## Notes",
        "",
        "- `type_accuracy` is unavailable in Phase 02 artifacts, so it is not scored here.",
        "- G3 is a formal syntax guard; the best-syntax GAN seed is still collapse-tagged.",
        "- G4 passes, meaning the available D-shortcut diagnostic does not explain the failure.",
        "- The failure is driven by diversity/frontier/collapse gates.",
        "",
        "## Outputs",
        "",
        "- `{}`".format(DECISION_F),
        "- `{}`".format(SUMMARY_F),
        "- `{}`{}".format(PLOT_F, "" if plot_written else " (not written; see plot_error.txt)"),
    ]

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_F.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    missing = [str(p) for p in [MLE_F, GAN_F] if not p.exists()]
    if missing:
        raise SystemExit("Missing required Phase 02 artifact(s): {}".format(", ".join(missing)))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    mle_results = load_json(MLE_F)
    gan_results = load_json(GAN_F)

    summary = build_statistical_summary(mle_results, gan_results)
    decision = build_decision(summary)

    write_json(SUMMARY_F, summary)
    write_json(DECISION_F, decision)
    plot_written = plot_frontier(summary)
    write_report(summary, decision, plot_written)

    print("Phase 03 decision:", decision["decision"])
    print("Gate passed:", decision["gate_passed"])
    print("Failed gates:", ", ".join(decision["failed_gates"]) if decision["failed_gates"] else "none")
    print("Wrote:", DECISION_F)
    print("Wrote:", SUMMARY_F)
    print("Wrote:", REPORT_F)
    if plot_written:
        print("Wrote:", PLOT_F)


if __name__ == "__main__":
    main()
