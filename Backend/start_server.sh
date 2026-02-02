#!/bin/bash

# Start FastAPI Backend Server
# WebGIS MSVT

echo "=================================="
echo "Starting WebGIS MSVT Backend API"
echo "=================================="

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate venv
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q -r requirements.txt

# Start server
echo ""
echo "🚀 Starting FastAPI server..."
echo "📝 API Docs: http://localhost:8000/docs"
echo "📊 Database: webgis_msvt"
echo ""

uvicorn main:app --reload --host 0.0.0.0 --port 8000
