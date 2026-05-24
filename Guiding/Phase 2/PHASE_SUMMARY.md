# Phase 2 - De-risk Vertical Slice Summary

## Mục tiêu

Phase 2 là vertical slice nhỏ để kiểm tra giả thuyết ban đầu: Gumbel-SeqGAN có đáng scale lên không khi so với Conditional MLE baseline. Phase này cố ý chạy trên slice nhỏ, có protocol khóa trước training, nhiều seed, và metric quality/diversity.

## Chuyện gì đã xảy ra

Pipeline Phase 2:

1. Sample khoảng 40k payload từ Phase 1 theo lane/length/keyword/function.
2. Processing/delex/chuẩn hóa thành slice usable.
3. Gán nhãn technique cho slice.
4. Train Conditional MLE baseline nhiều seed.
5. Train mini Gumbel-SeqGAN challenger nhiều seed.
6. Evaluate MLE vs GAN theo protocol khóa trước.

Kết quả cuối:

- Decision: `FAIL - do not scale GAN` cho full-sequence Gumbel-SeqGAN trên vertical slice.
- MLE tốt nhất: `unique_ratio=0.803`, `self_bleu3=0.014`, `syntax=0.710`.
- GAN mean: `unique_ratio=0.291`, `self_bleu3=0.436`, `syntax_validity_rate=0.615`.
- GAN collapse 3/3 seed theo report Phase 2.
- D-shortcut diagnostic không thấy shortcut rõ, nên lỗi chính không chỉ do D ăn gian representation.

## Kiến trúc mô hình

### Conditional MLE baseline

- Tokenizer đơn giản theo whitespace.
- Vocabulary lọc theo `MIN_FREQ`.
- Input gồm token sequence + condition technique.
- Generator dạng sequence model nhỏ, train bằng cross entropy/teacher forcing.
- Sampling grid: temperature, top-k, top-p.

Vai trò: baseline ổn định để tạo frontier quality/diversity.

### Mini Gumbel-SeqGAN

- Generator khởi tạo từ MLE seed 42.
- Discrete token được relax bằng Gumbel-Softmax.
- Discriminator phân biệt real/fake sequence.
- Loss gồm adversarial signal và cơ chế giữ cú pháp.
- Chạy seeds `[42, 123, 456]`, max `5000` steps, batch `64`, D steps/G `5`, tau `1.0 -> 0.1`.

Vấn đề: full-sequence token generation bị collapse/diversity kém, dù có lúc syntax nhìn tốt.

## File trong Phase 2

| File/thư mục | Tác dụng |
|---|---|
| `02_experiment_protocol.md` | Protocol khóa trước training: metric, seed, gate, early stop. Đây là tài liệu quan trọng nhất về tính khoa học của Phase 2. |
| `phase02_01_sampling.py` | Lấy sample stratified từ `Phase 1/phase01_data_reality.parquet`. |
| `slice_payloads_raw.parquet` | Slice thô sau sampling. |
| `phase02_02_processing.py` | Làm sạch/chuẩn hóa/delex slice. |
| `slice_payloads.parquet` | Slice sau processing. |
| `phase02_03_labeler.py` | Gán nhãn technique/condition cho slice. |
| `slice_labeled.parquet` | Dataset đã gán nhãn, input train MLE/GAN. |
| `phase02_04_mle_train.py` | Train Conditional MLE baseline và tạo `mle_frontier.json`. |
| `phase02_05_gan_train.py` | Train mini Gumbel-SeqGAN challenger. |
| `phase02_06_eval.py` | Tổng hợp metric và quyết định PASS/FAIL. |
| `02_slice_eval_report.md` | Report kết quả chính: MLE thắng, GAN fail/collapse. |
| `eval/mle_frontier.json` | Frontier metric của MLE. Input cho Phase 3 gate. |
| `eval/gan_results.json` | Metric GAN nhiều seed. Input cho Phase 3 gate. |
| `models/mle_baseline/seed_*/best.pt` | Checkpoint MLE từng seed. |
| `models/gumbel_seqgan/seed_*/checkpoint.pt` | Checkpoint GAN từng seed. |
| `Nhận định Phase 2.md` | File nhận định cũ, hiện gần như rỗng/không phải nguồn chính. |

## Vai trò trong toàn dự án

Phase 2 là bằng chứng âm đầu tiên: GAN full-sequence không nên scale mù quáng. Tuy nhiên, vì đề tài yêu cầu GAN, kết quả này không đóng GAN hoàn toàn; nó chỉ đóng hướng full-sequence Gumbel-SeqGAN naive.
