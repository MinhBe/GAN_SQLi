"""waf_oracle.py — Wrapper cho ModSecurity Docker container."""
import time

import requests


class WAFOracle:
    """Gọi ModSecurity Docker, trả anomaly_score và blocked status."""

    def __init__(
        self,
        url: str = "http://localhost:8080",
        timeout: float = 2.0,
        max_retries: int = 2,
    ):
        self.url = url
        self.timeout = timeout
        self.max_retries = max_retries
        self.session = requests.Session()

    def evaluate(self, payload: str) -> dict:
        """
        Returns dict với:
          - status_code: HTTP code
          - blocked: True nếu 403
          - anomaly_score: int (suy ra từ status code, ModSecurity stock không expose header)
        """
        if not payload or not isinstance(payload, str):
            return {"status_code": 0, "blocked": True, "anomaly_score": 999}

        for attempt in range(self.max_retries):
            try:
                resp = self.session.get(
                    self.url,
                    params={"id": payload},
                    timeout=self.timeout,
                )
                blocked = resp.status_code == 403
                anomaly_score = 10 if blocked else 0
                return {
                    "status_code": resp.status_code,
                    "blocked": blocked,
                    "anomaly_score": anomaly_score,
                }
            except (requests.Timeout, requests.ConnectionError) as e:
                if attempt == self.max_retries - 1:
                    return {
                        "status_code": 0,
                        "blocked": True,
                        "anomaly_score": 999,
                        "error": str(e),
                    }
                time.sleep(0.1)

    def close(self):
        self.session.close()


def waf_boundary_reward(anomaly_score: int, threshold: int = 5) -> float:
    """
    Boundary-aware reward — cao nhất khi anomaly_score gần threshold từ dưới.
    Payload sát ranh giới block/pass được thưởng nhiều hơn bypass dễ dàng.
    """
    if anomaly_score >= threshold:
        return -0.5
    distance = threshold - anomaly_score
    return 1.0 - (distance / threshold)
