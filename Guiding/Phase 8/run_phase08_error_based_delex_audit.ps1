$ErrorActionPreference = "Stop"
$Py = "C:\Users\Admin\AppData\Local\Programs\Python\Python311\python.exe"
if (-not (Test-Path -LiteralPath $Py)) {
  $Py = "python"
}
& $Py -u -B (Join-Path $PSScriptRoot "phase08_02_error_based_delex_audit.py")

