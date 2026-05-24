# Phase 8 - GAN Reopened as Paired Masked Surgery Summary

## Mục tiêu

Phase 8 mở lại GAN vì đề tài yêu cầu GAN là thành phần tối thiểu, nhưng không quay lại full-sequence GAN cũ. Hướng mới là:

```text
Paired Masked Payload-Surgery GAN
```

Ý tưởng: giữ khung/delex template SQLi, chỉ sinh hoặc sửa slot/local content. Discriminator so real/fake trong cùng frame/condition để giảm shortcut.

## Chuyện gì đã xảy ra

### 8A - Data/evaluator hardening

Đã triển khai:

- delex-template leakage audit
- error-based delex audit
- evaluator contract
- delex cluster split smoke/full

Split full:

- train: `1,561,364`
- dev: `150,694`
- test: `272,315`
- train/dev/test template overlap: `0`

### 8B - Re-score existing outputs

Evaluator contract đã chấm:

- MLE attack-only step 1000
- Gumbel balanced step 1500

Các metric tách thành:

- validity
- novelty
- conditioning debug
- evasion

Evasion hiện chưa có detector/WAF result nên vẫn báo `missing_detector_results`.

### 8C - Anchor-only và mutation-engine baselines

Đã triển khai `phase08_05_surgery_baselines.py`:

- Anchor-only masked infiller: supervised CE reconstruction trên placeholder slots.
- Mutation-engine: deterministic non-learned mutation baseline.

Full-lite trên RTX 3050 6GB:

- train rows: `300,000`
- dev rows: `25,000`
- batch: `64`
- max steps: `1000`
- mixed precision: bật
- dev slot accuracy anchor-only: `0.9821`

Evaluator full-lite:

| Model | Novel vs train | Batch duplicate | Ghi chú |
|---|---:|---:|---|
| Anchor-only | `0.3125` | `0.4250` | slot reconstruction mạnh nhưng bám train |
| Mutation-engine | `0.6925` | `0.1925` | novelty mạnh nhất hiện tại |

### 8D - H5' paired surgery GAN pilot

Đã triển khai `phase08_06_paired_surgery_gan.py`.

Các run đã chạy:

| Run | Kết quả kỹ thuật | Novel vs train | Batch duplicate |
|---|---|---:|---:|
| H5' smoke | pass, không OOM, D không bão hòa | `0.2250` | `0.1667` |
| H5' full-lite base | pass, dev slot acc `0.9870` | `0.1325` | `0.4275` |
| H5' full-lite adv015 | pass | `0.1425` | `0.4225` |
| H5' adv015 sampled | pass, GAN tốt nhất hiện tại | `0.1750` | `0.3900` |
| H5' max local | pass, mở action space local | `0.5950` | `0.2550` |
| H5' max aggressive | pass, novelty GAN mạnh nhất hiện tại | `0.8050` | `0.1725` |

Detector/evasion proxy đã được thêm bằng `phase08_07_detector_evasion_score.py`. Bảng core có detector:

| Model | Novel vs train | Detector bypass proxy |
|---|---:|---:|
| Anchor-only full-lite | `0.3125` | `0.1050` |
| Mutation-engine full-lite | `0.6925` | `0.1000` |
| H5' max local | `0.5950` | `0.1525` |
| H5' max aggressive | `0.8050` | `0.2325` |

Nhận định cập nhật: GAN slot-surgery chạy ổn trên GPU 6GB, không collapse/OOM. Placeholder-only GAN bám anchor và novelty yếu, nhưng khi mở action space sang operator/comment/boolean/technique tokens, H5' max aggressive đã vượt mutation-engine ở novelty template (`0.8050` vs `0.6925`) và detector-bypass proxy (`0.2325` vs `0.1000`). Tradeoff là technique hint giảm, nên claim hiện tại phải bounded: thắng novelty/evasion-proxy, chưa claim WAF thật hoặc condition fidelity toàn diện.

## Kiến trúc mô hình

### Anchor-only masked infiller

- Input: delex payload frame có placeholder slot bị mask.
- Condition: technique.
- Model: compact Conv encoder.
- Loss: cross entropy trên slot bị mask.
- Output: fill token cho slot.

Vai trò: supervised baseline bắt buộc. Nếu GAN không thắng anchor-only thì không được claim adversarial component có ích.

### Mutation-engine baseline

- Không học.
- Dùng rule deterministic để thay comment/operator/boolean/union/time placeholder.
- Vai trò: baseline novelty rẻ nhưng mạnh.

