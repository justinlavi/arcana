#!/usr/bin/env python3
"""Validates Markdown, invocation, formula, and hub format compliance.

Hub convention (v2): For any folder F that acts as a router, the hub file is
F/<basename(F)>.md. Hubs are validated as thin routers (< 200 lines, exists);
non-hub invocation files are validated against the invocation schema.

Usage:
    python3 rites/validate_format.py
    python3 rites/validate_format.py --grimoire ~/grimoires/cooking-grimoire

Exit codes: 0 = success, 1 = format violations found
"""

import argparse
import re
import sys
from pathlib import Path

from _lib import add_grimoire_arg, ok, resolve_grimoire_arg, warn
from diagnostics import DiagnosticReporter, add_output_format_arg

ROOT = None

INVOCATION_REQUIRED_SECTIONS = [
    (r"^# ", "Title heading (# ...)"),
    (r"^## .*Purpose", "## Purpose section"),
    (r"^## .*Invocation", "## Invocation section"),
]

HUB_MAX_LINES = 200
SHORT_TABLE_DELIMITER_RE = re.compile(
    r"^\|?\s*:?-{1,2}:?\s*(\|\s*:?-{1,2}:?\s*)+\|?\s*$"
)
FENCE_RE = re.compile(r"^\s*(```|~~~)")
BACKTICK_TREE_BRANCH_RE = re.compile(r"^\s*(?:\|\s*)*`--\s+\S")


def is_hub(path):
    """A hub file is named after its parent folder: <folder>/<folder>.md."""
    return path.stem == path.parent.name


SKIP_DIRS = {"sources"}


def under_skip_dir(path):
    rel = path.relative_to(ROOT)
    return rel.parts and rel.parts[0] in SKIP_DIRS


def markdown_files(root):
    """Yield Markdown files that should be validated."""
    for path in sorted(root.rglob("*.md")):
        if not under_skip_dir(path):
            yield path


def short_table_delimiter_rows(content):
    """Return lines where a Markdown table delimiter uses fewer than 3 hyphens."""
    in_fence = False
    fence = None

    for line_number, line in enumerate(content.splitlines(), 1):
        fence_match = FENCE_RE.match(line)
        if fence_match:
            marker = fence_match.group(1)
            if not in_fence:
                in_fence = True
                fence = marker
            elif marker == fence:
                in_fence = False
                fence = None
            continue

        if not in_fence and SHORT_TABLE_DELIMITER_RE.match(line):
            yield line_number, line


def unclosed_code_fences(content):
    """Return the opening line if a fenced code block is never closed."""
    in_fence = False
    fence = None
    start_line = None

    for line_number, line in enumerate(content.splitlines(), 1):
        fence_match = FENCE_RE.match(line)
        if not fence_match:
            continue

        marker = fence_match.group(1)
        if not in_fence:
            in_fence = True
            fence = marker
            start_line = line_number
        elif marker == fence:
            in_fence = False
            fence = None
            start_line = None

    if in_fence:
        return start_line, fence
    return None


def backtick_tree_branches(content):
    """Return pipe-tree lines that use backtick branch markers."""
    for line_number, line in enumerate(content.splitlines(), 1):
        if BACKTICK_TREE_BRANCH_RE.match(line):
            yield line_number, line


