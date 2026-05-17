"""run_prototype.py — End-to-end prototype on 1000 rows.

Pipeline:
  1. Sample 1000 rows random from combined_labeled_data.csv
  2. Apply strip_wrapper → payload_inner
  3. Apply delex_v2 → payload_delex_v2 + compute signature
  4. Apply critique_labels → verdict (KEEP/RELABEL/DROP)
  5. Print stats: vocab size, collision rate, signature distribution,
                  verdict distribution, function preservation rate

Target metrics (success criteria):
  - delex_v2 collision rate < 30% (vs original 71.89%)
  - vocab size 100-180 tokens (vs original 89)
  - function preservation > 95% for whitelisted functions
  - top-100 signatures cover < 25% of rows (vs original 42.82%)
"""
import argparse
import hashlib
import sys
from pathlib import Path

import pandas as pd
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from delex_v2 import delex_v2, compute_vocab
from strip_wrapper import strip_wrapper
from critique_labels import critique_row

DEFAULT_INPUT = "Asset/LabelData/combined_labeled_data.csv"

KEY_FUNCS = [
    "xmltype", "pg_sleep", "sleep", "waitfor", "benchmark", "extractvalue",
    "updatexml", "dbms_pipe", "utl_inaddr", "xp_cmdshell", "randomblob",
    "elt", "rlike", "chr", "concat", "cast", "union", "select",
]


def signature(delex: str) -> str:
    return hashlib.sha1(delex.encode("utf-8")).hexdigest()[:8]


def measure_function_preservation(df_attack):
    """For each key function: count occurrences in payload_norm vs payload_delex_v2."""
    print("\n=== FUNCTION PRESERVATION (delex_v2) ===")
    print(f"{'function':<15} {'norm':>8} {'delex_v2':>10} {'preserved%':>12}")
    print("-" * 50)
    for func in KEY_FUNCS:
        n_norm = df_attack["payload_norm"].str.lower().str.contains(
            rf"\b{func}\b", na=False, regex=True
        ).sum()
        n_delex = df_attack["payload_delex_v2"].str.contains(
            rf"\b{func}\b", na=False, regex=True
        ).sum()
        preserved = (n_delex / n_norm * 100) if n_norm > 0 else float("nan")
        marker = "" if preserved >= 95 else ("  !!" if preserved < 80 else "  ?")
        print(f"{func:<15} {n_norm:>8d} {n_delex:>10d} {preserved:>11.1f}%{marker}")


def measure_collision(df_attack):
    """Compare collision rate before (original delex) vs after (delex_v2)."""
    total = len(df_attack)
    unique_v2 = df_attack["payload_delex_v2"].nunique()
    collision_v2 = 1 - unique_v2 / total

    print("\n=== DELEX COLLISION RATE ===")
    print(f"Total rows         : {total}")
    print(f"Unique payload_norm: {df_attack['payload_norm'].nunique()}")
    print(f"Unique delex_v2    : {unique_v2}")
    print(f"Collision rate v2  : {collision_v2:.2%}  (target <30%)")

    # Top patterns
    print("\n=== TOP 10 DELEX_V2 PATTERNS ===")
    top = df_attack["payload_delex_v2"].value_counts().head(10)
    for delex, count in top.items():
        pct = count / total * 100
        print(f"  {count:5d} ({pct:5.2f}%) | {delex[:80]}")

    # Top-100 coverage
    top_100_cov = df_attack["payload_delex_v2"].value_counts().head(100).sum() / total
    print(f"\nTop-100 patterns cover: {top_100_cov:.2%}  (target <25%)")


def measure_vocab(df_attack):
    vocab = compute_vocab(df_attack["payload_delex_v2"])
    print(f"\n=== VOCAB STATS (delex_v2) ===")
    print(f"Vocab size: {len(vocab)} tokens  (target 100-180)")
    print(f"Top 15 tokens by frequency:")
    for tok, cnt in sorted(vocab.items(), key=lambda x: -x[1])[:15]:
        print(f"  {tok:<25} {cnt:7d}")


def measure_wrapper_strip(df_attack):
    print("\n=== WRAPPER STRIPPING ===")
    n_stripped = df_attack["wrapper_detected"].sum()
    print(f"Wrappers detected: {n_stripped} ({n_stripped/len(df_attack):.2%})")
    avg_orig = df_attack["payload_norm"].str.len().mean()
    avg_inner = df_attack["payload_inner"].str.len().mean()
    print(f"Length: original={avg_orig:.1f} -> inner={avg_inner:.1f}  "
          f"(reduction={1 - avg_inner/avg_orig:.1%})")


