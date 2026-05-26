@echo off
setlocal
cd /d %~dp0frontend

echo [frontend] Installing dependencies if needed...
if not exist node_modules (
  call npm install --cache .npm-cache
  if errorlevel 1 goto failed
)

echo [frontend] Building production bundle...
call npm run build
if errorlevel 1 goto failed

echo [frontend] Starting preview on http://127.0.0.1:5173
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
