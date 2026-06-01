from __future__ import annotations

import base64
import csv
import math
import re
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path


ROOT = Path("Timeline")
DATA = ROOT / "Data"
PROCESSED = DATA / "processed"
SPLITS = DATA / "splits"
REPRO = ROOT / "Reproduction"
CONFIGS = REPRO / "configs"
RESULTS = REPRO / "results"
LOGS = REPRO / "logs"
RECOVERY = ROOT / "RECOVERY.md"
TIMELINE = ROOT / "TIMELINE.md"
AUDIT = ROOT / "TRAJECTORY_AUDIT.md"

COMBINED = PROCESSED / "teacher_seed_sqli_normalized_combined.csv"
ASSIGNMENTS = SPLITS / "teacher_seed_split_assignments.csv"

SAMPLE_PER_SPLIT = 15
EVALUATOR_ID = "week4_offline_evaluator_smoke_v1"
WAF_MODE = "local_rule_smoke"


SQLI_PATTERNS = [
    ("sql_comment", re.compile(r"(--|#|/\*)", re.IGNORECASE)),
    ("union_select", re.compile(r"\bunion\b.{0,40}\bselect\b", re.IGNORECASE)),
    ("boolean_logic", re.compile(r"(\bor\b|\band\b).{0,30}(=|like|is|\bin\b)", re.IGNORECASE)),
    ("time_delay", re.compile(r"\b(sleep|benchmark|pg_sleep|waitfor|delay|dbms_lock|dbms_pipe)\b", re.IGNORECASE)),
    ("error_probe", re.compile(r"\b(extractvalue|updatexml|utl_inaddr|convert|cast)\b", re.IGNORECASE)),
    ("db_metadata", re.compile(r"\b(information_schema|sys\.|all_tables|sqlite_master|@@version)\b", re.IGNORECASE)),
    ("stacked_query", re.compile(r";\s*(select|insert|update|delete|drop|create|exec)\b", re.IGNORECASE)),
]

