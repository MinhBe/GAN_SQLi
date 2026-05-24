# 06 - Gumbel-SeqGAN Smoke Report

**Scope:** small adversarial smoke run, not full GAN training.
**Train source:** `gold.parquet` token shards
**Train rows available:** `1,652,331`
**MLE init checkpoint:** `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 6\checkpoints\mle_baseline\best.pt`
**MLE init source step:** `1250`
**Loaded MLE keys:** `8` / `8`
**Batch size:** `16`
**Max len:** `96`
**Max steps:** `1500`
**Mixed precision:** `True`

## Latest Metrics

- Step: `1500`
- Loss D: `1.005861759185791`
- Loss G: `0.49244409799575806`
- Loss adversarial: `1.5720266103744507`
- Loss MLE anchor: `0.3666819930076599`
- Tau: `0.7501`
- Unique ratio: `0.9833333333333333`
- Syntax validity rate: `1.0`
- Empty sample count: `0`
- D real/fake: `0.7913174629211426` / `0.21075209975242615`
- D shortcut suspected: `False`

## Gate

- Latest checkpoint: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 6\checkpoints\gumbel_seqgan_smoke_balanced\latest.pt`
- Best checkpoint: `C:\Users\Admin\Documents\GAN_SQLi\Guiding\Phase 6\checkpoints\gumbel_seqgan_smoke_balanced\best.pt`
- Continue only if there is no OOM, no non-finite loss, no severe unique-ratio collapse, and D shortcut is not suspected.
