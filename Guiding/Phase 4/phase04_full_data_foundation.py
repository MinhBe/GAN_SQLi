"""
Phase 04 - Full Data Foundation

Builds the full SQLi payload foundation from Phase 01 artifacts.

This script is intentionally CPU/RAM oriented and avoids GPU use. It performs
two streaming passes over the Phase 01 parquet:
  1. collect exact-dedup/template/literal/cluster statistics
  2. write the row-level foundation with known duplicate counts and safe splits
"""

import argparse
import hashlib
import json
import math
import re
import time
from collections import Counter, defaultdict
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = ROOT / "Guiding" / "Phase 1" / "phase01_data_reality.parquet"
DEFAULT_OUT_DIR = ROOT / "data" / "phase04"
DEFAULT_REPORT_DIR = ROOT / "reports"

PRESERVE_FUNCTIONS = [
    "sleep",
    "pg_sleep",
    "waitfor",
    "benchmark",
    "dbms_pipe",
    "extractvalue",
    "updatexml",
    "xmltype",
    "group_concat",
    "version",
    "database",
    "user",
    "information_schema",
    "sqlite_master",
    "utl_inaddr",
    "xp_cmdshell",
    "load_file",
]

RE_SQL_BLOCK_COMMENT = re.compile(r"/\*.*?\*/", re.DOTALL)
RE_SQL_LINE_COMMENT = re.compile(r"(--[^\r\n]*|#[^\r\n]*)")
RE_PLACEHOLDER = re.compile(r"__[A-Za-z_]+__")
RE_STR_SINGLE = re.compile(r"'(?:''|[^'])*'")
RE_STR_DOUBLE = re.compile(r'"(?:""|[^"])*"')
RE_TIME_LITERAL = re.compile(r"'?\b\d{1,2}:\d{1,2}(?::\d{1,2})?\b'?")
RE_NUM = re.compile(r"\b\d+(?:\.\d+)?\b")
RE_WHITESPACE = re.compile(r"\s+")
RE_IDENTIFIER_AFTER = re.compile(
    r"\b(from|join|into|update|table|database|schema)\s+([a-zA-Z_][a-zA-Z0-9_.$]*)",
    re.IGNORECASE,
)
RE_GENERIC_IDENTIFIER = re.compile(r"\b[a-zA-Z_][a-zA-Z0-9_.$]{2,}\b")
RE_TOKEN = re.compile(r"__[A-Z_]+__|[a-zA-Z_][a-zA-Z0-9_.$]*|\d+(?:\.\d+)?|[^\s]")

SQL_KEYWORDS = {
    "select",
    "union",
    "from",
    "where",
    "and",
    "or",
    "insert",
    "update",
    "delete",
    "drop",
    "create",
    "alter",
    "exec",
    "execute",
    "cast",
    "convert",
    "concat",
    "char",
    "chr",
    "order",
    "group",
    "by",
    "having",
    "limit",
    "offset",
    "into",
    "values",
    "set",
    "join",
    "inner",
    "outer",
    "left",
    "right",
    "table",
    "database",
    "schema",
    "user",
    "as",
    "on",
    "case",
    "when",
    "then",
    "else",
    "end",
    "null",
    "is",
    "not",
    "like",
    "in",
    "between",
    "distinct",
    "all",
    "asc",
    "desc",
    "true",
    "false",
    "waitfor",
    "delay",
}

PRESERVE_SET = set(PRESERVE_FUNCTIONS)


def as_text(value):
    if value is None:
        return ""
    if isinstance(value, float) and math.isnan(value):
        return ""
    return str(value)


def sha256_text(text):
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()


def stable_bucket(text, modulo=100):
    digest = hashlib.blake2b(text.encode("utf-8", errors="ignore"), digest_size=8).digest()
    return int.from_bytes(digest, "big") % modulo


def canonical_light(payload):
    text = as_text(payload)
    text = text.replace("\x00", " ")
    text = RE_WHITESPACE.sub(" ", text.strip())
    text = text.lower()
    return RE_PLACEHOLDER.sub(lambda m: m.group(0).upper(), text)


def canonical_structural(payload):
    text = canonical_light(payload)
    text = RE_SQL_BLOCK_COMMENT.sub("__COMMENT__", text)
    text = RE_SQL_LINE_COMMENT.sub("__COMMENT__", text)
    text = RE_STR_SINGLE.sub("__STR__", text)
    text = RE_STR_DOUBLE.sub("__STR__", text)
    text = RE_TIME_LITERAL.sub("__TIME__", text)
    text = RE_NUM.sub("__NUM__", text)
    text = RE_WHITESPACE.sub(" ", text.strip())
    return text


