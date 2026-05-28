# GAN for Structured and Text Data - Crawl Report

Date: 2026-05-24

## Scope

Topic: applications of GAN/generative adversarial models for structured data and text data.

Year range: 2014-2026.

Regions: global; no affiliation-country filter was applied.

Document type: scholarly metadata only. PDFs were not downloaded.

## Sources

- OpenAlex
- Crossref

The crawler used API-based collection only. No publisher pages, paywalled PDFs, CAPTCHA-protected sources, or restricted national databases were crawled.

## Query Set

Broad discovery queries:

- `GAN tabular data generation`
- `generative adversarial network structured data`
- `GAN synthetic tabular data`
- `GAN relational data generation`
- `GAN electronic health records synthetic data`
- `generative adversarial network text generation`
- `SeqGAN text generation`
- `GAN discrete sequence generation`
- `TextGAN natural language generation`
- `adversarial text generation GAN`

Targeted model/query expansion:

- `CTGAN tabular data`
- `TableGAN deep learning synthetic data`
- `TGAN tabular generative adversarial network`
- `medGAN synthetic electronic health records`
- `EHR GAN synthetic patient records`
- `CTAB-GAN tabular data synthesis`
- `ADS-GAN synthetic data generation`
- `relational tabular GAN`
- `RankGAN text generation`
- `LeakGAN text generation`
- `MaliGAN text generation`
- `MaskGAN text generation`
- `RelGAN text generation`
- `ORGAN Objective-Reinforced Generative Adversarial Networks`
- `Sequence Generative Adversarial Nets with Policy Gradient`

## Output Counts

- Full normalized corpus: 2,290 records
- Topic-filtered corpus: 487 records
- Filtered source split: OpenAlex 366, Crossref 121
- Filtered topic buckets:
  - Structured data: 318
  - Text data: 146
  - Structured + text overlap: 23
- Open-access signal in filtered corpus:
  - OpenAlex OA true: 278
  - OpenAlex OA false: 88
  - Crossref records without OA field: 121

## Filter Method

Records were deduplicated by DOI first, then normalized title + year. The filtered set keeps records with explicit GAN/generative-adversarial evidence plus structured-data indicators, text/discrete-sequence indicators, or known model names such as CTGAN, TableGAN, medGAN, ADS-GAN, SeqGAN, TextGAN, RankGAN, LeakGAN, MaliGAN, MaskGAN, RelGAN, and ScratchGAN.

## Top Countries in Filtered Corpus

Affiliation country counts are based on metadata returned by OpenAlex. Crossref often does not expose country-level affiliation metadata.

- US: 79
- CN: 72
- KR: 24
- GB: 23
- IN: 21
- CA: 17
- DE: 13
- NL: 11
- CH: 9
- ES: 9
- AU: 8
- TW: 8
- JP: 8

## Notable High-Citation Records in Filtered Corpus

- SeqGAN: Sequence Generative Adversarial Nets with Policy Gradient, 2017, DOI `10.1609/aaai.v31i1.10804`
- Objective-Reinforced Generative Adversarial Networks (ORGAN) for Sequence Generation Models, 2017, DOI `10.48550/arxiv.1705.10843`
- MolGAN: An implicit generative model for small molecular graphs, 2018, DOI `10.48550/arxiv.1805.11973`
- Long Text Generation via Adversarial Training with Leaked Information, 2018, DOI `10.1609/aaai.v32i1.11957`
- Survey on Synthetic Data Generation, Evaluation Methods and GANs, 2022, DOI `10.3390/math10152733`
- Generating Multi-label Discrete Patient Records using Generative Adversarial Networks, 2017, DOI `10.48550/arxiv.1703.06490`
- Anonymization Through Data Synthesis Using Generative Adversarial Networks (ADS-GAN), 2020, DOI `10.1109/jbhi.2020.2980262`
- Conditional Wasserstein GAN-based oversampling of tabular data for imbalanced learning, 2021, DOI `10.1016/j.eswa.2021.114582`
- Synthesizing electronic health records using improved generative adversarial networks, 2018, DOI `10.1093/jamia/ocy142`
- Synthesizing Tabular Data using Generative Adversarial Networks, 2018, DOI `10.48550/arxiv.1811.11264`

## Files

- Raw per-query files: `q01_*.jsonl` through `q25_*.jsonl`
- Full raw merged corpus: `gan_structured_text.raw.jsonl`
- Full normalized corpus: `gan_structured_text.normalized.jsonl`
- Full exports: `gan_structured_text.md`, `gan_structured_text.csv`, `gan_structured_text.bib`
- Filtered corpus: `gan_structured_text.filtered.jsonl`
- Filtered exports: `gan_structured_text.filtered.md`, `gan_structured_text.filtered.csv`, `gan_structured_text.filtered.bib`
- Reproducible filter script: `filter_relevant.py`

## Coverage Notes

The corpus is broad and API-derived. It is suitable for literature triage and citation mining, not as a final systematic-review database without manual screening. Crossref abstract coverage varies, and Crossref country metadata is sparse. OpenAlex provides stronger affiliation and open-access metadata but can still include broad survey papers or adjacent-domain work when queries are intentionally inclusive.
