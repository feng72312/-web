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

echo [backend] Stopping old API process on port 8000 if any...
for /f "tokens=5" %%p in ('netstat -ano ^| findstr ":8000" ^| findstr "LISTENING"') do (
  taskkill /PID %%p /F >nul 2>&1
)

echo [backend] Installing Python dependencies...
%PY% -m pip install -r requirements.txt -q
if errorlevel 1 (
  echo [backend] pip install failed. cursor-sdk needs Python 3.10 or newer.
  pause
  exit /b 1
)

echo [backend] Starting API on http://127.0.0.1:8000
%PY% -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
