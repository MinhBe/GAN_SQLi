#!/usr/bin/env python3
"""Build statistics for recent SQL injection corpus."""

from __future__ import annotations

import collections
import json
from pathlib import Path


BASE = Path(__file__).resolve().parent
FULL = BASE / "sqli_current.normalized.jsonl"
FILTERED = BASE / "sqli_current.filtered.jsonl"
STATS = BASE / "crawl_stats.json"


def iter_jsonl(path: Path):
    with path.open("r", encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                yield json.loads(line)


def pairs(counter: collections.Counter, limit: int | None = None):
    return [[key, value] for key, value in counter.most_common(limit)]


def main() -> int:
    full = list(iter_jsonl(FULL))
    filtered = list(iter_jsonl(FILTERED))
    stats = {
        "full_count": len(full),
        "filtered_count": len(filtered),
        "sources_full": pairs(collections.Counter(r.get("source") for r in full)),
        "sources_filtered": pairs(collections.Counter(r.get("source") for r in filtered)),
        "bucket_counts": pairs(
            collections.Counter(
                bucket for record in filtered for bucket in (record.get("topic_buckets") or [])
            )
        ),
        "years_filtered": pairs(collections.Counter(r.get("year") for r in filtered)),
        "countries_filtered": pairs(
            collections.Counter(
                country for record in filtered for country in (record.get("countries") or [])
            ),
            30,
        ),
        "oa_filtered": pairs(collections.Counter(str(r.get("is_open_access")) for r in filtered)),
        "top_filtered": [
            {
                "year": record.get("year"),
                "citation_count": record.get("citation_count"),
                "topic_bucket": record.get("topic_bucket"),
                "title": record.get("title"),
                "doi_or_url": record.get("doi") or record.get("url"),
            }
            for record in sorted(
                filtered,
                key=lambda item: item.get("citation_count") or 0,
                reverse=True,
            )[:40]
        ],
    }
    STATS.write_text(json.dumps(stats, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=True, indent=2)[:6000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
