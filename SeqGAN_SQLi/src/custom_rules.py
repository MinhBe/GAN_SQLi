"""custom_rules.py — Kiểm tra payload có phải SQLi đúng nghĩa không.
Chống reward hacking — payload chỉ bypass OWASP qua trick encoding
nhưng không thực sự là SQLi sẽ fail ở đây.
"""
import re
from typing import List, Tuple


class CustomRuleEngine:
    """Rule-based SQLi validity checker."""

    KEYWORDS = [
        "union", "select", "or 1", "and 1", "or '", "and '",
        "sleep", "benchmark", "waitfor", "pg_sleep",
        "extractvalue", "updatexml", "xmltype", "concat",
        "drop", "insert", "delete", "update", "alter",
    ]
    QUOTE_OPS = ["'", '"', "--", "/*", "*/", "#", ";", "||", "&&"]
    RELATIONAL = re.compile(r"[=<>]|union|select|order\s+by|having|group\s+by", re.I)
    BENIGN_LIKE = re.compile(r"^[\w\s]+$")

    def __init__(self, min_length: int = 5):
        self.min_length = min_length

    def rule_1_keyword(self, p: str) -> bool:
        pl = p.lower()
        return any(kw in pl for kw in self.KEYWORDS)

    def rule_2_quote_or_op(self, p: str) -> bool:
        return any(c in p for c in self.QUOTE_OPS)

    def rule_3_length(self, p: str) -> bool:
        return len(p.strip()) >= self.min_length

    def rule_4_not_benign(self, p: str) -> bool:
        return not self.BENIGN_LIKE.match(p.strip())

    def rule_5_relational(self, p: str) -> bool:
        return bool(self.RELATIONAL.search(p))

    def evaluate(self, payload: str) -> Tuple[float, List[bool]]:
        """Returns (pass_ratio, [bool_per_rule])."""
        if not payload or not isinstance(payload, str):
            return 0.0, [False] * 5

        results = [
            self.rule_1_keyword(payload),
            self.rule_2_quote_or_op(payload),
            self.rule_3_length(payload),
            self.rule_4_not_benign(payload),
            self.rule_5_relational(payload),
        ]
        ratio = sum(results) / len(results)
        return ratio, results

    def score(self, payload: str) -> float:
        return self.evaluate(payload)[0]
