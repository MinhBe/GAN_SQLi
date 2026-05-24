$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$Py = "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
if (-not (Test-Path -LiteralPath $Py)) {
  $Py = "python"
}
& $Py -u -B (Join-Path $PSScriptRoot "phase08_01_delex_template_leakage_audit.py") `
  --limit 50000 `
  --report-name "08_delex_template_leakage_audit_smoke.md" `
  --json-name "08_delex_template_leakage_audit_smoke.json"

