# 02 — De-risk Vertical Slice: Evaluation Report

**Decision: FAIL — do not scale GAN**

---

## MLE Baseline Results

| Seed | Best Config | unique_ratio | self_bleu3 | syntax_rate |
|---|---|---:|---:|---:|
| 42 | t1.2_k50_p0.95 | 0.793 | 0.015 | 0.698 |
| 123 | t1.2_k50_p0.95 | 0.803 | 0.014 | 0.710 |
| 456 | t1.2_k50_p0.95 | 0.801 | 0.013 | 0.712 |

**MLE Best Overall:** unique_ratio=0.803  self_bleu3=0.014  syntax=0.710

---

## Gumbel-SeqGAN Results

| Metric | Mean | Std | Best | Worst |
|---|---:|---:|---:|---:|
| unique_ratio | 0.291 | 0.252 | 0.497 | 0.010 |
| self_bleu3 | 0.436 | 0.457 | 0.934 | 0.037 |
| token_entropy | 2.069 | 1.778 | 4.107 | 0.833 |
| syntax_validity_rate | 0.615 | 0.296 | 0.832 | 0.278 |

### D Shortcut Diagnostic

- Seed 42: D_real=0.9999964833259583  D_softened=0.9999964237213135  delta=5.960464477539063e-08  shortcut=False
- Seed 123: D_real=0.9999991059303284  D_softened=0.9999991059303284  delta=0.0  shortcut=False
- Seed 456: D_real=0.9895492196083069  D_softened=0.9875990152359009  delta=0.0019502043724060059  shortcut=False

---

## Decision Gate

- [FAIL] FAIL: GAN unique_ratio (0.497) <= MLE (0.803)
- [FAIL] FAIL: GAN self_bleu3 (0.934) >= MLE (0.014)
- [FAIL] FAIL: GAN syntax_rate (0.615) < MLE*0.9 (0.639)
- [OK] PASS: No D shortcut (avg delta=0.001 < 0.3)

**Overall: FAIL**

---

## Collapse Check per Seed

| Seed | unique_ratio | collapse_detected |
|---|---:|---|
| 42 | 0.010 | True |
| 123 | 0.367 | True |
| 456 | 0.497 | True |

---

## Recommendation

GAN does not demonstrate sufficient advantage over MLE baseline.
Options:
1. Fix architecture issues (D shortcut, collapse) and re-run this slice
2. Proceed with MLE-only approach for Phase 03