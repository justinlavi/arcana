#!/usr/bin/env python3
"""Validates that every `/grm-*` skill reference in Arcana resolves to a real skill.

Scans all markdown files in Arcana for slash-command references matching
the namespace prefix (default: `grm-`) and ensures the referenced skill
folder exists under `skills/`. Catches drift like:

  - A doc mentioning `/grm-arcana-foo` after the skill was deleted/renamed.
  - A new skill mentioned in prose before its `skills/` folder is created.

Domain-grimoire skill references (e.g. `/oly-...`) are NOT validated here —
they live in their own grimoire repos. This is an Arcana-internal check.

Usage: python3 rites/validate_skill_refs.py
Exit codes: 0 = all references resolve, 1 = at least one dangling reference
"""

import os
import re
import sys
from pathlib import Path

ARCANA_ROOT = Path(os.environ.get("GRIMOIRE_ARCANA", Path(__file__).resolve().parent.parent))
SKILLS_DIR = ARCANA_ROOT / "skills"

# Arcana's own namespace, declared in arcana/grimoire.json. Hard-coded here
# rather than parsed because validators must run even if the manifest is
# malformed (validate_structure handles that).
ARCANA_NAMESPACE = "grm"

# Match `/grm-<slug>` references. Boundaries: not preceded by another word
# char, must end at a word boundary. Captures the slug (without prefix).
SKILL_REF_RE = re.compile(
    r"(?<![A-Za-z0-9_/-])/" + ARCANA_NAMESPACE + r"-([a-z][a-z0-9-]*)\b"
)

# Tokens that, when they immediately follow the matched slug, indicate a
# wildcard/placeholder rather than a concrete skill reference. Examples:
#   /grm-arcana-validate-*       (wildcard summary)
#   /grm-arcana-validate-<name>  (placeholder for prose)
#   /grm-arcana-validate-{slug}  (variable substitution)
PLACEHOLDER_SUFFIXES = ("-*", "-<", "-{")

# Files that intentionally mention not-yet-existing or hypothetical skill
# names (templates, examples, historical references).
SKIP_FILES = {
    "validate_skill_refs.py",
    "deprecated_terms.txt",
    "CHANGELOG.md",  # historical references (e.g., describing a renamed/retired skill)
}

SKIP_DIRS = {
    "formulae",  # template placeholders
    "skills/arcana-validate-skill-refs",  # the validator's own examples
    "sources",  # imported source artifacts
}


def discover_skill_slugs():
    """Return the set of valid skill slugs (folder names under skills/)."""
    if not SKILLS_DIR.is_dir():
        return set()
    return {
        d.name for d in SKILLS_DIR.iterdir()
        if d.is_dir() and (d / "SKILL.md").is_file()
    }


def scan_for_skill_refs():
    """Yield (file_rel, lineno, full_command, slug) for each /grm-* reference."""
    for path in sorted(ARCANA_ROOT.rglob("*.md")):
        if path.name in SKIP_FILES:
            continue
        rel = str(path.relative_to(ARCANA_ROOT))
        if any(rel.startswith(sd) for sd in SKIP_DIRS):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(content.splitlines(), start=1):
            for match in SKILL_REF_RE.finditer(line):
                # Skip wildcard/placeholder forms — they're prose, not refs.
                tail = line[match.end() : match.end() + 2]
                if any(tail.startswith(s) for s in PLACEHOLDER_SUFFIXES):
                    continue
                full = match.group(0)
                slug = match.group(1)
                yield rel, lineno, full, slug


def main():
    print()
    print("Validate Skill References")
    print("====================================")
    print(f"Arcana root:    {ARCANA_ROOT}")
    print(f"Skills dir:     {SKILLS_DIR}")
    print(f"Namespace:      {ARCANA_NAMESPACE}-")
    print()

    valid_slugs = discover_skill_slugs()
    print(f"Discovered {len(valid_slugs)} valid skill(s) under skills/.")
    print()

    print("Scanning markdown for /grm-* references...")
    dangling = []
    seen_pairs = set()
    for rel, lineno, full, slug in scan_for_skill_refs():
        if slug in valid_slugs:
            continue
        # Deduplicate (file, slug) pairs — one report per file per slug.
        key = (rel, slug)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        dangling.append((rel, lineno, full))
        print(f"  WARN  {rel}:{lineno}  references {full}  (no skills/{slug}/SKILL.md)")

    if not dangling:
        print("  OK    All /grm-* references resolve to existing skills.")
    print()

    print("====================================")
    print(f"Dangling skill references: {len(dangling)}")
    print()

    if not dangling:
        return 0
    print("Either create the missing skill or update the reference.")
    print("If a skill was renamed, update the docs that reference it.")
    print("After adding/removing a skill, also run:")
    print("   python3 rites/sync_docs.py --apply")
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
