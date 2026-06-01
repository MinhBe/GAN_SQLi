from __future__ import annotations

import argparse
import base64
import csv
import http.server
import socketserver
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


TIMELINE = Path(__file__).resolve().parents[1]
REPRO = TIMELINE / "Reproduction"
DATA = TIMELINE / "Data"
CONFIGS = REPRO / "configs"
RESULTS = REPRO / "results"
LOGS = REPRO / "logs"

COMBINED = DATA / "processed" / "teacher_seed_sqli_normalized_combined.csv"
SAMPLES = RESULTS / "evaluator_smoke_samples.csv"
RECOVERY = TIMELINE / "RECOVERY.md"
TIMELINE_MD = TIMELINE / "TIMELINE.md"
AUDIT = TIMELINE / "TRAJECTORY_AUDIT.md"

EVALUATOR_ID = "week4_real_waf_smoke_v1"
DEFAULT_IMAGE = "owasp/modsecurity-crs:nginx"
DEFAULT_CONTAINER = "gan-sqli-crs-smoke"
DEFAULT_HOST_PORT = 18080
DEFAULT_BACKEND_PORT = 18081


class BackendHandler(http.server.BaseHTTPRequestHandler):
    def do_GET(self) -> None:  # noqa: N802
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"ok\n")

    def log_message(self, _format: str, *_args: object) -> None:
        return


class ReusableTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def now_iso() -> str:
    return datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: Path, rows: list[dict[str, str]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def run_command(args: list[str], timeout: int = 60, check: bool = False) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        args,
        check=check,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
    )


def decode_payload(encoded: str) -> str:
    return base64.b64decode(encoded.encode("ascii")).decode("utf-8", errors="replace")


def load_payloads_by_hash() -> dict[str, str]:
    payloads: dict[str, str] = {}
    for row in read_csv(COMBINED):
        payloads.setdefault(row["normalized_sha256"], decode_payload(row["normalized_payload_base64"]))
    return payloads


def load_samples() -> list[dict[str, str]]:
    payloads_by_hash = load_payloads_by_hash()
    rows = []
    for sample in read_csv(SAMPLES):
        payload = payloads_by_hash.get(sample["normalized_sha256"])
        if payload is None:
            raise RuntimeError(f"Missing payload for hash {sample['normalized_sha256']}")
        row = sample.copy()
        row["_payload"] = payload
        rows.append(row)
    return rows


