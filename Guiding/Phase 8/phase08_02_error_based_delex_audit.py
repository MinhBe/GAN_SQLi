# -*- coding: utf-8 -*-
"""
Phase 08 - Script 2: audit error_based signatures before and after delex.

The report is aggregate-only and omits raw payload text. It answers whether
the current delex representation preserves error-based SQLi signatures.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow.parquet as pq


if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


PHASE_DIR = Path(__file__).resolve().parent
ROOT = PHASE_DIR.parent.parent
DEFAULT_SOURCE = ROOT / "Guiding" / "Phase 5" / "outputs" / "full" / "gold.parquet"
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"

SIGNATURE_PATTERNS: dict[str, re.Pattern[str]] = {
    "extractvalue": re.compile(r"\bextractvalue\b", re.IGNORECASE),
    "updatexml": re.compile(r"\bupdatexml\b", re.IGNORECASE),
    "cast": re.compile(r"\bcast\b", re.IGNORECASE),
    "convert": re.compile(r"\bconvert\b", re.IGNORECASE),
    "exp": re.compile(r"\bexp\s*\(", re.IGNORECASE),
    "floor_rand": re.compile(r"\bfloor\s*\(|\brand\s*\(", re.IGNORECASE),
    "group_by_having": re.compile(r"\bgroup\s+by\b|\bhaving\b", re.IGNORECASE),
    "xpath": re.compile(r"\bxpath\b|\bxml\b", re.IGNORECASE),
    "error_terms": re.compile(r"\berror\b|\bwarning\b|\bexception\b|\bduplicate\b", re.IGNORECASE),
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Audit error_based raw/delex signature preservation.")
    parser.add_argument("--source", type=Path, default=DEFAULT_SOURCE)
    parser.add_argument("--raw-col", default="payload_working")
    parser.add_argument("--delex-col", default="payload_delex_v5")
    parser.add_argument("--cond-col", default="technique_primary")
    parser.add_argument("--quality-col", default="quality_band")
    parser.add_argument("--needs-ai-col", default="needs_ai")
    parser.add_argument("--technique", default="error_based")
    parser.add_argument("--batch-size", type=int, default=100000)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--sample-size", type=int, default=50)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--report-name", default="08_error_based_delex_audit.md")
    parser.add_argument("--json-name", default="08_error_based_delex_audit.json")
    return parser.parse_args()


def as_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value)


def payload_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="replace")).hexdigest()[:20]


def pct(num: int, den: int) -> float:
    return num / den if den else 0.0


def signature_hits(text: str) -> set[str]:
    return {name for name, pattern in SIGNATURE_PATTERNS.items() if pattern.search(text)}


def load_columns(path: Path, args: argparse.Namespace) -> list[str]:
    names = set(pq.ParquetFile(path).schema_arrow.names)
    required = [args.raw_col, args.delex_col, args.cond_col]
    missing = [name for name in required if name not in names]
    if missing:
        raise KeyError(f"{path} missing required columns: {missing}")
    optional = [args.quality_col, args.needs_ai_col, "db_family", "confidence_score"]
    return required + [name for name in optional if name in names and name not in required]


def iter_error_batches(path: Path, args: argparse.Namespace):
    columns = load_columns(path, args)
    seen = 0
    parquet = pq.ParquetFile(path)
    for batch in parquet.iter_batches(batch_size=args.batch_size, columns=columns):
        df = batch.to_pandas()
        if args.limit is not None:
            remaining = args.limit - seen
            if remaining <= 0:
                break
            df = df.head(remaining)
        seen += len(df)

        for col in [args.raw_col, args.delex_col, args.cond_col]:
            df[col] = df[col].map(as_text)
        mask = df[args.cond_col].eq(args.technique)
        if args.quality_col in df.columns:
            mask &= df[args.quality_col].map(as_text).str.lower().eq("gold")
        if args.needs_ai_col in df.columns:
            mask &= ~df[args.needs_ai_col].fillna(False).astype(bool)
        filtered = df.loc[mask].reset_index(drop=True)
        if not filtered.empty:
            yield filtered
        if args.limit is not None and seen >= args.limit:
            break


def audit(args: argparse.Namespace) -> dict[str, Any]:
    started = time.time()
    total = Counter()
    raw_sig_counts: Counter[str] = Counter()
    delex_sig_counts: Counter[str] = Counter()
    lost_sig_counts: Counter[str] = Counter()
    sample_rows: list[dict[str, Any]] = []

    for df in iter_error_batches(args.source, args):
        for _, row in df.iterrows():
            raw = as_text(row[args.raw_col])
            delex = as_text(row[args.delex_col])
            raw_hits = signature_hits(raw)
            delex_hits = signature_hits(delex)
            lost_hits = raw_hits - delex_hits

            total["rows"] += 1
            if raw_hits:
                total["raw_has_signature"] += 1
            if delex_hits:
                total["delex_has_signature"] += 1
            if raw_hits and not delex_hits:
                total["raw_signature_lost_all"] += 1
            if lost_hits:
                total["raw_signature_lost_any"] += 1
            raw_sig_counts.update(raw_hits)
            delex_sig_counts.update(delex_hits)
            lost_sig_counts.update(lost_hits)

            if len(sample_rows) < args.sample_size:
                sample_rows.append(
                    {
                        "raw_hash": payload_hash(raw),
                        "delex_hash": payload_hash(delex),
                        "raw_len": len(raw),
                        "delex_len": len(delex),
                        "raw_signatures": sorted(raw_hits),
                        "delex_signatures": sorted(delex_hits),
                        "lost_signatures": sorted(lost_hits),
                        "db_family": as_text(row.get("db_family", "")),
                        "confidence_score": as_text(row.get("confidence_score", "")),
                    }
                )

        if total["rows"] and total["rows"] % max(args.batch_size, 1) == 0:
            elapsed = max(time.time() - started, 1e-6)
            print(f"error_based rows={total['rows']:,} rate={total['rows'] / elapsed:.0f}/s", flush=True)

    raw_rate = pct(total["raw_has_signature"], total["rows"])
    delex_rate = pct(total["delex_has_signature"], total["rows"])
    lost_all_rate = pct(total["raw_signature_lost_all"], total["raw_has_signature"])
    decision = "keep_current_representation"
    if raw_rate < 0.50:
        decision = "inspect_labels_or_expand_signature_schema"
    if raw_rate >= 0.50 and (delex_rate < raw_rate * 0.75 or lost_all_rate >= 0.20):
        decision = "build_delex_v2_preserving_error_function_names"

    return {
        "source": str(args.source),
        "technique": args.technique,
        "rows": total["rows"],
        "raw_signature_rate": raw_rate,
        "delex_signature_rate": delex_rate,
        "lost_all_signature_rate_given_raw_signature": lost_all_rate,
        "lost_any_signature_rate_given_raw_signature": pct(total["raw_signature_lost_any"], total["raw_has_signature"]),
        "raw_signature_counts": dict(raw_sig_counts),
        "delex_signature_counts": dict(delex_sig_counts),
        "lost_signature_counts": dict(lost_sig_counts),
        "sample_hash_audit": sample_rows,
        "decision": decision,
    }


def write_outputs(args: argparse.Namespace, result: dict[str, Any]) -> None:
    args.report_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.report_dir / args.json_name
    md_path = args.report_dir / args.report_name
    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# 08 - Error-Based Delex Audit",
        "",
        "Scope: aggregate signature preservation audit for `error_based` rows. Raw payloads are intentionally omitted.",
        "",
        "## Summary",
        "",
        f"- Source: `{result['source']}`",
        f"- Rows: `{result['rows']:,}`",
        f"- Raw signature rate: `{result['raw_signature_rate']:.4f}`",
        f"- Delex signature rate: `{result['delex_signature_rate']:.4f}`",
        f"- Lost-all rate given raw signature: `{result['lost_all_signature_rate_given_raw_signature']:.4f}`",
        f"- Decision: `{result['decision']}`",
        "",
        "## Signature Counts",
        "",
        "| Signature | Raw Count | Delex Count | Lost Count |",
        "|---|---:|---:|---:|",
    ]
    names = sorted(set(result["raw_signature_counts"]) | set(result["delex_signature_counts"]) | set(result["lost_signature_counts"]))
    for name in names:
        lines.append(
            f"| {name} | {result['raw_signature_counts'].get(name, 0):,} | {result['delex_signature_counts'].get(name, 0):,} | {result['lost_signature_counts'].get(name, 0):,} |"
        )

    lines.extend(
        [
            "",
            "## Sample Hash Audit",
            "",
            "| Raw Hash | Delex Hash | Raw Sigs | Delex Sigs | Lost Sigs |",
            "|---|---|---|---|---|",
        ]
    )
    for row in result["sample_hash_audit"]:
        lines.append(
            "| {raw_hash} | {delex_hash} | {raw} | {delex} | {lost} |".format(
                raw_hash=row["raw_hash"],
                delex_hash=row["delex_hash"],
                raw=", ".join(row["raw_signatures"]) or "none",
                delex=", ".join(row["delex_signatures"]) or "none",
                lost=", ".join(row["lost_signatures"]) or "none",
            )
        )

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- `build_delex_v2_preserving_error_function_names` means error-based signatures are being erased enough that training/evaluation on the current representation is unsafe.",
            "- `inspect_labels_or_expand_signature_schema` means the raw rows themselves do not match the current error-based signature schema often enough; label audit comes before model work.",
            "- `keep_current_representation` means current delex is not the primary blocker for this signature set, though evaluator calibration is still required.",
            "",
        ]
    )
    md_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"report={md_path}")
    print(f"json={json_path}")


def main() -> None:
    args = parse_args()
    result = audit(args)
    write_outputs(args, result)


if __name__ == "__main__":
    main()

