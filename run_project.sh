#!/usr/bin/env bash
# ====================================================
# Hologram Persona Chatbot - Unix/macOS Launcher
# ====================================================

set -e

echo "===================================================="
echo "     Hologram Persona Chatbot - Launcher"
echo "===================================================="

# Check Python version
if command -v python3 &>/dev/null; then
    PYTHON_CMD=python3
elif command -v python &>/dev/null; then
    PYTHON_CMD=python
else
    echo "[ERROR] Python 3 is required but not found."
    exit 1
fi

# Set up virtualenv if not present
if [ ! -d "venv" ]; then
    echo "[SETUP] Creating virtual environment..."
    $PYTHON_CMD -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    echo "[SETUP] Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
else
    source venv/bin/activate
fi

# Check for .env file
if [ ! -f ".env" ] && [ -f ".env.example" ]; then
    cp .env.example .env
    echo "[NOTICE] Created .env template. Please enter your GEMINI_API_KEY in .env!"
fi

echo ""
echo "Starting Hologram Persona Server on http://localhost:8000 ..."
python app.py
