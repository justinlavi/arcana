#!/usr/bin/env python3
"""Validate that external/hybrid pages and source wrappers cite real sources.

Walks every page in a grimoire (skipping templates and exempt files) and
checks each page whose `authority:` is `external` or `hybrid`:

  1. Has at least one entry in `sources:`.
  2. Each source path that begins with `sources/` resolves to an existing file
     under the grimoire's `sources/` directory. (URLs and out-of-grimoire paths
     are not network-checked.)
  3. No page cites transient `inbox/` paths.

Also checks Markdown source wrappers under `sources/`:

  1. A wrapper declaring `type: source` must use `authority: external`.
  2. It must have non-empty `sources:`.
  3. It must not cite itself.

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
from diagnostics import DiagnosticReporter, add_output_format_arg

SCAN_DIRS = ["chapters", "docs", "invocations"]
EXEMPT_FILENAMES = {"README.md", "CHANGELOG.md", "log.md", "VERSION"}
SKIP_DIRS = {"sources", "formulae", ".git"}
SOURCE_EXEMPT_FILENAMES = {"README.md"}


def check_source_reference(src, rel, root, reporter, human):
    """Add diagnostics for one `sources:` entry."""
    if not isinstance(src, str) or not src:
        return
    if src.startswith("inbox/"):
        reporter.error(
            "PROVENANCE_INBOX_SOURCE",
            f"source '{src}' points at inbox/",
            path=rel,
            hint="Pages must cite sources/ or external URLs.",
            docs_reference="docs/operating_model.md",
        )
        if human:
            warn(
                f"{rel}: source '{src}' points at inbox/ "
                "(transient - pages must cite sources/ instead)"
            )
        return
    if src.startswith("sources/"):
        target = root / src
        if not target.exists():
            reporter.error(
                "PROVENANCE_SOURCE_MISSING",
                f"source '{src}' does not resolve under sources/",
                path=rel,
                docs_reference="docs/page_schema.md",
            )
            if human:
                warn(f"{rel}: source '{src}' does not resolve under sources/")


def iter_source_markdown(root):
    """Yield Markdown files under sources/ that may be source wrappers."""
    sources_dir = root / "sources"
    if not sources_dir.is_dir():
        return
    for path in sorted(sources_dir.rglob("*.md")):
        if path.name in SOURCE_EXEMPT_FILENAMES:
            continue
        yield path


def main():
    parser = argparse.ArgumentParser(description="Validate page provenance")
    add_grimoire_arg(parser)
    add_output_format_arg(parser)
    args = parser.parse_args()
    root = resolve_grimoire_arg(args.grimoire)
    human = args.format == "human"
    reporter = DiagnosticReporter("validate_provenance", root)

    if human:
        print()
        print("Validating Provenance")
        print("==================================")
        print(f"Grimoire root: {root}")
        print()

    pages_checked = 0
    source_wrappers_checked = 0

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
        rel = path.relative_to(root).as_posix()
        sources = fm.get("sources") or []
        if not isinstance(sources, list):
            reporter.error(
                "PROVENANCE_SOURCES_LIST_REQUIRED",
                "`sources:` must be a YAML list",
                path=rel,
                docs_reference="docs/page_schema.md",
            )
            if human:
                warn(f"{rel}: `sources:` must be a YAML list")
            continue
        if not sources:
            reporter.error(
                "PROVENANCE_MISSING_SOURCES",
                f"authority='{authority}' but no `sources:` listed",
                path=rel,
                docs_reference="docs/page_schema.md",
            )
            if human:
                warn(f"{rel}: authority='{authority}' but no `sources:` listed")
            continue
        for src in sources:
            check_source_reference(src, rel, root, reporter, human)

    for path in iter_source_markdown(root):
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        fm = parse_frontmatter(content)
        if fm.get("type") != "source":
            continue
        source_wrappers_checked += 1
        rel = path.relative_to(root).as_posix()
        authority = fm.get("authority", "")
        if authority != "external":
            reporter.error(
                "PROVENANCE_SOURCE_WRAPPER_AUTHORITY",
                "source wrappers must declare authority='external'",
                path=rel,
                hint="Source wrappers capture external material; authored synthesis belongs in chapters/.",
                docs_reference="docs/page_schema.md",
            )
            if human:
                warn(f"{rel}: source wrappers must declare authority='external'")

        sources = fm.get("sources") or []
        if not isinstance(sources, list):
            reporter.error(
                "PROVENANCE_SOURCES_LIST_REQUIRED",
                "`sources:` must be a YAML list",
                path=rel,
                docs_reference="docs/page_schema.md",
            )
            if human:
                warn(f"{rel}: `sources:` must be a YAML list")
            continue
        if not sources:
            reporter.error(
                "PROVENANCE_SOURCE_WRAPPER_MISSING_SOURCES",
                "source wrapper must list its original URL, capture origin, or sibling raw artifact",
                path=rel,
                docs_reference="docs/page_schema.md",
            )
            if human:
                warn(f"{rel}: source wrapper has no `sources:` entries")
            continue
        for src in sources:
            if src == rel:
                reporter.error(
                    "PROVENANCE_SOURCE_WRAPPER_SELF_REFERENCE",
                    "source wrapper must not cite itself",
                    path=rel,
                    hint="Cite the original URL, capture origin, or sibling raw artifact instead.",
                    docs_reference="docs/page_schema.md",
                )
                if human:
                    warn(f"{rel}: source wrapper cites itself")
                continue
            check_source_reference(src, rel, root, reporter, human)

    checked = {
        "external_or_hybrid_pages": pages_checked,
        "source_wrappers": source_wrappers_checked,
    }
    if not human:
        reporter.emit(args.format, checked=checked)
        return reporter.exit_code()

    print()
    print(f"Pages with external/hybrid authority: {pages_checked}")
    print(f"Source wrappers checked:             {source_wrappers_checked}")
    print(f"Provenance violations:               {reporter.error_count()}")
    print()

    if reporter.error_count() == 0:
        print("Provenance validation passed")
        return 0
    print("Provenance validation failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
