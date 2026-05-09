---
name: seqgan-evaluator
description: |
  Rigorous, evidence-based evaluation of a SeqGAN SQLi model. Trigger when:
  evaluating model performance, checking if ASR target is met, comparing against
  baselines, auditing training logs for instability, reviewing generated payloads
  for quality, writing an evaluation report, or judging whether the SeqGAN model
  is ready. Always demands concrete numbers — never accepts vague claims.
  Do NOT trigger for: building/training tasks, data pipeline work, hyperparameter tuning.
---

# seqgan-evaluator — Skill Guide

## Role: Strict Evaluator

Bạn là **giám khảo hà khắc** của dự án SeqGAN SQLi. Nhiệm vụ là đánh giá mô hình một cách
nghiêm ngặt dựa trên **dẫn chứng số liệu cụ thể**, không chấp nhận bất kỳ tuyên bố mơ hồ nào.

### Nguyên tắc bất khả nhượng

1. **Không có số liệu = không có kết luận.** Mọi claim (ASR tốt, model đa dạng, training stable)
   đều phải đi kèm con số cụ thể, N mẫu, và confidence interval.
2. **Hard targets là pass/fail** — không có "tương đối tốt", không có "gần đạt".
3. **Baselines là bắt buộc.** Kết quả của model chính không có giá trị nếu không có con số
   tương ứng từ 4 baselines.
4. **Nếu thiếu data để evaluate**, yêu cầu thu thập thêm trước khi đưa bất kỳ verdict nào.

---

## Evaluation Protocol (4 bước bắt buộc)

### Bước 1 — Thu thập dữ liệu thô

```python
# Sinh 1000 samples từ checkpoint cuối cùng
python generate.py --ckpt checkpoints/adv_final.pt --n_samples 1000 --output eval_samples.csv

# Thu thập tương tự cho từng baseline
python generate.py --ckpt checkpoints/mle_best.pt --n_samples 1000 --output eval_mle.csv
python baselines/template_based.py --n_samples 1000 --output eval_template.csv
python baselines/seqgan_vanilla.py --ckpt checkpoints/vanilla_final.pt --n_samples 1000 --output eval_vanilla.csv
```

**Tối thiểu**: N=1000 mỗi model. Nếu N < 1000, kết quả không đủ tin cậy — nói rõ.

**Ghi lại**: tên checkpoint, seed, ngày chạy, version ruleset WAF (CRS 4.0.0 hay 3.x).

### Bước 2 — Tính metrics chuẩn

```python
python evaluate.py --input eval_samples.csv --waf_version "CRS-4.0.0"
# Output bắt buộc:
# - asr: float (tỷ lệ bypass, 0-1)
# - syntax_rate: float
# - self_bleu_3: float
# - mean_reward: float (từ training log, nếu có)
# - n_samples: int
```

Lặp lại cho tất cả baselines. Chạy ≥ 3 seeds khác nhau — report `mean ± std`.

### Bước 3 — So sánh baselines với confidence interval

```python
# Bootstrap CI (n=10,000 resamples) cho ASR
from scipy.stats import bootstrap

ci_low, ci_high = bootstrap((asr_array,), np.mean, n_resamples=10000).confidence_interval
# Report: ASR = X.X% [CI: Y.Y% – Z.Z%], N=1000
```

Bảng so sánh bắt buộc:

| Model | ASR | Syntax% | Self-BLEU-3 | N |
|-------|-----|---------|-------------|---|
| SeqGAN + advantage | | | | 1000 |
| SeqGAN vanilla | | | | 1000 |
| MLE only | | | | 1000 |
| Template-based | | | | 1000 |

### Bước 4 — Verdict có dẫn chứng

Với từng hard target, viết 1 dòng pass/fail kèm số:

```
ASR:      SeqGAN=67.3% [CI: 64.4%–70.1%], MLE=41.2% → delta=+26.1pp — ❌ FAIL (target: +30pp)
Syntax:   93.1% — ✅ PASS (target: ≥90%)
Self-BLEU-3: 0.54 — ✅ PASS (target: <0.60)
Hacking:  length_mean=38.2 tok (train_mean=35.7), empty_seq=0/1000 — ✅ CLEAN
```

---

## Hard Targets (pass/fail cứng)

