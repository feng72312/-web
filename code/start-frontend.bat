@echo off
setlocal
cd /d %~dp0frontend

echo [frontend] Stopping old preview/dev on port 5173 if any...
powershell -NoProfile -Command "Get-NetTCPConnection -LocalPort 5173 -State Listen -ErrorAction SilentlyContinue | ForEach-Object { Stop-Process -Id $_.OwningProcess -Force -ErrorAction SilentlyContinue }" >nul 2>&1
timeout /t 2 /nobreak >nul

echo [frontend] Installing dependencies if needed...
if not exist node_modules (
  call npm install --cache .npm-cache
  if errorlevel 1 goto failed
)

echo [frontend] Building production bundle (API -> http://127.0.0.1:8001/api/v1)...
call npm run build
if errorlevel 1 goto failed

echo [frontend] Starting preview on http://127.0.0.1:5173
echo [frontend] After open: Ctrl+F5 hard refresh if you still see old index-*.js in DevTools
call npm run preview
goto end

:failed
echo [frontend] Failed to start. Try running in PowerShell:
echo   cd d:\ZY\code\frontend
echo   npm install
echo   npm run build
echo   npm run preview
pause
exit /b 1

:end
pause