def start_backend(port: int) -> ReusableTCPServer:
    server = ReusableTCPServer(("127.0.0.1", port), BackendHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server


def docker_available() -> tuple[bool, str]:
    version = run_command(["docker", "--version"], timeout=15)
    if version.returncode != 0:
        return False, version.stderr.strip() or version.stdout.strip() or "docker command unavailable"
    info = run_command(["docker", "info"], timeout=30)
    if info.returncode != 0:
        return False, info.stderr.strip() or info.stdout.strip() or "docker daemon unavailable"
    return True, version.stdout.strip()


def remove_existing_container(name: str) -> None:
    run_command(["docker", "rm", "-f", name], timeout=30)


def start_waf_container(image: str, name: str, host_port: int, backend_port: int) -> str:
    remove_existing_container(name)
    backend = f"http://host.docker.internal:{backend_port}"
    args = [
        "docker",
        "run",
        "--rm",
        "-d",
        "--name",
        name,
        "-p",
        f"127.0.0.1:{host_port}:8080",
        "-e",
        f"BACKEND={backend}",
        "-e",
        "MODSEC_RULE_ENGINE=on",
        "-e",
        "PARANOIA=1",
        "-e",
        "BLOCKING_PARANOIA=1",
        "-e",
        "ANOMALY_INBOUND=5",
        "-e",
        "ANOMALY_OUTBOUND=4",
        image,
    ]
    result = run_command(args, timeout=120)
    if result.returncode != 0:
        raise RuntimeError(result.stderr.strip() or result.stdout.strip() or "docker run failed")
    return result.stdout.strip()


def wait_for_waf(host_port: int, timeout_seconds: int = 45) -> None:
    deadline = time.time() + timeout_seconds
    last_error = ""
    while time.time() < deadline:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{host_port}/health", timeout=3) as response:
                if response.status < 500:
                    return
        except Exception as exc:  # noqa: BLE001
            last_error = str(exc)
        time.sleep(1)
    raise RuntimeError(f"WAF container did not become ready: {last_error}")


def classify_status(status: int) -> str:
    if status in {403, 406, 429}:
        return "block"
    if 200 <= status < 500:
        return "allow"
    return "error"


def probe_waf(payload: str, host_port: int, sample_id: str) -> tuple[int, str, str]:
    query = urllib.parse.urlencode({"q": payload})
    url = f"http://127.0.0.1:{host_port}/?{query}"
    request = urllib.request.Request(url, headers={"X-GSQLI-Sample": sample_id})
    try:
        with urllib.request.urlopen(request, timeout=10) as response:
            status = response.status
            response.read(512)
            return status, classify_status(status), ""
    except urllib.error.HTTPError as exc:
        exc.read(512)
        return exc.code, classify_status(exc.code), ""
    except Exception as exc:  # noqa: BLE001
        return 0, "error", type(exc).__name__


def evaluate(samples: list[dict[str, str]], host_port: int, image: str) -> tuple[list[dict[str, str]], dict[str, str]]:
    rows = []
    for sample in samples:
        status, decision, error = probe_waf(sample["_payload"], host_port, sample["sample_id"])
        local_decision = sample.get("local_waf_decision", "")
        rows.append(
            {
                "sample_id": sample["sample_id"],
                "split": sample["split"],
                "source_id": sample["source_id"],
                "category": sample["category"],
                "dbms": sample["dbms"],
                "normalized_sha256": sample["normalized_sha256"],
                "payload_sha256": sample["payload_sha256"],
                "validity": sample["validity"],
                "validity_labels": sample["validity_labels"],
                "local_waf_decision": local_decision,
                "real_waf_engine": "modsecurity_crs",
                "real_waf_image": image,
                "real_waf_mode": "modsecurity_crs_docker",
                "http_status": str(status),
                "real_waf_decision": decision,
                "real_waf_rule_ids": "not_collected_payload_safe",
                "error": error,
            }
        )
    return rows, summarize(rows, image)


def summarize(rows: list[dict[str, str]], image: str) -> dict[str, str]:
    decisions = Counter(row["real_waf_decision"] for row in rows)
    local = Counter(row["local_waf_decision"] for row in rows)
    agreement = sum(1 for row in rows if row["local_waf_decision"] == row["real_waf_decision"])
    split_counts = Counter(row["split"] for row in rows)
    return {
        "evaluator_id": EVALUATOR_ID,
        "waf_mode": "modsecurity_crs_docker",
        "waf_engine": "modsecurity_crs",
        "waf_image": image,
        "sample_count": str(len(rows)),
        "real_waf_blocked": str(decisions.get("block", 0)),
        "real_waf_allowed": str(decisions.get("allow", 0)),
        "real_waf_errors": str(decisions.get("error", 0)),
        "local_rule_blocked": str(local.get("block", 0)),
        "local_rule_allowed": str(local.get("allow", 0)),
        "local_real_agreement": str(agreement),
        "local_real_disagreement": str(len(rows) - agreement),
        "train_samples": str(split_counts.get("train", 0)),
        "validation_samples": str(split_counts.get("validation", 0)),
        "test_samples": str(split_counts.get("test", 0)),
        "payload_text_logged": "false",
        "rule_ids_collected": "false",
    }


def write_config(image: str, host_port: int, backend_port: int) -> None:
    text = f"""evaluator_id: {EVALUATOR_ID}
scope: week4_real_waf_smoke_test
input:
  smoke_samples: Timeline/Reproduction/results/evaluator_smoke_samples.csv
  combined_csv: Timeline/Data/processed/teacher_seed_sqli_normalized_combined.csv
waf:
  engine: modsecurity_crs
  mode: modsecurity_crs_docker
  image: {image}
  host_port: {host_port}
  backend_port: {backend_port}
  backend: http://host.docker.internal:{backend_port}
  environment:
    MODSEC_RULE_ENGINE: "on"
    PARANOIA: "1"
    BLOCKING_PARANOIA: "1"
    ANOMALY_INBOUND: "5"
    ANOMALY_OUTBOUND: "4"
reporting:
  include_payload_text: false
  include_hashes: true
  include_rule_ids: false
guardrails:
  - Run only against the local Docker WAF and local backend.
  - Do not print detailed payload strings in markdown reports or logs.
  - Keep local_rule_smoke artifacts separate from real WAF artifacts.
"""
    CONFIGS.mkdir(parents=True, exist_ok=True)
    (CONFIGS / "real_waf_smoke_config.yaml").write_text(text, encoding="utf-8")


def write_outputs(rows: list[dict[str, str]], metric: dict[str, str], container_id: str) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    write_csv(
        RESULTS / "real_waf_smoke_samples.csv",
        rows,
        [
            "sample_id",
            "split",
            "source_id",
            "category",
            "dbms",
            "normalized_sha256",
            "payload_sha256",
            "validity",
            "validity_labels",
            "local_waf_decision",
            "real_waf_engine",
            "real_waf_image",
            "real_waf_mode",
            "http_status",
            "real_waf_decision",
            "real_waf_rule_ids",
            "error",
        ],
    )
    write_csv(RESULTS / "real_waf_smoke_metrics.csv", [metric], list(metric.keys()))

    report = f"""# Real WAF Smoke Test

## Summary

The Week 4 evaluator sample was rerun against a real local WAF engine: ModSecurity with OWASP CRS in Docker. Payload text is decoded only in memory for HTTP requests and is not written to reports or logs.

## Metrics

| Metric | Value |
| --- | ---: |
| Samples | {metric['sample_count']} |
| Real WAF blocked | {metric['real_waf_blocked']} |
| Real WAF allowed | {metric['real_waf_allowed']} |
| Real WAF errors | {metric['real_waf_errors']} |
| Local-rule blocked | {metric['local_rule_blocked']} |
| Local-rule allowed | {metric['local_rule_allowed']} |
| Local/real agreement | {metric['local_real_agreement']} |
| Local/real disagreement | {metric['local_real_disagreement']} |

## Configuration

- Config: `Timeline/Reproduction/configs/real_waf_smoke_config.yaml`
- Samples: `Timeline/Reproduction/results/evaluator_smoke_samples.csv`
- WAF image: `{metric['waf_image']}`
- WAF mode: `{metric['waf_mode']}`
- Payload text in reports/logs: no
- Rule IDs: not collected, to avoid storing WAF logs that may include request payload text

## Outputs

- `Timeline/Reproduction/results/real_waf_smoke_metrics.csv`
- `Timeline/Reproduction/results/real_waf_smoke_samples.csv`
- `Timeline/Reproduction/logs/real_waf_smoke_test.log`

## Next Step

Use these real-WAF decisions as the Week 5 baseline evaluator path. If rule-level attribution is needed later, add a sanitizer that strips payload-bearing request lines before persisting audit logs.
"""
    (RESULTS / "real_waf_smoke_test.md").write_text(report, encoding="utf-8")

    log_lines = [
        f"timestamp={now_iso()}",
        f"evaluator_id={EVALUATOR_ID}",
        "waf_engine=modsecurity_crs",
        "waf_mode=modsecurity_crs_docker",
        f"waf_image={metric['waf_image']}",
        f"container_id={container_id}",
        "payload_text_logged=false",
        "rule_ids_collected=false",
        f"sample_count={metric['sample_count']}",
        f"real_waf_blocked={metric['real_waf_blocked']}",
        f"real_waf_allowed={metric['real_waf_allowed']}",
        f"real_waf_errors={metric['real_waf_errors']}",
        "note=Real local ModSecurity+OWASP CRS smoke test; detailed request payloads were not written to artifacts.",
    ]
    (LOGS / "real_waf_smoke_test.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")


def write_blocked_outputs(reason: str, image: str, host_port: int, backend_port: int) -> None:
    write_config(image, host_port, backend_port)
    RESULTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    metric = {
        "evaluator_id": EVALUATOR_ID,
        "waf_mode": "modsecurity_crs_docker",
        "waf_engine": "modsecurity_crs",
        "waf_image": image,
        "sample_count": "0",
        "real_waf_blocked": "0",
        "real_waf_allowed": "0",
        "real_waf_errors": "0",
        "status": "blocked",
    }
    write_csv(RESULTS / "real_waf_smoke_metrics.csv", [metric], list(metric.keys()))
    report = f"""# Real WAF Smoke Test

## Status

Blocked before execution. The runner and config are in place, but the Docker WAF could not be started.

## Reason

`{reason}`

## Next Step

Start Docker Desktop or otherwise make the Docker daemon available, then rerun:

```powershell
python -X utf8 Timeline\\Scripts\\run_real_waf_smoke.py
```
"""
    (RESULTS / "real_waf_smoke_test.md").write_text(report, encoding="utf-8")
    (LOGS / "real_waf_smoke_test.log").write_text(
        "\n".join(
            [
                f"timestamp={now_iso()}",
                f"evaluator_id={EVALUATOR_ID}",
                "status=blocked",
                "payload_text_logged=false",
                f"reason={reason}",
            ]
        )
        + "\n",
        encoding="utf-8",
    )


def update_recovery(metric: dict[str, str]) -> None:
    text = f"""# Recovery

- Current phase: Week 4 real WAF smoke test completed
- Last completed step: ModSecurity + OWASP CRS Docker smoke test over the Week 4 evaluator sample
- Next exact step: Begin Week 5 baseline runs using the real-WAF evaluator path
- Updated artifacts:
  - `Timeline/RECOVERY.md`
  - `Timeline/TIMELINE.md`
  - `Timeline/TRAJECTORY_AUDIT.md`
  - `Timeline/Reproduction/configs/real_waf_smoke_config.yaml`
  - `Timeline/Reproduction/results/real_waf_smoke_test.md`
  - `Timeline/Reproduction/results/real_waf_smoke_metrics.csv`
  - `Timeline/Reproduction/results/real_waf_smoke_samples.csv`
  - `Timeline/Reproduction/logs/real_waf_smoke_test.log`
- Evaluator mode: Week 4 smoke sample rerun through real WAF
- WAF mode: `modsecurity_crs_docker`
- WAF engine status: configured and smoke-tested
- Command log summary:
  - Started a local backend and Docker WAF reverse proxy.
  - Sent {metric['sample_count']} split-aware samples through ModSecurity + OWASP CRS.
  - Wrote hashes, decisions, and status codes only; no payload text was written to reports or logs.
- Metric counts:
  - Real WAF blocked: {metric['real_waf_blocked']}
  - Real WAF allowed: {metric['real_waf_allowed']}
  - Real WAF errors: {metric['real_waf_errors']}
  - Local/real agreement: {metric['local_real_agreement']}
  - Local/real disagreement: {metric['local_real_disagreement']}
- Blockers:
  - None for Week 4 real WAF smoke.
  - Rule IDs are not collected yet because raw audit logs can contain request payload text.
- Last updated: `{now_iso()}`
"""
    RECOVERY.write_text(text, encoding="utf-8")


def append_timeline(metric: dict[str, str]) -> None:
    addition = f"""

### Week 4 Real WAF Smoke Completion

- Created `Timeline/Reproduction/configs/real_waf_smoke_config.yaml`.
- Reran the 45-sample evaluator smoke set against ModSecurity + OWASP CRS in Docker.
- Wrote `Timeline/Reproduction/results/real_waf_smoke_test.md`.
- Wrote `Timeline/Reproduction/results/real_waf_smoke_metrics.csv`.
- Wrote `Timeline/Reproduction/results/real_waf_smoke_samples.csv`.
- Real WAF blocked {metric['real_waf_blocked']}, allowed {metric['real_waf_allowed']}, and errored {metric['real_waf_errors']}.
- Payload text was not written to reports or logs.
"""
    with TIMELINE_MD.open("a", encoding="utf-8") as f:
        f.write(addition)


def update_audit(metric: dict[str, str]) -> None:
    text = AUDIT.read_text(encoding="utf-8")
    if "Timeline/Reproduction/results/real_waf_smoke_test.md" not in text:
        text = text.replace(
            "14. `Timeline/Reproduction/logs/waf_smoke_test.log`",
            "14. `Timeline/Reproduction/logs/waf_smoke_test.log`\n15. `Timeline/Reproduction/configs/real_waf_smoke_config.yaml`\n16. `Timeline/Reproduction/results/real_waf_smoke_test.md`\n17. `Timeline/Reproduction/logs/real_waf_smoke_test.log`",
        )
    text = text.replace(
        "- Week 4: evaluator smoke test completed with local rule-smoke WAF placeholder. Do not report final WAF metrics until a real WAF engine is configured.",
        "- Week 4: evaluator smoke test completed and rerun against ModSecurity + OWASP CRS in Docker. Use real-WAF artifacts for Week 5 baseline comparisons.",
    )
    if "- Real WAF smoke samples:" not in text:
        text = text.replace(
            "- Evaluator smoke samples: 45 with local WAF-rule blocked 27 and allowed 18\n",
            f"- Evaluator smoke samples: 45 with local WAF-rule blocked 27 and allowed 18\n- Real WAF smoke samples: {metric['sample_count']} with ModSecurity+CRS blocked {metric['real_waf_blocked']} and allowed {metric['real_waf_allowed']}\n",
        )
    text = text.replace(
        "| Next step | Real WAF engine setup or Week 5 baseline using accepted evaluator path | Work reports final ASR/FNR from local rule-smoke or trains before baseline acceptance |",
        "| Next step | Week 5 baseline using the accepted real-WAF evaluator path | Work reports local rule-smoke as final WAF results or trains before baseline metrics |",
    )
    text = text.replace(
        "- A report claims final WAF/ASR/FNR results from local rule-smoke instead of a configured WAF engine.",
        "- A report claims final WAF/ASR/FNR results from local rule-smoke instead of `real_waf_smoke_*` artifacts.",
    )
    text = text.replace(
        "- Week 4 outputs are skipped: evaluator config, evaluator smoke result, and WAF smoke-test notes.",
        "- Week 4 outputs are skipped: evaluator config, evaluator smoke result, local WAF note, and real-WAF smoke result.",
    )
    text = text.replace("`2026-05-29T01:50:11+07:00`", f"`{now_iso()}`")
    AUDIT.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the Week 4 smoke sample through a real local WAF.")
    parser.add_argument("--image", default=DEFAULT_IMAGE)
    parser.add_argument("--container-name", default=DEFAULT_CONTAINER)
    parser.add_argument("--host-port", type=int, default=DEFAULT_HOST_PORT)
    parser.add_argument("--backend-port", type=int, default=DEFAULT_BACKEND_PORT)
    parser.add_argument("--keep-container", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_config(args.image, args.host_port, args.backend_port)
    ok, docker_message = docker_available()
    if not ok:
        write_blocked_outputs(docker_message, args.image, args.host_port, args.backend_port)
        print(f"blocked={docker_message}")
        return 2

    backend = start_backend(args.backend_port)
    container_id = ""
    try:
        samples = load_samples()
        container_id = start_waf_container(args.image, args.container_name, args.host_port, args.backend_port)
        wait_for_waf(args.host_port)
        rows, metric = evaluate(samples, args.host_port, args.image)
        write_outputs(rows, metric, container_id)
        update_recovery(metric)
        append_timeline(metric)
        update_audit(metric)
        print(f"samples={metric['sample_count']}")
        print(f"real_waf_blocked={metric['real_waf_blocked']}")
        print(f"real_waf_allowed={metric['real_waf_allowed']}")
        print(f"real_waf_errors={metric['real_waf_errors']}")
        return 0 if metric["real_waf_errors"] == "0" else 1
    except Exception as exc:  # noqa: BLE001
        write_blocked_outputs(str(exc), args.image, args.host_port, args.backend_port)
        print(f"blocked={exc}")
        return 2
    finally:
        if container_id and not args.keep_container:
            remove_existing_container(args.container_name)
        backend.shutdown()
        backend.server_close()


if __name__ == "__main__":
    sys.exit(main())
