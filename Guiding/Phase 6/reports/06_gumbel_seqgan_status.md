# 06 - Trạng Thái Gumbel-SeqGAN Smoke

## Phạm Vi

Đã triển khai Gumbel-SeqGAN smoke run cho Phase 6 sau khi MLE/Warmup baseline đạt gate.

Nguồn khởi tạo generator:

- `Guiding/Phase 6/checkpoints/mle_baseline/best.pt`
- MLE source step: `1250`
- Loaded generator keys: `8/8`

Nguồn dữ liệu:

- Train shard: `Guiding/Phase 6/cache/token_shards/train`
- Train source gốc: `Guiding/Phase 5/outputs/full/gold.parquet`
- Không dùng `silver`, `bronze`, `review_queue`, `unknown`, hoặc `needs_ai=True` cho adversarial smoke.

## Script Và Config

Đã tạo:

- `Guiding/Phase 6/phase06_03_gumbel_seqgan_smoke.py`
- `Guiding/Phase 6/configs/gumbel_seqgan_smoke.json`
- `Guiding/Phase 6/configs/gumbel_seqgan_smoke_balanced.json`
- `Guiding/Phase 6/run_phase06_gumbel_smoke.ps1`
- `Guiding/Phase 6/run_phase06_gumbel_balanced_smoke.ps1`

Config được chọn để đi tiếp:

- `Guiding/Phase 6/configs/gumbel_seqgan_smoke_balanced.json`

Lý do:

- Bản smoke đầu tiên không OOM và không collapse, nhưng discriminator thắng quá mạnh ở step 200.
- Bản balanced thêm real-soft smoothing, label smoothing, input noise nhỏ và giảm `d_lr`.
- Bản balanced giữ được D/G cân bằng hơn trong 200 step đầu.

## Kết Quả Smoke Đầu Tiên

Config: `gumbel_seqgan_smoke.json`

| Step | Unique Ratio | Syntax Rate | D Real | D Fake | Nhận định |
|---:|---:|---:|---:|---:|---|
| 50 | 0.9583 | 1.0000 | 0.543 | 0.430 | ổn |
| 100 | 0.9917 | 0.9917 | 0.698 | 0.271 | D bắt đầu mạnh |
| 150 | 0.9750 | 1.0000 | 0.883 | 0.104 | D quá mạnh |
| 200 | 0.9667 | 1.0000 | 0.975 | 0.029 | không collapse nhưng D áp đảo |

Kết luận: không dùng config này để kéo dài.

## Kết Quả Balanced Smoke

Config: `gumbel_seqgan_smoke_balanced.json`

Các thay đổi chính:

- `d_lr`: `0.00001`
- `g_lr`: `0.00002`
- `tau_start -> tau_end`: `0.9 -> 0.7`
- `adv_weight`: `0.1`
- `mle_weight`: `1.0`
- `real_soft_smoothing`: `0.03`
- `d_real_label`: `0.9`
- `d_fake_label`: `0.1`
- `d_input_noise_std`: `0.02`

Mốc 200 step:

| Step | Loss D | Loss G | Loss Adv | Loss MLE | Unique Ratio | Syntax Rate | D Real | D Fake |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 50 | 1.36655 | 0.46929 | 0.71197 | 0.39810 | 0.9500 | 1.0000 | 0.505 | 0.492 |
| 100 | 1.34574 | 0.45522 | 0.73557 | 0.38166 | 0.9667 | 0.9750 | 0.509 | 0.477 |
| 150 | 1.31269 | 0.49754 | 0.77454 | 0.42009 | 0.9500 | 1.0000 | 0.518 | 0.463 |
| 200 | 1.26154 | 0.45710 | 0.77842 | 0.37926 | 0.9917 | 1.0000 | 0.536 | 0.457 |

Mốc extended 500 step:

| Step | Loss D | Loss G | Loss Adv | Loss MLE | Unique Ratio | Syntax Rate | D Real | D Fake |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 300 | 1.11744 | 0.47204 | 0.88825 | 0.38322 | 0.9500 | 1.0000 | 0.580 | 0.392 |
| 400 | 0.96782 | 0.48947 | 1.11163 | 0.37831 | 0.9417 | 1.0000 | 0.660 | 0.344 |
| 500 | 0.85285 | 0.51043 | 1.35178 | 0.37525 | 0.9667 | 1.0000 | 0.736 | 0.282 |

