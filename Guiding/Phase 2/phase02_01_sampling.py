"""
Phase 02 — Script 1: Stratified Bucket Sampling
Input : data/phase01/phase01_data_reality.parquet
Output: Guiding/Phase 2/slice_payloads_raw.parquet  (~40k rows)
"""

from pathlib import Path
import pandas as pd
import numpy as np

ROOT = Path(__file__).parent.parent.parent  # GAN_SQLi root
SRC  = ROOT / "Guiding" / "Phase 1" / "phase01_data_reality.parquet"
OUT  = Path(__file__).parent / "slice_payloads_raw.parquet"

TARGET = 40_000
SEED   = 42

LANE_BUDGET = {
    "N": 37_000,
    "R":  2_000,
    "D":    500,
    "X":    400,
    "M":      0,  # không dùng train
}

def length_bucket(length: pd.Series) -> pd.Series:
    return pd.cut(length,
                  bins=[0, 30, 80, 200, 9999],
                  labels=["short", "medium", "long", "very_long"])

def make_bucket_key(df: pd.DataFrame) -> pd.Series:
    lb = length_bucket(df["payload_length"]).astype(str)
    kw = df["has_sql_keyword"].map({True: "kw1", False: "kw0"})
    fn = df["has_known_function"].map({True: "fn1", False: "fn0"})
    return lb + "|" + kw + "|" + fn

def sample_lane(df: pd.DataFrame, lane: str, n: int, rng: np.random.Generator) -> pd.DataFrame:
    sub = df[df["lane"] == lane].copy()
    if len(sub) == 0 or n == 0:
        return pd.DataFrame()

    sub["_bucket"] = make_bucket_key(sub)
    buckets = sub["_bucket"].unique()

    per_bucket = max(1, n // len(buckets))
    parts = []
    for b in buckets:
        bdf = sub[sub["_bucket"] == b]
        k = min(per_bucket, len(bdf))
        parts.append(bdf.sample(k, random_state=int(rng.integers(1e6))))

    result = pd.concat(parts, ignore_index=True)

    # top-up or trim to exact n
    if len(result) < n:
        remaining = sub[~sub.index.isin(result.index)]
        extra = min(n - len(result), len(remaining))
        if extra > 0:
            result = pd.concat([result, remaining.sample(extra, random_state=int(rng.integers(1e6)))],
                               ignore_index=True)
    elif len(result) > n:
        result = result.sample(n, random_state=int(rng.integers(1e6)))

    result = result.drop(columns=["_bucket"])
    return result


def main():
    print("Phase 02 — Sampling")
    print(f"Source: {SRC}")

    df = pd.read_parquet(SRC)
    print(f"Total rows loaded: {len(df):,}")
    print("Lane distribution in source:")
    print(df["lane"].value_counts().to_string())

    rng = np.random.default_rng(SEED)
    parts = []
    for lane, n in LANE_BUDGET.items():
        if n == 0:
            print(f"  Lane {lane}: skipped (M excluded)")
            continue
        sampled = sample_lane(df, lane, n, rng)
        print(f"  Lane {lane}: target={n:,}  got={len(sampled):,}")
        parts.append(sampled)

    result = pd.concat(parts, ignore_index=True)
    result = result.sample(frac=1, random_state=SEED).reset_index(drop=True)  # shuffle

    print(f"\nFinal slice: {len(result):,} rows")
    print("Lane distribution in slice:")
    print(result["lane"].value_counts().to_string())

    OUT.parent.mkdir(parents=True, exist_ok=True)
    result.to_parquet(OUT, index=False)
    print(f"\nSaved: {OUT}")


if __name__ == "__main__":
    main()
