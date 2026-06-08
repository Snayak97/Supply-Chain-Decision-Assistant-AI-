@echo off
REM Setup script for SC AI Assistant MVP (Windows)
REM This script handles dependency installation, database setup, and sample data generation

echo ==========================================
echo SC AI Assistant MVP - Setup Script
echo ==========================================
echo.

REM Check if uv is installed
where uv >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Installing uv package manager...
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
) else (
    echo uv is already installed
)

echo.
echo Step 1: Installing Python dependencies with uv...
uv sync

echo.
echo Step 2: Setting up environment variables...
if not exist .env (
    copy .env.example .env
    echo Created .env file from .env.example
    echo Please edit .env file with your configuration
) else (
    echo .env file already exists
)

echo.
echo Step 3: Creating database tables...
python scripts\init_db.py

echo.
echo Step 4: Generating sample data...
python scripts\generate_mock_data.py

@REM echo.
@REM echo Step 5: Checking Ollama installation...
@REM where ollama >nul 2>nul
@REM if %ERRORLEVEL% NEQ 0 (
@REM     echo WARNING: Ollama is not installed
@REM     echo Please install Ollama from https://ollama.com
@REM     echo After installation, run: ollama pull llama3
@REM ) else (
@REM     echo Ollama is installed
@REM     echo Pulling llama3 model...
@REM     ollama pull llama3
@REM )

echo.
echo ==========================================
echo Setup complete!
echo ==========================================
echo.
echo To start the API server, run:
echo   uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
echo.
echo To access the API documentation, open:
echo   http://localhost:8000/docs
echo.

pause
