# V2 Training Results & Analysis

> Date: 2026-05-12  
> Total training time: ~47 min (MLE: ~15 min, Adversarial: ~46 min)

---

## Training Summary

| Phase | Steps | Duration | Key Metric |
|---|---|---|---|
| MLE pretrain | ~9 epochs (early stop) | ~15 min | val_ppl = 1.27 |
| Warmup (custom rules) | 0–2000 | ~6 min | avg_reward 0.42 → 0.70 |
| Adversarial (WAF + full composite) | 2000–15000 | ~31 min | avg_reward stable ~0.70 |
| Refinement (diversity-weighted) | 15000–20000 | ~9 min | avg_reward stable ~0.70 |

---

## Evaluation Results (500 samples, no WAF)

| Model | DB exec | AST entropy | ML-IDS evasion | Re-lex unique | Composite |
|---|---|---|---|---|---|
| v2_mle | 3.2% | 3.083 | 3.4% | 0.658 | **0.202** |
| v2_step1000 | 99.8% | 2.417 | **38.6%** | 0.008 | **0.405** |
| v2_step2000 | 100% | 2.565 | 0% | 0.012 | 0.354 |
| v2_step6000 | 100% | 2.565 | 0% | 0.002 | 0.353 |
| v2_refined (final) | 100% | 2.565 | 0% | **0.002** | 0.353 |

> Note: OWASP bypass = 0.0 for all (WAF disabled during eval). With WAF enabled, results may differ.

---

## Key Findings

### 1. Best checkpoint: v2_step1000 (end of warmup phase)
- Composite score 0.405 beats MLE baseline (0.202) by **+0.203**
- 99.8% DB execution rate vs MLE's 3.2%
- 38.6% ML-IDS evasion (surprising — warmup payloads evade the IDS)

### 2. Mode collapse at adversarial phase onset (step 2000)
**Symptom:** `relex_uniqueness` drops from 0.658 (MLE) to 0.012 (step 2000) to 0.002 (step 3000+).  
The AST entropy value is **frozen at exactly 2.5649** from step 2000 through step 20000 — the generator outputs one or a handful of unique payloads 500 times.

**Root cause:** REINFORCE with batch-mean baseline collapses when all generated payloads achieve similar reward:
- Generator finds payloads that pass DB gate (score ≥ 0.7)
- All batch members get similar reward → advantages ≈ 0 → gradient ≈ 0
- No exploration pressure → generator locks into a few high-reward payloads
- Cache hit rate: 96.9% by step 9000 confirms only ~17,600 unique payloads in 576,000 calls

**Refinement phase had zero effect** — even with `diversity` weight = 0.5, the zero-gradient problem prevented any exploration.

### 3. MLE baseline has better diversity but worse execution
- MLE generates syntactically correct (99.8%) but rarely executable (3.2%) payloads
- Natural diversity preserved from training data (relex_uniqueness = 0.658)

---

## Verdict: V2 vs V1

**V2 improvement**: composite 0.405 (v2_step1000) vs V1 MLE-only baseline ~0.202

**However**, the adversarial objective failed to produce a diverse, high-quality final model. The best output is the warmup-phase checkpoint, not the refinement final.

---

## Recommendations for V3 / Next Iteration

### Priority fixes (training stability):

1. **Entropy regularization in REINFORCE loss**:
   ```python
   g_loss = reinforce_loss(log_probs, advantages) - entropy_coeff * entropy(log_probs)
   ```
   Forces generator to maintain output distribution diversity.

2. **Per-batch exploration noise** — temperature > 1.0 during training:
   ```python
   token_ids, log_probs = gen.sample(..., temperature=1.2)
   ```

3. **Moving average baseline** instead of batch mean:
   ```python
   ema_baseline = 0.9 * ema_baseline + 0.1 * rewards.mean()
   advantages = rewards - ema_baseline
   ```
   Provides signal even when all batch rewards are equal.

4. **Diversity-aware reward shaping from warmup** (not just refinement):
   Add novelty bonus based on AST fingerprint distance from seen payloads.

5. **Periodic generator reset** — at adversarial phase start, reset generator to MLE checkpoint and use smaller lr_g.

### Alternative training objective:
Consider **PPO with KL divergence constraint** against MLE policy — prevents the generator from collapsing too far from the trained language model.
