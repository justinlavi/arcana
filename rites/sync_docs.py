#!/usr/bin/env python3
"""Generate canonical docs from authoritative source files.

Currently emits:
  docs/skills.md - canonical operational catalog of every Arcana skill,
                    derived from SKILL.md frontmatter and the public
                    command-surface contract.

Why a generator? The skill list is referenced from many places. With this rite,
each `SKILL.md` frontmatter and `rites/data/command_surface.json` entry form
the source of truth: edit the source files, re-run, and every consumer that
links to docs/skills.md sees the change.

Defaults to a dry-run that prints the diff. Pass --apply to write changes.

Usage:
    python3 sync_docs.py [--apply]
"""

import argparse
import difflib
import json
import re
import sys
from pathlib import Path

from command_surface import command_entries, validate_command_surface
from _lib import SKILL_PREFIX_PLACEHOLDER, load_skill_families, parse_frontmatter

ARCANA_PATH = Path(__file__).resolve().parent.parent
SKILLS_DIR = ARCANA_PATH / "skills"
DOCS_DIR = ARCANA_PATH / "docs"
SKILLS_DOC = DOCS_DIR / "skills.md"

ARCANA_MANIFEST = ARCANA_PATH / "arcana.json"


def read_frontmatter(skill_file):
    """Return a dict of frontmatter fields from a SKILL.md, or {} on failure."""
    return parse_frontmatter(skill_file.read_text(encoding="utf-8", errors="replace"))


def load_arcana_skill_families():
    """Return normalized command-family definitions from arcana.json."""
    return load_skill_families(ARCANA_PATH, with_fallback=True)


def collect_skills():
    """Return skill metadata for every Arcana-shipped public skill."""
    skills = []
    for family in load_arcana_skill_families():
        family_dir = family["path"]
        if not family_dir.is_dir():
            continue
        for skill_dir in sorted(family_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.is_file():
                continue
            fm = read_frontmatter(skill_file)
            templated_name = fm.get("name", "")
            if not templated_name:
                continue
            registered_name = templated_name.replace(
                SKILL_PREFIX_PLACEHOLDER, family["skill_prefix"]
            )
            description = fm.get("description", "")
            source = skill_file.relative_to(ARCANA_PATH).as_posix()
            skills.append({
                "name": registered_name,
                "description": description,
                "source": source,
            })
    return skills


def load_command_metadata():
    """Return command-surface metadata keyed by registered skill name."""
    contract, errors = validate_command_surface(ARCANA_PATH)
    if errors:
        messages = [
            f"{error['code']}: {error['message']} ({error['path']})"
            for error in errors
        ]
        raise RuntimeError(
            "command-surface contract is invalid:\n  " + "\n  ".join(messages)
        )
    if contract is None:
        raise RuntimeError("command-surface contract could not be loaded")

    metadata = {}
    for entry in command_entries(contract):
        metadata[entry["command"].lstrip("/")] = entry
    return metadata


def group_skills(skills):
    """Group skills by target and purpose."""
    groups = {}
    for skill in skills:
        name = skill["name"]
        without_ns = re.sub(r"^[a-z]+-", "", name, count=1)
        if name == "grm-validate" or name.startswith("grm-validate-"):
            group = "grimoire_validate"
        elif name.startswith("grm-audit-"):
            group = "grimoire_audit"
        elif name.startswith("grm-"):
            group = "grimoire"
        elif without_ns == "validate" or without_ns.startswith("validate-"):
            group = "arcana_validate"
        elif without_ns == "improve":
            group = "arcana"
        elif without_ns.startswith("library-"):
            group = "library"
        elif without_ns.startswith("agent-"):
            group = "agent"
        elif without_ns.startswith("workspace-"):
            group = "workspace"
        elif without_ns == "help":
            group = "help"
        else:
            group = without_ns.split("-", 1)[0] if "-" in without_ns else without_ns
        groups.setdefault(group, []).append(skill)

    # Stable ordering: Arcana core first, then grimoire and support groups.
    priority = {
        "arcana": 0,
        "arcana_validate": 1,
        "grimoire": 2,
        "grimoire_validate": 3,
        "grimoire_audit": 4,
        "library": 5,
        "agent": 6,
        "workspace": 7,
        "help": 8,
    }
    return sorted(groups.items(), key=lambda kv: (priority.get(kv[0], 99), kv[0]))


GROUP_HEADERS = {
    "arcana": "Arcana maintenance",
    "arcana_validate": "Arcana validation",
    "library": "Library management",
    "grimoire": "Grimoire operations",
    "grimoire_validate": "Grimoire validation",
    "grimoire_audit": "Grimoire audits",
    "help": "Help",
    "agent": "Agent configuration",
    "workspace": "Workspace maintenance",
}


def escape_table_cell(value):
    """Escape table delimiters and normalize whitespace in a Markdown cell."""
    return str(value).replace("|", "\\|").replace("\n", " ").strip()


def code_cell(value):
    """Render a short metadata value in a Markdown table cell."""
    if value is None or value == "":
        return "`none`"
    return f"`{escape_table_cell(value)}`"


def path_link(path, label=None):
    """Render a repository-relative path as a docs-relative Markdown link."""
    if not path:
        return "`none`"
    display = label or Path(path).name
    return f"[`{escape_table_cell(display)}`](../{path})"


def render_skill_row(skill, metadata):
    """Render one operational skill catalog row."""
    name = skill["name"]
    entry = metadata[name]
    return (
        f"| [`/{name}`](../{skill['source']}) "
        f"| {escape_table_cell(skill['description'])} "
        f"| {path_link(entry['invocation'])} "
        f"| {code_cell(entry['owner_type'])} "
        f"| {code_cell(entry['mutation_profile'])} "
        f"| {path_link(entry.get('rite_owner'))} "
        f"| {path_link(entry.get('guard'))} "
        f"| {code_cell(entry['validation_profile'])} |"
    )


def render_skills_doc(skills, command_metadata):
    """Render the canonical docs/skills.md content."""
    missing = sorted(
        skill["name"]
        for skill in skills
        if skill["name"] not in command_metadata
    )
    if missing:
        raise RuntimeError(
            "skills missing command-surface metadata: "
            + ", ".join(f"/{name}" for name in missing)
        )

    lines = [
        "---",
        "type: reference",
        'title: "Arcana Skill Catalog"',
        'aliases: ["skill-catalog", "skills-list"]',
        "tags: [type/reference, arcana/docs, generated]",
        "authority: grimoire",
        "last_verified: 2026-05-12",
        "---",
        "",
        "<!-- GENERATED by rites/sync_docs.py - do not edit by hand. -->",
        "<!-- Source of truth: skills/<family>/<slug>/SKILL.md frontmatter",
        "     and rites/data/command_surface.json. -->",
        "<!-- Regenerate with: python3 rites/sync_docs.py --apply -->",
        "",
        "# Arcana Skill Catalog",
        "",
        "Skills shipped by Arcana use command-family prefixes:",
        "`arc-*` for Arcana platform operations and `grm-*` for universal",
        "grimoire operations. See [skill_schema.md](skill_schema.md).",
        "Each entry links to the source `SKILL.md` and its operational",
        "command-surface metadata. The source files are canonical.",
        "",
        "Metadata columns come from",
        "[command_surface.json](../rites/data/command_surface.json): workflow",
        "home, owner type, mutation profile, rite owner, guard, and validation",
        "profile.",
        "",
        "Grimoire skills (e.g. `cook-*` for a cooking grimoire,",
        "`hr-*` for an HR grimoire) are not listed here - they're declared",
        "in each grimoire's own `skills/` directory and use the `skill_prefix`",
        "from that grimoire's `grimoire.json`. To enumerate every skill",
        "currently installed for an agent (Arcana + every grimoire),",
        "invoke `/arc-help`.",
        "",
        "---",
        "",
    ]

    for group, members in group_skills(skills):
        header = GROUP_HEADERS.get(group, group.title())
        lines.append(f"## {header}")
        lines.append("")
        lines.append(
            "| Skill | Description | Workflow | Owner | Mutation | Rite | Guard | Validation |"
        )
        lines.append("|---|---|---|---|---|---|---|---|")
        for skill in members:
            lines.append(render_skill_row(skill, command_metadata))
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Adding a new skill",
        "",
        "1. Choose the command family in [skill_schema.md](skill_schema.md).",
        "2. Create `skills/<family>/<slug>/SKILL.md` with frontmatter:",
        "   `name: {{SKILL_PREFIX}}-<registered-slug>` and a one-line `description`.",
        "3. Add or update the command entry in `rites/data/command_surface.json`.",
        "4. Run `python3 rites/validate_skill_refs.py` to validate public",
        "   command metadata.",
        "5. Run `python3 rites/sync_docs.py --apply` to refresh this library.",
        "6. Run `python3 rites/sync_skills.py` to install the skill into",
        "   agent skill directories.",
        "",
    ])
    return "\n".join(lines) + "\n"


