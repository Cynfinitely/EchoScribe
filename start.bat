@echo off
REM Start EchoScribe (API + UI on one port)

echo.
echo Starting EchoScribe...
echo.

if exist "venv" (
    call venv\Scripts\activate.bat
    echo Virtual environment activated
)

if exist ".env" (
    for /f "usebackq tokens=* eol=#" %%a in (".env") do (
        set %%a
    )
    echo Environment variables loaded
)

if "%PORT%"=="" set PORT=8000

echo App:            http://localhost:%PORT%
echo API docs:       http://localhost:%PORT%/docs
echo Health check:   http://localhost:%PORT%/health
echo.
echo Press Ctrl+C to stop the server
echo.

cd backend
python main.py
