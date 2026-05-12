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
: "${GRIMOIRE_SUMMON_BINARY:=auto}"
: "${GRIMOIRE_SUMMON_RELEASE_TAG:=latest}"
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

repo_http_base() {
    local repo_url="$1"

    if [[ "$repo_url" =~ ^https://github.com/([^/]+)/([^/.]+)(\.git)?$ ]]; then
        echo "https://github.com/${BASH_REMATCH[1]}/${BASH_REMATCH[2]}"
    else
        echo "https://github.com/justinlavi/arcana"
    fi
}

summon_platform() {
    local os
    local arch

    os="$(uname -s | tr '[:upper:]' '[:lower:]')"
    arch="$(uname -m | tr '[:upper:]' '[:lower:]')"

    case "$os" in
        linux) os="linux" ;;
        darwin) os="macos" ;;
        *) return 1 ;;
    esac

    case "$arch" in
        x86_64|amd64) arch="x86_64" ;;
        aarch64|arm64) arch="arm64" ;;
        *) return 1 ;;
    esac

    echo "$os-$arch"
}

release_download_base() {
    local repo_base="$1"
    local tag="$2"

    if [[ "$tag" == "latest" ]]; then
        echo "$repo_base/releases/latest/download"
    else
        echo "$repo_base/releases/download/$tag"
    fi
}

verify_checksum() {
    local checksum="$1"

    if command -v sha256sum &>/dev/null; then
        sha256sum -c "$checksum"
    elif command -v shasum &>/dev/null; then
        shasum -a 256 -c "$checksum"
    else
        echo "  [WARN]  sha256sum/shasum not found — skipping checksum verification"
        return 0
    fi
}

should_try_binary() {
    if [[ "$GRIMOIRE_SUMMON_BINARY" == "never" ]]; then
        return 1
    fi
    if [[ "$GRIMOIRE_SUMMON_BINARY" == "always" ]]; then
        return 0
    fi
    [[ ! -f "$SCRIPT_SOURCE" ]]
}

try_release_binary() {
    local platform
    local repo_base
    local download_base
    local asset
    local checksum
    local binary_temp
    local bin_dir
    local binary

    if ! platform="$(summon_platform)"; then
        echo "  [INFO]  No release binary available for this platform"
        return 1
    fi

    repo_base="$(repo_http_base "$GRIMOIRE_ARCANA_URL")"
    download_base="$(release_download_base "$repo_base" "$GRIMOIRE_SUMMON_RELEASE_TAG")"
    asset="grimoire-summon-$platform.tar.gz"
    checksum="$asset.sha256"

    binary_temp="$(mktemp -d "${TMPDIR:-/tmp}/grimoire-summon.XXXXXX")"
    bin_dir="$binary_temp/bin"
    mkdir -p "$bin_dir"

    echo "  [INFO]  Trying release binary: $asset"
    if ! download_file "$download_base/$asset" "$binary_temp/$asset"; then
        echo "  [INFO]  Release binary unavailable — falling back to Python source"
        rm -rf "$binary_temp"
        return 1
    fi

    if download_file "$download_base/$checksum" "$binary_temp/$checksum"; then
        if ! (cd "$binary_temp" && verify_checksum "$checksum"); then
            echo "  [WARN]  Release binary checksum failed — falling back to Python source"
            rm -rf "$binary_temp"
            return 1
        fi
    else
        echo "  [WARN]  Release checksum unavailable — falling back to Python source"
        rm -rf "$binary_temp"
        return 1
    fi

    if ! tar -xzf "$binary_temp/$asset" -C "$bin_dir"; then
        echo "  [WARN]  Could not extract release binary — falling back to Python source"
        rm -rf "$binary_temp"
        return 1
    fi

    binary="$bin_dir/grimoire-summon"
    if [[ ! -x "$binary" ]]; then
        chmod +x "$binary" 2>/dev/null || true
    fi
    if [[ ! -x "$binary" ]]; then
        echo "  [WARN]  Release binary is not executable — falling back to Python source"
        rm -rf "$binary_temp"
        return 1
    fi

    echo "  [OK]    Running release binary"
    TEMP_DIR="$binary_temp"
    exec "$binary" "$@"
}

if [[ -f "$SCRIPT_SOURCE" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_SOURCE")" && pwd)"
    if [[ "$GRIMOIRE_SUMMON_BINARY" == "always" ]]; then
        try_release_binary "$@" || true
    fi
else
    if should_try_binary; then
        try_release_binary "$@" || true
    fi
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
