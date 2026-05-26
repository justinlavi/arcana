#!/usr/bin/env python3
"""Validates internal links with layer-aware Markdown/wikilink policy.

Resolves two link forms:

  1. Standard Markdown links: `[text](path/to/file.md)` - required in
     public documentation such as README files and docs/.
  2. Wikilinks: `[[path/to/page|display text]]` - required in vault and
     AI-routing surfaces, resolved as repository-root relative paths.

External URLs, same-page anchors, and non-Markdown local artifacts use
standard Markdown links in every layer.

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
    "sources",
    "inbox",
    "tests",
}

SKIP_FILES = set()

PUBLIC_DOC_DIRS = {"docs"}
PUBLIC_DOC_FILENAMES = {"README.md", "CONTRIBUTING.md", "CHANGELOG.md"}

PLACEHOLDER_TOKENS = ["{", "<", "invocation_name", "chapter_name", "file_name",
                      "ARCANA_HOME", "GRIMOIRE_PATH", "ARCANA_PATH",
                      "Chapter Name", "Title", "Sub-topic", "filename",
                      "related_page", "sub_topic", "related_chapter",
                      "path/to/related", "path/url/system", "Source title"]

# Legacy placeholder tokens that have been renamed. Any occurrence in grimoire
# content is flagged so /grm-improve sweeps catch terminology drift instead of
# relying on LLM judgment alone. Format: { legacy_token: current_token }.
DEPRECATED_TOKENS = {
    "GRIMOIRE_ARCANA": "ARCANA_HOME",
}


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


def rel_posix(path, root):
    """Return a repository-root relative path using POSIX separators."""
    return path.relative_to(root).as_posix()


def public_document(path, root):
    """Return True when a Markdown file is meant to render portably on Git hosts."""
    rel = path.relative_to(root)
    if path.name in PUBLIC_DOC_FILENAMES:
        return True
    return bool(rel.parts and rel.parts[0] in PUBLIC_DOC_DIRS)


def resolve_markdown_link(target_path, source_path, root):
    """Resolve a standard Markdown link target relative to its source page."""
    if target_path.startswith("/"):
        resolved = root / target_path.lstrip("/")
    else:
        resolved = (source_path.parent / target_path).resolve()

    try:
        return resolved.resolve()
    except OSError:
        return resolved


def markdown_page_reference(target_path, resolved):
    """Return True when a standard Markdown link points at an internal page."""
    normalized = target_path.replace("\\", "/").rstrip("/")
    if normalized.endswith(".md"):
        return True
    if resolved.is_file() and resolved.suffix == ".md":
        return True
    if resolved.is_dir() and (resolved / "README.md").is_file():
        return True
    if not Path(normalized).suffix and resolved.with_suffix(".md").is_file():
        return True
    return False


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Validate internal links with layer-aware style rules")
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

        print("Scanning markdown files for broken links and layer-specific link styles...")

    for path in sorted(grimoire_root.rglob("*.md")):
        rel = rel_posix(path, grimoire_root)

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
        public_page = public_document(path, grimoire_root)

        # Deprecated placeholder sweep (covers backticked references, link text,
        # and prose mentions; runs before per-link checks so it catches uses
        # outside of link syntax too). Skipped for append-only history files
        # where legitimate historical entries reference legacy terminology.
        if path.name not in {"log.md", "CHANGELOG.md"}:
            for legacy, current in DEPRECATED_TOKENS.items():
                for m in re.finditer(re.escape(legacy), content):
                    line_number = content.count("\n", 0, m.start()) + 1
                    reporter.error(
                        "LINK_DEPRECATED_PLACEHOLDER",
                        f"deprecated placeholder token: {legacy}",
                        path=rel,
                        line=line_number,
                        hint=f"Use {current} instead.",
                    )
                    if human:
                        print(f"  STYLE   {rel}:{line_number}:")
                        print(f"          Deprecated placeholder: {legacy} -> {current}")

        # Standard markdown links
        for link_match in LINK_RE.finditer(scanable):
            link = link_match.group(1)
            line_number = scanable.count("\n", 0, link_match.start()) + 1

            if re.match(r"^[a-z]+://", link) or link.startswith("mailto:"):
                continue
            if link.startswith("#"):
                continue
            if any(tok in link for tok in PLACEHOLDER_TOKENS):
                continue

            target_path = link.split("#")[0]
            if not target_path:
                continue

            resolved = resolve_markdown_link(target_path, path, grimoire_root)
            try:
                resolved.relative_to(grimoire_root)
                internal = True
            except ValueError:
                internal = False

            if internal and markdown_page_reference(target_path, resolved) and not public_page:
                reporter.error(
                    "LINK_MARKDOWN_INTERNAL",
                    f"vault/AI surface uses a markdown link instead of a wikilink: {link}",
                    path=rel,
                    line=line_number,
                    hint="Use a repository-root relative wikilink, e.g. [[path/to/page|page]].",
                    docs_reference="docs/obsidian.md",
                )
                if human:
                    print(f"  STYLE   {rel}:{line_number}:")
                    print(f"          Markdown page link: {link}")
                    print("          Use a full-path wikilink in vault and AI-routing surfaces.")

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
            line_number = scanable.count("\n", 0, wl_match.start()) + 1
            if any(tok in target for tok in PLACEHOLDER_TOKENS):
                continue
            resolved = resolve_wikilink(target, grimoire_root)
            if public_page:
                reporter.error(
                    "LINK_WIKILINK_PUBLIC_DOC",
                    f"public documentation uses a wikilink instead of a Markdown link: [[{target}]]",
                    path=rel,
                    line=line_number,
                    hint="Use a relative Markdown link so README/docs pages remain clickable on Git hosts.",
                    docs_reference="docs/operating_model.md",
                )
                if human:
                    print(f"  STYLE   {rel}:{line_number}:")
                    print(f"          Public-doc wikilink: [[{target}]]")
                    print("          Use a relative Markdown link for public documentation.")
                continue
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
        print("Link validation passed (no broken links or layer-style violations found)")
        if reporter.warning_count():
            print(f"Link label warnings: {reporter.warning_count()}")
        return 0
    else:
        print(f"Link validation failed with {reporter.error_count()} error(s)")
        if reporter.warning_count():
            print(f"Link label warnings: {reporter.warning_count()}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