def main():
    parser = argparse.ArgumentParser(description="Sync auto-generated docs from source files")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write changes (default: dry-run / show diff)",
    )
    args = parser.parse_args()

    print()
    print("  Sync Docs")
    print("  ----------------------------")

    skills = collect_skills()
    print(f"  Discovered {len(skills)} Arcana skill(s) under {SKILLS_DIR}")
    try:
        command_metadata = load_command_metadata()
    except RuntimeError as exc:
        print()
        print(f"  [FAIL] {exc}", file=sys.stderr)
        print()
        sys.exit(1)
    print(f"  Loaded {len(command_metadata)} command-surface entries")

    new_content = render_skills_doc(skills, command_metadata)
    old_content = SKILLS_DOC.read_text(encoding="utf-8") if SKILLS_DOC.is_file() else ""

    if new_content == old_content:
        print(f"  [OK]  {SKILLS_DOC.relative_to(ARCANA_PATH)} is up to date.")
        print()
        sys.exit(0)

    print(f"  [DIFF] {SKILLS_DOC.relative_to(ARCANA_PATH)}")
    print()
    diff = difflib.unified_diff(
        old_content.splitlines(keepends=True),
        new_content.splitlines(keepends=True),
        fromfile=f"a/{SKILLS_DOC.relative_to(ARCANA_PATH)}",
        tofile=f"b/{SKILLS_DOC.relative_to(ARCANA_PATH)}",
    )
    sys.stdout.writelines(diff)
    print()

    if args.apply:
        DOCS_DIR.mkdir(parents=True, exist_ok=True)
        SKILLS_DOC.write_text(new_content, encoding="utf-8", newline="\n")
        print(f"  [OK]  Wrote {SKILLS_DOC}")
        print()
        sys.exit(0)
    else:
        print(f"  Re-run with --apply to write {SKILLS_DOC.relative_to(ARCANA_PATH)}.")
        print()
        sys.exit(1)


if __name__ == "__main__":
    main()
