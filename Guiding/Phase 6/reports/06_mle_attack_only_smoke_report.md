# 06 - MLE Attack-Only Smoke Report

**Device:** `cuda`
**Train rows:** `1,630,022`
**Dev rows:** `163,586`
**Test rows:** `163,976`
**Vocab size:** `1,584`
**Batch/grad accum:** `32` / `4`
**Max len:** `128`
**Embed/hidden:** `128` / `256`
**Mixed precision:** `True`

## Latest Progress

- Global step: `1000`
- Epoch: `0`
- Train loss: `0.17381030287221075`
- Val loss: `1.447074107961796`

## Gate Snapshot

- Loss finite: `yes`
- Unique ratio: `0.9833`
- Syntax validity rate: `1.0000`
- Empty sample count: `0`
- Latest checkpoint: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 6\checkpoints\mle_attack_only_smoke\latest.pt`
- Best checkpoint: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 6\checkpoints\mle_attack_only_smoke\best.pt`

## Scope Note

This is still the MLE/Warmup baseline stage. Do not start Gumbel-SeqGAN until OOM, loss, checkpoint/resume, and diversity gates pass on a representative run.
