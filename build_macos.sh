#!/bin/bash
# Build macOS .app bundle for Weighted Go

set -e  # Exit on error

echo "Building Weighted Go for macOS..."

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf dist build "Weighted Go.spec"

# Build with PyInstaller
echo "Running PyInstaller..."
python -m PyInstaller \
    --name "Weighted Go" \
    --windowed \
    --clean \
    --icon assets/icon.png \
    run_app.py

echo ""
echo "Build complete!"
echo "Application: dist/Weighted Go.app"
echo ""
echo "To test: open 'dist/Weighted Go.app'"
