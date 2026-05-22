# Tổng kết Phase 5

- Chế độ chạy: `full`
- Chế độ gán nhãn: `detector_only`
- Tổng số dòng xử lý: `12,753,953`
- Gold/Silver/Bronze: `1,652,331` / `268,303` / `10,833,319`
- Review queue: `11,064,143`
- Verified dev/test candidates: `165,836` / `166,206`
- Conflict rows: `10,828,030` (84.8994%)

## Phân phối technique

| Technique | Count | % |
|---|---:|---:|
| unknown | 9,733,440 | 76.317% |
| union_based | 1,623,457 | 12.729% |
| boolean_blind | 639,668 | 5.015% |
| time_blind | 558,870 | 4.382% |
| benign | 105,375 | 0.826% |
| error_based | 93,143 | 0.730% |

## Split integrity

Phase 5 preserves Phase 4 `split` and `near_dup_cluster_id`; no reassignment is performed in this phase.
