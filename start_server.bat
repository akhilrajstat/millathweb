@echo off
title Millath College ERP - Development Server
cd /d "%~dp0"

echo =====================================================================
echo           MILLATH COLLEGE OF TEACHER EDUCATION - ERP SYSTEM
echo =====================================================================
echo.

:: Check for virtual environment and activate if present
if exist ".venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment from .venv
    call ".venv\Scripts\activate.bat"
    goto :check_python
)

if exist "venv\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment from venv
    call "venv\Scripts\activate.bat"
    goto :check_python
)

if exist "env\Scripts\activate.bat" (
    echo [INFO] Activating virtual environment from env
    call "env\Scripts\activate.bat"
    goto :check_python
)

echo [INFO] Using system Python environment.

:check_python
echo [INFO] Checking Python environment...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    py --version >nul 2>&1
    if %errorlevel% equ 0 (
        set PYTHON_CMD=py
        goto :start_server
    )
    echo [ERROR] Python was not found in your system PATH.
    echo Please ensure Python is installed and added to PATH.
    echo.
    pause
    exit /b 1
)

set PYTHON_CMD=python

:start_server
echo.
echo ---------------------------------------------------------------------
echo  Server URL : http://127.0.0.1:8000/
echo  Admin URL  : http://127.0.0.1:8000/admin/
echo  Press Ctrl+C to stop the server.
echo ---------------------------------------------------------------------
echo.

%PYTHON_CMD% manage.py runserver 127.0.0.1:8000

if %errorlevel% neq 0 (
    echo.
    echo [ERROR] The server exited with error code %errorlevel%.
    pause
)
