@echo off
setlocal
cd /d %~dp0

echo [rag] Installing dependencies (first run may take several minutes)...
py -3.10 -m pip install -r requirements.txt --disable-pip-version-check
if errorlevel 1 (
  echo [rag] pip install failed.
  pause
  exit /b 1
)
echo [rag] Dependencies ready.
pause
