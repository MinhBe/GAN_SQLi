from __future__ import annotations

import csv
import contextlib
import io
import os
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path("/workspace/Timeline")
WAFAMOLE = ROOT / "Reproduction" / "external" / "WAF-A-MoLE"
RESULTS = ROOT / "Reproduction" / "results"
LOGS = ROOT / "Reproduction" / "logs"
REPORTS = ROOT / "Reports"
CONFIGS = ROOT / "Reproduction" / "configs"
POLICY = ROOT / "Reproduction" / "original_repro" / "WAFAMOLE_ORIGINAL_REPRO_POLICY.md"
RECOVERY = ROOT / "RECOVERY.md"
TIMELINE_MD = ROOT / "TIMELINE.md"
AUDIT = ROOT / "TRAJECTORY_AUDIT.md"

PAYLOAD = "UNION SELECT 1"
EVALUATOR_ID = "wafamole_original_runtime_probe_v1"


def run(args: list[str], cwd: Path | None = None, timeout: int = 60) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        cwd=str(cwd) if cwd else None,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def model_path(name: str) -> Path:
    return WAFAMOLE / "wafamole" / "models" / "custom" / "example_models" / name


def version_rows() -> list[dict[str, str]]:
    imports = ["numpy", "scipy", "sklearn", "joblib", "sqlparse", "networkx", "click", "keras", "tensorflow"]
    rows = []
    for module in imports:
        try:
            imported = __import__(module)
            version = getattr(imported, "__version__", "unknown")
            status = "ok"
            error = ""
        except Exception as exc:  # noqa: BLE001
            version = ""
            status = "failed"
            error = f"{type(exc).__name__}: {str(exc)[:180]}"
        rows.append({"module": module, "status": status, "version": version, "error": error})
    return rows


def try_model_status() -> list[dict[str, str]]:
    sys.path.insert(0, str(WAFAMOLE))
    from wafamole.models.custom.mlbasedwaf.mbwrapper import MLBasedWAFWrapper  # type: ignore
    from wafamole.models.custom.token.token_based import TokenClassifierWrapper  # type: ignore

    candidates = [
        ("token", "naive_bayes_trained.dump", TokenClassifierWrapper),
        ("token", "random_forest_trained.dump", TokenClassifierWrapper),
        ("token", "lin_svm_trained.dump", TokenClassifierWrapper),
        ("token", "gauss_svm_trained.dump", TokenClassifierWrapper),
        ("mlbasedwaf", "mlbasedwaf_svc.dump", MLBasedWAFWrapper),
        ("mlbasedwaf", "mlbasedwaf_svc_sqliv3.dump", MLBasedWAFWrapper),
        ("mlbasedwaf", "mlbasedwaf_svc_sqliv5.dump", MLBasedWAFWrapper),
        ("mlbasedwaf", "mlbasedwaf_sgd.dump", MLBasedWAFWrapper),
        ("mlbasedwaf", "mlbasedwaf_ada.dump", MLBasedWAFWrapper),
    ]
    rows = []
    for model_type, model_name, wrapper in candidates:
        started = time.time()
        try:
            model = wrapper().load(str(model_path(model_name)))
            confidence = float(model.classify(PAYLOAD))
            status = "ok"
            error_type = ""
            error_summary = ""
            confidence_summary = f"{confidence:.6f}"
        except Exception as exc:  # noqa: BLE001
            status = "failed"
            error_type = type(exc).__name__
            error_summary = str(exc).replace("\n", " ")[:240]
            confidence_summary = ""
        rows.append(
            {
                "model_type": model_type,
                "model_name": model_name,
                "status": status,
                "confidence_on_probe": confidence_summary,
                "error_type": error_type,
                "error_summary": error_summary,
                "elapsed_seconds": f"{time.time() - started:.3f}",
            }
        )
    return rows


def try_guided_engine(model_rows: list[dict[str, str]]) -> list[dict[str, str]]:
    ok_rows = [row for row in model_rows if row["status"] == "ok"]
    if not ok_rows:
        return [
            {
                "status": "skipped",
                "model_type": "",
                "model_name": "",
                "max_rounds": "0",
                "round_size": "0",
                "threshold": "0.5",
                "confidence": "",
                "payload_sha256": "",
                "error_type": "NoRunnableBundledModel",
                "error_summary": "No bundled model loaded and classified successfully in the original-faithful runtime.",
            }
        ]

    sys.path.insert(0, str(WAFAMOLE))
    from wafamole.evasion import EvasionEngine  # type: ignore
    from wafamole.models.custom.mlbasedwaf.mbwrapper import MLBasedWAFWrapper  # type: ignore
    from wafamole.models.custom.token.token_based import TokenClassifierWrapper  # type: ignore

    selected = ok_rows[0]
    wrapper = TokenClassifierWrapper if selected["model_type"] == "token" else MLBasedWAFWrapper
    try:
        model = wrapper().load(str(model_path(selected["model_name"])))
        with contextlib.redirect_stdout(io.StringIO()):
            confidence, payload = EvasionEngine(model).evaluate(PAYLOAD, max_rounds=3, round_size=2, timeout=20, threshold=0.5)
        import hashlib
        threshold_reached = float(confidence) < 0.5

        return [
            {
                "status": "ok_threshold_reached" if threshold_reached else "ok_no_threshold",
                "model_type": selected["model_type"],
                "model_name": selected["model_name"],
                "max_rounds": "3",
                "round_size": "2",
                "threshold": "0.5",
                "confidence": f"{float(confidence):.6f}",
                "payload_sha256": hashlib.sha256(payload.encode("utf-8", errors="replace")).hexdigest(),
                "error_type": "",
                "error_summary": "",
            }
        ]
    except Exception as exc:  # noqa: BLE001
        return [
            {
                "status": "failed",
                "model_type": selected["model_type"],
                "model_name": selected["model_name"],
                "max_rounds": "3",
                "round_size": "2",
                "threshold": "0.5",
                "confidence": "",
                "payload_sha256": "",
                "error_type": type(exc).__name__,
                "error_summary": str(exc).replace("\n", " ")[:240],
            }
        ]


