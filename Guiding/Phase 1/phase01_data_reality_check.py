"""
Phase 01 — Data Reality Check
Phân loại lane cho từng payload_norm trong 15 shard CSV.
Output: data/phase01/phase01_data_reality.parquet + reports/
"""

import re
import json
import unicodedata
from pathlib import Path

import pandas as pd

# ── Paths ──────────────────────────────────────────────────────────────────────
ROOT = Path(__file__).parent.parent
SHARD_DIR = ROOT / "Asset" / "LabelData" / "Testing_1"
OUT_PARQUET = ROOT / "data" / "phase01" / "phase01_data_reality.parquet"
REPORT_DIR = ROOT / "reports"

SHARD_PATHS = sorted(SHARD_DIR.glob("final_dataset_*.csv"),
                     key=lambda p: int(re.search(r"(\d+)", p.stem).group(1)))

# ── Regex patterns ─────────────────────────────────────────────────────────────
RE_PLACEHOLDER = re.compile(r"__[A-Z_]+__")
RE_LITERAL_NUM = re.compile(r"\b\d+\b")
RE_LITERAL_STR = re.compile(r"'[^']{1,80}'")
RE_SQL_KW = re.compile(
    r"\b(SELECT|UNION|FROM|WHERE|AND|OR|INSERT|UPDATE|DELETE|DROP|CREATE|"
    r"ALTER|EXEC|EXECUTE|CAST|CONVERT|CONCAT|CHAR|CHR|ORDER|GROUP|HAVING|"
    r"LIMIT|OFFSET|INTO|VALUES|SET|JOIN|INNER|OUTER|LEFT|RIGHT|TABLE|"
    r"DATABASE|SCHEMA|USER|INFORMATION_SCHEMA|SYS\.|ALL_)\b",
    re.IGNORECASE,
)
RE_SQL_COMMENT = re.compile(r"(--|#|/\*)")
RE_QUOTE = re.compile(r"['\"]")
RE_URL_ENC = re.compile(r"%[0-9A-Fa-f]{2}")
RE_HTML_ENT = re.compile(r"&#?[a-zA-Z0-9]+;")
RE_KNOWN_FUNC = re.compile(
    r"\b(pg_sleep|sleep|waitfor\s+delay|extractvalue|updatexml|"
    r"load_file|benchmark|hex|unhex|ascii|char|ord|mid|substr|substring|"
    r"utl_inaddr|dbms_pipe|xp_cmdshell)\b",
    re.IGNORECASE,
)
RE_NON_PRINT = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f-\x9f]")


# ── Feature extraction ─────────────────────────────────────────────────────────
def extract_features(payload: str) -> dict:
    if not isinstance(payload, str):
        payload = "" if pd.isna(payload) else str(payload)

    length = len(payload)
    num_tokens = len(payload.split())

    placeholders = RE_PLACEHOLDER.findall(payload)
    has_placeholder = bool(placeholders)
    placeholder_types = ",".join(sorted(set(placeholders))) if placeholders else ""

    # "literal signal" = literal num/string outside placeholder positions
    stripped = RE_PLACEHOLDER.sub(" ", payload)
    has_literal_number = bool(RE_LITERAL_NUM.search(stripped))
    has_literal_string = bool(RE_LITERAL_STR.search(stripped))
    has_literal_signal = has_literal_number or has_literal_string

    has_sql_keyword = bool(RE_SQL_KW.search(payload))
    has_sql_comment = bool(RE_SQL_COMMENT.search(payload))
    has_quote = bool(RE_QUOTE.search(payload))
    has_url_encoding = bool(RE_URL_ENC.search(payload))
    has_html_entity = bool(RE_HTML_ENT.search(payload))
    has_encoding_artifact = has_url_encoding or has_html_entity
    has_known_function = bool(RE_KNOWN_FUNC.search(payload))
    has_non_printable = bool(RE_NON_PRINT.search(payload))

    return {
        "payload_length": length,
        "num_tokens": num_tokens,
        "has_placeholder": has_placeholder,
        "placeholder_types": placeholder_types,
        "has_literal_signal": has_literal_signal,
        "has_sql_keyword": has_sql_keyword,
        "has_sql_comment": has_sql_comment,
        "has_quote": has_quote,
        "has_url_encoding": has_url_encoding,
        "has_html_entity": has_html_entity,
        "has_encoding_artifact": has_encoding_artifact,
        "has_known_function": has_known_function,
        "has_non_printable": has_non_printable,
        "has_literal_number": has_literal_number,
        "has_literal_string": has_literal_string,
    }


