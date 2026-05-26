@echo off
setlocal
cd /d %~dp0

echo [rag] Installing dependencies...
py -3.10 -m pip install -r requirements.txt -q
if errorlevel 1 (
  echo [rag] pip install failed.
  pause
  exit /b 1
)

if not exist "data\chroma" (
  echo [rag] Index not found, building from 数据库/八字 ...
  py -3.10 build_index.py
  if errorlevel 1 (
    echo [rag] build_index failed.
    pause
    exit /b 1
  )
)

echo [rag] Starting search service on http://127.0.0.1:8100
py -3.10 server.py
pause
