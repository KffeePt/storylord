@echo off
title Shiva - guac
echo Starting Shiva Protocol...
call npx tsx "C:/Users/santi/Documents/GitHub/vishnu/codeman/singletons/shiva/index.ts" "C:\Users\santi\Documents\guac"
echo.
echo --------------------------------------------------------------------------------
echo   SHIVA PROCESS TERMINATED
echo --------------------------------------------------------------------------------
pause
del "%~f0" & exit
