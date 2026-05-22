from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
import hashlib
import json
import random
import re
from typing import Any, Iterable


SQL_KEYWORDS = [
    "select",
    "union",
    "where",
    "from",
    "and",
    "or",
    "like",
    "between",
    "insert",
    "update",
    "delete",
    "drop",
    "sleep",
    "benchmark",
    "case",
    "when",
    "then",
    "else",
    "end",
    "order",
    "group",
    "having",
    "limit",
]

DB_FUNCTIONS = [
    "sleep",
    "pg_sleep",
    "benchmark",
    "extractvalue",
    "updatexml",
    "load_file",
    "version",
    "database",
    "user",
    "utl_inaddr.get_host_address",
    "chr",
    "char",
    "concat",
    "substring",
    "substr",
    "ascii",
    "cast",
    "convert",
]

ACTION_TAXONOMY: dict[str, dict[str, Any]] = {
    "literal": {
        "description": "String, numeric, delexed, identifier-like literal slots.",
        "actions": ["literal_mask"],
    },
    "operator": {
        "description": "Logical and comparison operator actions.",
        "actions": ["logical_operator_swap", "compare_operator_swap"],
    },
    "comment": {
        "description": "Inline, line, and hash comment tamper actions.",
        "actions": ["inline_comment", "comment_style_swap"],
    },
    "encoding": {
        "description": "URL, hex, and numeric/string encoding actions.",
        "actions": ["number_encoding", "string_encoding"],
    },
    "function": {
        "description": "SQL function choice and equivalent function variants.",
        "actions": ["function_variant"],
    },
    "keyword_variant": {
        "description": "Keyword case, splitting, and spelling-preserving variants.",
        "actions": ["case_swap", "keyword_split"],
    },
    "whitespace": {
        "description": "Whitespace normalization, tab/newline, and comment-as-space variants.",
        "actions": ["whitespace_swap"],
    },
    "tamper_candidate": {
        "description": "Composable non-literal SQLi action-surgery candidate.",
        "actions": ["logic_constant_insert"],
    },
}

ACTION_PRIORITY = [
    "comment",
    "encoding",
    "function",
    "operator",
    "keyword_variant",
    "whitespace",
    "literal",
    "tamper_candidate",
]

STRING_RE = re.compile(r"(?P<quote>['\"])(?:\\.|(?!\1).)*\1")
NUMBER_RE = re.compile(r"(?<![\w.])-?\d+(?:\.\d+)?(?![\w.])")
DELEX_RE = re.compile(r"__[A-Z][A-Z0-9_]*__")
COMMENT_RE = re.compile(r"(--[^\r\n]*|#[^\r\n]*|/\*.*?\*/)", re.DOTALL)
URL_ENCODING_RE = re.compile(r"%[0-9A-Fa-f]{2}")
HEX_RE = re.compile(r"\b0x[0-9A-Fa-f]+\b")
COMPARE_RE = re.compile(r"(?<![<>=!])(?:<>|!=|>=|<=|=|<|>)(?![<>=])")
LOGICAL_RE = re.compile(r"\b(?:and|or)\b", re.IGNORECASE)
WHITESPACE_RE = re.compile(r"(\s+|\+)")
FUNCTION_RE = re.compile(
    r"\b(?:"
    + "|".join(re.escape(name) for name in sorted(DB_FUNCTIONS, key=len, reverse=True))
    + r")\s*\(",
    re.IGNORECASE,
)
KEYWORD_RE = re.compile(
    r"\b(?:" + "|".join(re.escape(keyword) for keyword in SQL_KEYWORDS) + r")\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class ActionHit:
    family: str
    action_type: str
    value: str
    start: int
    end: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "family": self.family,
            "action_type": self.action_type,
            "value": self.value,
            "start": self.start,
            "end": self.end,
        }


def payload_id(payload: str) -> str:
    return hashlib.sha1(payload.encode("utf-8", errors="ignore")).hexdigest()[:16]


def _hits_from_regex(
    payload: str,
    regex: re.Pattern[str],
    family: str,
    action_type: str,
) -> list[ActionHit]:
    return [
        ActionHit(family, action_type, match.group(0), match.start(), match.end())
        for match in regex.finditer(payload)
    ]


def _keyword_variant_hits(payload: str) -> list[ActionHit]:
    hits: list[ActionHit] = []
    for match in KEYWORD_RE.finditer(payload):
        value = match.group(0)
        action = "case_swap" if value != value.lower() else "keyword_split"
        hits.append(
            ActionHit("keyword_variant", action, value, match.start(), match.end())
        )

    split_keyword = re.compile(
        r"\b(?:u\s*/\*.*?\*/\s*nion|sel\s*/\*.*?\*/\s*ect|or\s*/\*.*?\*/\s*der)\b",
        re.IGNORECASE | re.DOTALL,
    )
    for match in split_keyword.finditer(payload):
        hits.append(
            ActionHit(
                "keyword_variant",
                "keyword_split",
                match.group(0),
                match.start(),
                match.end(),
            )
        )
    return hits


