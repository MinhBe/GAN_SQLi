"""Generator policy: 3-layer LSTM."""
import torch
import torch.nn as nn
import torch.nn.functional as F
from typing import Optional, Tuple


class GeneratorLSTM(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 128, hidden_dim: int = 512,
                 num_layers: int = 3, dropout: float = 0.2):
        super().__init__()
        self.vocab_size = vocab_size
        self.hidden_dim = hidden_dim
        self.num_layers = num_layers
        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.lstm = nn.LSTM(embed_dim, hidden_dim, num_layers,
                            batch_first=True, dropout=dropout if num_layers > 1 else 0.0)
        self.dropout = nn.Dropout(dropout)
        self.proj = nn.Linear(hidden_dim, vocab_size)

    def forward(self, input_ids: torch.Tensor,
                hidden: Optional[Tuple] = None) -> Tuple[torch.Tensor, Tuple]:
        x = self.dropout(self.embed(input_ids))
        out, hidden = self.lstm(x, hidden)
        logits = self.proj(self.dropout(out))
        return logits, hidden

    def init_hidden(self, batch_size: int, device: torch.device) -> Tuple:
        h = torch.zeros(self.num_layers, batch_size, self.hidden_dim, device=device)
        c = torch.zeros(self.num_layers, batch_size, self.hidden_dim, device=device)
        return h, c

    def sample(self, batch_size: int, max_len: int, device: torch.device,
               sos_id: int = 2, eos_id: int = 3,
               temperature: float = 1.0) -> Tuple[torch.Tensor, torch.Tensor]:
        """Autoregressive sampling. Returns (token_ids, log_probs), both (B, T)."""
        hidden = self.init_hidden(batch_size, device)
        token = torch.full((batch_size, 1), sos_id, dtype=torch.long, device=device)
        tokens_list, logprob_list = [], []
        finished = torch.zeros(batch_size, dtype=torch.bool, device=device)

        for _ in range(max_len):
            logits, hidden = self.forward(token, hidden)  # (B, 1, V)
            logits = logits[:, -1, :] / temperature
            log_probs = F.log_softmax(logits, dim=-1)
            probs = torch.exp(log_probs)
            next_token = torch.multinomial(probs, 1)  # (B, 1)
            step_logprob = log_probs.gather(1, next_token)  # (B, 1)

            finished = finished | (next_token.squeeze(1) == eos_id)
            tokens_list.append(next_token)
            logprob_list.append(step_logprob)
            token = next_token

            if finished.all():
                break

        tokens = torch.cat(tokens_list, dim=1)   # (B, T)
        logprobs = torch.cat(logprob_list, dim=1)  # (B, T)
        return tokens, logprobs

    def get_hidden_last(self, input_ids: torch.Tensor) -> torch.Tensor:
        """Return last hidden state for baseline input."""
        _, (h, _) = self.forward(input_ids)
        return h[-1]  # (B, hidden_dim)
