from pathlib import Path

import pandas as pd

from gumbel_sqli.audit import run_audit
from gumbel_sqli.config import ProjectConfig
from gumbel_sqli.dataset import read_parquet
from gumbel_sqli.full_foundation import build_condition_table, build_full_foundation
from gumbel_sqli.slice_builder import build_slice


def _sample_csv(path: Path) -> None:
    rows = [
        {
            "payload_norm": "select 1 where 1=1 and name='a' -- x",
            "is_sqli": 1,
            "sqli_type": "boolean_blind",
            "db_engine": "mysql",
            "confidence": 0.95,
        },
        {
            "payload_norm": "UNION SELECT char(65),version() FROM users WHERE id=1",
            "is_sqli": 1,
            "sqli_type": "union_based",
            "db_engine": "mysql",
            "confidence": 0.95,
        },
        {
            "payload_norm": "or pg_sleep(5) and 'x'='x'",
            "is_sqli": 1,
            "sqli_type": "time_blind",
            "db_engine": "postgres",
            "confidence": 0.95,
        },
        {
            "payload_norm": "name=admin",
            "is_sqli": 0,
            "sqli_type": "",
            "db_engine": "unknown",
            "confidence": 0.0,
        },
    ]
    pd.DataFrame(rows).to_csv(path, index=False)


def test_audit_outputs_required_artifacts(tmp_path):
    source = tmp_path / "sample.csv"
    _sample_csv(source)
    config = ProjectConfig.from_args(root=tmp_path, seed=7, device="cpu")

    decision = run_audit(config, input_paths=[source], max_rows=20)

    assert decision["decision"] in {"S1_MASKED_SLOT", "S2_TAMPER_ACTION", "STOP"}
    assert (tmp_path / "reports" / "gumbel" / "01_slot_action_audit.md").exists()
    assert (tmp_path / "data" / "gumbel" / "audit" / "action_taxonomy.json").exists()
    assert (tmp_path / "data" / "gumbel" / "audit" / "action_candidates.parquet").exists()
    assert (tmp_path / "data" / "gumbel" / "audit" / "g0_decision.json").exists()


def test_build_slice_outputs_non_empty_splits(tmp_path):
    source = tmp_path / "sample.csv"
    _sample_csv(source)
    config = ProjectConfig.from_args(root=tmp_path, seed=7, device="cpu")

    result = build_slice(
        config,
        input_paths=[source],
        max_rows=20,
        train_size=3,
        dev_size=2,
        test_size=2,
    )

    assert result["split_sizes"]["train"] > 0
    assert result["split_sizes"]["dev"] > 0
    assert result["split_sizes"]["test"] > 0
    train = read_parquet(tmp_path / "data" / "gumbel" / "slice" / "action_surgery_train.parquet")
    assert not train.empty


def test_build_full_and_conditions_outputs_gumbel_artifacts(tmp_path):
    source = tmp_path / "sample.csv"
    _sample_csv(source)
    config = ProjectConfig.from_args(root=tmp_path, seed=7, device="cpu")

    full = build_full_foundation(config, input_paths=[source], max_rows=20)
    conditions = build_condition_table(config)

    assert full["action_rows"] > 0
    assert conditions["condition_rows"] > 0
    assert (tmp_path / "data" / "gumbel" / "full" / "action_foundation.parquet").exists()
    assert (tmp_path / "data" / "gumbel" / "full" / "action_splits.json").exists()
    assert (tmp_path / "data" / "gumbel" / "full" / "condition_table.parquet").exists()
    condition_table = read_parquet(
        tmp_path / "data" / "gumbel" / "full" / "condition_table.parquet"
    )
    assert "unlabeled_db_hint" in set(condition_table["db_hint"])
    assert "unknown" not in set(condition_table["db_hint"])
