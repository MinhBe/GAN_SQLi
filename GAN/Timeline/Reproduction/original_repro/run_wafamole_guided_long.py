from __future__ import annotations

import argparse
import contextlib
import csv
import hashlib
import io
import os
import sys
import time
from pathlib import Path


ROOT = Path("/workspace/Timeline")
WAFAMOLE = ROOT / "Reproduction" / "external" / "WAF-A-MoLE"
RESULTS = ROOT / "Reproduction" / "results"
LOGS = ROOT / "Reproduction" / "logs"
REPORTS = ROOT / "Reports"
CONFIGS = ROOT / "Reproduction" / "configs"
TIMELINE_MD = ROOT / "TIMELINE.md"
RECOVERY = ROOT / "RECOVERY.md"

EVALUATOR_ID = "wafamole_original_guided_long_v1"
PAYLOAD = "UNION SELECT 1"


def model_path(name: str) -> Path:
    return WAFAMOLE / "wafamole" / "models" / "custom" / "example_models" / name


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def load_model(model_type: str, model_name: str):
    sys.path.insert(0, str(WAFAMOLE))
    from wafamole.models.custom.mlbasedwaf.mbwrapper import MLBasedWAFWrapper  # type: ignore
    from wafamole.models.custom.token.token_based import TokenClassifierWrapper  # type: ignore

    wrapper = TokenClassifierWrapper if model_type == "token" else MLBasedWAFWrapper
    return wrapper().load(str(model_path(model_name)))


def runnable_models() -> list[tuple[str, str]]:
    return [
        ("token", "naive_bayes_trained.dump"),
        ("token", "random_forest_trained.dump"),
        ("token", "lin_svm_trained.dump"),
        ("token", "gauss_svm_trained.dump"),
        ("mlbasedwaf", "mlbasedwaf_ada.dump"),
    ]


def run_guided(model_type: str, model_name: str, max_rounds: int, round_size: int, timeout: int, threshold: float) -> dict[str, str]:
    sys.path.insert(0, str(WAFAMOLE))
    from wafamole.evasion import EvasionEngine  # type: ignore

    started = time.time()
    try:
        model = load_model(model_type, model_name)
        initial_confidence = float(model.classify(PAYLOAD))
        if initial_confidence <= threshold:
            return {
                "model_type": model_type,
                "model_name": model_name,
                "status": "skipped_initial_below_threshold",
                "initial_confidence": f"{initial_confidence:.6f}",
                "final_confidence": f"{initial_confidence:.6f}",
                "threshold": f"{threshold:.3f}",
                "threshold_reached": "false",
                "max_rounds": str(max_rounds),
                "round_size": str(round_size),
                "timeout_seconds": str(timeout),
                "elapsed_seconds": f"{time.time() - started:.3f}",
                "payload_sha256": hashlib.sha256(PAYLOAD.encode("utf-8")).hexdigest(),
                "error_type": "",
                "error_summary": "Initial payload already classified below threshold; skipped guided search for this model.",
            }

        with contextlib.redirect_stdout(io.StringIO()):
            confidence, payload = EvasionEngine(model).evaluate(
                PAYLOAD,
                max_rounds=max_rounds,
                round_size=round_size,
                timeout=timeout,
                threshold=threshold,
            )
        final_confidence = float(confidence)
        threshold_reached = final_confidence < threshold
        return {
            "model_type": model_type,
            "model_name": model_name,
            "status": "threshold_reached" if threshold_reached else "max_rounds_or_timeout_no_threshold",
            "initial_confidence": f"{initial_confidence:.6f}",
            "final_confidence": f"{final_confidence:.6f}",
            "threshold": f"{threshold:.3f}",
            "threshold_reached": str(threshold_reached).lower(),
            "max_rounds": str(max_rounds),
            "round_size": str(round_size),
            "timeout_seconds": str(timeout),
            "elapsed_seconds": f"{time.time() - started:.3f}",
            "payload_sha256": hashlib.sha256(payload.encode("utf-8", errors="replace")).hexdigest(),
            "error_type": "",
            "error_summary": "",
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "model_type": model_type,
            "model_name": model_name,
            "status": "failed",
            "initial_confidence": "",
            "final_confidence": "",
            "threshold": f"{threshold:.3f}",
            "threshold_reached": "false",
            "max_rounds": str(max_rounds),
            "round_size": str(round_size),
            "timeout_seconds": str(timeout),
            "elapsed_seconds": f"{time.time() - started:.3f}",
            "payload_sha256": "",
            "error_type": type(exc).__name__,
            "error_summary": str(exc).replace("\n", " ")[:240],
        }


