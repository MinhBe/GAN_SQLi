# 05 - Full Label System Report

**Run mode:** full
**Label mode:** detector_only
**Rows processed:** 12,753,953
**Elapsed seconds:** 20203.59
**Input:** `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 4\outputs\full\phase04_payload_foundation.parquet`
**Output directory:** `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 5\outputs\full`

## Artifact Rows

| Artifact | Rows |
|---|---:|
| phase05_labeled | 12,753,953 |
| gold | 1,652,331 |
| silver | 268,303 |
| bronze | 10,833,319 |
| review_queue | 11,064,143 |
| verified_dev | 165,836 |
| verified_test | 166,206 |

## Label Sources

| Source | Count | % |
|---|---:|---:|
| tier4_ai_needed | 9,733,440 | 76.317% |
| tier2_structural | 1,603,933 | 12.576% |
| tier1_exact | 1,268,298 | 9.944% |
| benign_classifier | 105,375 | 0.826% |
| tier3_contextual | 42,907 | 0.336% |

## Notes

- This run is detector-only and does not call external APIs or network services.
- `verified_dev.parquet` and `verified_test.parquet` are high-confidence offline candidates from Phase 4 split policy, not human-reviewed labels.
