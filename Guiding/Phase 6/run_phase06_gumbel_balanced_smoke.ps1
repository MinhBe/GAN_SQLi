$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$py = "python"
$phase = Join-Path $root "Guiding\Phase 6"

& $py (Join-Path $phase "phase06_03_gumbel_seqgan_smoke.py") `
  --config (Join-Path $phase "configs\gumbel_seqgan_smoke_balanced.json") `
  --cache-dir (Join-Path $phase "cache\token_shards") `
  --checkpoint-dir (Join-Path $phase "checkpoints\gumbel_seqgan_smoke_balanced") `
  --output-dir (Join-Path $phase "outputs\gumbel_seqgan_smoke_balanced") `
  --report-dir (Join-Path $phase "reports") `
  --log-dir (Join-Path $phase "logs")