## Artifact Chính

Balanced checkpoint:

- `Guiding/Phase 6/checkpoints/gumbel_seqgan_smoke_balanced/latest.pt`
- `Guiding/Phase 6/checkpoints/gumbel_seqgan_smoke_balanced/best.pt`
- `Guiding/Phase 6/checkpoints/gumbel_seqgan_smoke_balanced/step_00000500.pt`

Balanced samples:

- `Guiding/Phase 6/outputs/gumbel_seqgan_smoke_balanced/samples_step_00000200.jsonl`
- `Guiding/Phase 6/outputs/gumbel_seqgan_smoke_balanced/samples_step_00000500.jsonl`

Progress:

- `Guiding/Phase 6/logs/phase06_gumbel_seqgan_progress.json`

## Gate Hiện Tại

Đã đạt:

- Không OOM trên RTX 3050 Laptop 6GB.
- Loss finite.
- Checkpoint tạo được.
- Resume từ checkpoint balanced hoạt động.
- Unique ratio không collapse trong 500 step.
- Syntax validity giữ mức cao.
- D shortcut diagnostic không báo shortcut.

Cần chú ý:

- Ở step 500, discriminator bắt đầu mạnh hơn (`D_real=0.736`, `D_fake=0.282`).
- Không nên kéo dài ngay bằng cùng config tới full run nếu chưa thêm lịch điều tiết D/G.

## Quyết Định

Gumbel-SeqGAN smoke đã pass ở mức triển khai ban đầu.

Checkpoint nên dùng để phân tích tiếp:

- `Guiding/Phase 6/checkpoints/gumbel_seqgan_smoke_balanced/best.pt`

Nếu chạy tiếp, nên dùng chặng 500 -> 1000 với theo dõi chặt:

- D real/fake không nên tách quá xa quá sớm.
- Unique ratio không dưới `0.90`.
- Syntax rate duy trì gần `1.0`.
- Loss không NaN/Inf.

## Cập Nhật Resume Đến Step 1000

Đã resume balanced checkpoint từ step 500 lên step 1000 theo từng chặng 100 step để theo dõi sát.

Ở step 700, discriminator bắt đầu tách quá xa:

- `D_real`: `0.868`
- `D_fake`: `0.123`
- `unique_ratio`: `0.9583`
- `syntax_validity_rate`: `0.9917`

Không có collapse, nhưng không nên tiếp tục bằng learning-rate cũ. Vì vậy đã thêm config regulated:

- `Guiding/Phase 6/configs/gumbel_seqgan_smoke_regulated.json`
- `Guiding/Phase 6/run_phase06_gumbel_regulated_resume_1000.ps1`

Thay đổi regulated:

- Ép optimizer dùng LR mới khi resume checkpoint.
- `d_lr`: `0.000003`
- `adv_weight`: `0.08`
- `tau_end`: `0.75`
- `real_soft_smoothing`: `0.05`
- `d_real_label`: `0.8`
- `d_fake_label`: `0.2`
- `d_input_noise_std`: `0.04`

Kết quả sau regulated:

| Step | Loss D | Loss G | Loss Adv | Loss MLE | Unique Ratio | Syntax Rate | D Real | D Fake |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 600 | 0.71696 | 0.56094 | 1.72952 | 0.38799 | 0.9917 | 1.0000 | 0.820 | 0.183 |
| 700 | 0.67071 | 0.59406 | 2.06827 | 0.38723 | 0.9583 | 0.9917 | 0.868 | 0.123 |
| 800 | 1.02300 | 0.54289 | 1.95931 | 0.38614 | 0.9583 | 1.0000 | 0.851 | 0.150 |
| 900 | 1.01400 | 0.53484 | 1.84735 | 0.38705 | 0.9667 | 1.0000 | 0.835 | 0.165 |
| 1000 | 1.01017 | 0.52707 | 1.73908 | 0.38794 | 0.9583 | 0.9917 | 0.823 | 0.168 |

Step 1000 artifact:

- `Guiding/Phase 6/checkpoints/gumbel_seqgan_smoke_balanced/latest.pt`
- `Guiding/Phase 6/checkpoints/gumbel_seqgan_smoke_balanced/step_00001000.pt`
- `Guiding/Phase 6/outputs/gumbel_seqgan_smoke_balanced/samples_step_00001000.jsonl`

