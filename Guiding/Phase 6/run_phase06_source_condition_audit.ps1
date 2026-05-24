$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$py = "python"
$phase = Join-Path $root "Guiding\Phase 6"

& $py (Join-Path $phase "phase06_05_source_condition_audit.py") `
  --report-dir (Join-Path $phase "reports")
