"""strip_wrapper.py — Detect and strip wrapper patterns from SQLi payloads.

53.64% of attack payloads in combined_labeled_data.csv use the wrapper:
   select * from users WHERE username = "...actual payload..."

This wrapper collapses all 9,559 wrapped payloads into the same delex form
→ mode collapse.

This script strips the wrapper to expose the INNER payload for GAN training.

Reference: references/wrapper_patterns.md
"""
import re
from typing import Optional

# Wrapper patterns (case-insensitive)
RE_WRAPPER_DQ = re.compile(
    r'^\s*select\s+\*\s+from\s+\w+\s+where\s+\w+\s*=\s*"(.*)"\s*$',
    re.IGNORECASE | re.DOTALL,
)
RE_WRAPPER_SQ = re.compile(
    r"^\s*select\s+\*\s+from\s+\w+\s+where\s+\w+\s*=\s*'(.*)'\s*$",
    re.IGNORECASE | re.DOTALL,
)

# Multi-clause wrappers: `select ... where col = "X" OR col = "Y"`
RE_WRAPPER_MULTI_DQ = re.compile(
    r'^\s*select\s+\*\s+from\s+\w+\s+where\s+\w+\s*=\s*"([^"]+)"\s+(?:and|or)\s+\w+\s*=\s*"(.+?)"\s*$',
    re.IGNORECASE | re.DOTALL,
)

MIN_INNER_LEN = 5  # don't strip if inner < 5 chars (probably empty wrapper)
MAX_RECURSION_DEPTH = 3  # recursively strip nested wrappers


def _strip_once(payload: str) -> Optional[str]:
    """Try to strip 1 layer of wrapper. Returns inner or None if no wrapper found."""
    if not payload or not payload.strip():
        return None

    # Try multi-clause wrapper first (more specific)
    m = RE_WRAPPER_MULTI_DQ.match(payload)
    if m:
        a, b = m.group(1), m.group(2)
        # Return the longer, more suspicious-looking part
        candidate = a if len(a) > len(b) else b
        return candidate if len(candidate) >= MIN_INNER_LEN else None

    # Single-quote and double-quote wrappers
    for pattern in (RE_WRAPPER_DQ, RE_WRAPPER_SQ):
        m = pattern.match(payload)
        if m:
            inner = m.group(1)
            if len(inner) >= MIN_INNER_LEN:
                return inner
            return None

    return None


def strip_wrapper(payload: str) -> dict:
    """Strip wrappers recursively (up to MAX_RECURSION_DEPTH levels).

    Returns:
        {
            "payload_inner": str (stripped payload, or original if no wrapper),
            "wrapper_detected": bool,
            "strip_depth": int (number of layers stripped),
        }
    """
    if not isinstance(payload, str):
        return {"payload_inner": "", "wrapper_detected": False, "strip_depth": 0}

    current = payload
    depth = 0
    for _ in range(MAX_RECURSION_DEPTH):
        stripped = _strip_once(current)
        if stripped is None:
            break
        if stripped == current:
            break
        current = stripped
        depth += 1

    return {
        "payload_inner": current if current else payload,
        "wrapper_detected": depth > 0,
        "strip_depth": depth,
    }


def strip_wrapper_batch(payloads: list) -> list[dict]:
    return [strip_wrapper(p) for p in payloads]


# ── CLI ────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    import argparse
    import pandas as pd

    parser = argparse.ArgumentParser(description="Strip wrappers from SQLi payloads")
    parser.add_argument("--input", required=True, help="Input CSV with payload_norm")
    parser.add_argument("--output", required=True, help="Output CSV")
    parser.add_argument("--col_in", default="payload_norm")
    parser.add_argument("--col_out", default="payload_inner")
    args = parser.parse_args()

    df = pd.read_csv(args.input)
    results = strip_wrapper_batch(df[args.col_in].fillna("").astype(str).tolist())

    df[args.col_out] = [r["payload_inner"] for r in results]
    df["wrapper_detected"] = [r["wrapper_detected"] for r in results]
    df["strip_depth"] = [r["strip_depth"] for r in results]
    df.to_csv(args.output, index=False)

    n_wrapped = df["wrapper_detected"].sum()
    avg_inner_len = df[args.col_out].str.len().mean()
    avg_orig_len = df[args.col_in].fillna("").str.len().mean()

    print(f"Wrote {len(df)} rows to {args.output}")
    print(f"Wrappers detected: {n_wrapped} ({n_wrapped/len(df):.2%})")
    print(f"Average length: original={avg_orig_len:.1f} -> inner={avg_inner_len:.1f}")
    print(f"Length reduction: {(1 - avg_inner_len/avg_orig_len):.1%}")
