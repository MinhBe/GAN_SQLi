# Crawl report: IE-GAN and BERT-GAN SQL injection papers

Run date: 2026-05-26
Output directory: `Asset/Total_PDF1`
Skill used: `Skill/research-paper-crawler`

## Queries and filters

- `SQL Injection Attack Sample Generation Based on IE-GAN Xu TrustCom 2023`
  - Sources: OpenAlex, Crossref
  - Year filter: 2023
  - Max results: 10
- `Research on SQL Injection Attacks Detection Method Based on BERT-GAN Luo Tan Li 2024`
  - Sources: OpenAlex, Crossref
  - Year filter: 2024
  - Max results: 10
- `10.19304/J.ISSN1000-7180.2023.0721`
  - Sources: OpenAlex, Crossref
  - Year filter: 2024
  - Max results: 10

## Exact records

1. Xu et al. (2023), `SQL injection attack sample generation based on IE-GAN`
   - DOI: `10.1109/TRUSTCOM60117.2023.00142`
   - Venue: `2023 IEEE 22nd International Conference on Trust, Security and Privacy in Computing and Communications (TrustCom)`
   - Source matched: Crossref
   - PDF status: not downloaded. Crossref/OpenAlex did not expose a clearly open-access PDF URL.

2. Luo, Tan, Li (2024), `Research on SQL injection attacks detection method based on BERT-GAN`
   - DOI: `10.19304/J.ISSN1000-7180.2023.0721`
   - Venue: `Microelectronics & Computer`, 41(11):39-47
   - Source matched: journal site/search index; OpenAlex/Crossref did not return an exact metadata record
   - PDF status: not downloaded. `robots.txt` disallows the journal HTML and PDF paths for the crawler user agent.

## Files written

- `ie_gan_search.jsonl`: raw OpenAlex/Crossref search results for IE-GAN query
- `bert_gan_search.jsonl`: raw OpenAlex/Crossref search results for BERT-GAN title query
- `bert_gan_doi_search.jsonl`: raw OpenAlex/Crossref search results for BERT-GAN DOI query
- `target_papers.filtered.jsonl`: normalized two-record target metadata file
- `pdf_download_manifest.csv`: PDF download attempt manifest
- `pdf_download_stats.json`: PDF download stats
- `Crawl_Report_IEGAN_BERTGAN_20260526.md`: this report

## Deduplication and access policy

- Deduplication key: DOI where available, otherwise normalized title and year.
- Direct PDF downloading was attempted only through the skill's open-access PDF downloader.
- No paywall, CAPTCHA, login, publisher anti-bot, or robots.txt restriction was bypassed.

## Coverage gaps

- IEEE record is metadata-complete enough for citation, but full text is not confirmed open access.
- BERT-GAN has a journal PDF URL visible in public search results, but the journal robots policy blocks crawler access, so only metadata was retained.
