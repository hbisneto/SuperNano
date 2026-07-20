#!/bin/bash
# ================================================================================
# SuperNanno — Install Script [INSTALL.SH]
# ================================================================================
# Installs SuperNanno (stable version) via pipx with user confirmation.
# ================================================================================

# Steps until finished:
# 1. Check for pipx installation.
# 2. If pipx is not installed, prompt the user to install it.
# 3. If pipx is installed, proceed to install SuperNanno.
# 4. After installation, provide instructions to run SuperNanno.


set -euo pipefail
clear

# ======================================== Functions ========================================
check_environment(){
    case "$OS_TYPE" in
        Linux)
            if [[ "$PYTHON_PATH" == *linuxbrew* ]]; then
                echo "$UI_SEP"
                echo "[Python]: Unsupported installation detected."
                echo "$UI_SEP"
                echo "SuperNanno's installer expects the operating system's default Python installation."
                echo "Detected: $PYTHON_PATH"
                echo
                echo "This appears to be a Homebrew-managed Python installation, which is not supported by this installer."
                echo "Please install or use the system Python instead."
                echo
                echo ">> Please install the system Python using your distribution's package manager."
                echo "$UI_SEP"
                exit 1
            fi ;;
    esac
}

check_pipx() {
    if ! command -v pipx &> /dev/null; then
        install_pipx
        ## AFTER INSTALL, RESTART SHELL INSTRUCTION
        if [[ -n "$RC_FILE" ]]; then
            clear
            echo "$UI_SEP"
            echo "[RELOAD SESSION]:"
            echo "To apply changes, please reload your shell session."
            echo "$UI_SEP"
            echo "Run:"
            echo "    source \"$RC_FILE\""
            echo
            echo "Or simply restart your terminal."
            echo "$UI_SEP"
            exit 0
        fi
    else
        echo "$UI_SEP"
        echo "✅ [PIPX]: pipx is installed."
        echo "$UI_SEP"
    fi

}

detect_rc_file() {
    case "$(detect_shell)" in
        bash|git-bash)
            echo "$HOME/.bashrc";;
        zsh)
            echo "$HOME/.zshrc";;
        fish)
            echo "$HOME/.config/fish/config.fish";;
        *)
            echo "";;
    esac
}

detect_shell() {    
    # Detects the user's current shell/environment.
    local shell_name=""
    local shell_path="${SHELL:-}"

    # 1. Detect by $SHELL
    if [[ -n "$shell_path" ]]; then
        shell_name="$(basename "$shell_path")"
    fi

    # 2. Fallback: detect current process
    if [[ -z "$shell_name" ]]; then
        shell_name="$(ps -p $$ -o comm= 2>/dev/null | xargs basename)"
    fi

    # 3. Windows compatibility layers
    if [[ -n "${MSYSTEM:-}" ]]; then
        echo "git-bash"
        return
    fi

    if [[ -n "${WSL_DISTRO_NAME:-}" ]]; then
        echo "wsl"
        return
    fi

    if [[ -n "${CYGWIN:-}" ]]; then
        echo "cygwin"
        return
    fi

    case "$shell_name" in
        bash)
            echo "bash";;
        zsh)
            echo "zsh";;
        fish)
            echo "fish";;
        dash)
            echo "dash";;
        sh)
            echo "sh";;
        ksh)
            echo "ksh";;
        tcsh)
            echo "tcsh";;
        csh)
            echo "csh";;
        pwsh)
            echo "powershell";;
        powershell)
            echo "powershell";;
        cmd.exe)
            echo "cmd";;
        *)
            echo "unknown";;
    esac
}

install_pipx() {
    echo "$UI_SEP"
    echo "❌ [PIPX]: pipx is not installed."
    echo "$UI_SEP"
    read -p "[USER]: Do you want to install pipx now? [Y/n]: " -r install_pipx_choice
    echo "$UI_SEP"

    PYTHON_PATH=$(python3 -c 'import sys; print(sys.executable)')
    
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

print_header() {
    echo "$UI_SEP"
    echo "SUPERNANNO INSTALLER | v${INSTALLER_VERSION} | [INSTALL.SH]"
    echo "For user installation of the stable version."
    echo "$UI_SEP"
    echo "User           : $USERNAME_FORMATTED"
    echo "OS             : $OS_TYPE"
    echo "Shell          : $CURRENT_SHELL"
    echo "Shell Location : ${RC_FILE}"
    echo "Date           : $DATE_HOUR"
    echo "Directory      : $BASE_DIR"
    echo "$UI_SEP"
    echo ""
}
# ======================================== Functions ========================================

# ======================================== Variables ========================================
INSTALLER_VERSION="0.1.32"
OS_TYPE=$(uname -s)
USERNAME="$USER"
USERNAME_FORMATTED="$(echo "${USERNAME:0:1}" | tr '[:lower:]' '[:upper:]')$(echo "${USERNAME:1}" | tr '[:upper:]' '[:lower:]')"
UI_SEP=$(printf '%*s' "$(tput cols)" '' | tr ' ' '=')
BASE_DIR=$(pwd)
DATE_HOUR=$(date +"%Y-%m-%d %H:%M:%S")
PACKAGE_NAME="supernanno"
CURRENT_SHELL="$(detect_shell)"
RC_FILE="$(detect_rc_file)"
PYTHON_PATH=$(python3 -c 'import sys; print(sys.executable)')
# ======================================== Variables ========================================

# ======================================== Main ========================================
print_header
check_environment
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
# ======================================== Main ========================================