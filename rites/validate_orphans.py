#!/usr/bin/env python3
"""Detect orphan pages in a grimoire.

A page is an orphan when no other markdown file in the grimoire reaches it
through a valid layer-specific page link: Markdown links in public docs and
full-path wikilinks in vault/AI surfaces.

Pages that are themselves entry points are excluded from the orphan check:
  * the grimoire root hub (`<grimoire>/<grimoire>.md`)
  * folder hubs (`<folder>/<folder>.md`)  they appear in their parent hub's tree
  * `log.md`, `README.md`, `CHANGELOG.md`
  * everything under `sources/`

Usage:
    python3 rites/validate_orphans.py [--grimoire <path>]

Exit codes: 0 = no orphans, 1 = orphans found
"""

import argparse
import re
import sys
from pathlib import Path

from _lib import (
    LINK_RE,
    WIKILINK_RE,
    add_grimoire_arg,
    is_skipped,
    public_document,
    resolve_grimoire_arg,
    resolve_wikilink_path,
    strip_code_blocks,
    wikilink_target_body,
)
from diagnostics import DiagnosticReporter, add_output_format_arg

EXEMPT_FILENAMES = {"README.md", "RESTORATION.md", "CHANGELOG.md", "CONTRIBUTING.md", "log.md", "VERSION", "SKILL.md"}
SKIP_DIRS = {"sources", "inbox", ".git", "skills", "tests"}


def is_hub(path):
    return path.stem == path.parent.name


def collect_pages(root):
    pages = []
    for path in sorted(root.rglob("*.md")):
        if is_skipped(path.relative_to(root), SKIP_DIRS):
            continue
        pages.append(path)
    return pages


def resolve_markdown_page_link(link, src, root):
    """Resolve a public-doc Markdown link to an internal Markdown page."""
    target_path = link.split("#")[0].split("?")[0]
    if not target_path:
        return None
    if re.match(r"^[a-z]+://", target_path) or target_path.startswith("mailto:"):
        return None
    if target_path.startswith("/"):
        target = root / target_path.lstrip("/")
    else:
        target = (src.parent / target_path).resolve()
    try:
        target = target.resolve()
    except OSError:
        return None
    try:
        target.relative_to(root)
    except ValueError:
        return None
    if target.is_file() and target.suffix == ".md":
        return target
    return None


def collect_inbound(pages, root):
    """Return set of pages with at least one valid inbound page link."""
    inbound = set()
    for src in pages:
        try:
            content = src.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanable = strip_code_blocks(content)

        if public_document(src, root):
            for m in LINK_RE.finditer(scanable):
                path_target = resolve_markdown_page_link(m.group(1), src, root)
                if path_target is not None:
                    inbound.add(path_target.resolve())

        for m in WIKILINK_RE.finditer(scanable):
            body_raw = wikilink_target_body(m.group(1))
            path_target = resolve_wikilink_path(body_raw, root)
            if path_target is not None:
                inbound.add(path_target.resolve())
    return inbound


def main():
    parser = argparse.ArgumentParser(description="Detect orphan pages in a grimoire")
    add_grimoire_arg(parser)
    add_output_format_arg(parser)
    args = parser.parse_args()
    root = resolve_grimoire_arg(args.grimoire)
    human = args.format == "human"
    reporter = DiagnosticReporter("validate_orphans", root)

    if human:
        print()
        print("Validating Orphans")
        print("==================================")
        print(f"Grimoire root: {root}")
        print()

    pages = collect_pages(root)
    inbound = collect_inbound(pages, root)

    grimoire_name = root.name
    orphans = []
    for p in pages:
        if p.name in EXEMPT_FILENAMES:
            continue
        # Root hub is the entry point; folder hubs are reached from the parent
        # hub. If a hub has no inbound link, that's a real orphan worth flagging.
        if p.stem == grimoire_name and p.parent == root:
            continue
        if p.resolve() in inbound:
            continue
        orphans.append(p.relative_to(root))
        reporter.error(
            "ORPHAN_PAGE",
            "no other page links to this page",
            path=p.relative_to(root).as_posix(),
        )

    if not human:
        reporter.emit(args.format, checked={"pages": len(pages), "orphans": len(orphans)})
        return reporter.exit_code()

    if not orphans:
        print("  OK    No orphan pages found")
    else:
        print(f"  {len(orphans)} orphan page(s)  no other page links to them:")
        for o in sorted(orphans):
            print(f"  ORPHAN  {o}")

    print()
    print("==================================")
    return reporter.exit_code()


if __name__ == "__main__":
    sys.exit(main())
