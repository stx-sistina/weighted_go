# Release Guide

Guide for creating and publishing releases on GitHub.

## What Are Releases?

GitHub Releases allow you to distribute pre-built binaries that users can download and run **without installing Python**. Perfect for non-technical users!

## Building Release Packages

### macOS

```bash
# 1. Build the app
./scripts/build_macos.sh

# 2. Test it works
open "dist/Weighted Go.app"

# 3. Package for distribution
./scripts/package_macos.sh
```

This creates:
- `releases/WeightedGo-macOS-YYYY-MM-DD.zip` - For GitHub upload
- `releases/WeightedGo-macOS-YYYY-MM-DD.dmg` - Native macOS installer

### Windows

```powershell
# 1. Build the app
.\scripts\build_windows.ps1

# 2. Test it works
.\dist\Weighted Go\Weighted Go.exe

# 3. Package for distribution
.\scripts\package_windows.ps1
```

This creates:
- `releases\WeightedGo-Windows-YYYY-MM-DD.zip` - For GitHub upload

## Publishing to GitHub

### Option 1: GitHub Web Interface (Easy)

1. Go to your repository on GitHub
2. Click **"Releases"** (right sidebar)
3. Click **"Draft a new release"**
4. Fill in the form:
   - **Tag**: `v1.0.0` (or whatever version)
   - **Title**: `Weighted Go v1.0.0`
   - **Description**: Release notes (what's new, what changed)
5. **Attach files**: Drag and drop the ZIP files from `releases/` folder
   - `WeightedGo-macOS-YYYY-MM-DD.zip`
   - `WeightedGo-Windows-YYYY-MM-DD.zip`
6. Click **"Publish release"**

### Option 2: GitHub CLI (Fast)

```bash
# Install GitHub CLI first: https://cli.github.com/

# Create a release with both packages
gh release create v1.0.0 \
    releases/WeightedGo-macOS-*.zip \
    releases/WeightedGo-Windows-*.zip \
    --title "Weighted Go v1.0.0" \
    --notes "Initial release with GUI and CLI tools"
```

## What Users Get

After you publish, users can:

1. Go to your GitHub repository → Releases
2. Download the ZIP for their platform (macOS or Windows)
3. Extract the ZIP
4. **Run the app directly - no Python installation needed!**

### macOS Users:
- Extract `WeightedGo-macOS-*.zip`
- Double-click `Weighted Go.app`
- (First time: Right-click → Open to bypass Gatekeeper warning)

### Windows Users:
- Extract `WeightedGo-Windows-*.zip`
- Open the extracted folder
- Double-click `Weighted Go.exe`

## PyInstaller: How It Works

PyInstaller bundles everything needed into a standalone package:
- ✅ Python interpreter (embedded)
- ✅ All Python libraries (Tkinter, etc.)
- ✅ Your code and assets
- ✅ Application icon

**Users don't need Python** - everything is included in the package.

## File Sizes

Expect packages to be around:
- macOS: ~15-25 MB (ZIP), ~30-40 MB (DMG)
- Windows: ~10-20 MB (ZIP)

This is normal - the Python interpreter and libraries are bundled.

## Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- `v1.0.0` - Major release
- `v1.1.0` - Minor update (new features)
- `v1.0.1` - Patch (bug fixes)

## Example Release Notes Template

```markdown
## Weighted Go v1.0.0

### Features
- GUI for analyzing Go games with weighted scoring
- Support for uniform, center-square, and center-diamond weights
- SGF file loading with game metadata
- Dead stone marking with live score updates
- Territory and heatmap visualization modes
- Position editing with multiple modes

### Downloads
- **macOS**: Download `WeightedGo-macOS-*.zip`, extract, and run
- **Windows**: Download `WeightedGo-Windows-*.zip`, extract, and run

No Python installation required!

### Known Issues
- Windows build is untested (testers wanted!)
- macOS may show Gatekeeper warning (right-click → Open)

### System Requirements
- macOS 10.13+ or Windows 10+
- ~50 MB disk space
```

## Automation (Optional)

For future releases, consider GitHub Actions to auto-build on every tag:
- See `.github/workflows/release.yml` (create this file)
- Automatically builds macOS and Windows on push of version tags
- Creates GitHub Release with binaries attached

## Questions?

- GitHub Releases docs: https://docs.github.com/en/repositories/releasing-projects-on-github
- PyInstaller docs: https://pyinstaller.org/
