@echo off
setlocal

REM Check for Python 3
python --version 2>nul | findstr /r "^Python 3" >nul
if %errorlevel% neq 0 (
    echo Python 3 is not installed. Please install Python 3 and try again.
    exit /b 1
)

REM Check for pip
python -m pip --version 2>nul | findstr /r "pip" >nul
if %errorlevel% neq 0 (
    echo pip is not installed or not working. Please install pip and try again.
    exit /b 1
)

REM Run the Python script
python .\appdata\install_packages.py
endlocal
pause
