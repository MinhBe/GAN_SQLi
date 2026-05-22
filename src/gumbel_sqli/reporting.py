from __future__ import annotations

from datetime import datetime, timezone
import json
from pathlib import Path
from typing import Any

import pandas as pd

from .config import ProjectConfig


def write_json(payload: dict[str, Any], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=True), encoding="utf-8")


def now_iso_date() -> str:
    return datetime.now(timezone.utc).date().isoformat()


def write_audit_report(
    path: Path,
    decision: dict[str, Any],
    coverage: dict[str, Any],
    source_rows: int,
    candidate_rows: int,
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    family_rows = "\n".join(
        f"| {family} | {count} |"
        for family, count in sorted(coverage.get("family_counts", {}).items())
    )
    technique_rows = "\n".join(
        f"| {item['technique_primary']} | {item['db_hint']} | {item['rows']} | {item['non_literal_rate']:.3f} |"
        for item in coverage.get("technique_db_coverage", [])[:40]
    )
    text = f"""# 01 Slot/Action Audit

Generated: {now_iso_date()}

## G0 Decision

- Decision: `{decision['decision']}`
- Reason: {decision['reason']}
- Source payload rows: {source_rows}
- Action candidate rows: {candidate_rows}
- Non-literal coverage: {coverage.get('non_literal_coverage', 0.0):.3f}

## Action Family Counts

| Family | Count |
| --- | ---: |
{family_rows}

## Technique x DB Hint Coverage

| Technique | DB hint | Rows | Non-literal rate |
| --- | --- | ---: | ---: |
{technique_rows}

## Registered Risks

{chr(10).join(f"- {risk}" for risk in decision.get("risks", []))}
"""
    path.write_text(text, encoding="utf-8")


def write_slice_report(
    path: Path,
    metrics: dict[str, Any],
    decision: dict[str, Any],
    split_sizes: dict[str, int],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    split_rows = "\n".join(f"| {name} | {size} |" for name, size in split_sizes.items())
    metric_rows = "\n".join(
        f"| {key} | {value:.4f} |"
        for key, value in metrics.items()
        if isinstance(value, (int, float)) and key != "n"
    )
    text = f"""# 02 De-risk Action-Surgery Slice

Generated: {now_iso_date()}

## Slice Decision

- Decision: `{decision['decision']}`
- Reason: {decision['reason']}

## Split Sizes

| Split | Rows |
| --- | ---: |
{split_rows}

## Evaluator Metrics

| Metric | Value |
| --- | ---: |
{metric_rows}

Composite floors pass: `{metrics.get('composite', {}).get('passed_floors')}`
"""
    path.write_text(text, encoding="utf-8")


def write_evaluator_report(path: Path, config_payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    text = f"""# 06 Evaluator And Model Separation

Generated: {now_iso_date()}

The evaluator is stored independently at `eval/gumbel/evaluator_config.json`.
Composite scoring is vetoed by metric floors before weights are applied.

```json
{json.dumps(config_payload, indent=2)}
```
"""
    path.write_text(text, encoding="utf-8")


def dataframe_coverage(candidates: pd.DataFrame) -> dict[str, Any]:
    family_counts = candidates["action_family"].value_counts().to_dict()
    by_group = []
    if {"technique_primary", "db_hint", "non_literal_action_count"}.issubset(candidates.columns):
        grouped = candidates.groupby(["technique_primary", "db_hint"], dropna=False)
        for (technique, db_hint), group in grouped:
            by_group.append(
                {
                    "technique_primary": str(technique),
                    "db_hint": str(db_hint),
                    "rows": int(len(group)),
                    "non_literal_rate": float(
                        (group["non_literal_action_count"].fillna(0) > 0).mean()
                    ),
                }
            )
    return {
        "family_counts": {str(k): int(v) for k, v in family_counts.items()},
        "technique_db_coverage": by_group,
    }


def update_timeline_progress(
    config: ProjectConfig,
    phase_id: str,
    status: str,
    progress_percent: int,
    gate_result: str | None,
    evidence_artifacts: list[str],
    notes: str | None = None,
) -> None:
    path = config.timeline_progress_path
    if not path.exists():
        return
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["updated_at"] = now_iso_date()
    payload["project_root"] = str(config.root).replace("\\", "/")
    overall = payload.setdefault("overall_progress", {})
    if phase_id == "G09" and status == "completed":
        overall["status"] = "completed"
    elif status in {"blocked", "failed"}:
        overall["status"] = status
    else:
        overall["status"] = "in_progress"
    overall["active_phase_id"] = phase_id
    overall["progress_percent"] = max(int(overall.get("progress_percent", 0)), progress_percent)
    if status in {"completed", "failed", "blocked"}:
        overall["last_completed_phase_id"] = phase_id if status == "completed" else overall.get("last_completed_phase_id")
        overall["next_action"] = notes or overall.get("next_action", "")

    branch = payload.get("branches", {}).get("gumbel_action_surgery", {})
    if branch:
        branch["branch_status"] = overall["status"]
    phases = branch.get("phases", [])
    for phase in phases:
        if phase.get("id") != phase_id:
            continue
        phase["status"] = status
        phase["progress_percent"] = progress_percent
        phase["evidence_artifacts"] = evidence_artifacts
        if gate_result is not None:
            phase.setdefault("gate", {})["current_result"] = gate_result
        if notes is not None:
            phase["notes"] = notes
        break
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
