$ErrorActionPreference = "Stop"

$phaseDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$root = Split-Path -Parent (Split-Path -Parent $phaseDir)
$script = Join-Path $phaseDir "phase05_full_label_system.py"
$logDir = Join-Path $phaseDir "logs"
$out = Join-Path $phaseDir "outputs\full"
$reports = Join-Path $phaseDir "reports"
$log = Join-Path $logDir "phase05_full_run.log"
$err = Join-Path $logDir "phase05_full_run.err.log"
$progress = Join-Path $logDir "phase05_full_progress.json"

New-Item -ItemType Directory -Force -Path $logDir, $out, $reports | Out-Null
Set-Location $root

python -u -B $script `
  --out-dir $out `
  --report-dir $reports `
  --log-dir $logDir `
  --progress-file $progress `
  @args `
  1> $log `
  2> $err
