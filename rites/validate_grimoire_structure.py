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
import json
import sys
from pathlib import Path

from _lib import default_arcana_root, load_manifest
from scaffold_contract import (
    ScaffoldContractError,
    json_requirements,
    load_scaffold_contract,
    managed_scaffold_files,
    required_customized_files,
    required_directories,
    validate_contract_against_formula,
)


def main():
    parser = argparse.ArgumentParser(description="Validate grimoire structure")
    parser.add_argument("--grimoire", type=Path, default=Path.cwd(),
                        help="Grimoire root (default: cwd)")
    args = parser.parse_args()
    root = args.grimoire.expanduser().resolve()
    arcana_root = default_arcana_root()
    formula_root = arcana_root / "formulae" / "grimoire"

    print()
    print("Validating Grimoire Structure")
    print("==================================")
    print(f"Grimoire root: {root}")
    print()

    errors = 0
    try:
        scaffold_contract = load_scaffold_contract(arcana_root)
    except ScaffoldContractError as exc:
        print(f"  WARN     {exc}")
        print()
        print("==================================")
        print("Grimoire structure validation failed with 1 issue(s)")
        return 1

    for contract_error in validate_contract_against_formula(scaffold_contract, formula_root):
        print(f"  WARN     scaffold contract error: {contract_error}")
        errors += 1

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
    for f in required_customized_files(scaffold_contract):
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

    # 4. Required scaffold directories.
    for d in required_directories(scaffold_contract):
        if not (root / d).is_dir():
            print(f"  MISSING  directory: {d}")
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
        for rel in managed_scaffold_files(scaffold_contract):
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

    # 8. JSON requirements from the scaffold contract.
    for requirement in json_requirements(scaffold_contract):
        rel = requirement["path"]
        actual = root / rel
        if not actual.is_file():
            print(f"  WARN     {rel} missing")
            errors += 1
            continue
        try:
            cfg = json.loads(actual.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            print(f"  WARN     {rel} unreadable: {exc}")
            errors += 1
            continue

        for key, expected_value in requirement["required_values"].items():
            actual_value = cfg.get(key)
            if actual_value != expected_value:
                print(
                    f"  WARN     {rel} must set {key!r} to {expected_value!r} "
                    f"(got {actual_value!r})"
                )
                errors += 1
            else:
                print(f"  OK       {rel} ({key}={expected_value!r})")

    print()
    print("==================================")
    if errors == 0:
        print("Grimoire structure validation passed")
        return 0
    print(f"Grimoire structure validation failed with {errors} issue(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
