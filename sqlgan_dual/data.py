from __future__ import annotations

import json
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

MODULES = ["Y1_basic_boolean", "Y2_boolean_variation", "Y3_encoded_boolean", "Y4_obfuscated_boolean"]
CORE_MODULES = ["Y1_basic_boolean", "Y2_boolean_variation"]
DERIVED_MODULES = ["Y3_encoded_boolean", "Y4_obfuscated_boolean"]
PAYLOAD_COLUMNS = [
    "validation_payload_v4", "validation_payload", "payload_canonical", "payload_before_transform",
    "payload_decoded", "payload_normalized", "payload_raw", "payload", "raw_payload", "sql",
]
ACCEPT_COLUMNS = ["accepted_for_seqgan_v4", "accepted_for_seqgan", "static_accept", "final_accept", "accepted"]


@dataclass(frozen=True)
class DatasetPaths:
    root: Path
    dataset: Path
    generator: Path
    validation: Path
    metrics: Path
    rf_features: Path


def _looks_like_dataset_dir(path: Path) -> bool:
    return (path / "Dataset" / "A_generator_attack_corpus").exists() or (path / "A_generator_attack_corpus").exists()


def _find_dataset_root(path: Path) -> Path:
    if _looks_like_dataset_dir(path):
        return path
    candidates = []
    candidates.extend(p.parent for p in path.rglob("Dataset") if p.is_dir() and (p / "A_generator_attack_corpus").exists())
    candidates.extend(p.parent for p in path.rglob("A_generator_attack_corpus") if p.is_dir())
    if not candidates:
        raise FileNotFoundError(f"Cannot find Dataset/ or A_generator_attack_corpus/ below {path}")
    return sorted(set(candidates), key=lambda p: len(str(p)))[0]


def materialize_dataset(data: str | Path, work_dir: str | Path) -> DatasetPaths:
    data = Path(data)
    work_dir = Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    if data.is_file() and data.suffix.lower() == ".zip":
        out = work_dir / data.stem.replace(" ", "_")
        if not out.exists():
            out.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(data) as zf:
                zf.extractall(out)
        root = _find_dataset_root(out)
    elif data.is_dir():
        root = _find_dataset_root(data)
    else:
        raise FileNotFoundError(data)
    ds = root / "Dataset" if (root / "Dataset" / "A_generator_attack_corpus").exists() else root
    return DatasetPaths(root=root, dataset=ds, generator=ds / "A_generator_attack_corpus", validation=ds / "validation", metrics=ds / "metrics", rf_features=ds / "B_random_forest_feature_dataset")


def module_dir(paths: DatasetPaths, module_id: str) -> Path:
    p = paths.generator / module_id
    if not p.exists():
        raise FileNotFoundError(p)
    return p


def read_jsonl(path: str | Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with Path(path).open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def write_jsonl(rows: Iterable[dict[str, Any]], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def _accepted_mask(df: pd.DataFrame) -> pd.Series:
    for col in ACCEPT_COLUMNS:
        if col in df.columns:
            return df[col].fillna(0).astype(int).eq(1)
    return pd.Series([True] * len(df), index=df.index)


def _choose_payload(row: dict[str, Any], surface: str = "validation") -> str:
    if surface == "raw":
        cols = ["payload_raw", "payload", "raw_payload", "sql"] + PAYLOAD_COLUMNS
    elif surface == "canonical":
        cols = ["payload_canonical", "validation_payload", "validation_payload_v4", "payload_before_transform"] + PAYLOAD_COLUMNS
    else:
        cols = PAYLOAD_COLUMNS
    for col in cols:
        val = row.get(col)
        if val is not None and str(val) not in ("", "nan"):
            return str(val)
    return ""


def _metadata_path(mod: Path, accepted: bool = True) -> Path | None:
    names = ["seqgan_accepted_metadata.jsonl", "seqgan_attack_corpus.jsonl"] if accepted else ["seqgan_attack_corpus.jsonl", "seqgan_accepted_metadata.jsonl"]
    for name in names:
        p = mod / name
        if p.exists():
            return p
    return None


def load_payload_rows(paths: DatasetPaths, module_id: str, *, accepted_only: bool = True, surface: str = "validation") -> list[dict[str, Any]]:
    mod = module_dir(paths, module_id)
    meta = _metadata_path(mod, accepted=accepted_only)
    if meta:
        rows = read_jsonl(meta)
    else:
        csv = mod / "attack_samples.csv"
        if not csv.exists():
            raise FileNotFoundError(f"No metadata JSONL or attack_samples.csv in {mod}")
        df = pd.read_csv(csv)
        if accepted_only:
            df = df[_accepted_mask(df)].copy()
        rows = df.to_dict("records")
    out = []
    for i, row in enumerate(rows):
        r = dict(row)
        r.setdefault("module_id", module_id)
        r.setdefault("row_index", i)
        r["training_payload"] = _choose_payload(r, surface=surface)
        if r["training_payload"]:
            out.append(r)
    return out


def export_training_jsonl(paths: DatasetPaths, module_id: str, out_path: str | Path, *, accepted_only: bool = True, surface: str = "validation", unique: bool = True) -> dict[str, int | str]:
    rows = load_payload_rows(paths, module_id, accepted_only=accepted_only, surface=surface)
    seen = set()
    exported = []
    for row in rows:
        p = row["training_payload"]
        if unique and p in seen:
            continue
        seen.add(p)
        exported.append(row)
    write_jsonl(exported, out_path)
    return {"module_id": module_id, "input_rows": len(rows), "exported_rows": len(exported), "duplicates_removed": len(rows) - len(exported), "surface": surface}


def contract_from_row(row: dict[str, Any]) -> dict[str, Any]:
    keep = [
        "module_id", "y_level", "root_id", "root_grammar_id", "structure_cell_id", "cell_id",
        "semantic_family", "abstract_family_id", "required_tokens", "token_contract",
        "skeleton", "skeleton_signature", "structure_signature", "representation_recipe",
        "transform_recipe_id", "decode_requirement", "payload_canonical", "validation_payload",
        "validation_payload_v4", "training_payload",
    ]
    return {k: row[k] for k in keep if k in row and row[k] not in (None, "", "nan")}


def load_training_jsonl(path: str | Path, *, limit: int | None = None) -> tuple[list[str], list[dict[str, Any]]]:
    rows = read_jsonl(path)
    if limit:
        rows = rows[:limit]
    texts = [str(r.get("training_payload") or r.get("payload_raw") or r.get("payload") or "") for r in rows]
    contracts = [contract_from_row(r) for r in rows]
    return texts, contracts


def save_contracts(contracts: Iterable[dict[str, Any]], path: str | Path, *, max_contracts: int = 4096) -> None:
    unique = []
    seen = set()
    for c in contracts:
        key = json.dumps(c, sort_keys=True, ensure_ascii=False)
        if key in seen:
            continue
        seen.add(key)
        unique.append(c)
        if len(unique) >= max_contracts:
            break
    write_jsonl(unique, path)
