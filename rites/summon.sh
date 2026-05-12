#!/bin/bash
# rites/summon.sh
# Grimoire Summoning Rite — Bootstrap (Linux/Mac)
#
# Ensures Python 3, tkinter, and customtkinter are installed,
# then launches the cross-platform summoning script.
#
# One-liner entry point (substitute your Arcana URL):
#   rm -rf /tmp/grimoire-summon && git clone --depth 1 <your-arcana-url> /tmp/grimoire-summon && bash /tmp/grimoire-summon/rites/summon.sh

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

find_python() {
    if command -v python3 &>/dev/null; then
        echo "python3"
        return 0
    elif command -v python &>/dev/null; then
        if python -c "import sys; sys.exit(0 if sys.version_info >= (3, 7) else 1)" 2>/dev/null; then
            echo "python"
            return 0
        fi
    fi
    return 1
}

detect_pkg_manager() {
    if command -v apt-get &>/dev/null; then echo "apt"
    elif command -v dnf &>/dev/null; then echo "dnf"
    elif command -v pacman &>/dev/null; then echo "pacman"
    elif command -v brew &>/dev/null; then echo "brew"
    else echo ""; fi
}

install_packages() {
    local mgr="$1"; shift
    case "$mgr" in
        apt)    sudo apt-get update -qq && sudo apt-get install -y "$@" ;;
        dnf)    sudo dnf install -y "$@" ;;
        pacman) sudo pacman -S --noconfirm "$@" ;;
        brew)   brew install "$@" ;;
        *)      return 1 ;;
    esac
}

# ---------------------------------------------------------------------------
# 1. Find or install Python 3
# ---------------------------------------------------------------------------

PYTHON=""
if ! PYTHON=$(find_python); then
    echo ""
    echo "  Python 3 is required but not found."
    echo ""

    PKG_MGR=$(detect_pkg_manager)
    if [[ -z "$PKG_MGR" ]]; then
        echo "  Could not detect package manager. Install Python 3 manually and re-run."
        exit 1
    fi

    read -r -p "  Install Python 3 now? (requires sudo) [y/N]: " response
    if [[ "${response,,}" != "y" ]]; then
        echo "  Install Python 3 manually and re-run."
        exit 1
    fi

    case "$PKG_MGR" in
        apt)    install_packages "$PKG_MGR" python3 python3-tk python3-pip ;;
        dnf)    install_packages "$PKG_MGR" python3 python3-tkinter python3-pip ;;
        pacman) install_packages "$PKG_MGR" python python-tk python-pip ;;
        brew)   install_packages "$PKG_MGR" python3 python-tk ;;
    esac

    if ! PYTHON=$(find_python); then
        echo "  [ERROR] Python 3 installation failed. Install manually and re-run."
        exit 1
    fi
    echo "  [OK]    Python 3 installed: $($PYTHON --version 2>&1)"
fi

echo "  [OK]    Using $($PYTHON --version 2>&1)"

# ---------------------------------------------------------------------------
# 2. Ensure tkinter is available (system package)
# ---------------------------------------------------------------------------

if ! "$PYTHON" -c "import tkinter" 2>/dev/null; then
    echo "  [INFO]  tkinter not found — attempting to install..."
    PKG_MGR=$(detect_pkg_manager)
    case "$PKG_MGR" in
        apt)    install_packages "$PKG_MGR" python3-tk 2>/dev/null ;;
        dnf)    install_packages "$PKG_MGR" python3-tkinter 2>/dev/null ;;
        pacman) install_packages "$PKG_MGR" python-tk 2>/dev/null ;;
        brew)   install_packages "$PKG_MGR" python-tk 2>/dev/null ;;
    esac

    if "$PYTHON" -c "import tkinter" 2>/dev/null; then
        echo "  [OK]    tkinter installed"
    else
        echo "  [WARN]  Could not install tkinter — GUI mode will not be available"
    fi
else
    echo "  [OK]    tkinter available"
fi

# ---------------------------------------------------------------------------
# 3. Ensure pip is available
# ---------------------------------------------------------------------------

if ! "$PYTHON" -m pip --version &>/dev/null; then
    echo "  [INFO]  pip not found — attempting to install..."
    PKG_MGR=$(detect_pkg_manager)
    case "$PKG_MGR" in
        apt) install_packages "$PKG_MGR" python3-pip 2>/dev/null ;;
        dnf) install_packages "$PKG_MGR" python3-pip 2>/dev/null ;;
    esac
    if ! "$PYTHON" -m pip --version &>/dev/null; then
        "$PYTHON" -m ensurepip --default-pip 2>/dev/null || true
    fi
    if "$PYTHON" -m pip --version &>/dev/null; then
        echo "  [OK]    pip installed"
    else
        echo "  [WARN]  pip not available — customtkinter auto-install may fail"
    fi
fi

# ---------------------------------------------------------------------------
# 4. Ensure customtkinter is available (pip package)
# ---------------------------------------------------------------------------

if "$PYTHON" -c "import tkinter" 2>/dev/null; then
    if ! "$PYTHON" -c "import customtkinter" 2>/dev/null; then
        echo "  [INFO]  customtkinter not found — installing via pip..."
        if "$PYTHON" -m pip install --user customtkinter 2>/dev/null || \
           "$PYTHON" -m pip install customtkinter 2>/dev/null; then
            echo "  [OK]    customtkinter installed"
        else
            echo "  [WARN]  Could not install customtkinter — GUI may fall back to CLI"
        fi
    else
        echo "  [OK]    customtkinter available"
    fi
fi

# ---------------------------------------------------------------------------
# 5. Wayland: ensure DISPLAY is set for tkinter (needs XWayland)
# ---------------------------------------------------------------------------

if [[ -z "${DISPLAY:-}" ]]; then
    if [[ -n "${WAYLAND_DISPLAY:-}" || "${XDG_SESSION_TYPE:-}" == "wayland" ]]; then
        export DISPLAY=":0"
        echo "  [INFO]  Wayland session detected — set DISPLAY=:0 for XWayland"
    fi
fi

echo ""
exec "$PYTHON" "$SCRIPT_DIR/summon.py" "$@"
