#!/usr/bin/env python3
"""Validate text encoding, newline, and mojibake safety.

Arcana and grimoires may use Unicode, but every text file must be UTF-8
without BOM, use LF line endings, and avoid common mojibake artifacts.

Usage: python3 rites/validate_encoding.py [--grimoire <path>]
Exit codes: 0 = success, 1 = violations found
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from _lib import add_grimoire_arg, err, ok, resolve_grimoire_arg
from diagnostics import Diagnostic, DiagnosticReporter, add_output_format_arg

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
ASCII_ARTIFACT_PATTERNS = (
    (
        re.compile(r"\b\d+\?\d+\b"),
        "probable numeric range repair artifact",
    ),
)


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


def check_file(path: Path, root: Path) -> list[Diagnostic]:
    rel = str(path.relative_to(root)).replace("\\", "/")
    reporter = DiagnosticReporter("validate_encoding", root)
    try:
        data = path.read_bytes()
    except OSError as exc:
        reporter.error("ENCODING_READ_ERROR", f"could not read ({exc})", path=rel)
        return reporter.diagnostics

    if data.startswith(b"\xef\xbb\xbf"):
        reporter.error("ENCODING_BOM", "UTF-8 BOM is not allowed", path=rel)
    if b"\r" in data:
        reporter.error("ENCODING_CRLF", "CRLF/CR line endings found; use LF", path=rel)

    try:
        text = data.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        reporter.error("ENCODING_UTF8", f"not valid UTF-8 ({exc})", path=rel)
        return reporter.diagnostics

    for marker in MOJIBAKE_MARKERS:
        idx = text.find(marker)
        if idx != -1:
            reporter.error(
                "ENCODING_MOJIBAKE",
                f"probable mojibake marker {marker!r}",
                path=rel,
                line=line_for_offset(text, idx),
            )
            break

    for marker in ASCII_ARTIFACTS:
        idx = text.find(marker)
        if idx != -1:
            reporter.error(
                "ENCODING_REPAIR_ARTIFACT",
                f"probable mojibake repair artifact {marker!r}",
                path=rel,
                line=line_for_offset(text, idx),
            )
            break

    for pattern, label in ASCII_ARTIFACT_PATTERNS:
        match = pattern.search(text)
        if match:
            reporter.error(
                "ENCODING_REPAIR_ARTIFACT",
                f"{label} {match.group()!r}",
                path=rel,
                line=line_for_offset(text, match.start()),
            )
            break

    return reporter.diagnostics


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    add_grimoire_arg(parser)
    add_output_format_arg(parser)
    args = parser.parse_args()

    root = resolve_grimoire_arg(args.grimoire)
    human = args.format == "human"
    reporter = DiagnosticReporter("validate_encoding", root)

    if human:
        print()
        print("Validating Encoding and Newlines")
        print("================================")
        print(f"Root: {root}")
        print()

    checked = 0
    for path in iter_text_files(root):
        checked += 1
        reporter.diagnostics.extend(check_file(path, root))

    if not human:
        reporter.emit(args.format, checked={"files": checked})
        return reporter.exit_code()

    for diagnostic in reporter.diagnostics:
        location = diagnostic.path
        if diagnostic.line:
            location = f"{location}:{diagnostic.line}"
        err(f"{location}: {diagnostic.message}")

    print()
    print(f"Files checked:     {checked}")
    print(f"Violations found:  {reporter.error_count()}")
    print()
    print("================================")
    if reporter.error_count():
        print("Encoding validation failed")
        print()
        print("Use UTF-8 without BOM and LF line endings. Unicode is allowed,")
        print("but mojibake and repair artifacts are not.")
        return 1

    ok("Encoding validation passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
