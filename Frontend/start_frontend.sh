#!/bin/bash

# Start Frontend (Vue 3 + Vite)
# WebGIS MSVT

echo "=================================="
echo "Starting WebGIS MSVT Frontend"
echo "=================================="

cd Frontend

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

# Start dev server
echo ""
echo "🚀 Starting Vite dev server..."
echo "🌐 URL: http://localhost:5173"
echo "📊 Backend API: http://localhost:8000"
echo ""

npm run dev
