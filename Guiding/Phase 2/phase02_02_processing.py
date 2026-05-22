"""
Phase 02 — Script 2: Minimal Processing
Input : Guiding/Phase 2/slice_payloads_raw.parquet
Output: Guiding/Phase 2/slice_payloads.parquet
Schema: slice_id, row_id, payload_input, lane,
        payload_working, payload_delex, dedup_hash, basic_cluster_key
"""

import re
import hashlib
import html
import urllib.parse
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
SRC  = HERE / "slice_payloads_raw.parquet"
OUT  = HERE / "slice_payloads.parquet"

# ── Delex patterns (v5 minimal) ────────────────────────────────────────────────
# Order matters: more specific first
DELEX_RULES = [
    # TIME literals
    (re.compile(r"'0:\d+:\d+'"), "__TIME__"),
    (re.compile(r"\b\d+\.\d+\b"), "__NUM__"),
    # String literals in quotes
    (re.compile(r"'[^']{0,80}'"), "__STR__"),
    (re.compile(r'"[^"]{0,80}"'), "__STR__"),
    # Bare identifiers that look like table/column names (>= 3 alpha chars, not SQL keyword)
    # We'll do a light version: just numeric literals
    (re.compile(r"\b\d+\b"), "__NUM__"),
    # Comment markers kept as-is (we detect them, not replace)
]

SQL_KEYWORDS = frozenset(re.split(r'\s+', """
    SELECT UNION FROM WHERE AND OR NOT IN EXISTS BETWEEN LIKE IS NULL
    INSERT UPDATE DELETE DROP CREATE ALTER EXEC EXECUTE CAST CONVERT
    ORDER GROUP HAVING LIMIT OFFSET INTO VALUES SET JOIN INNER OUTER
    LEFT RIGHT TABLE DATABASE SCHEMA USER INFORMATION_SCHEMA
    SYS ALL DISTINCT TOP ROWNUM FETCH FIRST ROWS ONLY
    CASE WHEN THEN ELSE END AS ON USING WITH RECURSIVE
""".strip()))

RE_COMMENT = re.compile(r"(--|#\s|/\*.*?\*/)", re.DOTALL)
RE_PLACEHOLDER = re.compile(r"__[A-Z_]+__")


def decode_lane_r(payload: str) -> str:
    try:
        decoded = urllib.parse.unquote(payload)
        decoded = html.unescape(decoded)
        # replace + as space (URL form encoding)
        decoded = decoded.replace("+", " ")
        return decoded
    except Exception:
        return payload


def basic_delex(payload: str) -> str:
    """Apply minimal delex: replace string/number literals with placeholders."""
    result = payload
    for pattern, placeholder in DELEX_RULES:
        result = pattern.sub(placeholder, result)
    # Collapse multiple consecutive __NUM__ or __STR__
    result = re.sub(r"(__NUM__\s*)+", "__NUM__ ", result)
    result = re.sub(r"(__STR__\s*)+", "__STR__ ", result)
    return result.strip()


def make_cluster_key(payload_working: str) -> str:
    """Simple structural key for dedup bucketing."""
    # Lowercase, remove literals, keep SQL structure
    key = payload_working.lower()
    key = re.sub(r"'[^']*'", "S", key)
    key = re.sub(r'"[^"]*"', "S", key)
    key = re.sub(r"\b\d+\b", "N", key)
    key = re.sub(r"\s+", " ", key).strip()
    return key[:100]


def process_row(row: pd.Series) -> dict:
    payload_input = row["payload_input"]
    lane = row["lane"]

    if not isinstance(payload_input, str):
        payload_input = ""

    # Step 1: decode if Lane R
    if lane == "R":
        payload_working = decode_lane_r(payload_input)
    elif lane in ("D", "X"):
        payload_working = payload_input  # already has placeholders
    else:
        payload_working = payload_input  # N: keep as-is

    # Step 2: delex
    if lane in ("D", "X"):
        # Already delexed — use as-is for payload_delex
        payload_delex = payload_working
    else:
        payload_delex = basic_delex(payload_working)

    # Step 3: dedup hash (on working payload)
    dedup_hash = hashlib.md5(payload_working.encode("utf-8", errors="replace")).hexdigest()

    # Step 4: cluster key
    basic_cluster_key = make_cluster_key(payload_working)

    return {
        "payload_working": payload_working,
        "payload_delex": payload_delex,
        "dedup_hash": dedup_hash,
        "basic_cluster_key": basic_cluster_key,
    }


def main():
    print("Phase 02 — Processing")
    print(f"Source: {SRC}")

    df = pd.read_parquet(SRC)
    print(f"Loaded: {len(df):,} rows")

    # Process
    print("Applying decode + delex...")
    processed = df.apply(process_row, axis=1, result_type="expand")
    df = pd.concat([df, processed], axis=1)

    # Exact dedup
    before = len(df)
    df = df.drop_duplicates(subset=["dedup_hash"]).reset_index(drop=True)
    after = len(df)
    print(f"Dedup: {before:,} -> {after:,} (removed {before-after:,})")

    # Assign slice_id
    df.insert(0, "slice_id", range(len(df)))

    # Select final columns
    cols = [
        "slice_id", "row_id", "payload_input", "lane",
        "payload_working", "payload_delex", "dedup_hash", "basic_cluster_key",
        # keep useful features from phase01
        "payload_length", "has_sql_keyword", "has_known_function",
        "has_encoding_artifact", "has_placeholder", "placeholder_types",
    ]
    available = [c for c in cols if c in df.columns]
    df = df[available]

    df.to_parquet(OUT, index=False)
    print(f"Saved: {OUT}")
    print(f"Final rows: {len(df):,}")
    print("\nLane distribution:")
    print(df["lane"].value_counts().to_string())


if __name__ == "__main__":
    main()
