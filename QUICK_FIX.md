# Quick Fix for dlib Installation

## The Problem
`face-recognition` requires `dlib`, which needs CMake to build from source on Windows.

## Solution: Install CMake

### Step 1: Download CMake
1. Go to: https://cmake.org/download/
2. Download "Windows x64 Installer"
3. Run the installer

### Step 2: Important - Add to PATH
**During installation, make sure to check:**
- ✅ "Add CMake to system PATH"
- ✅ "Add CMake to PATH for all users" (if you have admin rights)

### Step 3: Restart Terminal/VS Code
Close and reopen your terminal or VS Code completely.

### Step 4: Verify CMake Installation
```bash
cmake --version
```
You should see the CMake version.

### Step 5: Install dlib and face-recognition
```bash
python -m pip install dlib
python -m pip install face-recognition
```

## Alternative: Use Pre-built Wheel

If CMake installation is not possible, try:

```bash
python -m pip install --only-binary :all: dlib
```

Or download a pre-built wheel manually from:
- https://pypi.org/project/dlib/#files
- Look for: `dlib-19.24.2-cp310-cp310-win_amd64.whl`

Then install:
```bash
python -m pip install dlib-19.24.2-cp310-cp310-win_amd64.whl
python -m pip install face-recognition
```

## Test Installation

After installation, test:
```bash
python -c "import dlib; import face_recognition; print('Success!')"
```
