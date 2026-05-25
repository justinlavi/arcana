#!/bin/bash
# rites/summon.sh
# Grimoire Summoning Rite - Bootstrap (Linux/Mac)
#
# Prefers a GitHub Release binary when run from the public curl command,
# then falls back to the Python source bootstrap when needed.
#
# One-liner entry point:
#   curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | bash

set -euo pipefail

DEFAULT_ARCANA_URL="https://github.com/justinlavi/arcana.git"
DEFAULT_ARCANA_REF="main"

: "${ARCANA_URL:=$DEFAULT_ARCANA_URL}"
: "${ARCANA_REF:=$DEFAULT_ARCANA_REF}"
: "${GRIMOIRE_SUMMON_PY_DEPS:=${XDG_CACHE_HOME:-$HOME/.cache}/grimoire/summon-python}"
: "${GRIMOIRE_SUMMON_BINARY:=auto}"
: "${GRIMOIRE_SUMMON_RELEASE_TAG:=latest}"
export ARCANA_URL
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

: "${ARCANA_RAW_BASE:=$(derive_raw_base "$ARCANA_URL" "$ARCANA_REF")}"

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
        mingw*|msys*|cygwin*) os="windows" ;;
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

arg_disables_gui() {
    local arg
    for arg in "$@"; do
        case "$arg" in
            --cli|-h|--help) return 0 ;;
        esac
    done
    return 1
}

has_display_session() {
    [[ -n "${DISPLAY:-}" || -n "${WAYLAND_DISPLAY:-}" || "${XDG_SESSION_TYPE:-}" == "x11" || "${XDG_SESSION_TYPE:-}" == "wayland" ]]
}

should_prefer_source_for_linux_gui() {
    local platform

    [[ "$GRIMOIRE_SUMMON_BINARY" == "auto" ]] || return 1
    [[ ! -f "$SCRIPT_SOURCE" ]] || return 1
    platform="$(summon_platform 2>/dev/null || true)"
    [[ "$platform" == linux-* ]] || return 1
    arg_disables_gui "$@" && return 1
    has_display_session
}

verify_checksum() {
    local checksum="$1"
    local normalized="$checksum.normalized"
    local check_file="$checksum"

    # Windows-built checksum assets may contain CRLF. GNU sha256sum under
    # Git Bash can treat the carriage return as part of the filename, so
    # normalize before verification. This keeps older published assets usable.
    if command -v tr &>/dev/null; then
        tr -d '\r' < "$checksum" > "$normalized"
        check_file="$normalized"
    fi

    if command -v sha256sum &>/dev/null; then
        sha256sum -c "$check_file"
    elif command -v shasum &>/dev/null; then
        shasum -a 256 -c "$check_file"
    else
        echo "  [WARN]  sha256sum/shasum not found - skipping checksum verification"
        return 0
    fi
}

extract_archive() {
    local archive="$1"
    local dest="$2"
    local archive_win
    local dest_win
    local py

    case "$archive" in
        *.zip)
            if command -v unzip &>/dev/null; then
                unzip -q "$archive" -d "$dest"
            elif command -v powershell.exe &>/dev/null && command -v cygpath &>/dev/null; then
                archive_win="$(cygpath -w "$archive")"
                dest_win="$(cygpath -w "$dest")"
                powershell.exe -NoProfile -Command \
                    "Expand-Archive -LiteralPath '$archive_win' -DestinationPath '$dest_win' -Force"
            else
                py="$(command -v python3 || command -v python || true)"
                if [[ -z "$py" ]]; then
                    return 1
                fi
                "$py" -c "import sys, zipfile; zipfile.ZipFile(sys.argv[1]).extractall(sys.argv[2])" "$archive" "$dest"
            fi
            ;;
        *.tar.gz)
            tar -xzf "$archive" -C "$dest"
            ;;
        *)
            return 1
            ;;
    esac
}

