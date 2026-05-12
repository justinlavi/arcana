#!/usr/bin/env python3
"""Validates invocation and formula format compliance (required sections).

Usage: python3 rites/validate_format.py
Exit codes: 0 = success, 1 = format violations found
"""

import os
import re
import sys
from pathlib import Path

ARCANA_ROOT = Path(os.environ.get("GRIMOIRE_ARCANA", Path(__file__).resolve().parent.parent))

INVOCATION_REQUIRED_SECTIONS = [
    (r"^# ", "Title heading (# ...)"),
    (r"^## .*Purpose", "## Purpose section"),
    (r"^## .*Invocation", "## Invocation section"),
]


def main():
    errors = 0

    print()
    print("Validating Invocation and Formula Format")
    print("==================================")
    print(f"Arcana root: {ARCANA_ROOT}")
    print()

    # Validate invocation files
    print("Checking invocation format compliance...")
    inv_violations = 0

    invocations_dir = ARCANA_ROOT / "invocations"
    if invocations_dir.is_dir():
        for path in sorted(invocations_dir.rglob("*.md")):
            if path.name == "INDEX.md" or path.name == "base_invocation.md":
                continue

            content = path.read_text(errors="replace")
            file_errors = 0

            for pattern, label in INVOCATION_REQUIRED_SECTIONS:
                if not re.search(pattern, content, re.MULTILINE):
                    if file_errors == 0:
                        print()
                        print(f"  WARN  Format violations in: {path.relative_to(ARCANA_ROOT)}")
                    print(f"         Missing section: {label}")
                    file_errors += 1
                    inv_violations += 1
                    errors += 1

    if inv_violations == 0:
        print("  OK    All invocations have required sections")
    print()

    # Validate INDEX.md files are thin routers (< 200 lines)
    print("Checking INDEX.md files are thin routers...")
    index_violations = 0

    if invocations_dir.is_dir():
        for path in sorted(invocations_dir.rglob("INDEX.md")):
            lines = len(path.read_text(errors="replace").splitlines())
            if lines > 200:
                print(f"  WARN  INDEX.md too long ({lines} lines, should be < 200): "
                      f"{path.relative_to(ARCANA_ROOT)}")
                index_violations += 1
                errors += 1

    if index_violations == 0:
        print("  OK    All INDEX.md files are appropriately sized")
    print()

    # Validate formulae have basic structure
    print("Checking formula format...")
    formula_violations = 0

    formulae_dir = ARCANA_ROOT / "formulae"
    if formulae_dir.is_dir():
        for path in sorted(formulae_dir.rglob("*.md")):
            content = path.read_text(errors="replace")
            if not re.search(r"^# ", content, re.MULTILINE):
                print(f"  WARN  Formula missing title heading: {path.relative_to(ARCANA_ROOT)}")
                formula_violations += 1
                errors += 1

    if formula_violations == 0:
        print("  OK    All formulae have proper format")
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
