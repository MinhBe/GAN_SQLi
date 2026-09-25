#!/usr/bin/env bash
set -euo pipefail
DATA_PATH="${1:-/content/GAN_SQLi/SQLGAN_PostgreSQL_Boolean_CSeqGAN_V5_1_CoverageFixed.zip}"
OUT_DIR="${2:-/content/runs_sqlgan/branch_c_cseqgan_minimal_smoke}"
python -m sqlgan_dual.experiment_c_conditioned_seqgan \
  --data "$DATA_PATH" \
  --out "$OUT_DIR" \
  --modules Y1_basic_boolean Y2_boolean_variation \
  --limit 2048 \
  --max-len 256 \
  --batch-size 160 \
  --mle-epochs 6 \
  --d-epochs 1 \
  --adv-epochs 1 \
  --adv-steps 25 \
  --emb-dim 128 \
  --hidden-dim 256 \
  --temperature 0.85 \
  --static-weight 0.45 \
  --generate-per-ruleset 2 \
  --generate-ruleset-limit 100 \
  --parallel-modules auto \
  --cpu-threads 2 \
  --num-workers 0
