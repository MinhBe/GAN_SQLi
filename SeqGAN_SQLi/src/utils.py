"""Shared utilities: seeding, checkpointing, sequence padding, SQLi type conditioning."""
import os
import random
import numpy as np
import torch
from typing import List, Optional


# ── SQLi type vocabulary for conditional generation ──
SQLI_TYPES = [
    'benign', 'error_based', 'boolean_blind', 'time_blind', 'union_based',
    'heavy_query', 'auth_bypass', 'out_of_band', 'unknown', 'polyglot',
    'stacked_queries', 'generic', 'rce', 'comment_based', 'inline_query',
    'second_order', 'ldap_injection', 'command_injection',
]
SQLI_TYPE_TO_IDX = {t: i for i, t in enumerate(SQLI_TYPES)}
NUM_SQLI_TYPES = len(SQLI_TYPES)


def sqli_type_to_idx(sqli_type: str) -> int:
    return SQLI_TYPE_TO_IDX.get(sqli_type, SQLI_TYPE_TO_IDX.get('benign', 0))


def idx_to_sqli_type(idx: int) -> str:
    if 0 <= idx < NUM_SQLI_TYPES:
        return SQLI_TYPES[idx]
    return SQLI_TYPES[0]


def encode_condition(sqli_type: str, device: torch.device = None) -> torch.Tensor:
    idx = sqli_type_to_idx(sqli_type)
    t = torch.tensor([idx], dtype=torch.long)
    if device is not None:
        t = t.to(device)
    return t


def encode_conditions(sqli_types: List[str], device: torch.device = None) -> torch.Tensor:
    indices = [sqli_type_to_idx(t) for t in sqli_types]
    t = torch.tensor(indices, dtype=torch.long)
    if device is not None:
        t = t.to(device)
    return t


def sample_random_conditions(batch_size: int, device: torch.device = None,
                             exclude_benign: bool = True) -> torch.Tensor:
    """Sample random SQLi attack types for unconditional generation."""
    start = 1 if exclude_benign else 0  # skip index 0 (benign) for attack generation
    indices = torch.randint(start, NUM_SQLI_TYPES, (batch_size,))
    if device is not None:
        indices = indices.to(device)
    return indices


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
