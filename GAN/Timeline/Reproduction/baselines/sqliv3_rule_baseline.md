# SQLiV3 Mirror Rule Baseline

- Source URL: `https://github.com/nidnogg/sqliv5-dataset`
- Downloaded commit/hash: `486e182221e48d2cadab63edc217dfd46eb67405`
- Input path: `GAN/Data/raw/sqliv5-dataset/SQLiV3_clean.json`
- Normalized output: `GAN/Data/processed/sqliv3_sqli_normalized.csv`

## Baseline Scope

- Reads online-downloaded `SQLiV3_clean.json`.
- Selects records where `type` is `sqli`.
- Trims leading and trailing whitespace for normalized hashes.
- Stores detailed strings as base64 in CSV artifacts.

## Aggregate Counts

- Normalized rows: 11347
- Unique payload hashes: 11288
- Duplicate rows by payload hash: 59

## Technique Distribution

| Technique | Rows |
| --- | ---: |
| boolean or tautology | 5833 |
| error based | 528 |
| sqli pattern | 2129 |
| stacked query | 28 |
| time based | 610 |
| union select | 2219 |
