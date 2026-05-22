from __future__ import annotations

from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd

from .config import ProjectConfig
from .dataset import build_action_candidate_table, load_payloads, write_parquet
from .reporting import (
    dataframe_coverage,
    update_timeline_progress,
    write_audit_report,
    write_json,
)
from .taxonomy import ACTION_TAXONOMY, taxonomy_payload


def decide_g0(candidates: pd.DataFrame, coverage: dict[str, Any]) -> dict[str, Any]:
    family_counts = Counter(candidates["action_family"].astype(str))
    non_literal_rows = candidates[
        ~candidates["action_family"].isin(["literal", "whitespace", "none"])
    ]
    non_literal_coverage = float(
        (candidates["non_literal_action_count"].fillna(0) > 0).mean()
    )
    strong_families = [
        family
        for family, count in family_counts.items()
        if family not in {"literal", "whitespace", "none"} and count >= 10
    ]
    coverage["non_literal_coverage"] = non_literal_coverage
    coverage["strong_non_literal_families"] = strong_families

    risks = []
    if non_literal_coverage < 0.25:
        risks.append("Non-literal action coverage is below 0.25.")
    if len(strong_families) < 3:
        risks.append("Fewer than three non-literal action families have enough rows.")
    if candidates["db_hint"].nunique() <= 1:
        risks.append("DB hint distribution is narrow; unknown is not treated as a DB class.")

    if len(non_literal_rows) >= 500 and len(strong_families) >= 3:
        decision = "S2_TAMPER_ACTION"
        reason = (
            "Action audit found enough non-literal tamper/action signal; "
            "use S2 tamper-action as the main path before any Gumbel GAN pilot."
        )
    elif family_counts.get("literal", 0) >= 500:
        decision = "S1_MASKED_SLOT"
        reason = (
            "Literal slots dominate and non-literal action signal is limited; "
            "continue only with masked-slot baselines."
        )
    else:
        decision = "STOP"
        reason = "The loaded data does not provide enough action or slot signal."

    return {
        "decision": decision,
        "reason": reason,
        "coverage": coverage,
        "risks": risks,
    }


def run_audit(
    config: ProjectConfig,
    input_paths: list[Path] | None = None,
    max_rows: int = 50_000,
) -> dict[str, Any]:
    payloads = load_payloads(config, input_paths=input_paths, max_rows=max_rows)
    candidates = build_action_candidate_table(payloads, seed=config.seed)
    coverage = dataframe_coverage(candidates)

    action_counts = candidates["action_type"].value_counts().to_dict()
    family_counts = candidates["action_family"].value_counts().to_dict()
    taxonomy = taxonomy_payload()
    taxonomy["observed"] = {
        "payload_rows": int(len(payloads)),
        "candidate_rows": int(len(candidates)),
        "action_type_counts": {str(k): int(v) for k, v in action_counts.items()},
        "action_family_counts": {str(k): int(v) for k, v in family_counts.items()},
        "known_families": list(ACTION_TAXONOMY),
    }

    decision = decide_g0(candidates, coverage)

    write_json(taxonomy, config.audit_dir / "action_taxonomy.json")
    write_parquet(candidates, config.audit_dir / "action_candidates.parquet")
    write_json(decision, config.audit_dir / "g0_decision.json")
    write_audit_report(
        config.report_dir / "01_slot_action_audit.md",
        decision,
        decision["coverage"],
        source_rows=len(payloads),
        candidate_rows=len(candidates),
    )
    update_timeline_progress(
        config,
        phase_id="G01",
        status="completed" if decision["decision"] != "STOP" else "failed",
        progress_percent=20,
        gate_result=decision["decision"],
        evidence_artifacts=[
            "reports/gumbel/01_slot_action_audit.md",
            "data/gumbel/audit/action_taxonomy.json",
            "data/gumbel/audit/action_candidates.parquet",
            "data/gumbel/audit/g0_decision.json",
        ],
        notes="G01 audit completed; build the G02 vertical slice next.",
    )
    return decision
