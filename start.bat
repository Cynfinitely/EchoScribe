@echo off
REM Start EchoScribe Backend Server

echo.
echo 🚀 Starting EchoScribe Backend...
echo.

REM Activate virtual environment if it exists
if exist "venv" (
    call venv\Scripts\activate.bat
    echo ✅ Virtual environment activated
)

REM Load environment variables if .env exists
if exist ".env" (
    for /f "usebackq tokens=*" %%a in (".env") do (
        set %%a
    )
    echo ✅ Environment variables loaded
)

REM Start the server
echo 🌐 Starting server on http://localhost:%PORT%
if "%PORT%"=="" (
    echo 🌐 Starting server on http://localhost:8000
)
echo 📚 API documentation: http://localhost:%PORT%/docs
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
python main.py
