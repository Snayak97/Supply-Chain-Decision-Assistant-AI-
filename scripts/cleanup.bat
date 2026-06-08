@echo off
REM Cleanup script to remove unwanted files and folders

echo Cleaning up unwanted files and folders...

REM Remove Python cache directories
echo Removing __pycache__ directories...
for /d /r . %%d in (__pycache__) do @if exist "%%d" (
    echo Removing: %%d
    rmdir /s /q "%%d"
)

REM Remove pytest cache
echo Removing .pytest_cache...
if exist .pytest_cache rmdir /s /q .pytest_cache

REM Remove unused files
echo Removing unused files...
if exist Dockerfile del Dockerfile
if exist main.py del main.py

REM Remove unused directories
echo Removing unused directories...
if exist data rmdir /s /q data
if exist repositories rmdir /s /q repositories
if exist services rmdir /s /q services

echo.
echo Cleanup complete!
echo.
echo Removed:
echo   - All __pycache__ directories
echo   - .pytest_cache directory
echo   - Dockerfile
echo   - main.py (root)
echo   - data/ directory
echo   - repositories/ directory
echo   - services/ directory
echo.
echo IMPORTANT: Kept:
echo   - .venv/ (virtual environment)
echo   - sc_ai.db (database)
echo   - logs/ (application logs)
echo   - All source code and schemas
echo.

pause
