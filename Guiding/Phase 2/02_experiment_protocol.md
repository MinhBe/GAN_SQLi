# 02 — Experiment Protocol (Locked Before Training)

> Protocol này được khóa trước khi chạy bất kỳ training nào. Không thay đổi metric sau khi thấy kết quả.

---

## 1. Primary Metrics

Quyết định chính dựa trên:

| Metric | Mô tả | Threshold để pass |
|---|---|---|
| `unique_ratio` | Tỉ lệ payload unique / tổng sinh ra | GAN > MLE |
| `self_bleu3` | Self-BLEU-3 (thấp = đa dạng hơn) | GAN < MLE |
| `token_entropy` | Entropy trung bình mỗi token | GAN ≥ MLE |
| `syntax_validity_rate` | % payload có SQL hợp lệ | GAN ≥ MLE × 0.9 |

## 2. Secondary Metrics

Không dùng để quyết định pass/fail nhưng phải report:

```text
type_accuracy          - % technique_primary đúng với condition
D_score                - discriminator output trên fake samples
proxy_true_gap         - khoảng cách giữa metric proxy và metric thật
copy_rate              - % sample gần như copy từ training set (BLEU-4 > 0.9)
delta_D_real_softened  - D shortcut diagnostic
```

## 3. Random Seeds

```text
MLE seeds:           [42, 123, 456]
Gumbel-SeqGAN seeds: [42, 123, 456]
```

Report: mean ± std + best + worst seed. **Không dùng best run làm kết luận.**

## 4. MLE Sampling Grid

Quét toàn bộ combinations:

```text
temperature : [0.7, 1.0, 1.2]
top_k       : [10, 20, 50]
top_p       : [0.9, 0.95]
max_length  : [64]  (cố định)
```

Tổng: 3 × 3 × 2 = 18 configurations mỗi seed → 54 experiments.

Output per config: 1000 generated samples.

## 5. GAN Configs Được Phép Thử

```text
tau_start   : 1.0
tau_end     : 0.1
tau_schedule: linear over steps
max_steps   : 5000
batch_size  : 64
D_steps_per_G: 5
```

Không thay đổi architecture giữa các seeds.

## 6. Decision Gate

Phase 02 **PASS** (→ tiếp tục Phase 03 full scale) nếu:
- GAN `unique_ratio` > MLE best `unique_ratio`
- GAN `self_bleu3` < MLE best `self_bleu3`
- GAN `syntax_validity_rate` ≥ MLE best × 0.9
- Không có D shortcut rõ ràng (`delta_D_real_softened` < 0.3)

Phase 02 **FAIL** (→ dừng GAN, dùng MLE only) nếu:
- GAN collapse: `unique_ratio` < 0.3 trong tất cả 3 seeds
- GAN copy: `copy_rate` > 0.5
- D shortcut: `delta_D_real_softened` > 0.5

## 7. Quality-Diversity Frontier

So sánh bằng 2D plot: trục X = `unique_ratio`, trục Y = `syntax_validity_rate`.
MLE configs tạo frontier curve. GAN phải nằm trên hoặc cùng frontier.

## 8. Max Training Budget

```text
MLE   : 50 epochs hoặc val_loss không giảm 5 epochs liên tiếp
GAN   : 5000 steps hoặc collapse detected (unique_ratio < 0.1)
```

## 9. Early Stop Rules

MLE early stop:
- Val loss không giảm 5 epochs liên tiếp → save best checkpoint

GAN early stop:
- `unique_ratio` < 0.1 sau step 1000 → collapse, dừng seed này
- D_score > 0.99 liên tục 500 steps → D dominant, log warning

---

*Protocol locked: 2026-05-20*