def main():
    global ROOT

    parser = argparse.ArgumentParser(description=__doc__)
    add_grimoire_arg(parser)
    add_output_format_arg(parser)
    args = parser.parse_args()

    ROOT = resolve_grimoire_arg(args.grimoire)
    human = args.format == "human"
    reporter = DiagnosticReporter("validate_format", ROOT)

    if human:
        print()
        print("Validating Markdown, Invocation, Formula, and Hub Format")
        print("==================================")
        print(f"Root: {ROOT}")
        print()

    invocations_dir = ROOT / "invocations"

    # 1. Invocation files (non-hub) must follow the invocation schema.
    if human:
        print("Checking invocation format compliance...")
    inv_violations = 0

    # Pattern templates and shared fragments aren't standalone invocations.
    INVOCATION_EXEMPT = {
        "base_invocation.md",
        "grimoire_directory_guard.md",
        "subagent_lanes.md",
    }

    if invocations_dir.is_dir():
        for path in sorted(invocations_dir.rglob("*.md")):
            if path.name in INVOCATION_EXEMPT:
                continue
            if is_hub(path):
                continue

            content = path.read_text(errors="replace")
            file_errors = 0

            for pattern, label in INVOCATION_REQUIRED_SECTIONS:
                if not re.search(pattern, content, re.MULTILINE):
                    if human and file_errors == 0:
                        warn(f"Format violations in: {path.relative_to(ROOT)}")
                    reporter.error(
                        "FORMAT_MISSING_INVOCATION_SECTION",
                        f"missing section: {label}",
                        path=path,
                    )
                    if human:
                        print(f"          Missing section: {label}")
                    file_errors += 1
                    inv_violations += 1

    if human and inv_violations == 0:
        ok("All invocations have required sections")
    if human:
        print()

    # 2. Hub files must be thin routers.
    if human:
        print(f"Checking hub files are thin routers (< {HUB_MAX_LINES} lines)...")
    hub_violations = 0

    if invocations_dir.is_dir():
        for path in sorted(invocations_dir.rglob("*.md")):
            if not is_hub(path):
                continue
            lines = len(path.read_text(errors="replace").splitlines())
            if lines > HUB_MAX_LINES:
                reporter.error(
                    "FORMAT_HUB_TOO_LONG",
                    f"hub too long ({lines} lines, should be < {HUB_MAX_LINES})",
                    path=path,
                )
                if human:
                    warn(f"Hub too long ({lines} lines, should be < {HUB_MAX_LINES}): "
                         f"{path.relative_to(ROOT)}")
                hub_violations += 1

    if human and hub_violations == 0:
        ok("All hub files are appropriately sized")
    if human:
        print()

    # 3. Formulae must have a title heading.
    if human:
        print("Checking formula format...")
    formula_violations = 0

    formulae_dir = ROOT / "formulae"
    if formulae_dir.is_dir():
        for path in sorted(formulae_dir.rglob("*.md")):
            content = path.read_text(errors="replace")
            if not re.search(r"^# ", content, re.MULTILINE):
                reporter.error(
                    "FORMAT_FORMULA_MISSING_TITLE",
                    "formula missing title heading",
                    path=path,
                )
                if human:
                    warn(f"Formula missing title heading: {path.relative_to(ROOT)}")
                formula_violations += 1

    if human and formula_violations == 0:
        ok("All formulae have proper format")
    if human:
        print()

    # 4. Markdown table delimiter rows must use 3+ hyphens per cell.
    if human:
        print("Checking markdown table delimiter rows...")
    table_violations = 0

    for path in markdown_files(ROOT):
        content = path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in short_table_delimiter_rows(content):
            if human and table_violations == 0:
                print()
            reporter.error(
                "FORMAT_SHORT_TABLE_DELIMITER",
                f"short table delimiter row: `{line}`",
                path=path,
                line=line_number,
            )
            if human:
                warn(
                    f"Short table delimiter row: {path.relative_to(ROOT)}:"
                    f"{line_number} `{line}`"
                )
            table_violations += 1

    if human and table_violations == 0:
        ok("All markdown table delimiter rows use 3+ hyphens")
    if human:
        print()

    # 5. Fenced code blocks must close.
    if human:
        print("Checking fenced code blocks...")
    fence_violations = 0

    for path in markdown_files(ROOT):
        content = path.read_text(encoding="utf-8", errors="replace")
        violation = unclosed_code_fences(content)
        if violation:
            line_number, fence = violation
            reporter.error(
                "FORMAT_UNCLOSED_CODE_FENCE",
                f"unclosed code fence `{fence}`",
                path=path,
                line=line_number,
            )
            if human:
                warn(
                    f"Unclosed code fence: {path.relative_to(ROOT)}:"
                    f"{line_number} `{fence}`"
                )
            fence_violations += 1

    if human and fence_violations == 0:
        ok("All fenced code blocks are closed")
    if human:
        print()

    # 6. Directory tree examples use pipe branch markers, not backticks.
    if human:
        print("Checking Markdown tree branch markers...")
    tree_violations = 0

    for path in markdown_files(ROOT):
        content = path.read_text(encoding="utf-8", errors="replace")
        for line_number, line in backtick_tree_branches(content):
            reporter.error(
                "FORMAT_TREE_BACKTICK_MARKER",
                f"backtick tree branch marker: `{line}`",
                path=path,
                line=line_number,
            )
            if human:
                warn(
                    f"Backtick tree branch marker: {path.relative_to(ROOT)}:"
                    f"{line_number} `{line}`"
                )
            tree_violations += 1

    if human and tree_violations == 0:
        ok("All Markdown tree examples use pipe branch markers")
    if human:
        print()

    checked = {
        "invocation_violations": inv_violations,
        "hub_violations": hub_violations,
        "formula_violations": formula_violations,
        "table_violations": table_violations,
        "fence_violations": fence_violations,
        "tree_violations": tree_violations,
    }
    if not human:
        reporter.emit(args.format, checked=checked)
        return reporter.exit_code()

    print("==================================")
    if reporter.error_count() == 0:
        print("Format validation passed")
        return 0
    else:
        print(f"Format validation failed with {reporter.error_count()} issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
