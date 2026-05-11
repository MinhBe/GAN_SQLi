"""Monte Carlo rollout for Q(s,a) estimation."""
import torch
import torch.nn.functional as F
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .generator import GeneratorLSTM


class MCRollout:
    def __init__(self, generator: 'GeneratorLSTM', K: int = 16, max_len: int = 80):
        self.generator = generator
        self.K = K
        self.max_len = max_len

    @torch.no_grad()
    def estimate_q(self, partial_seqs: torch.Tensor, hidden_at_t,
                   reward_fn, eos_id: int, device: torch.device) -> torch.Tensor:
        """
        partial_seqs: (B, t+1) — sequences up to current step
        Returns Q estimates: (B,)
        """
        B, t1 = partial_seqs.shape
        all_rewards = torch.zeros(B, self.K, device=device)

        for k in range(self.K):
            # Continue generation from current position
            tokens = partial_seqs.clone()  # (B, t1)
            h = tuple(s.clone() for s in hidden_at_t)
            last_token = tokens[:, -1:]
            finished = tokens[:, -1] == eos_id

            for _ in range(self.max_len - t1):
                if finished.all():
                    break
                logits, h = self.generator(last_token, h)
                probs = F.softmax(logits[:, -1, :], dim=-1)
                next_tok = torch.multinomial(probs, 1)
                # Don't update finished sequences
                next_tok[finished] = eos_id
                tokens = torch.cat([tokens, next_tok], dim=1)
                finished = finished | (next_tok.squeeze(1) == eos_id)
                last_token = next_tok

            rewards = reward_fn(tokens)  # (B,)
            all_rewards[:, k] = rewards

        return all_rewards.mean(dim=1)  # (B,)
