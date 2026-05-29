# Package Windows build for distribution
# Run this AFTER build_windows.ps1

Write-Host "Packaging Weighted Go for Windows distribution..." -ForegroundColor Green

# Check if build exists
if (-not (Test-Path "dist\Weighted Go\Weighted Go.exe")) {
    Write-Host "ERROR: Build not found!" -ForegroundColor Red
    Write-Host "Please run build_windows.ps1 first"
    Read-Host "Press Enter to exit"
    exit 1
}

# Create releases directory
New-Item -ItemType Directory -Force -Path "releases" | Out-Null

# Get version from version file or use date
$date = Get-Date -Format "yyyy-MM-dd"
$packageName = "WeightedGo-Windows-$date"

# Create ZIP package
Write-Host "Creating $packageName.zip..." -ForegroundColor Yellow
Compress-Archive -Path "dist\Weighted Go" -DestinationPath "releases\$packageName.zip" -Force

if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to create ZIP" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "============================================" -ForegroundColor Green
Write-Host "Package created successfully!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Green
Write-Host ""
Write-Host "File: releases\$packageName.zip" -ForegroundColor Cyan
Write-Host ""
Write-Host "You can now upload this to GitHub Releases" -ForegroundColor White
Write-Host ""
Read-Host "Press Enter to exit"
