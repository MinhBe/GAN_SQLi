#!/usr/bin/env bash
set -euo pipefail
DATA=${1:-/mnt/data/SQLGAN_PostgreSQL_Boolean_Attack_Corpus_V4_1_StaticTrainingCorpus.zip}
OUT=${2:-/mnt/data/sqlgan_branch_b_smoke}
python -m sqlgan_dual.experiment_b_core_renderers --data "$DATA" --out "$OUT" --smoke
