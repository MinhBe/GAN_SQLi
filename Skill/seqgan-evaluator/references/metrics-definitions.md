# Metrics Definitions — SeqGAN SQLi Evaluator

## ASR — Attack Success Rate

$$\text{ASR} = \frac{\#\{x \in S_{1000} : \text{ModSecurity CRS default KHÔNG block } x\}}{1000}$$

- Ghi rõ version ruleset (CRS 4.0.0 vs 3.x — threshold khác nhau).
- Per-type ASR (UNION, Boolean, Time, ...) nếu samples có label.
- Dev mode (không có Docker): dùng proxy `bypass_proxy(sqli_type)` — ghi rõ là "estimated ASR".

## Syntax Validity

$$\text{Syntax} = \frac{\#\{x \in S_{1000} : \text{sqlparse.parse}(x) \neq \text{error}\}}{1000}$$

- Dùng `sqlparse` library (không phải database engine thực).
- Nếu < 90%: dừng evaluate ASR, fix Generator trước.

## Self-BLEU-3

Với mỗi sample $x_i$, tính BLEU-3 so với tất cả $x_j,\ j \neq i$ làm reference corpus.
Self-BLEU-3 = mean của tất cả $x_i$.

**Thấp hơn = đa dạng hơn** (tốt hơn).

Reference baseline: tính Self-BLEU-3 trên `combined_labeled_data.csv` để có con số so sánh.

```python
from nltk.translate.bleu_score import sentence_bleu, SmoothingFunction
import numpy as np

def self_bleu_3(samples: list[list[str]]) -> float:
    scores = []
    smoother = SmoothingFunction().method1
    for i, hyp in enumerate(samples):
        refs = [s for j, s in enumerate(samples) if j != i]
        score = sentence_bleu(refs, hyp, weights=(1/3, 1/3, 1/3), smoothing_function=smoother)
        scores.append(score)
    return float(np.mean(scores))
```

## Reward Convergence

- Source: training log, field `mean_reward` per 1000 steps.
- Plot `mean_reward` vs `training_step`.
- Mô hình tốt: tăng dần và plateau ở mức cao.
- Cờ đỏ: plateau sớm (< 5k steps) ở mức thấp (< 0.2), hoặc oscillate mạnh.

---

## Statistical Rigor Checklist

Trước khi submit evaluation report, verify đủ tất cả:

- [ ] N ≥ 1000 per model
- [ ] ≥ 3 random seeds, report mean ± std
- [ ] Bootstrap CI (n=10,000) cho ASR và Self-BLEU-3
- [ ] Tất cả 4 baselines có số liệu đầy đủ
- [ ] WAF ruleset version được ghi rõ
- [ ] Tất cả 6 red flags đã được scan
- [ ] Không có claim nào thiếu con số cụ thể

---

## Bootstrap CI — Code mẫu

```python
import numpy as np
from scipy.stats import bootstrap

def compute_asr_ci(bypass_results: list[int], n_resamples=10000, confidence=0.95):
    """bypass_results: list of 0/1, 1=bypass."""
    arr = np.array(bypass_results, dtype=float)
    result = bootstrap(
        (arr,), np.mean,
        n_resamples=n_resamples,
        confidence_level=confidence,
        method='percentile'
    )
    return {
        'mean': arr.mean(),
        'ci_low': result.confidence_interval.low,
        'ci_high': result.confidence_interval.high,
        'n': len(arr)
    }

# Output: ASR = 67.3% [CI: 64.4%–70.1%, N=1000]
```
