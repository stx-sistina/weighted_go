# Build Windows .exe for Weighted Go
# WARNING: This script is untested - created on macOS without Windows testing

Write-Host "Building Weighted Go for Windows..." -ForegroundColor Green

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
Remove-Item -Path "dist" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "build" -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item -Path "Weighted Go.spec" -Force -ErrorAction SilentlyContinue

# Build with PyInstaller
Write-Host "Running PyInstaller..." -ForegroundColor Yellow
python -m PyInstaller `
    --name "Weighted Go" `
    --windowed `
    --clean `
    --icon assets/icon.png `
    run_app.py

Write-Host ""
Write-Host "Build complete!" -ForegroundColor Green
Write-Host "Application: dist\Weighted Go\Weighted Go.exe"
Write-Host ""
Write-Host "To test: .\dist\Weighted Go\Weighted Go.exe"