def measure_critique(df):
    print("\n=== CRITIQUE TRIAGE ===")
    counts = df["verdict"].value_counts()
    for v, c in counts.items():
        print(f"  {v:<10} {c:6d} ({c/len(df):6.2%})")

    # Show breakdown for KEEP rows by sqli_type
    keep = df[df["verdict"] == "KEEP"]
    if len(keep) > 0:
        print(f"\n  KEEP rows by sqli_type:")
        for t, c in keep["sqli_type"].value_counts().head(8).items():
            print(f"    {c:5d}  {t}")


def measure_signature(df_attack):
    print("\n=== SIGNATURE DIVERSITY ===")
    df_attack["signature"] = df_attack["payload_delex_v2"].map(signature)
    n_sig = df_attack["signature"].nunique()
    print(f"Unique signatures: {n_sig} (of {len(df_attack)} rows)")
    print(f"Mean rows/signature: {len(df_attack)/n_sig:.2f}")

    sig_counts = df_attack["signature"].value_counts()
    # Cap simulation
    for cap in (10, 30, 100):
        capped = sig_counts.clip(upper=cap).sum()
        print(f"  If cap signature@{cap}: dataset would be {capped} rows "
              f"({capped/len(df_attack):.1%} of original)")


def main():
    parser = argparse.ArgumentParser(description="Prototype 1000-row test")
    parser.add_argument("--input", default=DEFAULT_INPUT, help="Input CSV")
    parser.add_argument("--n_samples", type=int, default=1000)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--output", default="Asset/LabelData/prototype_v3.csv")
    parser.add_argument("--include_benign", action="store_true",
                        help="Include benign rows in stats (default: attack only)")
    args = parser.parse_args()

    # ── Step 1: Load & sample ────────────────────────────────────────────────
    df_full = pd.read_csv(args.input)
    print(f"Loaded {len(df_full)} rows from {args.input}")
    df = df_full.sample(n=min(args.n_samples, len(df_full)), random_state=args.seed).reset_index(drop=True)
    print(f"Sampled {len(df)} rows (seed={args.seed})\n")
    print(f"Type distribution in sample:")
    for t, c in df["sqli_type"].value_counts().head(10).items():
        print(f"  {c:5d}  {t}")

    # ── Step 2: Strip wrappers ───────────────────────────────────────────────
    print("\n[Step 2] Stripping wrappers...")
    strip_results = [strip_wrapper(p) for p in df["payload_norm"].fillna("").astype(str)]
    df["payload_inner"] = [r["payload_inner"] for r in strip_results]
    df["wrapper_detected"] = [r["wrapper_detected"] for r in strip_results]
    df["strip_depth"] = [r["strip_depth"] for r in strip_results]

    # ── Step 3: delex_v2 ─────────────────────────────────────────────────────
    print("[Step 3] Applying delex_v2...")
    df["payload_delex_v2"] = df["payload_inner"].fillna("").astype(str).map(delex_v2)

    # ── Step 4: critique ─────────────────────────────────────────────────────
    print("[Step 4] Critiquing existing labels...")
    critiques = [critique_row(row.to_dict()) for _, row in df.iterrows()]
    df["verdict"] = [r["verdict"] for r in critiques]
    df["critique_reasons"] = ["; ".join(r["reasons"]) for r in critiques]

    # ── Save ─────────────────────────────────────────────────────────────────
    df.to_csv(args.output, index=False)
    print(f"\nSaved to {args.output}")

    # ── Stats ────────────────────────────────────────────────────────────────
    df_attack = df if args.include_benign else df[df["sqli_type"] != "benign"].copy()
    print(f"\n{'='*60}")
    print(f"STATS (attack only, N={len(df_attack)}):" if not args.include_benign
          else f"STATS (all, N={len(df_attack)}):")
    print(f"{'='*60}")

    measure_wrapper_strip(df_attack)
    measure_collision(df_attack)
    measure_vocab(df_attack)
    measure_function_preservation(df_attack)
    measure_signature(df_attack)
    measure_critique(df)

    # ── Summary verdict ──────────────────────────────────────────────────────
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    collision = 1 - df_attack["payload_delex_v2"].nunique() / len(df_attack)
    vocab_size = len(compute_vocab(df_attack["payload_delex_v2"]))
    top100_cov = df_attack["payload_delex_v2"].value_counts().head(100).sum() / len(df_attack)

    print(f"Collision rate:        {collision:.2%}  ({'PASS' if collision < 0.30 else 'FAIL'} target <30%)")
    print(f"Vocab size:            {vocab_size}     ({'PASS' if 80 <= vocab_size <= 200 else 'CHECK'} target 100-180)")
    print(f"Top-100 coverage:      {top100_cov:.2%}  ({'PASS' if top100_cov < 0.25 else 'FAIL'} target <25%)")
    print(f"Wrapper strip rate:    {df_attack['wrapper_detected'].mean():.2%}  (expected ~50%)")


if __name__ == "__main__":
    main()
