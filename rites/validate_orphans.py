#!/usr/bin/env python3
"""Detect orphan pages in a grimoire.

A page is an orphan when no other markdown file in the grimoire links to it
via either a relative-path markdown link or a wikilink (resolved by stem or
`aliases:` frontmatter).

Pages that are themselves entry points are excluded from the orphan check:
  * the grimoire root hub (`<grimoire>/<grimoire>.md`)
  * folder hubs (`<folder>/<folder>.md`) — they appear in their parent hub's tree
  * `log.md`, `README.md`, `CHANGELOG.md`
  * everything under `sources/`

Usage:
    python3 rites/validate_orphans.py [--grimoire <path>]

Exit codes: 0 = no orphans, 1 = orphans found
"""

import argparse
import os
import re
import sys
from pathlib import Path

FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
LINK_RE = re.compile(r"\]\(([^)]+)\)")
WIKILINK_RE = re.compile(r"\[\[([^\]\n]+)\]\]")
CODE_FENCE_RE = re.compile(r"^```")

EXEMPT_FILENAMES = {"README.md", "CHANGELOG.md", "log.md", "VERSION", "SKILL.md"}
SKIP_DIRS = {"sources", "inbox", ".git", "skills"}


def parse_frontmatter_aliases(content):
    m = FRONTMATTER_RE.match(content)
    if not m:
        return []
    for line in m.group(1).splitlines():
        if not line.startswith("aliases:"):
            continue
        value = line.partition(":")[2].strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if not inner:
                return []
            return [s.strip().strip("'\"") for s in inner.split(",")]
    return []


def strip_code_blocks(content):
    out = []
    in_fence = False
    for line in content.splitlines():
        if CODE_FENCE_RE.match(line):
            in_fence = not in_fence
            out.append("")
            continue
        if in_fence:
            out.append("")
            continue
        out.append(re.sub(r"`[^`]*`", lambda m: " " * len(m.group()), line))
    return "\n".join(out)


def is_hub(path):
    return path.stem == path.parent.name


def collect_pages(root):
    pages = []
    for path in sorted(root.rglob("*.md")):
        rel_parts = path.relative_to(root).parts
        if rel_parts and rel_parts[0] in SKIP_DIRS:
            continue
        pages.append(path)
    return pages


def build_alias_map(pages, root):
    """alias-or-stem (lowercase) → page path"""
    m = {}
    for p in pages:
        try:
            content = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        m.setdefault(p.stem.lower(), p)
        for alias in parse_frontmatter_aliases(content):
            key = alias.strip().lower()
            if key:
                m.setdefault(key, p)
    return m


def collect_inbound(pages, root, alias_map):
    """Return set of pages with at least one inbound link or wikilink."""
    inbound = set()
    for src in pages:
        try:
            content = src.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        scanable = strip_code_blocks(content)

        for m in LINK_RE.finditer(scanable):
            link = m.group(1).split("#")[0].split("?")[0]
            if not link:
                continue
            if re.match(r"^[a-z]+://", link) or link.startswith("mailto:"):
                continue
            if link.startswith("/"):
                target = root / link.lstrip("/")
            else:
                target = (src.parent / link).resolve()
            try:
                target = target.resolve()
            except OSError:
                continue
            if target.is_file() and target.suffix == ".md":
                inbound.add(target)

        for m in WIKILINK_RE.finditer(scanable):
            body = m.group(1).split("|", 1)[0].split("#", 1)[0].strip().lower()
            if body in alias_map:
                inbound.add(alias_map[body].resolve())
    return inbound


def main():
    parser = argparse.ArgumentParser(description="Detect orphan pages in a grimoire")
    parser.add_argument("--grimoire", type=Path,
                        default=Path(os.environ.get("GRIMOIRE_ARCANA",
                                                    Path(__file__).resolve().parent.parent)),
                        help="Grimoire root (default: GRIMOIRE_ARCANA env or rites parent)")
    args = parser.parse_args()
    root = args.grimoire.expanduser().resolve()

    print()
    print("Validating Orphans")
    print("==================================")
    print(f"Grimoire root: {root}")
    print()

    pages = collect_pages(root)
    alias_map = build_alias_map(pages, root)
    inbound = collect_inbound(pages, root, alias_map)

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

    if not orphans:
        print("  OK    No orphan pages found")
    else:
        print(f"  {len(orphans)} orphan page(s) — no other page links to them:")
        for o in sorted(orphans):
            print(f"  ORPHAN  {o}")

    print()
    print("==================================")
    if not orphans:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
