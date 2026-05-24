$ErrorActionPreference = "Stop"

$phaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent (Split-Path -Parent $phaseDir)
$python = "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
$script = Join-Path $phaseDir "phase08_05_surgery_baselines.py"

& $python -u -B $script `
  --split-dir (Join-Path $phaseDir "outputs\delex_cluster_split_smoke") `
  --output-dir (Join-Path $phaseDir "outputs\surgery_baselines_smoke") `
  --checkpoint-dir (Join-Path $phaseDir "checkpoints\surgery_baselines_smoke") `
  --report-dir (Join-Path $phaseDir "reports") `
  --log-dir (Join-Path $phaseDir "logs") `
  --train-limit 50000 `
  --dev-limit 5000 `
  --sample-count 120 `
  --batch-size 64 `
  --max-steps 200 `
  --eval-every 50 `
  --log-every 25 `
  --max-len 96 `
  --embed-dim 64 `
  --hidden-dim 128 `
  --report-name "08_surgery_baselines_smoke_report.md" `
  --json-name "08_surgery_baselines_smoke_report.json"
