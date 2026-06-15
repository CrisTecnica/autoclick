#!/bin/bash
# AutoClick - Linux Installer
# Instala o AutoClick no sistema via .deb ou instalação direta

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "========================================"
echo "  AutoClick - Instalador Linux"
echo "========================================"
echo ""

# Prefer .deb installation if dpkg-deb is available
if command -v dpkg-deb &> /dev/null && [ -d "$DIR/packaging/autoclick" ]; then
    echo "Modo: Instalação via .deb package"
    echo ""

    # Build the .deb package
    BUILD_DIR="$DIR/dist"
    mkdir -p "$BUILD_DIR"
    PKG_FILE="$BUILD_DIR/autoclick_1.0.0_all.deb"

    echo "[1/2] Construindo pacote .deb..."
    dpkg-deb --build "$DIR/packaging/autoclick" "$PKG_FILE" >/dev/null

    echo "[2/2] Instalando pacote..."
    if [ "$EUID" -ne 0 ]; then
        echo "Reexecutando com sudo para instalação..."
        exec sudo dpkg -i "$PKG_FILE" && sudo apt install -f -y 2>/dev/null || true
    else
        dpkg -i "$PKG_FILE"
        apt install -f -y 2>/dev/null || true
    fi

    echo ""
    echo "========================================"
    echo "  ✅ AutoClick instalado com sucesso!"
    echo "========================================"
    echo ""
    echo "  Execute com:  autoclick"
    echo "  Busque por 'AutoClick' no menu de aplicativos."
    echo "  Atalhos: F9=Gravar F10=Parar F11=Reproduzir F12=Tudo Parar"
    echo ""
    echo "  Para remover: sudo apt remove autoclick"
    echo "========================================"
    exit 0
fi

# Fallback: direct installation
INSTALL_DIR="/opt/autoclick"
DESKTOP_FILE="/usr/share/applications/autoclick.desktop"
ICON_DIR="/usr/share/icons/hicolor/scalable/apps"
BIN_LINK="/usr/local/bin/autoclick"

if [ "$EUID" -ne 0 ]; then
  echo "Este instalador precisa de permissões de superusuário (sudo)."
  echo "Reexecutando com sudo..."
  exec sudo "$0" "$@"
  exit
fi

echo "Modo: Instalação direta em $INSTALL_DIR"
echo ""

echo "[1/5] Criando diretório de instalação..."
mkdir -p "$INSTALL_DIR"
cp -r "$DIR/autoclick" "$INSTALL_DIR/"
cp "$DIR/main.py" "$INSTALL_DIR/"
cp "$DIR/requirements.txt" "$INSTALL_DIR/"
cp "$DIR/autoclick.sh" "$INSTALL_DIR/"

echo "[2/5] Instalando dependências Python..."
if command -v python3 &> /dev/null; then
  python3 -m venv "$INSTALL_DIR/venv" 2>/dev/null || true
  "$INSTALL_DIR/venv/bin/pip" install PySide6 pynput --quiet 2>/dev/null || true
fi

chmod +x "$INSTALL_DIR/autoclick.sh"
ln -sf "$INSTALL_DIR/autoclick.sh" "$BIN_LINK"

if [ -f "$DIR/autoclick.svg" ]; then
  echo "[3/5] Instalando ícone..."
  mkdir -p "$ICON_DIR"
  cp "$DIR/autoclick.svg" "$ICON_DIR/autoclick.svg"
  gtk-update-icon-cache -f -t /usr/share/icons/hicolor/ 2>/dev/null || true
fi

echo "[4/5] Instalando atalho no menu..."
cp "$DIR/autoclick.desktop" "$DESKTOP_FILE"
chmod 644 "$DESKTOP_FILE"

echo "[5/5] Atualizando cache..."
update-desktop-database 2>/dev/null || true

echo ""
echo "========================================"
echo "  ✅ AutoClick instalado com sucesso!"
echo "========================================"
echo ""
echo "  Use:  autoclick"
echo "  Ou busque por 'AutoClick' no menu."
echo "  Atalhos: F9=Gravar F10=Parar F11=Reproduzir F12=Tudo Parar"
echo ""
echo "  Remover: sudo rm -rf $INSTALL_DIR $DESKTOP_FILE $BIN_LINK"
echo "========================================"
