from __future__ import annotations

import copy

import torch

from .models import Generator, Discriminator
from .tokenizer import CharCodec
from .reward import score_many


def pad_to(seq: torch.Tensor, width: int, pad_id: int) -> torch.Tensor:
    if seq.size(1) >= width:
        return seq[:, :width]
    pad = torch.full((seq.size(0), width - seq.size(1)), pad_id, dtype=seq.dtype, device=seq.device)
    return torch.cat([seq, pad], dim=1)


class Rollout:
    """Monte-Carlo rollout helper for SeqGAN-style intermediate rewards."""

    def __init__(self, generator: Generator, update_rate: float = 0.8):
        self.generator = copy.deepcopy(generator).eval()
        self.update_rate = float(update_rate)
        for p in self.generator.parameters():
            p.requires_grad_(False)

    @torch.no_grad()
    def update(self, generator: Generator) -> None:
        src = generator.state_dict()
        dst = self.generator.state_dict()
        for k, old in dst.items():
            old.copy_(self.update_rate * old + (1.0 - self.update_rate) * src[k])

    @torch.no_grad()
    def rewards(
        self,
        seq: torch.Tensor,
        discriminator: Discriminator,
        codec: CharCodec,
        *,
        contracts: list[dict] | None = None,
        training_hashes: set[str] | None = None,
        n_rollout: int = 4,
        static_weight: float = 0.35,
        temperature: float = 0.9,
    ) -> torch.Tensor:
        device = seq.device
        batch, steps = seq.size()
        out = torch.zeros(batch, steps, dtype=torch.float32, device=device)
        width = codec.max_len
        for t in range(1, steps + 1):
            acc = torch.zeros(batch, dtype=torch.float32, device=device)
            prefix = seq[:, :t]
            for _ in range(max(1, int(n_rollout))):
                completed = self.generator.complete_from_prefix(prefix, width, codec.bos_id, codec.eos_id, temperature)
                disc_in = pad_to(completed, width, codec.pad_id)
                d_reward = torch.sigmoid(discriminator(disc_in)).float()
                decoded = [codec.decode(row.tolist()) for row in completed.detach().cpu()]
                s_reward = torch.tensor(
                    [r.reward for r in score_many(decoded, contracts, training_hashes=training_hashes)],
                    dtype=torch.float32,
                    device=device,
                )
                acc += (1.0 - static_weight) * d_reward + static_weight * s_reward
            out[:, t - 1] = acc / max(1, int(n_rollout))
        return out
