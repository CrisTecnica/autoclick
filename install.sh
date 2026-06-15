#!/bin/bash
# AutoClick - Linux Installer
# Instala o AutoClick no sistema e cria atalho no menu de aplicativos

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
INSTALL_DIR="/opt/autoclick"
DESKTOP_FILE="/usr/share/applications/autoclick.desktop"
ICON_DIR="/usr/share/icons/hicolor/scalable/apps"
BIN_LINK="/usr/local/bin/autoclick"

echo "========================================"
echo "  AutoClick - Instalador Linux"
echo "========================================"
echo ""

# Verificar se está rodando como root
if [ "$EUID" -ne 0 ]; then
  echo "Este instalador precisa de permissões de superusuário (sudo)."
  echo "Reexecutando com sudo..."
  exec sudo "$0" "$@"
  exit
fi

echo "[1/5] Criando diretório de instalação em $INSTALL_DIR..."
mkdir -p "$INSTALL_DIR"
cp -r "$DIR/autoclick" "$INSTALL_DIR/"
cp "$DIR/main.py" "$INSTALL_DIR/"
cp "$DIR/requirements.txt" "$INSTALL_DIR/"
cp "$DIR/autoclick.sh" "$INSTALL_DIR/"

echo "[2/5] Instalando dependências Python..."
if command -v python3 &> /dev/null; then
  python3 -m venv "$INSTALL_DIR/venv" 2>/dev/null || true
  "$INSTALL_DIR/venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt" --quiet 2>/dev/null || \
  "$INSTALL_DIR/venv/bin/pip" install PySide6 pynput --quiet
fi

chmod +x "$INSTALL_DIR/autoclick.sh"
ln -sf "$INSTALL_DIR/autoclick.sh" "$BIN_LINK"

if [ -f "$DIR/autoclick.svg" ]; then
  echo "[3/5] Instalando ícone..."
  mkdir -p "$ICON_DIR"
  cp "$DIR/autoclick.svg" "$ICON_DIR/autoclick.svg"
  gtk-update-icon-cache -f -t /usr/share/icons/hicolor/ 2>/dev/null || true
fi

echo "[4/5] Instalando atalho no menu de aplicativos..."
cp "$DIR/autoclick.desktop" "$DESKTOP_FILE"
chmod 644 "$DESKTOP_FILE"

echo "[5/5] Atualizando cache do menu..."
update-desktop-database 2>/dev/null || true

echo ""
echo "========================================"
echo "  ✅ AutoClick instalado com sucesso!"
echo "========================================"
echo ""
echo "  Use o comando:  autoclick"
echo "  Ou busque por 'AutoClick' no menu de aplicativos."
echo "  Atalhos globais: F9=Gravar F10=Parar F11=Reproduzir F12=Tudo Parar"
echo ""
echo "  Para desinstalar: sudo rm -rf $INSTALL_DIR $DESKTOP_FILE $BIN_LINK"
echo "========================================"
