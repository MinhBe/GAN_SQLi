from __future__ import annotations

from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd
import torch
from torch import nn

from .config import ProjectConfig, set_global_seed
from .dataset import read_parquet
from .evaluator import EvaluatorConfig, evaluate_dataframe
from .models import (
    ACTION_TYPES,
    ActionGenerator,
    AnchorInfiller,
    PairedDScorer,
    action_label_vocabulary,
    condition_vocabulary,
    feature_matrix,
    save_d_scorer,
)
from .reporting import write_json
from .taxonomy import apply_action


def _load_split(config: ProjectConfig, split: str) -> pd.DataFrame:
    return read_parquet(config.slice_dir / f"action_surgery_{split}.parquet")


def _unique_payload_rows(df: pd.DataFrame) -> pd.DataFrame:
    return df.drop_duplicates(subset=["payload_id"]).reset_index(drop=True)


def train_anchor(
    config: ProjectConfig,
    epochs: int = 1,
) -> dict[str, Any]:
    train = _load_split(config, "train")
    dev = _load_split(config, "dev")
    model = AnchorInfiller.fit(train)
    model_path = config.model_dir / "anchor_infiller.json"
    model.save(model_path)

    rows = []
    for _, row in _unique_payload_rows(dev).iterrows():
        action_type = model.predict_row(row)
        rows.append(
            {
                **row.to_dict(),
                "action_type": action_type,
                "generated_payload": apply_action(row["payload_norm"], action_type),
                "generated_action_family": row.get("action_family", "none"),
            }
        )
    predictions = pd.DataFrame(rows)
    metrics = evaluate_dataframe(predictions, references=dev["payload_norm"].astype(str).tolist())
    output = {
        "model_path": str(model_path),
        "epochs": epochs,
        "dev_metrics": metrics,
    }
    write_json(output, config.eval_dir / "slice" / "anchor_infiller_eval.json")
    return output


def _d_training_frame(train: pd.DataFrame) -> tuple[pd.DataFrame, np.ndarray]:
    real = train.copy()
    real["generated_payload"] = real["payload_norm"]
    real["action_type"] = "real"
    real_labels = np.ones(len(real), dtype=np.float32)

    fake = train.copy()
    fake_labels = np.zeros(len(fake), dtype=np.float32)

    data = pd.concat([real, fake], ignore_index=True)
    labels = np.concatenate([real_labels, fake_labels])
    return data, labels


def train_d_scorer(
    config: ProjectConfig,
    epochs: int = 1,
    batch_size: int = 256,
    lr: float = 1e-3,
) -> dict[str, Any]:
    set_global_seed(config.seed)
    train = _load_split(config, "train")
    dev = _load_split(config, "dev")
    device = config.torch_device()

    train_frame, labels = _d_training_frame(train)
    features = feature_matrix(train_frame)
    model = PairedDScorer(features.shape[1]).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.BCEWithLogitsLoss()

    x = torch.tensor(features, dtype=torch.float32, device=device)
    y = torch.tensor(labels, dtype=torch.float32, device=device)
    indices = torch.arange(len(x), device=device)
    for _ in range(max(1, epochs)):
        shuffled = indices[torch.randperm(len(indices), device=device)]
        for start in range(0, len(shuffled), batch_size):
            batch = shuffled[start : start + batch_size]
            optimizer.zero_grad()
            loss = loss_fn(model(x[batch]), y[batch])
            loss.backward()
            optimizer.step()

    checkpoint_path = config.model_dir / "d_scorer" / "paired_d_scorer.pt"
    save_d_scorer(
        model,
        checkpoint_path,
        {"epochs": epochs, "train_examples": int(len(train_frame)), "device": device},
    )

    dev_frame, dev_labels = _d_training_frame(dev)
    with torch.no_grad():
        scores = torch.sigmoid(
            model(torch.tensor(feature_matrix(dev_frame), dtype=torch.float32, device=device))
        ).cpu().numpy()
    accuracy = float(((scores >= 0.5).astype(int) == dev_labels.astype(int)).mean())
    output = {
        "model_path": str(checkpoint_path),
        "epochs": epochs,
        "dev_accuracy": accuracy,
        "dev_examples": int(len(dev_frame)),
    }
    write_json(output, config.eval_dir / "slice" / "d_scorer_smoke_eval.json")
    return output


def train_action_gan(
    config: ProjectConfig,
    seed: int | None = None,
    epochs: int = 1,
    lr: float = 1e-3,
) -> dict[str, Any]:
    seed = config.seed if seed is None else seed
    set_global_seed(seed)
    train = _load_split(config, "train")
    dev = _load_split(config, "dev")
    device = config.torch_device()

    cond_vocab = condition_vocabulary(train)
    action_vocab = action_label_vocabulary(train)
    inverse_action_vocab = {idx: action for action, idx in action_vocab.items()}
    model = ActionGenerator(len(cond_vocab), len(action_vocab)).to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=lr)
    loss_fn = nn.CrossEntropyLoss()

    cond_ids = torch.tensor(
        [cond_vocab.get(AnchorInfiller.key(row), 0) for _, row in train.iterrows()],
        dtype=torch.long,
        device=device,
    )
    labels = torch.tensor(
        [action_vocab[str(action)] for action in train["action_type"]],
        dtype=torch.long,
        device=device,
    )
    for _ in range(max(1, epochs)):
        optimizer.zero_grad()
        logits = model.logits(cond_ids)
        loss = loss_fn(logits, labels)
        loss.backward()
        optimizer.step()

    rows = []
    unique_dev = _unique_payload_rows(dev)
    with torch.no_grad():
        for _, row in unique_dev.iterrows():
            key = AnchorInfiller.key(row)
            cond = torch.tensor([cond_vocab.get(key, 0)], dtype=torch.long, device=device)
            logits = model.logits(cond)
            action_idx = int(torch.argmax(logits, dim=-1).item())
            action_type = inverse_action_vocab[action_idx]
            rows.append(
                {
                    **row.to_dict(),
                    "action_type": action_type,
                    "generated_payload": apply_action(row["payload_norm"], action_type),
                }
            )
    predictions = pd.DataFrame(rows)
    metrics = evaluate_dataframe(predictions, references=dev["payload_norm"].astype(str).tolist())

    checkpoint_path = config.model_dir / "action_gan" / f"seed_{seed}" / "best.pt"
    checkpoint_path.parent.mkdir(parents=True, exist_ok=True)
    torch.save(
        {
            "model_type": "gumbel_action_surgery_generator",
            "state_dict": model.state_dict(),
            "condition_vocab": cond_vocab,
            "action_vocab": action_vocab,
            "all_action_types": ACTION_TYPES,
            "metadata": {
                "seed": seed,
                "epochs": epochs,
                "device": device,
                "scope": "action_category_only",
                "excluded": ["full_sequence_gan", "wgan_gp", "reinforce", "mc_rollout"],
            },
        },
        checkpoint_path,
    )
    output = {
        "model_path": str(checkpoint_path),
        "seed": seed,
        "epochs": epochs,
        "dev_metrics": metrics,
    }
    write_json(output, config.eval_dir / "slice" / f"action_gan_seed_{seed}_eval.json")
    return output
