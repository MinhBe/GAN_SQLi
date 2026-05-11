"""SQLiEnv: gym-like RL environment for token-by-token SQLi generation."""
from typing import Dict, List, Optional, Tuple
from .reward import RewardOracle
from .tokenizer import SQLTokenizer


class SQLiEnv:
    def __init__(self, tokenizer: SQLTokenizer, reward_oracle: RewardOracle,
                 max_len: int = 80):
        self.tokenizer = tokenizer
        self.reward_oracle = reward_oracle
        self.max_len = max_len
        self._tokens: List[int] = []

    def reset(self) -> List[int]:
        self._tokens = [self.tokenizer.sos_id]
        return list(self._tokens)

    def step(self, action: int) -> Tuple[List[int], float, bool, Dict]:
        self._tokens.append(action)
        done = (action == self.tokenizer.eos_id) or (len(self._tokens) >= self.max_len)
        reward = 0.0
        info: Dict = {}
        if done:
            payload = self.tokenizer.decode(self._tokens)
            result = self.reward_oracle.compute(
                payload, token_count=len(self._tokens)
            )
            reward = result['total']
            info = result
        return list(self._tokens), reward, done, info

    def compute_reward(self, token_ids: List[int],
                       d_score: float = 0.0) -> Dict[str, float]:
        payload = self.tokenizer.decode(token_ids)
        return self.reward_oracle.compute(
            payload, d_score=d_score, token_count=len(token_ids)
        )
