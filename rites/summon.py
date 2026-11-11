#!/usr/bin/env python3
"""Arcana Summoning Rite - installs Arcana and optionally clones grimoires.

Usage:
    python3 summon.py [--arcana-url URL] [--scope URL]
    python3 summon.py --check | --reconcile [--apply] | --update [--apply]

One-liner entry point:
    curl -fsSL https://raw.githubusercontent.com/justinlavi/arcana/main/rites/summon.sh | bash

This file is the dispatcher. The install logic lives in `summon_core.py`
(terminal install: git, discovery, library, agent files, skills; pure stdlib)
and the agent-legible state surface lives in `summon_state.py`. Everything runs
in the terminal; there is no GUI and no release binary.

Options:
    --arcana-url URL   URL of the Arcana git repository to install
    --scope URL        URL of the group/org containing your grimoires
    --cli              Accepted for compatibility with older instructions; the
                       installer is terminal-only, so this is the default
    -h, --help         Show this help message

Environment variables:
    ARCANA_URL      Same as --arcana-url (flag takes precedence)
    GRIMOIRE_SCOPE  Same as --scope (flag takes precedence)
    GITLAB_TOKEN    GitLab personal access token for private instances
    GITHUB_TOKEN    GitHub token for private orgs
"""

import argparse
import sys

from summon_core import run_cli


def build_parser():
    """Build the dispatcher's argument parser (install flags plus the state surface)."""
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
    parser.add_argument(
        "--cli",
        action="store_true",
        help="Accepted for compatibility; the installer is terminal-only",
    )
    return parser


def main():
    parser = build_parser()

    # Agent-legibility surface: --check / --reconcile / --update route to
    # summon_state instead of the interactive installer (see
    # rites/summon_state.py). It is only available on a full Arcana checkout;
    # the piped bootstrap ships the install-only subset, so a missing
    # summon_state degrades to the installer path rather than failing.
    try:
        from summon_state import add_state_args, is_state_invocation, run_state_command
        state_surface = True
    except ImportError:
        state_surface = False

    if state_surface:
        add_state_args(parser)
    args = parser.parse_args()

    if state_surface and is_state_invocation(args):
        sys.exit(run_state_command(args))

    run_cli(args)


if __name__ == "__main__":
    main()
