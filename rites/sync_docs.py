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
import sys
from pathlib import Path

from command_surface import command_entries, validate_command_surface
from _lib import SKILL_PREFIX_PLACEHOLDER, load_skill_families, parse_frontmatter

ARCANA_PATH = Path(__file__).resolve().parent.parent
SKILLS_DIR = ARCANA_PATH / "skills"
DOCS_DIR = ARCANA_PATH / "docs"
SKILLS_DOC = DOCS_DIR / "skills.md"


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
            argument_hint = fm.get("argument-hint", "")
            # Unquoted bracket hints (e.g. `argument-hint: [topic]`) parse as a
            # YAML flow sequence; render them back to a bracketed hint string.
            if isinstance(argument_hint, list):
                argument_hint = "[" + ", ".join(str(item) for item in argument_hint) + "]"
            argument_hint = str(argument_hint).strip()
            source = skill_file.relative_to(ARCANA_PATH).as_posix()
            skills.append({
                "name": registered_name,
                "description": description,
                "argument_hint": argument_hint,
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
    """Group skills by command family and purpose.

    Two command roots: grm (the universal grimoire surface) and arc (the Arcana
    platform/maintainer surface). Validation entry points get their own bucket so
    they read separately from the operational commands.
    """
    groups = {}
    for skill in skills:
        name = skill["name"]
        if name == "grm-validate" or name.startswith("grm-validate-"):
            group = "grimoire_validate"
        elif name.startswith("grm-audit-"):
            group = "grimoire_audit"
        elif name.startswith("grm-"):
            group = "grimoire"
        elif name == "arc-validate" or name.startswith("arc-validate-"):
            group = "arcana_validate"
        elif name.startswith("arc-"):
            group = "arcana"
        else:
            group = name.split("-", 1)[0] if "-" in name else name
        groups.setdefault(group, []).append(skill)

    # Stable ordering: Arcana core first, then the grimoire surface.
    priority = {
        "arcana": 0,
        "arcana_validate": 1,
        "grimoire": 2,
        "grimoire_validate": 3,
        "grimoire_audit": 4,
    }
    return sorted(groups.items(), key=lambda kv: (priority.get(kv[0], 99), kv[0]))


GROUP_HEADERS = {
    "arcana": "Arcana maintenance",
    "arcana_validate": "Arcana validation",
    "grimoire": "Grimoire operations",
    "grimoire_validate": "Grimoire validation",
    "grimoire_audit": "Grimoire audits",
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


def render_catalog_row(skill):
    """Render one user-facing catalog row: command, what it does, and input."""
    hint = skill.get("argument_hint") or ""
    input_cell = code_cell(hint) if hint else "none"
    return (
        f"| [`/{skill['name']}`](../{skill['source']}) "
        f"| {escape_table_cell(skill['description'])} "
        f"| {input_cell} |"
    )


def render_contract_row(skill, metadata):
    """Render one maintainer-facing command-contract row."""
    name = skill["name"]
    entry = metadata[name]
    return (
        f"| [`/{name}`](../{skill['source']}) "
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
        "Every command Arcana ships, grouped by what it does. `grm-*` commands",
        "operate on your grimoires; `arc-*` commands maintain the Arcana platform",
        "itself (most people never need them). Each command links to its source",
        "`SKILL.md`.",
        "",
        "Grimoire skills (e.g. `cook-*` for a cooking grimoire, `hr-*` for an HR",
        "grimoire) are declared in each grimoire's own `skills/` directory and are",
        "not listed here. Run `/arc-help` to enumerate every skill installed for an",
        "agent (Arcana + every grimoire).",
        "",
        "The [Command contract](#command-contract) at the end carries the",
        "engineering metadata (workflow home, owner, mutation profile, rite, guard,",
        "validation) for maintainers, generated from",
        "[command_surface.json](../rites/data/command_surface.json).",
        "",
        "---",
        "",
    ]

    for group, members in group_skills(skills):
        header = GROUP_HEADERS.get(group, group.title())
        lines.append(f"## {header}")
        lines.append("")
        lines.append("| Command | What it does | Input |")
        lines.append("|---|---|---|")
        for skill in members:
            lines.append(render_catalog_row(skill))
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Command contract",
        "",
        "Maintainer reference: the workflow home, owner type, mutation profile,",
        "rite owner, guard, and validation profile for each command, generated",
        "from [command_surface.json](../rites/data/command_surface.json).",
        "",
    ])
    for group, members in group_skills(skills):
        header = GROUP_HEADERS.get(group, group.title())
        lines.append(f"### {header}")
        lines.append("")
        lines.append(
            "| Command | Workflow | Owner | Mutation | Rite | Guard | Validation |"
        )
        lines.append("|---|---|---|---|---|---|---|")
        for skill in members:
            lines.append(render_contract_row(skill, command_metadata))
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
