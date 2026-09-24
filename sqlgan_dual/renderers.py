from __future__ import annotations

import random
import re
from dataclasses import dataclass
from typing import Callable, Iterable
from urllib.parse import quote, unquote

from .validators import normalize_sqlish, static_validate


@dataclass(frozen=True)
class RenderedPayload:
    parent_payload: str
    derived_payload: str
    derived_level: str
    recipe_id: str
    payload_decoded: str
    payload_normalized: str
    roundtrip_valid: bool
    structure_preserved: bool
    semantic_preserved: bool


def url_full(payload: str) -> str:
    return quote(payload, safe="")


def url_spaces_ops(payload: str) -> str:
    out = []
    for ch in payload:
        if ch.isspace() or ch in "()=<>,'":
            out.append(quote(ch, safe=""))
        else:
            out.append(ch)
    return "".join(out)


def tab_space(payload: str) -> str:
    return re.sub(r"\s+", "\t ", payload)


def comment_spacing(payload: str) -> str:
    # Representation transform for offline corpus work. Keep it simple and reversible-ish.
    return re.sub(r"\s+", "/**/", payload)


def keyword_case(payload: str) -> str:
    keywords = {"and", "or", "not", "in", "between", "like", "ilike", "is", "null", "true", "false"}
    def repl(m):
        w = m.group(0)
        if w.lower() in keywords:
            return "".join(c.upper() if i % 2 else c.lower() for i, c in enumerate(w))
        return w
    return re.sub(r"\b[A-Za-z_]+\b", repl, payload)


Y3_RECIPES: dict[str, Callable[[str], str]] = {
    "T_Y3_URL_FULL": url_full,
    "T_Y3_URL_SPACE_OPERATOR_QUOTE": url_spaces_ops,
}
Y4_RECIPES: dict[str, Callable[[str], str]] = {
    "T_Y4_TAB_SPACE": tab_space,
    "T_Y4_COMMENT_SPACE": comment_spacing,
    "T_Y4_KEYWORD_CASE": keyword_case,
}


def decode_y3(payload: str, recipe_id: str) -> str:
    return unquote(payload)


def normalize_y4(payload: str, recipe_id: str) -> str:
    return normalize_sqlish(payload)


def render_one(parent_payload: str, derived_level: str, recipe_id: str | None = None) -> RenderedPayload:
    if derived_level == "Y3":
        recipes = Y3_RECIPES
        recipe_id = recipe_id or random.choice(list(recipes))
        derived = recipes[recipe_id](parent_payload)
        decoded = decode_y3(derived, recipe_id)
        normalized = normalize_sqlish(decoded)
    elif derived_level == "Y4":
        recipes = Y4_RECIPES
        recipe_id = recipe_id or random.choice(list(recipes))
        derived = recipes[recipe_id](parent_payload)
        decoded = derived
        normalized = normalize_y4(derived, recipe_id)
    else:
        raise ValueError("derived_level must be Y3 or Y4")

    parent_norm = normalize_sqlish(parent_payload)
    roundtrip = normalize_sqlish(decoded) == parent_norm or normalized == parent_norm
    parent_valid = static_validate(parent_norm).final_accept
    child_valid = static_validate(normalized).final_accept
    return RenderedPayload(
        parent_payload=parent_payload,
        derived_payload=derived,
        derived_level=derived_level,
        recipe_id=recipe_id,
        payload_decoded=decoded,
        payload_normalized=normalized,
        roundtrip_valid=roundtrip,
        structure_preserved=child_valid,
        semantic_preserved=roundtrip and parent_valid and child_valid,
    )


def render_many(parent_payloads: Iterable[str], derived_level: str, per_parent: int = 1, seed: int = 7) -> list[dict]:
    random.seed(seed)
    rows = []
    recipes = list(Y3_RECIPES if derived_level == "Y3" else Y4_RECIPES)
    for idx, p in enumerate(parent_payloads):
        for j in range(per_parent):
            rid = recipes[(idx + j) % len(recipes)]
            r = render_one(p, derived_level=derived_level, recipe_id=rid)
            rows.append({
                "parent_index": idx,
                "parent_payload": r.parent_payload,
                "derived_payload": r.derived_payload,
                "derived_level": r.derived_level,
                "recipe_id": r.recipe_id,
                "payload_decoded": r.payload_decoded,
                "payload_normalized": r.payload_normalized,
                "roundtrip_valid": int(r.roundtrip_valid),
                "structure_preserved": int(r.structure_preserved),
                "semantic_preserved": int(r.semantic_preserved),
            })
    return rows