def write_config() -> None:
    CONFIGS.mkdir(parents=True, exist_ok=True)
    text = """evaluator_id: wafamole_original_runtime_probe_v1
scope: original_faithful_wafamole_runtime
runtime:
  dockerfile: Timeline/Reproduction/original_repro/Dockerfile.wafamole-legacy
  python: "3.7.4"
  scikit_learn_target: "0.21.1"
sources:
  wafamole_code: Timeline/Reproduction/external/WAF-A-MoLE
  wafamole_dataset: Timeline/Reproduction/external/wafamole-dataset
probe:
  bundled_models: true
  guided_engine_smoke: true
reporting:
  include_payload_text_in_reports: false
  include_payload_hashes: true
"""
    (CONFIGS / "wafamole_original_runtime_config.yaml").write_text(text, encoding="utf-8")


def write_outputs(version: list[dict[str, str]], model: list[dict[str, str]], guided: list[dict[str, str]]) -> int:
    RESULTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_config()
    write_csv(RESULTS / "wafamole_original_runtime_versions.csv", version, list(version[0].keys()))
    write_csv(RESULTS / "wafamole_original_model_status.csv", model, list(model[0].keys()))
    write_csv(RESULTS / "wafamole_original_guided_smoke.csv", guided, list(guided[0].keys()))

    model_ok = sum(1 for row in model if row["status"] == "ok")
    guided_ok = sum(1 for row in guided if row["status"].startswith("ok_"))
    guided_threshold = sum(1 for row in guided if row["status"] == "ok_threshold_reached")
    status = "guided_engine_smoke_no_evasion" if guided_ok and not guided_threshold else ("guided_engine_smoke_with_evasion" if guided_threshold else ("partial_original_runtime_reproduction" if model_ok else "blocked_original_runtime"))
    metric = {
        "evaluator_id": EVALUATOR_ID,
        "status": status,
        "model_candidates": str(len(model)),
        "model_ok": str(model_ok),
        "model_failed": str(len(model) - model_ok),
        "guided_smoke_ok": str(guided_ok),
        "guided_threshold_reached": str(guided_threshold),
        "payload_text_logged": "false",
    }
    write_csv(RESULTS / "wafamole_original_runtime_metrics.csv", [metric], list(metric.keys()))

    report = f"""# WAF-A-MoLE Original Runtime Probe

## Summary

This probe uses an original-faithful legacy Docker runtime for WAF-A-MoLE: Python 3.7.x and scikit-learn 0.21.1, matching the upstream README and the bundled pickle provenance observed in the modern-runtime failure.

## Metrics

| Metric | Value |
| --- | ---: |
| Candidate bundled models | {metric['model_candidates']} |
| Models loaded and classified | {metric['model_ok']} |
| Models failed | {metric['model_failed']} |
| Guided engine smoke OK | {metric['guided_smoke_ok']} |
| Guided threshold reached | {metric['guided_threshold_reached']} |

Status: `{metric['status']}`.

## Outputs

- `Timeline/Reproduction/configs/wafamole_original_runtime_config.yaml`
- `Timeline/Reproduction/results/wafamole_original_runtime_versions.csv`
- `Timeline/Reproduction/results/wafamole_original_model_status.csv`
- `Timeline/Reproduction/results/wafamole_original_guided_smoke.csv`
- `Timeline/Reproduction/results/wafamole_original_runtime_metrics.csv`

## Claim Rule

Only claim the guided engine path is running if `guided_smoke_ok` is greater than zero. Claim evasion success only if `guided_threshold_reached` is greater than zero.
"""
    (REPORTS / "03c_wafamole_original_runtime_report.md").write_text(report, encoding="utf-8")
    (RESULTS / "wafamole_original_runtime_report.md").write_text(report, encoding="utf-8")

    log_lines = [
        f"evaluator_id={EVALUATOR_ID}",
        f"status={metric['status']}",
        f"model_ok={metric['model_ok']}",
        f"guided_smoke_ok={metric['guided_smoke_ok']}",
        "payload_text_logged=false",
    ]
    (LOGS / "wafamole_original_runtime_probe.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")
    return 0 if guided_ok else 2


def main() -> int:
    os.chdir(str(WAFAMOLE))
    version = version_rows()
    model = try_model_status()
    guided = try_guided_engine(model)
    return write_outputs(version, model, guided)


if __name__ == "__main__":
    sys.exit(main())
