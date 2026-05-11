"""Scheduled Sampling: epsilon ramps linearly from 0 to 1 over ramp_steps."""


class ScheduledSampler:
    def __init__(self, ramp_steps: int = 5000):
        self.ramp_steps = ramp_steps
        self._step = 0

    @property
    def epsilon(self) -> float:
        return min(1.0, self._step / max(1, self.ramp_steps))

    def step(self) -> None:
        self._step += 1

    def should_use_own_pred(self) -> bool:
        import random
        return random.random() < self.epsilon
