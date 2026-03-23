@echo off
title Stock Chart Server
echo Starting stock chart server...
echo.
python server.py
if errorlevel 1 (
    echo.
    echo [ERROR] Python not found. Please install Python first: https://www.python.org/downloads/
    pause
)
