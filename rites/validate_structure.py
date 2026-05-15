#!/usr/bin/env python3
"""Validates Arcana structure completeness.

Usage: python3 rites/validate_structure.py
Exit codes: 0 = success, 1 = validation errors found

Hub convention (v2):
    For any folder F that acts as a router, the hub file is F/<basename(F)>.md.
    The Arcana root hub is arcana.md; the grimoire/ invocation router is
    invocations/grimoire/grimoire.md; etc.
"""

import sys
from pathlib import Path

from _lib import default_arcana_root

ARCANA_ROOT = default_arcana_root()

REQUIRED_DIRS = [
    "docs",
    "invocations/grimoire",
    "invocations/arcana",
    "invocations/arcana/quality",
    "invocations/arcana/validators",
    "invocations/meta",
    "formulae",
    "formulae/grimoire",
    "rites",
    "resources",
    "skills",
    "sources",
]

REQUIRED_FILES = [
    "arcana.md",
    "README.md",
    "CHANGELOG.md",
    "VERSION",
    "log.md",
    "library.json",
    "grimoire.json",
    "rites/summon.sh",
    "rites/register_skills.py",
    "docs/installation.md",
    "docs/agent_configuration.md",
    "docs/operating_model.md",
    "docs/governance.md",
    "docs/reference.md",
    "docs/page_schema.md",
]

# Folders whose hub file must exist with the folder-name convention.
HUB_DIRS = [
    "invocations/grimoire",
    "invocations/arcana",
    "invocations/arcana/quality",
    "invocations/arcana/validators",
    "invocations/meta",
]


def hub_path(rel_dir):
    """Resolve the hub file path for a folder using the F/F.md convention."""
    folder = ARCANA_ROOT / rel_dir
    return folder / f"{folder.name}.md"


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

    print("Checking router hub files (folder-name convention)...")
    for d in HUB_DIRS:
        hub = hub_path(d)
        rel = hub.relative_to(ARCANA_ROOT)
        if not hub.is_file():
            print(f"  MISSING  hub file: {rel}")
            errors += 1
        else:
            print(f"  OK       {rel}")
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
