@echo off
setlocal enabledelayedexpansion

title Sudev's Billing System - Starting...

echo.
echo =====================================================
echo  Sudev's Billing System
echo =====================================================
echo.

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python not found
    echo.
    echo Download Python 3.9+ from https://python.org
    echo Make sure to CHECK "Add Python to PATH" during install
    echo.
    pause
    exit /b
)

echo [OK] Python found: 
python --version

REM Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo.
    echo [SETUP] Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment
        pause
        exit /b
    )
    echo [OK] Virtual environment created
    echo [SETUP] Installing dependencies for first time...
    call venv\Scripts\activate.bat
    pip install -r requirements.txt --quiet --no-cache-dir
    if errorlevel 1 (
        echo [ERROR] Failed to install dependencies
        pause
        exit /b
    )
    echo [OK] Dependencies installed
) else (
    echo [OK] Virtual environment exists - using existing installation
    call venv\Scripts\activate.bat
)

REM Start the server
echo.
echo [STARTUP] Starting server...
echo.

REM Get local IP
for /f "delims=" %%a in ('python -c "import socket; s=socket.socket(); s.connect(('8.8.8.8',80)); print(s.getsockname()[0]); s.close()"') do set LOCAL_IP=%%a

echo =====================================================
echo [OK] Server running
echo =====================================================
echo.
echo COPY THIS URL AND SEND TO STAFF:
echo.
echo   http://%LOCAL_IP%:8000
echo.
echo OR use this (works on any WiFi):
echo.
echo   http://sudev-pc.local:8000
echo.
echo To generate QR code, visit:
echo   https://qr-code-generator.com/
echo   Paste: http://%LOCAL_IP%:8000
echo.
echo =====================================================
echo.
echo Press Ctrl+C to stop the server
echo.

REM Open browser after 2 seconds
timeout /t 2 /nobreak >nul
start http://localhost:8000

REM Run server
python -m uvicorn main:app --host 0.0.0.0 --port 8000

pause
