# OCR Quality Report

> Date: 2026-05-22
> Input checked: `Asset/Total_OCR_Rerun_2026_05_21`

## Summary

- Paper markdown files checked: 64
- Usable by content checks: 55
- Manual check: 1
- Reject / missing-source: 8

## Flag Counts

- `block_page`: 1
- `empty`: 6
- `not_found_page`: 1
- `short_manual_check`: 1
- `too_short`: 2

## Reject / Missing Source

- `Ahmadi_2018_Gap_Weighted_Kernel.md`: chars=0, words=0, flags=`empty`
- `Deep_Neural_Network_SQLi_2022.md`: chars=41, words=6, flags=`too_short|block_page`
- `GSQLi_2025_GAN_SQLi_WAF.md`: chars=0, words=0, flags=`empty`
- `Halfond_2006_Classification.md`: chars=103, words=18, flags=`too_short|not_found_page`
- `Justin_Clarke_2012_SQLi_Book_Preview.md`: chars=0, words=0, flags=`empty`
- `LSTM_on_AST_SQLi_2021.md`: chars=0, words=0, flags=`empty`
- `Muduli_2023_AE_Net_SQLi.md`: chars=0, words=0, flags=`empty`
- `Xu_2023_IE_GAN_SQLi.md`: chars=0, words=0, flags=`empty`

## Manual Check

- `OWASP_Top_10_2021.md`: chars=1748, words=257, alnum=0.827, flags=`short_manual_check`

## Recovered / Repaired

- `Attack_Model_2012_Penetration_SQLi.md`: status=`usable`, chars=29342, words=4551, flags=`none`
- `Ahsan_2022_Comparative_CGAN.md`: status=`usable`, chars=52625, words=8413, flags=`none`
- `Phuong_2024_GAN_IDS_Evasion.md`: status=`usable`, chars=29869, words=8758, flags=`none`
- `Rahman_2025_Leveraging_GANs_IDS.md`: status=`usable`, chars=41668, words=6037, flags=`none`
- `OWASP_Top_10_2021.md`: status=`manual_check`, chars=1748, words=257, flags=`short_manual_check`
- `Deep_Neural_Network_SQLi_2022.md`: status=`reject`, chars=41, words=6, flags=`too_short|block_page`

## Decision

Use files with `quality_status=usable` for literature synthesis. Files marked `reject` still need valid source PDFs before being cited as evidence.
