@echo off
REM Quick Launch Script for SecureMessenger Pro
REM Double-click this file to run the application

title SecureMessenger Pro

REM Check if executable exists
if not exist "dist\SecureMessenger_Pro.exe" (
    echo ========================================
    echo   ERROR: Executable not found!
    echo ========================================
    echo.
    echo The executable file does not exist.
    echo Please build it first by running: build.bat
    echo.
    pause
    exit /b 1
)

echo ========================================
echo   Starting SecureMessenger Pro...
echo ========================================
echo.

REM Run the application
start "" "dist\SecureMessenger_Pro.exe"

echo Application started!
echo.
echo You can close this window now.
timeout /t 2 >nul
exit
