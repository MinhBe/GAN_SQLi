# 06 - MLE Baseline Report

**Device:** `cuda`
**Train rows:** `1,652,331`
**Dev rows:** `165,836`
**Test rows:** `166,206`
**Vocab size:** `1,601`
**Batch/grad accum:** `32` / `4`
**Max len:** `128`
**Embed/hidden:** `128` / `256`
**Mixed precision:** `True`

## Latest Progress

- Global step: `21`
- Epoch: `0`
- Train loss: `None`
- Val loss: `3.3279668185121114`

## Gate Snapshot

- Loss finite: `yes`
- Unique ratio: `0.9667`
- Syntax validity rate: `0.7208`
- Empty sample count: `7`
- Latest checkpoint: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 6\checkpoints\mle_baseline\latest.pt`
- Best checkpoint: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 6\checkpoints\mle_baseline\best.pt`

## Scope Note

This is still the MLE/Warmup baseline stage. Do not start Gumbel-SeqGAN until OOM, loss, checkpoint/resume, and diversity gates pass on a representative run.
