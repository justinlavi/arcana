#!/usr/bin/env python3
"""Validates Arcana skill references and the public command-surface contract.

Scans all markdown files in Arcana for slash-command references matching
Arcana's declared command-family prefixes (for example `arc-` and `grm-`) and
ensures each reference resolves to a source `SKILL.md`. Catches drift like:

 - A doc mentioning `/grm-foo` after the skill was deleted/renamed.
 - A new skill mentioned in prose before its `skills/` folder is created.

Grimoire skill references (e.g. `/jpn-...`) are NOT validated here;
they live in their own grimoire repos. This is an Arcana-internal check.

Also validates `rites/data/command_surface.json`, the public contract that
connects every Arcana-shipped command to its skill source, invocation home,
workflow owner, safety posture, and validation profile.

Usage: python3 rites/validate_skill_refs.py
Exit codes: 0 = all references resolve, 1 = at least one dangling reference
"""

import json
import re
import sys
from pathlib import Path

from _lib import default_arcana_root, is_skipped, ok, warn
import command_surface as command_surface_contract
import rite_profiles as rite_profiles_contract
from diagnostics import DiagnosticReporter, add_output_format_arg

ARCANA_ROOT = default_arcana_root()
SKILLS_DIR = ARCANA_ROOT / "skills"
ARCANA_MANIFEST = ARCANA_ROOT / "arcana.json"
SKILL_PREFIX_PLACEHOLDER = "{{SKILL_PREFIX}}"

# Match slash-command references for Arcana-shipped command-family prefixes.
SKILL_REF_RE = re.compile(r"(?<![A-Za-z0-9_/-])/([a-z][a-z0-9]*)-([a-z][a-z0-9-]*)\b")

# Tokens that, when they immediately follow the matched slug, indicate a
# wildcard/placeholder rather than a concrete skill reference. Examples:
#   /arc-example-*       (wildcard summary)
#   /arc-example-<name>  (placeholder for prose)
#   /grm-example-{slug}  (variable substitution)
PLACEHOLDER_SUFFIXES = ("-*", "-<", "-{")

# Files that intentionally mention not-yet-existing or hypothetical skill
# names (templates, examples, historical references).
SKIP_FILES = {
    "validate_skill_refs.py",
    "CHANGELOG.md",  # historical references (e.g., describing a renamed/retired skill)
}

SKIP_DIRS = {
    "formulae",  # template placeholders
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
        if is_skipped(rel, SKIP_DIRS):
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


def mutation_profile_mismatches(surface_entries, rite_profile_entries):
    """Return rite-owned commands whose mutation_profile disagrees with the rite.

    A command's rite_owner that has a rite-profile entry must share that entry's
    profile; a rite_owner with no profile entry is not write-capable (the
    rite-profile contract requires every write-capable rite to be profiled), so
    the command must be read_only. Returns tuples of
    (command, rite_owner, command_mutation_profile, expected_profile).
    """
    rp_by_path = {entry.get("path"): entry for entry in rite_profile_entries}
    mismatches = []
    for entry in surface_entries:
        if entry.get("owner_type") != "rite":
            continue
        owner = entry.get("rite_owner")
        actual = entry.get("mutation_profile")
        profile = rp_by_path.get(owner)
        expected = profile.get("profile") if profile else "read_only"
        if actual != expected:
            mismatches.append((entry.get("command"), owner, actual, expected))
    return mismatches


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
    reference_count = 0
    for rel, lineno, full in scan_for_skill_refs(prefixes):
        reference_count += 1
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

    if human:
        print("Checking public command-surface contract...")
    surface_contract, surface_errors = command_surface_contract.validate_command_surface(ARCANA_ROOT)
    for error in surface_errors:
        reporter.error(
            error["code"],
            error["message"],
            path=error.get("path"),
            hint=error.get("hint"),
        )
        if human:
            warn(f"{error.get('path', '-')}: {error['message']}")

    surface_entries = (
        len(command_surface_contract.command_entries(surface_contract))
        if surface_contract is not None
        else 0
    )
    if human and not surface_errors:
        ok(f"Command-surface contract covers {surface_entries} public command(s).")
    if human:
        print()

    mutation_drift = 0
    if surface_contract is not None:
        try:
            rite_profile_list = rite_profiles_contract.profile_entries(
                rite_profiles_contract.load_rite_profiles(ARCANA_ROOT)
            )
        except (OSError, json.JSONDecodeError) as exc:
            rite_profile_list = []
            reporter.error(
                "COMMAND_SURFACE_RITE_PROFILES_READ",
                f"could not read rite-profile contract: {exc}",
                path="rites/data/rite_profiles.json",
                hint="Ensure rites/data/rite_profiles.json is valid JSON.",
            )
        for command, owner, actual, expected in mutation_profile_mismatches(
            command_surface_contract.command_entries(surface_contract), rite_profile_list
        ):
            mutation_drift += 1
            reporter.error(
                "COMMAND_SURFACE_MUTATION_PROFILE_DRIFT",
                f"{command} mutation_profile {actual!r} disagrees with {owner} (expected {expected!r})",
                path="rites/data/command_surface.json",
                hint="Align command_surface.mutation_profile with the rite's profile in rite_profiles.json.",
            )
            if human:
                warn(f"{command}: mutation_profile {actual!r} != expected {expected!r}")
    if human and not mutation_drift:
        ok("Command mutation profiles agree with the rite-profile contract.")
    if human:
        print()

    if not human:
        reporter.emit(
            args.format,
            checked={
                "valid_commands": len(valid_commands),
                "references": reference_count,
                "dangling_references": len(dangling),
                "command_surface_entries": surface_entries,
                "command_surface_errors": len(surface_errors),
                "mutation_profile_drift": mutation_drift,
            },
        )
        return reporter.exit_code()

    print("====================================")
    print(f"Dangling skill references: {len(dangling)}")
    print(f"Command-surface errors:    {len(surface_errors)}")
    print()

    if not dangling and reporter.error_count() == 0:
        return 0
    print("Either create the missing skill, update the reference, or repair the command-surface contract.")
    print("If a skill was renamed, update the docs and command-surface entry that reference it.")
    print("After adding/removing a skill, also run:")
    print("   python3 rites/sync_docs.py --apply")
    print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
