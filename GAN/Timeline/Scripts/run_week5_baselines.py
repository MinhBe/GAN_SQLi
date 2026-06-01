from __future__ import annotations

import argparse
import base64
import csv
import hashlib
import math
import re
import sys
from collections import Counter, defaultdict
from pathlib import Path

import run_real_waf_smoke as waf


TIMELINE = Path(__file__).resolve().parents[1]
DATA = TIMELINE / "Data"
REPRO = TIMELINE / "Reproduction"
REPORTS = TIMELINE / "Reports"
CONFIGS = REPRO / "configs"
RESULTS = REPRO / "results"
LOGS = REPRO / "logs"
BASELINES = REPRO / "baselines"

COMBINED = DATA / "processed" / "teacher_seed_sqli_normalized_combined.csv"
ASSIGNMENTS = DATA / "splits" / "teacher_seed_split_assignments.csv"
RECOVERY = TIMELINE / "RECOVERY.md"
TIMELINE_MD = TIMELINE / "TIMELINE.md"
AUDIT = TIMELINE / "TRAJECTORY_AUDIT.md"

EVALUATOR_ID = "week5_baseline_real_waf_v1"
DEFAULT_TEMPLATE_COUNT = 60
DEFAULT_MUTATION_COUNT = 60

SQLI_PATTERNS = [
    ("sql_comment", re.compile(r"(--|#|/\*)", re.IGNORECASE)),
    ("union_select", re.compile(r"\bunion\b.{0,40}\bselect\b", re.IGNORECASE)),
    ("boolean_logic", re.compile(r"(\bor\b|\band\b).{0,30}(=|like|is|\bin\b)", re.IGNORECASE)),
    ("time_delay", re.compile(r"\b(sleep|benchmark|pg_sleep|waitfor|delay|dbms_lock|dbms_pipe)\b", re.IGNORECASE)),
    ("error_probe", re.compile(r"\b(extractvalue|updatexml|utl_inaddr|convert|cast)\b", re.IGNORECASE)),
    ("db_metadata", re.compile(r"\b(information_schema|sys\.|all_tables|sqlite_master|@@version)\b", re.IGNORECASE)),
    ("stacked_query", re.compile(r";\s*(select|insert|update|delete|drop|create|exec)\b", re.IGNORECASE)),
]

KEYWORDS = [
    "select",
    "union",
    "where",
    "and",
    "or",
    "from",
    "sleep",
    "benchmark",
    "waitfor",
    "delay",
    "insert",
    "update",
    "delete",
    "drop",
]


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


def token_count(value: str) -> int:
    return len(re.findall(r"[A-Za-z_]+|\d+|[^\sA-Za-z_0-9]", value))


def char_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = Counter(value)
    total = len(value)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def validity_labels(payload: str) -> list[str]:
    labels = [name for name, pattern in SQLI_PATTERNS if pattern.search(payload)]
    if not labels and any(ch in payload for ch in ("'", '"', ";", ")")):
        labels.append("entry_point_probe")
    return labels


def load_train_hashes() -> set[str]:
    return {row["normalized_sha256"] for row in read_csv(ASSIGNMENTS) if row["split"] == "train"}


def load_train_rows() -> list[dict[str, str]]:
    train_hashes = load_train_hashes()
    rows = []
    seen: set[str] = set()
    for row in read_csv(COMBINED):
        if row["normalized_sha256"] not in train_hashes:
            continue
        if row["normalized_sha256"] in seen:
            continue
        seen.add(row["normalized_sha256"])
        enriched = row.copy()
        enriched["_payload"] = decode_payload(row["normalized_payload_base64"])
        rows.append(enriched)
    return rows


def balanced_sample(rows: list[dict[str, str]], limit: int, source_filter: str | None = None) -> list[dict[str, str]]:
    buckets: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        if source_filter and row["source_id"] != source_filter:
            continue
        buckets[row["category"] or "uncategorized"].append(row)
    selected: list[dict[str, str]] = []
    while len(selected) < limit:
        progressed = False
        for category in sorted(buckets):
            bucket = buckets[category]
            if not bucket:
                continue
            selected.append(bucket.pop(0))
            progressed = True
            if len(selected) >= limit:
                break
        if not progressed:
            break
    return selected


