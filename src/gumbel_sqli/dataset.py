from __future__ import annotations

from collections import defaultdict
from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd

from .config import ProjectConfig, ensure_parquet_engine
from .taxonomy import build_candidate_rows


PAYLOAD_COLUMNS = [
    "payload_norm",
    "payload",
    "query",
    "sentence",
    "Sentence",
    "Query",
    "text",
    "request",
]

SQLI_COLUMNS = ["is_sqli", "label", "Label", "class", "Class"]
TYPE_COLUMNS = ["sqli_type", "script_sqli_type", "attack_type", "type"]
DB_COLUMNS = ["db_engine", "db_hint", "database", "dialect"]
CONF_COLUMNS = ["confidence", "script_confidence", "label_confidence"]

KNOWN_DB_ENGINES = {
    "mysql",
    "postgres",
    "postgresql",
    "oracle",
    "mssql",
    "sqlserver",
    "sqlite",
    "mariadb",
}


def _first_column(columns: Iterable[str], candidates: list[str]) -> str | None:
    lower = {column.lower(): column for column in columns}
    for candidate in candidates:
        if candidate in columns:
            return candidate
        if candidate.lower() in lower:
            return lower[candidate.lower()]
    return None


def normalize_db_hint(value: object) -> str:
    raw = str(value or "").strip().lower()
    if raw in {"", "nan", "none", "null", "unknown"}:
        return "unlabeled_db_hint"
    if raw == "postgresql":
        return "postgres"
    if raw == "sqlserver":
        return "mssql"
    if raw in KNOWN_DB_ENGINES:
        return raw
    return "other_db_hint"


def normalize_bool_label(value: object) -> int:
    raw = str(value).strip().lower()
    if raw in {"1", "true", "yes", "sqli", "sql injection", "attack", "malicious"}:
        return 1
    if raw in {"0", "false", "no", "benign", "normal", "non-sqli", "safe"}:
        return 0
    try:
        return int(float(raw) > 0)
    except ValueError:
        return 1


def _read_csv_sample(path: Path, max_rows: int) -> pd.DataFrame:
    try:
        return pd.read_csv(path, nrows=max_rows, low_memory=False)
    except UnicodeDecodeError:
        return pd.read_csv(path, nrows=max_rows, low_memory=False, encoding="latin1")


def is_lfs_pointer(path: Path) -> bool:
    if not path.exists() or path.is_dir() or path.stat().st_size > 1024:
        return False
    try:
        first_line = path.read_text(encoding="utf-8", errors="ignore").splitlines()[0]
    except (IndexError, OSError):
        return False
    return first_line.strip() == "version https://git-lfs.github.com/spec/v1"


def _read_any(path: Path, max_rows: int) -> pd.DataFrame:
    suffix = path.suffix.lower()
    if is_lfs_pointer(path):
        raise RuntimeError(f"{path} is a Git LFS pointer; run `git lfs pull` first.")
    if suffix == ".parquet":
        return pd.read_parquet(path).head(max_rows)
    if suffix == ".txt":
        rows = []
        with path.open("r", encoding="utf-8", errors="ignore") as handle:
            for line in handle:
                payload = line.strip()
                if payload:
                    rows.append({"payload_norm": payload, "is_sqli": 1})
                if len(rows) >= max_rows:
                    break
        return pd.DataFrame(rows)
    return _read_csv_sample(path, max_rows)


def normalize_payload_frame(df: pd.DataFrame, source_path: Path) -> pd.DataFrame:
    payload_col = _first_column(df.columns, PAYLOAD_COLUMNS)
    if payload_col is None:
        return pd.DataFrame()

    is_sqli_col = _first_column(df.columns, SQLI_COLUMNS)
    type_col = _first_column(df.columns, TYPE_COLUMNS)
    db_col = _first_column(df.columns, DB_COLUMNS)
    conf_col = _first_column(df.columns, CONF_COLUMNS)

    out = pd.DataFrame()
    out["payload_norm"] = df[payload_col].astype(str).str.strip()
    out = out[out["payload_norm"].ne("") & out["payload_norm"].ne("nan")].copy()
    if out.empty:
        return out

    if is_sqli_col is not None:
        out["is_sqli"] = df.loc[out.index, is_sqli_col].map(normalize_bool_label).astype(int)
    else:
        out["is_sqli"] = 1

    if type_col is not None:
        out["technique_primary"] = (
            df.loc[out.index, type_col]
            .fillna("unlabeled_technique")
            .astype(str)
            .str.split("|")
            .str[0]
            .str.strip()
            .replace({"": "unlabeled_technique", "nan": "unlabeled_technique"})
        )
    else:
        out["technique_primary"] = "unlabeled_technique"

    if db_col is not None:
        out["db_hint"] = df.loc[out.index, db_col].map(normalize_db_hint)
    else:
        out["db_hint"] = "unlabeled_db_hint"

    if conf_col is not None:
        out["label_confidence"] = pd.to_numeric(
            df.loc[out.index, conf_col], errors="coerce"
        ).fillna(0.0)
    else:
        out["label_confidence"] = 0.0

    out["source_path"] = str(source_path)
    out["payload_length"] = out["payload_norm"].str.len()
    out["payload_length_bucket"] = pd.cut(
        out["payload_length"],
        bins=[-1, 40, 80, 160, 320, 10_000],
        labels=["0_40", "41_80", "81_160", "161_320", "321_plus"],
    ).astype(str)
    return out.reset_index(drop=True)


