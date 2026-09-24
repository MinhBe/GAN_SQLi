from __future__ import annotations

import json
import re
from dataclasses import dataclass
from typing import Any, Mapping, Sequence
from urllib.parse import unquote

BOOLEAN_TOKENS = {
    "AND", "OR", "NOT", "IN", "LIKE", "ILIKE", "BETWEEN", "IS", "NULL",
    "TRUE", "FALSE", "ANY", "ALL", "EXISTS", "SIMILAR", "TO", "DISTINCT", "FROM",
    "=", "<>", "!=", ">", "<", ">=", "<=",
}
READONLY_SQL_TOKENS = {"SELECT", "FROM", "WHERE", "EXISTS"}
FORBIDDEN_EFFECT_TOKENS = {
    "INSERT", "UPDATE", "DELETE", "DROP", "ALTER", "COPY", "CREATE", "TRUNCATE",
    "EXEC", "EXECUTE", "CALL", "DO", "GRANT", "REVOKE", "PG_SLEEP",
}
KEYWORD_RE = re.compile(r"[A-Za-z_]+|<>|!=|>=|<=|=|>|<|\(|\)|,|\+|-|\*|/")
STRING_RE = re.compile(r"'(?:''|[^'])*'")
NUMBER_RE = re.compile(r"\b\d+(?:\.\d+)?\b")
COMMENT_RE = re.compile(r"/\*.*?\*/|--.*?$", re.S | re.M)
PERCENT_RE = re.compile(r"%[0-9a-fA-F]{2}")


@dataclass(frozen=True)
class StaticValidation:
    payload: str
    validation_view: str
    delimiter_valid: bool
    quote_valid: bool
    boolean_signal_valid: bool
    required_tokens_valid: bool
    skeleton_valid: bool
    representation_valid: bool
    safe_scope_valid: bool
    slot_sanity_valid: bool
    static_score: float
    final_accept: bool
    error_class: str


def _field(contract: Mapping[str, Any] | None, *names: str, default: Any = None) -> Any:
    if not contract:
        return default
    for name in names:
        if name in contract and contract[name] not in (None, "", "nan"):
            return contract[name]
    return default


def parse_required_tokens(value: Any) -> list[str]:
    if value is None or value == "" or str(value).lower() == "nan":
        return []
    if isinstance(value, (list, tuple, set)):
        raw = list(value)
    else:
        text = str(value).strip()
        try:
            parsed = json.loads(text)
            raw = parsed if isinstance(parsed, list) else [parsed]
        except Exception:
            raw = re.split(r"[,|;]+|\s+", text)
    return [str(x).strip().upper() for x in raw if str(x).strip()]


def strip_string_literals(sql: str) -> str:
    return STRING_RE.sub("'<STR>'", sql)


