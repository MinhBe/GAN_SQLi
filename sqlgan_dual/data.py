from __future__ import annotations

import json
import shutil
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Optional

import pandas as pd

MODULES = [
    "Y1_basic_boolean",
    "Y2_boolean_variation",
    "Y3_encoded_boolean",
    "Y4_obfuscated_boolean",
]
CORE_MODULES = ["Y1_basic_boolean", "Y2_boolean_variation"]
DERIVED_MODULES = ["Y3_encoded_boolean", "Y4_obfuscated_boolean"]


@dataclass(frozen=True)
class DatasetPaths:
    root: Path
    dataset: Path
    generator: Path
    validation: Path
    metrics: Path
    rf_features: Path


def _looks_like_dataset_dir(path: Path) -> bool:
    """Return True for both supported layouts.

    Supported layouts:
    1. package root containing Dataset/A_generator_attack_corpus/...
    2. repository root containing A_generator_attack_corpus/... directly
       (current MinhBe/GAN_SQLi main layout).
    """
    return (
        (path / "Dataset" / "A_generator_attack_corpus").exists()
        or (path / "A_generator_attack_corpus").exists()
    )


def _find_dataset_root(path: Path) -> Path:
    """Find the dataset root, accepting both zipped Dataset/ layout and repo-root layout."""
    path = Path(path)
    if _looks_like_dataset_dir(path):
        return path
    candidates = []
    candidates.extend(p.parent for p in path.rglob("Dataset") if p.is_dir() and (p / "A_generator_attack_corpus").exists())
    candidates.extend(p.parent for p in path.rglob("A_generator_attack_corpus") if p.is_dir())
    if not candidates:
        raise FileNotFoundError(f"Cannot find Dataset/ or A_generator_attack_corpus/ below {path}")
    return sorted(set(candidates), key=lambda x: len(str(x)))[0]


def materialize_dataset(data: str | Path, work_dir: str | Path) -> DatasetPaths:
    """Extract a zip dataset if needed and return canonical paths.

    Parameters
    ----------
    data:
        Path to the V4.1 zip or an already-extracted dataset root.
    work_dir:
        Directory used for extraction. Existing contents are reused.
    """
    data = Path(data)
    work_dir = Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)

    if data.is_file() and data.suffix.lower() == ".zip":
        stamp = data.stem.replace(" ", "_")
        out = work_dir / stamp
        if not out.exists():
            out.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(data) as zf:
                zf.extractall(out)
        root = _find_dataset_root(out)
    elif data.is_dir():
        root = _find_dataset_root(data)
    else:
        raise FileNotFoundError(data)

    # V4.1 can be stored either as root/Dataset/... or directly as root/... in GitHub.
    ds = root / "Dataset" if (root / "Dataset" / "A_generator_attack_corpus").exists() else root
    return DatasetPaths(
        root=root,
        dataset=ds,
        generator=ds / "A_generator_attack_corpus",
        validation=ds / "validation",
        metrics=ds / "metrics",
        rf_features=ds / "B_random_forest_feature_dataset",
    )


def read_manifest(paths: DatasetPaths) -> dict:
    p = paths.dataset / "dataset_manifest.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def module_dir(paths: DatasetPaths, module_id: str) -> Path:
    p = paths.generator / module_id
    if not p.exists():
        raise FileNotFoundError(f"Missing module directory: {p}")
    return p


def load_module(paths: DatasetPaths, module_id: str, accepted_only: bool = False) -> pd.DataFrame:
    df = pd.read_csv(module_dir(paths, module_id) / "attack_samples.csv")
    if accepted_only and "accepted_for_seqgan_v4" in df.columns:
        df = df[df["accepted_for_seqgan_v4"].astype(int) == 1].copy()
    return df


def load_all_modules(paths: DatasetPaths, accepted_only: bool = False) -> Dict[str, pd.DataFrame]:
    return {m: load_module(paths, m, accepted_only=accepted_only) for m in MODULES}


def load_corpus(paths: DatasetPaths, module_id: str, accepted: bool = True) -> List[str]:
    fname = "seqgan_accepted_corpus.txt" if accepted else "seqgan_attack_corpus.txt"
    p = module_dir(paths, module_id) / fname
    if not p.exists():
        raise FileNotFoundError(p)
    return [line.rstrip("\n") for line in p.read_text(encoding="utf-8").splitlines() if line.strip()]


def load_metadata_jsonl(paths: DatasetPaths, module_id: str, accepted: bool = True) -> list[dict]:
    fname = "seqgan_accepted_metadata.jsonl" if accepted else "seqgan_attack_corpus.jsonl"
    p = module_dir(paths, module_id) / fname
    if not p.exists():
        raise FileNotFoundError(p)
    rows = []
    with p.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return rows


def load_transform_recipes(paths: DatasetPaths) -> pd.DataFrame:
    p = paths.generator / "transform_recipes.csv"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)


def load_transform_lineage(paths: DatasetPaths) -> pd.DataFrame:
    p = paths.generator / "transform_lineage_y3_y4.csv"
    if not p.exists():
        return pd.DataFrame()
    return pd.read_csv(p)


def export_lines(lines: Iterable[str], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def export_jsonl(rows: Iterable[dict], path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as fh:
        for row in rows:
            fh.write(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n")


def build_unique_corpus_file(paths: DatasetPaths, module_id: str, out_path: str | Path) -> dict:
    """Export de-duplicated accepted payloads while preserving order."""
    lines = load_corpus(paths, module_id, accepted=True)
    seen = set()
    unique = []
    for x in lines:
        if x not in seen:
            seen.add(x)
            unique.append(x)
    export_lines(unique, out_path)
    return {"module_id": module_id, "input": len(lines), "unique": len(unique), "duplicates": len(lines) - len(unique)}