LOCAL_WAF_RULES = [
    ("LOCAL-001", "comment_or_terminator", re.compile(r"(--|#|/\*)", re.IGNORECASE)),
    ("LOCAL-002", "union_select", re.compile(r"\bunion\b.{0,80}\bselect\b", re.IGNORECASE)),
    ("LOCAL-003", "time_delay", re.compile(r"\b(sleep|benchmark|pg_sleep|waitfor|dbms_lock|dbms_pipe)\b", re.IGNORECASE)),
    ("LOCAL-004", "metadata_probe", re.compile(r"\b(information_schema|sqlite_master|sys\.|all_tables|@@version)\b", re.IGNORECASE)),
    ("LOCAL-005", "stacked_statement", re.compile(r";\s*(select|insert|update|delete|drop|create|exec)\b", re.IGNORECASE)),
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


def decode_payload(row: dict[str, str]) -> str:
    encoded = row["normalized_payload_base64"]
    return base64.b64decode(encoded.encode("ascii")).decode("utf-8", errors="replace")


def char_entropy(value: str) -> float:
    if not value:
        return 0.0
    counts = Counter(value)
    total = len(value)
    return -sum((count / total) * math.log2(count / total) for count in counts.values())


def token_count(value: str) -> int:
    return len(re.findall(r"[A-Za-z_]+|\d+|[^\sA-Za-z_0-9]", value))


def validity_labels(payload: str) -> list[str]:
    labels = [name for name, pattern in SQLI_PATTERNS if pattern.search(payload)]
    if not labels and any(ch in payload for ch in ("'", '"', ";", ")")):
        labels.append("entry_point_probe")
    return labels


def local_waf(payload: str) -> tuple[str, list[str]]:
    hits = [rule_id for rule_id, _name, pattern in LOCAL_WAF_RULES if pattern.search(payload)]
    return ("block" if hits else "allow", hits)


def select_samples() -> list[dict[str, str]]:
    combined_rows = read_csv(COMBINED)
    assignment_rows = read_csv(ASSIGNMENTS)
    first_by_hash: dict[str, dict[str, str]] = {}
    for row in combined_rows:
        first_by_hash.setdefault(row["normalized_sha256"], row)

    selected = []
    for split in ("train", "validation", "test"):
        split_rows = [row for row in assignment_rows if row["split"] == split]
        for assignment in split_rows[:SAMPLE_PER_SPLIT]:
            source = first_by_hash[assignment["normalized_sha256"]].copy()
            source["split"] = split
            selected.append(source)
    return selected


def evaluate() -> tuple[list[dict[str, str]], dict[str, str]]:
    train_hashes = {
        row["normalized_sha256"]
        for row in read_csv(ASSIGNMENTS)
        if row["split"] == "train"
    }
    sample_rows = select_samples()
    results = []
    for index, row in enumerate(sample_rows, start=1):
        payload = decode_payload(row)
        labels = validity_labels(payload)
        waf_decision, rule_hits = local_waf(payload)
        novelty = "not_applicable_train" if row["split"] == "train" else ("novel_exact" if row["normalized_sha256"] not in train_hashes else "known_exact")
        results.append(
            {
                "sample_id": f"smoke-{index:03d}",
                "split": row["split"],
                "source_id": row["source_id"],
                "category": row["category"],
                "dbms": row["dbms"],
                "normalized_sha256": row["normalized_sha256"],
                "payload_sha256": row["payload_sha256"],
                "validity": "sqli_like" if labels else "needs_review",
                "validity_labels": ";".join(labels),
                "novelty_vs_train": novelty,
                "length": str(len(payload)),
                "token_count": str(token_count(payload)),
                "char_entropy": f"{char_entropy(payload):.4f}",
                "local_waf_mode": WAF_MODE,
                "local_waf_decision": waf_decision,
                "local_waf_rule_hits": ";".join(rule_hits),
            }
        )
    metric = summarize(results)
    return results, metric


def summarize(rows: list[dict[str, str]]) -> dict[str, str]:
    total = len(rows)
    valid = sum(1 for row in rows if row["validity"] == "sqli_like")
    blocked = sum(1 for row in rows if row["local_waf_decision"] == "block")
    unique_hashes = len({row["normalized_sha256"] for row in rows})
    split_counts = Counter(row["split"] for row in rows)
    novelty_counts = Counter(row["novelty_vs_train"] for row in rows)
    avg_len = sum(int(row["length"]) for row in rows) / total if total else 0
    avg_tokens = sum(int(row["token_count"]) for row in rows) / total if total else 0
    avg_entropy = sum(float(row["char_entropy"]) for row in rows) / total if total else 0
    return {
        "evaluator_id": EVALUATOR_ID,
        "waf_mode": WAF_MODE,
        "sample_count": str(total),
        "valid_sqli_like": str(valid),
        "needs_review": str(total - valid),
        "unique_hashes": str(unique_hashes),
        "local_waf_blocked": str(blocked),
        "local_waf_allowed": str(total - blocked),
        "train_samples": str(split_counts.get("train", 0)),
        "validation_samples": str(split_counts.get("validation", 0)),
        "test_samples": str(split_counts.get("test", 0)),
        "novel_exact_samples": str(novelty_counts.get("novel_exact", 0)),
        "known_exact_samples": str(novelty_counts.get("known_exact", 0)),
        "avg_length": f"{avg_len:.2f}",
        "avg_token_count": f"{avg_tokens:.2f}",
        "avg_char_entropy": f"{avg_entropy:.4f}",
    }


def write_config() -> None:
    CONFIGS.mkdir(parents=True, exist_ok=True)
    text = f"""evaluator_id: {EVALUATOR_ID}
scope: week4_smoke_test
input:
  combined_csv: Timeline/Data/processed/teacher_seed_sqli_normalized_combined.csv
  split_assignments: Timeline/Data/splits/teacher_seed_split_assignments.csv
sampling:
  per_split: {SAMPLE_PER_SPLIT}
  splits:
    - train
    - validation
    - test
checks:
  validity: lightweight_sqli_like_rules
  novelty: exact_hash_vs_train
  uniqueness: normalized_sha256
  diversity:
    - length
    - token_count
    - char_entropy
waf:
  mode: {WAF_MODE}
  note: local deterministic smoke rules only; not ModSecurity, CRS, or Coraza
reporting:
  include_payload_text: false
  include_hashes: true
  include_rule_ids: true
guardrails:
  - Do not treat local_rule_smoke as final WAF ASR/FNR.
  - Do not print detailed payload strings in markdown reports or logs.
  - Use split-aware sampling before reporting novelty.
"""
    (CONFIGS / "evaluation_config.yaml").write_text(text, encoding="utf-8")


def write_outputs(results: list[dict[str, str]], metric: dict[str, str]) -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    write_csv(
        RESULTS / "evaluator_smoke_samples.csv",
        results,
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
            "novelty_vs_train",
            "length",
            "token_count",
            "char_entropy",
            "local_waf_mode",
            "local_waf_decision",
            "local_waf_rule_hits",
        ],
    )
    write_csv(RESULTS / "evaluator_smoke_metrics.csv", [metric], list(metric.keys()))

    split_rows = Counter(row["split"] for row in results)
    decision_rows = Counter(row["local_waf_decision"] for row in results)
    report = f"""# Evaluator Smoke Test

## Summary

Week 4 smoke-tested the evaluator over a split-aware sample. The run uses lightweight SQLi-like validity rules, exact-hash novelty checks against the train split, simple diversity features, and a local deterministic WAF-rule smoke check.

This is not a final WAF evaluation. `local_rule_smoke` is a placeholder until ModSecurity plus OWASP CRS or Coraza is installed and configured.

## Configuration

- Config: `Timeline/Reproduction/configs/evaluation_config.yaml`
- Input corpus: `Timeline/Data/processed/teacher_seed_sqli_normalized_combined.csv`
- Split assignments: `Timeline/Data/splits/teacher_seed_split_assignments.csv`
- Samples per split: {SAMPLE_PER_SPLIT}
- Payload text in reports/logs: no

## Metrics

| Metric | Value |
| --- | ---: |
| Samples | {metric['sample_count']} |
| SQLi-like validity hits | {metric['valid_sqli_like']} |
| Needs review | {metric['needs_review']} |
| Unique hashes | {metric['unique_hashes']} |
| Local WAF-rule blocked | {metric['local_waf_blocked']} |
| Local WAF-rule allowed | {metric['local_waf_allowed']} |
| Average length | {metric['avg_length']} |
| Average token count | {metric['avg_token_count']} |
| Average character entropy | {metric['avg_char_entropy']} |

## Split Coverage

| Split | Samples |
| --- | ---: |
| train | {split_rows.get('train', 0)} |
| validation | {split_rows.get('validation', 0)} |
| test | {split_rows.get('test', 0)} |

## Local WAF-Rule Smoke

| Decision | Samples |
| --- | ---: |
| block | {decision_rows.get('block', 0)} |
| allow | {decision_rows.get('allow', 0)} |

## Outputs

- `Timeline/Reproduction/results/evaluator_smoke_metrics.csv`
- `Timeline/Reproduction/results/evaluator_smoke_samples.csv`
- `Timeline/Reproduction/logs/waf_smoke_test.log`

## Next Step

Install or configure a real WAF engine and rerun the same sample path. Until then, do not report ASR/FNR as real WAF metrics.
"""
    (RESULTS / "evaluator_smoke_test.md").write_text(report, encoding="utf-8")

    now = datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()
    log_lines = [
        f"timestamp={now}",
        f"evaluator_id={EVALUATOR_ID}",
        f"waf_mode={WAF_MODE}",
        "waf_engine=not_configured",
        "payload_text_logged=false",
        f"sample_count={metric['sample_count']}",
        f"local_waf_blocked={metric['local_waf_blocked']}",
        f"local_waf_allowed={metric['local_waf_allowed']}",
        "note=This is a deterministic local rule-smoke placeholder, not ModSecurity/CRS/Coraza.",
    ]
    (LOGS / "waf_smoke_test.log").write_text("\n".join(log_lines) + "\n", encoding="utf-8")


