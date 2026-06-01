#!/bin/bash

# =============================================================================
# SuperNanno — Smart Setup Script
# =============================================================================
# Suporta instalação via pipx tanto da versão local quanto do PyPI.

set -euo pipefail

# =================================== Variables ===================================

OS_TYPE=$(uname)
USERNAME="$USER"
USERNAME_FORMATTED="$(echo "${USERNAME:0:1}" | tr '[:lower:]' '[:upper:]')$(echo "${USERNAME:1}" | tr '[:upper:]' '[:lower:]')"
UI_SEP=$(printf '%*s' "$(tput cols)" '' | tr ' ' '=')
BASE_DIR=$(pwd)
DATE_HOUR=$(date +"%Y-%m-%d %H:%M:%S")
PACKAGE_NAME="supernanno"

# =================================== Functions ===================================

print_header() {
    echo "$UI_SEP"
    echo "🚀 SUPERNANNO SETUP v0.0.23"
    echo "$UI_SEP"
    echo "User     : $USERNAME_FORMATTED"
    echo "Date     : $DATE_HOUR"
    echo "OS       : $OS_TYPE"
    echo "Directory: $BASE_DIR"
    echo "$UI_SEP"
    echo ""
}

check_pipx() {
    if ! command -v pipx &> /dev/null; then
        echo "❌ pipx is not installed."
        echo ""
        echo "Install it with:"
        echo "   python3 -m pip install --user pipx"
        echo "   python3 -m pipx ensurepath"
        echo ""
        exit 1
    fi
    echo "✅ pipx is available"
}

# =================================== Main ===================================

print_header
check_pipx
echo ""

echo "How would you like to install SuperNanno?"
echo ""
echo "1) Stable Channel          ← Recommended"
echo "2) Local Developer Mode          ← editable"
echo "3) Dev Channel"
echo "4) Specific Dev Version"
echo "5) Specific Stable Version"
echo ""
read -p "Choose an option [1-5]: " -r choice

echo ""

case "$choice" in
    # NORMAL INSTALLATIONS
    1)
        echo "📦 Installing latest version from PyPI..."
        pipx uninstall "$PACKAGE_NAME" 2>/dev/null || true
        pipx install "$PACKAGE_NAME"
        echo "✅ Installed latest version from PyPI."
        ;;
    
    # DEVELOPMENT INSTALLATION
    2)
        echo "⚙️  Installing in LOCAL DEVELOPMENT mode (editable)..."
        pipx uninstall "$PACKAGE_NAME" 2>/dev/null || true
        pipx install --editable .
        echo "✅ Installed in editable mode from local source."
        ;;

    # TESTPYPI INSTALLATIONS
    3)
        echo "📦 Installing latest version from TestPyPI..."
        pipx uninstall "$PACKAGE_NAME" 2>/dev/null || true

        pipx install \
            --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple \
            "$PACKAGE_NAME"

        echo "✅ Installed latest version from TestPyPI."
        ;;

    # PYPI INSTALLATIONS
    4)
        read -p "Enter version (ex: 0.0.23): " -r version

        echo "📦 Installing version $version from TestPyPI..."
        pipx uninstall "$PACKAGE_NAME" 2>/dev/null || true

        pipx install \
            --index-url https://test.pypi.org/simple/ \
            --extra-index-url https://pypi.org/simple \
            "$PACKAGE_NAME==$version"

        echo "✅ Installed version $version from TestPyPI."
        ;; 

    5)
        read -p "Enter version (ex: 0.0.23): " -r version
        echo "📦 Installing version $version from PyPI..."
        pipx uninstall "$PACKAGE_NAME" 2>/dev/null || true
        pipx install "$PACKAGE_NAME==$version"
        echo "✅ Installed version $version from PyPI."
        ;;
    
    *)
        echo "❌ Invalid option. Exiting..."
        exit 1
        ;;
esac

echo ""
echo "$UI_SEP"
echo "🎉 SETUP COMPLETED SUCCESSFULLY!"
echo "$UI_SEP"
echo ""

echo "You can now run SuperNanno with:"
echo "   supernanno"
echo ""
echo "Useful commands:"
echo "   supernanno --help"
echo "   supernanno --version"
echo "   supernanno meu_arquivo.py"
echo ""

# Show configuration path
echo "📁 Configuration directory:"
echo "   ~/.config/Bisneto/SuperNanno/"
echo ""

# Optional: Run now?
read -p "Run SuperNanno now? (y/N): " -r run_now
if [[ "$run_now" =~ ^[Yy]$ ]]; then
    echo ""
    echo "Launching SuperNanno..."
    supernanno
fi