def extract_literals(payload):
    text = as_text(payload)
    stripped = RE_PLACEHOLDER.sub(" ", text)
    comments = RE_SQL_BLOCK_COMMENT.findall(stripped) + RE_SQL_LINE_COMMENT.findall(stripped)
    strings = RE_STR_SINGLE.findall(stripped) + RE_STR_DOUBLE.findall(stripped)
    without_strings = RE_STR_DOUBLE.sub(" ", RE_STR_SINGLE.sub(" ", stripped))
    times = RE_TIME_LITERAL.findall(without_strings)
    without_times = RE_TIME_LITERAL.sub(" ", without_strings)
    nums = RE_NUM.findall(without_times)
    ids = []
    tables = []
    for match in RE_IDENTIFIER_AFTER.finditer(stripped):
        table = match.group(2)
        if table.lower() not in SQL_KEYWORDS and table.lower() not in PRESERVE_SET:
            tables.append(table)
    for match in RE_GENERIC_IDENTIFIER.finditer(stripped):
        token = match.group(0)
        low = token.lower()
        if low not in SQL_KEYWORDS and low not in PRESERVE_SET and not low.startswith("__"):
            ids.append(token)
    return {
        "STR": strings,
        "NUM": nums,
        "TIME": times,
        "ID": ids,
        "TABLE": tables,
        "COMMENT": comments,
    }


def compact_unique(values, limit):
    seen = set()
    out = []
    for value in values:
        value = as_text(value).strip()
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
        if len(out) >= limit:
            break
    return out


def delex_v5(payload):
    text = canonical_light(payload)
    text = RE_SQL_BLOCK_COMMENT.sub(" __COMMENT__ ", text)
    text = RE_SQL_LINE_COMMENT.sub(" __COMMENT__ ", text)
    text = RE_STR_SINGLE.sub(" __STR__ ", text)
    text = RE_STR_DOUBLE.sub(" __STR__ ", text)
    text = RE_TIME_LITERAL.sub(" __TIME__ ", text)
    text = RE_NUM.sub(" __NUM__ ", text)

    def replace_table(match):
        return "{} __TABLE__".format(match.group(1))

    text = RE_IDENTIFIER_AFTER.sub(replace_table, text)
    tokens = RE_TOKEN.findall(text)
    out = []
    previous = ""
    for token in tokens:
        low = token.lower()
        if token.startswith("__") and token.endswith("__"):
            out.append(token)
        elif low in SQL_KEYWORDS or low in PRESERVE_SET:
            out.append(low)
        elif re.fullmatch(r"[a-zA-Z_][a-zA-Z0-9_.$]{2,}", token):
            if previous in ("from", "join", "into", "update", "table", "database", "schema"):
                out.append("__TABLE__")
            else:
                out.append("__ID__")
        else:
            out.append(token)
        previous = low
    return RE_WHITESPACE.sub(" ", " ".join(out)).strip()


def placeholder_types(delexed):
    placeholders = sorted(set(p.upper() for p in RE_PLACEHOLDER.findall(as_text(delexed))))
    return ",".join(placeholders)


def simhash64(text):
    tokens = RE_TOKEN.findall(as_text(text).lower())
    if not tokens:
        tokens = [as_text(text).lower()]
    vector = [0] * 64
    for token in tokens:
        digest = hashlib.blake2b(token.encode("utf-8", errors="ignore"), digest_size=8).digest()
        value = int.from_bytes(digest, "big")
        for bit in range(64):
            vector[bit] += 1 if value & (1 << bit) else -1
    result = 0
    for bit, weight in enumerate(vector):
        if weight >= 0:
            result |= 1 << bit
    return "{:016x}".format(result)


def near_dup_cluster_id(canonical):
    simhash = simhash64(canonical)
    return "sh_" + simhash[:12]


def split_for_cluster(cluster_id):
    bucket = stable_bucket(cluster_id, 100)
    if bucket < 80:
        return "train"
    if bucket < 90:
        return "val"
    if bucket < 98:
        return "test"
    return "verified_candidate"


