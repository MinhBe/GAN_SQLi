$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$py = "python"
$phase = Join-Path $root "Guiding\Phase 6"

& $py (Join-Path $phase "phase06_04_condition_audit.py") `
  --sample-dir (Join-Path $phase "outputs\gumbel_seqgan_smoke_balanced") `
  --report-dir (Join-Path $phase "reports") `
  --title "06 - Gumbel Condition Audit"
