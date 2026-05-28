#!/usr/bin/env python3
"""Filter and bucket comprehensive GAN structured/text records."""

from __future__ import annotations

import json
import re
from pathlib import Path


BASE = Path(__file__).resolve().parent
INPUT = BASE / "gan_structured_text.comprehensive.normalized.jsonl"
OUTPUT = BASE / "gan_structured_text.comprehensive.filtered.jsonl"

STRUCTURED_TERMS = [
    "tabular",
    "tabular data",
    "structured data",
    "relational data",
    "relational database",
    "categorical data",
    "mixed-type",
    "synthetic data",
    "data synthesis",
    "data generation",
    "oversampling",
    "imbalanced data",
    "ctgan",
    "ctab-gan",
    "tablegan",
    "tgan",
    "ganblr",
    "ads-gan",
    "rctgan",
]

HEALTH_TERMS = [
    "electronic health record",
    "electronic health records",
    "ehr",
    "patient record",
    "patient records",
    "clinical data",
    "medical data",
    "healthcare",
    "medgan",
]

RELATIONAL_GRAPH_TERMS = [
    "relational data",
    "relational database",
    "graph",
    "graphs",
    "molecular graph",
    "molgan",
]

TIME_SERIES_TERMS = [
    "time series",
    "temporal",
    "sequential data",
]

TEXT_TERMS = [
    "text generation",
    "text generat",
    "natural language generation",
    "language generation",
    "sentence generation",
    "long text generation",
    "sequence generation",
    "discrete sequence",
    "discrete sequences",
    "discrete data",
    "discrete token",
    "language model",
    "seqgan",
    "textgan",
    "rankgan",
    "leakgan",
    "maligan",
    "maskgan",
    "relgan",
    "sentigan",
    "scratchgan",
    "stepgan",
]

KNOWN_MODELS = [
    "ctgan",
    "ctab-gan",
    "tablegan",
    "medgan",
    "ads-gan",
    "ganblr",
    "rctgan",
    "molgan",
    "seqgan",
    "textgan",
    "rankgan",
    "leakgan",
    "maligan",
    "maskgan",
    "relgan",
    "sentigan",
    "scratchgan",
    "stepgan",
]

EXCLUDE_UNLESS_MODEL = [
    "text-to-image",
    "text to image",
    "image generation",
    "image-to-image",
    "image classification",
    "computer vision",
    "remote sensing",
    "point clouds",
    "low light enhancement",
    "video generation",
    "speech",
    "waveform",
    "audio",
]


def contains_any(blob: str, terms: list[str]) -> bool:
    return any(term in blob for term in terms)


def explicit_gan(blob: str) -> bool:
    return bool(re.search(r"\bgan\b|\bgans\b", blob)) or "generative adversarial" in blob


def known_model(blob: str) -> bool:
    if contains_any(blob, KNOWN_MODELS):
        return True
    return "objective-reinforced generative adversarial" in blob or (
        re.search(r"\borgan\b", blob) is not None and "sequence generation" in blob
    )


def buckets_for(blob: str) -> list[str]:
    buckets = []
    if contains_any(blob, STRUCTURED_TERMS):
        buckets.append("structured_tabular")
    if contains_any(blob, HEALTH_TERMS):
        buckets.append("ehr_health")
    if contains_any(blob, RELATIONAL_GRAPH_TERMS):
        buckets.append("relational_graph")
    if contains_any(blob, TIME_SERIES_TERMS):
        buckets.append("time_series")
    if contains_any(blob, TEXT_TERMS):
        buckets.append("text_discrete_sequence")
    return buckets


def main() -> int:
    total = 0
    kept = 0
    with INPUT.open("r", encoding="utf-8") as src, OUTPUT.open("w", encoding="utf-8") as dst:
        for line in src:
            if not line.strip():
                continue
            total += 1
            record = json.loads(line)
            blob = " ".join(
                str(record.get(key) or "")
                for key in ["title", "abstract", "keywords", "concepts"]
            ).lower()
            model_hit = known_model(blob)
            has_gan = explicit_gan(blob) or model_hit
            buckets = buckets_for(blob)
            if not has_gan or not buckets:
                continue
            if contains_any(blob, EXCLUDE_UNLESS_MODEL) and not model_hit:
                continue
            record["topic_buckets"] = buckets
            record["topic_bucket"] = "+".join(buckets)
            dst.write(json.dumps(record, ensure_ascii=False) + "\n")
            kept += 1

    print(f"read={total} kept={kept}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
