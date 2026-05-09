# Evaluation Report Template

Copy template này và điền số liệu sau khi chạy đủ 4 bước trong SKILL.md.

---

```markdown
# SeqGAN SQLi — Evaluation Report

**Checkpoint**: checkpoints/adv_final.pt (step=50,000)
**WAF ruleset**: ModSecurity CRS 4.0.0
**Date**: YYYY-MM-DD
**Seeds**: [42, 123, 456] — reported as mean ± std

---

## Primary Metrics

| Metric | SeqGAN+adv | SeqGAN vanilla | MLE only | Template |
|--------|-----------|----------------|----------|----------|
| ASR (%) | X.X ± X.X | | | |
| Syntax (%) | X.X ± X.X | | | |
| Self-BLEU-3 | X.XX ± X.XX | | | |

*N=1000 per model. CI via bootstrap n=10,000.*

---

## Hard Target Verdict

| Target | Result | Status |
|--------|--------|--------|
| ASR > MLE + 30pp | SeqGAN=X%, MLE=Y% → delta=Zpp | ✅/❌ |
| Syntax ≥ 90% | X% | ✅/❌ |
| Self-BLEU-3 < 0.60 | X.XX | ✅/❌ |
| No reward hacking | [evidence from RF scan] | ✅/❌ |

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

## Hướng dẫn điền

- **ASR CI**: `bootstrap((asr_binary_array,), np.mean, n_resamples=10000).confidence_interval`
- **delta**: tính trên mean ASR, không tính trên CI bound
- **Red flag CLEAR**: viết evidence ngắn (e.g., "Self-BLEU-3=0.54, length_mean=37.1±11.2")
- **Verdict CONDITIONAL**: dùng khi 1 target fail nhưng có path rõ ràng để fix trong 1 sprint
