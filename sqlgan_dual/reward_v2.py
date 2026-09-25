from __future__ import annotations

import hashlib
import json
import math
import re
from dataclasses import dataclass, asdict
from typing import Any, Iterable, Mapping

try:
    from .validators import static_validate, tokens as validator_tokens
except Exception:  # pragma: no cover - fallback for isolated tests
    static_validate = None
    validator_tokens = None

PREFIX_RE = re.compile(r"^(?P<prefix><RULE=(?P<rule>[^>]+)><CELL=(?P<cell>[^>]+)><FAMILY=(?P<family>[^>]+)>)\s*(?P<payload>.*)$", re.S)
WORD_RE = re.compile(r"[A-Za-z_]+|<>|!=|>=|<=|=|>|<|\?|&&|@>|<@|~\*|!~\*|!~|~|\(|\)|\[|\]|,|\+|-|\*|/|%")
STRING_RE = re.compile(r"'(?:''|[^'])*'")
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")


@dataclass(frozen=True)
class RewardV2Result:
    payload: str
    payload_stripped: str
    reward: float
    hard_gate_pass: bool
    static_score: float
    ruleset_score: float
    skeleton_score: float
    slot_score: float
    structure_score: float
    diversity_score: float
    coverage_score: float
    length_score: float
    duplicate_penalty: float
    near_duplicate_penalty: float
    off_ruleset_penalty: float
    matched_ruleset_id: str | None
    matched_structure_cell_id: str | None
    target_ruleset_id: str | None
    target_structure_cell_id: str | None
    error_class: str
    delimiter_valid: bool
    quote_valid: bool
    boolean_signal_valid: bool
    required_tokens_valid: bool
    skeleton_valid: bool
    slot_sanity_valid: bool
    off_ruleset: bool
    reward_version: str = "reward_v2.0-cseqgan-minimal"

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def sha256_text(text: str) -> str:
    return hashlib.sha256(str(text).encode("utf-8")).hexdigest()


def parse_condition_prefix(text: str) -> tuple[dict[str, str], str]:
    m = PREFIX_RE.match(str(text or ""))
    if not m:
        return {}, str(text or "")
    meta = {"ruleset_id": m.group("rule"), "structure_cell_id": m.group("cell"), "ruleset_family": m.group("family"), "prefix": m.group("prefix")}
    return meta, m.group("payload").strip()


def _tok(sql: str) -> list[str]:
    if validator_tokens is not None:
        try:
            return [str(x).upper() for x in validator_tokens(sql)]
        except Exception:
            pass
    no_str = STRING_RE.sub("'<STR>'", str(sql or ""))
    return [x.upper() for x in WORD_RE.findall(no_str)]


def _split_required(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, (list, tuple, set)):
        raw = list(value)
    else:
        s = str(value).strip()
        if not s or s.lower() == "nan":
            return []
        try:
            parsed = json.loads(s)
            raw = parsed if isinstance(parsed, list) else [parsed]
        except Exception:
            raw = re.split(r"\s*\|\s*|\s*,\s*|\s+", s)
    return [str(x).strip().upper() for x in raw if str(x).strip()]


def _target(contract: Mapping[str, Any], *names: str, default: str = "") -> str:
    for name in names:
        val = contract.get(name)
        if val not in (None, "", "nan"):
            return str(val)
    return default


def _jaccard(a: Iterable[str], b: Iterable[str]) -> float:
    sa, sb = set(a), set(b)
    if not sa and not sb:
        return 1.0
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / max(len(sa | sb), 1)


def _required_token_score(payload: str, required_tokens: Any) -> float:
    req = _split_required(required_tokens)
    if not req:
        return 1.0
    toks = set(_tok(payload))
    upper = payload.upper()
    hits = sum(1 for r in req if r in toks or r in upper)
    return hits / max(len(req), 1)


def _skeleton_score(payload: str, skeleton_reference: str, required_tokens: Any) -> float:
    if not skeleton_reference:
        return _required_token_score(payload, required_tokens)
    a = _tok(payload)
    b = _tok(str(skeleton_reference))
    overlap = _jaccard(a, b)
    req = _required_token_score(payload, required_tokens)
    # Brackets and parenthesis shape are cheap but useful for this corpus.
    shape_markers = ["(", ")", "[", "]"]
    want = [m for m in shape_markers if m in str(skeleton_reference)]
    if want:
        got = sum(1 for m in want if m in payload) / len(want)
    else:
        got = 1.0
    return max(0.0, min(1.0, 0.50 * overlap + 0.35 * req + 0.15 * got))


def _slot_schema(contract: Mapping[str, Any]) -> dict[str, Any]:
    raw = contract.get("slot_schema_json") or contract.get("target_slot_schema_json") or ""
    if isinstance(raw, dict):
        return raw
    if not raw or str(raw).lower() == "nan":
        return {}
    try:
        return json.loads(str(raw))
    except Exception:
        return {}


