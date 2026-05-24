# Phase 1 - Data Reality Check Summary

## Mục tiêu

Phase 1 kiểm tra thực tế dữ liệu trước khi train bất kỳ mô hình nào. Câu hỏi chính là: dữ liệu đầu vào đang ở dạng raw, normalized, delexed, mixed hay malformed; có đủ tín hiệu SQLi để train model sinh payload hay không; và phần nào cần loại khỏi train.

## Chuyện gì đã xảy ra

Script Phase 1 đọc các shard CSV nguồn và trích feature nhẹ trên từng payload. Kết quả chính:

- Tổng dòng xử lý: `12,753,953`.
- Phần lớn dữ liệu nằm ở lane `N` normalized-like: `12,749,451` dòng, khoảng `99.96%`.
- Lane `R` raw/encoded-like rất nhỏ: `2,744` dòng.
- Lane `D` delexed-like rất nhỏ: `116` dòng.
- Lane `X` mixed-state: `173` dòng.
- Lane `M` malformed: `1,469` dòng.

Nhận định quan trọng: dữ liệu thực tế không phải một bộ SQLi sạch đã delex sẵn. Nó chủ yếu là normalized SQL/payload-like text, có một lượng lớn noise và cần pipeline delex/dedup/label riêng trước khi train.

## Kiến trúc/logic xử lý

Không có mô hình học máy ở phase này. Đây là pipeline feature engineering:

1. Đọc payload từ các CSV shard nguồn.
2. Trích feature regex:
   - placeholder `__NUM__`, `__STR__`, `__TIME__`, ...
   - literal number/string
   - SQL keyword
   - SQL comment
   - URL/HTML encoding
   - function SQLi thường gặp như `sleep`, `pg_sleep`, `extractvalue`, `updatexml`, ...
   - ký tự lỗi/non-printable
3. Gán lane:
   - `N`: normalized-like
   - `R`: raw/encoded-like
   - `D`: delexed-like
   - `X`: mixed-state
   - `M`: malformed
4. Xuất parquet + report + sample audit.

## File trong Phase 1

| File | Tác dụng |
|---|---|
| `phase01_data_reality_check.py` | Script chính. Đọc dữ liệu nguồn, trích feature regex, phân lane, xuất parquet/report. |
| `phase01_data_reality.parquet` | Bảng dữ liệu sau audit Phase 1. Đây là input cho Phase 2 sampling. |
| `01_data_reality_check.md` | Report tổng kết lane distribution và ví dụ từng lane. |
| `01_lane_distribution.json` | Bản JSON của phân phối lane, dùng cho kiểm tra tự động/ghi log. |
| `01_audit_samples.csv` | Mẫu stratified để review thủ công các lane. |
| `Nhận định Phase 1.md` | File nhận định cũ, hiện gần như rỗng/không phải nguồn chính. |

## Artifact nào nên đọc trước

1. `PHASE_SUMMARY.md` file này.
2. `01_data_reality_check.md`.
3. `phase01_data_reality_check.py` nếu cần biết heuristic lane.
4. `phase01_data_reality.parquet` nếu cần chạy lại sampling.

## Vai trò trong toàn dự án

Phase 1 chứng minh cần làm data foundation nghiêm túc. Nó là lý do xuất hiện Phase 4 full data foundation thay vì train trực tiếp trên dữ liệu thô.
