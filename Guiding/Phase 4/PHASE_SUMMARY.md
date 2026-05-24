# Phase 4 - Full Data Foundation Summary

## Mục tiêu

Phase 4 xây nền dữ liệu full-scale từ toàn bộ `12,753,953` dòng. Đây là phase biến dữ liệu đã audit thành một foundation có thể train/eval:

- canonical text
- delex template
- exact dedup map
- near-duplicate cluster
- literal pools
- cluster-safe train/val/test split

## Chuyện gì đã xảy ra

Full run đã hoàn tất:

- Rows processed: `12,753,953`.
- Elapsed: khoảng `7667.5` giây.
- Lane distribution giữ gần giống Phase 1.
- Exact unique canonical payloads: `12,753,951`.
- Exact duplicate rows: `2`.
- Near-duplicate cluster buckets: `4,131,974`.
- Delex template keys: `268,272`.
- Split cluster-safe:
  - train: `10,217,352`
  - val: `1,265,681`
  - test: `1,021,820`
  - verified_candidate: `249,100`
- Cluster leakage giữa split: `0`.

## Kiến trúc/logic xử lý

Không có model training. Đây là data engineering pipeline:

1. Đọc dữ liệu audit/full payload.
2. Chuẩn hóa canonical payload.
3. Delex literal thành placeholder như `__STR__`, `__NUM__`, `__TIME__`, `__ID__`, `__TABLE__`, `__COMMENT__`.
4. Tạo exact dedup map.
5. Tạo near-duplicate cluster bằng SimHash-prefix bucketing để phù hợp RAM 20GB.
6. Tạo literal pools phục vụ relex hoặc generator/evaluator sau này.
7. Gán split theo cluster để tránh leakage.

## File trong Phase 4

| File/thư mục | Tác dụng |
|---|---|
| `phase04_full_data_foundation.py` | Script chính Phase 4. Xây full data foundation, delex, dedup, cluster split. |
| `run_phase04_full.ps1` | Launcher PowerShell cho full run. |
| `run_phase04_full.cmd` | Launcher CMD cho full run. |
| `PHASE4_ARTIFACT_MANIFEST.md` | Manifest artifact và vị trí output sau cleanup. |
| `logs/phase04_full_run.log` | Log stdout của full run. |
| `logs/phase04_full_run.err.log` | Log stderr của full run. |
| `logs/phase04_full_progress.json` | Progress JSON của full run. |
| `logs/phase04_sanity_progress.json` | Progress của sanity run. |
| `outputs/full/phase04_payload_foundation.parquet` | Dataset foundation chính, input Phase 5. |
| `outputs/full/exact_dedup_map.parquet` | Mapping exact duplicate/canonical payload. |
| `outputs/full/near_dup_clusters.parquet` | Cluster near-duplicate để split/audit leakage. |
| `outputs/full/relex_map.parquet` | Mapping/metadata phục vụ relex. |
| `outputs/full/literal_pools.json` | Pool literal extracted theo type. |
| `outputs/full/splits_cluster_safe.json` | Tóm tắt split và leakage=0. |
| `outputs/full/04_data_foundation_report.md` | Report full run chính. |
| `outputs/sanity/...` | Artifact chạy sanity 1k/10k. Dùng để debug, không phải output chính. |

## Artifact nào nên đọc trước

1. `PHASE_SUMMARY.md` file này.
2. `PHASE4_ARTIFACT_MANIFEST.md`.
3. `outputs/full/04_data_foundation_report.md`.
4. `phase04_full_data_foundation.py` nếu cần biết exact heuristic.

## Vai trò trong toàn dự án

Phase 4 là nền chống leakage và noise. Tất cả Phase 5/6/8 đúng ra phải đọc từ artifact Phase 4/5 thay vì quay lại dữ liệu thô.
