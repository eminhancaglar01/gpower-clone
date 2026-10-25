@echo off
chcp 65001 > nul
title gpower-clone — Bilimsel Guc Analizi Calisma Tezgahi (G*Power 3.1.9.7)

echo ======================================================================
echo       gpower-clone : Bilimsel Guc Analizi Calisma Tezgahi
echo       (YZM301 Teardown Sprint — G*Power 3.1.9.7 Yeniden Gercekleme)
echo ======================================================================
echo.

set SCRIPT_DIR=%~dp0
cd /d "%SCRIPT_DIR%"

if exist ".venv\Scripts\python.exe" (
    set PYTHON_CMD=.venv\Scripts\python.exe
) else (
    set PYTHON_CMD=python
)

echo [1/2] Web Sunucusu baslatiliyor (Flask)...
echo [2/2] Tarayici aciliyor: http://localhost:5000
echo.
echo Cikis yapmak icin bu pencereyi kapatabilir veya Ctrl+C yapabilirsiniz.
echo ----------------------------------------------------------------------

start "" "http://localhost:5000"
"%PYTHON_CMD%" web\app.py

pause
