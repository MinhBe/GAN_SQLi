from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch

from .config import ProjectConfig
from .dataset import read_parquet
from .evaluator import EvaluatorConfig, evaluate_dataframe
from .models import ActionGenerator, AnchorInfiller, score_with_d_scorer
from .reporting import update_timeline_progress, write_json, write_slice_report
from .taxonomy import apply_action


def _base_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates(subset=["payload_id"]).reset_index(drop=True)


def _sample_prediction_rows(df: pd.DataFrame, sample_count: int | None, seed: int) -> pd.DataFrame:
    if sample_count is None or sample_count <= 0 or len(df) == sample_count:
        return df.reset_index(drop=True)
    replace = len(df) < sample_count
    return (
        df.sample(n=sample_count, replace=replace, random_state=seed)
        .reset_index(drop=True)
    )


def _evaluate(name: str, df: pd.DataFrame, refs: list[str]) -> dict[str, Any]:
    metrics = evaluate_dataframe(df, references=refs)
    return {"name": name, "metrics": metrics}


def rule_tamper_baseline(df: pd.DataFrame, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for _, row in _base_rows(df).iterrows():
        actions = df[df["payload_id"].eq(row["payload_id"])]["action_type"].tolist()
        actions = [action for action in actions if action != "identity"]
        action_type = str(rng.choice(actions)) if actions else "identity"
        rows.append(
            {
                **row.to_dict(),
                "action_type": action_type,
                "generated_payload": apply_action(row["payload_norm"], action_type, seed=seed),
            }
        )
    return pd.DataFrame(rows)


def conditional_mle_baseline(df: pd.DataFrame) -> pd.DataFrame:
    rows = []
    global_action = str(df["action_type"].mode().iloc[0])
    for _, row in _base_rows(df).iterrows():
        condition = (
            (df["technique_primary"].eq(row["technique_primary"]))
            & (df["db_hint"].eq(row["db_hint"]))
            & (df["action_family"].eq(row["action_family"]))
        )
        subset = df[condition]
        action_type = str(subset["action_type"].mode().iloc[0]) if not subset.empty else global_action
        rows.append(
            {
                **row.to_dict(),
                "action_type": action_type,
                "generated_payload": apply_action(row["payload_norm"], action_type),
            }
        )
    return pd.DataFrame(rows)


def anchor_baseline(config: ProjectConfig, df: pd.DataFrame) -> pd.DataFrame | None:
    path = config.model_dir / "anchor_infiller.json"
    if not path.exists():
        return None
    model = AnchorInfiller.load(path)
    rows = []
    for _, row in _base_rows(df).iterrows():
        action_type = model.predict_row(row)
        rows.append(
            {
                **row.to_dict(),
                "action_type": action_type,
                "generated_payload": apply_action(row["payload_norm"], action_type),
            }
        )
    return pd.DataFrame(rows)


def d_scorer_rerank(config: ProjectConfig, df: pd.DataFrame) -> pd.DataFrame | None:
    path = config.model_dir / "d_scorer" / "paired_d_scorer.pt"
    if not path.exists():
        return None
    scored = df.copy()
    scored["d_score"] = score_with_d_scorer(scored, path, device=config.torch_device())
    rows = []
    for _, group in scored.groupby("payload_id"):
        chosen = group.sort_values("d_score", ascending=False).iloc[0]
        rows.append(chosen.to_dict())
    return pd.DataFrame(rows)


def action_gan_baseline(config: ProjectConfig, df: pd.DataFrame, seed: int) -> pd.DataFrame | None:
    path = config.model_dir / "action_gan" / f"seed_{seed}" / "best.pt"
    if not path.exists():
        return None
    checkpoint = torch.load(path, map_location=config.torch_device())
    cond_vocab = checkpoint["condition_vocab"]
    action_vocab = checkpoint["action_vocab"]
    inverse_action_vocab = {idx: action for action, idx in action_vocab.items()}
    model = ActionGenerator(len(cond_vocab), len(action_vocab)).to(config.torch_device())
    model.load_state_dict(checkpoint["state_dict"])
    model.eval()

    rows = []
    with torch.no_grad():
        for _, row in _base_rows(df).iterrows():
            key = AnchorInfiller.key(row)
            cond = torch.tensor([cond_vocab.get(key, 0)], dtype=torch.long, device=config.torch_device())
            logits = model.logits(cond)
            action_type = inverse_action_vocab[int(torch.argmax(logits, dim=-1).item())]
            rows.append(
                {
                    **row.to_dict(),
                    "action_type": action_type,
                    "generated_payload": apply_action(row["payload_norm"], action_type, seed=seed),
                }
            )
    return pd.DataFrame(rows)


def decide_slice(results: dict[str, Any]) -> dict[str, Any]:
    h4 = results.get("H4_gumbel_action_surgery_gan")
    h3 = results.get("H3_anchor_only_action_infiller")
    h2 = results.get("H2_mle_d_scorer")
    h1 = results.get("H1_conditional_mle")

    candidates = {
        key: value["metrics"]["composite"]["score"]
        for key, value in results.items()
        if value and "metrics" in value
    }
    best = max(candidates, key=candidates.get) if candidates else None
    if h4 and h3 and h2:
        h4_score = h4["metrics"]["composite"]["score"]
        if (
            h4["metrics"]["composite"]["passed_floors"]
            and h4_score > h3["metrics"]["composite"]["score"]
            and h4_score >= h2["metrics"]["composite"]["score"]
        ):
            return {"decision": "GUMBEL_ACTION_PASS", "reason": "H4 passed floors and beat H3/H2 on the registered composite."}
    if (
        h2
        and h2["metrics"]["composite"]["passed_floors"]
        and (
            not h1
            or h2["metrics"]["composite"]["score"]
            >= h1["metrics"]["composite"]["score"]
        )
    ):
        return {"decision": "D_SCORER_MAIN", "reason": "D-as-scorer is the strongest available passing baseline."}
    if h1 and h1["metrics"]["composite"]["passed_floors"]:
        return {"decision": "MLE_MAIN", "reason": "Conditional MLE passed floors; Gumbel did not beat it."}
    return {"decision": "INCONCLUSIVE", "reason": f"No candidate passed all floors; best observed baseline was {best}."}


def run_benchmark(
    config: ProjectConfig,
    split: str = "test",
    seed: int | None = None,
    sample_count: int | None = None,
    write_slice_artifacts: bool = True,
) -> dict[str, Any]:
    seed = config.seed if seed is None else seed
    df = read_parquet(config.slice_dir / f"action_surgery_{split}.parquet")
    refs = df["payload_norm"].astype(str).tolist()

    outputs: dict[str, pd.DataFrame | None] = {
        "H5_rule_tamper_baseline": rule_tamper_baseline(df, seed),
        "H1_conditional_mle": conditional_mle_baseline(df),
        "H3_anchor_only_action_infiller": anchor_baseline(config, df),
        "H2_mle_d_scorer": d_scorer_rerank(config, df),
        "H4_gumbel_action_surgery_gan": action_gan_baseline(config, df, seed),
    }
    outputs = {
        name: _sample_prediction_rows(pred, sample_count, seed)
        if pred is not None
        else None
        for name, pred in outputs.items()
    }

    results = {
        name: _evaluate(name, pred, refs) if pred is not None else None
        for name, pred in outputs.items()
    }
    decision = decide_slice({name: value for name, value in results.items() if value is not None})
    comparison = {
        "split": split,
        "seed": seed,
        "sample_count": sample_count,
        "baselines": results,
        "decision": decision,
    }
    if not write_slice_artifacts:
        return comparison

    write_json(comparison, config.eval_dir / "slice" / "baseline_comparison.json")
    write_json(decision, config.eval_dir / "slice" / "decision.json")

    primary_metrics = next(
        value["metrics"]
        for value in results.values()
        if value is not None and value["name"] == "H1_conditional_mle"
    )
    split_sizes = {
        item: len(read_parquet(config.slice_dir / f"action_surgery_{item}.parquet"))
        for item in ("train", "dev", "test")
        if (config.slice_dir / f"action_surgery_{item}.parquet").exists()
    }
    write_slice_report(
        config.report_dir / "02_de_risk_action_surgery_slice.md",
        primary_metrics,
        decision,
        split_sizes,
    )
    update_timeline_progress(
        config,
        phase_id="G02",
        status="completed" if decision["decision"] != "INCONCLUSIVE" else "failed",
        progress_percent=40,
        gate_result=decision["decision"],
        evidence_artifacts=[
            "data/gumbel/slice/action_surgery_train.parquet",
            "data/gumbel/slice/action_surgery_dev.parquet",
            "data/gumbel/slice/action_surgery_test.parquet",
            "eval/gumbel/slice/baseline_comparison.json",
            "eval/gumbel/slice/decision.json",
            "reports/gumbel/02_de_risk_action_surgery_slice.md",
        ],
        notes="G02 slice benchmark completed; run G03 multi-seed decision before scaling.",
    )
    return comparison


def _mean_std_ci(values: list[float]) -> dict[str, float]:
    arr = np.asarray(values, dtype=float)
    mean = float(arr.mean()) if len(arr) else 0.0
    std = float(arr.std(ddof=1)) if len(arr) > 1 else 0.0
    ci95 = float(1.96 * std / np.sqrt(len(arr))) if len(arr) > 1 else 0.0
    return {"mean": mean, "std": std, "ci95": ci95}


def _phase03_decision(summary: dict[str, Any]) -> dict[str, Any]:
    baselines = summary["baselines"]
    available = {
        name: payload
        for name, payload in baselines.items()
        if payload["seeds_completed"] > 0
    }
    if not available:
        return {"decision": "INCONCLUSIVE", "reason": "No baselines completed."}

    scores = {
        name: payload["metrics"]["composite_score"]["mean"]
        for name, payload in available.items()
    }
    floor_rates = {
        name: payload["floor_pass_rate"]
        for name, payload in available.items()
    }

    h4 = available.get("H4_gumbel_action_surgery_gan")
    h3 = available.get("H3_anchor_only_action_infiller")
    h2 = available.get("H2_mle_d_scorer")
    if (
        h4
        and h3
        and h2
        and floor_rates["H4_gumbel_action_surgery_gan"] == 1.0
        and scores["H4_gumbel_action_surgery_gan"] > scores["H3_anchor_only_action_infiller"]
        and scores["H4_gumbel_action_surgery_gan"] >= scores["H2_mle_d_scorer"]
    ):
        return {
            "decision": "GUMBEL_ACTION_PASS",
            "reason": "H4 mean composite passed all floors and beat H3/H2 across seeds.",
        }

    best = max(scores, key=scores.get)
    h1_score = scores.get("H1_conditional_mle", float("-inf"))
    h2_score = scores.get("H2_mle_d_scorer", float("-inf"))
    if (
        h2
        and floor_rates.get("H2_mle_d_scorer", 0.0) >= 2 / 3
        and h2_score >= h1_score
    ):
        return {
            "decision": "D_SCORER_MAIN",
            "reason": "H4 did not clear the pre-scale condition; D-as-scorer improved over conditional MLE.",
        }
    if floor_rates.get("H1_conditional_mle", 0.0) >= 2 / 3:
        return {
            "decision": "MLE_MAIN",
            "reason": "Conditional MLE passed floors and adversarial action generation did not beat simpler baselines.",
        }
    return {
        "decision": "INCONCLUSIVE",
        "reason": f"No baseline met the registered reliability rule; best mean score was {best}.",
    }


def write_phase03_report(path: Path, summary: dict[str, Any], decision: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = []
    for name, payload in summary["baselines"].items():
        score = payload["metrics"]["composite_score"]
        rows.append(
            f"| {name} | {payload['seeds_completed']} | {payload['floor_pass_rate']:.3f} | "
            f"{score['mean']:.4f} | {score['std']:.4f} | {score['ci95']:.4f} |"
        )
    text = """# 03 Decision Gate Report

## Decision

- Decision: `{decision}`
- Reason: {reason}
- Seeds: {seeds}
- Samples per seed: {sample_count}

## Mean/Std/CI

| Baseline | Seeds | Floor pass rate | Composite mean | Std | CI95 |
| --- | ---: | ---: | ---: | ---: | ---: |
{rows}
""".format(
        decision=decision["decision"],
        reason=decision["reason"],
        seeds=", ".join(str(seed) for seed in summary["seeds"]),
        sample_count=summary["sample_count"],
        rows="\n".join(rows),
    )
    path.write_text(text, encoding="utf-8")


def run_phase03_decision_gate(
    config: ProjectConfig,
    seeds: list[int],
    split: str = "test",
    sample_count: int = 5_000,
) -> dict[str, Any]:
    per_seed = [
        run_benchmark(
            config,
            split=split,
            seed=seed,
            sample_count=sample_count,
            write_slice_artifacts=False,
        )
        for seed in seeds
    ]

    baseline_names = sorted(
        {
            name
            for result in per_seed
            for name, payload in result["baselines"].items()
            if payload is not None
        }
    )
    baselines: dict[str, Any] = {}
    for name in baseline_names:
        values_by_metric: dict[str, list[float]] = {
            "composite_score": [],
            "round_trip_success": [],
            "parse_success": [],
            "action_validity": [],
            "unique_ratio": [],
            "self_bleu3": [],
            "near_copy_rate": [],
            "condition_accuracy": [],
        }
        floor_passes = []
        completed = 0
        for result in per_seed:
            payload = result["baselines"].get(name)
            if payload is None:
                continue
            completed += 1
            metrics = payload["metrics"]
            values_by_metric["composite_score"].append(metrics["composite"]["score"])
            floor_passes.append(bool(metrics["composite"]["passed_floors"]))
            for metric in values_by_metric:
                if metric == "composite_score":
                    continue
                values_by_metric[metric].append(float(metrics.get(metric, 0.0)))
        baselines[name] = {
            "seeds_completed": completed,
            "floor_pass_rate": float(np.mean(floor_passes)) if floor_passes else 0.0,
            "metrics": {
                metric: _mean_std_ci(values)
                for metric, values in values_by_metric.items()
            },
        }

    summary = {
        "split": split,
        "seeds": seeds,
        "sample_count": sample_count,
        "minimum_registered_samples_per_seed": 5_000,
        "baselines": baselines,
        "per_seed": per_seed,
    }
    decision = _phase03_decision(summary)
    write_json(summary, config.eval_dir / "phase03" / "statistical_summary.json")
    write_json(decision, config.eval_dir / "phase03" / "decision.json")
    write_phase03_report(
        config.report_dir / "03_decision_gate_report.md",
        summary,
        decision,
    )
    update_timeline_progress(
        config,
        phase_id="G03",
        status="completed",
        progress_percent=55,
        gate_result=decision["decision"],
        evidence_artifacts=[
            "eval/gumbel/phase03/decision.json",
            "eval/gumbel/phase03/statistical_summary.json",
            "reports/gumbel/03_decision_gate_report.md",
        ],
        notes="G03 multi-seed decision completed; do not scale Gumbel unless decision is GUMBEL_ACTION_PASS.",
    )
    return {"summary": summary, "decision": decision}
