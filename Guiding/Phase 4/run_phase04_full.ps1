$ErrorActionPreference = "Stop"

$root = "C:\Users\Admin\Documents\GAN_SQLi"
$script = Join-Path $root "Guiding\Phase 4\phase04_full_data_foundation.py"
$log = Join-Path $root "Guiding\Phase 4\phase04_full_run.log"
$err = Join-Path $root "Guiding\Phase 4\phase04_full_run.err.log"
$progress = Join-Path $root "Guiding\Phase 4\phase04_full_progress.json"
$out = Join-Path $root "data\phase04"
$reports = Join-Path $root "reports"

Set-Location $root

python -u -B $script `
  --batch-size 100000 `
  --pool-limit 20000 `
  --out-dir $out `
  --report-dir $reports `
  --progress-file $progress `
  1> $log `
  2> $err