def mutate_case_keywords(payload: str) -> str:
    def repl(match: re.Match[str]) -> str:
        word = match.group(0)
        return "".join(ch.upper() if idx % 2 == 0 else ch.lower() for idx, ch in enumerate(word))

    return re.sub(r"\b(" + "|".join(KEYWORDS) + r")\b", repl, payload, flags=re.IGNORECASE)


def mutate_space_runs(payload: str) -> str:
    return re.sub(r"\s+", "/**/", payload)


def mutate_boolean_words(payload: str) -> str:
    result = re.sub(r"\bor\b", "||", payload, flags=re.IGNORECASE)
    result = re.sub(r"\band\b", "&&", result, flags=re.IGNORECASE)
    return result


def mutate_url_encode_quotes(payload: str) -> str:
    return payload.replace("'", "%27").replace('"', "%22")


MUTATORS = [
    ("case_keywords", mutate_case_keywords),
    ("space_runs", mutate_space_runs),
    ("boolean_words", mutate_boolean_words),
    ("quote_url_encoding", mutate_url_encode_quotes),
]


def build_template_rows(seed_rows: list[dict[str, str]], limit: int) -> list[dict[str, str]]:
    rows = []
    for idx, row in enumerate(seed_rows[:limit], start=1):
        payload = row["_payload"]
        payload_hash = sha256_text(payload)
        rows.append(
            {
                "baseline_id": "template_rule",
                "sample_id": f"template-{idx:03d}",
                "source_sample_hash": row["normalized_sha256"],
                "source_id": row["source_id"],
                "category": row["category"],
                "dbms": row["dbms"],
                "_payload": payload,
                "payload_sha256": payload_hash,
                "normalized_sha256": payload_hash,
                "operator": "identity_template",
            }
        )
    return rows


def build_mutation_rows(seed_rows: list[dict[str, str]], limit: int) -> list[dict[str, str]]:
    rows = []
    idx = 1
    for row in seed_rows:
        for operator, mutator in MUTATORS:
            payload = mutator(row["_payload"])
            if payload == row["_payload"]:
                continue
            payload_hash = sha256_text(payload)
            rows.append(
                {
                    "baseline_id": "deterministic_mutation",
                    "sample_id": f"mutation-{idx:03d}",
                    "source_sample_hash": row["normalized_sha256"],
                    "source_id": row["source_id"],
                    "category": row["category"],
                    "dbms": row["dbms"],
                    "_payload": payload,
                    "payload_sha256": payload_hash,
                    "normalized_sha256": payload_hash,
                    "operator": operator,
                }
            )
            idx += 1
            if len(rows) >= limit:
                return rows
    return rows


def evaluate_rows(rows: list[dict[str, str]], train_hashes: set[str], host_port: int) -> list[dict[str, str]]:
    evaluated = []
    for row in rows:
        payload = row["_payload"]
        labels = validity_labels(payload)
        status, decision, error = waf.probe_waf(payload, host_port, row["sample_id"])
        evaluated.append(
            {
                "baseline_id": row["baseline_id"],
                "sample_id": row["sample_id"],
                "source_sample_hash": row["source_sample_hash"],
                "source_id": row["source_id"],
                "category": row["category"],
                "dbms": row["dbms"],
                "operator": row["operator"],
                "payload_sha256": row["payload_sha256"],
                "normalized_sha256": row["normalized_sha256"],
                "payload_base64": encode_payload(payload),
                "validity": "sqli_like" if labels else "needs_review",
                "validity_labels": ";".join(labels),
                "novelty_vs_train": "known_exact" if row["normalized_sha256"] in train_hashes else "novel_exact",
                "length": str(len(payload)),
                "token_count": str(token_count(payload)),
                "char_entropy": f"{char_entropy(payload):.4f}",
                "real_waf_mode": "modsecurity_crs_docker",
                "http_status": str(status),
                "real_waf_decision": decision,
                "real_waf_rule_ids": "not_collected_payload_safe",
                "error": error,
            }
        )
    return evaluated


