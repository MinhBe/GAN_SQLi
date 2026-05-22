@echo off
setlocal
set "PHASE_DIR=%~dp0"
powershell.exe -NoProfile -ExecutionPolicy Bypass -File "%PHASE_DIR%run_phase05_full.ps1" %*
exit /b %ERRORLEVEL%
