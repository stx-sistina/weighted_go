# All-in-one setup and build script for Windows testers
# This script checks for Python, installs PyInstaller, and builds the app
# No developer experience required!

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "Weighted Go - Windows Build Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
Write-Host "[1/4] Checking for Python..." -ForegroundColor Yellow
try {
    $pythonVersion = python --version 2>&1
    Write-Host $pythonVersion -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "ERROR: Python is not installed!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please install Python from: https://www.python.org/downloads/"
    Write-Host "Make sure to check 'Add Python to PATH' during installation"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Check if pip is available
Write-Host "[2/4] Checking for pip..." -ForegroundColor Yellow
try {
    python -m pip --version | Out-Null
    Write-Host "pip is available" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "ERROR: pip is not available!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Please reinstall Python and ensure pip is included"
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Install PyInstaller if not already installed
Write-Host "[3/4] Installing PyInstaller (if needed)..." -ForegroundColor Yellow
try {
    python -m pip install pyinstaller
    Write-Host "PyInstaller ready" -ForegroundColor Green
    Write-Host ""
} catch {
    Write-Host "ERROR: Failed to install PyInstaller" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

# Clean previous builds
Write-Host "[4/4] Building Weighted Go..." -ForegroundColor Yellow
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "Weighted Go.spec" -Force -ErrorAction SilentlyContinue

# Build the application
python -m PyInstaller `
    --name "Weighted Go" `
    --windowed `
    --clean `
    --icon assets/icon.png `
    run_app.py

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "ERROR: Build failed!" -ForegroundColor Red
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Build Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "The application is ready at:" -ForegroundColor White
Write-Host "  dist\Weighted Go\Weighted Go.exe" -ForegroundColor Cyan
Write-Host ""
Write-Host "Opening the application now..." -ForegroundColor Yellow
Write-Host ""

# Launch the application
Start-Process "dist\Weighted Go\Weighted Go.exe"

Write-Host ""
Write-Host "If the app opened successfully, you can share the entire" -ForegroundColor White
Write-Host '"dist\Weighted Go" folder with others - no Python needed!' -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
