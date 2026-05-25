#!/usr/bin/env python3
"""Grimoire Skill Registration - cross-platform skill installer.

Discovers skills from Arcana and all installed grimoires, cleans stale skills
by skill prefix, substitutes the {{SKILL_PREFIX}} placeholder with the declared
skill prefix, and installs pointer skills to supported agent skill directories.

Arcana declares its skill prefix in `arcana.json`:

    {
      "name": "arcana",
      "kind": "arcana",
      "skill_prefix": "arc",
      "description": "..."
    }

Each grimoire declares its skill prefix in `grimoire.json` at the grimoire root:

    {
      "name": "cooking-grimoire",
      "skill_prefix": "cook",
      "description": "..."
    }

Grimoire skill source folders provide the subcommand path after the skill prefix.
For example, skill_prefix "cook" plus skills/recipe-add registers as
/cook-recipe-add.

Source SKILL.md files use `{{SKILL_PREFIX}}-<slug>` in their `name:` frontmatter
field; the rite substitutes the placeholder during registration.

Usage:
    python3 register_skills.py [--agent all|claude|codex] [--dry-run]
"""

import argparse
import json
import shutil
from pathlib import Path

from _lib import (
    SKILL_PREFIX_RE,
    SKILL_SLUG_RE,
    info,
    load_library,
    load_manifest,
    ok,
    warn,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ARCANA_PATH = Path(__file__).resolve().parent.parent
ARCANA_MANIFEST = ARCANA_PATH / "arcana.json"
GRIMOIRES_HOME = Path.home() / "grimoires"
LOCAL_LIBRARY = GRIMOIRES_HOME / "library.json"
SKILL_PREFIX_PLACEHOLDER = "{{SKILL_PREFIX}}"
SKILL_TARGETS = {
    "claude": {
        "label": "Claude Code",
        "path": Path.home() / ".claude" / "skills",
        "pointer_only": False,
    },
    "codex": {
        "label": "Codex/ChatGPT",
        "path": Path.home() / ".codex" / "skills",
        "pointer_only": True,
    },
}


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------


def is_valid_skill_prefix(skill_prefix):
    """Return True when skill_prefix is a compact lowercase slug like grm or oly."""
    return bool(SKILL_PREFIX_RE.fullmatch(skill_prefix))


def is_valid_skill_slug(slug):
    """Return True when a skill slug uses lowercase hyphenated command syntax."""
    return bool(SKILL_SLUG_RE.fullmatch(slug))


def load_grimoire_metadata(grimoire_root, label):
    """Load and skill_prefix-validate a grimoire's manifest.

    Returns (metadata_dict, skill_prefix_str) on success, or (None, None) on
    failure with a warning logged. Thin wrapper over `_lib.load_manifest`
    that downgrades structured errors into the side-effect logs the
    skill-registration UX expects.
    """
    metadata, errors = load_manifest(grimoire_root)
    if metadata is None:
        warn(f"{label}: {errors[0]} (skipping)")
        return None, None
    if errors:
        warn(f"{label}: {errors[0]} (skipping)")
        return None, None
    return metadata, metadata.get("skill_prefix", "")


def load_arcana_metadata():
    """Load and validate Arcana's own manifest."""
    try:
        metadata = json.loads(ARCANA_MANIFEST.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        warn(f"Arcana: could not read arcana.json: {exc} (skipping)")
        return None, None

    skill_prefix = metadata.get("skill_prefix", "")
    if metadata.get("kind") != "arcana":
        warn("Arcana: arcana.json missing kind='arcana' (skipping)")
        return None, None
    if not skill_prefix or not SKILL_PREFIX_RE.fullmatch(skill_prefix):
        warn(
            "Arcana: arcana.json missing valid 'skill_prefix' "
            f"(must match {SKILL_PREFIX_RE.pattern})"
        )
        return None, None
    return metadata, skill_prefix


def read_frontmatter_name(skill_file):
    """Extract the simple YAML frontmatter name without requiring PyYAML."""
    content = skill_file.read_text(encoding="utf-8")
    if not content.startswith("---\n"):
        return ""

    end = content.find("\n---", 4)
    if end == -1:
        return ""

    for line in content[4:end].splitlines():
        if line.startswith("name:"):
            return line.split(":", 1)[1].strip().strip("'\"")
    return ""


def clean_prefix(skills_target, prefix, dry_run=False):
    """Remove all skill directories matching a skill_prefix."""
    cleaned = 0
    if not skills_target.is_dir():
        return cleaned

    for skill_dir in sorted(skills_target.iterdir()):
        if skill_dir.is_dir() and skill_dir.name.startswith(prefix):
            if dry_run:
                info(f"Would remove: {skill_dir.name}")
            else:
                shutil.rmtree(skill_dir)
            cleaned += 1
    return cleaned


def register_skill(
    source_dir,
    skills_target,
    skill_prefix,
    arcana_path,
    grimoire_path="",
    source_label="Arcana",
    dry_run=False,
    pointer_only=False,
):
    """Template and install a single skill. Returns True if registered."""
    source_file = source_dir / "SKILL.md"

    if not source_file.is_file():
        warn(f"No SKILL.md found in {source_dir} (skipping)")
        return False

    slug = source_dir.name
    expected_name = f"{skill_prefix}-{slug}"

    declared_name_template = read_frontmatter_name(source_file)
    expected_template = f"{SKILL_PREFIX_PLACEHOLDER}-{slug}"
    if declared_name_template != expected_template:
        warn(
            f"{source_dir}: SKILL.md name must be '{expected_template}' "
            f"(found '{declared_name_template or '<missing>'}')"
        )
        return False

    if dry_run:
        info(f"Would register: /{expected_name} ({source_label})")
        return True

    target_dir = skills_target / expected_name
    target_dir.mkdir(parents=True, exist_ok=True)

    # Template files in the skill directory. Codex/ChatGPT registrations are
    # intentionally SKILL.md only: the skill remains a thin pointer to Arcana.
    for source in source_dir.iterdir():
        if not source.is_file():
            continue
        if pointer_only and source.name != "SKILL.md":
            continue
        content = source.read_text(encoding="utf-8")
        content = content.replace(SKILL_PREFIX_PLACEHOLDER, skill_prefix)
        content = content.replace("{{ARCANA_PATH}}", str(arcana_path))
        if grimoire_path:
            content = content.replace("{{GRIMOIRE_PATH}}", str(grimoire_path))

        # Add provenance header to SKILL.md so AI knows this is a generated copy
        if source.name == "SKILL.md":
            provenance = (
                f"\n<!-- GENERATED - source: {source_dir}/SKILL.md | "
                f"DO NOT EDIT this file. Edit the source and run /arc-skills-register. -->\n"
            )
            # Insert after frontmatter closing ---
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[0] + "---" + parts[1] + "---" + provenance + parts[2]

        with open(target_dir / source.name, "w", encoding="utf-8", newline="\n") as f:
            f.write(content)

    ok(f"Registered: /{expected_name} ({source_label})")
    return True


def register_source_skills(
    source_root,
    skills_dir,
    skill_prefix,
    source_label,
    skills_target,
    grimoire_path,
    dry_run,
    pointer_only,
):
    """Clean a skill_prefix and register every well-formed skill folder under it."""
    prefix = f"{skill_prefix}-"

    info(f"Cleaning {prefix}* skill_prefix...")
    cleaned = clean_prefix(skills_target, prefix, dry_run)

    info(f"Scanning {source_label} skills...")
    registered = 0

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        if not is_valid_skill_slug(skill_dir.name):
            warn(f"{skill_dir}: invalid skill directory slug (skipping)")
            continue
        if register_skill(
            skill_dir,
            skills_target,
            skill_prefix,
            ARCANA_PATH,
            grimoire_path=grimoire_path,
            source_label=source_label,
            dry_run=dry_run,
            pointer_only=pointer_only,
        ):
            registered += 1

    return registered, cleaned


def register_arcana_skills(skills_target, dry_run=False, pointer_only=False):
    """Register all Arcana skills using the prefix declared in arcana.json."""
    skills_dir = ARCANA_PATH / "skills"
    if not skills_dir.is_dir():
        warn(f"No skills directory in Arcana at {skills_dir}")
        return 0, 0

    _, skill_prefix = load_arcana_metadata()
    if not skill_prefix:
        return 0, 0

    return register_source_skills(
        ARCANA_PATH,
        skills_dir,
        skill_prefix,
        "Arcana",
        skills_target,
        grimoire_path="",
        dry_run=dry_run,
        pointer_only=pointer_only,
    )


def register_grimoire_skills(skills_target, dry_run=False, pointer_only=False):
    """Register skills from all installed grimoires.

    Each grimoire's skill_prefix is read from its own grimoire.json. The library
    is consulted only to discover where grimoires live on disk.
    """
    if not LOCAL_LIBRARY.is_file():
        info(f"No local library at {LOCAL_LIBRARY} - skipping grimoire skills")
        return 0, 0

    library = load_library(LOCAL_LIBRARY)

    total_registered = 0
    total_cleaned = 0

    for key in sorted(library.get("grimoires", {}).keys()):
        entry = library["grimoires"][key]
        raw_path = entry.get("local_path", "")

        # Expand $HOME
        local_path = Path(raw_path.replace("$HOME", str(Path.home())))

        if not local_path.is_dir():
            info(f"{key}: directory not found at {local_path} (skipping)")
            continue

        skills_dir = local_path / "skills"
        if not skills_dir.is_dir():
            info(f"{key}: no skills/ directory (skipping)")
            continue

        _, skill_prefix = load_grimoire_metadata(local_path, key)
        if not skill_prefix:
            continue

        registered, cleaned = register_source_skills(
            local_path,
            skills_dir,
            skill_prefix,
            key,
            skills_target,
            grimoire_path=str(local_path),
            dry_run=dry_run,
            pointer_only=pointer_only,
        )
        total_registered += registered
        total_cleaned += cleaned

    return total_registered, total_cleaned


def selected_targets(agent):
    """Return target configurations for the requested agent."""
    if agent == "all":
        return SKILL_TARGETS.items()
    return [(agent, SKILL_TARGETS[agent])]


def register_target(agent_name, config, dry_run=False):
    """Register all skills for one agent target."""
    label = config["label"]
    skills_target = config["path"]
    pointer_only = config["pointer_only"]

    print(f"  Target: {label} ({skills_target})")
    if pointer_only:
        info("Pointer-only registration - copying SKILL.md files only")

    if not dry_run:
        skills_target.mkdir(parents=True, exist_ok=True)

    arcana_registered, arcana_cleaned = register_arcana_skills(
        skills_target, dry_run, pointer_only
    )
    grimoire_registered, grimoire_cleaned = register_grimoire_skills(
        skills_target, dry_run, pointer_only
    )

    total_registered = arcana_registered + grimoire_registered
    total_cleaned = arcana_cleaned + grimoire_cleaned

    print()
    print(f"  {label}: registered {total_registered} skill(s)")
    if total_cleaned > 0:
        print(f"  {label}: cleaned    {total_cleaned} stale skill(s)")
    print()

    return {
        "agent": agent_name,
        "label": label,
        "registered": total_registered,
        "cleaned": total_cleaned,
    }


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Grimoire Skill Registration")
    parser.add_argument(
        "--agent",
        choices=["all", "claude", "codex"],
        default="all",
        help="Agent skill target to register (default: all)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making changes",
    )
    args = parser.parse_args()

    print()
    print("  Grimoire Skill Registration")
    print("  ----------------------------")
    print()

    if args.dry_run:
        info("Dry run mode - no files will be written")
        print()

    results = []
    for agent_name, config in selected_targets(args.agent):
        results.append(register_target(agent_name, config, args.dry_run))

    print()
    print("  ----------------------------")
    total_registered = sum(result["registered"] for result in results)
    total_cleaned = sum(result["cleaned"] for result in results)
    print(f"  Registered: {total_registered} skill registration(s)")
    if total_cleaned > 0:
        print(f"  Cleaned:    {total_cleaned} stale skill registration(s)")
    print()

    if not args.dry_run and total_registered > 0:
        labels = ", ".join(result["label"] for result in results)
        print(f"  Skills are now available for: {labels}.")
        print("  Try: /arc-help")
        print()


if __name__ == "__main__":
    main()
