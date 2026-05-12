#!/bin/bash
# rites/summon.sh
# Grimoire Summoning Rite — Bootstrap (Linux/Mac)
#
# Ensures Python 3 is available, optionally prepares GUI dependencies,
# then launches the cross-platform summoning script.
#
# One-liner entry point:
#   curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | bash

set -euo pipefail

DEFAULT_ARCANA_URL="https://github.com/justinlavi/arcana.git"
DEFAULT_ARCANA_REF="main"

: "${GRIMOIRE_ARCANA_URL:=$DEFAULT_ARCANA_URL}"
: "${GRIMOIRE_ARCANA_REF:=$DEFAULT_ARCANA_REF}"
: "${GRIMOIRE_SUMMON_PY_DEPS:=${XDG_CACHE_HOME:-$HOME/.cache}/grimoire/summon-python}"
export GRIMOIRE_ARCANA_URL
export GRIMOIRE_SUMMON_PY_DEPS

TEMP_DIR=""
SCRIPT_SOURCE="${BASH_SOURCE[0]:-$0}"

derive_raw_base() {
    local repo_url="$1"
    local ref="$2"

    if [[ "$repo_url" =~ ^https://github.com/([^/]+)/([^/.]+)(\.git)?$ ]]; then
        echo "https://raw.githubusercontent.com/${BASH_REMATCH[1]}/${BASH_REMATCH[2]}/$ref"
    else
        echo "https://raw.githubusercontent.com/justinlavi/arcana/$ref"
    fi
}

: "${GRIMOIRE_ARCANA_RAW_BASE:=$(derive_raw_base "$GRIMOIRE_ARCANA_URL" "$GRIMOIRE_ARCANA_REF")}"

download_file() {
    local url="$1"
    local dest="$2"

    if command -v curl &>/dev/null; then
        curl -fsSL "$url" -o "$dest"
    elif command -v wget &>/dev/null; then
        wget -qO "$dest" "$url"
    else
        echo "  [ERROR] curl or wget is required to run the summoning rite from a pipe"
        return 1
    fi
}

if [[ -f "$SCRIPT_SOURCE" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_SOURCE")" && pwd)"
else
    TEMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/grimoire-summon.XXXXXX")"
    SCRIPT_DIR="$TEMP_DIR/rites"
    mkdir -p "$SCRIPT_DIR"
    echo "  [INFO]  Downloading summoning companion script..."
    download_file "$GRIMOIRE_ARCANA_RAW_BASE/rites/summon.py" "$SCRIPT_DIR/summon.py"
fi

cleanup() {
    if [[ -n "$TEMP_DIR" && -d "$TEMP_DIR" ]]; then
        rm -rf "$TEMP_DIR"
    fi
}
trap cleanup EXIT

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
        pacman) sudo pacman -S --needed --noconfirm "$@" ;;
        brew)   brew install "$@" ;;
        *)      return 1 ;;
    esac
}

pip_install_hint() {
    local mgr="$1"
    case "$mgr" in
        apt)    echo "sudo apt-get install python3-pip" ;;
        dnf)    echo "sudo dnf install python3-pip" ;;
        pacman) echo "sudo pacman -S --needed python-pip" ;;
        brew)   echo "brew install python" ;;
        *)      echo "install pip for $($PYTHON --version 2>&1)" ;;
    esac
}

python_can_import() {
    local module="$1"
    PYTHONPATH="$GRIMOIRE_SUMMON_PY_DEPS${PYTHONPATH:+:$PYTHONPATH}" \
        "$PYTHON" -c "import $module" 2>/dev/null
}

should_prepare_gui_deps() {
    local arg
    for arg in "$@"; do
        case "$arg" in
            --cli|-h|--help) return 1 ;;
        esac
    done
    return 0
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
        apt)    install_packages "$PKG_MGR" python3 python3-pip ;;
        dnf)    install_packages "$PKG_MGR" python3 python3-pip ;;
        pacman) install_packages "$PKG_MGR" python python-pip ;;
        brew)   install_packages "$PKG_MGR" python3 ;;
    esac

    if ! PYTHON=$(find_python); then
        echo "  [ERROR] Python 3 installation failed. Install manually and re-run."
        exit 1
    fi
    echo "  [OK]    Python 3 installed: $($PYTHON --version 2>&1)"
fi

echo "  [OK]    Using $($PYTHON --version 2>&1)"

# ---------------------------------------------------------------------------
# 2. Ensure app dependencies are available when app mode is possible
# ---------------------------------------------------------------------------

if should_prepare_gui_deps "$@"; then
    if ! "$PYTHON" -m pip --version &>/dev/null; then
        echo "  [INFO]  pip not found — attempting to install..."
        PKG_MGR=$(detect_pkg_manager)
        case "$PKG_MGR" in
            apt) install_packages "$PKG_MGR" python3-pip 2>/dev/null || true ;;
            dnf) install_packages "$PKG_MGR" python3-pip 2>/dev/null || true ;;
            pacman) install_packages "$PKG_MGR" python-pip 2>/dev/null || true ;;
            brew) install_packages "$PKG_MGR" python 2>/dev/null || true ;;
        esac
        if ! "$PYTHON" -m pip --version &>/dev/null; then
            "$PYTHON" -m ensurepip --default-pip 2>/dev/null || true
        fi
        if "$PYTHON" -m pip --version &>/dev/null; then
            echo "  [OK]    pip installed"
        else
            echo "  [WARN]  pip not available — Dear PyGui auto-install may fail"
            echo "  [INFO]  To enable app mode manually, run: $(pip_install_hint "$PKG_MGR")"
        fi
    fi

    if ! python_can_import "dearpygui.dearpygui"; then
        echo "  [INFO]  Dear PyGui not found — installing via pip..."
        if "$PYTHON" -m pip --version &>/dev/null; then
            mkdir -p "$GRIMOIRE_SUMMON_PY_DEPS"
            if "$PYTHON" -m pip install --upgrade --target "$GRIMOIRE_SUMMON_PY_DEPS" dearpygui 2>/dev/null; then
                echo "  [OK]    Dear PyGui installed"
            else
                echo "  [WARN]  Could not install Dear PyGui — GUI may fall back to CLI"
            fi
        else
            echo "  [WARN]  pip unavailable — GUI may fall back to CLI"
        fi
    else
        echo "  [OK]    Dear PyGui available"
    fi
else
    echo "  [INFO]  Skipping app dependencies for CLI/help mode"
fi

export PYTHONPATH="$GRIMOIRE_SUMMON_PY_DEPS${PYTHONPATH:+:$PYTHONPATH}"

# ---------------------------------------------------------------------------
# 4. Wayland: prefer XWayland if no DISPLAY is set
# ---------------------------------------------------------------------------

if [[ -z "${DISPLAY:-}" ]]; then
    if [[ -n "${WAYLAND_DISPLAY:-}" || "${XDG_SESSION_TYPE:-}" == "wayland" ]]; then
        export DISPLAY=":0"
        echo "  [INFO]  Wayland session detected — set DISPLAY=:0 for GUI rendering"
    fi
fi

echo ""
exec "$PYTHON" "$SCRIPT_DIR/summon.py" "$@"
