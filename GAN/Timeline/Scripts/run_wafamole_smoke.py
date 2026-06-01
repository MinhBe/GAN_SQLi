from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import random
import subprocess
import sys
from collections import Counter
from pathlib import Path

import run_real_waf_smoke as waf


TIMELINE = Path(__file__).resolve().parents[1]
REPRO = TIMELINE / "Reproduction"
REPORTS = TIMELINE / "Reports"
CONFIGS = REPRO / "configs"
RESULTS = REPRO / "results"
LOGS = REPRO / "logs"
EXTERNAL = REPRO / "external"
WAFAMOLE = EXTERNAL / "WAF-A-MoLE"
WAFAMOLE_DATASET = EXTERNAL / "wafamole-dataset"
BASELINE_SAMPLES = RESULTS / "baseline_samples.csv"
RECOVERY = TIMELINE / "RECOVERY.md"
TIMELINE_MD = TIMELINE / "TIMELINE.md"
AUDIT = TIMELINE / "TRAJECTORY_AUDIT.md"

EVALUATOR_ID = "week5_wafamole_smoke_v1"
DEFAULT_OPERATOR_SAMPLES = 40


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def decode_payload(encoded: str) -> str:
    return base64.b64decode(encoded.encode("ascii")).decode("utf-8", errors="replace")


def encode_payload(payload: str) -> str:
    return base64.b64encode(payload.encode("utf-8", errors="replace")).decode("ascii")


def sha256_text(payload: str) -> str:
    return hashlib.sha256(payload.encode("utf-8", errors="replace")).hexdigest()


def git_head(path: Path) -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=path,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=30,
    )
    return result.stdout.strip() if result.returncode == 0 else "unknown"


def count_lines(path: Path) -> int:
    with path.open("rb") as f:
        return sum(1 for _ in f)


def model_path(name: str) -> Path:
    return WAFAMOLE / "wafamole" / "models" / "custom" / "example_models" / name


def try_model_status() -> list[dict[str, str]]:
    sys.path.insert(0, str(WAFAMOLE))
    import sklearn  # type: ignore
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
        status = "ok"
        error_type = ""
        error_summary = ""
        try:
            model = wrapper().load(str(model_path(model_name)))
            confidence = model.classify("UNION SELECT 1")
            confidence_summary = f"{float(confidence):.6f}"
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
                "runtime_sklearn_version": sklearn.__version__,
            }
        )
    return rows


def load_seed_payloads(limit: int) -> list[dict[str, str]]:
    rows = []
    for row in read_csv(BASELINE_SAMPLES):
        if row["baseline_id"] != "template_rule":
            continue
        rows.append(
            {
                "source_sample_hash": row["normalized_sha256"],
                "source_id": row["source_id"],
                "category": row["category"],
                "dbms": row["dbms"],
                "_payload": decode_payload(row["payload_base64"]),
            }
        )
        if len(rows) >= limit:
            break
    return rows


def build_operator_samples(limit: int) -> list[dict[str, str]]:
    random.seed(20260529)
    sys.path.insert(0, str(WAFAMOLE))
    from wafamole.payloadfuzzer.sqlfuzzer import SqlFuzzer  # type: ignore

    seeds = load_seed_payloads(max(10, limit))
    samples = []
    seen: set[str] = set()
    idx = 1
    round_number = 0
    while len(samples) < limit and round_number < 8:
        round_number += 1
        for seed in seeds:
            fuzzer = SqlFuzzer(seed["_payload"])
            payload = seed["_payload"]
            for _ in range(round_number):
                payload = fuzzer.fuzz()
            if payload == seed["_payload"]:
                continue
            payload_hash = sha256_text(payload)
            if payload_hash in seen:
                continue
            seen.add(payload_hash)
            samples.append(
                {
                    "sample_id": f"wafamole-operator-{idx:03d}",
                    "source_sample_hash": seed["source_sample_hash"],
                    "source_id": seed["source_id"],
                    "category": seed["category"],
                    "dbms": seed["dbms"],
                    "_payload": payload,
                    "payload_sha256": payload_hash,
                    "normalized_sha256": payload_hash,
                    "mutation_rounds": str(round_number),
                }
            )
            idx += 1
            if len(samples) >= limit:
                return samples
    return samples


