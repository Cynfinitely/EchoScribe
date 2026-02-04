#!/bin/bash

# Start EchoScribe Backend Server

echo "🚀 Starting EchoScribe Backend..."
echo ""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✅ Virtual environment activated"
fi

# Load environment variables if .env exists
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
    echo "✅ Environment variables loaded"
fi

# Start the server
echo "🌐 Starting server on http://localhost:${PORT:-8000}"
echo "📚 API documentation: http://localhost:${PORT:-8000}/docs"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd backend
python main.py
