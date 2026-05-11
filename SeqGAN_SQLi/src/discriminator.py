"""Discriminator: TextCNN with WGAN-GP scoring."""
import torch
import torch.nn as nn
import torch.autograd as autograd
from typing import List


class DiscriminatorCNN(nn.Module):
    def __init__(self, vocab_size: int, embed_dim: int = 128,
                 kernel_sizes: List[int] = None, num_filters: int = 128):
        super().__init__()
        if kernel_sizes is None:
            kernel_sizes = [3, 4, 5]
        self.embed = nn.Embedding(vocab_size, embed_dim, padding_idx=0)
        self.convs = nn.ModuleList([
            nn.Conv1d(embed_dim, num_filters, k) for k in kernel_sizes
        ])
        self.dropout = nn.Dropout(0.3)
        self.fc = nn.Linear(num_filters * len(kernel_sizes), 1)

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        """input_ids: (B, T) → score (B,)"""
        x = self.embed(input_ids).permute(0, 2, 1)  # (B, E, T)
        pooled = []
        for conv in self.convs:
            h = torch.relu(conv(x))       # (B, F, T-k+1)
            h = h.max(dim=-1).values      # (B, F)
            pooled.append(h)
        out = self.dropout(torch.cat(pooled, dim=1))  # (B, F*n_kernels)
        return self.fc(out).squeeze(1)    # (B,)

    def gradient_penalty(self, real_ids: torch.Tensor,
                         fake_ids: torch.Tensor, gp_lambda: float = 10.0) -> torch.Tensor:
        """WGAN-GP: interpolate in embedding space."""
        B = real_ids.size(0)
        device = real_ids.device
        alpha = torch.rand(B, 1, 1, device=device)

        real_emb = self.embed(real_ids).detach()   # (B, T, E)
        fake_emb = self.embed(fake_ids).detach()

        T_min = min(real_emb.size(1), fake_emb.size(1))
        real_emb = real_emb[:, :T_min, :]
        fake_emb = fake_emb[:, :T_min, :]

        interp_emb = (alpha * real_emb + (1 - alpha) * fake_emb).requires_grad_(True)
        x = interp_emb.permute(0, 2, 1)  # (B, E, T)
        pooled = []
        for conv in self.convs:
            h = torch.relu(conv(x)).max(dim=-1).values
            pooled.append(h)
        out = self.dropout(torch.cat(pooled, dim=1))
        score = self.fc(out).squeeze(1)

        grads = autograd.grad(
            outputs=score, inputs=interp_emb,
            grad_outputs=torch.ones_like(score),
            create_graph=True, retain_graph=True
        )[0]
        gp = ((grads.norm(2, dim=-1) - 1) ** 2).mean()
        return gp_lambda * gp
