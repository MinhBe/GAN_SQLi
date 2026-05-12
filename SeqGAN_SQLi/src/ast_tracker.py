"""ast_tracker.py — Track AST subtree fingerprints để measure structural diversity."""
from collections import OrderedDict
from typing import Set

import sqlparse


class ASTFingerprintTracker:
    """Compute subtree fingerprints depth=3, track novelty cho diversity reward."""

    def __init__(self, max_cache_size: int = 10000, depth: int = 3):
        self.cache: OrderedDict = OrderedDict()
        self.max_size = max_cache_size
        self.depth = depth
        self.parse_fail_count = 0
        self.total_count = 0

    def _extract_subtrees(self, node, current_depth=0):
        if current_depth >= self.depth:
            return [hash(str(getattr(node, "ttype", None)))]

        ttype_hash = hash(str(getattr(node, "ttype", None)))
        child_hashes = []
        for child in getattr(node, "tokens", []):
            child_hashes.extend(self._extract_subtrees(child, current_depth + 1))

        combined = (
            hash((ttype_hash, tuple(sorted(child_hashes[:5]))))
            if child_hashes
            else ttype_hash
        )
        return [combined] + child_hashes

    def fingerprint(self, payload: str) -> Set[int]:
        if not payload or not isinstance(payload, str):
            return set()
        self.total_count += 1
        try:
            wrapped = f"SELECT * FROM dummy WHERE id={payload}"
            parsed = sqlparse.parse(wrapped)
            if not parsed:
                self.parse_fail_count += 1
                return set()
            return set(self._extract_subtrees(parsed[0]))
        except Exception:
            self.parse_fail_count += 1
            return set()

    def novelty(self, payload: str) -> float:
        """Returns 1.0 nếu hoàn toàn mới, 0.0 nếu đã thấy hết."""
        fp = self.fingerprint(payload)
        if not fp:
            return 0.0
        if not self.cache:
            for f in fp:
                self.cache[f] = 1
            return 1.0

        new_count = sum(1 for f in fp if f not in self.cache)
        novelty_score = new_count / len(fp)

        for f in fp:
            if f in self.cache:
                self.cache[f] += 1
                self.cache.move_to_end(f)
            else:
                self.cache[f] = 1
                if len(self.cache) > self.max_size:
                    self.cache.popitem(last=False)

        return novelty_score

    def reset(self):
        self.cache.clear()
        self.parse_fail_count = 0
        self.total_count = 0

    def get_stats(self) -> dict:
        return {
            "cache_size": len(self.cache),
            "parse_fail_rate": self.parse_fail_count / max(self.total_count, 1),
            "total_seen": self.total_count,
        }
