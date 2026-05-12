# V3 Results — Entropy Regularization

> Date: 2026-05-12  
> Config: seqgan_v3.yaml (entropy_coeff warmup=0.05, adv=0.03, ref=0.01; EMA alpha=0.05; temp 1.2→1.1→1.0)  
> Training: 20000 steps, --no_waf

---

## Kết quả so sánh (500 samples, no WAF)

| Model | DB% | AST-H | IDS% | Uniq | Composite |
|---|---|---|---|---|---|
| V2 MLE baseline | 4.0% | 3.120 | 2.8% | 0.686 | 0.208 |
| V2 step1000 (best V2) | 99.8% | 2.418 | 31.4% | 0.010 | 0.394 |
| V2 final (collapsed) | 100% | 2.565 | 0% | 0.002 | 0.353 |
| **V3 step1000** | 99.8% | 2.911 | 0.8% | **0.926** | **0.460** |
| **V3 step2000** ★ | 99.2% | **3.065** | 0% | **1.000** | **0.471** |
| V3 step12000 (collapsed) | 100% | 2.666 | 0% | 0.008 | 0.357 |
| V3 final (collapsed) | 100% | 2.661 | 0% | 0.008 | 0.357 |

**★ Best overall = V3 step2000** (`checkpoints/v3/adv_step2000.pt`)

---

## Phân tích

### V3 vs V2 — Warmup phase (step 1000)

| Metric | V2 step1000 | V3 step1000 | Delta |
|---|---|---|---|
| composite | 0.394 | **0.460** | **+0.066** |
| relex_uniqueness | 0.010 | **0.926** | **+0.916** |
| AST entropy | 2.418 | **2.911** | **+0.493** |
| DB execution | 99.8% | 99.8% | 0 |

Entropy regularization hoàn toàn ngăn collapse trong warmup. Cache hit rate: V3=42% vs V2=93%.

### V3 best vs V2 best

| Metric | V2 step1000 | V3 step2000 | Delta |
|---|---|---|---|
| composite | 0.394 | **0.471** | **+0.077 (+19.5%)** |
| relex_uniqueness | 0.010 | **1.000** | **+0.990** |
| AST entropy | 2.418 | **3.065** | **+0.647** |
| DB execution | 99.8% | 99.2% | -0.6% |
| Custom rules pass | 60.0% | **94.6%** | **+34.6%** |

### V3 training dynamics

```
Warmup (1-2000):
  - unique/64: 6 → 64/64 (recovers by step 750!)
  - H: 1.06 → 1.46 (entropy tăng trong warmup)
  - cache hit rate: 42% (vs V2's 93%)

Adversarial (2000-12000):
  - unique/64: 64 → 6-7 (collapse nhưng chậm hơn V2)
  - H: 1.46 → 0.38 (không collapse hoàn toàn)
  - g_loss ≠ 0 (entropy term duy trì gradient)

Refinement (12000-20000):
  - unique/64: 4/64 (tiếp tục collapse)
  - H: 0.56-0.60 (hơi tăng so với adversarial)
```

---

## Verdict

**V3 cải thiện đáng kể so với V2:**
- Best composite: 0.471 (V3 step2000) vs 0.394 (V2 step1000) = **+19.5%**
- Diversity: relex_uniqueness 1.000 vs 0.010 = **100× improvement**
- Entropy regularization hoạt động trong warmup và early adversarial

**V3 vẫn còn vấn đề:**
- Adversarial collapse vẫn xảy ra sau step 2500 (unique 6-7/64)
- IDS evasion = 0% ở best checkpoint (V2 step1000 có 31.4%)
- Best checkpoint là step2000 (transition point), không phải final

---

## Recommendation: Dừng ở step2000

Cơ chế adversarial (WGAN-GP + REINFORCE) không bổ sung giá trị sau step 2000. Xem xét:

1. **Chỉ dùng V3 warmup** với entropy regularization cao hơn (entropy_coeff=0.1-0.2)
2. **Early stopping** tại phase transition (step warmup_end)
3. Hoặc: Tăng `entropy_coeff_adversarial` từ 0.03 → 0.10 để duy trì diversity

---

## Files

| File | Mô tả |
|---|---|
| `checkpoints/v3/adv_step2000.pt` | **Best model** |
| `checkpoints/v3/adv_step1000.pt` | Good diversity, slightly lower composite |
| `eval/results_v3/v3_adv_step2000.json` | Eval results |
| `eval/samples_v3/v3_adv_step2000.csv` | 500 generated samples |
