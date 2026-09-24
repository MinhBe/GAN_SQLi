from __future__ import annotations

import torch
from torch import nn
import torch.nn.functional as F


class Generator(nn.Module):
    def __init__(self, vocab_size: int, emb_dim: int = 64, hidden_dim: int = 128, num_layers: int = 1, pad_id: int = 0):
        super().__init__()
        self.vocab_size = vocab_size
        self.pad_id = pad_id
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=pad_id)
        self.rnn = nn.LSTM(emb_dim, hidden_dim, num_layers=num_layers, batch_first=True)
        self.out = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x):
        y, _ = self.rnn(self.emb(x))
        return self.out(y)

    @torch.no_grad()
    def sample(self, batch_size: int, max_len: int, bos_id: int, eos_id: int, temperature: float = 0.9, device: str = "cpu"):
        self.eval()
        x = torch.full((batch_size, 1), bos_id, dtype=torch.long, device=device)
        hidden = None
        samples = []
        finished = torch.zeros(batch_size, dtype=torch.bool, device=device)
        for _ in range(max_len - 1):
            emb = self.emb(x[:, -1:])
            y, hidden = self.rnn(emb, hidden)
            logits = self.out(y[:, -1]) / max(temperature, 1e-6)
            logits[:, 0] = -1e9  # PAD
            logits[:, 1] = -1e9  # BOS
            probs = F.softmax(logits, dim=-1)
            nxt = torch.multinomial(probs, num_samples=1).squeeze(1)
            nxt = torch.where(finished, torch.full_like(nxt, eos_id), nxt)
            samples.append(nxt)
            finished |= nxt.eq(eos_id)
            if finished.all():
                break
            x = torch.cat([x, nxt[:, None]], dim=1)
        if not samples:
            return torch.empty(batch_size, 0, dtype=torch.long, device=device)
        return torch.stack(samples, dim=1)


class Discriminator(nn.Module):
    def __init__(self, vocab_size: int, emb_dim: int = 64, channels: int = 96, kernel_sizes=(3, 5, 7), pad_id: int = 0):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=pad_id)
        self.convs = nn.ModuleList([nn.Conv1d(emb_dim, channels, k, padding=k//2) for k in kernel_sizes])
        self.fc = nn.Linear(channels * len(kernel_sizes), 1)

    def forward(self, x):
        emb = self.emb(x).transpose(1, 2)
        feats = []
        for conv in self.convs:
            z = F.relu(conv(emb))
            z = F.max_pool1d(z, kernel_size=z.shape[-1]).squeeze(-1)
            feats.append(z)
        return self.fc(torch.cat(feats, dim=1)).squeeze(1)
