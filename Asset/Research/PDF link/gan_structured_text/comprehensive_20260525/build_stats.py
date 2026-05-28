#!/usr/bin/env python3
"""Build crawl statistics for the comprehensive corpus."""

from __future__ import annotations

import collections
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
FULL = BASE / "gan_structured_text.comprehensive.normalized.jsonl"
FILTERED = BASE / "gan_structured_text.comprehensive.filtered.jsonl"
STATS = BASE / "crawl_stats.json"


def iter_jsonl(path: Path):
    bad = 0
    with path.open("r", encoding="utf-8") as fh:
        for line_no, line in enumerate(fh, 1):
            if not line.strip():
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                bad += 1
    if bad:
        print(f"{path.name}: skipped_bad_lines={bad}")


def counter_to_pairs(counter: collections.Counter, limit: int | None = None):
    pairs = counter.most_common(limit)
    return [[key, value] for key, value in pairs]


def main() -> int:
    full_records = list(iter_jsonl(FULL))
    filtered_records = list(iter_jsonl(FILTERED))

    stats = {
        "full_count": len(full_records),
        "filtered_count": len(filtered_records),
        "sources_full": counter_to_pairs(collections.Counter(r.get("source") for r in full_records)),
        "sources_filtered": counter_to_pairs(collections.Counter(r.get("source") for r in filtered_records)),
        "bucket_counts": counter_to_pairs(
            collections.Counter(
                bucket
                for record in filtered_records
                for bucket in (record.get("topic_buckets") or [])
            )
        ),
        "years_filtered": counter_to_pairs(collections.Counter(r.get("year") for r in filtered_records)),
        "countries_filtered": counter_to_pairs(
            collections.Counter(
                country
                for record in filtered_records
                for country in (record.get("countries") or [])
            ),
            30,
        ),
        "oa_filtered": counter_to_pairs(collections.Counter(str(r.get("is_open_access")) for r in filtered_records)),
        "top_filtered": [
            {
                "year": record.get("year"),
                "citation_count": record.get("citation_count"),
                "topic_bucket": record.get("topic_bucket"),
                "title": record.get("title"),
                "doi_or_url": record.get("doi") or record.get("url"),
            }
            for record in sorted(
                filtered_records,
                key=lambda item: item.get("citation_count") or 0,
                reverse=True,
            )[:40]
        ],
    }
    STATS.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2)[:6000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
