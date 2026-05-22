from __future__ import annotations

from collections import Counter
from dataclasses import asdict, dataclass, field
import json
import math
from pathlib import Path
import re
import sqlite3
from difflib import SequenceMatcher
from typing import Any, Iterable

import numpy as np
import pandas as pd
import sqlparse

from .taxonomy import candidate_action_types, reconstruct_payload


@dataclass(frozen=True)
class EvaluatorConfig:
    floors: dict[str, float] = field(
        default_factory=lambda: {
            "round_trip_success": 0.95,
            "parse_success": 0.70,
            "action_validity": 0.70,
            "unique_ratio": 0.10,
            "near_copy_rate": 0.95,
        }
    )
    weights: dict[str, float] = field(
        default_factory=lambda: {
            "round_trip_success": 0.20,
            "parse_success": 0.20,
            "action_validity": 0.15,
            "unique_ratio": 0.15,
            "self_bleu3_diversity": 0.10,
            "template_entropy_norm": 0.10,
            "action_entropy_norm": 0.10,
        }
    )
    near_copy_threshold: float = 0.92

    def to_json(self) -> dict[str, Any]:
        return asdict(self)

    def write(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(self.to_json(), indent=2), encoding="utf-8")


def balanced_parentheses(payload: str) -> bool:
    text = str(payload or "")
    depth = 0
    for char in text:
        if char == "(":
            depth += 1
        elif char == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def balanced_quotes_and_parens(payload: str) -> bool:
    text = str(payload or "")
    if text.count("'") % 2 != 0:
        return False
    if text.count('"') % 2 != 0:
        return False
    return balanced_parentheses(text)


def parse_success(payload: str) -> bool:
    text = str(payload or "").strip()
    if not text:
        return False
    starts_as_statement = re.match(
        r"^(select|insert|update|delete|create|drop|alter|with)\b", text, re.I
    )
    has_sql_marker = re.search(
        r"\b(select|union|from|where|and|or|sleep|benchmark|like)\b|=|--|/\*|%[0-9A-Fa-f]{2}",
        text,
        re.I,
    )
    if starts_as_statement and not balanced_parentheses(text):
        return False
    if not starts_as_statement and not has_sql_marker:
        return False
    try:
        parsed = sqlparse.parse(text)
    except Exception:
        return False
    return bool(parsed)


def sqlite_execution_safety(payload: str) -> bool:
    text = str(payload or "").strip()
    if not text or ";" in text:
        return False
    if re.search(r"\b(drop|delete|update|insert|alter|create|attach|pragma)\b", text, re.I):
        return False
    if not balanced_quotes_and_parens(text):
        return False
    expression = text
    expression = re.sub(r"--.*$", "", expression).strip()
    if re.search(r"\b(select|union|from|where)\b", expression, re.I):
        return parse_success(expression)
    try:
        conn = sqlite3.connect(":memory:")
        conn.execute("EXPLAIN QUERY PLAN SELECT 1 WHERE " + expression)
        conn.close()
        return True
    except Exception:
        return False


def _tokens(text: str) -> list[str]:
    return re.findall(r"[A-Za-z_]+|\d+|[^\sA-Za-z_\d]", str(text).lower())


def _ngrams(tokens: list[str], n: int) -> Counter[tuple[str, ...]]:
    return Counter(tuple(tokens[idx : idx + n]) for idx in range(max(0, len(tokens) - n + 1)))


def bleu3(candidate: str, reference: str) -> float:
    cand_tokens = _tokens(candidate)
    ref_tokens = _tokens(reference)
    if not cand_tokens or not ref_tokens:
        return 0.0
    scores = []
    for n in (1, 2, 3):
        cand = _ngrams(cand_tokens, n)
        ref = _ngrams(ref_tokens, n)
        total = sum(cand.values())
        if total == 0:
            scores.append(0.0)
            continue
        overlap = sum(min(count, ref[gram]) for gram, count in cand.items())
        scores.append((overlap + 1.0) / (total + 1.0))
    return float(math.exp(sum(math.log(max(score, 1e-9)) for score in scores) / 3.0))


def self_bleu3(payloads: list[str], sample_limit: int = 200) -> float:
    if len(payloads) <= 1:
        return 0.0
    sample = payloads[:sample_limit]
    values = []
    for idx, payload in enumerate(sample):
        refs = sample[:idx] + sample[idx + 1 :]
        if refs:
            values.append(max(bleu3(payload, ref) for ref in refs))
    return float(np.mean(values)) if values else 0.0


def entropy(values: Iterable[Any]) -> float:
    counts = Counter(str(value) for value in values if str(value) != "")
    total = sum(counts.values())
    if total == 0:
        return 0.0
    return float(-sum((count / total) * math.log2(count / total) for count in counts.values()))


def normalized_entropy(values: Iterable[Any]) -> float:
    values = list(values)
    unique = len(set(values))
    if unique <= 1:
        return 0.0
    return entropy(values) / math.log2(unique)


def near_copy_rate(payloads: list[str], references: list[str], threshold: float) -> float:
    if not payloads or not references:
        return 0.0
    exact_refs = set(references)
    refs_by_len = sorted((len(ref), ref) for ref in references[:1_000])
    near = 0
    for payload in payloads:
        if payload in exact_refs:
            near += 1
            continue
        length = len(payload)
        candidates = [
            ref
            for ref_len, ref in refs_by_len
            if abs(ref_len - length) <= max(12, int(length * 0.35))
        ][:80]
        if any(
            SequenceMatcher(None, payload, ref).quick_ratio() >= threshold
            and SequenceMatcher(None, payload, ref).ratio() >= threshold
            for ref in candidates
        ):
            near += 1
    return near / len(payloads)