def assign_lane(f: dict, payload: str) -> tuple[str, str, str]:
    length = f["payload_length"]

    # Lane M — malformed
    if length == 0 or f["has_non_printable"]:
        return "M", "high", "empty or non-printable content"
    if length < 3 and not f["has_sql_keyword"]:
        return "M", "medium", "too short, no sql keyword"

    # Lane X — mixed state
    if f["has_placeholder"] and f["has_literal_signal"]:
        return "X", "high", "placeholder + literal coexist"

    # Lane D — delexed
    if f["has_placeholder"]:
        confidence = "high" if not f["has_literal_signal"] else "medium"
        return "D", confidence, "placeholder found, no literal"

    # Lane R — raw/encoded
    if f["has_encoding_artifact"]:
        return "R", "high", "url/html encoding artifact detected"

    # Lane N — normalized (default)
    confidence = "high" if f["has_sql_keyword"] else "medium"
    reason = "no placeholder/encoding; sql keyword present" if f["has_sql_keyword"] else "no special markers"
    return "N", confidence, reason


def heuristic_scores(lane: str, f: dict) -> dict:
    recoverability = {"N": 1.0, "R": 0.8, "X": 0.3, "D": 0.3, "M": 0.0}[lane]
    relex_potential = lane in ("D", "X") and bool(f["placeholder_types"])
    db_eval_potential = lane in ("N", "R")
    return {
        "recoverability_score": recoverability,
        "relex_potential": relex_potential,
        "db_eval_potential": db_eval_potential,
    }


# ── Process all shards ─────────────────────────────────────────────────────────
def process_all() -> pd.DataFrame:
    records = []
    row_id = 0

    for path in SHARD_PATHS:
        print(f"  Reading {path.name} ...", flush=True)
        for chunk in pd.read_csv(path, chunksize=200_000, dtype=str,
                                  encoding="utf-8", on_bad_lines="skip"):
            if "payload_norm" not in chunk.columns:
                print(f"    WARNING: no payload_norm column in {path.name}, skipping")
                continue
            for src_idx, payload in enumerate(chunk["payload_norm"]):
                f = extract_features(payload)
                lane, confidence, reason = assign_lane(f, payload if isinstance(payload, str) else "")
                scores = heuristic_scores(lane, f)

                records.append({
                    "row_id": row_id,
                    "source_file": path.name,
                    "source_row_index": src_idx,
                    "payload_input": payload,
                    "payload_length": f["payload_length"],
                    "lane": lane,
                    "lane_confidence": confidence,
                    "lane_reason": reason,
                    "payload_state": lane,
                    "has_placeholder": f["has_placeholder"],
                    "placeholder_types": f["placeholder_types"],
                    "has_sql_keyword": f["has_sql_keyword"],
                    "has_known_function": f["has_known_function"],
                    "has_encoding_artifact": f["has_encoding_artifact"],
                    "has_literal_string": f["has_literal_string"],
                    "has_literal_number": f["has_literal_number"],
                    "recoverability_score": scores["recoverability_score"],
                    "relex_potential": scores["relex_potential"],
                    "db_eval_potential": scores["db_eval_potential"],
                })
                row_id += 1

    return pd.DataFrame(records)


