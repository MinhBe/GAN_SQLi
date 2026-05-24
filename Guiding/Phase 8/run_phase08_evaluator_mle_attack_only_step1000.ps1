$ErrorActionPreference = "Stop"
$Py = "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
if (-not (Test-Path -LiteralPath $Py)) {
  $Py = "python"
}
$Samples = Join-Path (Split-Path -Parent $PSScriptRoot) "Phase 6\outputs\mle_attack_only_smoke\samples_step_00001000.jsonl"
& $Py -u -B (Join-Path $PSScriptRoot "phase08_03_evaluator_contract.py") `
  --samples $Samples `
  --report-name "08_evaluator_mle_attack_only_step1000.md" `
  --json-name "08_evaluator_mle_attack_only_step1000.json"
