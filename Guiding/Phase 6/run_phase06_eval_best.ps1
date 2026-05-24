$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$py = "python"
$phase = Join-Path $root "Guiding\Phase 6"

& $py (Join-Path $phase "phase06_02_mle_train.py") `
  --config (Join-Path $phase "configs\mle_baseline.json") `
  --cache-dir (Join-Path $phase "cache\token_shards") `
  --checkpoint-dir (Join-Path $phase "checkpoints\mle_baseline") `
  --output-dir (Join-Path $phase "outputs\mle_eval") `
  --report-dir (Join-Path $phase "reports") `
  --log-dir (Join-Path $phase "logs") `
  --resume (Join-Path $phase "checkpoints\mle_baseline\best.pt") `
  --eval-only `
  --eval-tag best_checkpoint `
  --eval-max-batches 500 `
  --sample-count 240