should_try_binary() {
    if [[ "$GRIMOIRE_SUMMON_BINARY" == "never" ]]; then
        return 1
    fi
    if [[ "$GRIMOIRE_SUMMON_BINARY" == "always" ]]; then
        return 0
    fi
    if should_prefer_source_for_linux_gui "$@"; then
        echo "  [INFO]  Linux GUI session detected - using Python source launcher"
        return 1
    fi
    [[ ! -f "$SCRIPT_SOURCE" ]]
}

# Defined before the source-download branch because bash only knows functions
# after their definitions have executed. Keep this tiny helper independent of
# Python so the piped bootstrap can decide whether to fetch summon_gui.py.
should_download_gui_source() {
    arg_disables_gui "$@" && return 1
    return 0
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
    local binary_name

    if ! platform="$(summon_platform)"; then
        echo "  [INFO]  No release binary available for this platform"
        return 1
    fi

    repo_base="$(repo_http_base "$ARCANA_URL")"
    download_base="$(release_download_base "$repo_base" "$GRIMOIRE_SUMMON_RELEASE_TAG")"
    if [[ "$platform" == windows-* ]]; then
        asset="grimoire-summon-$platform.zip"
        binary_name="grimoire-summon.exe"
    else
        asset="grimoire-summon-$platform.tar.gz"
        binary_name="grimoire-summon"
    fi
    checksum="$asset.sha256"

    binary_temp="$(mktemp -d "${TMPDIR:-/tmp}/grimoire-summon.XXXXXX")"
    bin_dir="$binary_temp/bin"
    mkdir -p "$bin_dir"

    echo "  [INFO]  Trying release binary: $asset"
    if ! download_file "$download_base/$asset" "$binary_temp/$asset"; then
        echo "  [INFO]  Release binary unavailable - falling back to Python source"
        rm -rf "$binary_temp"
        return 1
    fi

    if download_file "$download_base/$checksum" "$binary_temp/$checksum"; then
        if ! (cd "$binary_temp" && verify_checksum "$checksum"); then
            echo "  [WARN]  Release binary checksum failed - falling back to Python source"
            rm -rf "$binary_temp"
            return 1
        fi
    else
        echo "  [WARN]  Release checksum unavailable - falling back to Python source"
        rm -rf "$binary_temp"
        return 1
    fi

    if ! extract_archive "$binary_temp/$asset" "$bin_dir"; then
        echo "  [WARN]  Could not extract release binary - falling back to Python source"
        rm -rf "$binary_temp"
        return 1
    fi

    binary="$bin_dir/$binary_name"
    if [[ ! -x "$binary" ]]; then
        chmod +x "$binary" 2>/dev/null || true
    fi
    if [[ "$platform" == windows-* && ! -f "$binary" ]]; then
        echo "  [WARN]  Release binary not found after extraction - falling back to Python source"
        rm -rf "$binary_temp"
        return 1
    fi
    if [[ "$platform" != windows-* && ! -x "$binary" ]]; then
        echo "  [WARN]  Release binary is not executable - falling back to Python source"
        rm -rf "$binary_temp"
        return 1
    fi

    echo "  [OK]    Running release binary"
    # Run as a subprocess, not exec, so a crash (e.g. SIGABRT from GLFW/GLX)
    # returns a non-zero exit code here rather than killing the shell process
    # and losing the Python fallback path.
    if "$binary" "$@"; then
        rm -rf "$binary_temp"
        exit 0
    fi
    echo "  [WARN]  Release binary exited abnormally - falling back to Python source"
    rm -rf "$binary_temp"
    return 1
}

if [[ -f "$SCRIPT_SOURCE" ]]; then
    SCRIPT_DIR="$(cd "$(dirname "$SCRIPT_SOURCE")" && pwd)"
    if [[ "$GRIMOIRE_SUMMON_BINARY" == "always" ]]; then
        try_release_binary "$@" || true
    fi
