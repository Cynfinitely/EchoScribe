#!/bin/bash

# Start EchoScribe (API + UI on one port)

echo "Starting EchoScribe..."
echo ""

if [ -d "venv" ]; then
    source venv/bin/activate
    echo "Virtual environment activated"
fi

if [ -f ".env" ]; then
    set -a
    # shellcheck disable=SC1091
    source .env
    set +a
    echo "Environment variables loaded"
fi

PORT="${PORT:-8000}"

echo "App:            http://localhost:${PORT}"
echo "API docs:       http://localhost:${PORT}/docs"
echo "Health check:   http://localhost:${PORT}/health"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd backend
python main.py
