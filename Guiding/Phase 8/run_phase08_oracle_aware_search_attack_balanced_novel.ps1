$ErrorActionPreference = "Stop"

$phaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
$script = Join-Path $phaseDir "phase08_11_oracle_aware_search.py"

& $python -u -B $script `
  --samples (Join-Path $phaseDir "outputs\classifier_oracle_rerank\max_aggressive_candidates_top400_attack_balanced_novel.jsonl") `
  --out-dir (Join-Path $phaseDir "outputs\oracle_aware_search") `
  --report-dir (Join-Path $phaseDir "reports") `
  --name "attack_balanced_novel_oracle_search" `
  --variants-per-sample 16 `
  --top-n 400 `
  --require-novel `
  --require-balanced `
  --exclude-technique benign
