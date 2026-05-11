"""Shared utilities: seeding, checkpointing, sequence padding."""
import os
import random
import numpy as np
import torch
from typing import List


def set_seed(seed: int) -> None:
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def pad_sequences(seqs: List[List[int]], pad_id: int, max_len: int = None) -> torch.Tensor:
    if max_len is None:
        max_len = max(len(s) for s in seqs)
    out = torch.full((len(seqs), max_len), pad_id, dtype=torch.long)
    for i, s in enumerate(seqs):
        length = min(len(s), max_len)
        out[i, :length] = torch.tensor(s[:length], dtype=torch.long)
    return out


def save_checkpoint(path: str, model, optimizer, step: int, metrics: dict) -> None:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    torch.save({
        'step': step,
        'model_state': model.state_dict(),
        'optimizer_state': optimizer.state_dict(),
        'metrics': metrics,
    }, path)


def load_checkpoint(path: str, model, optimizer=None):
    ckpt = torch.load(path, map_location='cpu')
    model.load_state_dict(ckpt['model_state'])
    if optimizer is not None and 'optimizer_state' in ckpt:
        optimizer.load_state_dict(ckpt['optimizer_state'])
    return ckpt.get('step', 0), ckpt.get('metrics', {})


def get_device() -> torch.device:
    return torch.device('cuda' if torch.cuda.is_available() else 'cpu')
