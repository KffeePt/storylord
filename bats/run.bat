@echo off
setlocal
cd /d "%~dp0\.."

if not exist ".venv" (
    echo Creating virtual environment...
    python -m venv .venv
)

echo Activating environment...
call .venv\Scripts\activate

echo Installing dependencies...
pip install -r src/requirements.txt > nul

echo Launching Story Lord...
python src/main.py

pause
