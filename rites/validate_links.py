#!/usr/bin/env python3
"""Validates internal links and wikilinks in markdown files.

Resolves two link forms:

  1. Standard markdown links: `[text](path/to/file.md)` - relative or root-anchored.
  2. Wikilinks: `[[path/to/page|display text]]` - resolved only as a
     repository-root relative path, with `.md` optional.

Warns when wikilink display text repeats ancestor context instead of matching
the target filename stem. The path carries location; the label should name the
target page.

Usage: python3 rites/validate_links.py
Exit codes: 0 = success, 1 = broken links found
"""

import re
import sys
from pathlib import Path

from _lib import (
    LINK_RE,
    WIKILINK_RE,
    add_grimoire_arg,
    resolve_grimoire_arg,
    resolve_wikilink_path,
    strip_code_blocks,
    wikilink_target_body,
)
from diagnostics import DiagnosticReporter, add_output_format_arg

SKIP_DIRS = {
    "invocations/arcana/validators",
    "invocations/arcana/quality",
    "sources",
    "inbox",
    "tests",
}

SKIP_FILES = {"operating_model.md"}

PLACEHOLDER_TOKENS = ["{", "<", "invocation_name", "chapter_name", "file_name",
                      "ARCANA_HOME", "GRIMOIRE_PATH", "ARCANA_PATH",
                      "Chapter Name", "Title", "Sub-topic", "filename",
                      "related_page", "sub_topic", "related_chapter",
                      "path/to/related", "path/url/system", "Source title"]


def resolve_wikilink(target, root):
    """Return resolved Path or None."""
    body_raw = wikilink_target_body(target)
    return resolve_wikilink_path(body_raw, root)


def wikilink_display_text(target):
    """Return display text after `|`, or empty string if no display is present."""
    if "|" not in target:
        return ""
    return target.split("|", 1)[1].strip()


def label_key(text):
    """Normalize a filename stem or display label for comparison."""
    text = text.replace("_", " ").replace("-", " ")
    text = re.sub(r"\s+", " ", text)
    return text.strip().lower()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate internal links and wikilinks")
    add_grimoire_arg(parser)
    add_output_format_arg(parser)
    args = parser.parse_args()
    grimoire_root = resolve_grimoire_arg(args.grimoire)
    human = args.format == "human"
    reporter = DiagnosticReporter("validate_links", grimoire_root)

    files_checked = 0

    if human:
        print()
        print("Validating Internal Links and Wikilinks")
        print("==================================")
        print(f"Grimoire root: {grimoire_root}")
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
        files_checked += 1

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
                reporter.error(
                    "LINK_MARKDOWN_BROKEN",
                    f"markdown link does not resolve: {link}",
                    path=rel,
                    hint=f"Resolved to: {resolved}",
                )
                if human:
                    print(f"  BROKEN  {rel}:")
                    print(f"          Link: {link}")
                    print(f"          Resolved to: {resolved}")

        # Wikilinks
        for wl_match in WIKILINK_RE.finditer(scanable):
            target = wl_match.group(1)
            if any(tok in target for tok in PLACEHOLDER_TOKENS):
                continue
            resolved = resolve_wikilink(target, grimoire_root)
            if resolved is None:
                reporter.error(
                    "LINK_WIKILINK_BROKEN",
                    f"wikilink does not resolve as a repository path: [[{target}]]",
                    path=rel,
                    hint="Use a full-path wikilink target relative to the grimoire root.",
                    docs_reference="docs/obsidian.md",
                )
                if human:
                    print(f"  BROKEN  {rel}:")
                    print(f"          Wikilink: [[{target}]] (must resolve as a repository path; aliases and filename-only targets are invalid)")
                continue

            display = wikilink_display_text(target)
            if display and label_key(display) != label_key(resolved.stem):
                expected = resolved.stem.replace("_", " ").replace("-", " ")
                reporter.warning(
                    "LINK_LABEL_VERBOSE",
                    f"display label should be target filename only: \"{expected}\"",
                    path=rel,
                    hint=f"Wikilink: [[{target}]]",
                    docs_reference="docs/obsidian.md",
                )
                if human:
                    print(f"  WARN    {rel}:")
                    print(f"          Wikilink: [[{target}]]")
                    print(f"          Display label should be target filename only: \"{expected}\"")

    checked = {"files": files_checked}
    if not human:
        reporter.emit(args.format, checked=checked)
        return reporter.exit_code()

    print()
    print("==================================")
    if reporter.error_count() == 0:
        print("Link validation passed (no broken links or wikilinks found)")
        if reporter.warning_count():
            print(f"Link label warnings: {reporter.warning_count()}")
        return 0
    else:
        print(f"Link validation failed with {reporter.error_count()} broken link(s)")
        if reporter.warning_count():
            print(f"Link label warnings: {reporter.warning_count()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
