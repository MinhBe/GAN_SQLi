# 06 - Trạng Thái Triển Khai MLE Baseline

## Phạm Vi Đã Thực Hiện

Phase 6 đã được triển khai theo `00_Nhan_Dinh_Phase_6.md` ở mức MLE/Warmup baseline, chưa chuyển sang Gumbel-SeqGAN.

Các thành phần đã tạo:

- `configs/mle_baseline.json`
- `phase06_01_tokenize_shards.py`
- `phase06_02_mle_train.py`
- `run_phase06_smoke.ps1`
- `run_phase06_full_prep.ps1`
- `run_phase06_mle_train.ps1`

## Dữ Liệu Và Shard

Nguồn train chính vẫn là `Guiding/Phase 5/outputs/full/gold.parquet`.

Kết quả full token shard:

| Split | Rows | Shards |
|---|---:|---:|
| train | 1,652,331 | 34 |
| dev | 165,836 | 4 |
| test | 166,206 | 4 |

Tokenizer:

- Text column: `payload_delex_v5`
- Condition column: `technique_primary`
- `max_len`: 128
- `min_freq`: 3
- Vocab size: 1,601
- Techniques: `benign`, `boolean_blind`, `time_blind`, `union_based`, `error_based`, `unknown`

Cache chính:

- `Guiding/Phase 6/cache/token_shards/manifest.json`
- `Guiding/Phase 6/cache/token_shards/vocab.json`
- `Guiding/Phase 6/cache/token_shards/techniques.json`

## Cấu Hình Máy Đã Dùng

- GPU: RTX 3050 Laptop 6GB
- RAM mục tiêu: 20GB
- `batch_size`: 32
- `grad_accum`: 4
- `max_len`: 128
- `embed_dim`: 128
- `hidden_dim`: 256
- Mixed precision: bật trên CUDA

## Kết Quả Smoke Test

Smoke test dùng:

- Train: 2,048 dòng
- Dev: 512 dòng
- Test: 512 dòng
- Resume check: có

Kết quả:

- Không OOM.
- Checkpoint `latest.pt` và `best.pt` tạo được.
- Resume chạy tiếp từ step 4 sang step 5.
- Val loss sau resume smoke: 3.680570.
- Unique ratio: 1.0000.
- Syntax validity rate: 0.9000.

## Kết Quả Warmup Trên Full Shard

Đã chạy warmup trên full token shard đến global step 100.

Mốc quan sát:

| Step | Train Loss | Val Loss | Unique Ratio | Syntax Rate |
|---:|---:|---:|---:|---:|
| 25 | 2.73904 | 5.109952 | 0.9667 | 0.8167 |
| 50 | 2.19697 | 4.674549 | 0.9833 | 0.9500 |
| 75 | 1.83812 | 4.540145 | 1.0000 | 1.0000 |
| 100 | 1.59734 | 4.463687 | 1.0000 | 0.9833 |

Checkpoint chính:

- `Guiding/Phase 6/checkpoints/mle_baseline/latest.pt`
- `Guiding/Phase 6/checkpoints/mle_baseline/best.pt`

Sample/report:

- `Guiding/Phase 6/outputs/mle_baseline/history.jsonl`
- `Guiding/Phase 6/reports/06_mle_baseline_report.md`

## Gate Hiện Tại

Đã đạt ở mức warmup ngắn:

- Không OOM trên RTX 3050 6GB.
- Loss train giảm rõ.
- Eval loss giảm trong cùng cấu hình eval từ step 25 đến step 100.
- Checkpoint tạo được.
- Resume hoạt động trên smoke và full checkpoint.
- Sample chưa collapse sớm trong warmup ngắn.

Chưa nên chuyển sang Gumbel-SeqGAN ngay vì cần chạy MLE lâu hơn để đánh giá loss ổn định trên nhiều shard và nhiều mốc eval hơn.

## ETA Cho Lượt Tiếp Theo

Tổng full config 3 epoch ước tính khoảng 38,700 optimizer step.

Khuyến nghị chạy theo chặng:

- Chặng tiếp theo: resume đến step 500 để xác nhận loss/eval ổn hơn.
- ETA step 100 -> 500: khoảng 2-10 phút tùy nhiệt độ GPU và tốc độ đọc đĩa.
- ETA full 3 epoch: nên xem là chạy dài, có thể vài giờ trên RTX 3050 Laptop 6GB.

Lệnh chạy tiếp:

```powershell
powershell -ExecutionPolicy Bypass -File "Guiding\Phase 6\run_phase06_mle_train.ps1"
```

Script sẽ tự resume từ `checkpoints/mle_baseline/latest.pt` và tiếp tục ghi progress vào:

- `Guiding/Phase 6/logs/phase06_mle_progress.json`
- `Guiding/Phase 6/reports/06_mle_baseline_report.md`

