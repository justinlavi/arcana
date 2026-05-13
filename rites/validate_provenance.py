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
import os
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)

SCAN_DIRS = ["chapters", "docs", "invocations"]
EXEMPT_FILENAMES = {"README.md", "CHANGELOG.md", "log.md", "VERSION"}
SKIP_DIRS = {"sources", "formulae", ".git"}


def parse_frontmatter(text):
    m = FRONTMATTER_RE.match(text)
    if not m:
        return {}
    fields = {}
    for line in m.group(1).splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            fields[key] = [s.strip().strip("'\"") for s in inner.split(",")] if inner else []
        else:
            fields[key] = value.strip("'\"")
    return fields


def collect_pages(root):
    seen = set()
    for d in SCAN_DIRS:
        sub = root / d
        if not sub.is_dir():
            continue
        for path in sorted(sub.rglob("*.md")):
            if path.name in EXEMPT_FILENAMES:
                continue
            if any(part in SKIP_DIRS for part in path.relative_to(root).parts):
                continue
            seen.add(path)
            yield path
    for path in sorted(root.glob("*.md")):
        if path in seen or path.name in EXEMPT_FILENAMES:
            continue
        yield path


def main():
    parser = argparse.ArgumentParser(description="Validate page provenance")
    parser.add_argument("--grimoire", type=Path,
                        default=Path(os.environ.get("GRIMOIRE_ARCANA",
                                                    Path(__file__).resolve().parent.parent)),
                        help="Grimoire root (default: GRIMOIRE_ARCANA env or rites parent)")
    args = parser.parse_args()
    root = args.grimoire.expanduser().resolve()

    print()
    print("Validating Provenance")
    print("==================================")
    print(f"Grimoire root: {root}")
    print()

    violations = 0
    pages_checked = 0

    for path in collect_pages(root):
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
            print(f"  WARN  {rel}: `sources:` must be a YAML list")
            violations += 1
            continue
        if not sources:
            print(f"  WARN  {rel}: authority='{authority}' but no `sources:` listed")
            violations += 1
            continue
        for src in sources:
            if not isinstance(src, str) or not src:
                continue
            if src.startswith("inbox/"):
                print(f"  WARN  {rel}: source '{src}' points at inbox/ (transient — pages must cite sources/ instead)")
                violations += 1
                continue
            if src.startswith("sources/"):
                target = root / src
                if not target.exists():
                    print(f"  WARN  {rel}: source '{src}' does not resolve under sources/")
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
