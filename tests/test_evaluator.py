import pandas as pd

from gumbel_sqli.evaluator import (
    EvaluatorConfig,
    composite_score,
    evaluate_dataframe,
    parse_success,
)
from gumbel_sqli.taxonomy import build_candidate_rows


def test_parse_success_distinguishes_broken_payload():
    assert parse_success("select 1 where 1=1")
    assert not parse_success("select (1")


def test_composite_cannot_compensate_for_failed_floor():
    metrics = {
        "round_trip_success": 1.0,
        "parse_success": 0.1,
        "action_validity": 1.0,
        "unique_ratio": 1.0,
        "near_copy_rate": 0.0,
        "self_bleu3": 0.0,
        "template_entropy_norm": 1.0,
        "action_entropy_norm": 1.0,
    }
    result = composite_score(metrics, EvaluatorConfig())
    assert not result["passed_floors"]
    assert result["score"] == 0.0
    assert "parse_success" in result["floor_failures"]


def test_evaluator_known_valid_candidates():
    rows = build_candidate_rows("select 1 where 1=1 and name='a'")
    df = pd.DataFrame(rows)
    metrics = evaluate_dataframe(df, references=["select 1 where 1=1 and name='a'"])
    assert metrics["round_trip_success"] == 1.0
    assert metrics["action_validity"] >= 0.5
    assert metrics["n"] == len(df)