def choose_payload_column(df: pd.DataFrame) -> str:
    for column in ("generated_payload", "mutated_payload", "payload_norm", "payload"):
        if column in df.columns:
            return column
    raise ValueError("No payload column found for evaluation.")


def action_validity_row(row: pd.Series) -> bool:
    action_type = str(row.get("action_type", "identity"))
    if action_type == "identity":
        return True
    payload = str(row.get("payload_norm", row.get("generated_payload", "")))
    return action_type in candidate_action_types(payload)


def round_trip_row(row: pd.Series) -> bool:
    if "round_trip_success" in row:
        return bool(row["round_trip_success"])
    if {"template", "slots_json", "payload_norm"}.issubset(row.index):
        try:
            return reconstruct_payload(row["template"], row["slots_json"]) == row["payload_norm"]
        except Exception:
            return False
    return True


def condition_accuracy(df: pd.DataFrame) -> float:
    checks = []
    for expected, actual in [
        ("db_hint", "generated_db_hint"),
        ("technique_primary", "generated_technique_primary"),
        ("action_family", "generated_action_family"),
    ]:
        if expected in df.columns and actual in df.columns:
            checks.append((df[expected].astype(str) == df[actual].astype(str)).mean())
    if not checks:
        return 1.0
    return float(np.mean(checks))


def d_shortcut_diagnostic(df: pd.DataFrame) -> dict[str, Any]:
    if "d_score" not in df.columns:
        return {"status": "not_run", "length_score_abs_corr": None}
    scores = pd.to_numeric(df["d_score"], errors="coerce").fillna(0.0)
    lengths = df[choose_payload_column(df)].astype(str).str.len()
    if scores.nunique() <= 1 or lengths.nunique() <= 1:
        corr = 0.0
    else:
        corr = float(np.corrcoef(scores, lengths)[0, 1])
    return {
        "status": "pass" if abs(corr) < 0.50 else "warn",
        "length_score_abs_corr": abs(corr),
    }


def composite_score(metrics: dict[str, Any], config: EvaluatorConfig | None = None) -> dict[str, Any]:
    cfg = config or EvaluatorConfig()
    floor_failures = {}
    for metric, floor in cfg.floors.items():
        if metric == "near_copy_rate":
            ok = float(metrics.get(metric, 1.0)) <= floor
        else:
            ok = float(metrics.get(metric, 0.0)) >= floor
        if not ok:
            floor_failures[metric] = {
                "observed": float(metrics.get(metric, 0.0)),
                "floor": floor,
            }

    if floor_failures:
        return {"passed_floors": False, "score": 0.0, "floor_failures": floor_failures}

    score = 0.0
    for metric, weight in cfg.weights.items():
        source = metric
        if metric == "self_bleu3_diversity":
            value = 1.0 - float(metrics.get("self_bleu3", 1.0))
        else:
            value = float(metrics.get(source, 0.0))
        score += weight * max(0.0, min(1.0, value))
    return {"passed_floors": True, "score": float(score), "floor_failures": {}}


def evaluate_dataframe(
    df: pd.DataFrame,
    references: list[str] | None = None,
    config: EvaluatorConfig | None = None,
) -> dict[str, Any]:
    cfg = config or EvaluatorConfig()
    if df.empty:
        metrics = {
            "n": 0,
            "round_trip_success": 0.0,
            "parse_success": 0.0,
            "sqlite_execution_safety": 0.0,
            "action_validity": 0.0,
            "unique_ratio": 0.0,
            "self_bleu3": 1.0,
            "template_entropy": 0.0,
            "template_entropy_norm": 0.0,
            "action_entropy": 0.0,
            "action_entropy_norm": 0.0,
            "near_copy_rate": 1.0,
            "condition_accuracy": 0.0,
            "d_shortcut_diagnostic": {"status": "not_run"},
        }
        metrics["composite"] = composite_score(metrics, cfg)
        return metrics

    payload_column = choose_payload_column(df)
    payloads = df[payload_column].fillna("").astype(str).tolist()
    references = references if references is not None else df.get("payload_norm", pd.Series(payloads)).astype(str).tolist()

    metrics = {
        "n": int(len(df)),
        "round_trip_success": float(np.mean([round_trip_row(row) for _, row in df.iterrows()])),
        "parse_success": float(np.mean([parse_success(payload) for payload in payloads])),
        "sqlite_execution_safety": float(
            np.mean([sqlite_execution_safety(payload) for payload in payloads])
        ),
        "action_validity": float(np.mean([action_validity_row(row) for _, row in df.iterrows()])),
        "unique_ratio": float(len(set(payloads)) / len(payloads)),
        "self_bleu3": self_bleu3(payloads),
        "template_entropy": entropy(df.get("template", pd.Series([""] * len(df))).tolist()),
        "template_entropy_norm": normalized_entropy(
            df.get("template", pd.Series([""] * len(df))).tolist()
        ),
        "action_entropy": entropy(df.get("action_type", pd.Series([""] * len(df))).tolist()),
        "action_entropy_norm": normalized_entropy(
            df.get("action_type", pd.Series([""] * len(df))).tolist()
        ),
        "near_copy_rate": near_copy_rate(payloads, references or [], cfg.near_copy_threshold),
        "condition_accuracy": condition_accuracy(df),
        "d_shortcut_diagnostic": d_shortcut_diagnostic(df),
    }
    metrics["composite"] = composite_score(metrics, cfg)
    return metrics