def _slot_type_ok(payload: str, slot: Mapping[str, Any]) -> bool:
    p = str(payload or "")
    up = p.upper()
    st = str(slot.get("type") or slot.get("slot_type") or "").lower()
    allowed = slot.get("allowed_values")
    if allowed:
        return any(str(x).upper() in up for x in allowed)
    # Check compound SQL types before the generic "literal" branch.
    if "array" in st:
        return "ARRAY[" in up or ("[" in p and "]" in p)
    if "jsonb" in st or "json" in st:
        return "JSONB" in up or "::JSONB" in up or "{" in p or "[" in p
    if "inet" in st or "cidr" in st:
        return "INET" in up or "CIDR" in up or re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", p) is not None
    if "uuid" in st:
        return re.search(r"[0-9a-fA-F]{8}-[0-9a-fA-F-]{27,}", p) is not None
    if "integer" in st or st in {"int", "int_literal", "bounded_integer_literal"}:
        return NUMBER_RE.search(p) is not None
    if "text" in st or "string" in st or ("literal" in st and "integer" not in st and "int_" not in st):
        return STRING_RE.search(p) is not None or "STR" in up
    if "operator" in st:
        return bool(set(_tok(p)) & {"=", "<>", "!=", ">", "<", ">=", "<=", "?", "&&", "@>", "<@", "~", "!~", "~*", "!~*", "LIKE", "ILIKE", "BETWEEN", "IN"})
    return True


def _slot_score(payload: str, contract: Mapping[str, Any]) -> float:
    schema = _slot_schema(contract)
    slots = schema.get("slots") if isinstance(schema, dict) else None
    if not slots:
        # Fallback to semantic-family heuristics.
        fam = _target(contract, "ruleset_family", "semantic_family", "target_semantic_family").lower()
        checks = []
        if "array" in fam:
            checks.append("ARRAY[" in payload.upper())
        if "json" in fam:
            checks.append("JSONB" in payload.upper() or "::jsonb" in payload.lower() or "{" in payload)
        if "inet" in fam or "cidr" in fam:
            checks.append(bool(re.search(r"\b\d{1,3}(?:\.\d{1,3}){3}\b", payload)) or "INET" in payload.upper() or "CIDR" in payload.upper())
        if "text" in fam or "regex" in fam or "like" in fam:
            checks.append(STRING_RE.search(payload) is not None)
        if not checks:
            return 1.0
        return sum(bool(x) for x in checks) / len(checks)
    ok = [_slot_type_ok(payload, s) for s in slots if isinstance(s, Mapping)]
    if not ok:
        return 1.0
    return sum(ok) / len(ok)


def _structure_score(payload: str) -> tuple[float, dict[str, bool], str]:
    if static_validate is not None:
        try:
            v = static_validate(payload)
            checks = {
                "delimiter_valid": bool(getattr(v, "delimiter_valid", False)),
                "quote_valid": bool(getattr(v, "quote_valid", False)),
                "boolean_signal_valid": bool(getattr(v, "boolean_signal_valid", False)),
                "required_tokens_valid": bool(getattr(v, "required_tokens_valid", True)),
                "skeleton_valid": bool(getattr(v, "skeleton_valid", True)),
                "slot_sanity_valid": bool(getattr(v, "slot_sanity_valid", True)),
            }
            return float(getattr(v, "static_score", 0.0)), checks, str(getattr(v, "error_class", ""))
        except Exception:
            pass
    # Minimal fallback.
    depth = 0
    quote = False
    delimiter_ok = True
    i = 0
    while i < len(payload):
        ch = payload[i]
        if ch == "'":
            if quote and i + 1 < len(payload) and payload[i + 1] == "'":
                i += 2
                continue
            quote = not quote
        elif not quote:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth < 0:
                    delimiter_ok = False
                    break
        i += 1
    delimiter_ok = delimiter_ok and depth == 0
    quote_ok = not quote
    bool_ok = bool(set(_tok(payload)) & {"=", "<>", "!=", ">", "<", ">=", "<=", "IS", "IN", "LIKE", "ILIKE", "BETWEEN", "?", "&&", "@>", "<@", "~", "!~", "TRUE", "FALSE"})
    checks = {
        "delimiter_valid": delimiter_ok,
        "quote_valid": quote_ok,
        "boolean_signal_valid": bool_ok,
        "required_tokens_valid": True,
        "skeleton_valid": True,
        "slot_sanity_valid": True,
    }
    score = sum(checks.values()) / len(checks)
    error = "ok" if all(checks.values()) else "+".join(k.replace("_valid", "") for k, v in checks.items() if not v)
    return score, checks, error