def iter_input_batches(input_path, batch_size, limit=None, columns=None):
    parquet = pq.ParquetFile(input_path)
    emitted = 0
    for record_batch in parquet.iter_batches(batch_size=batch_size, columns=columns):
        df = record_batch.to_pandas()
        if limit is not None:
            remaining = limit - emitted
            if remaining <= 0:
                break
            if len(df) > remaining:
                df = df.iloc[:remaining].copy()
        emitted += len(df)
        if len(df):
            yield df
        if limit is not None and emitted >= limit:
            break


def input_total_rows(input_path, limit=None):
    total = pq.ParquetFile(input_path).metadata.num_rows
    return min(total, limit) if limit is not None else total


def write_progress(progress_file, stage, rows_done, rows_total, started, extra=None):
    if progress_file is None:
        return
    elapsed = time.time() - started
    pct = rows_done / rows_total * 100 if rows_total else 0.0
    obj = {
        "stage": stage,
        "rows_done": int(rows_done),
        "rows_total": int(rows_total),
        "percent": pct,
        "elapsed_seconds": elapsed,
        "rows_per_second": rows_done / elapsed if elapsed > 0 else 0.0,
        "updated_at_epoch": time.time(),
    }
    if extra:
        obj.update(extra)
    progress_file.parent.mkdir(parents=True, exist_ok=True)
    progress_file.write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")


def collect_stats(input_path, batch_size, limit, pool_limit, rows_total, started, progress_file):
    exact_counts = Counter()
    exact_first_row = {}
    exact_sample = {}
    template_counts = Counter()
    template_sample = {}
    template_placeholders = {}
    template_lanes = defaultdict(Counter)
    cluster_counts = Counter()
    cluster_sample = {}
    lane_counts = Counter()
    literal_pools = {key: [] for key in ["STR", "NUM", "TIME", "ID", "TABLE", "COMMENT"]}
    literal_seen = {key: set() for key in literal_pools}

    total = 0
    started = time.time()
    columns = ["row_id", "payload_input", "lane"]
    for batch_idx, df in enumerate(iter_input_batches(input_path, batch_size, limit, columns=columns), start=1):
        payloads = df["payload_input"].map(as_text)
        canon_light = payloads.map(canonical_light)
        delexed = payloads.map(delex_v5)
        dedup_hashes = canon_light.map(sha256_text)
        clusters = canon_light.map(near_dup_cluster_id)

        for row_id, payload, lane, canonical, dedup_hash, delex, cluster in zip(
            df["row_id"], payloads, df["lane"], canon_light, dedup_hashes, delexed, clusters
        ):
            row_id = int(row_id)
            lane = as_text(lane)
            exact_counts[dedup_hash] += 1
            if dedup_hash not in exact_first_row:
                exact_first_row[dedup_hash] = row_id
                exact_sample[dedup_hash] = canonical[:240]

            template_key = sha256_text(delex)
            template_counts[template_key] += 1
            if template_key not in template_sample:
                template_sample[template_key] = delex[:500]
                template_placeholders[template_key] = placeholder_types(delex)
            template_lanes[template_key][lane] += 1

            cluster_counts[cluster] += 1
            if cluster not in cluster_sample:
                cluster_sample[cluster] = canonical[:240]
            lane_counts[lane] += 1

            literals = extract_literals(payload)
            for key, values in literals.items():
                if len(literal_pools[key]) >= pool_limit:
                    continue
                for value in values:
                    value = as_text(value).strip()
                    if value and value not in literal_seen[key]:
                        literal_seen[key].add(value)
                        literal_pools[key].append(value)
                        if len(literal_pools[key]) >= pool_limit:
                            break

        total += len(df)
        if batch_idx == 1 or batch_idx % 10 == 0:
            elapsed = time.time() - started
            print("pass1 batch={} rows={:,} unique_hashes={:,} templates={:,} elapsed={:.1f}s".format(
                batch_idx, total, len(exact_counts), len(template_counts), elapsed
            ), flush=True)
        write_progress(
            progress_file,
            "pass1_collect_stats",
            total,
            rows_total,
            started,
            {
                "batch": batch_idx,
                "unique_hashes": len(exact_counts),
                "templates": len(template_counts),
                "near_dup_clusters": len(cluster_counts),
            },
        )

    return {
        "total_rows": total,
        "exact_counts": exact_counts,
        "exact_first_row": exact_first_row,
        "exact_sample": exact_sample,
        "template_counts": template_counts,
        "template_sample": template_sample,
        "template_placeholders": template_placeholders,
        "template_lanes": template_lanes,
        "cluster_counts": cluster_counts,
        "cluster_sample": cluster_sample,
        "lane_counts": lane_counts,
        "literal_pools": literal_pools,
    }


