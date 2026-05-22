# OCR Repair Queue

> Generated: 2026-05-21

## Files in Total_OCR that are too short

- Deep_Neural_Network_SQLi_2022.md (43 bytes)
- Halfond_2006_Classification.md (107 bytes)
- Phuong_2024_GAN_IDS_Evasion.md (55 bytes)
- Rahman_2025_Leveraging_GANs_IDS.md (110 bytes)

## PDF OCR errors from ocr_errors.json

- Ahmadi_2018_Gap_Weighted_Kernel.pdf — exception, pages=0, output_chars=0
- Attack_Model_2012_Penetration_SQLi.pdf — exception, pages=0, output_chars=0
- Deep_Neural_Network_SQLi_2022.pdf — output_too_short, pages=1, output_chars=41
- GSQLi_2025_GAN_SQLi_WAF.pdf — exception, pages=0, output_chars=0
- Justin_Clarke_2012_SQLi_Book_Preview.pdf — exception, pages=0, output_chars=0
- LSTM_on_AST_SQLi_2021.pdf — exception, pages=0, output_chars=0
- Muduli_2023_AE_Net_SQLi.pdf — exception, pages=0, output_chars=0
- Phương pháp phát sinh dữ liệu tấn công đánh lừa IDS học máy dựa trên mạng sinh đối kháng - phuong_phap_phat_sinh_du_lieu_tan_cong_danh_lua_ids_hoc_may.pdf — output_too_short, pages=6, output_chars=31
- Xu_2023_IE_GAN_SQLi.pdf — exception, pages=0, output_chars=0

## Repair policy

1. Try OCR again from Asset/Total_PDF with higher-quality mode.
2. If OCR still fails, mark the paper as missing_source and do not use it as primary evidence.
3. If the paper is SQLi/domain-critical, replace it with a readable source before final thesis synthesis.
