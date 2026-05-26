@echo off
setlocal
cd /d %~dp0

echo [rag-index] Installing dependencies...
py -3.10 -m pip install -r requirements.txt -q
if errorlevel 1 (
  echo [rag-index] pip install failed.
  exit /b 1
)

echo [rag-index] Building index from 数据库/八字 (txt + doc, no pdf)...
py -3.10 build_index.py
exit /b %errorlevel%
