#!/usr/bin/env python3
"""Validates Arcana semantics: hyphenated path examples in body text.

What this rite checks (mechanical, deterministic):
- Hyphenated path examples — paths like `chapters/example-name/` or
  `file-name.md` written in prose should use snake_case (Arcana convention).

What this rite does NOT do: intelligent semantic analysis (naming quality,
discoverability, organization). For that, use /grm-domain-analyze-semantics.
Filename naming is enforced separately by validate_naming.py.

Usage: python3 rites/validate_semantics.py
Exit codes: 0 = no violations, 1 = violations found
"""

import re
import sys
from pathlib import Path

from _lib import default_arcana_root, ok, warn

ARCANA_ROOT = default_arcana_root()

# Files exempt from scanning. These either *define* the patterns the rite
# checks (and so necessarily mention them) or are docs whose explicit purpose
# is to discuss the patterns as illustrative examples.
SKIP_FILES = {
    "validate_semantics.md",  # describes the rite, names the patterns it scans
    "validate_naming.md",     # documents naming-violation examples
    "script_vs_ai.md",        # demos validator behavior
}

SKIP_DIRS = {
    "invocations/arcana/quality",  # quality docs may discuss historical terms
    "sources",  # imported source artifacts may have hyphens in their original names
}

# Hyphen pattern for the wiki/chapters layer only. sources/ is allowed to contain
# arbitrary filenames (article-name.md, episode-3.md, etc.).
HYPHEN_PATTERN = re.compile(r"chapters/[a-z]+-[a-z]+/|chapters/[^ ]*[a-z]+-[a-z]+\.md")


def scan_markdown_files(root, predicate):
    """Yield (rel_path, line_number, line) for every .md file matching predicate."""
    for path in sorted(root.rglob("*.md")):
        if path.name in SKIP_FILES:
            continue
        rel = str(path.relative_to(root))
        if any(rel.startswith(sd) for sd in SKIP_DIRS):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(content.splitlines(), start=1):
            if predicate(line):
                yield rel, lineno, line
                break  # one report per file is enough


def check_hyphenated_examples():
    """Report any markdown file containing hyphenated path examples in body text."""
    print("Checking for hyphenated path examples...")
    found = 0

    def is_hyphenated_body_line(line):
        if line.lstrip().startswith("#"):
            return False
        return HYPHEN_PATTERN.search(line) is not None

    for rel, lineno, _line in scan_markdown_files(ARCANA_ROOT, is_hyphenated_body_line):
        warn(f"Hyphenated example: {rel}:{lineno}")
        found += 1

    if found == 0:
        ok("No hyphenated examples found")
    print()
    return found


def main():
    print()
    print("Validate Arcana Semantics")
    print("====================================")
    print(f"Arcana root: {ARCANA_ROOT}")
    print()

    hyphen_count = check_hyphenated_examples()

    print("====================================")
    print(f"Hyphenated paths:   {hyphen_count}")
    print()

    if hyphen_count == 0:
        print("Semantic validation passed.")
        print()
        print("For intelligent semantic analysis (naming quality, discoverability):")
        print("   /grm-domain-analyze-semantics")
        print()
        return 0

    print("Semantic validation failed.")
    print("   Convert hyphenated path examples to snake_case.")
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