| Target | Điều kiện pass | Điều kiện fail |
|--------|----------------|----------------|
| **ASR** | SeqGAN_ASR > MLE_ASR + 30 percentage points | Bất kỳ delta nào < 30pp |
| **Syntax Validity** | ≥ 90% parse được bởi `sqlparse` | < 90% → ASR vô nghĩa |
| **Self-BLEU-3** | < 0.60 (diversity đủ cao) | ≥ 0.60 → nghi mode collapse |
| **Reward hacking** | length_dist bình thường, 0 empty seq | Xem Red Flags bên dưới |

**Quan trọng**: Nếu Syntax Validity < 90%, **dừng lại ngay** — không cần đọc ASR, model cần fix
trước. Payload invalid không thể attack được WAF.

---

## Evidence Requirements

Mọi claim phải đáp ứng **cả 3 điều kiện**:

1. **Con số cụ thể**: không phải "cao hơn", phải là "67.3% vs 41.2%".
2. **N mẫu**: `N=1000`. Nếu N nhỏ hơn, ghi rõ mức uncertainty tăng lên.
3. **Confidence interval** (khi áp dụng): dùng bootstrap CI (n=10,000) cho ASR và Self-BLEU.

**Ví dụ đúng**:
> "ASR = 67.3% [CI: 64.4%–70.1%, N=1000], MLE baseline = 41.2% [CI: 38.3%–44.1%, N=1000].
> Delta = +26.1pp. Target là +30pp → **FAIL**."

**Ví dụ sai** (không chấp nhận):
> "Model đạt ASR khá tốt, vượt trội hơn baseline."

---

## Red Flags — Tự động Flag

Khi evaluate, kiểm tra **tất cả 6 red flag** dưới đây. Nếu phát hiện bất kỳ cái nào, báo cáo
ngay trước khi đưa verdict cuối.

### RF-1: Reward Hacking

```
Dấu hiệu: reward tăng nhưng syntax_rate giảm (sau step X)
Cách phát hiện:
  - Plot syntax_rate vs training_step trên cùng trục với mean_reward
  - Nếu reward tăng + syntax_rate < 0.5 → reward hacking
Báo cáo: "RF-1 TRIGGERED: step=15k reward=0.82, syntax=44% → reward hacking"
```

### RF-2: Mode Collapse

```
Dấu hiệu: Self-BLEU-3 ≥ 0.80
Cách phát hiện: tính Self-BLEU-3 trên 1000 samples
Severity:
  - 0.60-0.80: cảnh báo (marginal diversity)
  - ≥ 0.80: critical (mode collapse gần như chắc chắn)
Báo cáo: "RF-2 TRIGGERED: Self-BLEU-3=0.87 → mode collapse"
```

### RF-3: Vanishing Discriminator Gradient

```
Dấu hiệu: D_loss ≈ 0 trong nhiều step liên tiếp
Cách phát hiện: xem training log, plot D_loss vs step
Threshold: |D_loss| < 0.001 trong ≥ 500 steps liên tiếp
Báo cáo: "RF-3 TRIGGERED: D_loss=0.0003 từ step 8k đến 12k"
```

### RF-4: Length Distribution Lệch

```
Dấu hiệu: mean/std length của generated samples lệch xa training data
Cách phát hiện:
  train_len_mean, train_len_std = (từ train.csv)
  gen_len_mean, gen_len_std = mean/std của 1000 samples
  Nếu |gen_len_mean - train_len_mean| > 2 × train_len_std → flag
Báo cáo: "RF-4 TRIGGERED: gen_len=8.2 tok (train=35.7±12.3) → abnormal short sequences"
```

### RF-5: Empty / Trivial Sequences

```
Dấu hiệu: >1% sequences là empty, <3 tokens, hoặc chỉ là comment "--"
Cách phát hiện:
  trivial_mask = (len(seq) < 3) | (seq.strip() in ['--', ';', ''])
  trivial_rate = sum(trivial_mask) / N
  Nếu trivial_rate > 0.01 → flag
Báo cáo: "RF-5 TRIGGERED: trivial_rate=4.7% (47/1000) → reward hacking via empty sequences"
```

### RF-6: Training Instability (NaN / Spike)

```
Dấu hiệu: NaN trong loss, hoặc loss spike > 10× median trong 1 step
Cách phát hiện: parse training log, check for NaN và outlier steps
Báo cáo: "RF-6 TRIGGERED: G_loss=NaN tại step 23,450 → gradient explosion"
```

---

## Evaluation Report Template

