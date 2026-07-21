@echo off
REM  Foundry Core AI - baslatici
REM  Kurulum yapilmadiysa once: powershell -ExecutionPolicy Bypass -File install.ps1
cd /d "%~dp0"

if not exist "venv\Scripts\python.exe" (
    echo Sanal ortam bulunamadi. Once kurulumu calistirin:
    echo   powershell -ExecutionPolicy Bypass -File install.ps1
    pause
    exit /b 1
)

echo Foundry Core AI baslatiliyor... Arayuz: http://localhost:8000
echo Durdurmak icin bu pencerede Ctrl+C.
venv\Scripts\python.exe api_server.py
pause