def detect_actions(payload: str) -> list[dict[str, Any]]:
    payload = str(payload or "")
    hits: list[ActionHit] = []
    hits.extend(_hits_from_regex(payload, STRING_RE, "literal", "literal_mask"))
    hits.extend(_hits_from_regex(payload, DELEX_RE, "literal", "literal_mask"))
    hits.extend(_hits_from_regex(payload, NUMBER_RE, "literal", "literal_mask"))
    hits.extend(_hits_from_regex(payload, COMMENT_RE, "comment", "inline_comment"))
    hits.extend(_hits_from_regex(payload, URL_ENCODING_RE, "encoding", "string_encoding"))
    hits.extend(_hits_from_regex(payload, HEX_RE, "encoding", "number_encoding"))
    hits.extend(_hits_from_regex(payload, COMPARE_RE, "operator", "compare_operator_swap"))
    hits.extend(_hits_from_regex(payload, LOGICAL_RE, "operator", "logical_operator_swap"))
    hits.extend(_hits_from_regex(payload, FUNCTION_RE, "function", "function_variant"))
    hits.extend(_keyword_variant_hits(payload))
    hits.extend(_hits_from_regex(payload, WHITESPACE_RE, "whitespace", "whitespace_swap"))

    if any(hit.family != "literal" for hit in hits):
        hits.append(ActionHit("tamper_candidate", "logic_constant_insert", "", len(payload), len(payload)))

    hits.sort(key=lambda hit: (hit.start, hit.end, hit.family, hit.action_type))
    return [hit.to_dict() for hit in hits]


def detect_families(payload: str) -> set[str]:
    return {hit["family"] for hit in detect_actions(payload)}


def primary_action_family(actions: Iterable[dict[str, Any]]) -> str:
    families = {action["family"] for action in actions}
    for family in ACTION_PRIORITY:
        if family in families:
            return family
    return "none"


def action_counts(actions: Iterable[dict[str, Any]]) -> dict[str, int]:
    return dict(Counter(action["family"] for action in actions))


def _literal_slots(payload: str) -> list[ActionHit]:
    hits = []
    for regex in (STRING_RE, DELEX_RE, NUMBER_RE):
        hits.extend(
            ActionHit("literal", "literal_mask", match.group(0), match.start(), match.end())
            for match in regex.finditer(payload)
        )
    hits.sort(key=lambda hit: (hit.start, -(hit.end - hit.start)))

    selected: list[ActionHit] = []
    occupied: list[tuple[int, int]] = []
    for hit in hits:
        if any(not (hit.end <= start or hit.start >= end) for start, end in occupied):
            continue
        selected.append(hit)
        occupied.append((hit.start, hit.end))
    return sorted(selected, key=lambda hit: hit.start)


def make_action_frame(payload: str) -> dict[str, Any]:
    payload = str(payload or "")
    slots = []
    template = payload
    for idx, hit in enumerate(reversed(_literal_slots(payload))):
        placeholder = f"__TMP_SLOT_{idx}__"
        template = template[: hit.start] + placeholder + template[hit.end :]
        slots.append(
            {
                "placeholder": placeholder,
                "family": hit.family,
                "action_type": hit.action_type,
                "value": hit.value,
                "start": hit.start,
                "end": hit.end,
            }
        )
    slots = sorted(slots, key=lambda slot: slot["start"])
    for idx, slot in enumerate(slots):
        old_placeholder = slot["placeholder"]
        new_placeholder = f"__SLOT_{idx}__"
        if old_placeholder != new_placeholder:
            template = template.replace(old_placeholder, new_placeholder, 1)
            slot["placeholder"] = new_placeholder

    actions = detect_actions(payload)
    return {
        "payload_id": payload_id(payload),
        "payload_norm": payload,
        "template": template,
        "slots_json": json.dumps(slots, ensure_ascii=True),
        "actions_json": json.dumps(actions, ensure_ascii=True),
        "primary_action_family": primary_action_family(actions),
        "action_count": len(actions),
        "literal_slot_count": sum(1 for action in actions if action["family"] == "literal"),
        "non_literal_action_count": sum(
            1
            for action in actions
            if action["family"] not in {"literal", "whitespace"}
        ),
    }


def reconstruct_payload(template: str, slots_json: str | list[dict[str, Any]]) -> str:
    slots = json.loads(slots_json) if isinstance(slots_json, str) else slots_json
    payload = str(template)
    for slot in slots:
        payload = payload.replace(slot["placeholder"], slot["value"], 1)
    return payload


def candidate_action_types(payload: str) -> list[str]:
    families = detect_families(payload)
    actions: list[str] = []
    if "keyword_variant" in families:
        actions.extend(["case_swap", "keyword_split"])
    if "whitespace" in families:
        actions.append("whitespace_swap")
    if "operator" in families:
        actions.extend(["logical_operator_swap", "compare_operator_swap"])
    if "literal" in families:
        actions.extend(["number_encoding", "string_encoding"])
    if "function" in families:
        actions.append("function_variant")
    if "comment" not in families and ("keyword_variant" in families or "operator" in families):
        actions.append("inline_comment")
    if "operator" in families or "keyword_variant" in families:
        actions.append("logic_constant_insert")
    return sorted(set(actions))