def summarize(rows: list[dict[str, str]]) -> dict[str, str]:
    attempted = [row for row in rows if row["status"] not in {"skipped_initial_below_threshold"}]
    reached = [row for row in rows if row["status"] == "threshold_reached"]
    skipped = [row for row in rows if row["status"] == "skipped_initial_below_threshold"]
    failed = [row for row in rows if row["status"] == "failed"]
    no_threshold = [row for row in rows if row["status"] == "max_rounds_or_timeout_no_threshold"]
    return {
        "evaluator_id": EVALUATOR_ID,
        "models_total": str(len(rows)),
        "guided_attempted": str(len(attempted)),
        "threshold_reached": str(len(reached)),
        "skipped_initial_below_threshold": str(len(skipped)),
        "failed": str(len(failed)),
        "no_threshold": str(len(no_threshold)),
        "payload_text_logged": "false",
    }


def write_config(args: argparse.Namespace) -> None:
    CONFIGS.mkdir(parents=True, exist_ok=True)
    text = f"""evaluator_id: {EVALUATOR_ID}
scope: original_faithful_wafamole_guided_long
runtime:
  image: gan-sqli-wafamole-legacy:py37
  python: "3.7.4"
  scikit_learn: "0.21.1"
guided_run:
  payload: hash_only_not_reported
  max_rounds: {args.max_rounds}
  round_size: {args.round_size}
  timeout_seconds: {args.timeout}
  threshold: {args.threshold}
models:
  source: bundled WAF-A-MoLE example models
reporting:
  include_payload_text_in_reports: false
  include_payload_hashes: true
"""
    (CONFIGS / "wafamole_original_guided_long_config.yaml").write_text(text, encoding="utf-8")


def write_outputs(rows: list[dict[str, str]], metric: dict[str, str], args: argparse.Namespace) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_config(args)
    write_csv(RESULTS / "wafamole_original_guided_long_results.csv", rows, list(rows[0].keys()))
    write_csv(RESULTS / "wafamole_original_guided_long_metrics.csv", [metric], list(metric.keys()))

    table_rows = "\n".join(
        "| {model_type} | {model_name} | {status} | {initial_confidence} | {final_confidence} | {threshold_reached} | {elapsed_seconds} |".format(**row)
        for row in rows
    )
    report = f"""# WAF-A-MoLE Original Guided Long Run

## Summary

This run extends the original-faithful WAF-A-MoLE guided engine beyond the initial smoke probe. It uses the legacy Docker runtime and bundled upstream example models. Payload text is not written to reports or logs.

## Metrics

| Metric | Value |
| --- | ---: |
| Models total | {metric['models_total']} |
| Guided attempted | {metric['guided_attempted']} |
| Threshold reached | {metric['threshold_reached']} |
| Skipped, initial below threshold | {metric['skipped_initial_below_threshold']} |
| Failed | {metric['failed']} |
| No threshold reached | {metric['no_threshold']} |

## Per-Model Results

| Type | Model | Status | Initial confidence | Final confidence | Threshold reached | Seconds |
| --- | --- | --- | ---: | ---: | --- | ---: |
{table_rows}

## Claim Rule

Claim evasion success only for rows with `status=threshold_reached`. Rows with `skipped_initial_below_threshold` are not guided evasion successes because the starting payload was already below the classifier threshold.
"""
    (REPORTS / "03d_wafamole_original_guided_long_report.md").write_text(report, encoding="utf-8")
    (RESULTS / "wafamole_original_guided_long_report.md").write_text(report, encoding="utf-8")

    log_lines = [
        f"evaluator_id={EVALUATOR_ID}",
        f"models_total={metric['models_total']}",
        f"guided_attempted={metric['guided_attempted']}",
        f"threshold_reached={metric['threshold_reached']}",
        f"payload_text_logged={metric['payload_text_logged']}",
    ]
    (LOGS / "wafamole_original_guided_long.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")


