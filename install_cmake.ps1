# CMake Installation Script for Windows
# Run this script in PowerShell as Administrator

Write-Host "=== CMake Installation Helper ===" -ForegroundColor Cyan
Write-Host ""

# Check if CMake is already installed
$cmakePath = Get-Command cmake -ErrorAction SilentlyContinue
if ($cmakePath) {
    Write-Host "CMake is already installed!" -ForegroundColor Green
    & cmake --version
    exit 0
}

Write-Host "CMake is not installed. Installing..." -ForegroundColor Yellow
Write-Host ""

# Try to install using winget
Write-Host "Attempting to install CMake using winget..." -ForegroundColor Cyan
try {
    winget install --id Kitware.CMake -e --accept-package-agreements --accept-source-agreements
    Write-Host ""
    Write-Host "CMake installation completed!" -ForegroundColor Green
    Write-Host ""
    Write-Host "IMPORTANT: Please close and reopen your terminal/VS Code for changes to take effect." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After restarting, verify installation with: cmake --version" -ForegroundColor Cyan
    Write-Host "Then install dlib: python -m pip install dlib" -ForegroundColor Cyan
} catch {
    Write-Host ""
    Write-Host "Automatic installation failed. Please install manually:" -ForegroundColor Red
    Write-Host ""
    Write-Host "1. Download CMake from: https://cmake.org/download/" -ForegroundColor Yellow
    Write-Host "2. Run the installer" -ForegroundColor Yellow
    Write-Host "3. IMPORTANT: Check 'Add CMake to system PATH' during installation" -ForegroundColor Yellow
    Write-Host "4. Restart VS Code" -ForegroundColor Yellow
    Write-Host "5. Run: python -m pip install dlib" -ForegroundColor Yellow
}