def build_foundation_batch(df, stats):
    payloads = df["payload_input"].map(as_text)
    canon_light = payloads.map(canonical_light)
    canon_struct = payloads.map(canonical_structural)
    delexed = payloads.map(delex_v5)
    dedup_hashes = canon_light.map(sha256_text)
    clusters = canon_light.map(near_dup_cluster_id)
    template_keys = delexed.map(sha256_text)

    out = pd.DataFrame(
        {
            "row_id": df["row_id"].astype("int64"),
            "source_file": df["source_file"].map(as_text),
            "source_row_index": df["source_row_index"].astype("int64"),
            "payload_input": payloads,
            "lane": df["lane"].map(as_text),
            "lane_confidence": df["lane_confidence"].map(as_text),
            "payload_working": payloads,
            "payload_canonical_light": canon_light,
            "payload_canonical_structural": canon_struct,
            "payload_delex_v5": delexed,
            "dedup_hash": dedup_hashes,
            "duplicate_count": dedup_hashes.map(lambda h: int(stats["exact_counts"].get(h, 0))).astype("int64"),
            "is_exact_duplicate": dedup_hashes.map(lambda h: int(stats["exact_counts"].get(h, 0)) > 1),
            "first_seen_row_id": dedup_hashes.map(lambda h: int(stats["exact_first_row"].get(h, -1))).astype("int64"),
            "near_dup_cluster_id": clusters,
            "near_dup_cluster_size": clusters.map(lambda c: int(stats["cluster_counts"].get(c, 0))).astype("int64"),
            "cluster_representative": clusters.map(lambda c: stats["cluster_sample"].get(c, "")),
            "delex_version": "v5",
            "delex_flags": delexed.map(placeholder_types),
            "delex_collision_key": template_keys,
            "relex_map_id": template_keys.map(lambda h: "rx_" + h[:16]),
            "round_trip_status": "not_evaluated",
            "split": clusters.map(split_for_cluster),
        }
    )
    return out


