#!/usr/bin/env python3
"""Validates Arcana semantics: deprecated terminology + naming patterns.

What this rite checks (mechanical, deterministic):
1. Deprecated terms — any markdown file containing a term from
   `rites/data/deprecated_terms.txt` is reported as a violation.
2. Hyphenated path examples — paths like `chapters/example-name/` or
   `file-name.md` should use snake_case.

What this rite does NOT do: intelligent semantic analysis (naming quality,
discoverability, organization). For that, use /grm-domain-analyze-semantics.

Usage: python3 rites/validate_semantics.py
Exit codes: 0 = no violations, 1 = violations found
"""

import os
import re
import sys
from pathlib import Path

ARCANA_ROOT = Path(os.environ.get("GRIMOIRE_ARCANA", Path(__file__).resolve().parent.parent))
DEPRECATED_TERMS_FILE = ARCANA_ROOT / "rites" / "data" / "deprecated_terms.txt"

# Files exempt from scanning. These either *define* the patterns the rite
# checks (and so necessarily mention them) or are docs whose explicit purpose
# is to discuss the patterns as illustrative examples.
SKIP_FILES = {
    "validate_semantics.md",  # describes the rite, names the patterns it scans
    "deprecated_terms.txt",   # the data file
    "validate_naming.md",     # documents naming-violation examples
    "script_vs_ai.md",        # demos validator behavior, quotes AI naming a deprecated term
}

SKIP_DIRS = {
    "invocations/arcana/quality",  # quality docs may discuss historical terms
}

HYPHEN_PATTERN = re.compile(r"chapters/[a-z]+-[a-z]+/|[a-z]+-[a-z]+\.md")


def load_deprecated_terms():
    """Read deprecated terms from the data file, skipping comments and blanks."""
    if not DEPRECATED_TERMS_FILE.is_file():
        return []
    terms = []
    for line in DEPRECATED_TERMS_FILE.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        terms.append(line)
    return terms


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


def check_deprecated_terms(terms):
    """Report any markdown file containing a deprecated term."""
    if not terms:
        return 0

    # Build a single regex with word boundaries for whole-term matching.
    pattern = re.compile(
        r"\b(" + "|".join(re.escape(t) for t in terms) + r")\b"
    )

    print("Checking for deprecated terminology...")
    found = 0
    for rel, lineno, line in scan_markdown_files(
        ARCANA_ROOT, lambda l: pattern.search(l) is not None
    ):
        match = pattern.search(line)
        term = match.group(0) if match else "?"
        print(f"  WARN  Deprecated term '{term}': {rel}:{lineno}")
        found += 1

    if found == 0:
        print("  OK    No deprecated terms found")
    print()
    return found


def check_hyphenated_examples():
    """Report any markdown file containing hyphenated path examples in body text."""
    print("Checking for hyphenated path examples...")
    found = 0

    def is_hyphenated_body_line(line):
        if line.lstrip().startswith("#"):
            return False
        return HYPHEN_PATTERN.search(line) is not None

    for rel, lineno, _line in scan_markdown_files(ARCANA_ROOT, is_hyphenated_body_line):
        print(f"  WARN  Hyphenated example: {rel}:{lineno}")
        found += 1

    if found == 0:
        print("  OK    No hyphenated examples found")
    print()
    return found


def main():
    print()
    print("Validate Arcana Semantics")
    print("====================================")
    print(f"Arcana root:        {ARCANA_ROOT}")
    print(f"Deprecated terms:   {DEPRECATED_TERMS_FILE}")
    print()

    terms = load_deprecated_terms()
    if terms:
        print(f"Loaded {len(terms)} deprecated term(s) for scanning.")
    else:
        print("WARN: deprecated terms file missing or empty — skipping that check.")
    print()

    deprecated_count = check_deprecated_terms(terms)
    hyphen_count = check_hyphenated_examples()

    total = deprecated_count + hyphen_count
    print("====================================")
    print(f"Deprecated terms:   {deprecated_count}")
    print(f"Hyphenated paths:   {hyphen_count}")
    print(f"Total violations:   {total}")
    print()

    if total == 0:
        print("Semantic validation passed.")
        print()
        print("For intelligent semantic analysis (naming quality, discoverability):")
        print("   /grm-domain-analyze-semantics")
        print()
        return 0

    print("Semantic validation failed.")
    print("   Replace deprecated terms with their canonical equivalents and")
    print("   convert hyphenated examples to snake_case.")
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