def update_recovery(metric: dict[str, str]) -> None:
    now = datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()
    text = f"""# Recovery

- Current phase: Week 4 evaluator smoke test completed
- Last completed step: Offline evaluator smoke test and local WAF-rule smoke generated under `Timeline`
- Next exact step: Configure a real WAF engine and rerun WAF smoke test, or continue to Week 5 baseline only after evaluator path is accepted
- Updated artifacts:
  - `Timeline/RECOVERY.md`
  - `Timeline/TIMELINE.md`
  - `Timeline/TRAJECTORY_AUDIT.md`
  - `Timeline/Reproduction/configs/evaluation_config.yaml`
  - `Timeline/Reproduction/results/evaluator_smoke_test.md`
  - `Timeline/Reproduction/results/evaluator_smoke_metrics.csv`
  - `Timeline/Reproduction/results/evaluator_smoke_samples.csv`
  - `Timeline/Reproduction/logs/waf_smoke_test.log`
- Evaluator mode: lightweight offline smoke
- WAF mode: `local_rule_smoke`
- WAF engine status: not configured
- Command log summary:
  - Created evaluator configuration.
  - Sampled {metric['sample_count']} split-aware records from train, validation, and test.
  - Computed SQLi-like validity, exact novelty, uniqueness, simple diversity features, and local rule-smoke decisions.
  - Wrote hashes and metrics only; no payload text was written to reports or logs.
- Row counts:
  - Smoke samples: {metric['sample_count']}
  - Train samples: {metric['train_samples']}
  - Validation samples: {metric['validation_samples']}
  - Test samples: {metric['test_samples']}
  - Unique sample hashes: {metric['unique_hashes']}
- Metric counts:
  - SQLi-like validity hits: {metric['valid_sqli_like']}
  - Needs review: {metric['needs_review']}
  - Local WAF-rule blocked: {metric['local_waf_blocked']}
  - Local WAF-rule allowed: {metric['local_waf_allowed']}
- Blockers:
  - Real ModSecurity/OWASP CRS or Coraza engine is not configured in this artifact set.
- Last updated: `{now}`
"""
    RECOVERY.write_text(text, encoding="utf-8")


