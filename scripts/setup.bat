@REM @echo off
@REM REM Setup script for SC AI Assistant MVP (Windows)
@REM REM This script handles dependency installation, database setup, and sample data generation

@REM echo ==========================================
@REM echo SC AI Assistant MVP - Setup Script
@REM echo ==========================================
@REM echo.

@REM REM Check if uv is installed
@REM where uv >nul 2>nul
@REM if %ERRORLEVEL% NEQ 0 (
@REM     echo Installing uv package manager...
@REM     powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
@REM ) else (
@REM     echo uv is already installed
@REM )

@REM echo.
@REM echo Step 1: Installing Python dependencies with uv...
@REM uv sync

@REM echo.
@REM echo Step 2: Setting up environment variables...
@REM if not exist .env (
@REM     copy .env.example .env
@REM     echo Created .env file from .env.example
@REM     echo Please edit .env file with your configuration
@REM ) else (
@REM     echo .env file already exists
@REM )

@REM echo.
@REM echo Step 3: Creating database tables...
@REM python scripts\init_db.py

@REM echo.
@REM echo Step 4: Generating sample data...
@REM python scripts\generate_mock_data.py

@REM @REM echo.
@REM @REM echo Step 5: Checking Ollama installation...
@REM @REM where ollama >nul 2>nul
@REM @REM if %ERRORLEVEL% NEQ 0 (
@REM @REM     echo WARNING: Ollama is not installed
@REM @REM     echo Please install Ollama from https://ollama.com
@REM @REM     echo After installation, run: ollama pull llama3
@REM @REM ) else (
@REM @REM     echo Ollama is installed
@REM @REM     echo Pulling llama3 model...
@REM @REM     ollama pull llama3
@REM @REM )

@REM echo.
@REM echo ==========================================
@REM echo Setup complete!
@REM echo ==========================================
@REM echo.
@REM echo To start the API server, run:
@REM echo   uvicorn apps.api.main:app --reload --host 0.0.0.0 --port 8000
@REM echo.
@REM echo To access the API documentation, open:
@REM echo   http://localhost:8000/docs
@REM echo.

@REM pause
