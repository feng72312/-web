@echo off
setlocal
cd /d %~dp0

py -3.10 check_deps.py >nul 2>&1
if errorlevel 1 (
  echo [rag] First-time setup: installing dependencies, please wait...
  echo [rag] This can take 2-5 minutes on slow networks.
  py -3.10 -m pip install -r requirements.txt --disable-pip-version-check
  if errorlevel 1 (
    echo [rag] pip install failed. Run install-deps.bat manually.
    pause
    exit /b 1
  )
  echo [rag] Dependencies installed.
) else (
  echo [rag] Dependencies OK, skipping install.
)

if not exist "data\chroma" (
  echo [rag] Index not found, building from database folders ...
  py -3.10 build_index.py
  if errorlevel 1 (
    echo [rag] build_index failed.
    pause
    exit /b 1
  )
)

set RAG_RERANK=1
echo [rag] Starting search service on http://127.0.0.1:8100 (rerank enabled locally)
py -3.10 server.py
pause
