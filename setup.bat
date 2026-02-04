@echo off
REM EchoScribe - Quick Start Script for Windows
REM This script helps you get started with EchoScribe quickly

echo.
echo 🎬 EchoScribe - Quick Start Setup
echo ==================================
echo.

REM Check Python
echo Checking Python version...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python 3 is not installed. Please install Python 3.10 or higher.
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Found Python %PYTHON_VERSION%
echo.

REM Check FFmpeg
echo Checking FFmpeg...
ffmpeg -version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ FFmpeg is not installed.
    echo.
    echo Please install FFmpeg:
    echo   Download from https://ffmpeg.org/download.html
    echo   Or use: winget install ffmpeg
    exit /b 1
)
echo ✅ FFmpeg is installed
echo.

REM Create virtual environment
echo Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo ✅ Virtual environment created
) else (
    echo ✅ Virtual environment already exists
)
echo.

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing Python dependencies...
python -m pip install --upgrade pip
pip install -r backend\requirements.txt
echo ✅ Dependencies installed
echo.

REM Create .env file if it doesn't exist
if not exist ".env" (
    echo Creating .env file from example...
    copy .env.example .env
    echo ✅ .env file created
)
echo.

echo ==================================
echo ✅ Setup Complete!
echo ==================================
echo.
echo To start the application:
echo.
echo 1. Start the backend:
echo    cd backend ^&^& python main.py
echo.
echo 2. Open frontend:
echo    Open frontend\index.html in your browser
echo    OR run: python -m http.server 3000 --directory frontend
echo.
echo 3. Access the app at:
echo    Frontend: http://localhost:3000 (if using http.server)
echo    Backend API: http://localhost:8000
echo    API Docs: http://localhost:8000/docs
echo.
echo 📝 Note: The first transcription will download the Whisper model (~74MB for 'base')
echo.
pause
