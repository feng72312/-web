@echo off
setlocal
echo Starting Bazi app (rag + backend + frontend)...
echo.
start "Bazi RAG" cmd /k "%~dp0rag\start-rag.bat"
timeout /t 5 /nobreak >nul
start "Bazi Backend" cmd /k "%~dp0start-backend.bat"
timeout /t 3 /nobreak >nul
start "Bazi Frontend" cmd /k "%~dp0start-frontend.bat"
echo.
echo RAG: http://127.0.0.1:8100/health
echo Backend: http://127.0.0.1:8000/docs
echo Frontend: http://127.0.0.1:5173
echo.
pause
