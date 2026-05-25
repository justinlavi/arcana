#!/usr/bin/env python3
"""Validate that pages with `authority: external` or `hybrid` cite real sources.

Walks every page in a grimoire (skipping templates and exempt files) and
checks each page whose `authority:` is `external` or `hybrid`:

  1. Has at least one entry in `sources:`.
  2. Each source path that begins with `sources/` resolves to an existing file
     under the grimoire's `sources/` directory. (URLs and out-of-grimoire paths
     are not network-checked.)

Usage:
    python3 rites/validate_provenance.py [--grimoire <path>]

Exit codes: 0 = all provenance resolves, 1 = violations found
"""

import argparse
import sys
from pathlib import Path

from _lib import (
    add_grimoire_arg,
    iter_pages,
    parse_frontmatter,
    resolve_grimoire_arg,
    warn,
)

SCAN_DIRS = ["chapters", "docs", "invocations"]
EXEMPT_FILENAMES = {"README.md", "CHANGELOG.md", "log.md", "VERSION"}
SKIP_DIRS = {"sources", "formulae", ".git"}


def main():
    parser = argparse.ArgumentParser(description="Validate page provenance")
    add_grimoire_arg(parser)
    args = parser.parse_args()
    root = resolve_grimoire_arg(args.grimoire)

    print()
    print("Validating Provenance")
    print("==================================")
    print(f"Grimoire root: {root}")
    print()

    violations = 0
    pages_checked = 0

    for path in iter_pages(root, SCAN_DIRS, exempt_filenames=EXEMPT_FILENAMES, skip_dirs=SKIP_DIRS):
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fm = parse_frontmatter(content)
        authority = fm.get("authority", "")
        if authority not in ("external", "hybrid"):
            continue
        pages_checked += 1
        rel = path.relative_to(root)
        sources = fm.get("sources") or []
        if not isinstance(sources, list):
            warn(f"{rel}: `sources:` must be a YAML list")
            violations += 1
            continue
        if not sources:
            warn(f"{rel}: authority='{authority}' but no `sources:` listed")
            violations += 1
            continue
        for src in sources:
            if not isinstance(src, str) or not src:
                continue
            if src.startswith("inbox/"):
                warn(f"{rel}: source '{src}' points at inbox/ (transient - pages must cite sources/ instead)")
                violations += 1
                continue
            if src.startswith("sources/"):
                target = root / src
                if not target.exists():
                    warn(f"{rel}: source '{src}' does not resolve under sources/")
                    violations += 1

    print()
    print(f"Pages with external/hybrid authority: {pages_checked}")
    print(f"Provenance violations:               {violations}")
    print()

    if violations == 0:
        print("Provenance validation passed")
        return 0
    print("Provenance validation failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
