#!/bin/bash

# =============================================================================
# SuperNanno — Smart Setup Script [DEV.SH]
# =============================================================================
# Suporta instalação via pipx tanto da versão local quanto do PyPI.
# =============================================================================
set -euo pipefail
clear

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
    echo "SUPERNANNO SETUP | v0.0.23 | [DEV.SH]"
    echo "For development and testing purposes."
    echo "$UI_SEP"
    echo "User     : $USERNAME_FORMATTED"
    echo "Date     : $DATE_HOUR"
    echo "OS       : $OS_TYPE"
    echo "Directory: $BASE_DIR"
    echo "$UI_SEP"
    echo ""
}

install_pipx() {
    echo "$UI_SEP"
    echo "❌ [PIPX]: pipx is not installed."
    echo "$UI_SEP"
    read -p "[USER]: Do you want to install pipx now? [Y/n]: " -r install_pipx_choice
    echo "$UI_SEP"
    
    # More compatible lowercase
    choice_lower=$(echo "$install_pipx_choice" | tr '[:upper:]' '[:lower:]')
    
    if [[ -z "$install_pipx_choice" ]] || [[ "$choice_lower" =~ ^(y|yes)$ ]]; then
        echo "📦 [PIPX]: Installing pipx... ⏳"
        python3 -m pip install --user pipx
        python3 -m pipx ensurepath
        
        if [[ -f "$HOME/.local/bin/pipx" ]]; then
            export PATH="$HOME/.local/bin:$PATH"
        fi
        echo ""
        echo "$UI_SEP"
        echo "✅ [PIPX]: pipx installed successfully!"
        echo "$UI_SEP"
    else
        echo ""
        echo "$UI_SEP"
        echo "❌ [CANCELLED]: Installation cancelled. pipx is required."
        echo "$UI_SEP"
        exit 1
    fi
}

check_pipx() {
    if ! command -v pipx &> /dev/null; then
        install_pipx
    else
        echo "$UI_SEP"
        echo "✅ [PIPX]: pipx is installed."
        echo "$UI_SEP"
    fi
}

# =================================== Main ===================================

print_header
check_pipx
echo ""
echo "$UI_SEP"
echo "How would you like to install SuperNanno?"
echo "$UI_SEP"
echo "1) Stable Channel                     : [RECOMMENDED]"
echo "2) Specific Stable Version            : [STABLE_V_0.0.23]"
echo "3) Local Developer Mode               : [EDITABLE]"
echo "4) Dev Channel                        : [DEV]"
echo "5) Specific Dev Version               : [DEV_0.0.0.23]"
echo "$UI_SEP"
read -p "Choose an option [1-5]: " -r choice
echo "$UI_SEP"
echo ""

case "$choice" in
    # NORMAL INSTALLATIONS
    1)
        echo "$UI_SEP"
        echo "📦 Installing latest version from PyPI..."
        echo "$UI_SEP"
        pipx uninstall "$PACKAGE_NAME" 2>/dev/null || true
        echo "$UI_SEP"
        pipx install "$PACKAGE_NAME"
        echo "$UI_SEP"
        echo "✅ Installed latest version from PyPI."
        echo "$UI_SEP"
        ;;
    
    # PYPI INSTALLATIONS
    2)
        echo "$UI_SEP"
        read -p "Enter version (ex: 0.0.23): " -r version
        echo "$UI_SEP"
        echo "📦 Installing version $version from PyPI..."
        echo "$UI_SEP"
        pipx uninstall "$PACKAGE_NAME" 2>/dev/null || true
        echo "$UI_SEP"
        pipx install "$PACKAGE_NAME==$version"
        echo "$UI_SEP"
        echo "✅ Installed version $version from PyPI."
        echo "$UI_SEP"
        ;;
    
    # DEVELOPMENT INSTALLATION
    3)
        echo "$UI_SEP"
        echo "⚙️  Installing in LOCAL DEVELOPMENT mode (editable)..."
        echo "$UI_SEP"
        pipx uninstall "$PACKAGE_NAME" 2>/dev/null || true
        echo "$UI_SEP"
        pipx install --editable .
        echo "$UI_SEP"
        echo "✅ Installed in editable mode from local source."
        echo "$UI_SEP"
        ;;

    # TESTPYPI INSTALLATIONS
    4)
        echo "$UI_SEP"
        echo "📦 Installing latest version from TestPyPI..."
        echo "$UI_SEP"
        pipx uninstall "$PACKAGE_NAME" 2>/dev/null || true
        echo "$UI_SEP"

        pipx install \
            --pip-args="--index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple" \
            "$PACKAGE_NAME"
        echo "$UI_SEP"
        echo "✅ Installed latest version from TestPyPI."
        echo "$UI_SEP"
        ;;

    # TESTPYPI INSTALLATIONS
    5)
        echo "$UI_SEP"
        read -p "Enter version (ex: 0.0.23): " -r version
        echo "$UI_SEP"
        echo "📦 Installing version $version from TestPyPI..."
        echo "$UI_SEP"
        pipx uninstall "$PACKAGE_NAME" 2>/dev/null || true
        echo "$UI_SEP"
        pipx install \
            --pip-args="--index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple" \
            "$PACKAGE_NAME==$version"
        echo "$UI_SEP"
        echo "✅ Installed version $version from TestPyPI."
        echo "$UI_SEP"
        ;; 
    *)
        echo ""
        echo ""
        echo "$UI_SEP"
        echo "❌ Invalid option. Exiting..."
        echo "$UI_SEP"
        exit 1
        ;;
esac

echo ""
clear
print_header
echo "$UI_SEP"
echo "[SUPERNANNO]: SETUP COMPLETED SUCCESSFULLY!"
echo "$UI_SEP"
echo "You can now run SuperNanno with:"
echo "   supernanno"
echo ""
echo "Useful commands:"
echo "   supernanno --help"
echo "   supernanno --version"
echo "   supernanno my_file.py"
echo ""
# Show configuration path
echo "📁 Configuration directory:"
echo ""
echo "Linux: ~/.config/Bisneto/SuperNanno/"
echo "macOS: ~/Library/Application Support/Bisneto/SuperNanno/"
echo "Windows: %APPDATA%\Bisneto\SuperNanno"
echo ""
echo ""
supernanno --version
echo ""

# Optional: Run now?
echo "$UI_SEP"
read -p "[SUPERNANNO]: Would you like to run SuperNanno now? (y/N): " -r run_now
echo "$UI_SEP"
if [[ "$run_now" =~ ^[Yy]$ ]]; then
    echo "$UI_SEP"
    echo "[SUPERNANNO]: Starting..."
    echo "$UI_SEP"
    supernanno
fi