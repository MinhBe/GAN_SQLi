$ErrorActionPreference = "Stop"

$phaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
$script = Join-Path $phaseDir "phase08_10_classifier_oracle_rerank.py"

& $python -u -B $script `
  --samples "max_aggressive_candidates=$(Join-Path $phaseDir "outputs\gan_candidate_pools\paired_surgery_gan_max_aggressive_candidates.jsonl")" `
  --detector-results "max_aggressive_candidates=$(Join-Path $phaseDir "outputs\classifier_oracle_results\paired_surgery_gan_max_aggressive_candidates_classifier_oracle_results.csv")" `
  --out-dir (Join-Path $phaseDir "outputs\classifier_oracle_rerank") `
  --report-dir (Join-Path $phaseDir "reports") `
  --name "max_aggressive_candidates_top400_attack_balanced_novel" `
  --top-n 400 `
  --require-novel `
  --require-balanced `
  --exclude-technique benign
