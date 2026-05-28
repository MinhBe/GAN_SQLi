#!/usr/bin/env python3
"""Crawl recent SQL injection literature and metadata."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
SEARCH = ROOT / "Skill" / "research-paper-crawler" / "scripts" / "search_papers.py"
NORMALIZE = ROOT / "Skill" / "research-paper-crawler" / "scripts" / "normalize_records.py"
EXPORT = ROOT / "Skill" / "research-paper-crawler" / "scripts" / "export_results.py"

QUERIES = [
    ("q001_recent_sqli_survey", "SQL injection survey recent trends"),
    ("q002_sqli_systematic_review", "SQL injection systematic literature review"),
    ("q003_sqli_detection_recent", "SQL injection detection recent"),
    ("q004_sqli_prevention_recent", "SQL injection prevention recent"),
    ("q005_sqli_vulnerabilities_current", "SQL injection vulnerabilities current web applications"),
    ("q006_sqli_variants", "SQL injection variants blind time based error based union boolean"),
    ("q007_blind_sqli", "blind SQL injection detection prevention"),
    ("q008_time_based_sqli", "time based SQL injection"),
    ("q009_boolean_based_sqli", "boolean based SQL injection"),
    ("q010_error_based_sqli", "error based SQL injection"),
    ("q011_union_based_sqli", "union based SQL injection"),
    ("q012_second_order_sqli", "second order SQL injection"),
    ("q013_stored_sqli", "stored SQL injection second order"),
    ("q014_no_sql_injection", "NoSQL injection survey detection"),
    ("q015_orm_injection", "ORM injection SQL injection"),
    ("q016_api_sqli", "API SQL injection vulnerabilities"),
    ("q017_rest_sqli", "REST API SQL injection"),
    ("q018_graphql_sqli", "GraphQL SQL injection"),
    ("q019_microservices_sqli", "microservices SQL injection"),
    ("q020_cloud_sqli", "cloud SQL injection web applications"),
    ("q021_serverless_sqli", "serverless SQL injection"),
    ("q022_text_to_sql_injection", "Text-to-SQL SQL injection"),
    ("q023_llm_sqli", "large language model SQL injection"),
    ("q024_ai_generated_code_sqli", "AI generated code SQL injection vulnerability"),
    ("q025_prompt_to_sql_injection", "prompt to SQL injection"),
    ("q026_sqli_llm_detection", "LLM SQL injection detection"),
    ("q027_machine_learning_sqli", "SQL injection machine learning detection"),
    ("q028_deep_learning_sqli", "SQL injection deep learning detection"),
    ("q029_transformer_sqli", "SQL injection transformer detection"),
    ("q030_bert_sqli", "BERT SQL injection detection"),
    ("q031_lstm_sqli", "LSTM SQL injection detection"),
    ("q032_cnn_sqli", "CNN SQL injection detection"),
    ("q033_autoencoder_sqli", "SQL injection autoencoder detection"),
    ("q034_gan_sqli", "SQL injection GAN adversarial generation"),
    ("q035_adversarial_sqli", "adversarial SQL injection evasion detection"),
    ("q036_waf_sqli_bypass", "web application firewall SQL injection bypass"),
    ("q037_sqli_obfuscation", "SQL injection obfuscation evasion"),
    ("q038_sqli_payload_generation", "SQL injection payload generation"),
    ("q039_sqli_dataset", "SQL injection dataset benchmark"),
    ("q040_sqli_benchmark", "SQL injection detection benchmark dataset"),
    ("q041_sqli_static_analysis", "SQL injection static analysis"),
    ("q042_sqli_dynamic_analysis", "SQL injection dynamic analysis"),
    ("q043_sqli_taint_analysis", "SQL injection taint analysis"),
    ("q044_sqli_fuzzing", "SQL injection fuzzing"),
    ("q045_sqli_vapt", "SQL injection vulnerability assessment penetration testing"),
    ("q046_sqli_secure_coding", "SQL injection secure coding parameterized queries"),
    ("q047_sqli_prepared_statements", "SQL injection prepared statements parameterized queries"),
    ("q048_sqli_input_validation", "SQL injection input validation sanitization"),
    ("q049_sqli_still_prevalent", "why SQL injection still prevalent"),
    ("q050_sqli_web_security", "web application security SQL injection recent"),
    ("q051_sqli_owasp", "OWASP SQL injection 2021 2023 2024"),
    ("q052_sqli_cwe89", "CWE-89 SQL injection recent vulnerabilities"),
    ("q053_sqli_cve_analysis", "SQL injection CVE analysis"),
    ("q054_sqli_cms", "SQL injection CMS plugin vulnerabilities"),
    ("q055_wordpress_sqli", "WordPress plugin SQL injection vulnerabilities"),
    ("q056_ecommerce_sqli", "e-commerce SQL injection vulnerabilities"),
    ("q057_iot_sqli", "IoT SQL injection web interface"),
    ("q058_mobile_backend_sqli", "mobile application backend SQL injection"),
    ("q059_sqli_training_education", "SQL injection developer education secure coding"),
    ("q060_sqli_root_causes", "SQL injection root causes software development"),
]


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(part) for part in cmd), flush=True)
    subprocess.run([str(part) for part in cmd], cwd=ROOT, check=True)


def run_search(key: str, query: str, output: Path) -> None:
    cmd = [
        sys.executable,
        SEARCH,
        "--query",
        query,
        "--from-year",
        "2020",
        "--to-year",
        "2026",
        "--sources",
        "openalex,crossref",
        "--max-results",
        "200",
        "--output",
        output,
        "--delay",
        "0.5",
    ]
    for attempt in range(1, 4):
        try:
            run(cmd)
            return
        except subprocess.CalledProcessError as exc:
            print(f"! search failed for {key} attempt {attempt}: {exc}", flush=True)
            time.sleep(5 * attempt)
    fallback = cmd.copy()
    fallback[fallback.index("openalex,crossref")] = "openalex"
    print(f"! falling back to OpenAlex only for {key}", flush=True)
    run(fallback)


def main() -> int:
    BASE.mkdir(parents=True, exist_ok=True)
    (BASE / "queries.json").write_text(
        json.dumps([{"id": key, "query": query} for key, query in QUERIES], indent=2),
        encoding="utf-8",
    )

    for key, query in QUERIES:
        output = BASE / f"{key}.jsonl"
        if output.exists() and output.stat().st_size > 0:
            continue
        run_search(key, query, output)

    raw = BASE / "sqli_current.raw.jsonl"
    with raw.open("w", encoding="utf-8") as dst:
        for key, _ in QUERIES:
            src = BASE / f"{key}.jsonl"
            if src.exists():
                dst.write(src.read_text(encoding="utf-8-sig"))

    normalized = BASE / "sqli_current.normalized.jsonl"
    run([sys.executable, NORMALIZE, "--input", raw, "--output", normalized])
    for fmt, suffix in [("md", "md"), ("csv", "csv"), ("bibtex", "bib")]:
        run(
            [
                sys.executable,
                EXPORT,
                "--input",
                normalized,
                "--format",
                fmt,
                "--output",
                BASE / f"sqli_current.{suffix}",
            ]
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
