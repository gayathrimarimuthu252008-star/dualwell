@echo off
echo =====================================================================
echo   DualWell: Stopping Services
echo =====================================================================
echo.

echo [*] Stopping backend processes on port 8000...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":8000" ^| findstr "LISTENING"') do (
    echo Killing PID %%a on port 8000...
    taskkill /F /PID %%a >nul 2>nul
)

echo [*] Stopping frontend processes on port 5173...
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":5173" ^| findstr "LISTENING"') do (
    echo Killing PID %%a on port 5173...
    taskkill /F /PID %%a >nul 2>nul
)

echo.
echo [OK] DualWell backend and frontend processes stopped.
echo.
