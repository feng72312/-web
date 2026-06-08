@echo off
setlocal
echo Starting Bazi app (rag + backend + frontend)...
echo.
start "Bazi RAG" cmd /k "%~dp0rag\start-rag.bat"
timeout /t 5 /nobreak >nul
start "Bazi Backend" cmd /k "%~dp0start-backend.bat"
timeout /t 3 /nobreak >nul
py -3.10 "%~dp0backend\scripts\check_utils_api.py" http://127.0.0.1:8001
if errorlevel 1 (
  echo [warn] Backend missing /api/v1/utils - close old Bazi Backend window and run start-backend.bat again
)
start "Bazi Frontend" cmd /k "%~dp0start-frontend.bat"
echo.
echo RAG: http://127.0.0.1:8100/health
echo Backend: http://127.0.0.1:8001/docs  (must include utils routes after code update)
echo Frontend: http://127.0.0.1:5173
echo.
pause