# ── Audit stratified samples ───────────────────────────────────────────────────
def build_audit(df: pd.DataFrame, n: int = 100) -> pd.DataFrame:
    groups = {
        "random": df.sample(min(n, len(df)), random_state=42),
        "has_placeholder": df[df["has_placeholder"]].sample(min(n, df["has_placeholder"].sum()), random_state=42),
        "has_sql_keyword": df[df["has_sql_keyword"]].sample(min(n, df["has_sql_keyword"].sum()), random_state=42),
        "has_known_function": df[df["has_known_function"]].sample(min(n, df["has_known_function"].sum()), random_state=42),
        "has_encoding_artifact": df[df["has_encoding_artifact"]].sample(min(n, df["has_encoding_artifact"].sum()), random_state=42),
        "very_short": df[df["payload_length"] < 10].sample(min(n, (df["payload_length"] < 10).sum()), random_state=42),
        "very_long": df[df["payload_length"] > 200].sample(min(n, (df["payload_length"] > 200).sum()), random_state=42),
        "lane_X": df[df["lane"] == "X"].sample(min(n, (df["lane"] == "X").sum()), random_state=42),
    }
    parts = []
    for group_name, subset in groups.items():
        tagged = subset.copy()
        tagged["audit_group"] = group_name
        parts.append(tagged)
    return pd.concat(parts, ignore_index=True).drop_duplicates(subset=["row_id"])


# ── Reports ────────────────────────────────────────────────────────────────────
def write_lane_distribution(df: pd.DataFrame):
    total = len(df)
    dist = {"total": total}
    for lane in ["N", "R", "D", "X", "M"]:
        count = int((df["lane"] == lane).sum())
        dist[lane] = {"count": count, "pct": round(count / total * 100, 2)}
    out = REPORT_DIR / "01_lane_distribution.json"
    out.write_text(json.dumps(dist, indent=2, ensure_ascii=False), encoding="utf-8")
    return dist


def write_markdown_report(df: pd.DataFrame, dist: dict):
    total = dist["total"]
    lines = [
        "# 01 — Data Reality Check Report",
        "",
        f"**Total rows processed:** {total:,}",
        "",
        "## Lane Distribution",
        "",
        "| Lane | Name | Count | % |",
        "|---|---|---:|---:|",
    ]
    lane_names = {"N": "normalized-like", "R": "raw/encoded-like",
                  "D": "delexed-like", "X": "mixed-state", "M": "malformed"}
    for lane in ["N", "R", "D", "X", "M"]:
        d = dist[lane]
        lines.append(f"| {lane} | {lane_names[lane]} | {d['count']:,} | {d['pct']}% |")

    lines += ["", "## Examples per Lane", ""]
    for lane in ["N", "R", "D", "X", "M"]:
        subset = df[df["lane"] == lane]["payload_input"].dropna().head(3)
        lines.append(f"### Lane {lane} — {lane_names[lane]}")
        for ex in subset:
            lines.append(f"- `{str(ex)[:120]}`")
        lines.append("")

    lines += [
        "## Notes",
        "",
        "- `recoverability_score`, `relex_potential`, `db_eval_potential` are **soft heuristics only**.",
        "- Do NOT use them as hard gates before manual audit validation.",
        "- See `reports/01_audit_samples.csv` for stratified manual review.",
    ]

    out = REPORT_DIR / "01_data_reality_check.md"
    out.write_text("\n".join(lines), encoding="utf-8")


# ── Main ───────────────────────────────────────────────────────────────────────
def main():
    print("Phase 01 — Data Reality Check")
    print(f"Shards: {len(SHARD_PATHS)} files")

    OUT_PARQUET.parent.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)

    print("\nProcessing shards...")
    df = process_all()
    print(f"\nTotal rows: {len(df):,}")

    print("Writing parquet...")
    df.to_parquet(OUT_PARQUET, index=False)

    print("Building audit samples...")
    audit_df = build_audit(df)
    audit_df.to_csv(REPORT_DIR / "01_audit_samples.csv", index=False, encoding="utf-8")

    print("Writing lane distribution...")
    dist = write_lane_distribution(df)

    print("Writing markdown report...")
    write_markdown_report(df, dist)

    print("\n-- Lane Distribution ------------------------------------------")
    for lane in ["N", "R", "D", "X", "M"]:
        d = dist[lane]
        print(f"  {lane}: {d['count']:>8,}  ({d['pct']:5.1f}%)")
    print(f"  Total: {dist['total']:>8,}")
    print("\nDone. Outputs:")
    print(f"  {OUT_PARQUET}")
    print(f"  {REPORT_DIR / '01_data_reality_check.md'}")
    print(f"  {REPORT_DIR / '01_audit_samples.csv'}")
    print(f"  {REPORT_DIR / '01_lane_distribution.json'}")


if __name__ == "__main__":
    main()
