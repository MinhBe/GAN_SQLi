# HttpParamsDataset SQLi Source Card

- Source URL: `https://github.com/Morzeux/HttpParamsDataset`
- Raw source path: `GAN/Data/raw/httpparamsdataset`
- README path: `GAN/Data/raw/httpparamsdataset/README.md`
- Primary CSV path: `GAN/Data/raw/httpparamsdataset/payload_full.csv`
- Downloaded commit/hash: `926670a710283f87c05b554680facf3f9530548c`
- Retrieval mode: online git clone
- Total source records: 31067
- SQLi rows selected: 10852
- Non-SQLi rows skipped: 20215
- Unique SQLi payload hashes: 10852
- Duplicate SQLi rows by payload hash: 0

## Source Schema

| Column | Use |
| --- | --- |
| payload | Encoded into normalized teacher seed rows |
| length | Source-provided payload length metadata |
| attack_type | Filtered to `sqli` |
| label | Confirmed as `sqli` for selected rows |
