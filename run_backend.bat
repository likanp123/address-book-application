@echo off
setlocal

REM Run from this script's directory
cd /d "%~dp0"

echo ===============================================
echo Address Book Backend - Auto Run Script
echo ===============================================
echo.

where python >nul 2>nul
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo Please install Python 3.10+ and try again.
    pause
    exit /b 1
)

echo [1/4] Installing dependencies...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo [ERROR] Dependency installation failed.
    pause
    exit /b 1
)
echo [OK] Dependencies installed.
echo.

echo [2/4] Running database migrations...
alembic upgrade head
if errorlevel 1 (
    echo [ERROR] Alembic migration failed.
    pause
    exit /b 1
)
echo [OK] Migrations applied.
echo.

echo [3/4] Running test cases...
python -m pytest -q
if errorlevel 1 (
    echo [ERROR] Tests failed.
    pause
    exit /b 1
)
echo [OK] All tests passed.
echo.

if /I "%~1"=="--check-only" (
    echo [INFO] Check-only mode complete. Skipping server startup.
    pause
    exit /b 0
)

echo [4/4] Starting backend server...
echo Swagger UI: http://127.0.0.1:8000/docs
echo Press Ctrl+C to stop the server.
echo.
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
if errorlevel 1 (
    echo [ERROR] Server exited unexpectedly.
    pause
    exit /b 1
)

endlocal

