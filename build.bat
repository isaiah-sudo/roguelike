@echo off
setlocal enabledelayedexpansion
title Crypt of the Necrolord - Build System

cd /d "%~dp0"

echo ======================================================================
echo           Crypt of the Necrolord - EXE & Installer Builder
echo ======================================================================
echo.

:: 1. Detect Python
set "PYTHON_EXE="
if exist "C:\Python314\python.exe" set "PYTHON_EXE=C:\Python314\python.exe"
if "%PYTHON_EXE%"=="" (
    where python >nul 2>&1
    if !errorlevel! EQU 0 set "PYTHON_EXE=python"
)
if "%PYTHON_EXE%"=="" (
    where py >nul 2>&1
    if !errorlevel! EQU 0 set "PYTHON_EXE=py"
)

if "%PYTHON_EXE%"=="" (
    echo [ERROR] Python not found! Please ensure Python is installed and in PATH.
    pause
    exit /b 1
)

echo [1/4] Using Python: %PYTHON_EXE%

:: Ensure requirements
"%PYTHON_EXE%" -m pip install pygame-ce numpy Pillow pyinstaller >nul 2>&1

:: 2. Generate Icons
echo [2/4] Generating high-resolution icons (PNG and multi-size ICO)...
"%PYTHON_EXE%" scripts\generate_icon.py
if !errorlevel! NEQ 0 (
    echo [ERROR] Failed to generate game icons.
    pause
    exit /b 1
)

:: 3. Build Executable with PyInstaller
echo [3/4] Building standalone Windows executable with PyInstaller...
"%PYTHON_EXE%" -m PyInstaller --noconfirm CryptOfTheNecrolord.spec
if !errorlevel! NEQ 0 (
    echo [ERROR] PyInstaller build failed!
    pause
    exit /b !errorlevel!
)

:: 4. Locate Inno Setup Compiler (ISCC)
echo [4/4] Building Windows Setup Installer with Inno Setup...
set "ISCC_EXE="
where iscc >nul 2>&1
if !errorlevel! EQU 0 set "ISCC_EXE=iscc"

if "%ISCC_EXE%"=="" (
    if exist "%LocalAppData%\Programs\Inno Setup 6\ISCC.exe" (
        set "ISCC_EXE=%LocalAppData%\Programs\Inno Setup 6\ISCC.exe"
    ) else if exist "C:\Program Files (x86)\Inno Setup 6\ISCC.exe" (
        set "ISCC_EXE=C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    ) else if exist "C:\Program Files\Inno Setup 6\ISCC.exe" (
        set "ISCC_EXE=C:\Program Files\Inno Setup 6\ISCC.exe"
    )
)

if "%ISCC_EXE%"=="" (
    echo [WARNING] Inno Setup compiler (ISCC.exe) was not found in PATH or standard directories.
    echo Standalone executable was built successfully in dist\CryptOfTheNecrolord\
    echo To build the installer, install Inno Setup 6 (winget install JRSoftware.InnoSetup).
    goto :DONE
)

echo Compiling installer using: "!ISCC_EXE!"
"!ISCC_EXE!" installer.iss
if !errorlevel! NEQ 0 (
    echo [ERROR] Inno Setup compiler failed!
    pause
    exit /b !errorlevel!
)

:DONE
echo.
echo ======================================================================
echo                     BUILD COMPLETED SUCCESSFULLY!
echo ======================================================================
echo.
echo 1. Standalone Game Folder & EXE:
echo    dist\CryptOfTheNecrolord\CryptOfTheNecrolord.exe
echo.
if exist "installer_output\CryptOfTheNecrolord_Setup_v1.0.0.exe" (
    echo 2. Windows Setup Installer:
    echo    installer_output\CryptOfTheNecrolord_Setup_v1.0.0.exe
    echo.
)
echo 3. Game Icons:
echo    assets\icon.ico (Windows multi-res icon 16x16 to 256x256)
echo    assets\icon.png (256x256 window & UI icon)
echo.
echo ======================================================================
echo.
pause
