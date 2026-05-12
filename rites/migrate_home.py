#!/usr/bin/env python3
"""One-shot migration: ~/grimoire/ → ~/grimoires/ and catalog.json → library.json.

Existing installs created before the home-directory rename need to be moved
once. This rite is idempotent — safe to run multiple times.

Steps performed:
  1. If ~/grimoires/ already exists, report and stop (nothing to do).
  2. Move ~/grimoire/ → ~/grimoires/ via an atomic rename.
  3. Rename grimoires/catalog.json → grimoires/library.json (if it exists).
  4. Rewrite $HOME path strings inside library.json so local_path values
     still resolve (they stored "$HOME/grimoire/..." and now need
     "$HOME/grimoires/...").
  5. Update GRIMOIRE_ARCANA references in ~/.claude/CLAUDE.md and
     ~/.codex/AGENTS.md if they reference the old default path.

Usage:
    python3 rites/migrate_home.py [--dry-run]

Exit codes: 0 = success / nothing-to-do, 1 = error
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

OLD_HOME = Path.home() / "grimoire"
NEW_HOME = Path.home() / "grimoires"
OLD_LIBRARY = NEW_HOME / "catalog.json"   # after move it's here
NEW_LIBRARY = NEW_HOME / "library.json"
CLAUDE_MD = Path.home() / ".claude" / "CLAUDE.md"
CODEX_AGENTS_MD = Path.home() / ".codex" / "AGENTS.md"


def info(msg):
    print(f"  [INFO]  {msg}")


def ok(msg):
    print(f"  [OK]    {msg}")


def warn(msg):
    print(f"  [WARN]  {msg}")


def err(msg):
    print(f"  [ERROR] {msg}")


def rewrite_file(path, replacements, dry_run):
    """Apply {old: new} string replacements to a text file in-place."""
    if not path.is_file():
        return False
    original = path.read_text(encoding="utf-8", errors="replace")
    updated = original
    for old, new in replacements.items():
        updated = updated.replace(old, new)
    if updated == original:
        return False
    if dry_run:
        info(f"Would update: {path}")
    else:
        path.write_text(updated, encoding="utf-8")
        ok(f"Updated:      {path}")
    return True


def migrate_library_paths(library_path, dry_run):
    """Rewrite local_path values inside library.json from the old home to new."""
    if not library_path.is_file():
        return
    try:
        data = json.loads(library_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        warn(f"Could not parse {library_path}: {exc} — skipping path rewrite")
        return

    changed = False
    for key, entry in data.get("grimoires", {}).items():
        old_path = entry.get("local_path", "")
        if "$HOME/grimoire/" in old_path:
            new_path = old_path.replace("$HOME/grimoire/", "$HOME/grimoires/")
            if dry_run:
                info(f"Would rewrite local_path for '{key}': {old_path!r} → {new_path!r}")
            else:
                entry["local_path"] = new_path
            changed = True

    if not dry_run and changed:
        library_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        ok(f"Rewrote local_path entries in {library_path}")
    elif dry_run and not changed:
        info("No local_path rewrites needed in library.json")


def main():
    parser = argparse.ArgumentParser(description="Migrate ~/grimoire/ → ~/grimoires/")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be done without making any changes",
    )
    args = parser.parse_args()

    print()
    print("  Grimoire Home Migration")
    print("  ----------------------------")
    if args.dry_run:
        info("Dry-run mode — no changes will be made")
    print()

    # Step 1: Check if already migrated.
    if NEW_HOME.is_dir():
        ok(f"~/grimoires/ already exists — nothing to move.")
        print()
        # Still check catalog.json → library.json and path rewrites.
        if OLD_LIBRARY.is_file():
            if args.dry_run:
                info(f"Would rename: {OLD_LIBRARY} → {NEW_LIBRARY}")
            else:
                OLD_LIBRARY.rename(NEW_LIBRARY)
                ok(f"Renamed:      {OLD_LIBRARY.name} → {NEW_LIBRARY.name}")
            migrate_library_paths(NEW_LIBRARY if not args.dry_run else OLD_LIBRARY, args.dry_run)
        elif NEW_LIBRARY.is_file():
            ok(f"library.json already present — checking local_path values...")
            migrate_library_paths(NEW_LIBRARY, args.dry_run)
        else:
            info("No library.json found — skipping path rewrite.")
        _update_agent_files(args.dry_run)
        return 0

    # Step 2: old home doesn't exist either — nothing to do.
    if not OLD_HOME.is_dir():
        info("Neither ~/grimoire/ nor ~/grimoires/ found — nothing to migrate.")
        print()
        return 0

    # Step 3: Move ~/grimoire/ → ~/grimoires/
    info(f"Moving {OLD_HOME} → {NEW_HOME} ...")
    if not args.dry_run:
        try:
            OLD_HOME.rename(NEW_HOME)
            ok(f"Moved: ~/grimoire/ → ~/grimoires/")
        except OSError as exc:
            err(f"Failed to move directory: {exc}")
            err("If ~/grimoires/ already exists as a partial migration, remove it first.")
            return 1
    else:
        info(f"Would move: {OLD_HOME} → {NEW_HOME}")

    # Step 4: Rename catalog.json → library.json (it's now inside the new home).
    old_catalog = NEW_HOME / "catalog.json"
    if args.dry_run:
        if (OLD_HOME / "catalog.json").is_file():
            info(f"Would rename: catalog.json → library.json")
    elif old_catalog.is_file():
        old_catalog.rename(NEW_LIBRARY)
        ok(f"Renamed: catalog.json → library.json")

    # Step 5: Rewrite local_path values in the library.
    migrate_library_paths(NEW_LIBRARY if not args.dry_run else (OLD_HOME / "catalog.json"), args.dry_run)

    # Step 6: Update agent instruction files.
    _update_agent_files(args.dry_run)

    print()
    ok("Migration complete.")
    print()
    print("  Next steps:")
    print("    1. Run /grm-library-sync to verify the library is correct.")
    print("    2. Run /grm-skills-register to refresh skill registrations.")
    print()
    return 0


def _update_agent_files(dry_run):
    """Update ~/grimoire/ path references in CLAUDE.md and AGENTS.md."""
    replacements = {
        "~/grimoire/catalog.json": "~/grimoires/library.json",
        "~/grimoire/arcana/": "~/grimoires/arcana/",
        "~/grimoire/": "~/grimoires/",
        "$HOME/grimoire/": "$HOME/grimoires/",
        "**Catalog**": "**Library**",
    }
    for path in (CLAUDE_MD, CODEX_AGENTS_MD):
        changed = rewrite_file(path, replacements, dry_run)
        if not changed and path.is_file():
            info(f"No changes needed in {path.name}")
        elif not path.is_file():
            info(f"{path} not found — skipping")


if __name__ == "__main__":
    sys.exit(main())
