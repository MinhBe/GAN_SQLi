# OCR Run Report

> Date: 2026-05-21
> Input: `Asset/Total_PDF`
> Output: `Asset/Total_OCR_Rerun_2026_05_21`

## Summary

- Total PDFs processed: 64
- Final usable Markdown files: 54
- OCR MAX retried: 4 files
- Corrupt/unreadable source PDFs: 7
- Too short/block-page sources: 2
- Short manual-check source: 1

## OCR MAX Results

- `Ahsan_2022_Comparative_CGAN.pdf` -> usable, 52,772 bytes
- `Phuong_2024_GAN_IDS_Evasion.pdf` -> usable, 37,352 bytes
- `Rahman_2025_Leveraging_GANs_IDS.pdf` -> usable, 41,802 bytes
- `Deep_Neural_Network_SQLi_2022.pdf` -> still too short, source appears to be a JS/cookie block page

## Not Usable From Current PDF Files

- `Ahmadi_2018_Gap_Weighted_Kernel.pdf` -> `corrupt_or_unreadable_pdf`, pdf_bytes=16, ocr_bytes=0
- `Attack_Model_2012_Penetration_SQLi.pdf` -> `corrupt_or_unreadable_pdf`, pdf_bytes=16, ocr_bytes=0
- `GSQLi_2025_GAN_SQLi_WAF.pdf` -> `corrupt_or_unreadable_pdf`, pdf_bytes=16, ocr_bytes=0
- `Justin_Clarke_2012_SQLi_Book_Preview.pdf` -> `corrupt_or_unreadable_pdf`, pdf_bytes=10, ocr_bytes=0
- `LSTM_on_AST_SQLi_2021.pdf` -> `corrupt_or_unreadable_pdf`, pdf_bytes=16, ocr_bytes=0
- `Muduli_2023_AE_Net_SQLi.pdf` -> `corrupt_or_unreadable_pdf`, pdf_bytes=16, ocr_bytes=0
- `Xu_2023_IE_GAN_SQLi.pdf` -> `corrupt_or_unreadable_pdf`, pdf_bytes=16, ocr_bytes=0
- `OWASP_Top_10_2021.pdf` -> `short_check_manually`, pdf_bytes=26378, ocr_bytes=1850
- `Deep_Neural_Network_SQLi_2022.pdf` -> `too_short_source_or_block_page`, pdf_bytes=5627, ocr_bytes=41
- `Halfond_2006_Classification.pdf` -> `too_short_source_or_block_page`, pdf_bytes=242, ocr_bytes=107

## Next Action

Replace the corrupt/blocked PDFs from original sources before using them as thesis evidence. Do not treat zero-byte OCR outputs as missing evidence against a method; treat them as missing source files.
