# Phase 5 - Full Label System Summary

## Mục tiêu

Phase 5 gán nhãn toàn bộ dữ liệu foundation từ Phase 4 bằng detector-only/offline labeling. Nó tạo các split chất lượng `gold/silver/bronze/review_queue`, nhãn technique, DB hint, confidence, conflict flag và verified dev/test.

## Chuyện gì đã xảy ra

Full labeling đã chạy xong:

- Run mode: `full`.
- Labeling mode: `detector_only`.
- Tổng dòng xử lý: `12,753,953`.
- Gold/Silver/Bronze:
  - gold: `1,652,331`
  - silver: `268,303`
  - bronze: `10,833,319`
- Review queue: `11,064,143`.
- Verified dev/test candidates:
  - dev: `165,836`
  - test: `166,206`
- Conflict rows: `10,828,030` (`84.8994%`).

Phân phối technique:

- unknown: `9,733,440` (`76.317%`)
- union_based: `1,623,457`
- boolean_blind: `639,668`
- time_blind: `558,870`
- benign: `105,375`
- error_based: `93,143`

Nhận định: full corpus có rất nhiều unknown/conflict. Vì vậy Phase 6 không train trực tiếp trên toàn bộ `phase05_labeled.parquet`; ưu tiên `gold.parquet` và verified split.

## Kiến trúc/logic xử lý

Không train model neural. Đây là labeling cascade/offline detector:

1. Đọc `Guiding/Phase 4/outputs/full/phase04_payload_foundation.parquet`.
2. Áp rules/detectors để suy ra:
   - `is_sqli`
   - `technique_primary`
   - `sqli_type`
   - `db_family`
   - confidence/band
   - quality band
   - conflict flags
3. Chia output thành:
   - `gold`: đủ tự tin để train baseline ban đầu
   - `silver`: có thể dùng sau khi baseline ổn
   - `bronze`: chủ yếu audit/hard-case
   - `review_queue`: cần review/không dùng train chính
4. Giữ nguyên split/cluster từ Phase 4, không tự reassignment.

## File trong Phase 5

| File/thư mục | Tác dụng |
|---|---|
| `phase05_full_label_system.py` | Script chính labeling full/sanity. |
| `run_phase05_full.ps1` | Launcher PowerShell cho full run. |
| `run_phase05_full.cmd` | Launcher CMD cho full run. |
| `PHASE5_ARTIFACT_MANIFEST.md` | Manifest cấu trúc, input/output/report/log. |
| `Tổng kết Phase 5.md` | Summary kết quả full run. |
| `logs/phase05_full_run.log` | Log stdout full run. |
| `logs/phase05_full_run.err.log` | Log stderr full run. |
| `logs/phase05_full_progress.json` | Progress full run. |
| `logs/phase05_sanity_progress.json` | Progress sanity run. |
| `outputs/full/phase05_labeled.parquet` | Dataset full đã gán nhãn. Không nên train trực tiếp toàn bộ ngay. |
| `outputs/full/gold.parquet` | Dataset sạch nhất, input chính Phase 6 baseline. |
| `outputs/full/silver.parquet` | Dữ liệu có thể mở rộng sau khi MLE ổn. |
| `outputs/full/bronze.parquet` | Dữ liệu nhiễu/hard-case, không dùng train chính ban đầu. |
| `outputs/full/review_queue.parquet` | Dòng cần review, không dùng train chính. |
| `outputs/full/verified_dev.parquet` | Dev/eval candidate đã tách. |
| `outputs/full/verified_test.parquet` | Test candidate đã tách. |
| `outputs/full/label_distribution.json` | Phân phối nhãn máy đọc được. |
| `outputs/full/conflict_summary.json` | Summary conflict. |
| `outputs/sanity/...` | Artifact chạy sanity. |
| `reports/05_full_label_system_report.md` | Report full label system. |
| `reports/05_label_distribution.md` | Report phân phối nhãn. |
| `reports/05_conflict_report.md` | Report conflict. |
| `reports/05_gold_quality_report.md` | Report chất lượng gold. |

## Vai trò trong toàn dự án

Phase 5 tạo dataset train/eval chính cho Phase 6 và Phase 8. Nó cũng chỉ ra rủi ro lớn nhất: nhãn unknown/conflict rất nhiều, nên mọi claim mô hình phải nói rõ subset dùng train.
