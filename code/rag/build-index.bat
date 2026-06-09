@echo off
setlocal
cd /d %~dp0

py -3.10 check_deps.py >nul 2>&1
if errorlevel 1 (
  echo [rag-index] Installing dependencies (first run may take several minutes)...
  py -3.10 -m pip install -r requirements.txt --disable-pip-version-check
  if errorlevel 1 (
    echo [rag-index] pip install failed. Run install-deps.bat manually.
    exit /b 1
  )
) else (
  echo [rag-index] Dependencies OK, skipping install.
)

echo [rag-index] Building index from 数据库/八字 (txt + doc, no pdf)...
py -3.10 build_index.py
exit /b %errorlevel%
