@echo off
setlocal enabledelayedexpansion
title Hologram Persona Chatbot
echo ====================================================
echo      Hologram Persona Chatbot - Launcher
echo ====================================================

:: Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python 3 is not found in PATH!
    echo Please install Python 3.10+ from python.org and check "Add to PATH".
    pause
    exit /b 1
)

:: Check if virtual environment exists
if not exist "venv\Scripts\activate.bat" (
    echo [SETUP] Virtual environment not found. Creating venv...
    python -m venv venv
    if errorlevel 1 (
        echo [ERROR] Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo [SETUP] Installing required dependencies...
    call venv\Scripts\activate.bat
    python -m pip install --upgrade pip
    pip install -r requirements.txt
    echo [SETUP] Setup complete!
) else (
    call venv\Scripts\activate.bat
)

:: Check for .env file
if not exist ".env" (
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
        echo [NOTICE] Created .env from .env.example.
        echo Please ensure you set your GEMINI_API_KEY in the .env file!
    )
)

echo.
echo Starting Web Server on http://localhost:8000 ...
start "Hologram Persona Server" venv\Scripts\python.exe app.py
timeout /t 3 /nobreak >nul

echo.
echo ====================================================
echo Server is LIVE!
echo Local URL: http://localhost:8000
echo ====================================================
echo.
echo [1] Press any key to also launch a FREE Cloudflare Public Tunnel
echo     (Allows anyone on mobile or external networks to test it!)
echo [2] Or close this window if you only want local testing.
echo.
pause

echo Starting Cloudflare tunnel...
npx -y cloudflared tunnel --url http://127.0.0.1:8000
pause
