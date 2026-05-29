#!/bin/bash
# Package macOS build for distribution
# Run this AFTER build_macos.sh

set -e

echo "Packaging Weighted Go for macOS distribution..."

# Check if build exists
if [ ! -d "dist/Weighted Go.app" ]; then
    echo "ERROR: Build not found!"
    echo "Please run build_macos.sh first"
    exit 1
fi

# Create releases directory
mkdir -p releases

# Get version from version file or use date
DATE=$(date +%Y-%m-%d)
PACKAGE_NAME="WeightedGo-macOS-${DATE}"

# Create ZIP package (preserves macOS metadata)
echo "Creating ${PACKAGE_NAME}.zip..."
cd dist
zip -r "../releases/${PACKAGE_NAME}.zip" "Weighted Go.app"
cd ..

# Also create a DMG (optional, more native for macOS)
echo "Creating ${PACKAGE_NAME}.dmg..."
hdiutil create -volname "Weighted Go" -srcfolder "dist/Weighted Go.app" -ov -format UDZO "releases/${PACKAGE_NAME}.dmg"

echo ""
echo "============================================"
echo "Packages created successfully!"
echo "============================================"
echo ""
echo "Files:"
echo "  releases/${PACKAGE_NAME}.zip (for GitHub)"
echo "  releases/${PACKAGE_NAME}.dmg (for macOS users)"
echo ""
echo "You can now upload these to GitHub Releases"
echo ""
