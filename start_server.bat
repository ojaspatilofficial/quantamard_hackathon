@echo off
echo ====================================
echo Starting CryptexQ Server
echo ====================================
echo.

cd /d "%~dp0"

echo Checking Python installation...
python --version
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    pause
    exit /b 1
)

echo.
echo Starting Flask server...
echo.
echo ====================================
echo Once server starts, open your browser and go to:
echo https://localhost:5000/home
echo ====================================
echo.
echo Press Ctrl+C to stop the server when done.
echo.

python app.py

pause
