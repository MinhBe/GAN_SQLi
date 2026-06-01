# HttpParamsDataset Rule Baseline

- Source URL: `https://github.com/Morzeux/HttpParamsDataset`
- Downloaded commit/hash: `926670a710283f87c05b554680facf3f9530548c`
- Input path: `GAN/Data/raw/httpparamsdataset/payload_full.csv`
- Normalized output: `GAN/Data/processed/httpparams_sqli_normalized.csv`

## Baseline Scope

- Reads online-downloaded `payload_full.csv`.
- Selects rows where source SQLi labels are present.
- Trims leading and trailing whitespace for normalized hashes.
- Stores detailed strings as base64 in CSV artifacts.

## Aggregate Counts

- Normalized rows: 10852
- Unique payload hashes: 10852
- Duplicate rows by payload hash: 0

## Technique Distribution

| Technique | Rows |
| --- | ---: |
| boolean or tautology | 4924 |
| error based | 129 |
| http parameter sqli | 417 |
| stacked query | 1112 |
| time based | 2318 |
| union select | 1952 |