def append_timeline(metric: dict[str, str], args: argparse.Namespace) -> None:
    addition = f"""

### WAF-A-MoLE Original Guided Long Run

- Continued original-faithful WAF-A-MoLE reproduction in Docker image `gan-sqli-wafamole-legacy:py37`.
- Ran bundled model guided attempts with max_rounds {args.max_rounds}, round_size {args.round_size}, timeout {args.timeout}s, threshold {args.threshold}.
- Models total: {metric['models_total']}; guided attempted: {metric['guided_attempted']}; threshold reached: {metric['threshold_reached']}; skipped initial-below-threshold: {metric['skipped_initial_below_threshold']}; failed: {metric['failed']}.
- Wrote `Timeline/Reproduction/results/wafamole_original_guided_long_results.csv`.
- Wrote `Timeline/Reproduction/results/wafamole_original_guided_long_metrics.csv`.
- Wrote `Timeline/Reports/03d_wafamole_original_guided_long_report.md`.
- Payload text was not written to reports or logs.
"""
    with TIMELINE_MD.open("a", encoding="utf-8") as f:
        f.write(addition)


def update_recovery(metric: dict[str, str], args: argparse.Namespace) -> None:
    text = f"""# Recovery

- Current phase: WAF-A-MoLE original guided long run completed
- Last completed step: Extended original-faithful guided WAF-A-MoLE run in legacy Docker runtime
- Next exact step: If threshold reached is zero, increase runtime/rounds for selected model or move to selected GSQLi reproduction planning with WAF-A-MoLE status recorded
- Runtime:
  - Docker image: `gan-sqli-wafamole-legacy:py37`
  - max_rounds: {args.max_rounds}
  - round_size: {args.round_size}
  - timeout_seconds: {args.timeout}
  - threshold: {args.threshold}
- Results:
  - Models total: {metric['models_total']}
  - Guided attempted: {metric['guided_attempted']}
  - Threshold reached: {metric['threshold_reached']}
  - Skipped initial-below-threshold: {metric['skipped_initial_below_threshold']}
  - Failed: {metric['failed']}
- Updated artifacts:
  - `Timeline/RECOVERY.md`
  - `Timeline/TIMELINE.md`
  - `Timeline/Reproduction/configs/wafamole_original_guided_long_config.yaml`
  - `Timeline/Reproduction/results/wafamole_original_guided_long_results.csv`
  - `Timeline/Reproduction/results/wafamole_original_guided_long_metrics.csv`
  - `Timeline/Reproduction/logs/wafamole_original_guided_long.log`
  - `Timeline/Reports/03d_wafamole_original_guided_long_report.md`
- Claim rule:
  - Only rows with `status=threshold_reached` count as WAF-A-MoLE evasion success.
  - Rows skipped because the initial payload was already below threshold are not guided evasion successes.
"""
    RECOVERY.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run longer original-faithful WAF-A-MoLE guided attempts.")
    parser.add_argument("--max-rounds", type=int, default=200)
    parser.add_argument("--round-size", type=int, default=20)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--threshold", type=float, default=0.5)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    os.chdir(str(WAFAMOLE))
    rows = [run_guided(model_type, model_name, args.max_rounds, args.round_size, args.timeout, args.threshold) for model_type, model_name in runnable_models()]
    metric = summarize(rows)
    write_outputs(rows, metric, args)
    append_timeline(metric, args)
    update_recovery(metric, args)
    print(f"models_total={metric['models_total']}")
    print(f"guided_attempted={metric['guided_attempted']}")
    print(f"threshold_reached={metric['threshold_reached']}")
    print(f"failed={metric['failed']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
