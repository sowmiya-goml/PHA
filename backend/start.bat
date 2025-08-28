@echo off
echo Starting PHA Database Connection Manager with UV...

REM Check if uv is installed
uv --version >nul 2>&1
if errorlevel 1 (
    echo Error: UV is not installed. Please install UV first.
    echo Visit: https://github.com/astral-sh/uv
    pause
    exit /b 1
)

REM Install/sync dependencies
echo Syncing dependencies with UV...
uv sync

REM Start the application
echo Starting FastAPI application...
echo.
echo API will be available at: http://localhost:8000
echo API Documentation: http://localhost:8000/docs
echo.
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload
