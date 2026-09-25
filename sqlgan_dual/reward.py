from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Iterable, Mapping, Any

from .validators import StaticValidation, static_validate, tokens


@dataclass(frozen=True)
class RewardResult:
    payload: str
    static_score: float
    duplicate_penalty: float
    reward: float
    matched_contract_index: int | None
    validation: StaticValidation


def sha256_text(text: str) -> str:
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()


def _token_overlap(payload: str, contract: Mapping[str, Any]) -> int:
    tt = set(tokens(payload))
    required = str(contract.get("required_tokens") or contract.get("token_contract") or "")
    sig = str(contract.get("structure_signature") or contract.get("skeleton") or "")
    return len(tt & set(tokens(required + " " + sig)))


def candidate_contracts(payload: str, contracts: list[dict[str, Any]] | None, *, top_k: int = 32) -> list[tuple[int | None, dict[str, Any] | None]]:
    if not contracts:
        return [(None, None)]
    ranked = sorted(enumerate(contracts), key=lambda x: _token_overlap(payload, x[1]), reverse=True)
    return ranked[: max(1, min(top_k, len(ranked)))]


def score_payload(
    payload: str,
    contracts: list[dict[str, Any]] | None = None,
    *,
    training_hashes: set[str] | None = None,
    duplicate_penalty: float = 0.25,
    strict_required: bool = False,
) -> RewardResult:
    best_idx: int | None = None
    best_v: StaticValidation | None = None
    for idx, contract in candidate_contracts(payload, contracts):
        v = static_validate(payload, contract, strict_required=strict_required)
        if best_v is None or v.static_score > best_v.static_score:
            best_v = v
            best_idx = idx
    assert best_v is not None
    dup = duplicate_penalty if training_hashes and sha256_text(payload) in training_hashes else 0.0
    reward = max(0.0, best_v.static_score - dup)
    return RewardResult(payload=payload, static_score=best_v.static_score, duplicate_penalty=dup, reward=reward, matched_contract_index=best_idx, validation=best_v)


def score_many(payloads: Iterable[str], contracts: list[dict[str, Any]] | None = None, *, training_hashes: set[str] | None = None, strict_required: bool = False) -> list[RewardResult]:
    return [score_payload(p, contracts, training_hashes=training_hashes, strict_required=strict_required) for p in payloads]
