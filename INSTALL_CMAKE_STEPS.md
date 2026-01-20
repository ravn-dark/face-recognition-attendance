# Step-by-Step CMake Installation Guide

## Quick Installation Steps

### Option 1: Using Windows Package Manager (winget) - Recommended

1. Open PowerShell as Administrator (Right-click PowerShell → Run as Administrator)
2. Run this command:
   ```powershell
   winget install --id Kitware.CMake -e
   ```
3. When prompted, type `Y` and press Enter
4. Wait for installation to complete
5. **IMPORTANT**: Close and reopen your terminal/VS Code
6. Verify installation:
   ```powershell
   cmake --version
   ```
7. If it shows the version, you're good! Now install dlib:
   ```powershell
   python -m pip install dlib
   python -m pip install face-recognition
   ```

### Option 2: Manual Installation

1. **Download CMake:**
   - Go to: https://cmake.org/download/
   - Click "Windows x64 Installer" (or "Windows win64-x64 Installer")
   - Download the `.msi` file

2. **Install CMake:**
   - Run the downloaded `.msi` installer
   - **CRITICAL**: During installation, check this option:
     - ✅ **"Add CMake to system PATH"** (or "Add CMake to PATH for all users")
   - Click "Install" and wait for completion

3. **Restart VS Code:**
   - Close VS Code completely
   - Reopen VS Code
   - Open a new terminal

4. **Verify Installation:**
   ```powershell
   cmake --version
   ```
   You should see something like: `cmake version 3.xx.x`

5. **Install dlib and face-recognition:**
   ```powershell
   python -m pip install dlib
   python -m pip install face-recognition
   ```

6. **Restart your Flask app:**
   ```powershell
   python app.py
   ```

## Troubleshooting

### If `cmake --version` doesn't work after installation:

1. **Check if CMake is installed:**
   - Look in: `C:\Program Files\CMake\bin\cmake.exe`
   - Or: `C:\Program Files (x86)\CMake\bin\cmake.exe`

2. **Add to PATH manually:**
   - Press `Win + X` → System → Advanced system settings
   - Click "Environment Variables"
   - Under "System variables", find "Path" and click "Edit"
   - Click "New" and add: `C:\Program Files\CMake\bin`
   - Click OK on all dialogs
   - **Restart VS Code**

3. **Alternative: Use full path:**
   ```powershell
   & "C:\Program Files\CMake\bin\cmake.exe" --version
   ```

### If dlib still fails to build:

1. Make sure you have Visual Studio Build Tools:
   - Download: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
   - Install "Desktop development with C++" workload

2. Or try installing from a pre-built wheel (if available for your Python version)

## After Installation

Once CMake is installed and dlib/face-recognition are installed, restart your Flask app and face recognition will be enabled automatically!