def normalize_sqlish(sql: str, *, comments_as_space: bool = True) -> str:
    s = str(sql or "")
    if comments_as_space:
        s = COMMENT_RE.sub(" ", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s


def validation_surface(payload: str, contract: Mapping[str, Any] | None = None, view: str = "auto") -> tuple[str, str]:
    raw = str(payload or "")
    module = str(_field(contract, "module_id", "y_level", "parent_module_level", default="")).upper()
    recipe = str(_field(contract, "transform_recipe_id", "representation_recipe", "recipe_id", default="")).upper()
    if view == "raw":
        return raw, "raw"
    if view == "decoded" or module.startswith("Y3") or recipe.startswith("T_Y3") or PERCENT_RE.search(raw):
        return unquote(raw), "decoded"
    if view == "normalized" or module.startswith("Y4") or recipe.startswith("T_Y4"):
        return normalize_sqlish(raw), "normalized"
    return raw, "raw"


def tokens(sql: str) -> list[str]:
    return [t.upper() for t in KEYWORD_RE.findall(strip_string_literals(sql))]


def balanced_parentheses(sql: str) -> bool:
    depth = 0
    in_str = False
    i = 0
    while i < len(sql):
        ch = sql[i]
        if ch == "'":
            if in_str and i + 1 < len(sql) and sql[i + 1] == "'":
                i += 2
                continue
            in_str = not in_str
        elif not in_str:
            if ch == "(":
                depth += 1
            elif ch == ")":
                depth -= 1
                if depth < 0:
                    return False
        i += 1
    return depth == 0 and not in_str


def quote_valid(sql: str) -> bool:
    in_str = False
    i = 0
    while i < len(sql):
        if sql[i] == "'":
            if in_str and i + 1 < len(sql) and sql[i + 1] == "'":
                i += 2
                continue
            in_str = not in_str
        i += 1
    return not in_str


def token_signature(sql: str) -> str:
    s = normalize_sqlish(strip_string_literals(sql)).upper()
    s = NUMBER_RE.sub("<NUM>", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def boolean_signal_valid(sql: str) -> bool:
    tt = set(tokens(sql))
    predicate_markers = BOOLEAN_TOKENS - {"AND", "OR", "NOT"}
    return bool(tt & predicate_markers)


def required_tokens_valid(sql: str, required: Any, *, strict: bool = False) -> bool:
    req = parse_required_tokens(required)
    if not req:
        return not strict
    tt = set(tokens(sql))
    upper = sql.upper()
    return all(x in tt or x in upper for x in req)


def skeleton_valid(sql: str, contract: Mapping[str, Any] | None, *, min_overlap: float = 0.70) -> bool:
    if not contract:
        return True
    expected = _field(contract, "skeleton", "skeleton_signature", "structure_signature", default="")
    if not expected:
        return True
    a = set(tokens(token_signature(sql)))
    b = set(tokens(token_signature(str(expected))))
    if not b:
        return True
    return len(a & b) / max(len(b), 1) >= min_overlap


def representation_valid(raw: str, surface: str, contract: Mapping[str, Any] | None) -> bool:
    module = str(_field(contract, "module_id", "y_level", "derived_level", default="")).upper()
    recipe = str(_field(contract, "transform_recipe_id", "representation_recipe", "recipe_id", default="")).upper()
    if module.startswith("Y3") or recipe.startswith("T_Y3"):
        return bool(PERCENT_RE.search(raw)) and unquote(raw) != raw
    if module.startswith("Y4") or recipe.startswith("T_Y4"):
        return COMMENT_RE.search(raw) is not None or bool(re.search(r"\s{2,}|\t", raw)) or raw != raw.upper()
    return True


def safe_scope_valid(sql: str, *, allow_readonly_select: bool = True) -> bool:
    tt = set(tokens(sql))
    if tt & FORBIDDEN_EFFECT_TOKENS:
        return False
    if not allow_readonly_select and (tt & READONLY_SQL_TOKENS):
        return False
    if ";" in sql:
        return False
    return True


def slot_sanity_valid(sql: str, *, max_digits: int = 9, max_length: int = 512) -> bool:
    if len(sql) > max_length:
        return False
    return all(len(x.replace(".", "")) <= max_digits for x in NUMBER_RE.findall(sql))


def static_validate(
    payload: str,
    contract: Mapping[str, Any] | None = None,
    *,
    strict_required: bool = False,
    allow_readonly_select: bool = True,
    view: str = "auto",
) -> StaticValidation:
    raw = str(payload or "")
    sql, view_name = validation_surface(raw, contract, view=view)
    required = _field(contract, "required_tokens", "required_token", "token_contract", default=None)
    checks = {
        "delimiter": balanced_parentheses(sql),
        "quote": quote_valid(sql),
        "boolean": boolean_signal_valid(sql),
        "required": required_tokens_valid(sql, required, strict=strict_required),
        "skeleton": skeleton_valid(sql, contract),
        "representation": representation_valid(raw, sql, contract),
        "scope": safe_scope_valid(sql, allow_readonly_select=allow_readonly_select),
        "slot": slot_sanity_valid(sql),
    }
    weights = {
        "delimiter": 0.16,
        "quote": 0.10,
        "boolean": 0.16,
        "required": 0.18,
        "skeleton": 0.12,
        "representation": 0.10,
        "scope": 0.10,
        "slot": 0.08,
    }
    score = sum(weights[k] for k, ok in checks.items() if ok)
    final = score >= 0.82 and checks["delimiter"] and checks["quote"] and checks["boolean"] and checks["scope"]
    if strict_required:
        final = final and checks["required"]
    error = "ok" if final else "+".join(k for k, ok in checks.items() if not ok) or "low_score"
    return StaticValidation(
        payload=raw,
        validation_view=view_name,
        delimiter_valid=checks["delimiter"],
        quote_valid=checks["quote"],
        boolean_signal_valid=checks["boolean"],
        required_tokens_valid=checks["required"],
        skeleton_valid=checks["skeleton"],
        representation_valid=checks["representation"],
        safe_scope_valid=checks["scope"],
        slot_sanity_valid=checks["slot"],
        static_score=round(float(score), 4),
        final_accept=bool(final),
        error_class=error,
    )