def summarize(rows: list[dict[str, str]]) -> list[dict[str, str]]:
    summaries = []
    for baseline_id in sorted({row["baseline_id"] for row in rows}):
        group = [row for row in rows if row["baseline_id"] == baseline_id]
        total = len(group)
        unique_hashes = len({row["normalized_sha256"] for row in group})
        decisions = Counter(row["real_waf_decision"] for row in group)
        validity = Counter(row["validity"] for row in group)
        novelty = Counter(row["novelty_vs_train"] for row in group)
        avg_length = sum(int(row["length"]) for row in group) / total if total else 0
        avg_tokens = sum(int(row["token_count"]) for row in group) / total if total else 0
        avg_entropy = sum(float(row["char_entropy"]) for row in group) / total if total else 0
        summaries.append(
            {
                "evaluator_id": EVALUATOR_ID,
                "baseline_id": baseline_id,
                "sample_count": str(total),
                "valid_sqli_like": str(validity.get("sqli_like", 0)),
                "needs_review": str(validity.get("needs_review", 0)),
                "unique_hashes": str(unique_hashes),
                "duplicate_outputs": str(total - unique_hashes),
                "novel_exact": str(novelty.get("novel_exact", 0)),
                "known_exact": str(novelty.get("known_exact", 0)),
                "real_waf_blocked": str(decisions.get("block", 0)),
                "real_waf_allowed": str(decisions.get("allow", 0)),
                "real_waf_errors": str(decisions.get("error", 0)),
                "avg_length": f"{avg_length:.2f}",
                "avg_token_count": f"{avg_tokens:.2f}",
                "avg_char_entropy": f"{avg_entropy:.4f}",
                "payload_text_logged": "false",
            }
        )
    return summaries


def write_config(args: argparse.Namespace) -> None:
    text = f"""evaluator_id: {EVALUATOR_ID}
scope: week5_baseline_real_waf
input:
  combined_csv: Timeline/Data/processed/teacher_seed_sqli_normalized_combined.csv
  split_assignments: Timeline/Data/splits/teacher_seed_split_assignments.csv
baseline_sampling:
  split: train
  template_rule_count: {args.template_count}
  deterministic_mutation_count: {args.mutation_count}
  preferred_seed_source: payloadsallthethings_sqli_intruder
waf:
  engine: modsecurity_crs
  mode: modsecurity_crs_docker
  image: {args.image}
  host_port: {args.host_port}
  backend_port: {args.backend_port}
reporting:
  include_payload_text_in_reports: false
  include_payload_base64_in_machine_csv: true
  include_hashes: true
  include_rule_ids: false
guardrails:
  - Run only against the local Docker WAF and local backend.
  - Use train-split seeds for baseline construction.
  - Do not print detailed payload strings in markdown reports or logs.
  - Treat output payload CSV as local machine artifact, not public report content.
"""
    CONFIGS.mkdir(parents=True, exist_ok=True)
    (CONFIGS / "week5_baseline_config.yaml").write_text(text, encoding="utf-8")


def write_baseline_definition() -> None:
    text = """# Week 5 Baseline Definitions

## Baselines

| Baseline | Role | Construction |
| --- | --- | --- |
| `template_rule` | Minimal seed/template baseline | Balanced sample from train-split teacher seed rows |
| `deterministic_mutation` | Simple mutation baseline | Deterministic operator families applied to train-split teacher seed rows |

## Operator Families

The mutation baseline records only operator family names in reports: case variation, spacing/comment-style separator variation, boolean-word variation, and quote encoding variation. Detailed payload text is not written to markdown reports or logs.

## Evaluation

Both baselines are evaluated through the same ModSecurity + OWASP CRS Docker path established by Week 4 real-WAF smoke testing.
"""
    BASELINES.mkdir(parents=True, exist_ok=True)
    (BASELINES / "week5_baseline_definitions.md").write_text(text, encoding="utf-8")


