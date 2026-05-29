# Contributing to Weighted Go

We welcome contributions! This guide covers development setup, testing, and building standalone applications.

## Development Setup

### Installation

```bash
# Install the package in development mode
pip install -e .

# Install development dependencies (pytest, pyinstaller)
pip install -e ".[dev]"
# or
pip install -r requirements-dev.txt
```

### Running Tests

```bash
# All tests (71 total)
pytest tests/ -v

# Specific modules
pytest tests/test_core.py -v        # 47 tests
pytest tests/test_sgf_reader.py -v  # 24 tests
```

### Running the GUI

```bash
# From project root
./scripts/run_gui.sh
# or
python -m weighted_go.gui.run_gui
# or
python run_app.py
```

## Building Standalone Applications

### macOS

Build a standalone .app bundle:

```bash
./scripts/build_macos.sh
```

This creates `dist/Weighted Go.app` which can be distributed without requiring Python installation.

**Requirements:**
- PyInstaller 6.0+ (`pip install pyinstaller`)
- Python 3.13+ (or adjust SDK version warnings)

**Output:**
- `dist/Weighted Go.app` - Standalone macOS application
- `build/` - Intermediate build files (can be deleted)

**Testing:**
```bash
open "dist/Weighted Go.app"
```

### Windows

Build a standalone .exe:

**Using PowerShell (recommended):**
```powershell
.\scripts\build_windows.ps1
```

**Using Command Prompt:**
```batch
.\scripts\build_windows.bat
```

**Requirements:**
- PyInstaller 6.0+ (`pip install pyinstaller`)
- Python 3.8+ (tested with 3.13)

**Output:**
- `dist\Weighted Go\Weighted Go.exe` - Standalone Windows application
- `dist\Weighted Go\` - Directory contains .exe and all dependencies
- `build\` - Intermediate build files (can be deleted)

**Testing:**
```powershell
.\dist\Weighted Go\Weighted Go.exe
```

**Note:** These scripts were created on macOS and are untested on Windows. Please report any issues!

### Manual Build

If the build script doesn't work, use PyInstaller directly:

```bash
# Clean previous builds
rm -rf dist build "Weighted Go.spec"

# Build
python -m PyInstaller --name "Weighted Go" --windowed run_app.py

# Output: dist/Weighted Go.app (macOS) or dist/Weighted Go.exe (Windows)
```

## Project Architecture

See [CLAUDE.md](CLAUDE.md) for detailed architecture and development guidance.

## Reporting Issues

- **Bugs**: Open an issue with steps to reproduce
- **Feature requests**: Describe the use case and expected behavior
- **Build issues**: Include OS, Python version, and build output

Thank you for contributing to Weighted Go!
