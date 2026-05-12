"""smoke_waf.py — Test WAFOracle hoạt động."""
import sys
import time
import requests

WAF_URL = "http://localhost:8080"

KNOWN_ATTACKS = [
    "1' OR '1'='1",
    "1; DROP TABLE users--",
    "1 UNION SELECT password FROM users--",
    "<script>alert(1)</script>",
]
KNOWN_BENIGN = ["1", "admin", "hello world", "user@example.com"]


def test_payload(payload):
    try:
        resp = requests.get(WAF_URL, params={"id": payload}, timeout=5)
        return resp.status_code
    except Exception as e:
        return f"ERROR: {e}"


def main():
    print("=== WAF Smoke Test ===")
    print(f"Target: {WAF_URL}\n")

    attack_ok = 0
    print("[Attacks - expect 403]")
    for p in KNOWN_ATTACKS:
        code = test_payload(p)
        ok = "OK" if code == 403 else "FAIL"
        if code == 403:
            attack_ok += 1
        print(f"  [{ok}] {code} | {p[:50]}")

    benign_ok = 0
    print("\n[Benign - expect 200]")
    for p in KNOWN_BENIGN:
        code = test_payload(p)
        ok = "OK" if code == 200 else "WARN"
        if code == 200:
            benign_ok += 1
        print(f"  [{ok}] {code} | {p[:50]}")

    print("\n[Latency test - 20 calls]")
    start = time.time()
    for _ in range(20):
        test_payload("test")
    elapsed = time.time() - start
    ms_per_call = elapsed / 20 * 1000
    print(f"  20 calls: {elapsed:.2f}s ({ms_per_call:.1f}ms/call)")
    latency_ok = ms_per_call < 200

    print(f"\n=== Results ===")
    print(f"  Attack block rate: {attack_ok}/{len(KNOWN_ATTACKS)}")
    print(f"  Benign pass rate:  {benign_ok}/{len(KNOWN_BENIGN)}")
    print(f"  Latency OK (<200ms): {latency_ok} ({ms_per_call:.1f}ms)")

    if attack_ok < len(KNOWN_ATTACKS):
        print("\nWARN: Some attacks not blocked — check CRS paranoia level")
    if not latency_ok:
        print("WARN: High latency — may impact Phase 2 WAF reward speed")


if __name__ == "__main__":
    main()
