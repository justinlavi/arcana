#!/usr/bin/env python3
"""Extracts semantic data from Arcana for AI analysis.

This rite does NOT try to be intelligent. It simply:
1. Extracts terminology from reference
2. Checks basic pattern violations (hyphenated examples)
3. Reports facts - AI (analyze_semantics invocation) does intelligent analysis

Usage: python3 rites/validate_semantics.py
Exit codes: 0 = no mechanical violations, 1 = pattern violations found
"""

import os
import re
import sys
from pathlib import Path

ARCANA_ROOT = Path(os.environ.get("GRIMOIRE_ARCANA", Path(__file__).resolve().parent.parent))
REFERENCE = ARCANA_ROOT / "docs" / "reference.md"
RESULTS_DIR = ARCANA_ROOT / "rites" / ".artifacts"

SKIP_FILES = {
    "validate_naming.md", "validate_format.md", "validate_semantics.md",
    "script_vs_ai_intelligence.md",
}

SKIP_DIRS = {"invocations/arcana/quality"}

HYPHEN_PATTERN = re.compile(r"chapters/[a-z]+-[a-z]+/|[a-z]+-[a-z]+\.md")


def extract_section(content, header_pattern, end_pattern="^---$"):
    """Extract table rows from a reference section."""
    in_section = False
    rows = []
    for line in content.splitlines():
        if re.search(header_pattern, line):
            in_section = True
            continue
        if in_section and re.search(end_pattern, line):
            break
        if in_section and line.startswith("|") and not line.startswith("| Concept") \
                and not line.startswith("| Role") and not line.startswith("| Deprecated") \
                and not line.startswith("|---"):
            rows.append(line)
    return rows


def main():
    errors = 0

    print()
    print("Extracting Semantic Data (Rite)")
    print("====================================")
    print(f"Arcana root: {ARCANA_ROOT}")
    print(f"Reference: {REFERENCE}")
    print()
    print("Note: This rite extracts data only.")
    print("For intelligent semantic analysis, use: /grm-domain-analyze-semantics")
    print()

    if not REFERENCE.is_file():
        print(f"  ERROR  Reference file not found: {REFERENCE}")
        return 1

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # Extract canonical terminology
    print("Extracting canonical terminology from reference...")
    ref_content = REFERENCE.read_text(errors="replace")

    output_lines = ["=== CANONICAL TERMS (from reference.md) ===", ""]
    output_lines.append("## Core Concepts:")
    output_lines.extend(extract_section(ref_content, r"^## .* Core Concepts"))
    output_lines.append("")
    output_lines.append("## Domain Structure:")
    output_lines.extend(extract_section(ref_content, r"^## .* Domain Structure"))
    output_lines.append("")
    output_lines.append("## People & Roles:")
    output_lines.extend(extract_section(ref_content, r"^## .* People & Roles"))
    output_lines.append("")
    output_lines.append("## Deprecated Terms (should NOT be used):")
    output_lines.extend(extract_section(ref_content, r"^## Deprecated Terminology"))

    output_path = RESULTS_DIR / "canonical_terminology.txt"
    output_path.write_text("\n".join(output_lines) + "\n")
    print(f"  OK    Terminology extracted to: {output_path}")
    print()

    # Mechanical check: hyphenated examples
    print("Checking for mechanical pattern violations...")
    found_hyphens = 0

    for path in sorted(ARCANA_ROOT.rglob("*.md")):
        if path.name in SKIP_FILES:
            continue

        rel = str(path.relative_to(ARCANA_ROOT))
        if any(rel.startswith(sd) for sd in SKIP_DIRS):
            continue

        content = path.read_text(errors="replace")
        for line in content.splitlines():
            if line.lstrip().startswith("#"):
                continue
            if HYPHEN_PATTERN.search(line):
                print(f"  WARN  Hyphenated example: {rel}")
                found_hyphens += 1
                errors += 1
                break

    if found_hyphens == 0:
        print("  OK    No hyphenated examples found")
    print()

    print("====================================")
    print("Data Extraction Complete")
    print()
    print("Extracted data:")
    print(f"  - {output_path}")
    print()
    print(f"Mechanical violations: {errors}")
    print()

    if errors == 0:
        print("No mechanical pattern violations")
        print()
        print("For intelligent semantic analysis:")
        print("   /grm-domain-analyze-semantics")
        print()
        return 0
    else:
        print(f"Found {errors} mechanical pattern violations")
        print("   (Fix these simple pattern issues first)")
        print()
        return 1


if __name__ == "__main__":
    sys.exit(main())
