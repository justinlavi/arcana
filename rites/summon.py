#!/usr/bin/env python3
"""Arcana Summoning Rite - installs Arcana and optionally clones grimoires.

Usage:
    python3 summon.py [--arcana-url URL] [--scope URL] [--cli] [--gui]

One-liner entry point:
    curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | bash

This file is the dispatcher. The actual install logic lives in
`summon_core.py` (CLI + git/HTTP/discovery, pure stdlib) and the optional
GUI front end lives in `summon_gui.py` (lazy-imported, requires DearPyGui).

Options:
    --arcana-url URL   URL of the Arcana git repository to install
    --scope URL        URL of the group/org containing your grimoires
    --cli              Force terminal mode (no GUI)
    --gui              Force GUI mode (DearPyGui)
    -h, --help         Show this help message

Environment variables:
    ARCANA_URL  Same as --arcana-url (flag takes precedence)
    GRIMOIRE_SCOPE       Same as --scope (flag takes precedence)
    GITLAB_TOKEN         GitLab personal access token for private instances
    GITHUB_TOKEN         GitHub token for private orgs
    GRIMOIRE_GUI_SCALE   Override DPI scale (e.g. 1.5 for HiDPI)
"""

import argparse
import os
import sys

from summon_core import run_cli


def _detect_gui_mode(args):
    """Decide GUI vs CLI. Returns (use_gui: bool, skip_reason: str)."""
    if args.gui:
        return True, ""
    if args.cli:
        return False, ""
    if sys.platform == "win32":
        return True, ""
    session_type = os.environ.get("XDG_SESSION_TYPE", "")
    has_display = bool(
        os.environ.get("DISPLAY")
        or os.environ.get("WAYLAND_DISPLAY")
        or session_type in ("x11", "wayland")
    )
    if not has_display:
        return False, "no display server detected"
    return True, ""


def main():
    parser = argparse.ArgumentParser(
        description="Arcana Summoning Rite - install Arcana and optionally clone grimoires"
    )
    parser.add_argument(
        "--arcana-url",
        help="URL of the Arcana git repository to install (defaults to public GitHub Arcana)",
    )
    parser.add_argument(
        "--scope",
        help="URL of the group/org containing your grimoires (e.g., https://github.com/my-org)",
    )
    parser.add_argument("--cli", action="store_true", help="Force terminal mode (no GUI)")
    parser.add_argument("--gui", action="store_true", help="Force GUI mode (Dear PyGui)")
    args = parser.parse_args()

    use_gui, skip_reason = _detect_gui_mode(args)

    if use_gui:
        try:
            # Lazy import keeps headless installs from needing DearPyGui at all.
            from summon_gui import run_gui
            run_gui(args)
        except Exception as e:
            print(f"  [WARN]  GUI failed ({e}), falling back to CLI")
            run_cli(args)
    else:
        if skip_reason and not args.cli:
            print(f"  [INFO]  Using CLI mode: {skip_reason}")
        run_cli(args)


if __name__ == "__main__":
    main()