def write_outputs(rows: list[dict[str, str]], summaries: list[dict[str, str]]) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)
    write_csv(
        RESULTS / "baseline_samples.csv",
        rows,
        [
            "baseline_id",
            "sample_id",
            "source_sample_hash",
            "source_id",
            "category",
            "dbms",
            "operator",
            "payload_sha256",
            "normalized_sha256",
            "payload_base64",
            "validity",
            "validity_labels",
            "novelty_vs_train",
            "length",
            "token_count",
            "char_entropy",
            "real_waf_mode",
            "http_status",
            "real_waf_decision",
            "real_waf_rule_ids",
            "error",
        ],
    )
    write_csv(RESULTS / "baseline_metrics.csv", summaries, list(summaries[0].keys()))

    table_rows = "\n".join(
        "| {baseline_id} | {sample_count} | {valid_sqli_like} | {unique_hashes} | {novel_exact} | {real_waf_blocked} | {real_waf_allowed} | {real_waf_errors} |".format(**row)
        for row in summaries
    )
    report = f"""# Week 5 Baseline Results

## Summary

Week 5 evaluates two minimum baselines through the real local ModSecurity + OWASP CRS WAF path. Reports and logs contain metrics and hashes only; detailed payload text is not printed in markdown or logs.

## Metrics

| Baseline | Samples | Valid | Unique | Novel exact | Real WAF blocked | Real WAF allowed | Errors |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
{table_rows}

## Outputs

- `Timeline/Reproduction/configs/week5_baseline_config.yaml`
- `Timeline/Reproduction/baselines/week5_baseline_definitions.md`
- `Timeline/Reproduction/results/baseline_metrics.csv`
- `Timeline/Reproduction/results/baseline_samples.csv`
- `Timeline/Reproduction/logs/baseline_run.log`

## Interpretation

`template_rule` is the non-generative seed/template baseline. `deterministic_mutation` is the first mutation baseline and provides the minimum comparison point before WAF-A-MoLE or GSQLi reproduction work.
"""
    (REPORTS / "03_baseline_results.md").write_text(report, encoding="utf-8")

    log_lines = [
        f"timestamp={waf.now_iso()}",
        f"evaluator_id={EVALUATOR_ID}",
        "waf_engine=modsecurity_crs",
        "waf_mode=modsecurity_crs_docker",
        "payload_text_logged=false",
        "rule_ids_collected=false",
    ]
    for row in summaries:
        log_lines.append(
            "baseline={baseline_id} samples={sample_count} blocked={real_waf_blocked} allowed={real_waf_allowed} errors={real_waf_errors}".format(**row)
        )
    (LOGS / "baseline_run.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")


def update_recovery(summaries: list[dict[str, str]]) -> None:
    summary_lines = "\n".join(
        "- {baseline_id}: samples {sample_count}, blocked {real_waf_blocked}, allowed {real_waf_allowed}, errors {real_waf_errors}".format(**row)
        for row in summaries
    )
    text = f"""# Recovery

- Current phase: Week 5 baseline results completed
- Last completed step: Template/rule and deterministic mutation baselines evaluated through ModSecurity + OWASP CRS Docker
- Next exact step: Add WAF-A-MoLE smoke/failure report or begin selected GSQLi reproduction planning
- Updated artifacts:
  - `Timeline/RECOVERY.md`
  - `Timeline/TIMELINE.md`
  - `Timeline/TRAJECTORY_AUDIT.md`
  - `Timeline/Reproduction/configs/week5_baseline_config.yaml`
  - `Timeline/Reproduction/baselines/week5_baseline_definitions.md`
  - `Timeline/Reproduction/results/baseline_metrics.csv`
  - `Timeline/Reproduction/results/baseline_samples.csv`
  - `Timeline/Reproduction/logs/baseline_run.log`
  - `Timeline/Reports/03_baseline_results.md`
- Evaluator mode: Week 5 baseline real-WAF run
- WAF mode: `modsecurity_crs_docker`
- WAF engine status: configured and used for baseline metrics
- Metric counts:
{summary_lines}
- Blockers:
  - WAF-A-MoLE has not been smoke-tested yet.
  - GSQLi reproduction has not started yet.
- Last updated: `{waf.now_iso()}`
"""
    RECOVERY.write_text(text, encoding="utf-8")


def append_timeline(summaries: list[dict[str, str]]) -> None:
    summary_lines = "\n".join(
        "- `{baseline_id}`: samples {sample_count}, blocked {real_waf_blocked}, allowed {real_waf_allowed}, errors {real_waf_errors}.".format(**row)
        for row in summaries
    )
    addition = f"""

### Week 5 Baseline Completion

- Created `Timeline/Reproduction/configs/week5_baseline_config.yaml`.
- Created `Timeline/Reproduction/baselines/week5_baseline_definitions.md`.
- Evaluated template/rule and deterministic mutation baselines through ModSecurity + OWASP CRS Docker.
{summary_lines}
- Wrote `Timeline/Reproduction/results/baseline_metrics.csv`.
- Wrote `Timeline/Reproduction/results/baseline_samples.csv`.
- Wrote `Timeline/Reports/03_baseline_results.md`.
- Payload text was not written to markdown reports or logs.
"""
    with TIMELINE_MD.open("a", encoding="utf-8") as f:
        f.write(addition)


