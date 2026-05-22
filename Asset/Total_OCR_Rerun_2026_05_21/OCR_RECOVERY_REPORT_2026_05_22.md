# OCR Recovery Report

> Date: 2026-05-22
> Goal: recover OCR for files that were previously empty, blocked, or invalid.

## Result

- Recovered successfully: `Attack_Model_2012_Penetration_SQLi.pdf` from arXiv, extracted to `Attack_Model_2012_Penetration_SQLi.md`.
- Re-ran OCR MAX for `OWASP_Top_10_2021.pdf`; still short, keep as `manual_check`.
- Tried alternate download for `Deep_Neural_Network_SQLi_2022.pdf`; source remains Cloudflare/JS challenge, not a PDF.
- Tried alternate download for `GSQLi_2025_GAN_SQLi_WAF.pdf`; MDPI PDF endpoint returns Access Denied.
- Tried alternate download for `Halfond_2006_Classification.pdf`; available URLs return 404.

## Still Missing Valid PDF Source

- `Ahmadi_2018_Gap_Weighted_Kernel.pdf` — current file is `error code: 1020`.
- `Deep_Neural_Network_SQLi_2022.pdf` — current file is Cloudflare challenge HTML.
- `GSQLi_2025_GAN_SQLi_WAF.pdf` — current file is `error code: 1020`; alternate MDPI PDF denied.
- `Halfond_2006_Classification.pdf` — current file is 404 HTML.
- `Justin_Clarke_2012_SQLi_Book_Preview.pdf` — current file says `Not found`.
- `LSTM_on_AST_SQLi_2021.pdf` — current file is `error code: 1020`.
- `Muduli_2023_AE_Net_SQLi.pdf` — current file is `error code: 1020`.
- `Xu_2023_IE_GAN_SQLi.pdf` — current file is `error code: 1020`.

## Current Quality Count

- Usable: 55 / 64
- Manual check: 1 / 64
- Reject or missing source: 8 / 64

## Decision

No OCR model can recover text from these missing-source files because they are not valid PDFs. Replace those PDFs with real downloaded files, then run OCR MAX only if native extraction is still empty.