def apply_action(payload: str, action_type: str, seed: int | None = None) -> str:
    rng = random.Random(seed)
    payload = str(payload or "")

    if action_type == "case_swap":
        def swap(match: re.Match[str]) -> str:
            token = match.group(0)
            return token.upper() if token.islower() else token.lower()

        return KEYWORD_RE.sub(swap, payload, count=1)

    if action_type == "keyword_split":
        def split(match: re.Match[str]) -> str:
            token = match.group(0)
            if len(token) < 4:
                return token
            idx = max(1, len(token) // 2)
            return token[:idx] + "/**/" + token[idx:]

        return KEYWORD_RE.sub(split, payload, count=1)

    if action_type == "whitespace_swap":
        if " " in payload:
            return re.sub(r"\s+", rng.choice(["/**/", "%09", "\t"]), payload, count=1)
        return payload + "/**/"

    if action_type == "logical_operator_swap":
        def logical(match: re.Match[str]) -> str:
            return "OR" if match.group(0).lower() == "and" else "AND"

        return LOGICAL_RE.sub(logical, payload, count=1)

    if action_type == "compare_operator_swap":
        mapping = {"=": "LIKE", "!=": "<>", "<>": "!=", ">": ">=", "<": "<=", ">=": ">", "<=": "<"}
        return COMPARE_RE.sub(lambda m: mapping.get(m.group(0), m.group(0)), payload, count=1)

    if action_type == "number_encoding":
        def encode_number(match: re.Match[str]) -> str:
            value = match.group(0)
            try:
                number = int(float(value))
            except ValueError:
                return value
            return hex(number)

        return NUMBER_RE.sub(encode_number, payload, count=1)

    if action_type == "string_encoding":
        match = STRING_RE.search(payload)
        if not match:
            return payload
        raw = match.group(0).strip("'\"")
        if not raw:
            return payload
        encoded = "CHAR(" + ",".join(str(ord(ch)) for ch in raw[:24]) + ")"
        return payload[: match.start()] + encoded + payload[match.end() :]

    if action_type == "inline_comment":
        match = KEYWORD_RE.search(payload)
        if not match:
            return payload + "/**/"
        token = match.group(0)
        if len(token) < 4:
            return payload[: match.end()] + "/**/" + payload[match.end() :]
        idx = match.start() + max(1, len(token) // 2)
        return payload[:idx] + "/**/" + payload[idx:]

    if action_type == "function_variant":
        variants = {
            "sleep": "pg_sleep",
            "pg_sleep": "sleep",
            "substring": "substr",
            "substr": "substring",
            "char": "chr",
            "chr": "char",
        }

        def variant(match: re.Match[str]) -> str:
            name = match.group(0)[:-1].strip()
            repl = variants.get(name.lower(), name)
            return repl + "("

        return FUNCTION_RE.sub(variant, payload, count=1)

    if action_type == "logic_constant_insert":
        connector = " AND " if re.search(r"\bwhere\b|\band\b|\bor\b", payload, re.IGNORECASE) else " OR "
        return payload.rstrip() + connector + "1=1"

    return payload


def build_candidate_rows(payload: str, seed: int = 0) -> list[dict[str, Any]]:
    frame = make_action_frame(payload)
    rows = []
    for idx, action_type in enumerate(candidate_action_types(payload)):
        mutated = apply_action(payload, action_type, seed=seed + idx)
        action_family = _action_type_family(action_type)
        rows.append(
            {
                **frame,
                "candidate_id": f"{frame['payload_id']}_{idx:02d}",
                "action_type": action_type,
                "action_family": action_family,
                "generated_payload": mutated,
                "mutation_changed": mutated != payload,
                "round_trip_payload": reconstruct_payload(frame["template"], frame["slots_json"]),
            }
        )
    if not rows:
        rows.append(
            {
                **frame,
                "candidate_id": f"{frame['payload_id']}_00",
                "action_type": "identity",
                "action_family": "none",
                "generated_payload": payload,
                "mutation_changed": False,
                "round_trip_payload": reconstruct_payload(frame["template"], frame["slots_json"]),
            }
        )
    return rows


def _action_type_family(action_type: str) -> str:
    for family, spec in ACTION_TAXONOMY.items():
        if action_type in spec["actions"]:
            return family
    return "none"


def taxonomy_payload() -> dict[str, Any]:
    return {
        "schema_version": "1.0",
        "families": ACTION_TAXONOMY,
        "policy": {
            "implementation_scope": "action_surgery_only",
            "excluded": ["full_sequence_gan", "wgan_gp", "reinforce", "mc_rollout"],
        },
    }
