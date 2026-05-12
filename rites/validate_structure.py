#!/usr/bin/env python3
"""Validates Arcana structure completeness.

Usage: python3 rites/validate_structure.py
Exit codes: 0 = success, 1 = validation errors found
"""

import os
import sys
from pathlib import Path

ARCANA_ROOT = Path(os.environ.get("GRIMOIRE_ARCANA", Path(__file__).resolve().parent.parent))

REQUIRED_DIRS = [
    "docs",
    "invocations/grimoire",
    "invocations/arcana",
    "invocations/meta",
    "formulae",
    "rites",
    "resources",
    "formulae/grimoire",
    "skills",
]

REQUIRED_FILES = [
    "INDEX.md",
    "README.md",
    "CHANGELOG.md",
    "rites/summon.sh",
    "rites/register_skills.py",
    "catalog.json",
    "docs/quickstart.md",
    "docs/agent_configuration.md",
    "docs/operating_model.md",
    "docs/governance.md",
    "docs/reference.md",
]

INVOCATION_DIRS = ["grimoire", "arcana", "meta"]


def main():
    errors = 0

    print()
    print("Validating Arcana Structure")
    print("==================================")
    print(f"Arcana root: {ARCANA_ROOT}")
    print()

    print("Checking required directories...")
    for d in REQUIRED_DIRS:
        path = ARCANA_ROOT / d
        if not path.is_dir():
            print(f"  MISSING  directory: {d}")
            errors += 1
        else:
            print(f"  OK       {d}")
    print()

    print("Checking required files...")
    for f in REQUIRED_FILES:
        path = ARCANA_ROOT / f
        if not path.is_file():
            print(f"  MISSING  file: {f}")
            errors += 1
        else:
            print(f"  OK       {f}")
    print()

    print("Checking invocation directory structure...")
    for inv_dir in INVOCATION_DIRS:
        index = ARCANA_ROOT / "invocations" / inv_dir / "INDEX.md"
        if not index.is_file():
            print(f"  MISSING  INDEX.md in invocations/{inv_dir}/")
            errors += 1
        else:
            print(f"  OK       invocations/{inv_dir}/INDEX.md")
    print()

    print("==================================")
    if errors == 0:
        print("Structure validation passed")
        return 0
    else:
        print(f"Structure validation failed with {errors} errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())
