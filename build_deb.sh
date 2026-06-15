#!/bin/bash
# AutoClick - .deb package builder
# Builds a Debian package and optionally installs it

set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PACKAGE_DIR="$DIR/packaging/autoclick"
OUTPUT_DIR="$DIR/dist"
PKG_NAME="autoclick_1.0.0_all.deb"

echo "========================================"
echo "  AutoClick - .deb Package Builder"
echo "========================================"
echo ""

# Ensure dependencies are met
if ! command -v dpkg-deb &> /dev/null; then
    echo "ERRO: dpkg-deb não encontrado. Instale dpkg-dev."
    echo "  sudo apt install dpkg-dev"
    exit 1
fi

# Verify package structure
if [ ! -d "$PACKAGE_DIR/DEBIAN" ]; then
    echo "ERRO: Estrutura DEBIAN não encontrada em $PACKAGE_DIR"
    exit 1
fi

# Set permissions
chmod 755 "$PACKAGE_DIR/DEBIAN/postinst" 2>/dev/null || true
chmod 755 "$PACKAGE_DIR/DEBIAN/prerm" 2>/dev/null || true

# Build the package
echo "[1/2] Building package..."
mkdir -p "$OUTPUT_DIR"
dpkg-deb --build "$PACKAGE_DIR" "$OUTPUT_DIR/$PKG_NAME"

echo "[2/2] Package built successfully!"
echo ""
echo "========================================"
echo "  📦 $OUTPUT_DIR/$PKG_NAME"
echo "========================================"
echo ""
echo "  Install with:  sudo dpkg -i $OUTPUT_DIR/$PKG_NAME"
echo "  Then run:       autoclick"
echo "  Remove with:    sudo apt remove autoclick"
echo ""

# Ask if user wants to install
read -p "Instalar agora? (s/N): " answer
if [ "$answer" = "s" ] || [ "$answer" = "S" ]; then
    echo ""
    echo "Instalando..."
    sudo dpkg -i "$OUTPUT_DIR/$PKG_NAME"
    sudo apt install -f -y 2>/dev/null || true
    echo ""
    echo "✅ AutoClick instalado! Execute com: autoclick"
fi
