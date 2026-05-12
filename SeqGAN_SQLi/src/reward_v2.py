"""reward_v2.py — Composite reward: WAF boundary + custom rules + AST diversity + DB execution."""
from .ast_tracker import ASTFingerprintTracker
from .custom_rules import CustomRuleEngine
from .db_sandbox import DBSandbox
from .parser_gate import SQLParserGate
from .reward_cache import RewardCache
from .waf_oracle import WAFOracle, waf_boundary_reward


PHASE_WEIGHTS = {
    "warmup":      {"owasp": 0.0, "custom": 0.7, "diversity": 0.0, "overlap": 0.0},
    "adversarial": {"owasp": 0.4, "custom": 0.3, "diversity": 0.2, "overlap": 0.1},
    "refinement":  {"owasp": 0.3, "custom": 0.1, "diversity": 0.5, "overlap": 0.1},
}


class CompositeRewardV2:
    """
    r = syntax_gate × executable_gate × (
          w_owasp · r_boundary(anomaly)
        + w_custom · r_custom
        + w_diversity · novelty
        - w_overlap · overlap_penalty
    )

    Gates trả -1.0 hoặc -0.5 ngay khi fail (không tính composite).
    """

    def __init__(
        self,
        phase: str = "warmup",
        waf_url: str = "http://localhost:8080",
        boundary_threshold: int = 5,
        use_waf: bool = True,
        cache_size: int = 100000,
    ):
        self.parser = SQLParserGate()
        self.db = DBSandbox()
        self.custom = CustomRuleEngine()
        self.ast = ASTFingerprintTracker()
        self.waf = WAFOracle(url=waf_url) if use_waf else None
        self.use_waf = use_waf
        self.boundary_threshold = boundary_threshold
        self.cache = RewardCache(max_size=cache_size)
        self.set_phase(phase)

    def set_phase(self, phase: str):
        if phase not in PHASE_WEIGHTS:
            raise ValueError(f"Unknown phase: {phase}")
        self.phase = phase
        self.weights = PHASE_WEIGHTS[phase]

    def __call__(self, payload: str) -> float:
        cached = self.cache.get(payload)
        if cached is not None:
            return cached

        if self.parser.evaluate(payload) == 0:
            r = -1.0
            self.cache.set(payload, r)
            return r

        if self.db.evaluate(payload) == 0:
            r = -0.5
            self.cache.set(payload, r)
            return r

        if self.weights["owasp"] > 0 and self.use_waf and self.waf:
            waf_result = self.waf.evaluate(payload)
            r_owasp = waf_boundary_reward(
                waf_result["anomaly_score"], self.boundary_threshold
            )
        else:
            r_owasp = 0.0

        r_custom = self.custom.score(payload)
        r_diversity = self.ast.novelty(payload) if self.weights["diversity"] > 0 else 0.0
        overlap_penalty = max(0, r_owasp - r_custom) if r_owasp > 0 else 0.0

        r = (
            self.weights["owasp"] * r_owasp
            + self.weights["custom"] * r_custom
            + self.weights["diversity"] * r_diversity
            - self.weights["overlap"] * overlap_penalty
        )

        self.cache.set(payload, r)
        return r

    def get_stats(self) -> dict:
        return {
            "phase": self.phase,
            "cache": self.cache.stats(),
            "ast": self.ast.get_stats(),
        }

    def reset_ast_cache(self):
        """Dùng trong refinement phase để force re-exploration."""
        self.ast.reset()

    def close(self):
        self.db.close()
        if self.waf:
            self.waf.close()
