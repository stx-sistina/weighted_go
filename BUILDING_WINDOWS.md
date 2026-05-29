# Building Weighted Go on Windows

**For testers with no programming experience** - Just follow these simple steps!

## What You Need

1. **Python** - Download from [python.org/downloads](https://www.python.org/downloads/)
   - During installation, **check the box**: "Add Python to PATH" ✅
   - Click "Install Now"
   - That's it!

2. **This project's code** - Download the ZIP from GitHub or get it from the developer

## How to Build (2 minutes)

### Option 1: PowerShell (Recommended)

1. Open the project folder in File Explorer
2. Right-click in the folder → **"Open in Terminal"** or **"Open PowerShell window here"**
3. Type this command and press Enter:
   ```powershell
   .\scripts\setup_and_build_windows.ps1
   ```
4. Wait for it to finish (downloads PyInstaller, builds the app)
5. The app will open automatically when done! 🎉

### Option 2: Command Prompt

1. Open the project folder in File Explorer
2. Click in the address bar, type `cmd`, press Enter
3. Type this command and press Enter:
   ```batch
   .\scripts\setup_and_build_windows.bat
   ```
4. Wait for it to finish
5. The app will open automatically! 🎉

## What You Get

After building, you'll find the app at:
```
dist\Weighted Go\Weighted Go.exe
```

**You can share the entire `dist\Weighted Go` folder with anyone** - they don't need Python or anything else. Just run the `.exe`!

## Troubleshooting

### "Python is not recognized..."
- You need to install Python first
- Make sure you checked "Add Python to PATH" during installation
- If you already installed Python without this option, reinstall it

### "Cannot be loaded because running scripts is disabled..."
- This is a PowerShell security setting
- Use **Option 2 (Command Prompt)** instead, or
- Run this in PowerShell first (as Administrator):
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
  ```

### Build fails or app doesn't work
- Make sure you're in the project root folder (you should see `run_app.py`)
- Check that your internet connection is working (needed to download PyInstaller)
- Copy any error messages and send them to the developer

## What the Script Does

For transparency, the setup script:
1. ✅ Checks if Python is installed
2. ✅ Checks if pip (Python package manager) works
3. ✅ Installs PyInstaller (app bundling tool)
4. ✅ Cleans old build files
5. ✅ Builds the standalone `.exe`
6. ✅ Launches the app

**No scary stuff, no system changes** - just building the app!

## Questions?

Contact the developer or open an issue on GitHub.
