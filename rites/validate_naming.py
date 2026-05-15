#!/usr/bin/env python3
"""Validates snake_case naming convention for files and directories.

Usage: python3 rites/validate_naming.py
Exit codes: 0 = success, 1 = violations found
"""

import re
import sys
from pathlib import Path

from _lib import default_arcana_root

ARCANA_ROOT = default_arcana_root()

UPPERCASE_EXCEPTIONS = {"README.md", "CHANGELOG.md", "CONTRIBUTING.md",
                        "CLAUDE.md", "AGENTS.md", "LICENSE.md",
                        "IMPLEMENTATION_PLAN.md", "VERSION"}


SKIP_DIRS = {"sources", ".git", "tests"}


def check_naming(glob_pattern, label, ext):
    errors = 0
    violations = 0

    print(f"Checking {label} naming...")
    for path in sorted(ARCANA_ROOT.rglob(glob_pattern)):
        name = path.name
        rel_parts = path.relative_to(ARCANA_ROOT).parts
        if rel_parts and rel_parts[0] in SKIP_DIRS:
            continue

        if name in UPPERCASE_EXCEPTIONS:
            continue

        if re.match(r"^[a-z].*-.*\." + ext + "$", name):
            print(f"  WARN  Hyphenated (should use snake_case): {path.relative_to(ARCANA_ROOT)}")
            violations += 1
            errors += 1

        if re.search(r"[a-z][A-Z]", name):
            print(f"  WARN  CamelCase (should use snake_case): {path.relative_to(ARCANA_ROOT)}")
            violations += 1
            errors += 1

    if violations == 0:
        print(f"  OK    All {label} use proper naming")
    print()
    return errors


def main():
    errors = 0

    print()
    print("Validating Naming Conventions")
    print("==================================")
    print(f"Arcana root: {ARCANA_ROOT}")
    print()

    errors += check_naming("*.md", "markdown file", "md")
    errors += check_naming("*.py", "Python script", "py")

    print("==================================")
    if errors == 0:
        print("Naming validation passed")
        return 0
    else:
        print(f"Naming validation found {errors} issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