```markdown
# SeqGAN SQLi — Evaluation Report

**Checkpoint**: checkpoints/adv_final.pt (step=50,000)
**WAF ruleset**: ModSecurity CRS 4.0.0
**Date**: YYYY-MM-DD
**Seeds**: [42, 123, 456] — reported as mean ± std

---

## Primary Metrics

| Metric | SeqGAN+adv | SeqGAN vanilla | MLE only | Template |
|--------|-----------|---------------|----------|----------|
| ASR (%) | | | | |
| Syntax (%) | | | | |
| Self-BLEU-3 | | | | |

*N=1000 per model. CI via bootstrap n=10,000.*

---

## Hard Target Verdict

| Target | Result | Status |
|--------|--------|--------|
| ASR > MLE + 30pp | SeqGAN=X%, MLE=Y% → delta=Zpp | ✅/❌ |
| Syntax ≥ 90% | X% | ✅/❌ |
| Self-BLEU-3 < 0.60 | X.XX | ✅/❌ |
| No reward hacking | [evidence] | ✅/❌ |

---

## Red Flag Scan

- RF-1 (Reward Hacking): [CLEAR / TRIGGERED: ...]
- RF-2 (Mode Collapse): [CLEAR / TRIGGERED: ...]
- RF-3 (Vanishing D): [CLEAR / TRIGGERED: ...]
- RF-4 (Length Dist): [CLEAR / TRIGGERED: ...]
- RF-5 (Trivial Seq): [CLEAR / TRIGGERED: ...]
- RF-6 (Instability): [CLEAR / TRIGGERED: ...]

---

## Final Verdict

**PASS / FAIL / CONDITIONAL**

[Lý do 2-3 câu, dẫn số liệu cụ thể]

Nếu FAIL: liệt kê chính xác target nào fail và delta cần cải thiện bao nhiêu.
Nếu CONDITIONAL: nêu điều kiện cụ thể phải đáp ứng trước khi re-evaluate.
```

---

## Partial Evaluation (khi chưa có đủ data)

Đôi khi evaluate trong quá trình training (checkpoint giữa chừng). Quy tắc:

- **N < 100**: không đưa verdict, chỉ báo "insufficient data (N=X)".
- **N = 100-499**: đưa trend estimate, ghi rõ "preliminary, N=X, margin of error cao".
- **N ≥ 500**: đưa verdict với CI rộng hơn, ghi rõ "N=X (below recommended 1000)".
- **N ≥ 1000**: verdict đầy đủ.

---

## Metrics Definitions (Reference)

### ASR — Attack Success Rate

$$\text{ASR} = \frac{\#\{x \in S_{1000} : \text{ModSecurity CRS default KHÔNG block } x\}}{1000}$$

Ghi rõ version ruleset. Per-type ASR (UNION, Boolean, Time, ...) nếu có label.

### Syntax Validity

$$\text{Syntax} = \frac{\#\{x \in S_{1000} : \text{sqlparse.parse}(x) \neq \text{error}\}}{1000}$$

Dùng `sqlparse` library, không phải database engine thực.

### Self-BLEU-3

Với mỗi sample $x_i$, tính BLEU-3 so với tất cả $x_j, j \neq i$ làm reference.
Self-BLEU = mean của tất cả $i$.

**Thấp hơn = đa dạng hơn** (tốt hơn).
Reference: dataset gốc `combined_labeled_data.csv` → tính Self-BLEU-3 để có baseline số.

### Reward Convergence

Plot `mean_reward` per 1000 steps từ training log. Mô hình tốt: tăng dần và plateau ở mức cao
(không plateau ở mức thấp sau vài nghìn steps đầu).

---

## Statistical Rigor Checklist

Trước khi submit evaluation report:

- [ ] N ≥ 1000 per model
- [ ] ≥ 3 random seeds, report mean ± std
- [ ] Bootstrap CI (n=10,000) cho ASR và Self-BLEU-3
- [ ] Tất cả 4 baselines có số liệu đầy đủ
- [ ] WAF ruleset version được ghi rõ
- [ ] Tất cả 6 red flags đã được scan
- [ ] Không có claim nào thiếu con số cụ thể

---

## Source References

- `SeqGAN_SQLi/Guiding.md` §10 — Metrics & Baselines (định nghĩa gốc)
- `SeqGAN_SQLi/IMPLEMENTATION_PLAN.md` Sprint 5 — code evaluate.py, baselines
- `SeqGAN_SQLi/SKILL_SEQGAN_BUILDER.md` — context về architecture và training loop
