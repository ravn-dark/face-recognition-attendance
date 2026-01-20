# Quick Install Guide - CMake & dlib

## Fastest Method (Choose One)

### Method 1: PowerShell Script (Recommended)

1. **Open PowerShell as Administrator:**
   - Press `Win + X`
   - Select "Windows PowerShell (Admin)" or "Terminal (Admin)"

2. **Navigate to project directory:**
   ```powershell
   cd C:\Users\Chhav\Desktop\system
   ```

3. **Run the installation script:**
   ```powershell
   .\install_cmake.ps1
   ```

4. **If script fails, use Method 2 below**

---

### Method 2: Manual Installation (5 minutes)

#### Step 1: Download CMake
- Go to: **https://cmake.org/download/**
- Click: **"Windows x64 Installer"** (the `.msi` file)
- Save the file

#### Step 2: Install CMake
1. Double-click the downloaded `.msi` file
2. Click "Next" through the wizard
3. **IMPORTANT**: When you see "Install Options", check:
   - ✅ **"Add CMake to system PATH for all users"**
4. Click "Install"
5. Wait for installation to complete
6. Click "Finish"

#### Step 3: Restart VS Code
- **Close VS Code completely**
- Reopen VS Code
- Open a new terminal

#### Step 4: Verify CMake
```powershell
cmake --version
```
You should see: `cmake version 3.xx.x`

#### Step 5: Install dlib and face-recognition
```powershell
python -m pip install dlib
python -m pip install face-recognition
```

#### Step 6: Restart Flask App
```powershell
python app.py
```

---

### Method 3: Using Chocolatey (If Installed)

If you have Chocolatey installed:
```powershell
choco install cmake -y
```

Then restart VS Code and run:
```powershell
python -m pip install dlib face-recognition
```

---

## Verification

After installation, test with:
```powershell
python -c "import dlib; import face_recognition; print('Success!')"
```

If you see "Success!", you're all set! 🎉

---

## Troubleshooting

### "cmake is not recognized"
- **Solution**: Restart VS Code/terminal completely
- If still not working, manually add to PATH (see INSTALL_CMAKE_STEPS.md)

### "dlib build failed"
- Make sure CMake is in PATH: `cmake --version` should work
- Try: `python -m pip install --upgrade pip`
- Then: `python -m pip install dlib`

### Still having issues?
Check `INSTALL_CMAKE_STEPS.md` for detailed troubleshooting.
