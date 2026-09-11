@echo off
cd /d "%~dp0"
echo Launching Bullet Cards...
echo.

where python >nul 2>nul
if %ERRORLEVEL%==0 (
    python game_v2.py
) else (
    echo Python not found! Please install Python 3.8+ from https://python.org
    echo.
    pause
)
