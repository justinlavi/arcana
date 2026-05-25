#!/usr/bin/env python3
"""Validates snake_case naming convention for files and directories.

Usage: python3 rites/validate_naming.py
Exit codes: 0 = success, 1 = violations found
"""

import re
import sys
import json
from pathlib import Path

from _lib import default_arcana_root, ok, warn
from diagnostics import DiagnosticReporter, add_output_format_arg

ARCANA_ROOT = default_arcana_root()

UPPERCASE_EXCEPTIONS = {"README.md", "CHANGELOG.md", "CONTRIBUTING.md",
                        "CLAUDE.md", "AGENTS.md", "LICENSE.md",
                        "IMPLEMENTATION_PLAN.md", "VERSION"}


SKIP_DIRS = {"sources", ".git", "tests"}
ARCANA_MANIFEST = ARCANA_ROOT / "arcana.json"


def check_naming(glob_pattern, label, ext, reporter, human):
    violations = 0

    if human:
        print(f"Checking {label} naming...")
    for path in sorted(ARCANA_ROOT.rglob(glob_pattern)):
        name = path.name
        rel_parts = path.relative_to(ARCANA_ROOT).parts
        if rel_parts and rel_parts[0] in SKIP_DIRS:
            continue

        if name in UPPERCASE_EXCEPTIONS:
            continue

        if re.match(r"^[a-z].*-.*\." + ext + "$", name):
            reporter.error(
                "NAMING_HYPHENATED",
                "hyphenated name should use snake_case",
                path=path,
            )
            if human:
                warn(f"Hyphenated (should use snake_case): {path.relative_to(ARCANA_ROOT)}")
            violations += 1

        if re.search(r"[a-z][A-Z]", name):
            reporter.error(
                "NAMING_CAMELCASE",
                "CamelCase name should use snake_case",
                path=path,
            )
            if human:
                warn(f"CamelCase (should use snake_case): {path.relative_to(ARCANA_ROOT)}")
            violations += 1

    if human and violations == 0:
        ok(f"All {label} use proper naming")
    if human:
        print()
    return violations


def parse_skill_name(skill_file):
    content = skill_file.read_text(encoding="utf-8", errors="replace")
    match = re.search(r"(?m)^name:\s*(.+)$", content)
    return match.group(1).strip() if match else ""