def evaluate_operator_samples(samples: list[dict[str, str]], host_port: int) -> list[dict[str, str]]:
    rows = []
    for sample in samples:
        status, decision, error = waf.probe_waf(sample["_payload"], host_port, sample["sample_id"])
        rows.append(
            {
                "sample_id": sample["sample_id"],
                "source_sample_hash": sample["source_sample_hash"],
                "source_id": sample["source_id"],
                "category": sample["category"],
                "dbms": sample["dbms"],
                "payload_sha256": sample["payload_sha256"],
                "normalized_sha256": sample["normalized_sha256"],
                "payload_base64": encode_payload(sample["_payload"]),
                "mutation_rounds": sample["mutation_rounds"],
                "wafamole_mode": "operator_only_sqlfuzzer",
                "guided_model_used": "false",
                "real_waf_mode": "modsecurity_crs_docker",
                "http_status": str(status),
                "real_waf_decision": decision,
                "real_waf_rule_ids": "not_collected_payload_safe",
                "error": error,
            }
        )
    return rows


def summarize(model_rows: list[dict[str, str]], sample_rows: list[dict[str, str]], dataset_rows: list[dict[str, str]]) -> dict[str, str]:
    decisions = Counter(row["real_waf_decision"] for row in sample_rows)
    model_status = Counter(row["status"] for row in model_rows)
    return {
        "evaluator_id": EVALUATOR_ID,
        "wafamole_code_commit": git_head(WAFAMOLE),
        "wafamole_dataset_commit": git_head(WAFAMOLE_DATASET),
        "model_candidates": str(len(model_rows)),
        "model_ok": str(model_status.get("ok", 0)),
        "model_failed": str(model_status.get("failed", 0)),
        "operator_samples": str(len(sample_rows)),
        "operator_real_waf_blocked": str(decisions.get("block", 0)),
        "operator_real_waf_allowed": str(decisions.get("allow", 0)),
        "operator_real_waf_errors": str(decisions.get("error", 0)),
        "dataset_attacks_rows": dataset_rows[0]["attacks_rows"],
        "dataset_sane_rows": dataset_rows[0]["sane_rows"],
        "guided_reproduction_status": "blocked_by_example_model_runtime",
        "payload_text_logged": "false",
    }


def dataset_inventory_rows() -> list[dict[str, str]]:
    return [
        {
            "dataset": "wafamole-dataset",
            "source_url": "https://github.com/blindusername/wafamole-dataset",
            "commit_hash": git_head(WAFAMOLE_DATASET),
            "attacks_rows": str(count_lines(WAFAMOLE_DATASET / "attacks.sql")),
            "sane_rows": str(count_lines(WAFAMOLE_DATASET / "sane.sql")),
            "readme_note": "repository readme points to https://github.com/zangobot/wafamole_dataset",
            "status": "cloned_counted",
        }
    ]


def write_config(args: argparse.Namespace) -> None:
    text = f"""evaluator_id: {EVALUATOR_ID}
scope: wafamole_smoke_and_failure_report
external_sources:
  wafamole_code: Timeline/Reproduction/external/WAF-A-MoLE
  wafamole_dataset: Timeline/Reproduction/external/wafamole-dataset
  wafamole_code_commit: {git_head(WAFAMOLE)}
  wafamole_dataset_commit: {git_head(WAFAMOLE_DATASET)}
waf:
  engine: modsecurity_crs
  mode: modsecurity_crs_docker
  image: {args.image}
  host_port: {args.host_port}
  backend_port: {args.backend_port}
smoke:
  operator_samples: {args.operator_samples}
  guided_model_probe_payload: hash_only_not_reported
reporting:
  include_payload_text_in_reports: false
  include_payload_base64_in_machine_csv: true
  include_hashes: true
  include_rule_ids: false
guardrails:
  - Do not label operator-only SqlFuzzer output as full guided WAF-A-MoLE evasion.
  - Do not print detailed payload strings in markdown reports or logs.
  - Treat payload CSVs as local machine artifacts, not public report content.
"""
    CONFIGS.mkdir(parents=True, exist_ok=True)
    (CONFIGS / "wafamole_smoke_config.yaml").write_text(text, encoding="utf-8")


