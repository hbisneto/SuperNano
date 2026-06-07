#!/bin/bash
# =============================================================================
# SuperNanno — Install Script [INSTALL.SH]
# =============================================================================
# Installs SuperNanno (stable version) via pipx with user confirmation.
# =============================================================================
set -euo pipefail
clear

# =================================== Variables ===================================
OS_TYPE=$(uname -s)
USERNAME="$USER"
USERNAME_FORMATTED="$(echo "${USERNAME:0:1}" | tr '[:lower:]' '[:upper:]')$(echo "${USERNAME:1}" | tr '[:upper:]' '[:lower:]')"
UI_SEP=$(printf '%*s' "$(tput cols)" '' | tr ' ' '=')
BASE_DIR=$(pwd)
DATE_HOUR=$(date +"%Y-%m-%d %H:%M:%S")
PACKAGE_NAME="supernanno"

# =================================== Functions ===================================
print_header() {
    echo "$UI_SEP"
    echo "SUPERNANNO INSTALLER | v0.0.23 | [INSTALL.SH]"
    echo "For user installation of the stable version."
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
echo "[SUPERNANNO]: This script will install the stable version of SuperNanno via pipx."
echo "$UI_SEP"
read -p "[USER]: Do you want to continue with the installation? [Y/n]: " -r confirm
echo "$UI_SEP"

# More compatible lowercase conversion
confirm_lower=$(echo "$confirm" | tr '[:upper:]' '[:lower:]')

if [[ -n "$confirm" ]] && [[ ! "$confirm_lower" =~ ^(y|yes)$ ]]; then
    echo "$UI_SEP"
    echo "❌ [CANCELLED]: Installation cancelled by the user."
    echo "$UI_SEP"
    exit 0
fi

echo "📦 [INSTALL]: Installing latest SuperNanno version..."
echo "🔄 [INSTALL]: Please wait, this may take a few seconds..."
echo "$UI_SEP"

# Remove previous installation if exists
echo ""
echo "$UI_SEP"
pipx uninstall "$PACKAGE_NAME" 2>/dev/null || true
echo "$UI_SEP"

# Install stable version
echo ""
echo "$UI_SEP"
pipx install "$PACKAGE_NAME"
echo "$UI_SEP"

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