Gate sau step 1000:

- Không OOM.
- Loss finite.
- Checkpoint/resume hoạt động.
- Unique ratio vẫn trên `0.95`.
- Syntax rate gần `1.0`.
- D shortcut diagnostic vẫn không báo shortcut.
- Discriminator vẫn mạnh, nhưng regulated config đã cải thiện `D_fake` từ `0.123` lên `0.168`.

Quyết định sau step 1000:

- Step 1000 pass cho extended smoke.
- Chưa nên xem đây là full adversarial training.
- Nếu chạy tiếp tới step 1500, phải tiếp tục dùng regulated config hoặc giảm D mạnh hơn nữa nếu `D_fake < 0.12`.

## Cap Nhat Resume Den Step 1500

Da resume checkpoint balanced tu step 1000 len step 1500 bang regulated config va override `--max-steps 1500`.

Ket qua:

| Step | Loss D | Loss G | Loss Adv | Loss MLE | Unique Ratio | Syntax Rate | D Real | D Fake |
|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 1100 | 1.00516 | 0.52493 | 1.70882 | 0.38823 | 0.9833 | 0.9917 | 0.812 | 0.209 |
| 1200 | 1.00404 | 0.51687 | 1.57866 | 0.39058 | 0.9750 | 1.0000 | 0.801 | 0.198 |
| 1300 | 1.01852 | 0.50864 | 1.55068 | 0.38458 | 0.9583 | 1.0000 | 0.791 | 0.231 |
| 1400 | 1.00701 | 0.52680 | 1.50154 | 0.40668 | 1.0000 | 1.0000 | 0.789 | 0.228 |
| 1500 | 1.00586 | 0.49244 | 1.57203 | 0.36668 | 0.9833 | 1.0000 | 0.791 | 0.211 |

Gate sau step 1500:

- Khong OOM tren CUDA.
- Loss finite.
- Unique ratio giu tren `0.95`.
- Syntax rate giu `1.0` o cac moc 1200-1500.
- `D_fake` da phuc hoi len vung `0.20-0.23`, tot hon moc rui ro step 700.
- D shortcut diagnostic van `False`.

Artifact step 1500:

- `Guiding/Phase 6/checkpoints/gumbel_seqgan_smoke_balanced/latest.pt`
- `Guiding/Phase 6/checkpoints/gumbel_seqgan_smoke_balanced/step_00001500.pt`
- `Guiding/Phase 6/outputs/gumbel_seqgan_smoke_balanced/samples_step_00001500.jsonl`
- `Guiding/Phase 6/reports/06_gumbel_seqgan_smoke_report.md`

Quyet dinh sau step 1500:

- Step 1500 pass cho regulated extended smoke.
- Co the chay tiep chang 1500 -> 2000 bang `Guiding/Phase 6/run_phase06_gumbel_regulated_resume_2000.ps1`, nhung chua nen chay dai hon neu chua audit condition.
- Van chua goi day la full adversarial training; can danh gia mau sinh va so sanh voi MLE baseline truoc khi mo rong dai hon.

## Cap Nhat Condition Audit Sau Step 1500

Da them va chay:

- `Guiding/Phase 6/phase06_04_condition_audit.py`
- `Guiding/Phase 6/run_phase06_gumbel_condition_audit.ps1`
- `Guiding/Phase 6/run_phase06_mle_condition_audit.ps1`
- `Guiding/Phase 6/reports/06_gumbel_condition_audit_report.md`
- `Guiding/Phase 6/reports/06_mle_condition_audit_report.md`

Ket qua audit latest sample step 1500:

- Samples: `120`
- SQL signal rate: `1.0000`
- Benign SQL signal rate: `1.0000`
- Technique hint rate: `0.6354`

So sanh MLE latest step 2000 cung heuristic:

- Samples: `120`
- SQL signal rate: `1.0000`
- Benign SQL signal rate: `1.0000`
- Technique hint rate: `0.6771`

Nhan dinh:

- Gate training mechanics da pass, nhung condition separation chua pass.
- Tat ca mau gan nhan `benign` co SQL signal theo heuristic, nen generator chua hoc tach benign khoi payload SQL-like.
- Van de benign khong phai rieng Gumbel; MLE baseline cung co `benign_sql_signal_rate=1.0000`.
- `error_based` co technique hint rate `0.0000` trong ca hai audit heuristic, can xem lai label conditioning hoac heuristic truoc khi dung ket qua adversarial.

