"""Value baseline network: MLP on generator hidden state with EMA."""
import torch
import torch.nn as nn


class ValueBaseline(nn.Module):
    def __init__(self, hidden_dim: int = 512, ema_decay: float = 0.95):
        super().__init__()
        self.ema_decay = ema_decay
        self.net = nn.Sequential(
            nn.Linear(hidden_dim, 256),
            nn.ReLU(),
            nn.Dropout(0.1),
            nn.Linear(256, 1),
        )
        self._ema_value = 0.0
        self._initialized = False

    def forward(self, hidden: torch.Tensor) -> torch.Tensor:
        """hidden: (B, hidden_dim) → baseline (B,)"""
        return self.net(hidden).squeeze(-1)

    def update_ema(self, mean_reward: float) -> float:
        if not self._initialized:
            self._ema_value = mean_reward
            self._initialized = True
        else:
            self._ema_value = (
                self.ema_decay * self._ema_value
                + (1 - self.ema_decay) * mean_reward
            )
        return self._ema_value

    @property
    def ema_value(self) -> float:
        return self._ema_value
