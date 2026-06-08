#!/bin/bash

echo ""
echo "====================================================="
echo "  Sudev's Billing System"
echo "====================================================="
echo ""

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "[ERROR] python3 not found"
    echo ""
    echo "Install Python 3.9+ from https://python.org"
    echo "Or: brew install python3  (Mac)"
    echo "    sudo apt install python3  (Linux)"
    echo ""
    exit 1
fi

echo "[OK] Python found:"
python3 --version

# Create venv if doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "[SETUP] Creating virtual environment..."
    python3 -m venv venv
    if [ $? -ne 0 ]; then
        echo "[ERROR] Failed to create virtual environment"
        exit 1
    fi
    echo "[OK] Virtual environment created"
fi

# Activate venv
echo ""
echo "[SETUP] Activating environment..."
source venv/bin/activate
echo "[OK] Environment activated"

# Upgrade pip
echo ""
echo "[SETUP] Upgrading pip..."
python -m pip install --upgrade pip --quiet 2>/dev/null || true

# Install requirements
echo ""
echo "[SETUP] Installing dependencies (this may take 30 seconds)..."
pip install -r requirements.txt --quiet --no-cache-dir
if [ $? -ne 0 ]; then
    echo "[ERROR] Failed to install dependencies"
    echo ""
    echo "Try manually running:"
    echo "  source venv/bin/activate"
    echo "  pip install -r requirements.txt"
    echo ""
    exit 1
fi
echo "[OK] Dependencies installed"

# Start server
echo ""
echo "[STARTUP] Starting server..."
echo "====================================================="
echo "[OK] Server running at http://localhost:8000"
echo "====================================================="
echo ""
echo "On your phone, use: http://192.168.x.x:8000"
echo "Find your IP: ifconfig | grep inet"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

# Open browser after 2 seconds
(sleep 2 && (open http://localhost:8000 2>/dev/null || xdg-open http://localhost:8000 2>/dev/null)) &

# Run server
python -m uvicorn main:app --host 0.0.0.0 --port 8000
