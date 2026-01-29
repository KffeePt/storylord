@echo off
REM Setup script for Story Lord
REM Runs the configuration TUI (setup.py) using the virtual environment

cd /d "%~dp0\.."

if not exist .venv (
    echo [ERROR] Virtual environment not found!
    echo Please run 'python -m venv .venv' and install requirements.
    pause
    exit /b 1
)

echo Launching Story Lord Configuration TUI...
.venv\Scripts\python setup.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo [ERROR] Setup script exited with error code %ERRORLEVEL%.
    pause
) else (
    echo.
    echo Setup complete.
)
