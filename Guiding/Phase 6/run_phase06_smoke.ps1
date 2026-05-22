$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$py = "python"
$phase = Join-Path $root "Guiding\Phase 6"

& $py (Join-Path $phase "phase06_01_tokenize_shards.py") `
  --cache-dir (Join-Path $phase "cache\smoke_token_shards") `
  --report-dir (Join-Path $phase "reports") `
  --log-dir (Join-Path $phase "logs") `
  --limit-train 2048 `
  --limit-dev 512 `
  --limit-test 512 `
  --shard-rows 512 `
  --overwrite

& $py (Join-Path $phase "phase06_02_mle_train.py") `
  --cache-dir (Join-Path $phase "cache\smoke_token_shards") `
  --checkpoint-dir (Join-Path $phase "checkpoints\smoke_mle") `
  --output-dir (Join-Path $phase "outputs\smoke_mle") `
  --report-dir (Join-Path $phase "reports") `
  --log-dir (Join-Path $phase "logs") `
  --max-steps 4 `
  --eval-every 2 `
  --save-every 2 `
  --log-every 1 `
  --eval-max-batches 4 `
  --sample-count 24

& $py (Join-Path $phase "phase06_02_mle_train.py") `
  --cache-dir (Join-Path $phase "cache\smoke_token_shards") `
  --checkpoint-dir (Join-Path $phase "checkpoints\smoke_mle") `
  --output-dir (Join-Path $phase "outputs\smoke_mle_resume") `
  --report-dir (Join-Path $phase "reports") `
  --log-dir (Join-Path $phase "logs") `
  --resume-latest `
  --max-steps 5 `
  --eval-every 1 `
  --save-every 1 `
  --log-every 1 `
  --eval-max-batches 2 `
  --sample-count 12
