from __future__ import annotations

import torch
from torch import nn
import torch.nn.functional as F


class Generator(nn.Module):
    def __init__(self, vocab_size: int, emb_dim: int = 96, hidden_dim: int = 192, num_layers: int = 1, pad_id: int = 0):
        super().__init__()
        self.vocab_size = vocab_size
        self.pad_id = pad_id
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=pad_id)
        self.rnn = nn.LSTM(emb_dim, hidden_dim, num_layers=num_layers, batch_first=True)
        self.out = nn.Linear(hidden_dim, vocab_size)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        y, _ = self.rnn(self.emb(x))
        return self.out(y)

    def step(self, last_token: torch.Tensor, hidden=None):
        y, hidden = self.rnn(self.emb(last_token[:, None]), hidden)
        return self.out(y[:, -1]), hidden

    def sample_with_logp(
        self,
        batch_size: int,
        max_len: int,
        bos_id: int,
        eos_id: int,
        temperature: float = 0.9,
        device: str = "cpu",
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor]:
        x = torch.full((batch_size,), bos_id, dtype=torch.long, device=device)
        hidden = None
        seq, logps, mask = [], [], []
        finished = torch.zeros(batch_size, dtype=torch.bool, device=device)
        banned = torch.zeros(self.vocab_size, dtype=torch.bool, device=device)
        banned[self.pad_id] = True
        banned[bos_id] = True
        for _ in range(max_len - 1):
            logits, hidden = self.step(x, hidden)
            logits = logits / max(float(temperature), 1e-6)
            logits = logits.masked_fill(banned.unsqueeze(0), -1e9)
            probs = F.softmax(logits.float(), dim=-1)
            dist = torch.distributions.Categorical(probs=probs)
            sampled = dist.sample()
            logp = dist.log_prob(sampled)
            active = ~finished
            token = torch.where(active, sampled, torch.full_like(sampled, eos_id))
            seq.append(token)
            logps.append(torch.where(active, logp, torch.zeros_like(logp)))
            mask.append(active.float())
            finished = finished | token.eq(eos_id)
            x = token
            if bool(finished.all().item()):
                break
        return torch.stack(seq, 1), torch.stack(logps, 1), torch.stack(mask, 1)

    @torch.no_grad()
    def sample(self, batch_size: int, max_len: int, bos_id: int, eos_id: int, temperature: float = 0.9, device: str = "cpu") -> torch.Tensor:
        seq, _, _ = self.sample_with_logp(batch_size, max_len, bos_id, eos_id, temperature, device)
        return seq

    @torch.no_grad()
    def complete_from_prefix(
        self,
        prefix: torch.Tensor,
        max_len: int,
        bos_id: int,
        eos_id: int,
        temperature: float = 0.9,
    ) -> torch.Tensor:
        """Complete a batch of partial generated sequences.

        `prefix` excludes BOS and contains already-generated tokens. It may contain
        EOS; rows with EOS are padded by repeating EOS.
        """
        device = prefix.device
        batch = prefix.size(0)
        if prefix.numel() == 0:
            return self.sample(batch, max_len, bos_id, eos_id, temperature, str(device))
        inp = torch.cat([torch.full((batch, 1), bos_id, dtype=torch.long, device=device), prefix], dim=1)
        _, hidden = self.rnn(self.emb(inp))
        out = [prefix]
        last = prefix[:, -1]
        finished = prefix.eq(eos_id).any(dim=1)
        banned = torch.zeros(self.vocab_size, dtype=torch.bool, device=device)
        banned[self.pad_id] = True
        banned[bos_id] = True
        for _ in range(max_len - 1 - prefix.size(1)):
            logits, hidden = self.step(last, hidden)
            logits = logits / max(float(temperature), 1e-6)
            logits = logits.masked_fill(banned.unsqueeze(0), -1e9)
            probs = F.softmax(logits.float(), dim=-1)
            nxt = torch.multinomial(probs, 1).squeeze(1)
            nxt = torch.where(finished, torch.full_like(nxt, eos_id), nxt)
            out.append(nxt[:, None])
            finished = finished | nxt.eq(eos_id)
            last = nxt
            if bool(finished.all().item()):
                break
        return torch.cat(out, dim=1)


class Discriminator(nn.Module):
    def __init__(self, vocab_size: int, emb_dim: int = 96, channels: int = 128, kernel_sizes=(3, 5, 7), pad_id: int = 0):
        super().__init__()
        self.emb = nn.Embedding(vocab_size, emb_dim, padding_idx=pad_id)
        self.convs = nn.ModuleList([nn.Conv1d(emb_dim, channels, k, padding=k // 2) for k in kernel_sizes])
        self.fc = nn.Linear(channels * len(kernel_sizes), 1)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        z = self.emb(x).transpose(1, 2)
        feats = []
        for conv in self.convs:
            h = F.relu(conv(z))
            feats.append(F.max_pool1d(h, kernel_size=h.size(-1)).squeeze(-1))
        return self.fc(torch.cat(feats, dim=1)).squeeze(1)
