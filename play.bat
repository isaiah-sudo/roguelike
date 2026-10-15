@echo off
setlocal enabledelayedexpansion
title Dark Spire Roguelike

:: Ensure current directory is the script directory
cd /d "%~dp0"

echo ========================================================
echo        Dark Spire Roguelike - Windows Launcher
echo ========================================================
echo.

:: Detect Python executable
set "PYTHON_EXE="

:: 1. Check direct C:\Python314\python.exe
if exist "C:\Python314\python.exe" (
    "C:\Python314\python.exe" -c "import pygame, numpy" >nul 2>&1
    if !errorlevel! EQU 0 (
        set "PYTHON_EXE=C:\Python314\python.exe"
        goto :LAUNCH
    )
)

:: 2. Check standard 'python' in PATH
where python >nul 2>&1
if !errorlevel! EQU 0 (
    python -c "import pygame, numpy" >nul 2>&1
    if !errorlevel! EQU 0 (
        set "PYTHON_EXE=python"
        goto :LAUNCH
    )
)

:: 3. Check 'py' launcher
where py >nul 2>&1
if !errorlevel! EQU 0 (
    py -c "import pygame, numpy" >nul 2>&1
    if !errorlevel! EQU 0 (
        set "PYTHON_EXE=py"
        goto :LAUNCH
    )
)

:: 4. Fallback to any python found and install requirements if needed
if exist "C:\Python314\python.exe" (
    set "PYTHON_EXE=C:\Python314\python.exe"
) else (
    where python >nul 2>&1
    if !errorlevel! EQU 0 (
        set "PYTHON_EXE=python"
    ) else (
        where py >nul 2>&1
        if !errorlevel! EQU 0 (
            set "PYTHON_EXE=py"
        )
    )
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python was not found on your system!
    echo Please install Python from https://www.python.org/
    echo Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)

echo Installing missing dependencies (pygame-ce, numpy)...
"%PYTHON_EXE%" -m pip install pygame-ce numpy
echo.

:LAUNCH
echo Starting Dark Spire Roguelike using: %PYTHON_EXE%
echo.
"%PYTHON_EXE%" main.py

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ========================================================
    echo [ERROR] Game encountered an issue (Exit Code: %ERRORLEVEL%)
    echo ========================================================
    echo.
    pause
    exit /b %ERRORLEVEL%
)

echo.
echo Thank you for playing Dark Spire!
timeout /t 2 >nul
exit /b 0
