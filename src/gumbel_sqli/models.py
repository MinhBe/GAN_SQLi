from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
from typing import Any

import numpy as np
import pandas as pd
import torch
from torch import nn

from .taxonomy import ACTION_TAXONOMY


ACTION_TYPES = sorted(
    {action for spec in ACTION_TAXONOMY.values() for action in spec["actions"]}
    | {"identity", "real"}
)
ACTION_TO_INDEX = {action: idx for idx, action in enumerate(ACTION_TYPES)}


def payload_numeric_features(payload: str) -> list[float]:
    text = str(payload or "")
    length = max(len(text), 1)
    return [
        min(length / 320.0, 5.0),
        sum(ch.isdigit() for ch in text) / length,
        sum(ch.isalpha() for ch in text) / length,
        text.count("'") / length,
        text.count('"') / length,
        text.count("(") / length,
        text.count(")") / length,
        len(re.findall(r"--|#|/\*", text)) / length,
        len(re.findall(r"%[0-9A-Fa-f]{2}", text)) / length,
        len(re.findall(r"\b(and|or|union|select|where)\b", text, re.I)) / length,
    ]


def one_hot(value: str, vocabulary: dict[str, int]) -> list[float]:
    values = [0.0] * len(vocabulary)
    values[vocabulary.get(str(value), vocabulary.get("identity", 0))] = 1.0
    return values


def feature_matrix(
    df: pd.DataFrame,
    payload_column: str = "generated_payload",
    action_column: str = "action_type",
) -> np.ndarray:
    if payload_column not in df.columns:
        payload_column = "payload_norm"
    rows = []
    for _, row in df.iterrows():
        payload = row.get(payload_column, row.get("payload_norm", ""))
        action_type = str(row.get(action_column, "identity"))
        rows.append(payload_numeric_features(payload) + one_hot(action_type, ACTION_TO_INDEX))
    return np.asarray(rows, dtype=np.float32)


class PairedDScorer(nn.Module):
    def __init__(self, feature_dim: int):
        super().__init__()
        hidden = max(12, min(64, feature_dim * 2))
        self.net = nn.Sequential(
            nn.Linear(feature_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, 1),
        )

    def forward(self, features: torch.Tensor) -> torch.Tensor:
        return self.net(features).squeeze(-1)


class ActionGenerator(nn.Module):
    def __init__(self, num_conditions: int, num_actions: int):
        super().__init__()
        self.embedding = nn.Embedding(num_conditions, 16)
        self.net = nn.Sequential(
            nn.Linear(16, 32),
            nn.ReLU(),
            nn.Linear(32, num_actions),
        )

    def forward(self, condition_ids: torch.Tensor, temperature: float = 1.0) -> torch.Tensor:
        logits = self.net(self.embedding(condition_ids))
        return torch.nn.functional.gumbel_softmax(logits, tau=temperature, hard=False)

    def logits(self, condition_ids: torch.Tensor) -> torch.Tensor:
        return self.net(self.embedding(condition_ids))


@dataclass
class AnchorInfiller:
    global_action: str
    by_condition: dict[str, str]

    @staticmethod
    def key(row: pd.Series | dict[str, Any]) -> str:
        return "|".join(
            [
                str(row.get("technique_primary", "unlabeled_technique")),
                str(row.get("db_hint", "unlabeled_db_hint")),
                str(row.get("action_family", row.get("primary_action_family", "none"))),
            ]
        )

    @classmethod
    def fit(cls, df: pd.DataFrame) -> "AnchorInfiller":
        global_action = str(df["action_type"].mode().iloc[0])
        by_condition = {}
        for key, group in df.groupby(df.apply(cls.key, axis=1)):
            by_condition[str(key)] = str(group["action_type"].mode().iloc[0])
        return cls(global_action=global_action, by_condition=by_condition)

    def predict_row(self, row: pd.Series | dict[str, Any]) -> str:
        return self.by_condition.get(self.key(row), self.global_action)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(
                {
                    "model_type": "anchor_only_action_infiller",
                    "global_action": self.global_action,
                    "by_condition": self.by_condition,
                },
                indent=2,
            ),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path: Path) -> "AnchorInfiller":
        payload = json.loads(path.read_text(encoding="utf-8"))
        return cls(
            global_action=payload["global_action"],
            by_condition={str(k): str(v) for k, v in payload["by_condition"].items()},
        )


def save_d_scorer(model: PairedDScorer, path: Path, metadata: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_type": "paired_d_scorer",
            "state_dict": model.state_dict(),
            "feature_dim": next(model.parameters()).shape[1],
            "action_types": ACTION_TYPES,
            "metadata": metadata,
        },
        path,
    )


def load_d_scorer(path: Path, device: str = "cpu") -> PairedDScorer:
    checkpoint = torch.load(path, map_location=device)
    model = PairedDScorer(int(checkpoint["feature_dim"]))
    model.load_state_dict(checkpoint["state_dict"])
    model.to(device)
    model.eval()
    return model


def score_with_d_scorer(df: pd.DataFrame, checkpoint_path: Path, device: str = "cpu") -> np.ndarray:
    model = load_d_scorer(checkpoint_path, device=device)
    features = torch.tensor(feature_matrix(df), dtype=torch.float32, device=device)
    with torch.no_grad():
        return torch.sigmoid(model(features)).cpu().numpy()


def condition_vocabulary(df: pd.DataFrame) -> dict[str, int]:
    keys = sorted(set(df.apply(AnchorInfiller.key, axis=1)))
    return {key: idx for idx, key in enumerate(keys)}


def action_label_vocabulary(df: pd.DataFrame) -> dict[str, int]:
    actions = sorted(set(str(action) for action in df["action_type"]))
    return {action: idx for idx, action in enumerate(actions)}
