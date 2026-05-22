from __future__ import annotations

from pathlib import Path
from typing import Any

from .config import ProjectConfig
from .dataset import (
    build_action_candidate_table,
    load_payloads,
    stratified_slice_split,
    write_slice_splits,
)
from .evaluator import EvaluatorConfig, evaluate_dataframe
from .reporting import write_evaluator_report, write_json, write_slice_report


def build_slice(
    config: ProjectConfig,
    input_paths: list[Path] | None = None,
    max_rows: int = 50_000,
    train_size: int = 5_000,
    dev_size: int = 1_000,
    test_size: int = 1_000,
) -> dict[str, Any]:
    payloads = load_payloads(
        config,
        input_paths=input_paths,
        max_rows=max_rows,
        sqli_only=True,
    )
    candidates = build_action_candidate_table(payloads, seed=config.seed)
    splits = stratified_slice_split(
        candidates,
        train_size=train_size,
        dev_size=dev_size,
        test_size=test_size,
        seed=config.seed,
    )
    write_slice_splits(splits, config)

    evaluator_config = EvaluatorConfig()
    evaluator_config.write(config.eval_dir / "evaluator_config.json")
    write_evaluator_report(
        config.report_dir / "06_evaluator_model_separation.md",
        evaluator_config.to_json(),
    )

    dev_metrics = evaluate_dataframe(
        splits["dev"],
        references=splits["train"]["payload_norm"].astype(str).tolist(),
        config=evaluator_config,
    )
    floors_passed = bool(dev_metrics.get("composite", {}).get("passed_floors"))
    initial_decision = {
        "decision": "SLICE_READY" if floors_passed else "STOP",
        "reason": "Evaluator floors passed on the dev slice."
        if floors_passed
        else "One or more evaluator floors failed on the dev slice.",
    }
    write_json(
        {
            "split_sizes": {name: int(len(df)) for name, df in splits.items()},
            "dev_metrics": dev_metrics,
            "initial_decision": initial_decision,
        },
        config.eval_dir / "slice" / "slice_build_summary.json",
    )
    write_slice_report(
        config.report_dir / "02_de_risk_action_surgery_slice.md",
        dev_metrics,
        initial_decision,
        {name: int(len(df)) for name, df in splits.items()},
    )
    return {
        "split_sizes": {name: int(len(df)) for name, df in splits.items()},
        "dev_metrics": dev_metrics,
        "decision": initial_decision,
    }
