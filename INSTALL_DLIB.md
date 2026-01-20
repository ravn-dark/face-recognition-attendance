# Installing dlib on Windows

The `dlib` library requires CMake to build from source. Here are the options:

## Option 1: Install CMake (Recommended)

1. Download CMake from: https://cmake.org/download/
2. Install CMake and **make sure to check "Add CMake to system PATH"** during installation
3. Restart your terminal/VS Code
4. Run: `python -m pip install dlib`

## Option 2: Use Pre-built Wheel (Easier)

Try installing from a pre-built wheel:

```bash
python -m pip install https://files.pythonhosted.org/packages/0e/ce/f8a3cff33ac03a8219768f0694c5d703c8e037e6aba2e865f9bae22ed63c/dlib-19.24.2-cp310-cp310-win_amd64.whl
```

Or try:

```bash
python -m pip install dlib-binary
```

## Option 3: Install Visual Studio Build Tools

1. Download Visual Studio Build Tools: https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio-2022
2. Install "Desktop development with C++" workload
3. Restart terminal
4. Run: `python -m pip install dlib`

## Quick Test

After installation, test with:
```python
python -c "import dlib; print('dlib installed successfully!')"
```

Then install face-recognition:
```bash
python -m pip install face-recognition
```