def load_skill_families(reporter, human):
    """Return Arcana skill families declared in arcana.json."""
    try:
        metadata = json.loads(ARCANA_MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        reporter.error("SKILL_SCHEMA_MANIFEST_READ", f"could not read arcana.json: {exc}", path="arcana.json")
        if human:
            warn(f"Could not read arcana.json skill_families: {exc}")
        return []

    default_prefix = metadata.get("skill_prefix", "arc")
    raw_families = metadata.get("skill_families", {})
    if not isinstance(raw_families, dict) or not raw_families:
        reporter.error("SKILL_SCHEMA_MISSING_FAMILIES", "arcana.json missing skill_families", path="arcana.json")
        if human:
            warn("arcana.json missing skill_families")
        return []

    families = []
    for name, config in raw_families.items():
        if not isinstance(config, dict):
            reporter.error("SKILL_SCHEMA_FAMILY_INVALID", f"skill_families.{name} must be an object", path="arcana.json")
            if human:
                warn(f"skill_families.{name} must be an object")
            continue
        rel_path = config.get("path", "")
        if not rel_path:
            reporter.error("SKILL_SCHEMA_FAMILY_MISSING_PATH", f"skill_families.{name} missing path", path="arcana.json")
            if human:
                warn(f"skill_families.{name} missing path")
            continue
        families.append({
            "name": name,
            "path": ARCANA_ROOT / rel_path,
            "rel_path": Path(rel_path),
            "skill_prefix": config.get("skill_prefix", default_prefix),
            "slug_prefix": config.get("slug_prefix", ""),
        })
    return families


def check_skill_schema(reporter, human):
    violations = 0
    skills_dir = ARCANA_ROOT / "skills"

    if human:
        print("Checking skill naming schema...")
    if not skills_dir.is_dir():
        reporter.error("SKILL_SCHEMA_MISSING_DIR", "missing skills/ directory", path="skills")
        if human:
            warn("Missing skills/ directory")
        return 1

    families = load_skill_families(reporter, human)
    if not families:
        reporter.error("SKILL_SCHEMA_NO_FAMILIES", "no valid skill families declared", path="arcana.json")
        if human:
            warn("No valid skill families declared")
        return 1

    expected_top_dirs = {family["rel_path"].parts[1] for family in families}
    for folder in sorted(p for p in skills_dir.iterdir() if p.is_dir()):
        if folder.name not in expected_top_dirs:
            reporter.error(
                "SKILL_SCHEMA_UNEXPECTED_FAMILY_DIR",
                "unexpected skill family directory",
                path=folder,
            )
            if human:
                warn(f"Unexpected skill family directory: {folder.relative_to(ARCANA_ROOT)}")
            violations += 1
            continue

    for family in families:
        family_dir = family["path"]
        if not family_dir.is_dir():
            reporter.error(
                "SKILL_SCHEMA_MISSING_FAMILY_DIR",
                "missing skill family directory",
                path=family_dir,
            )
            if human:
                warn(f"Missing skill family directory: {family_dir.relative_to(ARCANA_ROOT)}")
            violations += 1
            continue

        for folder in sorted(p for p in family_dir.iterdir() if p.is_dir()):
            skill_file = folder / "SKILL.md"
            if not skill_file.is_file():
                reporter.error("SKILL_SCHEMA_MISSING_SKILL_FILE", "missing SKILL.md", path=folder)
                if human:
                    warn(f"Missing SKILL.md: {folder.relative_to(ARCANA_ROOT)}")
                violations += 1
                continue

            command_slug = (
                f"{family['slug_prefix']}-{folder.name}"
                if family["slug_prefix"]
                else folder.name
            )
            expected_name = f"{{{{SKILL_PREFIX}}}}-{command_slug}"
            actual_name = parse_skill_name(skill_file)
            if actual_name != expected_name:
                reporter.error(
                    "SKILL_SCHEMA_NAME_MISMATCH",
                    f"skill name mismatch (expected `{expected_name}`, got `{actual_name}`)",
                    path=skill_file,
                )
                if human:
                    warn(
                        f"Skill name mismatch: {skill_file.relative_to(ARCANA_ROOT)} "
                        f"(expected `{expected_name}`, got `{actual_name}`)"
                    )
                violations += 1

        direct_skill = family_dir / "SKILL.md"
        if direct_skill.exists():
            reporter.error(
                "SKILL_SCHEMA_DIRECT_SKILL_FILE",
                "skill family has direct SKILL.md; expected nested skill folders",
                path=direct_skill,
            )
            if human:
                warn(f"Skill family has direct SKILL.md; expected nested skill folders: {direct_skill.relative_to(ARCANA_ROOT)}")
            violations += 1

    for skill_file in sorted(skills_dir.rglob("SKILL.md")):
        if any(skill_file.is_relative_to(family["path"]) for family in families):
            continue
        reporter.error(
            "SKILL_SCHEMA_FILE_OUTSIDE_FAMILIES",
            "SKILL.md is outside declared skill families",
            path=skill_file,
        )
        if human:
            warn(f"SKILL.md is outside declared skill families: {skill_file.relative_to(ARCANA_ROOT)}")
        violations += 1

    if human and violations == 0:
        ok("All skills follow the command-family naming schema")
    if human:
        print()
    return violations


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate naming conventions")
    add_output_format_arg(parser)
    args = parser.parse_args()
    human = args.format == "human"
    reporter = DiagnosticReporter("validate_naming", ARCANA_ROOT)

    if human:
        print()
        print("Validating Naming Conventions")
        print("==================================")
        print(f"Arcana root: {ARCANA_ROOT}")
        print()

    markdown_violations = check_naming("*.md", "markdown file", "md", reporter, human)
    python_violations = check_naming("*.py", "Python script", "py", reporter, human)
    skill_violations = check_skill_schema(reporter, human)

    if not human:
        reporter.emit(
            args.format,
            checked={
                "markdown_violations": markdown_violations,
                "python_violations": python_violations,
                "skill_violations": skill_violations,
            },
        )
        return reporter.exit_code()

    print("==================================")
    if reporter.error_count() == 0:
        print("Naming validation passed")
        return 0
    else:
        print(f"Naming validation found {reporter.error_count()} issues")
        return 1


if __name__ == "__main__":
    sys.exit(main())
