@echo off
setlocal
set "ROOT=C:\Users\Admin\Documents\GAN_SQLi"
set "SCRIPT=%ROOT%\Guiding\Phase 4\phase04_full_data_foundation.py"
set "LOG=%ROOT%\Guiding\Phase 4\phase04_full_run.log"
set "ERR=%ROOT%\Guiding\Phase 4\phase04_full_run.err.log"
set "PROGRESS=%ROOT%\Guiding\Phase 4\phase04_full_progress.json"
set "OUT=%ROOT%\data\phase04"
set "REPORTS=%ROOT%\reports"

cd /d "%ROOT%"
python -u -B "%SCRIPT%" --batch-size 100000 --pool-limit 20000 --out-dir "%OUT%" --report-dir "%REPORTS%" --progress-file "%PROGRESS%" > "%LOG%" 2> "%ERR%"
endlocal
