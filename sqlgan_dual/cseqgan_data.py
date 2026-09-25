from __future__ import annotations

import json
import re
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import pandas as pd

CORE_MODULES = ["Y1_basic_boolean", "Y2_boolean_variation"]
PREFIX_RE = re.compile(r"^(?P<prefix><RULE=[^>]+><CELL=[^>]+><FAMILY=[^>]+>)\s*(?P<payload>.*)$", re.S)


@dataclass(frozen=True)
class CSeqGANPaths:
    root: Path
    dataset: Path
    contracts_dir: Path
    training_dir: Path
    candidates_dir: Path
    rendered_dir: Path
    metrics_dir: Path


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


def _looks_like_v5_dataset(path: Path) -> bool:
    ds = path / "Dataset"
    return (
        (ds / "A_ruleset_contracts" / "ruleset_contracts.csv").exists()
        and (ds / "B_conditioned_seqgan_training").exists()
    ) or (
        (path / "A_ruleset_contracts" / "ruleset_contracts.csv").exists()
        and (path / "B_conditioned_seqgan_training").exists()
    )


def _find_v5_root(path: Path) -> Path:
    if _looks_like_v5_dataset(path):
        return path
    candidates = []
    for p in path.rglob("ruleset_contracts.csv"):
        if p.parent.name == "A_ruleset_contracts":
            # p = <root>/Dataset/A_ruleset_contracts/ruleset_contracts.csv
            maybe_dataset = p.parent.parent
            maybe_root = maybe_dataset.parent if maybe_dataset.name == "Dataset" else maybe_dataset
            if _looks_like_v5_dataset(maybe_root):
                candidates.append(maybe_root)
    if not candidates:
        raise FileNotFoundError(f"Cannot find a V5/V5.1 C-SeqGAN Dataset below {path}")
    return sorted(set(candidates), key=lambda x: len(str(x)))[0]


def materialize_cseqgan_dataset(data: str | Path, work_dir: str | Path) -> CSeqGANPaths:
    data = Path(data)
    work_dir = Path(work_dir)
    work_dir.mkdir(parents=True, exist_ok=True)
    if data.is_file() and data.suffix.lower() == ".zip":
        out = work_dir / data.stem.replace(" ", "_")
        marker = out / ".extracted_ok"
        if not marker.exists():
            out.mkdir(parents=True, exist_ok=True)
            with zipfile.ZipFile(data) as zf:
                zf.extractall(out)
            marker.write_text("ok", encoding="utf-8")
        root = _find_v5_root(out)
    elif data.is_dir():
        root = _find_v5_root(data)
    else:
        raise FileNotFoundError(str(data))
    ds = root / "Dataset" if (root / "Dataset" / "A_ruleset_contracts").exists() else root
    return CSeqGANPaths(
        root=root,
        dataset=ds,
        contracts_dir=ds / "A_ruleset_contracts",
        training_dir=ds / "B_conditioned_seqgan_training",
        candidates_dir=ds / "C_generated_candidates",
        rendered_dir=ds / "D_rendered_representations",
        metrics_dir=ds / "metrics",
    )


def split_conditioned_text(text: str) -> tuple[str, str]:
    m = PREFIX_RE.match(str(text or ""))
    if not m:
        return "", str(text or "")
    return m.group("prefix"), m.group("payload").strip()


def make_prefix(ruleset_id: str, structure_cell_id: str, ruleset_family: str) -> str:
    return f"<RULE={ruleset_id}><CELL={structure_cell_id}><FAMILY={ruleset_family}>"


def load_ruleset_contracts(paths: CSeqGANPaths, modules: list[str] | None = None) -> list[dict[str, Any]]:
    p = paths.contracts_dir / "ruleset_contracts.csv"
    if not p.exists():
        raise FileNotFoundError(p)
    df = pd.read_csv(p)
    if modules:
        df = df[df["module_id"].isin(modules)].copy()
    return df.fillna("").to_dict("records")


