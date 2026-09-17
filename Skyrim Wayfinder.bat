@echo off
setlocal

set "PROJECT_DIR=%~dp0"
set "PYTHONW=%PROJECT_DIR%.venv\Scripts\pythonw.exe"

if not exist "%PYTHONW%" (
    echo Skyrim Wayfinder is not set up yet.
    echo.
    echo From this folder, run:
    echo   python -m venv .venv
    echo   .venv\Scripts\python -m pip install -e ".[dev]"
    echo.
    pause
    exit /b 1
)

start "Skyrim Wayfinder" /D "%PROJECT_DIR%" "%PYTHONW%" -m skyrim_wayfinder
