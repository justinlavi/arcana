#!/usr/bin/env python3
"""Validates internal links and references in markdown files.

Usage: python3 rites/validate_links.py
Exit codes: 0 = success, 1 = broken links found
"""

import os
import re
import sys
from pathlib import Path

ARCANA_ROOT = Path(os.environ.get("GRIMOIRE_ARCANA", Path(__file__).resolve().parent.parent))

SKIP_DIRS = {
    "invocations/arcana/validators",
    "invocations/arcana/quality",
}

SKIP_FILES = {"operating_model.md"}

LINK_RE = re.compile(r"\]\(([^)]+)\)")

PLACEHOLDER_TOKENS = ["{", "invocation_name", "chapter_name", "file_name",
                      "GRIMOIRE_ARCANA", "GRIMOIRE_PATH", "ARCANA_PATH"]


def main():
    errors = 0

    print()
    print("Validating Internal Links")
    print("==================================")
    print(f"Arcana root: {ARCANA_ROOT}")
    print()

    print("Scanning markdown files for broken links...")

    for path in sorted(ARCANA_ROOT.rglob("*.md")):
        rel = str(path.relative_to(ARCANA_ROOT))

        if path.name in SKIP_FILES:
            continue
        if any(rel.startswith(sd) for sd in SKIP_DIRS):
            continue

        content = path.read_text(errors="replace")
        lines = content.splitlines()
        total = len(lines)
        if total == 0:
            continue

        code_fence_count = sum(1 for l in lines if l.strip().startswith("```"))
        if total > 0 and (code_fence_count * 100 // total) > 30:
            continue

        for link_match in LINK_RE.finditer(content):
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
                resolved = ARCANA_ROOT / target_path.lstrip("/")
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

    print()

    print("==================================")
    if errors == 0:
        print("Link validation passed (no broken links found)")
        return 0
    else:
        print(f"Link validation failed with {errors} broken links")
        return 1


if __name__ == "__main__":
    sys.exit(main())