def append_timeline(metric: dict[str, str]) -> None:
    addition = f"""

### Week 4 Completion

- Created `Timeline/Reproduction/configs/evaluation_config.yaml`.
- Created split-aware evaluator smoke test over {metric['sample_count']} samples.
- Wrote `Timeline/Reproduction/results/evaluator_smoke_test.md`.
- Wrote `Timeline/Reproduction/results/evaluator_smoke_metrics.csv`.
- Wrote `Timeline/Reproduction/results/evaluator_smoke_samples.csv`.
- Wrote `Timeline/Reproduction/logs/waf_smoke_test.log`.
- Validity hits: {metric['valid_sqli_like']}; needs review: {metric['needs_review']}.
- Local WAF-rule smoke blocked {metric['local_waf_blocked']} and allowed {metric['local_waf_allowed']}.
- Real WAF engine is still not configured; do not treat local rule-smoke as final WAF ASR/FNR.
"""
    with TIMELINE.open("a", encoding="utf-8") as f:
        f.write(addition)


def update_audit(metric: dict[str, str]) -> None:
    now = datetime.now(timezone.utc).astimezone().replace(microsecond=0).isoformat()
    text = AUDIT.read_text(encoding="utf-8")
    if "Timeline/Reproduction/configs/evaluation_config.yaml" not in text.split("## Read Order", 1)[1].split("## Current Trajectory", 1)[0]:
        text = text.replace(
            "11. `Timeline/Reproduction/baselines/payloadsallthethings_rule_baseline.md`",
            "11. `Timeline/Reproduction/baselines/payloadsallthethings_rule_baseline.md`\n12. `Timeline/Reproduction/configs/evaluation_config.yaml`\n13. `Timeline/Reproduction/results/evaluator_smoke_test.md`\n14. `Timeline/Reproduction/logs/waf_smoke_test.log`",
        )
    text = text.replace(
        "- Week 4 next: evaluator and WAF smoke test. Do not jump to baseline metrics, GSQLi reproduction, or GAN training before evaluator smoke results exist.",
        "- Week 4: evaluator smoke test completed with local rule-smoke WAF placeholder. Do not report final WAF metrics until a real WAF engine is configured.",
    )
    text = text.replace(
        "| Next step | Week 4 evaluator and WAF smoke test | Work jumps to baseline metrics, reproduction, or training without evaluator smoke results |",
        "| Next step | Real WAF engine setup or Week 5 baseline using accepted evaluator path | Work reports final ASR/FNR from local rule-smoke or trains before baseline acceptance |",
    )
    if "- Evaluator smoke samples:" not in text:
        text = text.replace(
            "- Split counts: train 18516, validation 2274, test 2292 unique hashes\n",
            f"- Split counts: train 18516, validation 2274, test 2292 unique hashes\n- Evaluator smoke samples: {metric['sample_count']} with local WAF-rule blocked {metric['local_waf_blocked']} and allowed {metric['local_waf_allowed']}\n",
        )
    text = text.replace(
        "- A report claims WAF/ASR/FNR results before `Timeline/Reproduction/configs/evaluation_config.yaml` and evaluator smoke results exist.",
        "- A report claims final WAF/ASR/FNR results from local rule-smoke instead of a configured WAF engine.",
    )
    text = text.replace(
        "`2026-05-29T01:34:49+07:00`",
        f"`{now}`",
    )
    AUDIT.write_text(text, encoding="utf-8")


def main() -> None:
    write_config()
    results, metric = evaluate()
    write_outputs(results, metric)
    update_recovery(metric)
    append_timeline(metric)
    update_audit(metric)
    print(f"samples={metric['sample_count']}")
    print(f"valid_sqli_like={metric['valid_sqli_like']}")
    print(f"needs_review={metric['needs_review']}")
    print(f"local_waf_blocked={metric['local_waf_blocked']}")
    print(f"local_waf_allowed={metric['local_waf_allowed']}")


if __name__ == "__main__":
    main()
