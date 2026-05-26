@echo off
setlocal
cd /d %~dp0backend

echo [backend] Installing Python dependencies...
python -m pip install -r requirements.txt -q
if errorlevel 1 (
  echo [backend] pip install failed. Check Python is installed.
  pause
  exit /b 1
)

echo [backend] Starting API on http://127.0.0.1:8000
python -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
pause
