@echo off
REM Build Windows .exe for Weighted Go
REM WARNING: This script is untested - created on macOS without Windows testing

echo Building Weighted Go for Windows...

REM Clean previous builds
echo Cleaning previous builds...
if exist dist rmdir /s /q dist
if exist build rmdir /s /q build
if exist "Weighted Go.spec" del "Weighted Go.spec"

REM Build with PyInstaller
echo Running PyInstaller...
python -m PyInstaller ^
    --name "Weighted Go" ^
    --windowed ^
    --clean ^
    --icon assets\icon.png ^
    run_app.py

echo.
echo Build complete!
echo Application: dist\Weighted Go\Weighted Go.exe
echo.
echo To test: dist\Weighted Go\Weighted Go.exe
