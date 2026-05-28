#!/usr/bin/env python3
"""Filter and bucket recent SQL injection records."""

from __future__ import annotations

import json
import re
from pathlib import Path


BASE = Path(__file__).resolve().parent
INPUT = BASE / "sqli_current.normalized.jsonl"
OUTPUT = BASE / "sqli_current.filtered.jsonl"

SQLI_TERMS = [
    "sql injection",
    "sqli",
    "cwe-89",
    "structured query language injection",
    "nosql injection",
    "no sql injection",
    "text-to-sql injection",
    "text to sql injection",
]

VARIANT_TERMS = [
    "blind sql injection",
    "time based",
    "time-based",
    "boolean based",
    "boolean-based",
    "error based",
    "error-based",
    "union based",
    "union-based",
    "second order",
    "second-order",
    "stored sql injection",
    "out-of-band",
    "stacked query",
    "batched query",
]

MODERN_SURFACE_TERMS = [
    "api",
    "rest",
    "graphql",
    "microservice",
    "microservices",
    "cloud",
    "serverless",
    "mobile",
    "iot",
    "cms",
    "wordpress",
    "plugin",
    "e-commerce",
    "orm",
    "nosql",
    "text-to-sql",
    "text to sql",
]

AI_LLM_TERMS = [
    "large language model",
    "llm",
    "chatgpt",
    "generative ai",
    "text-to-sql",
    "text to sql",
    "prompt",
    "ai generated code",
    "code generation",
]

ML_DETECTION_TERMS = [
    "machine learning",
    "deep learning",
    "neural network",
    "cnn",
    "lstm",
    "bert",
    "transformer",
    "autoencoder",
    "classification",
    "classifier",
    "detection",
]

EVASION_TERMS = [
    "evasion",
    "bypass",
    "obfuscation",
    "adversarial",
    "payload generation",
    "web application firewall",
    "waf",
    "mutation",
]

DATASET_TERMS = [
    "dataset",
    "benchmark",
    "corpus",
    "evaluation",
    "testbed",
]

DEFENSE_TERMS = [
    "prevention",
    "mitigation",
    "prepared statement",
    "prepared statements",
    "parameterized",
    "sanitization",
    "input validation",
    "static analysis",
    "dynamic analysis",
    "taint analysis",
    "fuzzing",
    "secure coding",
]

SURVEY_CAUSE_TERMS = [
    "survey",
    "review",
    "systematic literature review",
    "root cause",
    "prevalent",
    "still",
    "developer",
    "education",
    "owasp",
    "cve",
    "cwe",
]

EXCLUDE_TERMS = [
    "sql server performance",
    "structured query language database teaching",
]


def contains_any(blob: str, terms: list[str]) -> bool:
    return any(term in blob for term in terms)


def has_sqli(blob: str) -> bool:
    if contains_any(blob, SQLI_TERMS):
        return True
    return bool(re.search(r"\bsql\s*injection\b|\bsqli\b", blob))


def buckets_for(blob: str) -> list[str]:
    buckets = []
    if contains_any(blob, VARIANT_TERMS):
        buckets.append("attack_variants")
    if contains_any(blob, MODERN_SURFACE_TERMS):
        buckets.append("modern_surfaces")
    if contains_any(blob, AI_LLM_TERMS):
        buckets.append("ai_llm_text2sql")
    if contains_any(blob, ML_DETECTION_TERMS):
        buckets.append("ml_dl_detection")
    if contains_any(blob, EVASION_TERMS):
        buckets.append("evasion_waf_adversarial")
    if contains_any(blob, DATASET_TERMS):
        buckets.append("datasets_benchmarks")
    if contains_any(blob, DEFENSE_TERMS):
        buckets.append("defense_secure_coding")
    if contains_any(blob, SURVEY_CAUSE_TERMS):
        buckets.append("surveys_root_causes")
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
            if contains_any(blob, EXCLUDE_TERMS):
                continue
            if not has_sqli(blob):
                continue
            buckets = buckets_for(blob)
            if not buckets:
                buckets = ["general_recent_sqli"]
            record["topic_buckets"] = buckets
            record["topic_bucket"] = "+".join(buckets)
            dst.write(json.dumps(record, ensure_ascii=False) + "\n")
            kept += 1
    print(f"read={total} kept={kept}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