def write_parquet_from_rows(rows, path, batch_size=100_000):
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = None
    try:
        for start in range(0, len(rows), batch_size):
            df = pd.DataFrame(rows[start:start + batch_size])
            table = pa.Table.from_pandas(df, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(path, table.schema, compression="zstd")
            writer.write_table(table)
    finally:
        if writer is not None:
            writer.close()


def write_exact_dedup_map(stats, out_dir):
    rows = []
    for dedup_hash, count in stats["exact_counts"].items():
        rows.append(
            {
                "dedup_hash": dedup_hash,
                "duplicate_count": int(count),
                "first_seen_row_id": int(stats["exact_first_row"][dedup_hash]),
                "canonical_sample": stats["exact_sample"].get(dedup_hash, ""),
            }
        )
    write_parquet_from_rows(rows, out_dir / "exact_dedup_map.parquet")


def write_near_dup_clusters(stats, out_dir):
    rows = []
    for cluster_id, count in stats["cluster_counts"].items():
        rows.append(
            {
                "near_dup_cluster_id": cluster_id,
                "near_dup_cluster_size": int(count),
                "cluster_representative": stats["cluster_sample"].get(cluster_id, ""),
                "split": split_for_cluster(cluster_id),
            }
        )
    write_parquet_from_rows(rows, out_dir / "near_dup_clusters.parquet")


def write_relex_map(stats, out_dir):
    rows = []
    for template_key, count in stats["template_counts"].items():
        lanes = stats["template_lanes"][template_key]
        rows.append(
            {
                "relex_map_id": "rx_" + template_key[:16],
                "delex_collision_key": template_key,
                "payload_delex_v5": stats["template_sample"].get(template_key, ""),
                "template_count": int(count),
                "placeholder_types": stats["template_placeholders"].get(template_key, ""),
                "lane_counts_json": json.dumps(dict(lanes), ensure_ascii=False, sort_keys=True),
            }
        )
    write_parquet_from_rows(rows, out_dir / "relex_map.parquet")


def write_foundation(input_path, batch_size, limit, stats, out_dir, rows_total, started, progress_file):
    path = out_dir / "phase04_payload_foundation.parquet"
    path.parent.mkdir(parents=True, exist_ok=True)
    writer = None
    total = 0
    started = time.time()
    try:
        for batch_idx, df in enumerate(iter_input_batches(input_path, batch_size, limit), start=1):
            out = build_foundation_batch(df, stats)
            table = pa.Table.from_pandas(out, preserve_index=False)
            if writer is None:
                writer = pq.ParquetWriter(path, table.schema, compression="zstd")
            writer.write_table(table)
            total += len(out)
            if batch_idx == 1 or batch_idx % 10 == 0:
                elapsed = time.time() - started
                print("pass2 batch={} rows={:,} elapsed={:.1f}s".format(batch_idx, total, elapsed), flush=True)
            write_progress(
                progress_file,
                "pass2_write_foundation",
                total,
                rows_total,
                started,
                {"batch": batch_idx},
            )
    finally:
        if writer is not None:
            writer.close()
    return total


def write_literal_pools(stats, out_dir):
    pools = {
        key: {
            "count": len(values),
            "values": values,
        }
        for key, values in stats["literal_pools"].items()
    }
    pools["DB_FUNCTION_POOL"] = {
        "count": len(PRESERVE_FUNCTIONS),
        "values": PRESERVE_FUNCTIONS,
    }
    path = out_dir / "literal_pools.json"
    path.write_text(json.dumps(pools, ensure_ascii=False, indent=2), encoding="utf-8")


def write_split_json(stats, out_dir):
    split_counts = Counter(split_for_cluster(cluster_id) for cluster_id in stats["cluster_counts"])
    row_split_counts = Counter()
    for cluster_id, count in stats["cluster_counts"].items():
        row_split_counts[split_for_cluster(cluster_id)] += count
    obj = {
        "split_policy": "deterministic blake2b bucket over near_dup_cluster_id",
        "cluster_counts": dict(sorted(split_counts.items())),
        "row_counts": {k: int(v) for k, v in sorted(row_split_counts.items())},
        "cluster_leakage": 0,
    }
    (out_dir / "splits_cluster_safe.json").write_text(json.dumps(obj, ensure_ascii=False, indent=2), encoding="utf-8")
    return obj


def top_counter(counter, n=20):
    return [{"key": key, "count": int(count)} for key, count in counter.most_common(n)]


def write_report(stats, split_summary, out_dir, report_dir, elapsed_seconds, mode_label):
    report_dir.mkdir(parents=True, exist_ok=True)
    total = stats["total_rows"]
    exact_unique = len(stats["exact_counts"])
    exact_dup_rows = total - exact_unique
    cluster_count = len(stats["cluster_counts"])
    template_count = len(stats["template_counts"])
    top_templates = stats["template_counts"].most_common(10)
    lines = [
        "# 04 - Full Data Foundation Report",
        "",
        f"**Run mode:** {mode_label}",
        f"**Rows processed:** {total:,}",
        f"**Elapsed seconds:** {elapsed_seconds:.1f}",
        "",
        "## Lane Distribution",
        "",
        "| Lane | Count | % |",
        "|---|---:|---:|",
    ]
    for lane, count in sorted(stats["lane_counts"].items()):
        pct = count / total * 100 if total else 0
        lines.append(f"| {lane} | {count:,} | {pct:.3f}% |")
    lines += [
        "",
        "## Deduplication",
        "",
        f"- Exact unique canonical payloads: `{exact_unique:,}`",
        f"- Exact duplicate rows: `{exact_dup_rows:,}`",
        f"- Near-duplicate cluster buckets: `{cluster_count:,}`",
        f"- Delex template keys: `{template_count:,}`",
        "",
        "## Split Summary",
        "",
        "| Split | Rows | Clusters |",
        "|---|---:|---:|",
    ]
    row_counts = split_summary["row_counts"]
    cluster_counts = split_summary["cluster_counts"]
    for split in ["train", "val", "test", "verified_candidate"]:
        lines.append(f"| {split} | {row_counts.get(split, 0):,} | {cluster_counts.get(split, 0):,} |")
    lines += [
        "",
        "Cluster leakage between splits: `0` by deterministic cluster assignment.",
        "",
        "## Literal Pools",
        "",
        "| Pool | Stored unique values |",
        "|---|---:|",
    ]
    for key, values in stats["literal_pools"].items():
        lines.append(f"| {key} | {len(values):,} |")
    lines += [
        "",
        "## Top Delex Templates",
        "",
        "| Count | Template sample |",
        "|---:|---|",
    ]
    for template_key, count in top_templates:
        sample = stats["template_sample"].get(template_key, "").replace("|", "\\|")
        lines.append(f"| {count:,} | `{sample[:160]}` |")
    lines += [
        "",
        "## Outputs",
        "",
        f"- `{out_dir / 'phase04_payload_foundation.parquet'}`",
        f"- `{out_dir / 'exact_dedup_map.parquet'}`",
        f"- `{out_dir / 'near_dup_clusters.parquet'}`",
        f"- `{out_dir / 'relex_map.parquet'}`",
        f"- `{out_dir / 'literal_pools.json'}`",
        f"- `{out_dir / 'splits_cluster_safe.json'}`",
        "",
        "## Notes",
        "",
        "- `round_trip_status` is `not_evaluated`; DB/WAF execution belongs to later evaluator phases.",
        "- Near-dedup is approximate SimHash-prefix bucketing, chosen to fit 20GB RAM.",
        "- `payload_input` is preserved; canonical/delex columns are derived views.",
    ]
    (report_dir / "04_data_foundation_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args():
    parser = argparse.ArgumentParser(description="Phase 04 full data foundation")
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--batch-size", type=int, default=200_000)
    parser.add_argument("--limit", type=int, default=None)
    parser.add_argument("--pool-limit", type=int, default=50_000)
    parser.add_argument("--progress-file", type=Path, default=None)
    parser.add_argument("--skip-heavy-maps", action="store_true", help="Only write foundation/report/literal pools")
    return parser.parse_args()


def main():
    args = parse_args()
    if not args.input.exists():
        raise SystemExit(f"Input not found: {args.input}")

    args.out_dir.mkdir(parents=True, exist_ok=True)
    args.report_dir.mkdir(parents=True, exist_ok=True)
    mode_label = "full" if args.limit is None else f"limit={args.limit}"
    started = time.time()
    rows_total = input_total_rows(args.input, args.limit)

    print("Phase 04 - Full Data Foundation")
    print(f"input={args.input}")
    print(f"out_dir={args.out_dir}")
    print(f"report_dir={args.report_dir}")
    print(f"batch_size={args.batch_size}")
    print(f"mode={mode_label}")
    print(f"rows_total={rows_total:,}", flush=True)
    write_progress(args.progress_file, "starting", 0, rows_total, started)

    print("\n[1/6] Collecting stats")
    stats = collect_stats(args.input, args.batch_size, args.limit, args.pool_limit, rows_total, started, args.progress_file)

    print("\n[2/6] Writing foundation")
    written = write_foundation(args.input, args.batch_size, args.limit, stats, args.out_dir, rows_total, started, args.progress_file)
    if written != stats["total_rows"]:
        raise RuntimeError(f"Row count mismatch: pass1={stats['total_rows']} pass2={written}")

    print("\n[3/6] Writing literal pools and split summary")
    write_progress(args.progress_file, "write_literal_pools_and_splits", written, rows_total, started)
    write_literal_pools(stats, args.out_dir)
    split_summary = write_split_json(stats, args.out_dir)

    if args.skip_heavy_maps:
        print("\n[4/6] Skipping heavy maps by request")
    else:
        print("\n[4/6] Writing exact dedup map")
        write_progress(args.progress_file, "write_exact_dedup_map", written, rows_total, started)
        write_exact_dedup_map(stats, args.out_dir)
        print("[5/6] Writing near-dup clusters and relex map")
        write_progress(args.progress_file, "write_near_dup_and_relex_maps", written, rows_total, started)
        write_near_dup_clusters(stats, args.out_dir)
        write_relex_map(stats, args.out_dir)

    elapsed = time.time() - started
    print("\n[6/6] Writing report")
    write_progress(args.progress_file, "write_report", written, rows_total, started)
    write_report(stats, split_summary, args.out_dir, args.report_dir, elapsed, mode_label)
    write_progress(
        args.progress_file,
        "done",
        written,
        rows_total,
        started,
        {
            "exact_unique": len(stats["exact_counts"]),
            "near_dup_clusters": len(stats["cluster_counts"]),
            "templates": len(stats["template_counts"]),
        },
    )

    print("\nDone")
    print(f"rows={stats['total_rows']:,}")
    print(f"exact_unique={len(stats['exact_counts']):,}")
    print(f"near_dup_clusters={len(stats['cluster_counts']):,}")
    print(f"templates={len(stats['template_counts']):,}")
    print(f"report={args.report_dir / '04_data_foundation_report.md'}")


if __name__ == "__main__":
    main()