else
    if should_try_binary "$@"; then
        try_release_binary "$@" || true
    fi
    TEMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/grimoire-summon.XXXXXX")"
    SCRIPT_DIR="$TEMP_DIR/rites"
    mkdir -p "$SCRIPT_DIR/templates"
    echo "  [INFO]  Downloading summoning companion scripts..."
    # summon.py is the dispatcher and summon_core.py is the install engine.
    # The Grimoire block template is canonical and must travel with source
    # bootstrap installs. summon_gui.py is only needed when the GUI runs, so
    # skip it for --cli/-h/--help to keep the source bootstrap minimal.
    download_file "$ARCANA_RAW_BASE/rites/summon.py" "$SCRIPT_DIR/summon.py"
    download_file "$ARCANA_RAW_BASE/rites/summon_core.py" "$SCRIPT_DIR/summon_core.py"
    download_file "$ARCANA_RAW_BASE/rites/templates/grimoire_block.md" "$SCRIPT_DIR/templates/grimoire_block.md"
    if should_download_gui_source "$@"; then
        download_file "$ARCANA_RAW_BASE/rites/summon_gui.py" "$SCRIPT_DIR/summon_gui.py" || \
            echo "  [WARN]  summon_gui.py download failed - GUI mode will fall back to CLI"
    fi
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

prompt_yes() {
    local prompt="$1"
    local response=""

    if [[ -t 0 ]]; then
        read -r -p "$prompt [y/N]: " response || response=""
    elif [[ -r /dev/tty && -w /dev/tty ]]; then
        printf "%s [y/N]: " "$prompt" > /dev/tty
        IFS= read -r response < /dev/tty || response=""
    else
        echo "  [WARN]  No interactive terminal available - not installing dependencies"
        return 1
    fi

    [[ "$response" == [yY] ]]
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
    arg_disables_gui "$@" && return 1
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

    if ! prompt_yes "  Install Python 3 now? (requires sudo)"; then
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
    if ! python_can_import "dearpygui.dearpygui"; then
        PKG_MGR=$(detect_pkg_manager)
        echo "  [INFO]  Dear PyGui not found"
        if ! "$PYTHON" -m pip --version &>/dev/null; then
            echo "  [INFO]  pip not found"
            if prompt_yes "  Install pip now? (may require sudo)"; then
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
                    echo "  [WARN]  pip not available - GUI may fall back to CLI"
                    echo "  [INFO]  To enable app mode manually, run: $(pip_install_hint "$PKG_MGR")"
                fi
            else
                echo "  [WARN]  pip install skipped - GUI may fall back to CLI"
                echo "  [INFO]  To enable app mode manually, run: $(pip_install_hint "$PKG_MGR")"
            fi
        fi

        if "$PYTHON" -m pip --version &>/dev/null; then
            if prompt_yes "  Install Dear PyGui into $GRIMOIRE_SUMMON_PY_DEPS now?"; then
                mkdir -p "$GRIMOIRE_SUMMON_PY_DEPS"
                if "$PYTHON" -m pip install --upgrade --target "$GRIMOIRE_SUMMON_PY_DEPS" dearpygui 2>/dev/null; then
                    echo "  [OK]    Dear PyGui installed"
                else
                    echo "  [WARN]  Could not install Dear PyGui - GUI may fall back to CLI"
                fi
            else
                echo "  [WARN]  Dear PyGui install skipped - GUI will fall back to CLI"
            fi
        else
            echo "  [WARN]  pip unavailable - GUI may fall back to CLI"
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

# Display environment: DearPyGui requires X11/GLX (via XWayland on Wayland).
# When XWayland is running the compositor exports DISPLAY automatically.
# Setting DISPLAY=:0 blindly when only WAYLAND_DISPLAY is set causes GLFW
# to attempt an X connection that doesn't exist, producing GLX init failures.
# The Python bootstrap probes GL compatibility at runtime and falls back to
# CLI automatically - no manual DISPLAY override needed here.
if [[ -z "${DISPLAY:-}" && ( -n "${WAYLAND_DISPLAY:-}" || "${XDG_SESSION_TYPE:-}" == "wayland" ) ]]; then
    echo "  [INFO]  Wayland session detected - display compatibility will be probed at runtime"
fi

echo ""
exec "$PYTHON" "$SCRIPT_DIR/summon.py" "$@"
