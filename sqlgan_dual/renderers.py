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
    return "".join(quote(ch, safe="") if ch.isspace() or ch in "()=<>,'" else ch for ch in payload)


def tab_space(payload: str) -> str:
    return re.sub(r"\s+", "\t ", payload)


def comment_spacing(payload: str) -> str:
    return re.sub(r"\s+", "/**/", payload)


def keyword_case(payload: str) -> str:
    keywords = {"and", "or", "not", "in", "between", "like", "ilike", "is", "null", "true", "false", "exists"}

    def repl(m: re.Match[str]) -> str:
        w = m.group(0)
        if w.lower() not in keywords:
            return w
        return "".join(ch.upper() if i % 2 else ch.lower() for i, ch in enumerate(w))

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


def render_one(parent_payload: str, derived_level: str, recipe_id: str | None = None) -> RenderedPayload:
    parent_payload = str(parent_payload)
    if derived_level == "Y3":
        recipes = Y3_RECIPES
        recipe_id = recipe_id or random.choice(list(recipes))
        derived = recipes[recipe_id](parent_payload)
        decoded = unquote(derived)
        normalized = normalize_sqlish(decoded)
    elif derived_level == "Y4":
        recipes = Y4_RECIPES
        recipe_id = recipe_id or random.choice(list(recipes))
        derived = recipes[recipe_id](parent_payload)
        decoded = derived
        normalized = normalize_sqlish(derived)
    else:
        raise ValueError("derived_level must be Y3 or Y4")
    parent_norm = normalize_sqlish(parent_payload)
    roundtrip = normalized == parent_norm or normalize_sqlish(decoded) == parent_norm
    parent_valid = static_validate(parent_norm).final_accept
    child_contract = {"module_id": derived_level, "transform_recipe_id": recipe_id}
    child_valid = static_validate(derived, child_contract).final_accept
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
    recipes = list(Y3_RECIPES if derived_level == "Y3" else Y4_RECIPES)
    rows = []
    for i, payload in enumerate(parent_payloads):
        for j in range(per_parent):
            rid = recipes[(i + j) % len(recipes)]
            r = render_one(payload, derived_level, rid)
            rows.append({**r.__dict__, "parent_index": i})
    return rows