### H5' Paired Surgery GAN

Generator:

- Kiến trúc Conv giống anchor-only.
- Khởi tạo từ anchor checkpoint nếu shape compatible.
- Sinh logits cho slot bị mask.
- Loss:
  - `anchor_weight * CE`
  - `adv_weight * adversarial_loss`
  - `- entropy_weight * slot_entropy`

Discriminator:

- Paired discriminator.
- Input gồm:
  - masked frame
  - filled payload embedding real/fake
  - condition
  - position embedding
- Pool mean/max theo valid mask.
- Output binary real/fake.

Guardrail:

- mixed precision trên CUDA
- batch nhỏ
- D freeze threshold khi D accuracy quá cao
- NaN/OOM checks
- evaluator contract sau mỗi run

## File trong Phase 8

| File/thư mục | Tác dụng |
|---|---|
| `00_Phase8_Positioning_Delta_GSQLi.md` | Positioning khoa học: Phase 8 khác GSQLi ở đâu, evaluation contract, interpretation. |
| `phase08_01_delex_template_leakage_audit.py` | Audit leakage theo normalized delex-template hash. |
| `phase08_02_error_based_delex_audit.py` | Audit riêng `error_based`, kiểm tra delex/representation. |
| `phase08_03_evaluator_contract.py` | Evaluator contract tách validity/novelty/conditioning/evasion. |
| `phase08_04_build_delex_cluster_split.py` | Build train/dev/test split theo delex-template cluster, overlap=0. |
| `phase08_05_surgery_baselines.py` | Anchor-only masked infiller + mutation-engine baseline. |
| `phase08_06_paired_surgery_gan.py` | H5' paired masked surgery GAN pilot. |
| `phase08_07_detector_evasion_score.py` | Detector/WAF-style offline proxy, xuất CSV `sample_id,detected` cho evaluator. |
| `run_phase08_delex_*`, `run_phase08_error_*`, `run_phase08_evaluator_*` | Launcher audit/evaluator. |
| `run_phase08_surgery_baselines_smoke.ps1` | Chạy baseline smoke. |
| `run_phase08_surgery_baselines_full_lite.ps1` | Chạy baseline full-lite phù hợp RTX 3050 6GB. |
| `run_phase08_paired_surgery_gan_smoke.ps1` | Chạy H5' smoke. |
| `run_phase08_paired_surgery_gan_full_lite.ps1` | Chạy H5' full-lite. |
| `run_phase08_paired_surgery_gan_max_local.ps1` | Chạy H5' local action-space max run. |
| `run_phase08_paired_surgery_gan_max_aggressive.ps1` | Chạy H5' aggressive action-space max run. |
| `run_phase08_detector_core_comparison.ps1` | Chấm detector + evaluator có detector cho anchor/mutation/GAN max. |
| `outputs/delex_cluster_split*/` | Dataset split theo delex-template cluster. |
| `outputs/surgery_baselines_*` | Samples anchor-only/mutation-engine. |
| `outputs/paired_surgery_gan_*` | Samples H5' GAN. |
| `checkpoints/surgery_baselines_*` | Checkpoint anchor-only. |
| `checkpoints/paired_surgery_gan_*` | Checkpoint H5' generator/discriminator. |
| `reports/08_delex_*` | Reports audit leakage/split. |
| `reports/08_evaluator_*` | Reports evaluator contract cho từng sample source. |
| `reports/08_surgery_baselines_*` | Reports baseline anchor/mutation. |
| `reports/08_paired_surgery_gan_*` | Reports H5' GAN runs. |
| `reports/08_gan_max_push_summary.md` | Summary riêng cho giai đoạn đẩy GAN tối đa. |
| `outputs/detector_results/` | CSV detector results dùng làm input `--detector-results`. |
| `logs/phase08_*progress.json` | Progress của baseline/GAN run gần nhất. |

## Vai trò trong toàn dự án

Phase 8 là hướng GAN chính hiện tại. Khi viết luận văn, câu chuyện nên là:

1. Full-sequence GAN fail có bằng chứng Phase 2/3/6.
2. Đổi đơn vị sinh sang slot-surgery để phù hợp SQLi.
3. H5' GAN chạy được và được so với anchor-only/mutation-engine.
4. Hiện tại GAN chưa thắng novelty baseline, nhưng đây là kết quả thực nghiệm có giá trị; bước tiếp theo là mở rộng action space sang operator/comment/obfuscation slots và thêm detector/WAF evasion axis.
