#!/usr/bin/env python3
"""Run a broad metadata crawl for GANs on structured and text data."""

from __future__ import annotations

import json
import subprocess
import sys
import time
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
BASE = Path(__file__).resolve().parent
OUT = BASE / "comprehensive_20260525"
SEARCH = ROOT / "Skill" / "research-paper-crawler" / "scripts" / "search_papers.py"
NORMALIZE = ROOT / "Skill" / "research-paper-crawler" / "scripts" / "normalize_records.py"
EXPORT = ROOT / "Skill" / "research-paper-crawler" / "scripts" / "export_results.py"

QUERIES = [
    ("q001_gan_tabular_generation", "GAN tabular data generation"),
    ("q002_generative_adversarial_tabular", "generative adversarial networks tabular data"),
    ("q003_synthetic_tabular_gan", "synthetic tabular data GAN"),
    ("q004_tabular_data_synthesis_gan", "tabular data synthesis generative adversarial network"),
    ("q005_structured_data_gan", "structured data generative adversarial network"),
    ("q006_relational_data_gan", "relational data generation GAN"),
    ("q007_database_gan", "database data generation generative adversarial network"),
    ("q008_categorical_data_gan", "categorical data generative adversarial network"),
    ("q009_mixed_type_tabular_gan", "mixed-type tabular data GAN"),
    ("q010_privacy_tabular_gan", "privacy preserving synthetic tabular data GAN"),
    ("q011_imbalanced_tabular_gan", "imbalanced tabular data GAN oversampling"),
    ("q012_credit_fraud_tabular_gan", "tabular GAN credit fraud synthetic data"),
    ("q013_network_intrusion_tabular_gan", "tabular GAN intrusion detection synthetic data"),
    ("q014_iot_botnet_ctgan", "CTGAN IoT botnet tabular data"),
    ("q015_medical_tabular_gan", "medical tabular data generative adversarial network"),
    ("q016_ehr_gan", "electronic health records GAN synthetic data"),
    ("q017_patient_records_gan", "patient records generative adversarial network"),
    ("q018_medgan", "medGAN synthetic electronic health records"),
    ("q019_ehrgan", "EHR-GAN synthetic patient records"),
    ("q020_healthcare_synthetic_gan", "healthcare synthetic data GAN electronic health records"),
    ("q021_ctgan", "CTGAN tabular data"),
    ("q022_tablegan", "TableGAN synthetic data"),
    ("q023_tgan", "TGAN tabular generative adversarial network"),
    ("q024_ctabgan", "CTAB-GAN tabular data synthesis"),
    ("q025_ctabgan_plus", "CTAB-GAN+ tabular data synthesis"),
    ("q026_ads_gan", "ADS-GAN synthetic data generation"),
    ("q027_ganblr", "GANBLR tabular data generation"),
    ("q028_bayesian_network_gan_tabular", "Bayesian network GAN tabular data"),
    ("q029_rctgan", "RCTGAN relational tabular data"),
    ("q030_table_evaluator_gan", "tabular GAN synthetic data evaluation"),
    ("q031_graph_gan_structured", "graph generative adversarial network structured data"),
    ("q032_molgan", "MolGAN graph generative adversarial network"),
    ("q033_time_series_gan_structured", "time series GAN structured data synthesis"),
    ("q034_text_generation_gan", "generative adversarial network text generation"),
    ("q035_adversarial_text_generation", "adversarial text generation GAN"),
    ("q036_natural_language_generation_gan", "natural language generation generative adversarial network"),
    ("q037_discrete_sequence_gan", "discrete sequence generation GAN"),
    ("q038_sequence_gan_policy_gradient", "sequence generative adversarial nets policy gradient"),
    ("q039_seqgan", "SeqGAN text generation"),
    ("q040_textgan", "TextGAN natural language generation"),
    ("q041_rankgan", "RankGAN language generation"),
    ("q042_leakgan", "LeakGAN long text generation"),
    ("q043_maligan", "MaliGAN text generation"),
    ("q044_maskgan", "MaskGAN text generation"),
    ("q045_relgan", "RelGAN text generation"),
    ("q046_sentigan", "SentiGAN sentimental text generation"),
    ("q047_scratchgan", "ScratchGAN text generation"),
    ("q048_stepgan", "StepGAN text generation"),
    ("q049_text_discrete_gumbel_gan", "Gumbel Softmax GAN discrete text generation"),
    ("q050_text_vae_gan", "VAE GAN text generation discrete sequences"),
    ("q051_nlp_gan_review", "GAN natural language processing survey"),
    ("q052_gan_discrete_data", "generative adversarial networks discrete data"),
    ("q053_adversarial_sequence_generation", "adversarial sequence generation generative adversarial network"),
    ("q054_objective_reinforced_gan", "Objective-Reinforced Generative Adversarial Networks sequence generation"),
    ("q055_organ_sequence", "ORGAN sequence generation generative adversarial network"),
    ("q056_sql_gan_text", "SQL query generation GAN text"),
    ("q057_code_generation_gan", "code generation generative adversarial network discrete sequence"),
    ("q058_query_generation_gan", "query generation generative adversarial network text"),
    ("q059_structured_text_gan", "structured text generation GAN"),
    ("q060_synthetic_data_generation_gan_survey", "synthetic data generation GAN survey tabular text"),
]


def run(cmd: list[str]) -> None:
    print("+", " ".join(str(part) for part in cmd), flush=True)
    subprocess.run([str(part) for part in cmd], cwd=ROOT, check=True)


def run_search(key: str, query: str, output: Path) -> None:
    base_cmd = [
        sys.executable,
        SEARCH,
        "--query",
        query,
        "--from-year",
        "2014",
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
            run(base_cmd)
            return
        except subprocess.CalledProcessError as exc:
            print(f"! search failed for {key} attempt {attempt}: {exc}", flush=True)
            if attempt < 3:
                time.sleep(5 * attempt)

    fallback = base_cmd.copy()
    fallback[fallback.index("openalex,crossref")] = "openalex"
    print(f"! falling back to OpenAlex only for {key}", flush=True)
    run(fallback)


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "queries.json").write_text(
        json.dumps([{"id": key, "query": query} for key, query in QUERIES], indent=2),
        encoding="utf-8",
    )

    for key, query in QUERIES:
        output = OUT / f"{key}.jsonl"
        if output.exists() and output.stat().st_size > 0:
            continue
        run_search(key, query, output)

    raw = OUT / "gan_structured_text.comprehensive.raw.jsonl"
    with raw.open("w", encoding="utf-8") as dst:
        for key, _ in QUERIES:
            src = OUT / f"{key}.jsonl"
            if src.exists():
                dst.write(src.read_text(encoding="utf-8-sig"))

    normalized = OUT / "gan_structured_text.comprehensive.normalized.jsonl"
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
                OUT / f"gan_structured_text.comprehensive.{suffix}",
            ]
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
