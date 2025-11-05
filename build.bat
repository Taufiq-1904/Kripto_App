@echo off
REM Build Script for SecureMessenger Pro
REM This script will create a standalone executable

echo ========================================
echo   SecureMessenger Pro - Build Script
echo ========================================
echo.

echo [1/3] Checking dependencies...
python -c "import PIL; import Crypto; print('All dependencies OK!')" 2>nul
if errorlevel 1 (
    echo ERROR: Missing dependencies!
    echo Installing required packages...
    pip install pillow pycryptodome pyinstaller
)

echo.
echo [2/3] Building executable with PyInstaller...
echo This may take a few minutes...
python -m PyInstaller build_app.spec --clean

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo Please check the error messages above.
    pause
    exit /b 1
)

echo.
echo [3/3] Build completed successfully!
echo.
echo ========================================
echo   Executable created:
echo   dist\SecureMessenger_Pro.exe
echo ========================================
echo.
echo You can now run: dist\SecureMessenger_Pro.exe
echo.
pause
