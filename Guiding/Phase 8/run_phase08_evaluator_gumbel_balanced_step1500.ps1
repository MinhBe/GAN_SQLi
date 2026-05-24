$ErrorActionPreference = "Stop"
$Py = "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
if (-not (Test-Path -LiteralPath $Py)) {
  $Py = "python"
}
$Samples = Join-Path (Split-Path -Parent $PSScriptRoot) "Phase 6\outputs\gumbel_seqgan_smoke_balanced\samples_step_00001500.jsonl"
& $Py -u -B (Join-Path $PSScriptRoot "phase08_03_evaluator_contract.py") `
  --samples $Samples `
  --report-name "08_evaluator_gumbel_balanced_step1500.md" `
  --json-name "08_evaluator_gumbel_balanced_step1500.json"
