# Kaggle 2 × T4 — performance profile

This is an **experimental throughput profile**, not a measured optimum. Use `nvidia-smi` and
the per-epoch `training_sequences_per_second` / `gpu_peak_allocated_gib` log to tune.

## What changed from the previous MVP

- Rollouts are evaluated **as one batch of K completions**, not K serial GPU calls.
- Rollout work stops at the longest active EOS position in the batch (no reward
  sampling at every padding position).
- Generator reuses its recurrent state while sampling (the prefix is consumed
  once per continuation).
- Training logs sequences/sec and peak allocated VRAM per GPU (rank 0).

## Start with a benchmark, not a 12-hour blind run

Upload the ABCD zip to Kaggle, clone this repository and run from the
`abcd_conditional_seqgan` directory:

```bash
nvidia-smi
python -m pytest -q tests/test_smoke.py
torchrun --standalone --nproc_per_node=2 -m abcd_seqgan.train \\
  --data /kaggle/input/YOUR_DATASET/Boolean_ABCD.zip \\
  --out /kaggle/working/abcd_benchmark --amp --batch 32 --workers 0 \\
  --embedding 128 --hidden 256 --layers 2 --filters 128 \\
  --mle-epochs 1 --d-epochs 1 --adv-epochs 1 \\
  --rollouts 2 --rollout-stride 32 --max-steps 20
```

Compare `--batch 32`, `--batch 64` and `--batch 96` **per GPU**. For
fair comparisons, hold all other arguments fixed, record epoch times,
peak VRAM, and generation acceptance rate. `--batch 96` is not guaranteed
to fit on every run; reduce batch on OOM. Do not infer speed from GPU
utilization alone.

For a longer run, after selecting a batch size that fits:

```bash
torchrun --standalone --nproc_per_node=2 -m abcd_seqgan.train \\
  --data /kaggle/input/YOUR_DATASET/Boolean_ABCD.zip \\
  --out /kaggle/working/abcd_run --amp --batch 64 --workers 0 \\
  --embedding 128 --hidden 256 --layers 2 --filters 128 \\
  --mle-epochs 12 --d-epochs 3 --adv-epochs 5 \\
  --rollouts 2 --rollout-stride 32
```

**Research tradeoff:** `--rollout-stride 32` is an approximation, not
per-token MC estimation from the original SeqGAN paper. Compare against
`--rollout-stride 8` / `--rollouts 4` and, if feasible, stride 1 on
a short controlled benchmark. Faster sampling is not evidence of better
learned grammar.

## Important limits

- 2 × 15 GiB VRAM is **not** one 30 GiB memory pool.
- DDP trains on both T4s; generation splits structure cells by rank.
- No CUDA benchmark was run in the file-creation environment.
- The generator remains autoregressive; character-level strings up to
  464 tokens make Monte Carlo rollout expensive.
- Checkpoint resume in the original MVP does not preserve RNG states,
  GradScaler states or exact mid-epoch position; do not claim bitwise
  reproducibility after resuming.
- This patch does not add dialect-aware validation. The generated
  strings remain synthetic/unvalidated until independently checked.
