# V2 Post-mortem & V3 Plan

> **Ngày**: 2026-05-12  
> **Trạng thái**: V2 training done → phân tích → chuẩn bị V3 fix

---

## Tình hình sau V2

### Timeline thực tế

| Thời điểm | Sự kiện |
|---|---|
| 09:36 | MLE pretrain hoàn tất: val_ppl = 1.27 (V1 = 1.70) |
| 09:45 | Phát hiện crash UnicodeEncodeError tại step 2000 (`→` ký tự) |
| 09:51 | Fix Unicode, xác nhận phase transition qua --steps 2050 |
| 10:08 | Bắt đầu full 20000-step adversarial training |
| 10:54 | Training hoàn tất — 20 checkpoints (adv_step1000 → adv_step20000 + adv_final) |
| 10:55 | Chạy eval pipeline (22 models × 500 samples, no WAF) |
| 11:05 | Eval xong — **mode collapse chẩn đoán xác nhận** |

### Kết quả định lượng

| Checkpoint | DB exec | AST entropy | ML-IDS evasion | Re-lex unique | Composite |
|---|---|---|---|---|---|
| v2_mle | 3.2% | 3.083 | 3.4% | 0.658 | 0.202 |
| **v2_step1000** | 99.8% | 2.417 | 38.6% | 0.008 | **0.405** |
| v2_step2000 | 100% | 2.565 | 0% | 0.012 | 0.354 |
| v2_refined (final) | 100% | 2.565 | 0% | 0.002 | **0.353** |

- **Best = step1000** (end of warmup). Adversarial và refinement KHÔNG cải thiện.
- AST entropy đóng băng tại 2.5649 từ step 2000 → 20000: generator ra cùng 1 payload.
- `relex_uniqueness = 0.002` = gần như 1 unique payload lặp lại 500 lần.

---

## Root Cause Analysis: Mode Collapse

### Cơ chế

```
G generates payload p → reward_fn(p) = 0.7 (pass custom rules + DB gate)
All batch members get similar reward → advantage(i) = r(i) - mean(r) ≈ 0
∇L_REINFORCE = -log_prob × advantage ≈ 0
Generator không học gì → stuck tại local optimum
```

### Tại sao xảy ra sớm (step 2000)

1. Warmup đã train G đến avg_reward = 0.70 (custom rules + DB gate)
2. Adversarial phase: reward function đổi weight nhưng G đã ở plateau
3. D-score contribution (10-20%) không đủ để phá vỡ plateau
4. Cache hit rate = 96% tại step 9000 → G ra ~17k unique payloads trong 576k calls

### Tại sao refinement không cứu được

- `diversity` weight tăng từ 0.2 → 0.5 nhưng advantage vẫn ≈ 0
- Weight thay đổi không tạo ra gradient nếu tất cả samples có cùng reward
- G loss ≈ 0.0000 suốt refinement phase

---

## V3 Fix Plan: Entropy Regularization

### Thay đổi code

**1. `src/losses.py`** — thêm `reinforce_loss_with_entropy()`:
- REINFORCE loss + entropy bonus (khuyến khích distribution đa dạng)
- `g_loss = reinforce_loss - entropy_coeff × entropy(log_probs)`

**2. `configs/seqgan_v3.yaml`** — thêm params:
- `entropy_coeff_warmup: 0.05`
- `entropy_coeff_adversarial: 0.03`  
- `entropy_coeff_refinement: 0.01`
- `ema_baseline_alpha: 0.05` (thay batch-mean baseline)
- `sample_temperature: 1.1` (exploration noise)

**3. `train_adversarial_v3.py`** — sử dụng V3 loss:
- EMA baseline thay batch mean
- Temperature sampling
- Entropy coefficient theo phase
- Gradient logging để detect collapse sớm

### Metrics để monitor

| Metric | Healthy range | Collapse signal |
|---|---|---|
| g_loss | -0.05 ~ -0.001 | ≈ 0.0000 |
| advantages std | > 0.05 | < 0.001 |
| unique payloads/batch | > 50/64 | < 5/64 |
| entropy of logits | > 2.0 | < 0.5 |

---

## Files thay đổi trong V3

| File | Action | Lý do |
|---|---|---|
| `src/losses.py` | ADD `reinforce_loss_with_entropy()` | Core fix |
| `configs/seqgan_v3.yaml` | CREATE | Entropy params |
| `train_adversarial_v3.py` | CREATE | V3 training loop |

**Không thay đổi**: `src/reward_v2.py`, `src/generator.py`, `pretrain_mle_v2.py`  
(MLE checkpoint tốt, chỉ adversarial loop cần fix)