def load_payloads(
    config: ProjectConfig,
    input_paths: list[Path] | None = None,
    max_rows: int = 50_000,
    sqli_only: bool = False,
) -> pd.DataFrame:
    paths = input_paths or config.default_input_paths
    frames = []
    remaining = max_rows
    for path in paths:
        if remaining <= 0:
            break
        if not path.exists() or path.is_dir():
            continue
        try:
            raw = _read_any(path, remaining)
            normalized = normalize_payload_frame(raw, path)
        except Exception:
            continue
        if normalized.empty:
            continue
        frames.append(normalized)
        remaining -= len(normalized)

    if not frames:
        raise FileNotFoundError(
            "No payload rows could be loaded from configured inputs under "
            f"{config.label_data_dir}."
        )

    data = pd.concat(frames, ignore_index=True)
    data = data.drop_duplicates(subset=["payload_norm"]).reset_index(drop=True)
    if sqli_only:
        data = data[data["is_sqli"].eq(1)].reset_index(drop=True)
    return data.head(max_rows)


def build_action_candidate_table(
    payloads: pd.DataFrame,
    seed: int = 0,
) -> pd.DataFrame:
    rows = []
    for idx, record in payloads.reset_index(drop=True).iterrows():
        for row in build_candidate_rows(record["payload_norm"], seed=seed + idx):
            row.update(
                {
                    "is_sqli": int(record.get("is_sqli", 1)),
                    "technique_primary": record.get(
                        "technique_primary", "unlabeled_technique"
                    ),
                    "db_hint": record.get("db_hint", "unlabeled_db_hint"),
                    "label_confidence": float(record.get("label_confidence", 0.0)),
                    "source_path": record.get("source_path", ""),
                    "payload_length": int(record.get("payload_length", len(row["payload_norm"]))),
                    "payload_length_bucket": record.get("payload_length_bucket", "unknown"),
                }
            )
            row["round_trip_success"] = row["round_trip_payload"] == row["payload_norm"]
            rows.append(row)
    return pd.DataFrame(rows)


def write_parquet(df: pd.DataFrame, path: Path) -> None:
    ensure_parquet_engine()
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_parquet(path, index=False)


def read_parquet(path: Path) -> pd.DataFrame:
    ensure_parquet_engine()
    return pd.read_parquet(path)


def stratified_slice_split(
    candidates: pd.DataFrame,
    train_size: int = 5_000,
    dev_size: int = 1_000,
    test_size: int = 1_000,
    seed: int = 1729,
) -> dict[str, pd.DataFrame]:
    if candidates.empty:
        raise ValueError("Cannot split an empty candidate table.")

    usable = candidates[candidates["is_sqli"].eq(1)].copy()
    if usable.empty:
        usable = candidates.copy()
    usable = usable[usable["action_type"].ne("identity")].copy()
    if usable.empty:
        usable = candidates.copy()

    rng = np.random.default_rng(seed)
    usable["_stratum"] = (
        usable["action_family"].astype(str)
        + "|"
        + usable["technique_primary"].astype(str)
        + "|"
        + usable["db_hint"].astype(str)
    )
    groups = defaultdict(list)
    for idx, stratum in enumerate(usable["_stratum"]):
        groups[stratum].append(idx)

    ordered_indices: list[int] = []
    group_keys = sorted(groups, key=lambda key: len(groups[key]), reverse=True)
    group_positions = {key: 0 for key in group_keys}
    for key in group_keys:
        rng.shuffle(groups[key])

    while len(ordered_indices) < len(usable):
        progressed = False
        for key in group_keys:
            pos = group_positions[key]
            if pos < len(groups[key]):
                ordered_indices.append(groups[key][pos])
                group_positions[key] += 1
                progressed = True
        if not progressed:
            break

    ordered = usable.iloc[ordered_indices].drop(columns=["_stratum"]).reset_index(drop=True)
    total = min(len(ordered), train_size + dev_size + test_size)
    if total < 3:
        raise ValueError("Need at least three action candidates to create train/dev/test.")

    train_end = min(train_size, max(1, total - 2))
    dev_end = min(train_end + dev_size, max(train_end + 1, total - 1))
    return {
        "train": ordered.iloc[:train_end].reset_index(drop=True),
        "dev": ordered.iloc[train_end:dev_end].reset_index(drop=True),
        "test": ordered.iloc[dev_end:total].reset_index(drop=True),
    }


def write_slice_splits(splits: dict[str, pd.DataFrame], config: ProjectConfig) -> None:
    for split, df in splits.items():
        write_parquet(df, config.slice_dir / f"action_surgery_{split}.parquet")
