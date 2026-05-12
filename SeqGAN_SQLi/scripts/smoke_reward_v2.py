"""smoke_reward_v2.py — Smoke test CompositeRewardV2 (WAF optional)."""
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from SeqGAN_SQLi.src.reward_v2 import CompositeRewardV2

TEST_PAYLOADS = [
    ("1", "trivial integer"),
    ("admin", "benign string"),
    ("1 OR 1=1", "classic OR attack"),
    ("1' OR '1'='1", "quoted SQLi"),
    ("1 UNION SELECT password FROM users", "union attack"),
    ("--", "comment only"),
    ("asdf garbage @#", "non-SQL noise"),
    ("1 AND SLEEP(5)", "time-based"),
    ("1; DROP TABLE users--", "stacked query"),
]


def test_phase(phase: str, use_waf: bool):
    print(f"\n=== Phase: {phase} | WAF: {use_waf} ===")
    r = CompositeRewardV2(phase=phase, use_waf=use_waf)
    print(f"Weights: {r.weights}")
    rewards = []
    for payload, desc in TEST_PAYLOADS:
        t0 = time.time()
        reward = r(payload)
        ms = (time.time() - t0) * 1000
        rewards.append(reward)
        print(f"  [{reward:+.3f}] ({ms:5.1f}ms) {desc}")

    print(f"Stats: {r.get_stats()}")

    attack_rewards = [rewards[i] for i in [2, 3, 4, 7, 8]]
    noise_rewards = [rewards[i] for i in [0, 1, 5, 6]]
    avg_attack = sum(attack_rewards) / len(attack_rewards)
    avg_noise = sum(noise_rewards) / len(noise_rewards)
    print(f"  avg attack reward: {avg_attack:+.3f}  avg noise reward: {avg_noise:+.3f}")
    if avg_attack > avg_noise:
        print("  PASS: attacks rewarded more than noise")
    else:
        print("  WARN: attacks not separated from noise")

    r.close()


if __name__ == "__main__":
    test_phase("warmup", use_waf=False)

    import sys
    if "--waf" in sys.argv:
        test_phase("adversarial", use_waf=True)
        test_phase("refinement", use_waf=True)
    else:
        print("\n(Skip WAF phases — pass --waf to test with ModSecurity Docker)")
