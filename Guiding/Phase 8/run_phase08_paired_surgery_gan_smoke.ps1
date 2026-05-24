$ErrorActionPreference = "Stop"

$phaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
$script = Join-Path $phaseDir "phase08_06_paired_surgery_gan.py"

& $python -u -B $script `
  --split-dir (Join-Path $phaseDir "outputs\delex_cluster_split_smoke") `
  --anchor-checkpoint (Join-Path $phaseDir "checkpoints\surgery_baselines_smoke\anchor_only_latest.pt") `
  --output-dir (Join-Path $phaseDir "outputs\paired_surgery_gan_smoke") `
  --checkpoint-dir (Join-Path $phaseDir "checkpoints\paired_surgery_gan_smoke") `
  --report-dir (Join-Path $phaseDir "reports") `
  --log-dir (Join-Path $phaseDir "logs") `
  --train-limit 50000 `
  --dev-limit 5000 `
  --sample-count 120 `
  --batch-size 64 `
  --max-steps 300 `
  --eval-every 50 `
  --log-every 25 `
  --max-len 96 `
  --embed-dim 64 `
  --hidden-dim 128 `
  --d-hidden-dim 128 `
  --adv-weight 0.05 `
  --entropy-weight 0.002 `
  --report-name "08_paired_surgery_gan_smoke_report.md" `
  --json-name "08_paired_surgery_gan_smoke_report.json"
