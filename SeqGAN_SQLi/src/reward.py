"""Reward oracle: syntax (sqlparse) + bypass proxy + reward shaping."""
import sqlparse
from typing import Dict, List


ATTACK_TYPES = {
    'error_based', 'boolean_blind', 'time_blind', 'union_based',
    'heavy_query', 'auth_bypass', 'out_of_band', 'polyglot',
    'stacked_queries', 'generic', 'rce', 'comment_based',
    'inline_query', 'second_order', 'command_injection', 'ldap_injection',
}

MIN_ATTACK_LEN = 5  # tokens below this → trivial penalty


class RewardOracle:
    def __init__(self, lambda_d: float = 0.3, lambda_bypass: float = 0.5,
                 lambda_syntax: float = 0.2, length_penalty_coef: float = 0.01,
                 max_len: int = 80):
        self.lambda_d = lambda_d
        self.lambda_bypass = lambda_bypass
        self.lambda_syntax = lambda_syntax
        self.length_penalty_coef = length_penalty_coef
        self.max_len = max_len

    def update_lambda_syntax(self, new_val: float) -> None:
        self.lambda_syntax = new_val
        total = self.lambda_d + self.lambda_bypass + self.lambda_syntax
        self.lambda_d /= total
        self.lambda_bypass /= total
        self.lambda_syntax /= total

    def syntax_reward(self, payload: str) -> float:
        """1.0 if sqlparse parses without error, 0.0 otherwise."""
        try:
            stmts = sqlparse.parse(payload.strip())
            if stmts and stmts[0].tokens:
                return 1.0
            return 0.0
        except Exception:
            return 0.0

    def bypass_proxy(self, payload: str, sqli_type: str = None) -> float:
        """Dev-mode proxy bypass reward (no Docker WAF).
        In dev mode we can't check real WAF, so reward non-benign payloads."""
        if sqli_type is not None:
            return 0.1 if sqli_type in ATTACK_TYPES else 0.0
        # Heuristic: check for common attack patterns
        p = payload.lower()
        patterns = ["union", "select", "sleep(", "pg_sleep", "or 1=1",
                    "' or", "-- ", "#", "/*", "xp_cmd", "load_file",
                    "information_schema", "benchmark("]
        score = sum(1 for pat in patterns if pat in p)
        return min(0.1 * score, 0.5)

    def length_penalty(self, token_count: int) -> float:
        return self.length_penalty_coef * max(0, token_count - self.max_len)

    def trivial_penalty(self, token_count: int) -> float:
        return 0.3 if token_count < MIN_ATTACK_LEN else 0.0

    def compute(self, payload: str, d_score: float = 0.0,
                sqli_type: str = None, token_count: int = None) -> Dict[str, float]:
        r_syntax = self.syntax_reward(payload)
        r_bypass = self.bypass_proxy(payload, sqli_type)
        if token_count is None:
            token_count = len(payload.split())

        r_total = (
            self.lambda_d * d_score
            + self.lambda_bypass * r_bypass
            + self.lambda_syntax * r_syntax
            - self.length_penalty(token_count)
            - self.trivial_penalty(token_count)
        )
        return {
            'syntax': r_syntax,
            'bypass': r_bypass,
            'd_score': d_score,
            'total': r_total,
        }

    def compute_batch(self, payloads: List[str], d_scores: List[float] = None,
                      token_counts: List[int] = None) -> List[Dict[str, float]]:
        if d_scores is None:
            d_scores = [0.0] * len(payloads)
        if token_counts is None:
            token_counts = [len(p.split()) for p in payloads]
        return [self.compute(p, d, tc=tc)
                for p, d, tc in zip(payloads, d_scores, token_counts)]