Quyet dinh sau audit:

- Khong nen mo rong thanh full adversarial training ngay.
- Buoc tiep theo nen la sua/evaluate conditioning: audit MLE baseline cung thang do, xem lai phan bo `benign`, va co the tach generator attack-only neu muc tieu chinh la sinh payload SQLi.

## Cap Nhat Source Audit Va Nhanh Attack-Only

Da them va chay source audit:

- `Guiding/Phase 6/phase06_05_source_condition_audit.py`
- `Guiding/Phase 6/run_phase06_source_condition_audit.ps1`
- `Guiding/Phase 6/reports/06_source_condition_audit_report.md`
- `Guiding/Phase 6/reports/06_source_condition_audit_report.json`

Ket qua source audit:

| Source | Rows | SQL Signal | Benign SQL Signal | Technique Hint |
|---|---:|---:|---:|---:|
| `gold.parquet` | 1,652,331 | 0.9762 | 0.0012 | 0.8706 |
| `verified_dev.parquet` | 165,836 | 0.9761 | 0.0009 | 0.8671 |
| `verified_test.parquet` | 166,206 | 0.9764 | 0.0009 | 0.8677 |

Nhan dinh source:

- Gold benign chi chiem `1.3502%` train rows.
- Gold benign gan nhu sach theo SQL-signal heuristic (`0.0012`), nen mau benign sinh ra SQL-like la loi imbalance/conditioning, khong phai do gold benign ban.

Da tao nhanh attack-only:

- `Guiding/Phase 6/cache/token_shards_attack_only`
- `Guiding/Phase 6/configs/mle_attack_only_smoke.json`
- `Guiding/Phase 6/run_phase06_attack_only_prep.ps1`
- `Guiding/Phase 6/run_phase06_mle_attack_only_smoke.ps1`
- `Guiding/Phase 6/run_phase06_mle_attack_only_condition_audit.ps1`

Attack-only cache:

| Split | Rows | Shards |
|---|---:|---:|
| train | 1,630,022 | 33 |
| dev | 163,586 | 4 |
| test | 163,976 | 4 |

Included techniques:

- `boolean_blind`
- `time_blind`
- `union_based`
- `error_based`

Attack-only MLE smoke den step 1000:

| Step | Train Loss | Val Loss | Unique Ratio | Syntax Rate |
|---:|---:|---:|---:|---:|
| 100 | 1.63905 | 4.75084 | 1.0000 | 0.9917 |
| 200 | 0.90720 | 5.03639 | 0.8500 | 0.9917 |
| 300 | 0.62791 | 5.23230 | 0.8667 | 1.0000 |
| 400 | 0.56085 | 2.59034 | 0.9333 | 0.9667 |
| 500 | 0.61085 | 1.40747 | 0.9917 | 1.0000 |
| 600 | 0.18081 | 2.51025 | 0.7333 | 1.0000 |
| 700 | 0.10609 | 2.57082 | 0.7167 | 1.0000 |
| 800 | 0.07943 | 2.61264 | 0.6917 | 1.0000 |
| 900 | 0.09009 | 1.49851 | 0.9750 | 1.0000 |
| 1000 | 0.17381 | 1.44707 | 0.9833 | 1.0000 |

Best val checkpoint hien tai van la step 500 (`1.40747`), latest step 1000 gan bang nhung khong tot hon (`1.44707`).

Attack-only condition audit step 1000:

- SQL signal rate: `1.0000`
- Benign SQL signal rate: `0.0000` (khong con benign trong nhanh nay)
- Technique hint rate: `0.6250`
- By technique: `boolean_blind=0.8333`, `time_blind=0.7333`, `union_based=0.9333`, `error_based=0.0000`

Quyet dinh:

- Attack-only la nhanh hop le hon neu muc tieu la sinh payload SQLi, vi tranh condition `benign` bi lech lop.
- Chua nen keo Gumbel/adversarial full-run tren mixed cache.
- Truoc khi GAN tiep, can xu ly `error_based`: audit heuristic, label type, hoac tach/rerank candidate bang evaluator thay vi dua vao syntax keyword-only.