def score_payload_v2(
    payload: str,
    target_contract: Mapping[str, Any],
    *,
    training_hashes: set[str] | None = None,
    recent_payloads: list[str] | None = None,
    coverage_count: int = 0,
    max_len: int = 256,
    reward_floor: float = 0.02,
) -> RewardV2Result:
    meta, stripped = parse_condition_prefix(payload)
    target_rule = _target(target_contract, "ruleset_id", "target_ruleset_id") or None
    target_cell = _target(target_contract, "structure_cell_id", "target_structure_cell_id") or None
    target_family = _target(target_contract, "ruleset_family", "target_ruleset_family", "semantic_family", "target_semantic_family")
    gen_rule = meta.get("ruleset_id")
    gen_cell = meta.get("structure_cell_id")
    gen_family = meta.get("ruleset_family")

    if target_rule and gen_rule == target_rule:
        r_ruleset = 1.0
    elif target_family and gen_family == target_family:
        r_ruleset = 0.7
    elif gen_rule or gen_family:
        r_ruleset = 0.35
    else:
        # No prefix in generated text: judge only by content.
        r_ruleset = 0.55 if _required_token_score(stripped, target_contract.get("required_tokens")) >= 0.75 else 0.25

    r_skeleton = _skeleton_score(stripped, _target(target_contract, "skeleton_reference", "target_skeleton_reference"), target_contract.get("required_tokens") or target_contract.get("target_required_tokens"))
    r_slot = _slot_score(stripped, target_contract)
    static_score, checks, error = _structure_score(stripped)
    r_structure = static_score

    dup = 0.20 if training_hashes and sha256_text(payload) in training_hashes else 0.0
    near_pen = 0.0
    diversity = 1.0
    if recent_payloads:
        this = set(_tok(stripped))
        sims = [_jaccard(this, _tok(parse_condition_prefix(x)[1])) for x in recent_payloads[-256:]]
        mx = max(sims) if sims else 0.0
        diversity = max(0.0, 1.0 - mx)
        near_pen = 0.20 if mx >= 0.92 else 0.10 if mx >= 0.82 else 0.0
    coverage = 1.0 / math.sqrt(1.0 + max(0, int(coverage_count)))
    length = max(0.0, min(1.0, 1.0 - max(0, len(str(payload)) - max_len) / max(max_len, 1)))
    off_ruleset = bool(target_rule and gen_rule and gen_rule != target_rule)
    off_pen = 0.25 if off_ruleset else 0.0

    hard_gate = bool(checks["delimiter_valid"] and checks["quote_valid"] and checks["boolean_signal_valid"])
    raw_reward = (
        0.30 * r_ruleset
        + 0.25 * r_skeleton
        + 0.20 * r_slot
        + 0.10 * diversity
        + 0.10 * coverage
        + 0.05 * length
        - dup
        - near_pen
        - off_pen
    )
    if not hard_gate:
        raw_reward *= 0.35
    reward = max(float(reward_floor), min(1.0, raw_reward))
    return RewardV2Result(
        payload=payload,
        payload_stripped=stripped,
        reward=round(reward, 6),
        hard_gate_pass=hard_gate,
        static_score=round(float(static_score), 6),
        ruleset_score=round(float(r_ruleset), 6),
        skeleton_score=round(float(r_skeleton), 6),
        slot_score=round(float(r_slot), 6),
        structure_score=round(float(r_structure), 6),
        diversity_score=round(float(diversity), 6),
        coverage_score=round(float(coverage), 6),
        length_score=round(float(length), 6),
        duplicate_penalty=round(float(dup), 6),
        near_duplicate_penalty=round(float(near_pen), 6),
        off_ruleset_penalty=round(float(off_pen), 6),
        matched_ruleset_id=gen_rule or target_rule,
        matched_structure_cell_id=gen_cell or target_cell,
        target_ruleset_id=target_rule,
        target_structure_cell_id=target_cell,
        error_class=error or "ok",
        delimiter_valid=checks["delimiter_valid"],
        quote_valid=checks["quote_valid"],
        boolean_signal_valid=checks["boolean_signal_valid"],
        required_tokens_valid=_required_token_score(stripped, target_contract.get("required_tokens") or target_contract.get("target_required_tokens")) >= 0.999,
        skeleton_valid=r_skeleton >= 0.70,
        slot_sanity_valid=r_slot >= 0.70,
        off_ruleset=off_ruleset,
    )


def score_many_v2(
    payloads: Iterable[str],
    target_contracts: Iterable[Mapping[str, Any]],
    *,
    training_hashes: set[str] | None = None,
    recent_payloads: list[str] | None = None,
    coverage_counts: Mapping[str, int] | None = None,
    max_len: int = 256,
) -> list[RewardV2Result]:
    out: list[RewardV2Result] = []
    coverage_counts = coverage_counts or {}
    for payload, contract in zip(payloads, target_contracts):
        key = _target(contract, "ruleset_id", "target_ruleset_id")
        out.append(
            score_payload_v2(
                payload,
                contract,
                training_hashes=training_hashes,
                recent_payloads=recent_payloads,
                coverage_count=int(coverage_counts.get(key, 0)),
                max_len=max_len,
            )
        )
    return out
