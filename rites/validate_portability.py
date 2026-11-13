#!/usr/bin/env python3
"""Validates filesystem portability - no Windows-reserved characters in paths.

On Windows, the characters < > : " | ? * are reserved and cannot appear in
file or directory names. `git checkout` aborts on encounter ("invalid path"),
leaving the working tree partially populated - a state the summon rite cannot
recover from on subsequent attempts. This validator catches the issue before
any Windows consumer attempts to clone the grimoire.

It also rejects Windows reserved basenames (CON, PRN, AUX, NUL, COM1-9, LPT1-9)
and segments that end with `.` or ` ` (Windows trims/rejects those), and two
entries in one directory whose names differ only by case - a tree that
checks out on Linux but cannot be materialized on Windows or macOS.

Usage: python3 rites/validate_portability.py [--grimoire <path>]
Exit codes: 0 = success, 1 = violations found
"""

import argparse
import sys

from _lib import add_grimoire_arg, err, ok, resolve_grimoire_arg, walk_files
from diagnostics import DiagnosticReporter, add_output_format_arg

# Windows-reserved characters in filenames (path separators / and \ excluded
# since they're handled by the OS as separators, not as filename chars).
RESERVED_CHARS = set('<>:"|?*')

# Windows reserved basenames (case-insensitive), with or without extension.
RESERVED_BASENAMES = frozenset({
    "CON", "PRN", "AUX", "NUL",
    *(f"COM{i}" for i in range(1, 10)),
    *(f"LPT{i}" for i in range(1, 10)),
})

# Top-level directories to skip - not part of the working-tree distribution.
SKIP_TOP_LEVEL = {".git", "publish"}


def check_segments(rel_parts):
    """Return a list of (code, description) tuples for the path's segments."""
    issues = []
    for part in rel_parts:
        bad_chars = sorted({c for c in part if c in RESERVED_CHARS})
        if bad_chars:
            issues.append(
                (
                    "PORTABILITY_RESERVED_CHAR",
                    f"segment '{part}' contains Windows-reserved char(s): {''.join(bad_chars)}",
                )
            )
        stem = part.split(".", 1)[0].upper()
        if stem in RESERVED_BASENAMES:
            issues.append(
                (
                    "PORTABILITY_RESERVED_BASENAME",
                    f"segment '{part}' uses Windows-reserved basename '{stem}'",
                )
            )
        if part and part[-1] in ". ":
            issues.append(
                (
                    "PORTABILITY_TRAILING_DOT_SPACE",
                    f"segment '{part}' ends with '.' or ' ' (Windows trims / rejects)",
                )
            )
    return issues


def find_case_collisions(names):
    """Return groups of names in one directory that are equal under casefold()."""
    groups = {}
    for name in names:
        groups.setdefault(name.casefold(), []).append(name)
    return [sorted(group) for group in groups.values() if len(group) > 1]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_grimoire_arg(parser)
    add_output_format_arg(parser)
    args = parser.parse_args()

    root = resolve_grimoire_arg(args.grimoire)
    human = args.format == "human"
    reporter = DiagnosticReporter("validate_portability", root)

    if human:
        print()
        print("Validating Filesystem Portability (Windows-safe paths)")
        print("==================================")
        print(f"Grimoire root: {root}")
        print()

    checked = 0
    children = {}

    for p in walk_files(root):
        rel = p.relative_to(root)
        if rel.parts and rel.parts[0] in SKIP_TOP_LEVEL:
            continue
        checked += 1
        children.setdefault(rel.parent.as_posix(), []).append(rel.name)
        for code, issue in check_segments(rel.parts):
            reporter.error(code, issue, path=rel.as_posix())
            if human:
                err(f"{rel}: {issue}")

    for parent, names in sorted(children.items()):
        for group in find_case_collisions(names):
            issue = (
                f"entries differ only by case: {', '.join(group)} "
                "(cannot coexist on Windows or macOS)"
            )
            reporter.error("PORTABILITY_CASE_COLLISION", issue, path=parent)
            if human:
                err(f"{parent}: {issue}")

    if not human:
        reporter.emit(args.format, checked={"paths": checked})
        return reporter.exit_code()

    print()
    print(f"Paths checked:    {checked}")
    print(f"Violations found: {reporter.error_count()}")
    print()
    print("==================================")
    if reporter.error_count() == 0:
        ok("Portability validation passed")
        return 0
    print(f"Portability validation failed with {reporter.error_count()} violation(s)")
    print()
    print("Windows reserves these filename characters: < > : \" | ? *")
    print("Replace them with portable alternatives, e.g. curly braces for")
    print("template placeholders ({target_app} instead of <target_app>).")
    return 1


if __name__ == "__main__":
    sys.exit(main())
