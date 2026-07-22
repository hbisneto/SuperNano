#!/bin/bash
# ================================================================================
# SuperNanno — Smart Setup Script [DEV.SH]
# ================================================================================
# Supports both local and PyPI installation via pipx.
# ================================================================================
set -euo pipefail
clear

# ======================================== FUNCTIONS ========================================
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
        echo
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

install_complete(){
    clear
    show_header
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
    echo "$UI_SEP"
    echo ""
    echo "$UI_SEP"
    echo "[SUPERNANNO]: ABOUT"
    echo "$UI_SEP"
    supernanno --version
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

install_supernanno_dev(){
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
            remove_old_installation
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
            remove_old_installation
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
            remove_old_installation
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
            remove_old_installation
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
            remove_old_installation
            pipx install \
                --pip-args="--index-url https://test.pypi.org/simple/ --extra-index-url https://pypi.org/simple" \
                "$PACKAGE_NAME==$version"
            echo "$UI_SEP"
            echo "✅ Installed version $version from TestPyPI."
            echo "$UI_SEP" ;; 
        *)
            echo "$UI_SEP"
            echo "❌ Invalid option. Quitting..."
            echo "$UI_SEP"
            exit 1 ;;
    esac
}

show_header() {
    echo "$UI_SEP"
    echo "SUPERNANNO SETUP | v${INSTALLER_VERSION} | [DEV.SH]"
    echo "For development and testing purposes."
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

remove_old_installation(){
    # Remove previous installation if exists
    echo ""
    echo "$UI_SEP"
    pipx uninstall "$PACKAGE_NAME" 2>/dev/null || true
    echo "$UI_SEP"
}

run_supernanno(){
    # Optional: Run now?
    echo "$UI_SEP"
    read -p "[SUPERNANNO]: Would you like to run SuperNanno now? (y/N): " -r run_now
    echo "$UI_SEP"
    if [[ "$run_now" =~ ^[Yy]$ ]]; then
        clear
        show_header
        echo "$UI_SEP"
        echo "[SUPERNANNO]: STARTING..."
        echo "$UI_SEP"
        supernanno
    fi
}
# ======================================== FUNCTIONS ========================================

# ======================================== VARIABLES ========================================
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
# ======================================== VARIABLES ========================================

# ======================================== MAIN ========================================
show_header
check_pipx
install_supernanno_dev
install_complete
run_supernanno
# ======================================== MAIN ========================================