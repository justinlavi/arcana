#!/usr/bin/env python3
"""Validates invocation, formula, and hub format compliance.

Hub convention (v2): For any folder F that acts as a router, the hub file is
F/<basename(F)>.md. Hubs are validated as thin routers (< 200 lines, exists);
non-hub invocation files are validated against the invocation schema.

Usage: python3 rites/validate_format.py
Exit codes: 0 = success, 1 = format violations found
"""

import re
import sys
from pathlib import Path

from _lib import default_arcana_root, ok, warn

ARCANA_ROOT = default_arcana_root()

INVOCATION_REQUIRED_SECTIONS = [
    (r"^# ", "Title heading (# ...)"),
    (r"^## .*Purpose", "## Purpose section"),
    (r"^## .*Invocation", "## Invocation section"),
]

HUB_MAX_LINES = 200


def is_hub(path):
    """A hub file is named after its parent folder: <folder>/<folder>.md."""
    return path.stem == path.parent.name


SKIP_DIRS = {"sources"}


def under_skip_dir(path):
    rel = path.relative_to(ARCANA_ROOT)
    return rel.parts and rel.parts[0] in SKIP_DIRS


def main():
    errors = 0

    print()
    print("Validating Invocation, Formula, and Hub Format")
    print("==================================")
    print(f"Arcana root: {ARCANA_ROOT}")
    print()

    invocations_dir = ARCANA_ROOT / "invocations"

    # 1. Invocation files (non-hub) must follow the invocation schema.
    print("Checking invocation format compliance...")
    inv_violations = 0

    # Pattern templates and shared fragments aren't standalone invocations.
    INVOCATION_EXEMPT = {"base_invocation.md", "grimoire_directory_guard.md"}

    if invocations_dir.is_dir():
        for path in sorted(invocations_dir.rglob("*.md")):
            if path.name in INVOCATION_EXEMPT:
                continue
            if is_hub(path):
                continue

            content = path.read_text(errors="replace")
            file_errors = 0

            for pattern, label in INVOCATION_REQUIRED_SECTIONS:
                if not re.search(pattern, content, re.MULTILINE):
                    if file_errors == 0:
                        print()
                        warn(f"Format violations in: {path.relative_to(ARCANA_ROOT)}")
                    print(f"          Missing section: {label}")
                    file_errors += 1
                    inv_violations += 1
                    errors += 1

    if inv_violations == 0:
        ok("All invocations have required sections")
    print()

    # 2. Hub files must be thin routers.
    print(f"Checking hub files are thin routers (< {HUB_MAX_LINES} lines)...")
    hub_violations = 0

    if invocations_dir.is_dir():
        for path in sorted(invocations_dir.rglob("*.md")):
            if not is_hub(path):
                continue
            lines = len(path.read_text(errors="replace").splitlines())
            if lines > HUB_MAX_LINES:
                warn(f"Hub too long ({lines} lines, should be < {HUB_MAX_LINES}): "
                     f"{path.relative_to(ARCANA_ROOT)}")
                hub_violations += 1
                errors += 1

    if hub_violations == 0:
        ok("All hub files are appropriately sized")
    print()

    # 3. Formulae must have a title heading.
    print("Checking formula format...")
    formula_violations = 0

    formulae_dir = ARCANA_ROOT / "formulae"
    if formulae_dir.is_dir():
        for path in sorted(formulae_dir.rglob("*.md")):
            content = path.read_text(errors="replace")
            if not re.search(r"^# ", content, re.MULTILINE):
                warn(f"Formula missing title heading: {path.relative_to(ARCANA_ROOT)}")
                formula_violations += 1
                errors += 1

    if formula_violations == 0:
        ok("All formulae have proper format")
    print()

    print("==================================")
    if errors == 0:
        print("Format validation passed")
        return 0
    else:
        print(f"Format validation failed with {errors} issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
