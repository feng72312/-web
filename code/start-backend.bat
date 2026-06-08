@echo off
setlocal
cd /d %~dp0backend

rem cursor-sdk requires Python 3.10+
set PY=py -3.10
%PY% --version >nul 2>&1
if errorlevel 1 (
  set PY=python
)

echo [backend] Using: 
%PY% --version

set API_PORT=8001
echo [backend] Stopping old API process on port %API_PORT% if any...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort %API_PORT% -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1
timeout /t 2 /nobreak >nul
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":%API_PORT%" ^| findstr "LISTENING"') do (
  taskkill /PID %%p /F >nul 2>&1
)
timeout /t 1 /nobreak >nul

echo [backend] Installing Python dependencies...
%PY% -m pip install -r requirements.txt -q
if errorlevel 1 (
  echo [backend] pip install failed. cursor-sdk needs Python 3.10 or newer.
  pause
  exit /b 1
)

echo [backend] Starting API on http://127.0.0.1:%API_PORT%  (includes /api/v1/utils)
%PY% -m uvicorn app.main:app --reload --host 127.0.0.1 --port %API_PORT%
pause