def update_audit(summaries: list[dict[str, str]]) -> None:
    text = AUDIT.read_text(encoding="utf-8")
    if "Timeline/Reproduction/results/baseline_metrics.csv" not in text:
        text = text.replace(
            "17. `Timeline/Reproduction/logs/real_waf_smoke_test.log`",
            "17. `Timeline/Reproduction/logs/real_waf_smoke_test.log`\n18. `Timeline/Reproduction/configs/week5_baseline_config.yaml`\n19. `Timeline/Reproduction/results/baseline_metrics.csv`\n20. `Timeline/Reports/03_baseline_results.md`",
        )
    text = text.replace(
        "- Week 4: evaluator smoke test completed and rerun against ModSecurity + OWASP CRS in Docker. Use real-WAF artifacts for Week 5 baseline comparisons.",
        "- Week 5: template/rule and deterministic mutation baselines completed through the ModSecurity + OWASP CRS Docker evaluator path.",
    )
    if "- Week 5 baseline rows:" not in text:
        total = sum(int(row["sample_count"]) for row in summaries)
        text = text.replace(
            "- Real WAF smoke samples: 45 with ModSecurity+CRS blocked 41 and allowed 4\n",
            f"- Real WAF smoke samples: 45 with ModSecurity+CRS blocked 41 and allowed 4\n- Week 5 baseline rows: {total} across template_rule and deterministic_mutation\n",
        )
    text = text.replace(
        "| Baseline status | PATT baseline is a definition only | It is reported as having real evaluator/WAF metrics |",
        "| Baseline status | Week 5 minimum baselines have real-WAF metrics | Reports claim WAF-A-MoLE or GSQLi metrics before those runs exist |",
    )
    text = text.replace(
        "| Next step | Week 5 baseline using the accepted real-WAF evaluator path | Work reports local rule-smoke as final WAF results or trains before baseline metrics |",
        "| Next step | WAF-A-MoLE smoke/failure report or selected GSQLi reproduction plan | Work claims model superiority before WAF-A-MoLE/GSQLi artifacts exist |",
    )
    text = text.replace("`2026-05-29T02:17:09+07:00`", f"`{waf.now_iso()}`")
    AUDIT.write_text(text, encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run Week 5 baselines through the real local WAF.")
    parser.add_argument("--image", default=waf.DEFAULT_IMAGE)
    parser.add_argument("--container-name", default="gan-sqli-crs-week5-baseline")
    parser.add_argument("--host-port", type=int, default=18082)
    parser.add_argument("--backend-port", type=int, default=18083)
    parser.add_argument("--template-count", type=int, default=DEFAULT_TEMPLATE_COUNT)
    parser.add_argument("--mutation-count", type=int, default=DEFAULT_MUTATION_COUNT)
    parser.add_argument("--keep-container", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    write_config(args)
    write_baseline_definition()
    ok, docker_message = waf.docker_available()
    if not ok:
        raise RuntimeError(docker_message)

    train_rows = load_train_rows()
    patt_seed = balanced_sample(train_rows, args.template_count, "payloadsallthethings_sqli_intruder")
    if len(patt_seed) < args.template_count:
        patt_seed.extend(balanced_sample(train_rows, args.template_count - len(patt_seed)))
    mutation_seed = balanced_sample(train_rows, max(args.mutation_count, 30), "payloadsallthethings_sqli_intruder")
    if len(mutation_seed) < 30:
        mutation_seed.extend(balanced_sample(train_rows, 30 - len(mutation_seed)))

    baseline_rows = build_template_rows(patt_seed, args.template_count)
    baseline_rows.extend(build_mutation_rows(mutation_seed, args.mutation_count))

    backend = waf.start_backend(args.backend_port)
    container_id = ""
    try:
        container_id = waf.start_waf_container(args.image, args.container_name, args.host_port, args.backend_port)
        waf.wait_for_waf(args.host_port)
        evaluated = evaluate_rows(baseline_rows, load_train_hashes(), args.host_port)
        summaries = summarize(evaluated)
        write_outputs(evaluated, summaries)
        update_recovery(summaries)
        append_timeline(summaries)
        update_audit(summaries)
        for row in summaries:
            print(
                "baseline={baseline_id} samples={sample_count} blocked={real_waf_blocked} allowed={real_waf_allowed} errors={real_waf_errors}".format(
                    **row
                )
            )
        return 0
    finally:
        if container_id and not args.keep_container:
            waf.remove_existing_container(args.container_name)
        backend.shutdown()
        backend.server_close()


if __name__ == "__main__":
    sys.exit(main())