def _training_file_for_module(paths: CSeqGANPaths, module_id: str, *, use_full_coverage: bool) -> Path:
    mod = paths.training_dir / module_id
    if not mod.exists():
        raise FileNotFoundError(mod)
    candidates = []
    if use_full_coverage:
        candidates.append(mod / "cseqgan_train_full_coverage.jsonl")
    candidates.extend([mod / "cseqgan_train.jsonl", mod / "cseqgan_train_metadata.jsonl"])
    for p in candidates:
        if p.exists():
            return p
    raise FileNotFoundError(f"No C-SeqGAN training JSONL found in {mod}")


def _contract_from_row(row: dict[str, Any], module_id: str) -> dict[str, Any]:
    prefix, payload = split_conditioned_text(str(row.get("text") or row.get("training_payload") or row.get("payload_raw") or ""))
    ruleset_id = str(row.get("ruleset_id") or row.get("target_ruleset_id") or "")
    cell_id = str(row.get("structure_cell_id") or row.get("target_structure_cell_id") or "")
    family = str(row.get("ruleset_family") or row.get("target_ruleset_family") or row.get("semantic_family") or "")
    if not prefix and ruleset_id and cell_id and family:
        prefix = make_prefix(ruleset_id, cell_id, family)
    return {
        "sample_id": row.get("sample_id", ""),
        "module_id": str(row.get("module_id") or module_id),
        "y_level": str(row.get("y_level") or row.get("target_y_level") or ""),
        "ruleset_id": ruleset_id,
        "root_id": str(row.get("root_id") or row.get("target_root_id") or ""),
        "structure_cell_id": cell_id,
        "semantic_family": str(row.get("semantic_family") or row.get("target_semantic_family") or family),
        "ruleset_family": family,
        "skeleton_reference": str(row.get("skeleton_reference") or row.get("target_skeleton_reference") or ""),
        "required_tokens": row.get("required_tokens") or row.get("target_required_tokens") or "",
        "slot_schema_id": str(row.get("slot_schema_id") or row.get("target_slot_schema_id") or ""),
        "slot_schema_json": row.get("slot_schema_json") or "",
        "prefix": prefix,
        "payload_raw": str(row.get("payload_raw") or row.get("payload_stripped") or payload),
        "training_role": str(row.get("training_role") or ""),
        "usable_for_reward_positive": row.get("usable_for_reward_positive", ""),
        "source_view": str(row.get("source_view") or ""),
    }


def load_cseqgan_training_jsonl(
    paths: CSeqGANPaths,
    module_id: str,
    *,
    use_full_coverage: bool = True,
    limit: int | None = None,
    unique: bool = True,
) -> tuple[list[str], list[dict[str, Any]], Path]:
    src = _training_file_for_module(paths, module_id, use_full_coverage=use_full_coverage)
    rows = read_jsonl(src)
    if limit:
        rows = rows[: int(limit)]
    texts: list[str] = []
    contracts: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        raw_text = str(row.get("text") or row.get("training_payload") or "")
        prefix, payload = split_conditioned_text(raw_text)
        if not raw_text:
            c0 = _contract_from_row(row, module_id)
            prefix = c0["prefix"]
            payload = str(row.get("payload_raw") or row.get("payload_stripped") or "")
            raw_text = f"{prefix} {payload}".strip()
        if not raw_text:
            continue
        if unique and raw_text in seen:
            continue
        seen.add(raw_text)
        contract = _contract_from_row(row, module_id)
        if not contract.get("prefix"):
            contract["prefix"] = prefix
        if not contract.get("payload_raw"):
            contract["payload_raw"] = payload
        contract["training_payload"] = raw_text
        texts.append(raw_text)
        contracts.append(contract)
    if not texts:
        raise ValueError(f"Empty C-SeqGAN training file: {src}")
    return texts, contracts, src


def export_training_jsonl_for_legacy_train(texts: list[str], contracts: list[dict[str, Any]], out_path: str | Path) -> None:
    rows = []
    for text, c in zip(texts, contracts):
        row = dict(c)
        row["training_payload"] = text
        rows.append(row)
    write_jsonl(rows, out_path)
