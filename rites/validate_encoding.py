#!/usr/bin/env python3
"""Validate text encoding, newline, and mojibake safety.

Arcana and grimoires may use Unicode, but every text file must be UTF-8
without BOM, use LF line endings, and avoid common mojibake artifacts.

Usage: python3 rites/validate_encoding.py [--grimoire <path>]
Exit codes: 0 = success, 1 = violations found
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _lib import add_grimoire_arg, err, ok, resolve_grimoire_arg

TEXT_SUFFIXES = {
    ".cfg",
    ".css",
    ".csv",
    ".gitattributes",
    ".gitignore",
    ".html",
    ".ini",
    ".js",
    ".json",
    ".md",
    ".py",
    ".sh",
    ".toml",
    ".ts",
    ".txt",
    ".yaml",
    ".yml",
}
TEXT_NAMES = {
    ".editorconfig",
    ".gitattributes",
    ".gitignore",
    "AGENTS.md",
    "CLAUDE.md",
    "LICENSE",
    "VERSION",
}
SKIP_DIRS = {".git", ".mypy_cache", ".pytest_cache", "__pycache__", ".artifacts"}
MOJIBAKE_MARKERS = ("\u00c3", "\u00c2", "\u00e2", "\ufffd")
ASCII_ARTIFACTS = ("A" + "a" + ",a", "A" + ",a", " a" + "' ")


def is_text_candidate(path: Path) -> bool:
    return path.name in TEXT_NAMES or path.suffix.lower() in TEXT_SUFFIXES


def iter_text_files(root: Path):
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in SKIP_DIRS for part in rel_parts):
            continue
        if is_text_candidate(path):
            yield path


def line_for_offset(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def check_file(path: Path, root: Path) -> list[str]:
    rel = str(path.relative_to(root)).replace("\\", "/")
    try:
        data = path.read_bytes()
    except OSError as exc:
        return [f"{rel}: could not read ({exc})"]

    violations = []
    if data.startswith(b"\xef\xbb\xbf"):
        violations.append(f"{rel}: UTF-8 BOM is not allowed")
    if b"\r" in data:
        violations.append(f"{rel}: CRLF/CR line endings found; use LF")

    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        return [f"{rel}: not valid UTF-8 ({exc})"]

    for marker in MOJIBAKE_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            violations.append(
                f"{rel}:{line_for_offset(text, idx)}: probable mojibake marker {marker!r}"
            )
            break

    for marker in ASCII_ARTIFACTS:
        idx = text.find(marker)
        if idx != -1:
            violations.append(
                f"{rel}:{line_for_offset(text, idx)}: probable mojibake repair artifact {marker!r}"
            )
            break

    return violations


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_grimoire_arg(parser)
    args = parser.parse_args()

    root = resolve_grimoire_arg(args.grimoire)

    print()
    print("Validating Encoding and Newlines")
    print("================================")
    print(f"Root: {root}")
    print()

    violations = []
    checked = 0
    for path in iter_text_files(root):
        checked += 1
        violations.extend(check_file(path, root))

    for violation in violations:
        err(violation)

    print()
    print(f"Files checked:     {checked}")
    print(f"Violations found:  {len(violations)}")
    print()
    print("================================")
    if violations:
        print("Encoding validation failed")
        print()
        print("Use UTF-8 without BOM and LF line endings. Unicode is allowed,")
        print("but mojibake and repair artifacts are not.")
        return 1

    ok("Encoding validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