def write_outputs(
    model_rows: list[dict[str, str]],
    sample_rows: list[dict[str, str]],
    dataset_rows: list[dict[str, str]],
    metric: dict[str, str],
) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_csv(RESULTS / "wafamole_model_status.csv", model_rows, list(model_rows[0].keys()))
    write_csv(RESULTS / "wafamole_dataset_inventory.csv", dataset_rows, list(dataset_rows[0].keys()))
    write_csv(
        RESULTS / "wafamole_operator_smoke_samples.csv",
        sample_rows,
        [
            "sample_id",
            "source_sample_hash",
            "source_id",
            "category",
            "dbms",
            "payload_sha256",
            "normalized_sha256",
            "payload_base64",
            "mutation_rounds",
            "wafamole_mode",
            "guided_model_used",
            "real_waf_mode",
            "http_status",
            "real_waf_decision",
            "real_waf_rule_ids",
            "error",
        ],
    )
    write_csv(RESULTS / "wafamole_smoke_metrics.csv", [metric], list(metric.keys()))

    failed_types = Counter(row["error_type"] for row in model_rows if row["status"] == "failed")
    failure_summary = ", ".join(f"{k}: {v}" for k, v in sorted(failed_types.items()) if k) or "none"
    report = f"""# WAF-A-MoLE Smoke / Failure Report

## Summary

WAF-A-MoLE code and dataset were cloned and inspected. The full guided reproduction is blocked in the current Python environment because the bundled example classifiers are old serialized sklearn/Keras artifacts and do not load or predict cleanly under the current runtime.

The SQL mutation operator layer itself was smoke-tested through the same local ModSecurity + OWASP CRS WAF path used in Week 5. This operator-only run is not reported as full guided WAF-A-MoLE evasion.

## Source Status

| Source | Commit | Status |
| --- | --- | --- |
| WAF-A-MoLE code | `{metric['wafamole_code_commit']}` | cloned |
| wafamole-dataset | `{metric['wafamole_dataset_commit']}` | cloned/counted |

## Dataset Counts

| File | Rows |
| --- | ---: |
| attacks.sql | {metric['dataset_attacks_rows']} |
| sane.sql | {metric['dataset_sane_rows']} |

## Model Probe

| Metric | Value |
| --- | ---: |
| Candidate example models | {metric['model_candidates']} |
| Models loaded and classified probe | {metric['model_ok']} |
| Models failed | {metric['model_failed']} |

Failure types: `{failure_summary}`.

## Operator-Only WAF Smoke

| Metric | Value |
| --- | ---: |
| Operator samples | {metric['operator_samples']} |
| Real WAF blocked | {metric['operator_real_waf_blocked']} |
| Real WAF allowed | {metric['operator_real_waf_allowed']} |
| Real WAF errors | {metric['operator_real_waf_errors']} |

## Outputs

- `Timeline/Reproduction/configs/wafamole_smoke_config.yaml`
- `Timeline/Reproduction/results/wafamole_model_status.csv`
- `Timeline/Reproduction/results/wafamole_dataset_inventory.csv`
- `Timeline/Reproduction/results/wafamole_operator_smoke_samples.csv`
- `Timeline/Reproduction/results/wafamole_smoke_metrics.csv`
- `Timeline/Reproduction/logs/wafamole_smoke.log`

## Decision

Use WAF-A-MoLE as a documented strong baseline candidate with an operator-layer smoke result and a concrete environment blocker. Do not claim full guided WAF-A-MoLE reproduction until a compatible legacy environment is created or the bundled models are regenerated.
"""
    (RESULTS / "wafamole_smoke_test.md").write_text(report, encoding="utf-8")
    (REPORTS / "03b_wafamole_smoke_report.md").write_text(report, encoding="utf-8")

    log_lines = [
        f"timestamp={waf.now_iso()}",
        f"evaluator_id={EVALUATOR_ID}",
        "payload_text_logged=false",
        "guided_reproduction_status=blocked_by_example_model_runtime",
        f"model_ok={metric['model_ok']}",
        f"model_failed={metric['model_failed']}",
        f"operator_samples={metric['operator_samples']}",
        f"operator_real_waf_blocked={metric['operator_real_waf_blocked']}",
        f"operator_real_waf_allowed={metric['operator_real_waf_allowed']}",
        f"operator_real_waf_errors={metric['operator_real_waf_errors']}",
    ]
    (LOGS / "wafamole_smoke.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")


