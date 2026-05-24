$ErrorActionPreference = "Stop"

$root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$py = "python"
$phase = Join-Path $root "Guiding\Phase 6"

& $py (Join-Path $phase "phase06_04_condition_audit.py") `
  --sample-dir (Join-Path $phase "outputs\mle_baseline") `
  --report-dir (Join-Path $phase "reports") `
  --report-name "06_mle_condition_audit_report.md" `
  --title "06 - MLE Condition Audit"
