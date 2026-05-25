#!/usr/bin/env python3
"""Validates that every Arcana-shipped skill reference resolves to a real skill.

Scans all markdown files in Arcana for slash-command references matching
Arcana's declared command-family prefixes (for example `arc-` and `grm-`) and
ensures each reference resolves to a source `SKILL.md`. Catches drift like:

 - A doc mentioning `/grm-foo` after the skill was deleted/renamed.
 - A new skill mentioned in prose before its `skills/` folder is created.

Grimoire skill references (e.g. `/jpn-...`) are NOT validated here;
they live in their own grimoire repos. This is an Arcana-internal check.

Usage: python3 rites/validate_skill_refs.py
Exit codes: 0 = all references resolve, 1 = at least one dangling reference
"""

import json
import re
import sys
from pathlib import Path

from _lib import default_arcana_root, ok, warn
from diagnostics import DiagnosticReporter, add_output_format_arg

ARCANA_ROOT = default_arcana_root()
SKILLS_DIR = ARCANA_ROOT / "skills"
ARCANA_MANIFEST = ARCANA_ROOT / "arcana.json"
SKILL_PREFIX_PLACEHOLDER = "{{SKILL_PREFIX}}"

# Match slash-command references for Arcana-shipped command-family prefixes.
SKILL_REF_RE = re.compile(r"(?<![A-Za-z0-9_/-])/([a-z][a-z0-9]*)-([a-z][a-z0-9-]*)\b")

# Tokens that, when they immediately follow the matched slug, indicate a
# wildcard/placeholder rather than a concrete skill reference. Examples:
#   /arc-validate-*       (wildcard summary)
#   /arc-validate-<name>         (placeholder for prose)
#   /grm-validate-{slug}         (variable substitution)
PLACEHOLDER_SUFFIXES = ("-*", "-<", "-{")

# Files that intentionally mention not-yet-existing or hypothetical skill
# names (templates, examples, historical references).
SKIP_FILES = {
    "validate_skill_refs.py",
    "CHANGELOG.md",  # historical references (e.g., describing a renamed/retired skill)
}

SKIP_DIRS = {
    "formulae",  # template placeholders
    "skills/arcana/validate-skill-refs",  # the validator's own examples
    "sources",  # imported source artifacts
}


def read_frontmatter_name(skill_file):
    content = skill_file.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"(?m)^name:\s*(.+)$", content)
    return match.group(1).strip() if match else ""


def load_skill_families(reporter, human):
    """Return Arcana command-family definitions from arcana.json."""
    try:
        metadata = json.loads(ARCANA_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        reporter.error("SKILL_REFS_MANIFEST_READ", f"could not read arcana.json: {exc}", path="arcana.json")
        if human:
            warn(f"Could not read arcana.json: {exc}")
        return []

    default_prefix = metadata.get("skill_prefix", "arc")
    raw_families = metadata.get("skill_families", {})
    if not isinstance(raw_families, dict):
        return []

    families = []
    for name, config in raw_families.items():
        if not isinstance(config, dict):
            continue
        families.append({
            "name": name,
            "skill_prefix": config.get("skill_prefix", default_prefix),
            "path": ARCANA_ROOT / config.get("path", ""),
        })
    return families


def discover_skill_commands(reporter, human):
    """Return the set of valid slash commands shipped by Arcana."""
    commands = set()
    prefixes = set()
    for family in load_skill_families(reporter, human):
        prefixes.add(family["skill_prefix"])
        family_dir = family["path"]
        if not family_dir.is_dir():
            continue
        for skill_file in sorted(family_dir.glob("*/SKILL.md")):
            templated_name = read_frontmatter_name(skill_file)
            if not templated_name:
                continue
            commands.add(
                "/" + templated_name.replace(
                    SKILL_PREFIX_PLACEHOLDER, family["skill_prefix"]
                )
            )
    return commands, prefixes


def scan_for_skill_refs(prefixes):
    """Yield (file_rel, lineno, full_command) for each Arcana skill reference."""
    for path in sorted(ARCANA_ROOT.rglob("*.md")):
        if path.name in SKIP_FILES:
            continue
        rel = str(path.relative_to(ARCANA_ROOT)).replace("\\", "/")
        if any(rel.startswith(sd) for sd in SKIP_DIRS):
            continue
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        for lineno, line in enumerate(content.splitlines(), start=1):
            for match in SKILL_REF_RE.finditer(line):
                prefix = match.group(1)
                if prefix not in prefixes:
                    continue
                # Skip wildcard/placeholder forms - they're prose, not refs.
                tail = line[match.end() : match.end() + 2]
                if any(tail.startswith(s) for s in PLACEHOLDER_SUFFIXES):
                    continue
                full = match.group(0)
                yield rel, lineno, full


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate Arcana skill references")
    add_output_format_arg(parser)
    args = parser.parse_args()
    human = args.format == "human"
    reporter = DiagnosticReporter("validate_skill_refs", ARCANA_ROOT)

    if human:
        print()
        print("Validate Skill References")
        print("====================================")
        print(f"Arcana root:    {ARCANA_ROOT}")
        print(f"Skills dir:     {SKILLS_DIR}")
        print()

    valid_commands, prefixes = discover_skill_commands(reporter, human)
    if human:
        print(f"Skill prefixes: {', '.join(f'{prefix}-' for prefix in sorted(prefixes))}")
        print(f"Discovered {len(valid_commands)} valid Arcana-shipped skill(s).")
        print()

    if human:
        print("Scanning markdown for Arcana-shipped slash-command references...")
    dangling = []
    seen_pairs = set()
    for rel, lineno, full in scan_for_skill_refs(prefixes):
        if full in valid_commands:
            continue
        # Deduplicate (file, slug) pairs - one report per file per slug.
        key = (rel, full)
        if key in seen_pairs:
            continue
        seen_pairs.add(key)
        dangling.append((rel, lineno, full))
        reporter.error(
            "SKILL_REFS_DANGLING",
            f"references {full} with no source SKILL.md",
            path=rel,
            line=lineno,
            hint="Create the source skill or update the reference.",
        )
        if human:
            warn(f"{rel}:{lineno}  references {full}  (no source SKILL.md)")

    if human and not dangling:
        ok("All Arcana-shipped skill references resolve to existing skills.")
    if human:
        print()

    if not human:
        reporter.emit(
            args.format,
            checked={
                "valid_commands": len(valid_commands),
                "references": len(seen_pairs),
                "dangling_references": len(dangling),
            },
        )
        return reporter.exit_code()

    print("====================================")
    print(f"Dangling skill references: {len(dangling)}")
    print()

    if not dangling and reporter.error_count() == 0:
        return 0
    print("Either create the missing skill or update the reference.")
    print("If a skill was renamed, update the docs that reference it.")
    print("After adding/removing a skill, also run:")
    print("   python3 rites/sync_docs.py --apply")
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
