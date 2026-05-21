@echo off
REM Build script to create IGLHUD.exe using PyInstaller

echo ========================================
echo CS2 IGL HUD - EXE BUILDER
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
echo [*] Building IGLHUD.exe...

REM Ensure we run from repository root so relative paths resolve correctly
SET SCRIPT_DIR=%~dp0
PUSHD "%SCRIPT_DIR%.."

python -m PyInstaller --onefile --paths src --add-data "src\igl_hud\index.html;." --add-data "src\igl_hud\analytics.html;." --name "IGLHUD" Main.py

POPD

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ========================================
    echo [+] BUILD SUCCESSFUL!
    echo ========================================
    echo.
    echo Your executable is located at:
    echo   dist\IGLHUD.exe
    echo.
    echo The packaged executable will store runtime data next to the .exe.
    echo.
) else (
    echo.
    echo [!] BUILD FAILED!
    echo.
)

pause
