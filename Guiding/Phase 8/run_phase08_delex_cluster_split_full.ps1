$ErrorActionPreference = "Stop"
$Py = "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
if (-not (Test-Path -LiteralPath $Py)) {
  $Py = "python"
}
& $Py -u -B (Join-Path $PSScriptRoot "phase08_04_build_delex_cluster_split.py") `
  --out-dir (Join-Path $PSScriptRoot "outputs\delex_cluster_split") `
  --overwrite

