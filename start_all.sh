#!/bin/bash

# Start both Backend and Frontend
# WebGIS MSVT Full Stack

echo "========================================="
echo "Starting WebGIS MSVT Full Stack"
echo "========================================="

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null
    wait $BACKEND_PID $FRONTEND_PID 2>/dev/null
    echo "✅ All servers stopped"
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start Backend
echo "🔧 Starting Backend API..."
cd Backend
./start_server.sh &
BACKEND_PID=$!
cd ..

# Wait a bit for backend to start
sleep 3

# Start Frontend
echo "🎨 Starting Frontend..."
cd Frontend
./start_frontend.sh &
FRONTEND_PID=$!
cd ..

echo ""
echo "========================================="
echo "✅ All servers started!"
echo "========================================="
echo "Backend API:  http://localhost:8000"
echo "API Docs:     http://localhost:8000/docs"
echo "Frontend:     http://localhost:5173"
echo "========================================="
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for processes
wait $BACKEND_PID $FRONTEND_PID
