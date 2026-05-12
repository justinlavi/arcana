#!/usr/bin/env python3
"""Grimoire Skill Registration — cross-platform skill installer.

Discovers skills from Arcana and all installed grimoires, cleans stale skills
by namespace prefix, substitutes the {{NAMESPACE}} placeholder with the
grimoire's declared namespace, and installs pointer skills to supported agent
skill directories.

Each grimoire (and Arcana) declares its namespace in `grimoire.json` at the
grimoire root:

    {
      "name": "olympus-grimoire",
      "namespace": "oly",
      "description": "..."
    }

Domain skill source folders provide the subcommand path after the namespace.
For example, namespace "oly" plus skills/gui-create-plugin registers
as /oly-gui-create-plugin.

Source SKILL.md files use `{{NAMESPACE}}-<slug>` in their `name:` frontmatter
field; the rite substitutes the placeholder during registration.

Usage:
    python3 register_skills.py [--agent all|claude|codex] [--dry-run]
"""

import argparse
import json
import re
import shutil
from pathlib import Path

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

ARCANA_PATH = Path(__file__).resolve().parent.parent
GRIMOIRE_HOME = Path.home() / "grimoire"
LOCAL_CATALOG = GRIMOIRE_HOME / "catalog.json"
NAMESPACE_RE = re.compile(r"^[a-z][a-z0-9]*$")
SKILL_SLUG_RE = re.compile(r"^[a-z][a-z0-9]*(?:-[a-z0-9]+)*$")
NAMESPACE_PLACEHOLDER = "{{NAMESPACE}}"
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
# Logging
# ---------------------------------------------------------------------------


def info(msg):
    print(f"  [INFO]  {msg}")


def ok(msg):
    print(f"  [OK]    {msg}")


def warn(msg):
    print(f"  [WARN]  {msg}")


def err(msg):
    print(f"  [ERROR] {msg}")


# ---------------------------------------------------------------------------
# Core operations
# ---------------------------------------------------------------------------


def is_valid_namespace(namespace):
    """Return True when namespace is a compact lowercase slug like grm or oly."""
    return bool(NAMESPACE_RE.fullmatch(namespace))


def is_valid_skill_slug(slug):
    """Return True when a skill slug uses lowercase hyphenated command syntax."""
    return bool(SKILL_SLUG_RE.fullmatch(slug))


def load_grimoire_metadata(grimoire_root, label):
    """Load grimoire.json from a grimoire (or Arcana) root.

    Returns (metadata_dict, namespace_str) on success, or (None, None) on
    failure with a warning logged.
    """
    metadata_file = grimoire_root / "grimoire.json"
    if not metadata_file.is_file():
        warn(f"{label}: missing grimoire.json at {metadata_file} (skipping)")
        return None, None

    try:
        with open(metadata_file) as f:
            metadata = json.load(f)
    except (json.JSONDecodeError, OSError) as exc:
        warn(f"{label}: could not read grimoire.json ({exc}) (skipping)")
        return None, None

    namespace = metadata.get("namespace", "")
    if not namespace:
        warn(f"{label}: grimoire.json missing 'namespace' field (skipping)")
        return None, None
    if not is_valid_namespace(namespace):
        warn(f"{label}: invalid namespace '{namespace}' in grimoire.json (skipping)")
        return None, None

    return metadata, namespace


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
    """Remove all skill directories matching a namespace prefix."""
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
    namespace,
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
    expected_name = f"{namespace}-{slug}"

    declared_name_template = read_frontmatter_name(source_file)
    expected_template = f"{NAMESPACE_PLACEHOLDER}-{slug}"
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
        content = content.replace(NAMESPACE_PLACEHOLDER, namespace)
        content = content.replace("{{ARCANA_PATH}}", str(arcana_path))
        if grimoire_path:
            content = content.replace("{{GRIMOIRE_PATH}}", str(grimoire_path))

        # Add provenance header to SKILL.md so AI knows this is a generated copy
        if source.name == "SKILL.md":
            provenance = (
                f"\n<!-- GENERATED — source: {source_dir}/SKILL.md | "
                f"DO NOT EDIT this file. Edit the source and run /grm-skills-register. -->\n"
            )
            # Insert after frontmatter closing ---
            parts = content.split("---", 2)
            if len(parts) >= 3:
                content = parts[0] + "---" + parts[1] + "---" + provenance + parts[2]

        (target_dir / source.name).write_text(content, encoding="utf-8")

    ok(f"Registered: /{expected_name} ({source_label})")
    return True


def register_source_skills(
    source_root,
    skills_dir,
    namespace,
    source_label,
    skills_target,
    grimoire_path,
    dry_run,
    pointer_only,
):
    """Clean a namespace and register every well-formed skill folder under it."""
    prefix = f"{namespace}-"

    info(f"Cleaning {prefix}* namespace...")
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
            namespace,
            ARCANA_PATH,
            grimoire_path=grimoire_path,
            source_label=source_label,
            dry_run=dry_run,
            pointer_only=pointer_only,
        ):
            registered += 1

    return registered, cleaned


def register_arcana_skills(skills_target, dry_run=False, pointer_only=False):
    """Register all Arcana skills using namespace declared in arcana/grimoire.json."""
    skills_dir = ARCANA_PATH / "skills"
    if not skills_dir.is_dir():
        warn(f"No skills directory in Arcana at {skills_dir}")
        return 0, 0

    _, namespace = load_grimoire_metadata(ARCANA_PATH, "Arcana")
    if not namespace:
        return 0, 0

    return register_source_skills(
        ARCANA_PATH,
        skills_dir,
        namespace,
        "Arcana",
        skills_target,
        grimoire_path="",
        dry_run=dry_run,
        pointer_only=pointer_only,
    )


def register_grimoire_skills(skills_target, dry_run=False, pointer_only=False):
    """Register skills from all installed domain grimoires.

    Each grimoire's namespace is read from its own grimoire.json. The catalog
    is consulted only to discover where grimoires live on disk.
    """
    if not LOCAL_CATALOG.is_file():
        info(f"No local catalog at {LOCAL_CATALOG} — skipping domain skills")
        return 0, 0

    try:
        with open(LOCAL_CATALOG) as f:
            catalog = json.load(f)
    except (json.JSONDecodeError, OSError):
        warn("Could not read local catalog — skipping domain skills")
        return 0, 0

    total_registered = 0
    total_cleaned = 0

    for key in sorted(catalog.get("grimoires", {}).keys()):
        entry = catalog["grimoires"][key]
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

        _, namespace = load_grimoire_metadata(local_path, key)
        if not namespace:
            continue

        registered, cleaned = register_source_skills(
            local_path,
            skills_dir,
            namespace,
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
        info("Pointer-only registration — copying SKILL.md files only")

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
        info("Dry run mode — no files will be written")
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
        print("  Try: /grm-meta-help")
        print()


if __name__ == "__main__":
    main()
