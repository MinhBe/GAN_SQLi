from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
import os
import random
from typing import Iterable

import numpy as np


DEFAULT_SEED = 1729


def resolve_project_root(root: str | Path | None = None) -> Path:
    if root is not None:
        return Path(root).expanduser().resolve()
    env_root = os.environ.get("GUMBEL_SQLI_ROOT")
    if env_root:
        return Path(env_root).expanduser().resolve()
    return Path.cwd().resolve()


def _existing(paths: Iterable[Path]) -> list[Path]:
    return [path for path in paths if path.exists()]


@dataclass(frozen=True)
class ProjectConfig:
    root: Path = field(default_factory=resolve_project_root)
    seed: int = DEFAULT_SEED
    device: str = "auto"

    @classmethod
    def from_args(
        cls,
        root: str | Path | None = None,
        seed: int = DEFAULT_SEED,
        device: str = "auto",
    ) -> "ProjectConfig":
        return cls(root=resolve_project_root(root), seed=seed, device=device)

    @property
    def label_data_dir(self) -> Path:
        return self.root / "Asset" / "LabelData"

    @property
    def data_dir(self) -> Path:
        return self.root / "data" / "gumbel"

    @property
    def audit_dir(self) -> Path:
        return self.data_dir / "audit"

    @property
    def slice_dir(self) -> Path:
        return self.data_dir / "slice"

    @property
    def full_dir(self) -> Path:
        return self.data_dir / "full"

    @property
    def eval_dir(self) -> Path:
        return self.root / "eval" / "gumbel"

    @property
    def model_dir(self) -> Path:
        return self.root / "models" / "gumbel"

    @property
    def report_dir(self) -> Path:
        return self.root / "reports" / "gumbel"

    @property
    def timeline_progress_path(self) -> Path:
        return (
            self.root
            / "Guiding_Gumbel-Softmax"
            / "timeline"
            / "timeline_progress.json"
        )

    @property
    def default_input_paths(self) -> list[Path]:
        base = self.label_data_dir
        candidates = [
            base / "Testing" / "Testing_labeled.csv",
            base / "Testing_1" / "data1" / "test_labeled.csv",
            base / "Testing_1" / "data1" / "labeled.csv",
            base / "Testing_1" / "báo cáo đánh nhãn" / "final_dataset_1_ai_only_labeled.csv",
            base / "FinalDataSet" / "final_dataset_1.csv",
            base / "Dataset Source" / "mendeley_SQLI_Dataset.csv",
            base / "Dataset Source" / "bccc_sfu" / "BCCC-SFU-SQLInj-2023.csv",
            base / "Dataset Source" / "gist_johntroony" / "Troony_SQLi_Payloads.txt",
        ]
        return _existing(candidates)

    def torch_device(self) -> str:
        if self.device != "auto":
            return self.device
        try:
            import torch

            return "cuda" if torch.cuda.is_available() else "cpu"
        except Exception:
            return "cpu"


def set_global_seed(seed: int = DEFAULT_SEED) -> None:
    random.seed(seed)
    np.random.seed(seed)
    try:
        import torch

        torch.manual_seed(seed)
        if torch.cuda.is_available():
            torch.cuda.manual_seed_all(seed)
    except Exception:
        pass


def ensure_parquet_engine() -> None:
    try:
        import pyarrow  # noqa: F401
    except ImportError as exc:
        raise RuntimeError(
            "pyarrow is required for .parquet artifacts. Install with "
            "`python -m pip install pyarrow`."
        ) from exc