def update_recovery(metric: dict[str, str]) -> None:
    text = f"""# Recovery

- Current phase: WAF-A-MoLE smoke/failure report completed
- Last completed step: WAF-A-MoLE code/dataset cloned, model probe attempted, operator-only fuzzer smoke evaluated through ModSecurity + OWASP CRS Docker
- Next exact step: Begin selected GSQLi reproduction planning
- Updated artifacts:
  - `Timeline/RECOVERY.md`
  - `Timeline/TIMELINE.md`
  - `Timeline/TRAJECTORY_AUDIT.md`
  - `Timeline/Reproduction/configs/wafamole_smoke_config.yaml`
  - `Timeline/Reproduction/results/wafamole_model_status.csv`
  - `Timeline/Reproduction/results/wafamole_dataset_inventory.csv`
  - `Timeline/Reproduction/results/wafamole_operator_smoke_samples.csv`
  - `Timeline/Reproduction/results/wafamole_smoke_metrics.csv`
  - `Timeline/Reproduction/results/wafamole_smoke_test.md`
  - `Timeline/Reproduction/logs/wafamole_smoke.log`
  - `Timeline/Reports/03b_wafamole_smoke_report.md`
- WAF-A-MoLE source commits:
  - Code: `{metric['wafamole_code_commit']}`
  - Dataset: `{metric['wafamole_dataset_commit']}`
- Model probe:
  - Candidate models: {metric['model_candidates']}
  - Loaded/classified: {metric['model_ok']}
  - Failed: {metric['model_failed']}
- Operator-only WAF smoke:
  - Samples: {metric['operator_samples']}
  - Blocked: {metric['operator_real_waf_blocked']}
  - Allowed: {metric['operator_real_waf_allowed']}
  - Errors: {metric['operator_real_waf_errors']}
- Blockers:
  - Full guided WAF-A-MoLE reproduction is blocked by bundled example model runtime incompatibility.
  - Operator-only SqlFuzzer smoke must not be reported as full guided evasion.
- Last updated: `{waf.now_iso()}`
"""
    RECOVERY.write_text(text, encoding="utf-8")


def append_timeline(metric: dict[str, str]) -> None:
    addition = f"""

### WAF-A-MoLE Smoke / Failure Completion

- Cloned WAF-A-MoLE code at `{metric['wafamole_code_commit']}`.
- Cloned wafamole-dataset at `{metric['wafamole_dataset_commit']}`.
- Counted wafamole-dataset rows: attacks {metric['dataset_attacks_rows']}, sane {metric['dataset_sane_rows']}.
- Probed {metric['model_candidates']} bundled example models; {metric['model_ok']} loaded/classified and {metric['model_failed']} failed under the current runtime.
- Ran operator-only SqlFuzzer smoke through ModSecurity + OWASP CRS Docker: samples {metric['operator_samples']}, blocked {metric['operator_real_waf_blocked']}, allowed {metric['operator_real_waf_allowed']}, errors {metric['operator_real_waf_errors']}.
- Wrote `Timeline/Reports/03b_wafamole_smoke_report.md`.
- Full guided WAF-A-MoLE reproduction remains blocked until a compatible model runtime is created or models are regenerated.
"""
    with TIMELINE_MD.open("a", encoding="utf-8") as f:
        f.write(addition)


