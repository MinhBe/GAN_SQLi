$ErrorActionPreference = "Stop"
$Py = "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
if (-not (Test-Path -LiteralPath $Py)) {
  $Py = "python"
}
& $Py -u -B (Join-Path $PSScriptRoot "phase08_01_delex_template_leakage_audit.py")

