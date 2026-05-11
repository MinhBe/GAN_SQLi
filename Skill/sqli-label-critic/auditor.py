import random
import logging
from collections import defaultdict
from dataclasses import dataclass, field

from shared.patterns import ATTACK_KEYWORDS


logger = logging.getLogger("auditor")


@dataclass
class AuditReport:
    total_benign: int
    sample_size: int
    false_negatives: list[dict] = field(default_factory=list)
    fn_rate: float = 0.0
    recommendation: str = ""


@dataclass
class ConflictGroup:
    payload: str
    rows: list[int] = field(default_factory=list)
    conflict_types: list[str] = field(default_factory=list)
    verdict: str = ""
    resolution: str = ""


def benign_audit(rows: list[dict], sample_size: int = 500) -> AuditReport:
    benign_rows = [r for r in rows if r.get("sqli_type", "").strip() == "benign"]
    if not benign_rows:
        return AuditReport(total_benign=0, sample_size=0,
                          false_negatives=[], fn_rate=0.0,
                          recommendation="No benign rows to audit")

    sample = random.sample(benign_rows, min(sample_size, len(benign_rows)))
    false_negatives = []

    for row in sample:
        payload = row.get("payload_norm", "").lower()
        found = [kw for kw in ATTACK_KEYWORDS if kw in payload]
        if found:
            false_negatives.append({
                "row_index": row.get("row_index", "?"),
                "payload": row.get("payload_norm", "")[:80],
                "keywords": found,
            })

    fn_rate = len(false_negatives) / len(sample) * 100
    recommendation = (
        "Full re-review recommended" if fn_rate > 5
        else "Benign quality acceptable" if fn_rate <= 2
        else "Partial re-review recommended"
    )

    return AuditReport(
        total_benign=len(benign_rows),
        sample_size=len(sample),
        false_negatives=false_negatives,
        fn_rate=fn_rate,
        recommendation=recommendation,
    )


def find_conflicts(rows: list[dict]) -> list[ConflictGroup]:
    groups = defaultdict(list)
    for row in rows:
        payload = row.get("payload_norm", "").strip()
        if payload:
            groups[payload].append(row)

    conflicts = []
    for payload, group in groups.items():
        if len(group) < 2:
            continue
        types = set(r.get("sqli_type", "").strip() for r in group)
        row_indices = [int(r.get("row_index", 0)) for r in group]

        if len(types) > 1:
            conflicts.append(ConflictGroup(
                payload=payload,
                rows=row_indices,
                conflict_types=list(types),
                verdict="REJECT",
                resolution=f"Same payload but different types: {types}. Need re-label to unify"
            ))
        else:
            conflicts.append(ConflictGroup(
                payload=payload,
                rows=row_indices,
                conflict_types=list(types),
                verdict="FLAG",
                resolution=f"Exact duplicate ({len(group)} rows). Keep lowest row index"
            ))

    return conflicts
