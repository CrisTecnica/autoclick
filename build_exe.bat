@echo off
REM AutoClick - Build Script for Windows
REM Gera um executável portátil .exe com PyInstaller

echo ========================================
echo   AutoClick - Build Windows
echo ========================================
echo.

echo [1/4] Verificando Python...
python --version || (
    echo ERRO: Python nao encontrado. Instale Python 3.10+ em python.org
    pause
    exit /b 1
)

echo [2/4] Instalando dependencias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias
    pause
    exit /b 1
)

echo [3/4] Instalando PyInstaller...
pip install pyinstaller
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar PyInstaller
    pause
    exit /b 1
)

echo [4/4] Compilando executavel...
pyinstaller --clean --onefile --windowed --name AutoClick ^
    --add-data "autoclick;autoclick" ^
    --hidden-import PySide6.QtCore ^
    --hidden-import PySide6.QtGui ^
    --hidden-import PySide6.QtWidgets ^
    --hidden-import pynput.keyboard ^
    --hidden-import pynput.mouse ^
    --hidden-import pynput._util.xorg ^
    --exclude-module tkinter ^
    --exclude-module test ^
    --exclude-module unittest ^
    main.py

if %errorlevel% equ 0 (
    echo.
    echo ========================================
    echo   ✅ Build concluido!
    echo ========================================
    echo   Executavel: dist\AutoClick.exe
    echo.
) else (
    echo.
    echo   ERRO: Falha no build
    pause
)
