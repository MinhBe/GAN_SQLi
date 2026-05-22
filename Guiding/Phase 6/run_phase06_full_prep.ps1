$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$py = "python"
$phase = Join-Path $root "Guiding\Phase 6"

& $py (Join-Path $phase "phase06_01_tokenize_shards.py") `
  --cache-dir (Join-Path $phase "cache\token_shards") `
  --report-dir (Join-Path $phase "reports") `
  --log-dir (Join-Path $phase "logs") `
  --batch-size 50000 `
  --shard-rows 50000 `
  --max-len 128 `
  --min-freq 3 `
  --max-vocab 64000 `
  --overwrite
