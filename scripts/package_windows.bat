@echo off
REM Package Windows build for distribution
REM Run this AFTER build_windows.bat

echo Packaging Weighted Go for Windows distribution...

REM Check if build exists
if not exist "dist\Weighted Go\Weighted Go.exe" (
    echo ERROR: Build not found!
    echo Please run build_windows.bat first
    pause
    exit /b 1
)

REM Create releases directory
if not exist releases mkdir releases

REM Get version from a version file or use date
for /f "tokens=2-4 delims=/ " %%a in ('date /t') do (set mydate=%%c-%%a-%%b)
set PACKAGE_NAME=WeightedGo-Windows-%mydate%

REM Create ZIP package
echo Creating %PACKAGE_NAME%.zip...
powershell -Command "Compress-Archive -Path 'dist\Weighted Go' -DestinationPath 'releases\%PACKAGE_NAME%.zip' -Force"

if errorlevel 1 (
    echo ERROR: Failed to create ZIP
    pause
    exit /b 1
)

echo.
echo ============================================
echo Package created successfully!
echo ============================================
echo.
echo File: releases\%PACKAGE_NAME%.zip
echo.
echo You can now upload this to GitHub Releases
echo.
pause