def update_audit(metric: dict[str, str]) -> None:
    text = AUDIT.read_text(encoding="utf-8")
    if "Timeline/Reproduction/results/wafamole_smoke_metrics.csv" not in text:
        text = text.replace(
            "20. `Timeline/Reports/03_baseline_results.md`",
            "20. `Timeline/Reports/03_baseline_results.md`\n21. `Timeline/Reproduction/results/wafamole_smoke_metrics.csv`\n22. `Timeline/Reports/03b_wafamole_smoke_report.md`",
        )
    text = text.replace(
        "- Week 5: template/rule and deterministic mutation baselines completed through the ModSecurity + OWASP CRS Docker evaluator path.",
        "- WAF-A-MoLE smoke/failure report completed: code/dataset cloned, example model runtime blocker recorded, operator-only SqlFuzzer smoke evaluated through ModSecurity + OWASP CRS Docker.",
    )
    if "- WAF-A-MoLE operator smoke rows:" not in text:
        text = text.replace(
            "- Week 5 baseline rows: 120 across template_rule and deterministic_mutation\n",
            f"- Week 5 baseline rows: 120 across template_rule and deterministic_mutation\n- WAF-A-MoLE operator smoke rows: {metric['operator_samples']} with blocked {metric['operator_real_waf_blocked']} and allowed {metric['operator_real_waf_allowed']}\n",
        )
    else:
        text = re_sub_wafamole_audit_counts(text, metric)
    text = text.replace(
        "| Next step | WAF-A-MoLE smoke/failure report or selected GSQLi reproduction plan | Work claims model superiority before WAF-A-MoLE/GSQLi artifacts exist |",
        "| Next step | Selected GSQLi reproduction plan | Work claims model superiority before GSQLi artifacts exist |",
    )
    text = text.replace("`2026-05-29T07:04:40+07:00`", f"`{waf.now_iso()}`")
    AUDIT.write_text(text, encoding="utf-8")


def re_sub_wafamole_audit_counts(text: str, metric: dict[str, str]) -> str:
    import re

    return re.sub(
        r"- WAF-A-MoLE operator smoke rows: \d+ with blocked \d+ and allowed \d+",
        f"- WAF-A-MoLE operator smoke rows: {metric['operator_samples']} with blocked {metric['operator_real_waf_blocked']} and allowed {metric['operator_real_waf_allowed']}",
        text,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run WAF-A-MoLE smoke/failure checks.")
    parser.add_argument("--image", default=waf.DEFAULT_IMAGE)
    parser.add_argument("--container-name", default="gan-sqli-crs-wafamole-smoke")
    parser.add_argument("--host-port", type=int, default=18084)
    parser.add_argument("--backend-port", type=int, default=18085)
    parser.add_argument("--operator-samples", type=int, default=DEFAULT_OPERATOR_SAMPLES)
    parser.add_argument("--keep-container", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_config(args)
    dataset_rows = dataset_inventory_rows()
    model_rows = try_model_status()
    operator_samples = build_operator_samples(args.operator_samples)

    ok, docker_message = waf.docker_available()
    if not ok:
        raise RuntimeError(docker_message)

    backend = waf.start_backend(args.backend_port)
    container_id = ""
    try:
        container_id = waf.start_waf_container(args.image, args.container_name, args.host_port, args.backend_port)
        waf.wait_for_waf(args.host_port)
        sample_rows = evaluate_operator_samples(operator_samples, args.host_port)
    finally:
        if container_id and not args.keep_container:
            waf.remove_existing_container(args.container_name)
        backend.shutdown()
        backend.server_close()

    metric = summarize(model_rows, sample_rows, dataset_rows)
    write_outputs(model_rows, sample_rows, dataset_rows, metric)
    update_recovery(metric)
    append_timeline(metric)
    update_audit(metric)
    print(f"model_ok={metric['model_ok']}")
    print(f"model_failed={metric['model_failed']}")
    print(f"operator_samples={metric['operator_samples']}")
    print(f"operator_blocked={metric['operator_real_waf_blocked']}")
    print(f"operator_allowed={metric['operator_real_waf_allowed']}")
    print(f"operator_errors={metric['operator_real_waf_errors']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
