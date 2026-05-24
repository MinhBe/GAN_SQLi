$ErrorActionPreference = "Stop"
$Py = "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
if (-not (Test-Path -LiteralPath $Py)) {
  $Py = "python"
}
& $Py -u -B (Join-Path $PSScriptRoot "phase08_04_build_delex_cluster_split.py") `
  --limit-per-source 50000 `
  --out-dir (Join-Path $PSScriptRoot "outputs\delex_cluster_split_smoke") `
  --report-name "08_delex_cluster_split_smoke_report.md" `
  --json-name "08_delex_cluster_split_smoke_report.json" `
  --overwrite

