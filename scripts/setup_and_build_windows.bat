@echo off
REM All-in-one setup and build script for Windows testers
REM This script checks for Python, installs PyInstaller, and builds the app
REM No developer experience required!

echo ============================================
echo Weighted Go - Windows Build Setup
echo ============================================
echo.

REM Check if Python is installed
echo [1/4] Checking for Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python from: https://www.python.org/downloads/
    echo Make sure to check "Add Python to PATH" during installation
    echo.
    pause
    exit /b 1
)
python --version
echo.

REM Check if pip is available
echo [2/4] Checking for pip...
python -m pip --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: pip is not available!
    echo.
    echo Please reinstall Python and ensure pip is included
    echo.
    pause
    exit /b 1
)
echo pip is available
echo.

REM Install PyInstaller if not already installed
echo [3/4] Installing PyInstaller (if needed)...
python -m pip install pyinstaller
if errorlevel 1 (
    echo ERROR: Failed to install PyInstaller
    echo.
    pause
    exit /b 1
)
echo PyInstaller ready
echo.

REM Clean previous builds
echo [4/4] Building Weighted Go...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist "Weighted Go.spec" del "Weighted Go.spec"

REM Build the application
python -m PyInstaller ^
    --name "Weighted Go" ^
    --windowed ^
    --clean ^
    --icon assets\icon.png ^
    run_app.py

if errorlevel 1 (
    echo.
    echo ERROR: Build failed!
    echo.
    pause
    exit /b 1
)

echo.
echo ============================================
echo Build Complete!
echo ============================================
echo.
echo The application is ready at:
echo   dist\Weighted Go\Weighted Go.exe
echo.
echo Opening the application now...
echo.

REM Launch the application
start "" "dist\Weighted Go\Weighted Go.exe"

echo.
echo If the app opened successfully, you can share the entire
echo "dist\Weighted Go" folder with others - no Python needed!
echo.
pause
