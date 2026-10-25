@echo off
setlocal enabledelayedexpansion

echo =====================================================================
echo   DualWell: Smart Student Wellness and Academic Performance System
echo   Startup Script for Windows Development Environment
echo =====================================================================
echo.

:: 1. Check Python installation
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Python is not installed or not found in system PATH.
    echo Please install Python 3.10+ from https://www.python.org/
    pause
    exit /b 1
)

:: 2. Check Node.js and NPM installation
where node >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo [ERROR] Node.js is not installed or not found in system PATH.
    echo Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)

:: 3. Setup Backend Environment
echo [*] Checking Backend Virtual Environment...
if not exist "backend\venv\Scripts\python.exe" (
    echo [*] Creating Python virtual environment in backend\venv...
    python -m venv backend\venv
    if %ERRORLEVEL% neq 0 (
        echo [ERROR] Failed to create Python virtual environment.
        pause
        exit /b 1
    )
    echo [*] Installing backend dependencies...
    backend\venv\Scripts\python -m pip install -r backend\requirements.txt
) else (
    echo [OK] Backend virtual environment found.
)

:: 4. Initialize Database and Seed Demo Records if needed
echo [*] Initializing SQLite database and verifying seed data...
backend\venv\Scripts\python -m app.seed
if %ERRORLEVEL% neq 0 (
    echo [WARNING] Database seed check encountered a non-fatal note. Proceeding...
)

:: 5. Setup Frontend Environment
echo [*] Checking Frontend dependencies...
if not exist "frontend\node_modules" (
    echo [*] Installing frontend npm packages...
    cd frontend
    call npm install
    cd ..
) else (
    echo [OK] Frontend packages verified.
)

:: 6. Launch Backend in separate window
echo [*] Launching FastAPI Backend on http://localhost:8000...
start "DualWell Backend API (Port 8000)" cmd /k "cd backend && venv\Scripts\python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload"

:: 7. Launch Frontend in separate window
echo [*] Launching React Frontend on http://localhost:5173...
start "DualWell Frontend Vite (Port 5173)" cmd /k "cd frontend && npm run dev -- --host --port 5173"

echo.
echo =====================================================================
echo   DualWell is starting up!
echo.
echo   Frontend Web Application:  http://localhost:5173
echo   Backend REST API:          http://localhost:8000
echo   Interactive Swagger Docs:  http://localhost:8000/docs
echo.
echo   Default Demo Login:
echo     Email:     alex.morgan@dualwell.edu
echo     Password:  DualWell2026!
echo     (or click 'One-Click Login as Alex Morgan' on login screen)
echo.
echo   To stop both servers, run:  stop.bat
echo =====================================================================
echo.
