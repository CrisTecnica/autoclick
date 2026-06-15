# AutoClick - Build Script for Windows (PowerShell)
# Generates a portable .exe using PyInstaller

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  AutoClick - Build Windows (PowerShell)" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[1/4] Checking Python..." -ForegroundColor Yellow
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "ERROR: Python not found. Install Python 3.10+ from python.org" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}
python --version

Write-Host "[2/4] Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install dependencies" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[3/4] Installing PyInstaller..." -ForegroundColor Yellow
pip install pyinstaller
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERROR: Failed to install PyInstaller" -ForegroundColor Red
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "[4/4] Building executable..." -ForegroundColor Yellow
pyinstaller --clean --onefile --windowed --name AutoClick `
    --add-data "autoclick;autoclick" `
    --hidden-import PySide6.QtCore `
    --hidden-import PySide6.QtGui `
    --hidden-import PySide6.QtWidgets `
    --hidden-import pynput.keyboard `
    --hidden-import pynput.mouse `
    --hidden-import pynput._util.xorg `
    --exclude-module tkinter `
    --exclude-module test `
    --exclude-module unittest `
    main.py

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  ✅ Build complete!" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Green
    Write-Host "  Executable: dist\AutoClick.exe"
}
else {
    Write-Host "ERROR: Build failed" -ForegroundColor Red
    Read-Host "Press Enter to exit"
}
