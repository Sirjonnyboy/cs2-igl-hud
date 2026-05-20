@echo off
REM Build script to create Scout.exe using PyInstaller

echo ========================================
echo CS2 SCOUT - EXE BUILDER
echo ========================================

echo.
echo [*] Checking if PyInstaller is installed...
pip show pyinstaller >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [!] PyInstaller not found. Installing...
    pip install pyinstaller
) else (
    echo [+] PyInstaller found.
)

echo.
echo [*] Building Scout.exe...
pyinstaller --onefile --windowed --icon=scout.ico --name "CS2Scout" --add-data "scout_config.json:." Scout.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo [+] BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Your executable is located at:
    echo   dist\CS2Scout.exe
    echo.
    echo You can now distribute this .exe to your teammates!
    echo.
) else (
    echo.
    echo [!] BUILD FAILED!
    echo.
)

pause
