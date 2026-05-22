# Nhận Định Phase 6 - GPU Training Baseline

## Bối Cảnh

Phase 5 đã hoàn tất detector-only labeling trên toàn bộ dữ liệu với `12,753,953` dòng. Artifact chính của Phase 5 nằm tại:

- `Guiding/Phase 5/outputs/full/phase05_labeled.parquet`
- `Guiding/Phase 5/outputs/full/gold.parquet`
- `Guiding/Phase 5/outputs/full/silver.parquet`
- `Guiding/Phase 5/outputs/full/bronze.parquet`
- `Guiding/Phase 5/outputs/full/review_queue.parquet`
- `Guiding/Phase 5/outputs/full/verified_dev.parquet`
- `Guiding/Phase 5/outputs/full/verified_test.parquet`

Phase 6 chưa bắt đầu training trong bước này. Mục tiêu của file này là khóa lại nhận định kỹ thuật trước khi triển khai data prep, token shard, MLE warmup và Gumbel-SeqGAN.

## Nhận Định

Không nên train trực tiếp trên toàn bộ `phase05_labeled.parquet` ở vòng đầu.

Lý do chính:

- `bronze`, `review_queue`, `unknown`, và các dòng `needs_ai=True` chiếm tỷ lệ lớn, dễ đưa nhiễu vào generator.
- Full parquet quá lớn so với máy hiện tại nếu load trực tiếp vào RAM hoặc tokenize một lần trong bộ nhớ.
- Vòng đầu cần kiểm tra pipeline GPU, checkpoint/resume, loss curve và diversity trước khi mở rộng dữ liệu.

## Quyết Định Kỹ Thuật

Phase 6 bắt đầu bằng baseline sạch và nhỏ nhất có ý nghĩa:

- Train chính: `Guiding/Phase 5/outputs/full/gold.parquet`
- Eval: `Guiding/Phase 5/outputs/full/verified_dev.parquet`
- Test cuối vòng: `Guiding/Phase 5/outputs/full/verified_test.parquet`
- Silver: chỉ thêm sau khi MLE baseline ổn định.
- Bronze: giữ cho audit hoặc hard-case analysis, không dùng cho train chính ở vòng đầu.
- Review queue, unknown và `needs_ai=True`: không đưa vào train chính ở vòng đầu.

Thứ tự triển khai nên là:

1. Data prep từ `gold.parquet`.
2. Tokenization theo shard, có cache.
3. MLE/Warmup baseline.
4. Resume từ checkpoint và xác nhận reproducibility tối thiểu.
5. Chỉ sau khi baseline đạt gate mới chuyển sang Gumbel-SeqGAN adversarial.

## Cấu Hình Máy

Máy hiện tại:

- GPU: RTX 3050 Laptop 6GB
- RAM: 20GB

Ràng buộc thực tế:

- VRAM 6GB không phù hợp với batch lớn hoặc model lớn.
- RAM 20GB không phù hợp với việc load full `phase05_labeled.parquet` và token cache toàn bộ cùng lúc.
- Cần thiết kế pipeline theo shard, stream/batch đọc dữ liệu, và checkpoint thường xuyên.

Cấu hình khởi điểm đề xuất:

- `batch_size`: 32
- `grad_accum`: 4
- `max_len`: 128
- `embed_dim`: 128
- `hidden_dim`: 256
- Mixed precision: bật
- Token cache: theo shard, không load full parquet vào RAM
- Checkpoint: lưu định kỳ và hỗ trợ resume

Nếu vẫn OOM, giảm theo thứ tự:

1. `batch_size`
2. `max_len`
3. `hidden_dim`
4. `embed_dim`

## Mục Tiêu Phase 6

Mục tiêu gần nhất là MLE/Warmup baseline, không phải adversarial training ngay.

Phase 6 cần chứng minh rằng pipeline có thể:

- Đọc dữ liệu Phase 5 đúng subset.
- Tokenize và cache theo shard.
- Train trên GPU RTX 3050 6GB mà không OOM.
- Ghi checkpoint và resume được.
- Sinh sample có diversity tối thiểu.

Gumbel-SeqGAN chỉ nên triển khai sau khi MLE baseline đã ổn định, vì adversarial training sẽ khuếch đại lỗi từ dữ liệu nhiễu, tokenization sai, checkpoint lỗi hoặc collapse sớm.

## Gate Tiếp Tục

Chỉ chuyển sang Gumbel-SeqGAN adversarial khi MLE baseline đạt các điều kiện sau:

- Không OOM trong ít nhất một lượt train đại diện.
- Loss giảm ổn định, không NaN/Inf.
- Checkpoint tạo được và resume chạy tiếp đúng.
- Sample có diversity, không lặp một mẫu hoặc một template quá sớm.
- Unique ratio đủ tốt trên sample eval.
- Không có dấu hiệu mode collapse sớm.

Nếu một trong các điều kiện trên không đạt, tiếp tục sửa MLE baseline hoặc data pipeline trước khi chuyển sang GAN.

## Phạm Vi Bước Này

Bước hiện tại chỉ tạo nền tảng tổ chức Phase 6 và ghi nhận định kỹ thuật trước triển khai.

Chưa thực hiện:

- Chưa tạo script data prep.
- Chưa tạo token shard.
- Chưa train MLE.
- Chưa chạy Gumbel-SeqGAN.

