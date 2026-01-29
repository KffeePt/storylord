@echo off
cd /d "%~dp0\.."
python setup.py --deploy
pause
