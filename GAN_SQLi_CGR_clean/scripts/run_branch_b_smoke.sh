#!/usr/bin/env bash
set -euo pipefail
DATA=${1:-.}
OUT=${2:-./runs/cgr_branch_b_smoke}
python -m sqlgan_dual.experiment_b_core_renderers --data "$DATA" --out "$OUT" --smoke --adv-epochs 1
