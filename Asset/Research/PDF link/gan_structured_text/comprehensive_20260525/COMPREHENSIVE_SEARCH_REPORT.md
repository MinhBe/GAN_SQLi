# Comprehensive Crawl Report: GAN for Structured and Text Data

Date: 2026-05-25

## Scope

Topic: GAN/generative-adversarial models for structured data and text/discrete sequence data.

Year range: 2014-2026.

Region filter: global; no country or affiliation filter was applied.

Document scope: metadata only. No PDFs were downloaded.

## Collection Method

The crawl used the local `research-paper-crawler` skill with API-first collection:

- OpenAlex
- Crossref

The run did not crawl publisher HTML pages, bypass paywalls, access CAPTCHA-protected sites, or download restricted PDFs.

## Query Coverage

The comprehensive run used 60 queries covering:

- General GAN + tabular / structured / relational / categorical / mixed-type data
- Synthetic tabular data, privacy-preserving synthesis, oversampling, imbalanced data
- EHR, patient records, clinical and healthcare synthetic data
- Named structured-data models: CTGAN, CTAB-GAN, TableGAN, TGAN, medGAN, ADS-GAN, GANBLR, RCTGAN, MolGAN
- Graph, relational, molecular graph, time-series, and temporal structured data
- Text generation, natural language generation, discrete sequence generation
- Named text/discrete-sequence models: SeqGAN, TextGAN, RankGAN, LeakGAN, MaliGAN, MaskGAN, RelGAN, SentiGAN, ScratchGAN, StepGAN, ORGAN
- Adjacent SQL/query/code generation terms using GAN/discrete sequence language

The exact query list is saved in `queries.json`.

## Output Counts

- Per-query JSONL files: 60
- Full normalized corpus after deduplication: 8,011 records
- Topic-filtered corpus: 1,662 records
- Full source split:
  - OpenAlex: 5,254
  - Crossref: 2,757
- Filtered source split:
  - OpenAlex: 1,253
  - Crossref: 409

## Filtered Topic Buckets

Records can belong to more than one bucket.

- Structured/tabular: 1,091
- Relational/graph: 455
- Text/discrete sequence: 291
- EHR/health: 258
- Time series/temporal: 188

## Filtered Year Distribution

- 2026: 93
- 2025: 290
- 2024: 306
- 2023: 320
- 2022: 197
- 2021: 153
- 2020: 119
- 2019: 79
- 2018: 66
- 2017: 35
- 2016: 1
- 2015: 2
- 2014: 1

## Top Affiliation Countries in Filtered Corpus

OpenAlex provides the strongest country metadata. Crossref records often do not include country-level affiliation data.

- CN: 301
- US: 242
- GB: 94
- IN: 74
- KR: 67
- CA: 60
- DE: 44
- AU: 37
- ES: 33
- IT: 30
- JP: 28
- SA: 27
- PK: 26
- FR: 25
- CH: 23
- SG: 23
- NL: 22
- MY: 21
- TW: 18
- HK: 17

## Open-Access Signal

Filtered corpus:

- Open-access true: 920
- Open-access false: 333
- No OA field, mostly Crossref records: 409

## Notable Seed Papers and Model Families

These records are useful starting points for manual review and citation chaining:

- Generative Adversarial Networks, 2014, DOI `10.48550/arxiv.1406.2661`
- SeqGAN: Sequence Generative Adversarial Nets with Policy Gradient, 2017, DOI `10.1609/aaai.v31i1.10804`
- Objective-Reinforced Generative Adversarial Networks for Sequence Generation Models, 2017, DOI `10.48550/arxiv.1705.10843`
- Long Text Generation via Adversarial Training with Leaked Information, 2018, DOI `10.1609/aaai.v32i1.11957`
- MaskGAN: Better Text Generation via Filling in the Blank, 2018, DOI `10.48550/arxiv.1801.07736`
- RelGAN: Relational Generative Adversarial Networks for Text Generation, 2018, OpenAlex record available
- Synthesizing Tabular Data using Generative Adversarial Networks, 2018, DOI `10.48550/arxiv.1811.11264`
- Synthesizing electronic health records using improved generative adversarial networks, 2018, DOI `10.1093/jamia/ocy142`
- Generating Multi-label Discrete Patient Records using Generative Adversarial Networks, 2017, DOI `10.48550/arxiv.1703.06490`
- Anonymization Through Data Synthesis Using Generative Adversarial Networks (ADS-GAN), 2020, DOI `10.1109/jbhi.2020.2980262`
- Conditional Wasserstein GAN-based oversampling of tabular data for imbalanced learning, 2021, DOI `10.1016/j.eswa.2021.114582`
- Survey on Synthetic Data Generation, Evaluation Methods and GANs, 2022, DOI `10.3390/math10152733`
- GraphGAN: Graph Representation Learning With Generative Adversarial Nets, 2018, DOI `10.1609/aaai.v32i1.11872`
- MolGAN: An implicit generative model for small molecular graphs, 2018, DOI `10.48550/arxiv.1805.11973`

## Files

Core corpus:

- `gan_structured_text.comprehensive.raw.jsonl`
- `gan_structured_text.comprehensive.normalized.jsonl`
- `gan_structured_text.comprehensive.csv`
- `gan_structured_text.comprehensive.md`
- `gan_structured_text.comprehensive.bib`

Filtered corpus:

- `gan_structured_text.comprehensive.filtered.jsonl`
- `gan_structured_text.comprehensive.filtered.csv`
- `gan_structured_text.comprehensive.filtered.md`
- `gan_structured_text.comprehensive.filtered.bib`

Reproducibility and metadata:

- `queries.json`
- `run_comprehensive_crawl.py`
- `filter_comprehensive.py`
- `build_stats.py`
- `crawl_stats.json`

## Limitations

This is a high-recall crawl. It intentionally casts a wide net and therefore includes adjacent papers, surveys, and some false positives where metadata contains model names or broad GAN terminology. Use the filtered corpus for triage, then manually screen titles/abstracts before treating papers as in-scope for a systematic review.

Coverage is strongest for OpenAlex and Crossref-indexed literature. Russia, China, Korea, Japan, and India may have additional local-indexed literature in CNKI, Wanfang, KCI/KISTI, J-STAGE, CiNii, CyberLeninka, and thesis repositories that may require permitted manual export or official APIs.
