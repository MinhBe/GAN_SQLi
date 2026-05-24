$ErrorActionPreference = "Stop"

$phaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent (Split-Path -Parent $phaseDir)
$python = "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
$script = Join-Path $phaseDir "phase08_05_surgery_baselines.py"

& $python -u -B $script `
  --split-dir (Join-Path $phaseDir "outputs\delex_cluster_split") `
  --output-dir (Join-Path $phaseDir "outputs\surgery_baselines_full_lite") `
  --checkpoint-dir (Join-Path $phaseDir "checkpoints\surgery_baselines_full_lite") `
  --report-dir (Join-Path $phaseDir "reports") `
  --log-dir (Join-Path $phaseDir "logs") `
  --train-limit 300000 `
  --dev-limit 25000 `
  --sample-count 400 `
  --batch-size 64 `
  --max-steps 1000 `
  --eval-every 100 `
  --log-every 50 `
  --max-len 96 `
  --embed-dim 64 `
  --hidden-dim 128 `
  --report-name "08_surgery_baselines_full_lite_report.md" `
  --json-name "08_surgery_baselines_full_lite_report.json"
