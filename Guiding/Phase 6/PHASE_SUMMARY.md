# Phase 6 - GPU Training, MLE, Gumbel Smoke Summary

## Mục tiêu

Phase 6 đưa pipeline lên GPU RTX 3050 6GB/20GB RAM:

- tokenize theo shard để không quá RAM
- train MLE/Warmup baseline
- kiểm tra checkpoint/resume
- chạy Gumbel-SeqGAN smoke/balanced
- audit condition/source
- mở nhánh attack-only để tránh imbalance benign

## Chuyện gì đã xảy ra

### Nền dữ liệu

Phase 6 ban đầu quyết định không train trên toàn bộ `phase05_labeled.parquet`. Nguồn chính:

- train: `Guiding/Phase 5/outputs/full/gold.parquet`
- dev: `Guiding/Phase 5/outputs/full/verified_dev.parquet`
- test: `Guiding/Phase 5/outputs/full/verified_test.parquet`

### MLE baseline

Conditional LSTM MLE được train trên token shards. Nó chứng minh:

- CUDA nhìn thấy RTX 3050 6GB.
- Không OOM với model/batch bảo thủ.
- Checkpoint và resume hoạt động.
- Có thể sinh samples định kỳ.

### Gumbel-SeqGAN smoke

Gumbel smoke ban đầu không OOM và không collapse ngay, nhưng D thắng quá nhanh. Bản balanced/regulated thêm:

- lower `d_lr`
- label smoothing
- real-soft smoothing
- input noise
- lower/adapted adversarial weight

Kết quả regulated đến step 1500:

- không OOM
- loss finite
- unique ratio giữ trên `0.95`
- syntax rate gần `1.0`
- D shortcut diagnostic không báo shortcut
- nhưng condition separation chưa pass

### Condition/source audit

Source audit cho thấy gold benign sạch, nhưng generated benign lại SQL-like. Vấn đề đến từ imbalance/conditioning, không phải do source benign bẩn.

### Attack-only branch

Tạo nhánh attack-only loại benign:

- train rows: `1,630,022`
- dev rows: `163,586`
- test rows: `163,976`
- techniques: `boolean_blind`, `time_blind`, `union_based`, `error_based`

Attack-only MLE smoke đến step 1000 có syntax cao, unique tốt ở một số checkpoint, nhưng `error_based` technique hint vẫn yếu.

## Kiến trúc mô hình

### Conditional MLE LSTM

- Embedding token.
- Embedding condition/technique.
- LSTM nhỏ.
- Linear head ra vocab logits.
- Loss: cross entropy teacher forcing.
- Sampling: temperature/top-k/top-p.

Vai trò: baseline chính và checkpoint khởi tạo cho adversarial.

### Conditional Gumbel Generator

- Kiến trúc gần MLE LSTM.
- Sinh soft token bằng Gumbel-Softmax.
- Có MLE anchor loss để tránh trôi khỏi cú pháp.

### Conditional Discriminator

- Nhận embedding real/fake + condition.
- LSTM bidirectional/MLP head.
- Binary real/fake objective.

### Regulated adversarial setup

- MLE anchor luôn bật.
- D smoothing/noise để tránh D bão hòa.
- Theo dõi `D_real`, `D_fake`, `unique_ratio`, `syntax`, NaN/OOM.

## File trong Phase 6

| File/thư mục | Tác dụng |
|---|---|
| `00_Nhan_Dinh_Phase_6.md` | Nhận định trước train, cấu hình phù hợp RTX 3050 6GB. |
| `phase06_01_tokenize_shards.py` | Tokenize Phase 5 parquet thành shard `.pt`. |
| `phase06_02_mle_train.py` | Train/eval Conditional MLE baseline. |
| `phase06_03_gumbel_seqgan_smoke.py` | Train Gumbel-SeqGAN smoke/balanced/regulated. |
| `phase06_04_condition_audit.py` | Audit generated samples theo technique condition. |
| `phase06_05_source_condition_audit.py` | Audit source gold/dev/test để so với generated behavior. |
| `configs/mle_baseline.json` | Config MLE main. |
| `configs/mle_attack_only_smoke.json` | Config MLE attack-only branch. |
| `configs/gumbel_seqgan_smoke*.json` | Config các biến thể Gumbel smoke/balanced/regulated. |
| `run_phase06_full_prep.ps1` | Tokenize/prep full gold shards. |
| `run_phase06_mle_train.ps1` | Chạy MLE main. |
| `run_phase06_eval_best.ps1`, `run_phase06_eval_latest.ps1` | Eval checkpoint MLE. |
| `run_phase06_gumbel_*.ps1` | Launcher các run Gumbel. |
| `run_phase06_*condition_audit.ps1` | Launcher audit condition. |
| `run_phase06_attack_only_prep.ps1` | Chuẩn bị attack-only token shards. |
| `cache/token_shards/` | Token shards main gold. |
| `cache/token_shards_attack_only/` | Token shards attack-only. |
| `checkpoints/mle_baseline/` | Checkpoint MLE main. |
| `checkpoints/mle_attack_only_smoke/` | Checkpoint MLE attack-only. |
| `checkpoints/gumbel_seqgan_smoke*/` | Checkpoint Gumbel smoke/balanced. |
| `outputs/mle_baseline/` | Samples/history MLE main. |
| `outputs/mle_attack_only_smoke/` | Samples/history attack-only. |
| `outputs/gumbel_seqgan_smoke*/` | Samples/history Gumbel. |
| `outputs/mle_eval/` | Eval-only samples/json cho MLE checkpoints. |
| `reports/06_mle_baseline_report.md` | Report MLE main. |
| `reports/06_gumbel_seqgan_status.md` | Narrative status Gumbel smoke đến step 1500 và audits. |
| `reports/06_*condition_audit_report.md` | Report condition/source audit. |
| `logs/*.json`, `logs/*.log` | Progress/logs của các run. |

## Vai trò trong toàn dự án

Phase 6 chứng minh training local khả thi trên máy hiện tại. Nó cũng cho thấy full-sequence Gumbel có thể chạy kỹ thuật, nhưng condition/evaluator yếu. Đây là lý do Phase 8 đổi đơn vị GAN sang slot-surgery thay vì tiếp tục full-sequence.
