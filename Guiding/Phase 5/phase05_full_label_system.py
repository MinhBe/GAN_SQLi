# -*- coding: utf-8 -*-
"""
Phase 05 - Full Label System

Streaming, detector-only wrapper for the Phase 4 payload foundation.

Default contract:
  - Input:  Guiding/Phase 4/outputs/full/phase04_payload_foundation.parquet
  - Output: Guiding/Phase 5/outputs/full
  - Logs:   Guiding/Phase 5/logs
  - Report: Guiding/Phase 5/reports

Passing --limit without --out-dir switches the output directory to
Guiding/Phase 5/outputs/sanity so sanity runs do not overwrite full artifacts.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import math
import re
import sys
import time
from collections import Counter
from pathlib import Path
from typing import Any

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


if hasattr(sys.stdout, "buffer"):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
if hasattr(sys.stderr, "buffer"):
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")


PHASE_DIR = Path(__file__).resolve().parent
ROOT = PHASE_DIR.parent.parent
LABEL_SCRIPTS_DIR = ROOT / "Skill" / "label-sqli" / "scripts"
sys.path.insert(0, str(LABEL_SCRIPTS_DIR))

from cascade_labeler import label_payload  # noqa: E402


DEFAULT_INPUT = ROOT / "Guiding" / "Phase 4" / "outputs" / "full" / "phase04_payload_foundation.parquet"
DEFAULT_FULL_OUT_DIR = PHASE_DIR / "outputs" / "full"
DEFAULT_SANITY_OUT_DIR = PHASE_DIR / "outputs" / "sanity"
DEFAULT_LOG_DIR = PHASE_DIR / "logs"
DEFAULT_REPORT_DIR = PHASE_DIR / "reports"
SUMMARY_PATH = PHASE_DIR / "Tổng kết Phase 5.md"

INPUT_COLUMNS = [
    "row_id",
    "payload_working",
    "payload_delex_v5",
    "lane",
    "split",
    "near_dup_cluster_id",
    "delex_collision_key",
    "duplicate_count",
]

OUTPUT_COLUMNS = [
    "row_id",
    "payload_working",
    "payload_delex_v5",
    "lane",
    "split",
    "near_dup_cluster_id",
    "delex_collision_key",
    "duplicate_count",
    "is_sqli",
    "technique_primary",
    "sqli_type",
    "sqli_types",
    "script_sqli_type",
    "script_confidence",
    "db_engine",
    "db_family",
    "db_confidence",
    "confidence",
    "confidence_score",
    "confidence_band",
    "quality_band",
    "label_source",
    "label_mode",
    "is_complex",
    "low_confidence",
    "needs_ai",
    "payload_state",
    "obf_comment",
    "obf_case",
    "obf_encoding",
    "intent_secondary_multilabel",
    "syntax_validity",
    "conflict_flags",
    "review_priority",
    "review_reason",
    "label_sources_json",
    "verified_label_flag",
    "verified_by",
]

OUTPUT_SCHEMA = pa.schema(
    [
        ("row_id", pa.int64()),
        ("payload_working", pa.large_string()),
        ("payload_delex_v5", pa.large_string()),
        ("lane", pa.large_string()),
        ("split", pa.large_string()),
        ("near_dup_cluster_id", pa.large_string()),
        ("delex_collision_key", pa.large_string()),
        ("duplicate_count", pa.int64()),
        ("is_sqli", pa.int64()),
        ("technique_primary", pa.large_string()),
        ("sqli_type", pa.large_string()),
        ("sqli_types", pa.large_string()),
        ("script_sqli_type", pa.large_string()),
        ("script_confidence", pa.float64()),
        ("db_engine", pa.large_string()),
        ("db_family", pa.large_string()),
        ("db_confidence", pa.float64()),
        ("confidence", pa.float64()),
        ("confidence_score", pa.float64()),
        ("confidence_band", pa.large_string()),
        ("quality_band", pa.large_string()),
        ("label_source", pa.large_string()),
        ("label_mode", pa.large_string()),
        ("is_complex", pa.bool_()),
        ("low_confidence", pa.bool_()),
        ("needs_ai", pa.bool_()),
        ("payload_state", pa.large_string()),
        ("obf_comment", pa.float64()),
        ("obf_case", pa.float64()),
        ("obf_encoding", pa.float64()),
        ("intent_secondary_multilabel", pa.large_string()),
        ("syntax_validity", pa.large_string()),
        ("conflict_flags", pa.large_string()),
        ("review_priority", pa.int64()),
        ("review_reason", pa.large_string()),
        ("label_sources_json", pa.large_string()),
        ("verified_label_flag", pa.bool_()),
        ("verified_by", pa.large_string()),
    ]
)


SQL_SIGNAL_RE = re.compile(
    r"('|\bselect\b|\bunion\b|\bwhere\b|\band\b|\bor\b|\bsleep\b|\bpg_sleep\b|"
    r"\bwaitfor\b|\bbenchmark\b|\bextractvalue\b|\bupdatexml\b|--|#|/\*)",
    re.IGNORECASE,
)
QUERY_START_RE = re.compile(r"^\s*(select|insert|update|delete|with|drop|alter|create)\b", re.IGNORECASE)
ENCODED_RE = re.compile(r"(%[0-9a-fA-F]{2}|\\x[0-9a-fA-F]{2}|0x[0-9a-fA-F]{2,}|char\s*\()", re.IGNORECASE)
HTTP_PARAM_RE = re.compile(r"(^|[?&])[^=&\s]+=[^&\s]+")
TIME_SIGNAL_RE = re.compile(r"\b(sleep|pg_sleep|waitfor\s+delay|benchmark|dbms_pipe\.receive_message)\b", re.IGNORECASE)
UNION_SIGNAL_RE = re.compile(r"\bunion\b.{0,80}\bselect\b", re.IGNORECASE | re.DOTALL)
ERROR_SIGNAL_RE = re.compile(
    r"\b(extractvalue|updatexml|xmltype|utl_inaddr|floor\s*\(|exp\s*\(|"
    r"cast\s*\(|convert\s*\(|to_number\s*\()",
    re.IGNORECASE,
)

ENGINE_PATTERNS = {
    "mysql": re.compile(r"\b(sleep|benchmark|extractvalue|updatexml|information_schema|load_file)\b", re.IGNORECASE),
    "postgres": re.compile(r"\b(pg_sleep|pg_catalog|current_database|generate_series)\b|::", re.IGNORECASE),
    "mssql": re.compile(r"\b(waitfor\s+delay|xp_cmdshell|sysobjects|sys\.|@@version)\b", re.IGNORECASE),
    "oracle": re.compile(r"\b(dbms_pipe|xmltype|utl_inaddr|dual|v\$|all_tables|rownum)\b", re.IGNORECASE),
    "sqlite": re.compile(r"\b(sqlite_master|sqlite_version|randomblob)\b", re.IGNORECASE),
}

INTENT_PATTERNS = {
    "metadata_enumeration": re.compile(
        r"\b(information_schema|pg_catalog|sqlite_master|sysobjects|all_tables|v\$|table_name|column_name)\b",
        re.IGNORECASE,
    ),
    "db_fingerprint": re.compile(
        r"\b(version\s*\(|@@version|sqlite_version|current_database|database\s*\(|user\s*\(|current_user)\b",
        re.IGNORECASE,
    ),
    "data_exfiltration": re.compile(
        r"\b(union\b.{0,80}\bselect|group_concat|concat\s*\(|load_file|outfile)\b",
        re.IGNORECASE | re.DOTALL,
    ),
    "privilege_probe": re.compile(r"\b(xp_cmdshell|is_srvrolemember|dba_users|user_privileges)\b", re.IGNORECASE),
    "destructive_action": re.compile(r"\b(drop|truncate|delete\s+from|alter\s+table|shutdown)\b", re.IGNORECASE),
    "auth_bypass": re.compile(
        r"(\bor\b|\band\b)\s+['\"]?\d+['\"]?\s*=\s*['\"]?\d+|"
        r"(\bor\b|\band\b)\s+['\"][^'\"]+['\"]\s*=\s*['\"][^'\"]+['\"]",
        re.IGNORECASE,
    ),
    "obfuscation_only": re.compile(r"(/\*.*?\*/|%[0-9a-fA-F]{2}|\\x[0-9a-fA-F]{2})", re.IGNORECASE | re.DOTALL),
}


def as_text(value: Any) -> str:
    if value is None:
        return ""
    try:
        if isinstance(value, float) and math.isnan(value):
            return ""
        if pd.isna(value):
            return ""
    except (TypeError, ValueError):
        pass
    return str(value)


def as_int(value: Any, default: int = 0) -> int:
    try:
        if value is None or pd.isna(value):
            return default
        return int(value)
    except (TypeError, ValueError):
        return default


def as_float(value: Any, default: float = 0.0) -> float:
    try:
        if value is None or pd.isna(value):
            return default
        return float(value)
    except (TypeError, ValueError):
        return default


def stable_bucket(value: Any, modulo: int = 100) -> int:
    text = as_text(value)
    digest = hashlib.blake2b(text.encode("utf-8", errors="ignore"), digest_size=8).digest()
    return int.from_bytes(digest, "big") % modulo


def db_family(engine: str) -> str:
    return {
        "mysql": "mysql_like",
        "postgres": "postgresql",
        "oracle": "oracle",
        "mssql": "mssql",
        "sqlite": "sqlite_or_generic",
        "unknown": "unknown",
    }.get(engine or "unknown", "unknown")


def engine_signal_families(payload: str) -> set[str]:
    return {family for family, pattern in ENGINE_PATTERNS.items() if pattern.search(payload)}


def infer_intents(payload: str, technique: str) -> str:
    if technique == "benign":
        return "none"

    intents = [name for name, pattern in INTENT_PATTERNS.items() if pattern.search(payload)]
    if technique == "union_based" and "data_exfiltration" not in intents:
        intents.append("data_exfiltration")
    if technique == "time_blind" and "db_fingerprint" not in intents:
        intents.append("db_fingerprint")

    if not intents:
        intents.append("unknown" if technique == "unknown" else "none")
    return "|".join(sorted(set(intents)))


def classify_syntax(payload: str, technique: str) -> str:
    text = as_text(payload)
    low = text.lower()
    if not low.strip():
        return "unknown"
    if HTTP_PARAM_RE.search(text) and ("&" in text or "?" in text):
        return "http_param"
    if ENCODED_RE.search(text):
        return "encoded_payload"
    if QUERY_START_RE.search(text):
        return "valid_query"
    if SQL_SIGNAL_RE.search(text) or "__" in text:
        if low.count("'") % 2 == 1 and ("--" not in low and "#" not in low):
            return "malformed"
        return "valid_fragment"
    if technique == "benign":
        return "non_sql"
    return "unknown"


def detect_conflicts(payload: str, result: dict[str, Any]) -> str:
    technique = as_text(result.get("sqli_type")) or "unknown"
    engine = as_text(result.get("db_engine")) or "unknown"
    confidence = as_float(result.get("confidence"))
    flags: list[str] = []

    families = engine_signal_families(payload)
    if len(families) > 1:
        flags.append("multi_db_signal")

    expected_family = db_family(engine)
    expected_signal = {
        "mysql_like": "mysql",
        "postgresql": "postgres",
        "mssql": "mssql",
        "oracle": "oracle",
        "sqlite_or_generic": "sqlite",
    }.get(expected_family)
    if expected_signal and families and expected_signal not in families and technique != "benign":
        flags.append("engine_signal_mismatch")

    if technique == "time_blind" and not TIME_SIGNAL_RE.search(payload):
        flags.append("weak_time_signal")
    if technique == "union_based" and not UNION_SIGNAL_RE.search(payload):
        flags.append("weak_union_signal")
    if technique == "error_based" and not ERROR_SIGNAL_RE.search(payload):
        flags.append("weak_error_signal")
    if technique == "benign" and SQL_SIGNAL_RE.search(payload):
        flags.append("benign_with_sql_signal")
    if technique == "unknown":
        flags.append("unresolved_label")
    if result.get("is_sqli") and confidence < 0.50:
        flags.append("low_confidence_positive")

    return "|".join(sorted(set(flags))) if flags else "none"


def review_priority_and_reason(
    result: dict[str, Any],
    conflict_flags: str,
    split: str,
    duplicate_count: int,
) -> tuple[int, str]:
    score = 0
    reasons: list[str] = []
    confidence = as_float(result.get("confidence"))
    max_obf = max(
        as_float(result.get("obf_comment")),
        as_float(result.get("obf_case")),
        as_float(result.get("obf_encoding")),
    )

    if bool(result.get("needs_ai")):
        score += 60
        reasons.append("needs_ai")
    if confidence < 0.50:
        score += 25
        reasons.append("very_low_confidence")
    elif confidence < 0.70:
        score += 15
        reasons.append("low_confidence")
    if conflict_flags != "none":
        score += 25
        reasons.append("conflict")
    if duplicate_count >= 100:
        score += 10
        reasons.append("large_duplicate_cluster")
    if max_obf >= 0.60:
        score += 10
        reasons.append("obfuscation")
    if split == "verified_candidate":
        score += 15
        reasons.append("verified_candidate_split")

    if not reasons:
        return 0, "none"
    return min(score, 100), "|".join(sorted(set(reasons)))


def quality_band(result: dict[str, Any], conflict_flags: str) -> str:
    if conflict_flags != "none" or bool(result.get("needs_ai")) or not result.get("sqli_type"):
        return "bronze"
    confidence = as_float(result.get("confidence"))
    if confidence >= 0.85:
        return "gold"
    if confidence >= 0.70:
        return "silver"
    return "bronze"


def label_record(row: dict[str, Any], payload_col: str) -> dict[str, Any]:
    payload = as_text(row.get(payload_col))
    result = label_payload(payload)

    technique = as_text(result.get("sqli_type")) or "unknown"
    engine = as_text(result.get("db_engine")) or "unknown"
    confidence = as_float(result.get("confidence"))
    split = as_text(row.get("split")) or "unknown"
    duplicate_count = as_int(row.get("duplicate_count"), 1)
    conflict_flags = detect_conflicts(payload, result)
    review_priority, review_reason = review_priority_and_reason(result, conflict_flags, split, duplicate_count)
    qband = quality_band(result, conflict_flags)

    source_obj = {
        "mode": "detector_only",
        "cascade_label_source": as_text(result.get("label_source")) or "unknown",
        "script_sqli_type": technique,
        "script_confidence": round(confidence, 4),
        "payload_state": as_text(result.get("payload_state")) or "unknown",
        "needs_ai": bool(result.get("needs_ai")),
    }

    return {
        "row_id": as_int(row.get("row_id")),
        "payload_working": as_text(row.get("payload_working")),
        "payload_delex_v5": as_text(row.get("payload_delex_v5")),
        "lane": as_text(row.get("lane")) or "unknown",
        "split": split,
        "near_dup_cluster_id": as_text(row.get("near_dup_cluster_id")),
        "delex_collision_key": as_text(row.get("delex_collision_key")),
        "duplicate_count": duplicate_count,
        "is_sqli": as_int(result.get("is_sqli")),
        "technique_primary": technique,
        "sqli_type": technique,
        "sqli_types": as_text(result.get("sqli_types")) or technique,
        "script_sqli_type": as_text(result.get("script_sqli_type")) or technique,
        "script_confidence": as_float(result.get("script_confidence"), confidence),
        "db_engine": engine,
        "db_family": db_family(engine),
        "db_confidence": as_float(result.get("db_confidence")),
        "confidence": confidence,
        "confidence_score": confidence,
        "confidence_band": as_text(result.get("tier")) or qband,
        "quality_band": qband,
        "label_source": as_text(result.get("label_source")) or "unknown",
        "label_mode": "detector_only",
        "is_complex": bool(result.get("is_complex")),
        "low_confidence": bool(result.get("low_confidence")),
        "needs_ai": bool(result.get("needs_ai")),
        "payload_state": as_text(result.get("payload_state")) or "unknown",
        "obf_comment": as_float(result.get("obf_comment")),
        "obf_case": as_float(result.get("obf_case")),
        "obf_encoding": as_float(result.get("obf_encoding")),
        "intent_secondary_multilabel": infer_intents(payload, technique),
        "syntax_validity": classify_syntax(payload, technique),
        "conflict_flags": conflict_flags,
        "review_priority": review_priority,
        "review_reason": review_reason,
        "label_sources_json": json.dumps(source_obj, ensure_ascii=False, sort_keys=True),
        "verified_label_flag": False,
        "verified_by": "",
    }


def label_dataframe(df: pd.DataFrame, payload_col: str) -> pd.DataFrame:
    records: list[dict[str, Any]] = []
    rows = df.to_dict(orient="records")
    for row in rows:
        records.append(label_record(row, payload_col))
    return pd.DataFrame.from_records(records, columns=OUTPUT_COLUMNS)


class ParquetSink:
    def __init__(self, path: Path):
        self.path = path
        self.writer: pq.ParquetWriter | None = None
        self.rows = 0

    def write(self, df: pd.DataFrame) -> None:
        if df.empty:
            return
        table = pa.Table.from_pandas(df[OUTPUT_COLUMNS], schema=OUTPUT_SCHEMA, preserve_index=False)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.writer is None:
            self.writer = pq.ParquetWriter(self.path, OUTPUT_SCHEMA, compression="zstd")
        self.writer.write_table(table)
        self.rows += len(df)

    def close(self) -> None:
        if self.writer is not None:
            self.writer.close()
            self.writer = None
        elif not self.path.exists():
            self.path.parent.mkdir(parents=True, exist_ok=True)
            empty = pa.Table.from_batches([], schema=OUTPUT_SCHEMA)
            pq.write_table(empty, self.path, compression="zstd")


def input_total_rows(input_path: Path, limit: int | None) -> int:
    total = pq.ParquetFile(input_path).metadata.num_rows
    return min(total, limit) if limit is not None else total


def validate_input(input_path: Path, payload_col: str) -> None:
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")
    schema_names = set(pq.ParquetFile(input_path).schema_arrow.names)
    missing = [col for col in INPUT_COLUMNS if col not in schema_names]
    if payload_col not in schema_names:
        missing.append(payload_col)
    if missing:
        raise SystemExit(f"Input is missing required columns: {', '.join(sorted(set(missing)))}")


def require_phase5_path(path: Path, label: str) -> Path:
    resolved = path.resolve()
    phase_root = PHASE_DIR.resolve()
    try:
        resolved.relative_to(phase_root)
    except ValueError as exc:
        raise SystemExit(f"{label} must stay inside {phase_root}: {resolved}") from exc
    return path


def iter_input_batches(input_path: Path, batch_size: int, limit: int | None) -> Any:
    remaining = limit
    parquet_file = pq.ParquetFile(input_path)
    for batch in parquet_file.iter_batches(batch_size=batch_size, columns=INPUT_COLUMNS):
        if remaining is not None:
            if remaining <= 0:
                return
            if batch.num_rows > remaining:
                batch = batch.slice(0, remaining)
            remaining -= batch.num_rows
        yield batch.to_pandas()


def now_text() -> str:
    return time.strftime("%Y-%m-%d %H:%M:%S")


def write_json(path: Path, obj: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_progress(
    path: Path | None,
    stage: str,
    rows_done: int,
    rows_total: int,
    started: float,
    extra: dict[str, Any] | None = None,
) -> None:
    if path is None:
        return
    elapsed = time.time() - started
    rate = rows_done / elapsed if elapsed > 0 else 0.0
    eta = (rows_total - rows_done) / rate if rate > 0 and rows_total >= rows_done else 0.0
    obj: dict[str, Any] = {
        "stage": stage,
        "updated_at": now_text(),
        "rows_done": rows_done,
        "rows_total": rows_total,
        "pct_done": round(rows_done / rows_total * 100, 4) if rows_total else 0.0,
        "elapsed_seconds": round(elapsed, 2),
        "rows_per_second": round(rate, 2),
        "eta_seconds": round(eta, 2),
    }
    if extra:
        obj.update(extra)
    write_json(path, obj)


def initialize_stats(mode_label: str, input_path: Path, out_dir: Path, report_dir: Path, rows_total: int) -> dict[str, Any]:
    return {
        "run_mode": mode_label,
        "label_mode": "detector_only",
        "started_at": now_text(),
        "input": str(input_path),
        "out_dir": str(out_dir),
        "report_dir": str(report_dir),
        "rows_total_expected": rows_total,
        "rows_processed": 0,
        "needs_ai_rows": 0,
        "review_queue_rows": 0,
        "conflict_rows": 0,
        "verified_dev_rows": 0,
        "verified_test_rows": 0,
        "counters": {
            "technique_primary": Counter(),
            "db_engine": Counter(),
            "db_family": Counter(),
            "confidence_band": Counter(),
            "quality_band": Counter(),
            "split": Counter(),
            "lane": Counter(),
            "label_source": Counter(),
            "syntax_validity": Counter(),
            "intent_secondary_multilabel": Counter(),
            "is_sqli": Counter(),
            "needs_ai": Counter(),
            "conflict_flags": Counter(),
        },
        "conflict_examples": [],
    }


def update_stats(stats: dict[str, Any], labeled: pd.DataFrame, review_queue: pd.DataFrame) -> None:
    stats["rows_processed"] += len(labeled)
    stats["review_queue_rows"] += len(review_queue)
    stats["needs_ai_rows"] += int(labeled["needs_ai"].sum())

    for col in [
        "technique_primary",
        "db_engine",
        "db_family",
        "confidence_band",
        "quality_band",
        "split",
        "lane",
        "label_source",
        "syntax_validity",
        "intent_secondary_multilabel",
        "is_sqli",
        "needs_ai",
    ]:
        stats["counters"][col].update(labeled[col].astype(str).tolist())

    for _, row in labeled.iterrows():
        flags = as_text(row["conflict_flags"])
        flag_items = ["none"] if not flags or flags == "none" else flags.split("|")
        stats["counters"]["conflict_flags"].update(flag_items)
        if flags and flags != "none":
            stats["conflict_rows"] += 1
            if len(stats["conflict_examples"]) < 20:
                stats["conflict_examples"].append(
                    {
                        "row_id": as_int(row["row_id"]),
                        "technique_primary": as_text(row["technique_primary"]),
                        "db_engine": as_text(row["db_engine"]),
                        "confidence": as_float(row["confidence_score"]),
                        "conflict_flags": flags,
                        "payload_sample": as_text(row["payload_working"])[:240],
                    }
                )


def counter_to_dict(counter: Counter) -> dict[str, int]:
    return {str(k): int(v) for k, v in counter.most_common()}


def markdown_counter_table(counter: Counter, key_name: str, limit: int | None = None) -> list[str]:
    rows = counter.most_common(limit)
    total = sum(counter.values())
    lines = [f"| {key_name} | Count | % |", "|---|---:|---:|"]
    if not rows:
        lines.append("| none | 0 | 0.000% |")
        return lines
    for key, count in rows:
        pct = count / total * 100 if total else 0.0
        lines.append(f"| {key} | {count:,} | {pct:.3f}% |")
    return lines


def build_report_payload(stats: dict[str, Any], sinks: dict[str, ParquetSink], elapsed: float) -> dict[str, Any]:
    artifact_rows = {name: sink.rows for name, sink in sinks.items()}
    counters = {name: counter_to_dict(counter) for name, counter in stats["counters"].items()}
    return {
        "run_mode": stats["run_mode"],
        "label_mode": stats["label_mode"],
        "started_at": stats["started_at"],
        "finished_at": now_text(),
        "elapsed_seconds": round(elapsed, 2),
        "input": stats["input"],
        "out_dir": stats["out_dir"],
        "report_dir": stats["report_dir"],
        "rows_total_expected": int(stats["rows_total_expected"]),
        "rows_processed": int(stats["rows_processed"]),
        "artifact_rows": artifact_rows,
        "needs_ai_rows": int(stats["needs_ai_rows"]),
        "review_queue_rows": int(stats["review_queue_rows"]),
        "conflict_rows": int(stats["conflict_rows"]),
        "conflict_rate": round(stats["conflict_rows"] / max(stats["rows_processed"], 1), 6),
        "verified_dev_rows": artifact_rows.get("verified_dev", 0),
        "verified_test_rows": artifact_rows.get("verified_test", 0),
        "counters": counters,
        "conflict_examples": stats["conflict_examples"],
    }


def write_distribution_json(report_payload: dict[str, Any], out_dir: Path) -> None:
    obj = {
        "run_mode": report_payload["run_mode"],
        "label_mode": report_payload["label_mode"],
        "rows_processed": report_payload["rows_processed"],
        "artifact_rows": report_payload["artifact_rows"],
        "needs_ai_rows": report_payload["needs_ai_rows"],
        "review_queue_rows": report_payload["review_queue_rows"],
        "counters": {
            key: report_payload["counters"][key]
            for key in [
                "technique_primary",
                "db_engine",
                "db_family",
                "confidence_band",
                "quality_band",
                "split",
                "lane",
                "label_source",
                "syntax_validity",
                "is_sqli",
                "needs_ai",
            ]
        },
    }
    write_json(out_dir / "label_distribution.json", obj)


def write_conflict_json(report_payload: dict[str, Any], out_dir: Path) -> None:
    obj = {
        "run_mode": report_payload["run_mode"],
        "rows_processed": report_payload["rows_processed"],
        "conflict_rows": report_payload["conflict_rows"],
        "conflict_rate": report_payload["conflict_rate"],
        "conflict_flags": report_payload["counters"]["conflict_flags"],
        "examples": report_payload["conflict_examples"],
    }
    write_json(out_dir / "conflict_summary.json", obj)


def write_markdown_reports(report_payload: dict[str, Any], out_dir: Path, report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    counters = {k: Counter(v) for k, v in report_payload["counters"].items()}
    artifact_rows = report_payload["artifact_rows"]

    full_lines = [
        "# 05 - Full Label System Report",
        "",
        f"**Run mode:** {report_payload['run_mode']}",
        f"**Label mode:** {report_payload['label_mode']}",
        f"**Rows processed:** {report_payload['rows_processed']:,}",
        f"**Elapsed seconds:** {report_payload['elapsed_seconds']:.2f}",
        f"**Input:** `{report_payload['input']}`",
        f"**Output directory:** `{out_dir}`",
        "",
        "## Artifact Rows",
        "",
        "| Artifact | Rows |",
        "|---|---:|",
    ]
    for name, rows in artifact_rows.items():
        full_lines.append(f"| {name} | {rows:,} |")
    full_lines += [
        "",
        "## Label Sources",
        "",
        *markdown_counter_table(counters["label_source"], "Source"),
        "",
        "## Notes",
        "",
        "- This run is detector-only and does not call external APIs or network services.",
        "- `verified_dev.parquet` and `verified_test.parquet` are high-confidence offline candidates from Phase 4 split policy, not human-reviewed labels.",
    ]
    (report_dir / "05_full_label_system_report.md").write_text("\n".join(full_lines) + "\n", encoding="utf-8")

    dist_lines = [
        "# 05 - Label Distribution",
        "",
        f"Rows processed: `{report_payload['rows_processed']:,}`",
        "",
        "## Technique",
        "",
        *markdown_counter_table(counters["technique_primary"], "Technique"),
        "",
        "## DB Engine",
        "",
        *markdown_counter_table(counters["db_engine"], "DB Engine"),
        "",
        "## Quality Band",
        "",
        *markdown_counter_table(counters["quality_band"], "Quality Band"),
        "",
        "## Split",
        "",
        *markdown_counter_table(counters["split"], "Split"),
        "",
        "## Lane",
        "",
        *markdown_counter_table(counters["lane"], "Lane"),
    ]
    (report_dir / "05_label_distribution.md").write_text("\n".join(dist_lines) + "\n", encoding="utf-8")

    conflict_lines = [
        "# 05 - Conflict Report",
        "",
        f"Rows processed: `{report_payload['rows_processed']:,}`",
        f"Conflict rows: `{report_payload['conflict_rows']:,}`",
        f"Conflict rate: `{report_payload['conflict_rate']:.4%}`",
        "",
        "## Conflict Flags",
        "",
        *markdown_counter_table(counters["conflict_flags"], "Flag"),
        "",
        "## Example Conflicts",
        "",
        "| Row ID | Technique | DB | Confidence | Flags | Payload sample |",
        "|---:|---|---|---:|---|---|",
    ]
    if report_payload["conflict_examples"]:
        for item in report_payload["conflict_examples"]:
            payload = as_text(item["payload_sample"]).replace("|", "\\|")
            conflict_lines.append(
                "| {row_id} | {technique_primary} | {db_engine} | {confidence:.4f} | {conflict_flags} | `{payload}` |".format(
                    **item,
                    payload=payload,
                )
            )
    else:
        conflict_lines.append("| 0 | none | none | 0 | none | none |")
    (report_dir / "05_conflict_report.md").write_text("\n".join(conflict_lines) + "\n", encoding="utf-8")

    gold_lines = [
        "# 05 - Gold Quality Report",
        "",
        "## Quality Band Counts",
        "",
        *markdown_counter_table(counters["quality_band"], "Quality Band"),
        "",
        "## Gold Composition",
        "",
        f"- Gold rows: `{artifact_rows.get('gold', 0):,}`",
        f"- Silver rows: `{artifact_rows.get('silver', 0):,}`",
        f"- Bronze rows: `{artifact_rows.get('bronze', 0):,}`",
        f"- Review queue rows: `{artifact_rows.get('review_queue', 0):,}`",
        f"- Verified dev candidate rows: `{artifact_rows.get('verified_dev', 0):,}`",
        f"- Verified test candidate rows: `{artifact_rows.get('verified_test', 0):,}`",
        "",
        "Gold rows require high detector confidence, no AI-needed flag, and no conflict flags.",
    ]
    (report_dir / "05_gold_quality_report.md").write_text("\n".join(gold_lines) + "\n", encoding="utf-8")

    summary_lines = [
        "# Tổng kết Phase 5",
        "",
        f"- Chế độ chạy: `{report_payload['run_mode']}`",
        f"- Chế độ gán nhãn: `{report_payload['label_mode']}`",
        f"- Tổng số dòng xử lý: `{report_payload['rows_processed']:,}`",
        f"- Gold/Silver/Bronze: `{artifact_rows.get('gold', 0):,}` / `{artifact_rows.get('silver', 0):,}` / `{artifact_rows.get('bronze', 0):,}`",
        f"- Review queue: `{artifact_rows.get('review_queue', 0):,}`",
        f"- Verified dev/test candidates: `{artifact_rows.get('verified_dev', 0):,}` / `{artifact_rows.get('verified_test', 0):,}`",
        f"- Conflict rows: `{report_payload['conflict_rows']:,}` ({report_payload['conflict_rate']:.4%})",
        "",
        "## Phân phối technique",
        "",
        *markdown_counter_table(counters["technique_primary"], "Technique"),
        "",
        "## Split integrity",
        "",
        "Phase 5 preserves Phase 4 `split` and `near_dup_cluster_id`; no reassignment is performed in this phase.",
    ]
    SUMMARY_PATH.write_text("\n".join(summary_lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Phase 05 full label system")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--out-dir", type=Path, default=None)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--log-dir", type=Path, default=DEFAULT_LOG_DIR)
    parser.add_argument("--progress-file", type=Path, default=None)
    parser.add_argument("--batch-size", type=int, default=100_000)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--payload-col", choices=["payload_working", "payload_delex_v5"], default="payload_working")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.batch_size <= 0:
        raise SystemExit("--batch-size must be positive")
    if args.limit is not None and args.limit <= 0:
        raise SystemExit("--limit must be positive when provided")

    out_dir = args.out_dir
    if out_dir is None:
        out_dir = DEFAULT_SANITY_OUT_DIR if args.limit is not None else DEFAULT_FULL_OUT_DIR
    report_dir = args.report_dir
    log_dir = args.log_dir
    progress_file = args.progress_file
    if progress_file is None:
        progress_name = "phase05_sanity_progress.json" if args.limit is not None else "phase05_full_progress.json"
        progress_file = log_dir / progress_name

    out_dir = require_phase5_path(out_dir, "--out-dir")
    report_dir = require_phase5_path(report_dir, "--report-dir")
    log_dir = require_phase5_path(log_dir, "--log-dir")
    progress_file = require_phase5_path(progress_file, "--progress-file")

    validate_input(args.input, args.payload_col)
    out_dir.mkdir(parents=True, exist_ok=True)
    report_dir.mkdir(parents=True, exist_ok=True)
    log_dir.mkdir(parents=True, exist_ok=True)

    mode_label = "full" if args.limit is None else f"limit={args.limit}"
    rows_total = input_total_rows(args.input, args.limit)
    stats = initialize_stats(mode_label, args.input, out_dir, report_dir, rows_total)
    started = time.time()

    sinks = {
        "phase05_labeled": ParquetSink(out_dir / "phase05_labeled.parquet"),
        "gold": ParquetSink(out_dir / "gold.parquet"),
        "silver": ParquetSink(out_dir / "silver.parquet"),
        "bronze": ParquetSink(out_dir / "bronze.parquet"),
        "review_queue": ParquetSink(out_dir / "review_queue.parquet"),
        "verified_dev": ParquetSink(out_dir / "verified_dev.parquet"),
        "verified_test": ParquetSink(out_dir / "verified_test.parquet"),
    }

    print("Phase 05 - Full Label System")
    print(f"input={args.input}")
    print(f"out_dir={out_dir}")
    print(f"report_dir={report_dir}")
    print(f"log_dir={log_dir}")
    print(f"batch_size={args.batch_size}")
    print(f"payload_col={args.payload_col}")
    print(f"mode={mode_label}")
    print(f"rows_total={rows_total:,}", flush=True)
    write_progress(progress_file, "starting", 0, rows_total, started)

    rows_done = 0
    try:
        for batch_idx, batch_df in enumerate(iter_input_batches(args.input, args.batch_size, args.limit), start=1):
            labeled = label_dataframe(batch_df, args.payload_col)
            sinks["phase05_labeled"].write(labeled)

            gold = labeled[labeled["quality_band"] == "gold"]
            silver = labeled[labeled["quality_band"] == "silver"]
            bronze = labeled[labeled["quality_band"] == "bronze"]
            review_queue = labeled[
                (labeled["review_priority"] > 0)
                | (labeled["needs_ai"])
                | (labeled["conflict_flags"] != "none")
                | (labeled["confidence_score"] < 0.70)
            ]
            verified_candidates = gold[gold["split"].isin(["verified_candidate", "val", "test"])]
            verified_dev = verified_candidates[
                verified_candidates["row_id"].map(lambda value: stable_bucket(value, 100) < 50)
            ]
            verified_test = verified_candidates[
                verified_candidates["row_id"].map(lambda value: stable_bucket(value, 100) >= 50)
            ]

            sinks["gold"].write(gold)
            sinks["silver"].write(silver)
            sinks["bronze"].write(bronze)
            sinks["review_queue"].write(review_queue)
            sinks["verified_dev"].write(verified_dev)
            sinks["verified_test"].write(verified_test)

            update_stats(stats, labeled, review_queue)
            rows_done += len(labeled)
            elapsed = time.time() - started
            rate = rows_done / elapsed if elapsed > 0 else 0.0
            print(
                "batch={} rows={:,}/{:,} rate={:.0f}/s elapsed={:.1f}s".format(
                    batch_idx,
                    rows_done,
                    rows_total,
                    rate,
                    elapsed,
                ),
                flush=True,
            )
            write_progress(
                progress_file,
                "labeling",
                rows_done,
                rows_total,
                started,
                {"batch": batch_idx, "review_queue_rows": stats["review_queue_rows"]},
            )
    finally:
        for sink in sinks.values():
            sink.close()

    elapsed = time.time() - started
    report_payload = build_report_payload(stats, sinks, elapsed)
    write_distribution_json(report_payload, out_dir)
    write_conflict_json(report_payload, out_dir)
    write_markdown_reports(report_payload, out_dir, report_dir)
    write_progress(progress_file, "done", rows_done, rows_total, started, {"reports_written": True})

    print("Done")
    print(f"rows={rows_done:,}")
    print(f"gold={sinks['gold'].rows:,}")
    print(f"silver={sinks['silver'].rows:,}")
    print(f"bronze={sinks['bronze'].rows:,}")
    print(f"review_queue={sinks['review_queue'].rows:,}")
    print(f"summary={SUMMARY_PATH}")


if __name__ == "__main__":
    main()
