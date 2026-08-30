#!/usr/bin/env bash

set -e

echo "======================================"
echo " Healthcare Data API"
echo "======================================"

# Create virtual environment if it does not exist
if [ ! -d ".venv" ]; then
    echo "[1/4] Creating virtual environment..."
    python -m venv .venv
else
    echo "[1/4] Virtual environment already exists."
fi

# Activate virtual environment
echo "[2/4] Activating virtual environment..."
source .venv/Scripts/activate

# Install dependencies
echo "[3/4] Installing dependencies..."
python -m pip install --upgrade pip
pip install -r requirements.txt

# Run data ingestion
echo "[4/4] Fetching and processing healthcare data..."
python scripts/ingest.py

echo ""
echo "======================================"
echo " Starting FastAPI server"
echo "======================================"
echo "API:  http://127.0.0.1:8000"
echo "Docs: http://127.0.0.1:8000/docs"
echo ""

python -m uvicorn app.main:app --host 127.0.0.1 --port 8000