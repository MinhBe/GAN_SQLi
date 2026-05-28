# OCR Quality Report

Generated: 2026-05-26T01:39:00

## Environment

- OCR engines available during probe: native_pdf, easyocr, tesseract, pytesseract_wrapper, rapidocr, paddleocr, surya, marker, doctr.
- Runtime probe classified the machine as local-limited, with CUDA available on NVIDIA GeForce RTX 3050 6GB Laptop GPU.

## Sample checks

| PDF | Pages | Mode | Status | Title | Notes |
|---|---:|---|---|---|---|
| 2212.11119v1.pdf | 41 | auto | pass | A Survey on Text Generation using Generative | ok |
| 2502.04786v1.pdf | 13 | auto | pass | Enhancing SQL Injection Detection and Prevention | ok |
| Agrawal_2024_GenAI_Synthetic.pdf | 22 | auto | pass | Not peer-reviewed version | ok |
| CTGAN_IDS_Rare_Attacks_2025_Menssouri.pdf | 6 | auto | pass | A Conditional Tabular GAN-Enhanced Intrusion | ok |
| Goodfellow_2014_GAN.pdf | 9 | auto | pass | Generative Adversarial Nets | ok |
| GSQLi_2025_uncertain_from_old_notes.pdf | 19 | auto | pass | Active Deep Kernel Learning of Molecular Properties from Structural Embeddings | ok |
| Gulrajani_2017_WGAN_GP.pdf | 20 | auto | pass | Improved Training of Wasserstein GANs | ok |
| Le_2024_GSQLi.pdf | 6 | auto | pass | GSQLi: A GAN-based Approach for Adversarial | ok |
| Lu_2022_GA_WGAN_SQLi.pdf | 8 | auto | pass | Trần Quý Nam | ok |
| Lu_2022_GAN_SQLi.pdf | 7 | auto | pass | A GAN-based Method for Generating SQL | ok |
| Nawaz_2025_CTGAN_Web_Attacks.pdf | 23 | auto | pass | Improving Credit Card Fraud Detection through Transformer-Enhanced GAN Oversampling | ok |
| Radford_2015_DCGAN.pdf | 16 | auto | pass | Under review as a conference paper at ICLR 2016 | ok |
| Research+on+SQL+injection+attacks+detection+method+based+on+BERT-GAN.pdf | 9 | auto | pass | 引用格式:罗艺铭,谭玉波,李建平.基于BERT-GAN 的SQL 注入攻击检测方法研究[J]. 微电子学与计算机,2024,41(11):39- | ok |
| Xu_2023_S2CGAN_IDS_possible_IE_GAN.pdf | 12 | auto | pass | Effective Intrusion Detection in Highly Imbalanced | ok |

## Full-run summary

- Markdown outputs retained after cleanup: 14/14 canonical PDF filenames.
- Canonical PDFs OCRed: 14; exact duplicate outputs copied during OCR then deleted after cleanup: 3.
- Non-PDF arXiv page snapshots in `GAN\Paper\PDF` were deleted after cleanup.
- Conservative post-processing applied: ftfy mojibake repair, form-feed removal, whitespace cleanup, obvious lowercase hyphenation joins, and blank-line normalization only.

## Router errors / weak pages

- `Lu_2022_GA_WGAN_SQLi.pdf` page `` mode `quality` in `GAN\Paper\OCR\_sample\ocr_router_errors.json`: exception Unknown argument: show_log
