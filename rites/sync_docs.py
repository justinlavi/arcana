#!/usr/bin/env python3
"""Generate canonical docs from authoritative source files.

Currently emits:
  docs/skills.md - canonical list of every Arcana skill, derived from each
                    SKILL.md frontmatter (name + description).

Why a generator? The skill list is referenced from many places. With this rite,
each `SKILL.md` frontmatter is the single source of truth: edit the source file,
re-run, and every consumer that links to docs/skills.md sees the change.

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

ARCANA_PATH = Path(__file__).resolve().parent.parent
SKILLS_DIR = ARCANA_PATH / "skills"
DOCS_DIR = ARCANA_PATH / "docs"
SKILLS_DOC = DOCS_DIR / "skills.md"

SKILL_PREFIX_PLACEHOLDER = "{{SKILL_PREFIX}}"
ARCANA_SKILL_PREFIX = "arc"
ARCANA_MANIFEST = ARCANA_PATH / "arcana.json"


def read_frontmatter(skill_file):
    """Return a dict of frontmatter fields from a SKILL.md, or {} on failure."""
    content = skill_file.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return {}
    end = content.find("\n---", 4)
    if end == -1:
        return {}
    fields = {}
    for line in content[4:end].splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip().strip("'\"")
    return fields


def load_arcana_skill_families():
    """Return normalized command-family definitions from arcana.json."""
    metadata = json.loads(ARCANA_MANIFEST.read_text(encoding="utf-8"))
    default_prefix = metadata.get("skill_prefix", ARCANA_SKILL_PREFIX)
    raw_families = metadata.get("skill_families", {})
    if not isinstance(raw_families, dict) or not raw_families:
        raw_families = {
            "arcana": {
                "skill_prefix": default_prefix,
                "path": "skills",
                "slug_prefix": "",
            }
        }

    families = []
    for name, config in raw_families.items():
        families.append({
            "name": name,
            "skill_prefix": config.get("skill_prefix", default_prefix),
            "path": ARCANA_PATH / config.get("path", ""),
            "slug_prefix": config.get("slug_prefix", ""),
        })
    return families


def collect_skills():
    """Return list of (registered_name, description, source_path) for Arcana skills."""
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
            skills.append((registered_name, description, source))
    return skills


def group_skills(skills):
    """Group skills by target and purpose."""
    groups = {}
    for name, desc, source in skills:
        without_ns = re.sub(r"^[a-z]+-", "", name, count=1)
        if name.startswith("grm-validate-"):
            group = "grimoire_validate"
        elif name.startswith("grm-"):
            group = "grimoire"
        elif without_ns.startswith("validate-"):
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
        groups.setdefault(group, []).append((name, desc, source))

    # Stable ordering: Arcana core first, then grimoire and support groups.
    priority = {
        "arcana": 0,
        "arcana_validate": 1,
        "grimoire": 2,
        "grimoire_validate": 3,
        "library": 4,
        "agent": 5,
        "workspace": 6,
        "help": 7,
    }
    return sorted(groups.items(), key=lambda kv: (priority.get(kv[0], 99), kv[0]))


GROUP_HEADERS = {
    "arcana": "Arcana maintenance",
    "arcana_validate": "Arcana validation",
    "library": "Library management",
    "grimoire": "Grimoire operations",
    "grimoire_validate": "Grimoire validation",
    "help": "Help",
    "agent": "Agent configuration",
    "workspace": "Workspace maintenance",
}


def render_skills_doc(skills):
    """Render the canonical docs/skills.md content."""
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
        "<!-- Source of truth: each skills/<family>/<slug>/SKILL.md frontmatter. -->",
        "<!-- Regenerate with: python3 rites/sync_docs.py --apply -->",
        "",
        "# Arcana Skill Catalog",
        "",
        "Skills shipped by Arcana use command-family prefixes:",
        "`arc-*` for Arcana platform operations and `grm-*` for universal",
        "grimoire operations. See [skill_schema.md](skill_schema.md).",
        "Each entry links to the source `SKILL.md` - that file is canonical.",
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
        lines.append("| Skill | Description |")
        lines.append("|---|---|")
        for name, desc, source in members:
            lines.append(f"| [`/{name}`](../{source}) | {desc} |")
        lines.append("")

    lines.extend([
        "---",
        "",
        "## Adding a new skill",
        "",
        "1. Choose the command family in [skill_schema.md](skill_schema.md).",
        "2. Create `skills/<family>/<slug>/SKILL.md` with frontmatter:",
        "   `name: {{SKILL_PREFIX}}-<registered-slug>` and a one-line `description`.",
        "3. Run `python3 rites/sync_docs.py --apply` to refresh this library.",
        "4. Run `python3 rites/register_skills.py` to install the skill into agent skill directories.",
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

    new_content = render_skills_doc(skills)
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
