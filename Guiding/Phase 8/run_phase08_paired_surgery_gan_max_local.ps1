$ErrorActionPreference = "Stop"

$phaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
$script = Join-Path $phaseDir "phase08_06_paired_surgery_gan.py"

& $python -u -B $script `
  --split-dir (Join-Path $phaseDir "outputs\delex_cluster_split") `
  --anchor-checkpoint (Join-Path $phaseDir "checkpoints\surgery_baselines_full_lite\anchor_only_latest.pt") `
  --output-dir (Join-Path $phaseDir "outputs\paired_surgery_gan_max_local") `
  --checkpoint-dir (Join-Path $phaseDir "checkpoints\paired_surgery_gan_max_local") `
  --report-dir (Join-Path $phaseDir "reports") `
  --log-dir (Join-Path $phaseDir "logs") `
  --train-limit 300000 `
  --dev-limit 25000 `
  --sample-count 400 `
  --batch-size 64 `
  --max-steps 2000 `
  --d-steps 2 `
  --eval-every 100 `
  --log-every 50 `
  --max-len 96 `
  --embed-dim 64 `
  --hidden-dim 128 `
  --d-hidden-dim 192 `
  --slot-mode local `
  --adv-weight 0.30 `
  --anchor-weight 0.70 `
  --entropy-weight 0.03 `
  --sample-temperature 1.4 `
  --sample-top-k 12 `
  --d-freeze-acc 0.90 `
  --report-name "08_paired_surgery_gan_max_local_report.md" `
  --json-name "08_paired_surgery_gan_max_local_report.json"
