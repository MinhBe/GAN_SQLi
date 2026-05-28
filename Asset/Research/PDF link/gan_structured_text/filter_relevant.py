#!/usr/bin/env python3
"""Build a topic-filtered GAN corpus from normalized crawler records."""

from __future__ import annotations

import json
import re
from pathlib import Path


BASE = Path(__file__).resolve().parent
INPUT = BASE / "gan_structured_text.normalized.jsonl"
OUTPUT = BASE / "gan_structured_text.filtered.jsonl"

STRUCTURED_TERMS = [
    "tabular data",
    "tabular",
    "structured data",
    "relational data",
    "relational database",
    "electronic health record",
    "electronic health records",
    "ehr",
    "patient record",
    "patient records",
    "clinical data",
    "clinical records",
    "categorical data",
    "mixed-type data",
    "data synthesis",
    "ctgan",
    "ctab-gan",
    "tablegan",
    "tgan",
    "medgan",
    "ads-gan",
    "ganblr",
    "rctgan",
]

TEXT_TERMS = [
    "text generation",
    "text generat",
    "natural language generation",
    "language generation",
    "sentence generation",
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
    "scratchgan",
]

KNOWN_MODELS = [
    "ctgan",
    "ctab-gan",
    "tablegan",
    "medgan",
    "ads-gan",
    "ganblr",
    "seqgan",
    "textgan",
    "rankgan",
    "leakgan",
    "maligan",
    "maskgan",
    "relgan",
    "scratchgan",
]

IMAGE_DOMINANT_TERMS = [
    "text-to-image",
    "text to image",
    "image generation",
    "image-to-image",
    "computer vision",
    "point clouds",
    "low light enhancement",
    "remote sensing",
]


def contains_any(blob: str, terms: list[str]) -> bool:
    return any(term in blob for term in terms)


def has_explicit_gan(blob: str) -> bool:
    return bool(re.search(r"\bgan\b|\bgans\b", blob)) or "generative adversarial" in blob


def has_known_model(blob: str) -> bool:
    if contains_any(blob, KNOWN_MODELS):
        return True
    return "objective-reinforced generative adversarial" in blob or (
        re.search(r"\borgan\b", blob) is not None and "sequence generation" in blob
    )


def main() -> int:
    records = []
    for line in INPUT.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        record = json.loads(line)
        blob = " ".join(
            str(record.get(key) or "")
            for key in ["title", "abstract", "keywords", "concepts"]
        ).lower()
        model_hit = has_known_model(blob)
        has_gan = has_explicit_gan(blob) or model_hit
        is_structured = contains_any(blob, STRUCTURED_TERMS)
        is_text = contains_any(blob, TEXT_TERMS)
        image_dominant = contains_any(blob, IMAGE_DOMINANT_TERMS)
        if image_dominant and not model_hit:
            continue
        if has_gan and (is_structured or is_text or model_hit):
            record["topic_bucket"] = (
                "structured+text"
                if is_structured and is_text
                else ("structured_data" if is_structured else "text_data")
            )
            records.append(record)

    OUTPUT.write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in records),
        encoding="utf-8",
    )
    print(len(records))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
