$ErrorActionPreference = "Stop"

$phaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$python = "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
$script = Join-Path $phaseDir "phase08_09_gan_candidate_sampler.py"

& $python -u -B $script `
  --checkpoint (Join-Path $phaseDir "checkpoints\paired_surgery_gan_max_aggressive\paired_surgery_gan_latest.pt") `
  --split-dir (Join-Path $phaseDir "outputs\delex_cluster_split") `
  --output-dir (Join-Path $phaseDir "outputs\gan_candidate_pools") `
  --report-dir (Join-Path $phaseDir "reports") `
  --name "paired_surgery_gan_max_aggressive_candidates" `
  --row-count 1000 `
  --rounds 8 `
  --temperature 1.7 `
  --top-k 24
