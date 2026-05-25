#!/usr/bin/env python3
"""Validates a grimoire's structure against Arcana conventions.

Required at the grimoire root:
    <grimoire-name>.md   (root hub; folder-name convention)
    README.md
    grimoire.json
    log.md
    sources/                  (immutable sources layer; may contain only .gitkeep)
    chapters/             (LLM-authored knowledge)

For each chapter folder F, the hub file F/F.md must exist (folder-name
convention). Sub-chapters follow the same rule recursively.

Usage:
    python3 rites/validate_grimoire_structure.py [--grimoire <path>]

Exit codes: 0 = compliant, 1 = violations
"""

import argparse
import filecmp
import sys
from pathlib import Path

from _lib import default_arcana_root, load_manifest

REQUIRED_DIRS = ["sources", "chapters"]
RECOMMENDED_DIRS = ["inbox"]  # Warn-only; inbox/ is the transient drop zone for /grm-ingest
# grimoire.json is validated separately (step 1); the root hub is checked in step 3.
REQUIRED_FILES_BY_CONVENTION = ["README.md", "log.md"]
MANAGED_SCAFFOLD_FILES = [
    ".editorconfig",
    ".gitattributes",
    ".obsidian/app.json",
    ".obsidian/graph.json",
    "inbox/README.md",
    "sources/README.md",
]


def main():
    parser = argparse.ArgumentParser(description="Validate grimoire structure")
    parser.add_argument("--grimoire", type=Path, default=Path.cwd(),
                        help="Grimoire root (default: cwd)")
    args = parser.parse_args()
    root = args.grimoire.expanduser().resolve()
    formula_root = default_arcana_root() / "formulae" / "grimoire"

    print()
    print("Validating Grimoire Structure")
    print("==================================")
    print(f"Grimoire root: {root}")
    print()

    errors = 0

    # 1. Manifest must exist, parse, and declare both 'name' and a valid skill_prefix.
    if not (root / "grimoire.json").is_file():
        print(f"  MISSING  grimoire.json")
        errors += 1
        grimoire_name = root.name
    else:
        manifest, manifest_errors = load_manifest(root)
        if manifest is None:
            # Parse failure - load_manifest reports the cause in errors[0].
            print(f"  WARN     {manifest_errors[0]}")
            errors += 1
            grimoire_name = root.name
        else:
            grimoire_name = manifest.get("name", root.name)
            for err_msg in manifest_errors:
                print(f"  WARN     {err_msg}")
                errors += 1
            print(f"  OK       grimoire.json (name={grimoire_name})")

    # 2. Required root files (other than the dynamic hub name).
    for f in REQUIRED_FILES_BY_CONVENTION:
        if not (root / f).is_file():
            print(f"  MISSING  file: {f}")
            errors += 1
        else:
            print(f"  OK       {f}")

    # 3. Root hub.
    root_hub = root / f"{grimoire_name}.md"
    if not root_hub.is_file():
        print(f"  MISSING  root hub: {grimoire_name}.md")
        errors += 1
    else:
        print(f"  OK       {grimoire_name}.md")

    # 4. Required directories.
    for d in REQUIRED_DIRS:
        if not (root / d).is_dir():
            print(f"  MISSING  directory: {d}")
            errors += 1
        else:
            print(f"  OK       {d}/")

    # 4b. Recommended directories (warn but don't fail).
    for d in RECOMMENDED_DIRS:
        if not (root / d).is_dir():
            print(f"  MISSING  directory: {d}/  - drop zone for /grm-ingest")
            errors += 1
        else:
            print(f"  OK       {d}/")

    # 5. Hub files inside chapters/ (folder-name convention, recursive).
    # Asset folders (templates/, snippets/, scripts/, configs/, examples/, tasks/)
    # and any folder whose name contains a `<placeholder>` token are not
    # required to have a hub - they hold demonstrative or asset content.
    ASSET_FOLDERS = {"templates", "snippets", "scripts", "configs", "assets", "media"}

    def is_asset_folder(folder, root):
        for part in folder.relative_to(root).parts:
            if part in ASSET_FOLDERS:
                return True
            if "<" in part or ">" in part:
                return True
        return False

    chapters = root / "chapters"
    if chapters.is_dir():
        print()
        print("Checking chapter hubs (folder-name convention)...")
        for folder in sorted(p for p in chapters.rglob("*") if p.is_dir()):
            if is_asset_folder(folder, root):
                continue
            hub = folder / f"{folder.name}.md"
            rel = folder.relative_to(root)
            if not hub.is_file():
                has_md = any(p.suffix == ".md" for p in folder.rglob("*.md") if p.is_file())
                if has_md:
                    print(f"  MISSING  hub: {rel}/{folder.name}.md")
                    errors += 1
            else:
                print(f"  OK       {rel}/{folder.name}.md")

    # 6. sources/ must not contain any wiki content (sanity).
    sources_dir = root / "sources"
    if sources_dir.is_dir():
        # A non-immutable artifact would be a `chapters/` folder under sources/
        forbidden = list(sources_dir.glob("chapters"))
        if forbidden:
            print(f"  WARN     sources/chapters exists - sources/ is for immutable artifacts, not wiki content")
            errors += 1

    # 7. Managed scaffold files should match the current Arcana formulae.
    # These files are operational support files, not grimoire-specific content.
    # Root README, root hub, grimoire.json, and log.md are intentionally not
    # compared because they are customized during grimoire creation.
    if formula_root.is_dir():
        print()
        print("Checking managed scaffold files against current Arcana formulae...")
        for rel in MANAGED_SCAFFOLD_FILES:
            expected = formula_root / rel
            actual = root / rel
            if not expected.is_file():
                print(f"  WARN     Arcana formula missing managed scaffold: {rel}")
                errors += 1
            elif not actual.is_file():
                print(f"  MISSING  managed scaffold: {rel}")
                errors += 1
            elif not filecmp.cmp(expected, actual, shallow=False):
                print(f"  STALE    managed scaffold differs from Arcana formula: {rel}")
                errors += 1
            else:
                print(f"  OK       {rel}")
    else:
        print(f"  WARN     Arcana formula root missing: {formula_root}")
        errors += 1

    # 8. Obsidian app.json must set newLinkFormat=absolute. The default
    # ("shortest") causes Ctrl-clicking a full-path wikilink to create a
    # recursive directory tree relative to the current note when the link
    # doesn't resolve. Setting "absolute" matches the validator's wikilink
    # resolution model.
    obsidian_app = root / ".obsidian" / "app.json"
    if obsidian_app.is_file():
        import json
        try:
            cfg = json.loads(obsidian_app.read_text())
        except (json.JSONDecodeError, OSError) as exc:
            print(f"  WARN     .obsidian/app.json unreadable: {exc}")
            errors += 1
        else:
            if cfg.get("newLinkFormat") != "absolute":
                print(f"  WARN     .obsidian/app.json must set \"newLinkFormat\": \"absolute\" "
                      f"(got {cfg.get('newLinkFormat')!r}); Ctrl-click on full-path wikilinks "
                      f"will create recursive directory trees otherwise")
                errors += 1
            else:
                print(f"  OK       .obsidian/app.json (newLinkFormat=absolute)")
    else:
        print(f"  WARN     .obsidian/app.json missing - copy from "
              f"ARCANA_HOME/formulae/grimoire/.obsidian/app.json to prevent "
              f"Obsidian's default link behavior from creating recursive directories")
        errors += 1

    print()
    print("==================================")
    if errors == 0:
        print("Grimoire structure validation passed")
        return 0
    print(f"Grimoire structure validation failed with {errors} issue(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
