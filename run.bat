@echo off
title Queen Sheba Shopping App
echo ====================================================
echo           QUEEN SHEBA SHOPPING APP
echo   Intentionally Vulnerable AI Demo Environment
echo ====================================================
echo.

cd /d "%~dp0"

echo [1/2] Checking and installing requirements...
py -m pip install -r backend/requirements.txt >nul 2>&1
if %errorlevel% neq 0 (
    python -m pip install -r backend/requirements.txt
)

echo.
echo [2/2] Starting server at http://127.0.0.1:8001 ...
echo.
echo Open your browser at: http://127.0.0.1:8001
echo Press CTRL+C to stop the server.
echo.

py -m uvicorn backend.main:app --port 8001 --reload
if %errorlevel% neq 0 (
    python -m uvicorn backend.main:app --port 8001 --reload
)

pause
