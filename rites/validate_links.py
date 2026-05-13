#!/usr/bin/env python3
"""Validates internal links and wikilinks in markdown files.

Resolves three link forms:

  1. Standard markdown links: `[text](path/to/file.md)` — relative or root-anchored.
  2. Wikilinks: `[[page-name]]` — resolved via:
       a. exact filename stem match (`page-name.md` anywhere in the grimoire), or
       b. `aliases:` frontmatter match (any page whose `aliases:` contains the
          wikilink's body resolves to that page).
     Wikilinks may use `[[page#section]]` or `[[page|display text]]`; the body
     before `#` or `|` is what's resolved.

Usage: python3 rites/validate_links.py
Exit codes: 0 = success, 1 = broken links found
"""

import os
import re
import sys
from pathlib import Path

def _default_root():
    return Path(os.environ.get("GRIMOIRE_ARCANA", Path(__file__).resolve().parent.parent))

SKIP_DIRS = {
    "invocations/arcana/validators",
    "invocations/arcana/quality",
    "sources",
    "inbox",
}

SKIP_FILES = {"operating_model.md"}

LINK_RE = re.compile(r"\]\(([^)]+)\)")
WIKILINK_RE = re.compile(r"\[\[([^\]\n]+)\]\]")
FRONTMATTER_RE = re.compile(r"\A---\s*\n(.*?)\n---\s*\n", re.DOTALL)
CODE_FENCE_RE = re.compile(r"^```")

PLACEHOLDER_TOKENS = ["{", "<", "invocation_name", "chapter_name", "file_name",
                      "GRIMOIRE_ARCANA", "GRIMOIRE_PATH", "ARCANA_PATH",
                      "Chapter Name", "Title", "Sub-topic", "filename",
                      "related_page", "sub_topic", "related_chapter",
                      "path/to/related", "path/url/system", "Source title"]


def parse_frontmatter_aliases(content):
    """Return list of aliases from frontmatter, or []."""
    m = FRONTMATTER_RE.match(content)
    if not m:
        return []
    block = m.group(1)
    for line in block.splitlines():
        if not line.startswith("aliases:"):
            continue
        value = line.partition(":")[2].strip()
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if not inner:
                return []
            return [s.strip().strip("'\"") for s in inner.split(",")]
    return []


def build_alias_index(root):
    """Map wikilink-body → resolved file path. Body matches stem or any alias."""
    index = {}
    for path in sorted(root.rglob("*.md")):
        rel_parts = path.relative_to(root).parts
        if rel_parts and rel_parts[0] in SKIP_DIRS:
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        # Stem indexing — last writer wins, but warn at validation time.
        index.setdefault(path.stem.lower(), path)
        for alias in parse_frontmatter_aliases(content):
            key = alias.strip().lower()
            if key:
                index.setdefault(key, path)
    return index


def strip_code_blocks(content):
    """Replace fenced code blocks and inline code with whitespace so links inside don't get scanned."""
    result = []
    in_fence = False
    for line in content.splitlines():
        if CODE_FENCE_RE.match(line):
            in_fence = not in_fence
            result.append("")
            continue
        if in_fence:
            result.append("")
            continue
        # Inline code: replace `...` content with empty backticks of same length.
        result.append(re.sub(r"`[^`]*`", lambda m: " " * len(m.group()), line))
    return "\n".join(result)


def resolve_wikilink(target, alias_index):
    """Return resolved Path or None."""
    body = target.split("|", 1)[0].split("#", 1)[0].strip().lower()
    if not body:
        return None
    return alias_index.get(body)


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate internal links and wikilinks")
    parser.add_argument("--grimoire", type=Path, default=_default_root(),
                        help="Grimoire root (default: GRIMOIRE_ARCANA env or rites parent)")
    args = parser.parse_args()
    grimoire_root = args.grimoire.expanduser().resolve()

    errors = 0

    print()
    print("Validating Internal Links and Wikilinks")
    print("==================================")
    print(f"Grimoire root: {grimoire_root}")
    print()

    print("Building wikilink alias index...")
    alias_index = build_alias_index(grimoire_root)
    print(f"  {len(alias_index)} resolvable wikilink targets indexed.")
    print()

    print("Scanning markdown files for broken links and wikilinks...")

    for path in sorted(grimoire_root.rglob("*.md")):
        rel = str(path.relative_to(grimoire_root))

        if path.name in SKIP_FILES:
            continue
        if any(rel.startswith(sd) for sd in SKIP_DIRS):
            continue

        try:
            content = path.read_text(errors="replace")
        except OSError:
            continue
        lines = content.splitlines()
        total = len(lines)
        if total == 0:
            continue

        scanable = strip_code_blocks(content)

        # Standard markdown links
        for link_match in LINK_RE.finditer(scanable):
            link = link_match.group(1)

            if re.match(r"^[a-z]+://", link) or link.startswith("mailto:"):
                continue
            if link.startswith("#"):
                continue
            if any(tok in link for tok in PLACEHOLDER_TOKENS):
                continue

            target_path = link.split("#")[0]
            if not target_path:
                continue

            if target_path.startswith("/"):
                resolved = grimoire_root / target_path.lstrip("/")
            else:
                resolved = (path.parent / target_path).resolve()

            try:
                resolved = resolved.resolve()
            except OSError:
                pass

            if not resolved.exists():
                print(f"  BROKEN  {rel}:")
                print(f"          Link: {link}")
                print(f"          Resolved to: {resolved}")
                errors += 1

        # Wikilinks
        for wl_match in WIKILINK_RE.finditer(scanable):
            target = wl_match.group(1)
            if any(tok in target for tok in PLACEHOLDER_TOKENS):
                continue
            resolved = resolve_wikilink(target, alias_index)
            if resolved is None:
                print(f"  BROKEN  {rel}:")
                print(f"          Wikilink: [[{target}]] (no page or alias matches)")
                errors += 1

    print()

    print("==================================")
    if errors == 0:
        print("Link validation passed (no broken links or wikilinks found)")
        return 0
    else:
        print(f"Link validation failed with {errors} broken link(s)")
        return 1


if __name__ == "__main__":
    sys.exit(main())
