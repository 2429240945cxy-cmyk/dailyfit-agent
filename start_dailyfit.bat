@echo off
setlocal
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0start_dailyfit.ps1" -Mode live -Port 8000 -OpenBrowser
pause
