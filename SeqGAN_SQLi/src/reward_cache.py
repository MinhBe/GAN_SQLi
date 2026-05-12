"""reward_cache.py — LRU cache cho composite reward."""
from collections import OrderedDict
from typing import Any, Callable, Optional


class RewardCache:
    """LRU cache: payload_hash → reward value."""

    def __init__(self, max_size: int = 100000):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_size
        self.hits = 0
        self.misses = 0

    def get(self, payload: str) -> Optional[Any]:
        h = hash(payload)
        if h in self.cache:
            self.hits += 1
            self.cache.move_to_end(h)
            return self.cache[h]
        self.misses += 1
        return None

    def set(self, payload: str, value: Any):
        h = hash(payload)
        self.cache[h] = value
        self.cache.move_to_end(h)
        if len(self.cache) > self.max_size:
            self.cache.popitem(last=False)

    def get_or_compute(self, payload: str, compute_fn: Callable) -> Any:
        cached = self.get(payload)
        if cached is not None:
            return cached
        result = compute_fn(payload)
        self.set(payload, result)
        return result

    def stats(self) -> dict:
        total = self.hits + self.misses
        return {
            "size": len(self.cache),
            "hits": self.hits,
            "misses": self.misses,
            "hit_rate": self.hits / max(total, 1),
        }

    def reset(self):
        self.cache.clear()
        self.hits = 0
        self.misses = 0
