from __future__ import annotations

from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any

import pandas as pd

from .config import ProjectConfig
from .dataset import build_action_candidate_table, load_payloads, write_parquet
from .reporting import update_timeline_progress, write_json


def _bucket(payload_id: str) -> int:
    digest = hashlib.blake2b(str(payload_id).encode("utf-8"), digest_size=2).digest()
    return int.from_bytes(digest, "big") % 100


def assign_full_split(candidates: pd.DataFrame) -> pd.DataFrame:
    out = candidates.copy()
    buckets = out["payload_id"].map(_bucket)
    out["split"] = "train"
    out.loc[buckets.between(80, 89), "split"] = "dev"
    out.loc[buckets.between(90, 97), "split"] = "test"
    out.loc[buckets >= 98, "split"] = "verified_candidate"
    return out


def write_full_report(
    path: Path,
    foundation: pd.DataFrame,
    split_payload_counts: dict[str, int],
    gate: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    family_rows = "\n".join(
        f"| {family} | {count} |"
        for family, count in foundation["action_family"].value_counts().items()
    )
    split_rows = "\n".join(
        f"| {split} | {count} |"
        for split, count in split_payload_counts.items()
    )
    text = f"""# 04 Full Data Foundation + Action Taxonomy

## Scope

This is the Gumbel namespace foundation under `data/gumbel/full`.
It does not reuse `Guiding/Phase 5` as a Gumbel phase. External artifacts may be
used only when explicitly passed as `--input`.

## Gate

- Result: `{gate['current_result']}`
- Reason: {gate['reason']}

## Rows

- Action rows: {len(foundation)}
- Unique payloads: {foundation['payload_id'].nunique()}
- Cluster/split policy: deterministic hash over `payload_id`
- Split leakage by payload_id: `0`

## Split Payload Counts

| Split | Unique payloads |
| --- | ---: |
{split_rows}

## Action Families

| Family | Rows |
| --- | ---: |
{family_rows}
"""
    path.write_text(text, encoding="utf-8")


def write_condition_report(
    path: Path,
    condition_table: pd.DataFrame,
    gate: dict[str, Any],
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    top = condition_table.sort_values("rows", ascending=False).head(30)
    rows = "\n".join(
        f"| {row.condition_id} | {row.technique_primary} | {row.db_hint} | "
        f"{row.action_family} | {row.rows} |"
        for row in top.itertuples(index=False)
    )
    text = f"""# 05 Label And Condition System

## Scope

This condition table belongs to the Gumbel action-surgery branch. The value
`unlabeled_db_hint` is a missing/unknown hint bucket, not a real database engine.

## Gate

- Result: `{gate['current_result']}`
- Reason: {gate['reason']}

## Condition Summary

- Condition rows: {len(condition_table)}
- Total action rows covered: {int(condition_table['rows'].sum()) if not condition_table.empty else 0}

| Condition | Technique | DB hint | Action family | Rows |
| --- | --- | --- | --- | ---: |
{rows}
"""
    path.write_text(text, encoding="utf-8")


def build_full_foundation(
    config: ProjectConfig,
    input_paths: list[Path] | None = None,
    max_rows: int = 100_000,
) -> dict[str, Any]:
    payloads = load_payloads(
        config,
        input_paths=input_paths,
        max_rows=max_rows,
        sqli_only=False,
    )
    candidates = build_action_candidate_table(payloads, seed=config.seed)
    foundation = assign_full_split(candidates)

    split_payload_counts = {
        split: int(group["payload_id"].nunique())
        for split, group in foundation.groupby("split", dropna=False)
    }
    family_counts = Counter(foundation["action_family"].astype(str))
    strong_families = [
        family
        for family, count in family_counts.items()
        if family not in {"none", "literal", "whitespace"} and count >= 100
    ]
    split_ok = all(
        foundation[foundation["split"].eq(split)]["payload_id"].nunique() > 0
        for split in ["train", "dev", "test"]
    )
    gate = {
        "current_result": "FULL_FOUNDATION_READY"
        if split_ok and len(strong_families) >= 3
        else "BLOCKED",
        "reason": "Gumbel full foundation has train/dev/test payloads and enough non-literal action families."
        if split_ok and len(strong_families) >= 3
        else "Gumbel full foundation lacks split coverage or non-literal action family coverage.",
        "strong_non_literal_families": strong_families,
    }

    write_parquet(foundation, config.full_dir / "action_foundation.parquet")
    write_json(
        {
            "split_policy": "deterministic blake2b bucket over payload_id",
            "payload_counts": split_payload_counts,
            "cluster_leakage": 0,
            "note": "payload_id is used as the leakage unit until a Gumbel-native near-duplicate cluster is added.",
        },
        config.full_dir / "action_splits.json",
    )
    write_full_report(
        config.report_dir / "04_full_data_foundation_action_taxonomy.md",
        foundation,
        split_payload_counts,
        gate,
    )
    update_timeline_progress(
        config,
        phase_id="G04",
        status="completed" if gate["current_result"] == "FULL_FOUNDATION_READY" else "blocked",
        progress_percent=65,
        gate_result=gate["current_result"],
        evidence_artifacts=[
            "data/gumbel/full/action_foundation.parquet",
            "data/gumbel/full/action_splits.json",
            "reports/gumbel/04_full_data_foundation_action_taxonomy.md",
        ],
        notes="G04 Gumbel-native full action foundation completed; build G05 condition table next.",
    )
    return {
        "gate": gate,
        "payload_rows": int(len(payloads)),
        "action_rows": int(len(foundation)),
        "split_payload_counts": split_payload_counts,
    }


def build_condition_table(config: ProjectConfig) -> dict[str, Any]:
    foundation_path = config.full_dir / "action_foundation.parquet"
    foundation = pd.read_parquet(foundation_path)
    group_cols = ["technique_primary", "db_hint", "action_family", "action_type", "split"]
    condition_table = (
        foundation.groupby(group_cols, dropna=False)
        .agg(
            rows=("payload_id", "size"),
            unique_payloads=("payload_id", "nunique"),
            mean_label_confidence=("label_confidence", "mean"),
            round_trip_success=("round_trip_success", "mean"),
        )
        .reset_index()
    )
    condition_table["condition_id"] = [
        "C" + hashlib.sha1(
            "|".join(str(row[col]) for col in group_cols).encode("utf-8")
        ).hexdigest()[:10]
        for _, row in condition_table.iterrows()
    ]
    condition_table = condition_table[
        [
            "condition_id",
            *group_cols,
            "rows",
            "unique_payloads",
            "mean_label_confidence",
            "round_trip_success",
        ]
    ]

    unknown_engine_rows = int(
        condition_table[condition_table["db_hint"].eq("unknown")]["rows"].sum()
    )
    gate = {
        "current_result": "CONDITION_READY"
        if not condition_table.empty and unknown_engine_rows == 0
        else "BLOCKED",
        "reason": "Gumbel condition table is populated; unknown is not used as a database engine class."
        if not condition_table.empty and unknown_engine_rows == 0
        else "Condition table is empty or contains `unknown` as a database engine class.",
        "unknown_engine_rows": unknown_engine_rows,
    }
    write_parquet(condition_table, config.full_dir / "condition_table.parquet")
    write_condition_report(
        config.report_dir / "05_label_condition_system.md",
        condition_table,
        gate,
    )
    update_timeline_progress(
        config,
        phase_id="G05",
        status="completed" if gate["current_result"] == "CONDITION_READY" else "blocked",
        progress_percent=72,
        gate_result=gate["current_result"],
        evidence_artifacts=[
            "data/gumbel/full/condition_table.parquet",
            "reports/gumbel/05_label_condition_system.md",
        ],
        notes="G05 Gumbel-native condition table completed; evaluator remains separated under G06.",
    )
    return {
        "gate": gate,
        "condition_rows": int(len(condition_table)),
        "action_rows_covered": int(condition_table["rows"].sum())
        if not condition_table.empty
        else 0,
    }
