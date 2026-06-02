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

The folder-name convention is enforced as an if-and-only-if under chapters/: a
folder-named page (the root hub and each F/F.md) must declare `type: hub`, and a
page that declares `type: hub` must be folder-named. This lets an agent tell hubs
from leaves by path alone. Demonstrative asset folders are exempt.

Usage:
    python3 rites/validate_grimoire_structure.py [--grimoire <path>]

Exit codes: 0 = compliant, 1 = violations
"""

import argparse
import filecmp
import json
import sys
from pathlib import Path

from _lib import default_arcana_root, load_manifest, parse_frontmatter
from diagnostics import DiagnosticReporter, add_output_format_arg
from scaffold_contract import (
    ScaffoldContractError,
    json_requirements,
    load_scaffold_contract,
    managed_scaffold_files,
    required_customized_files,
    required_directories,
    validate_contract_against_formula,
)


def page_type(path):
    """Return a page's declared frontmatter `type`, or None if unreadable/absent."""
    try:
        return parse_frontmatter(path.read_text(encoding="utf-8", errors="replace")).get("type")
    except OSError:
        return None


def main():
    parser = argparse.ArgumentParser(description="Validate grimoire structure")
    parser.add_argument("--grimoire", type=Path, default=Path.cwd(),
                        help="Grimoire root (default: cwd)")
    add_output_format_arg(parser)
    args = parser.parse_args()
    root = args.grimoire.expanduser().resolve()
    arcana_root = default_arcana_root()
    formula_root = arcana_root / "formulae" / "grimoire"
    human = args.format == "human"
    reporter = DiagnosticReporter("validate_grimoire_structure", root)

    if human:
        print()
        print("Validating Grimoire Structure")
        print("==================================")
        print(f"Grimoire root: {root}")
        print()

    try:
        scaffold_contract = load_scaffold_contract(arcana_root)
    except ScaffoldContractError as exc:
        reporter.error("GRIMOIRE_STRUCTURE_CONTRACT_READ", str(exc))
        if not human:
            reporter.emit(args.format)
            return reporter.exit_code()
        print(f"  WARN     {exc}")
        print()
        print("==================================")
        print("Grimoire structure validation failed with 1 issue(s)")
        return 1

    for contract_error in validate_contract_against_formula(scaffold_contract, formula_root):
        reporter.error("GRIMOIRE_STRUCTURE_CONTRACT", contract_error)
        if human:
            print(f"  WARN     scaffold contract error: {contract_error}")

    # 1. Manifest must exist, parse, and declare both 'name' and a valid skill_prefix.
    if not (root / "grimoire.json").is_file():
        reporter.error("GRIMOIRE_STRUCTURE_MISSING_MANIFEST", "missing grimoire.json", path="grimoire.json")
        if human:
            print(f"  MISSING  grimoire.json")
        grimoire_name = root.name
    else:
        manifest, manifest_errors = load_manifest(root)
        if manifest is None:
            # Parse failure - load_manifest reports the cause in errors[0].
            reporter.error("GRIMOIRE_STRUCTURE_INVALID_MANIFEST", manifest_errors[0], path="grimoire.json")
            if human:
                print(f"  WARN     {manifest_errors[0]}")
            grimoire_name = root.name
        else:
            grimoire_name = manifest.get("name", root.name)
            for err_msg in manifest_errors:
                reporter.error("GRIMOIRE_STRUCTURE_INVALID_MANIFEST", err_msg, path="grimoire.json")
                if human:
                    print(f"  WARN     {err_msg}")
            if human:
                print(f"  OK       grimoire.json (name={grimoire_name})")

    # 2. Required root files (other than the dynamic hub name).
    for f in required_customized_files(scaffold_contract):
        if not (root / f).is_file():
            reporter.error("GRIMOIRE_STRUCTURE_MISSING_FILE", f"missing file: {f}", path=f)
            if human:
                print(f"  MISSING  file: {f}")
        else:
            if human:
                print(f"  OK       {f}")

    # 3. Root hub.
    root_hub = root / f"{grimoire_name}.md"
    if not root_hub.is_file():
        reporter.error(
            "GRIMOIRE_STRUCTURE_MISSING_ROOT_HUB",
            f"missing root hub: {grimoire_name}.md",
            path=f"{grimoire_name}.md",
        )
        if human:
            print(f"  MISSING  root hub: {grimoire_name}.md")
    else:
        root_hub_type = page_type(root_hub)
        if root_hub_type != "hub":
            reporter.error(
                "GRIMOIRE_STRUCTURE_HUB_NOT_DECLARED",
                f"root hub {grimoire_name}.md must declare type: hub (found type: {root_hub_type or 'none'})",
                path=f"{grimoire_name}.md",
                docs_reference="docs/operating_model.md",
            )
            if human:
                print(f"  WARN     root hub {grimoire_name}.md must declare type: hub (found {root_hub_type or 'none'})")
        elif human:
            print(f"  OK       {grimoire_name}.md")

    # 4. Required scaffold directories.
    for d in required_directories(scaffold_contract):
        if not (root / d).is_dir():
            reporter.error("GRIMOIRE_STRUCTURE_MISSING_DIR", f"missing directory: {d}", path=d)
            if human:
                print(f"  MISSING  directory: {d}")
        else:
            if human:
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
        if human:
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
                    reporter.error(
                        "GRIMOIRE_STRUCTURE_MISSING_CHAPTER_HUB",
                        f"missing hub: {rel}/{folder.name}.md",
                        path=f"{rel}/{folder.name}.md",
                    )
                    if human:
                        print(f"  MISSING  hub: {rel}/{folder.name}.md")
            else:
                hub_type = page_type(hub)
                if hub_type != "hub":
                    reporter.error(
                        "GRIMOIRE_STRUCTURE_HUB_NOT_DECLARED",
                        f"hub {rel}/{folder.name}.md must declare type: hub (found type: {hub_type or 'none'})",
                        path=f"{rel}/{folder.name}.md",
                        docs_reference="docs/operating_model.md",
                    )
                    if human:
                        print(f"  WARN     hub {rel}/{folder.name}.md must declare type: hub (found {hub_type or 'none'})")
                elif human:
                    print(f"  OK       {rel}/{folder.name}.md")

    # 5b. Declared hubs must sit in a folder-named position (the reverse of the
    # rule above). This closes the if-and-only-if: under chapters/, a page is a
    # hub exactly when its filename stem equals its folder name, so an agent can
    # tell hubs from leaves by path alone without reading frontmatter.
    if chapters.is_dir():
        for page in sorted(chapters.rglob("*.md")):
            if page.stem == page.parent.name:
                continue  # folder-named: the valid hub slot, checked above
            if is_asset_folder(page.parent, root):
                continue  # demonstrative/asset content is exempt
            if page_type(page) == "hub":
                rel = page.relative_to(root)
                reporter.error(
                    "GRIMOIRE_STRUCTURE_HUB_MISPLACED",
                    f"{rel} declares type: hub but is not a folder-named hub "
                    f"(a hub here must be named {page.parent.name}.md)",
                    path=str(rel),
                    docs_reference="docs/operating_model.md",
                )
                if human:
                    print(f"  WARN     {rel} declares type: hub but is not a folder-named hub")

    # 6. sources/ must not contain any wiki content (sanity).
    sources_dir = root / "sources"
    if sources_dir.is_dir():
        # A non-immutable artifact would be a `chapters/` folder under sources/
        forbidden = list(sources_dir.glob("chapters"))
        if forbidden:
            reporter.error(
                "GRIMOIRE_STRUCTURE_SOURCES_CHAPTERS",
                "sources/chapters exists; sources/ is for immutable artifacts",
                path="sources/chapters",
            )
            if human:
                print(f"  WARN     sources/chapters exists - sources/ is for immutable artifacts, not wiki content")

    # 7. Managed scaffold files should match the current Arcana formulae.
    # These files are operational support files, not grimoire-specific content.
    # Root README, root hub, grimoire.json, and log.md are intentionally not
    # compared because they are customized during grimoire creation.
    if formula_root.is_dir():
        if human:
            print()
            print("Checking managed scaffold files against current Arcana formulae...")
        for rel in managed_scaffold_files(scaffold_contract):
            expected = formula_root / rel
            actual = root / rel
            if not expected.is_file():
                reporter.error(
                    "GRIMOIRE_STRUCTURE_FORMULA_MISSING_MANAGED",
                    f"Arcana formula missing managed scaffold: {rel}",
                    path=rel,
                )
                if human:
                    print(f"  WARN     Arcana formula missing managed scaffold: {rel}")
            elif not actual.is_file():
                reporter.error("GRIMOIRE_STRUCTURE_MISSING_MANAGED", f"missing managed scaffold: {rel}", path=rel)
                if human:
                    print(f"  MISSING  managed scaffold: {rel}")
            elif not filecmp.cmp(expected, actual, shallow=False):
                reporter.error(
                    "GRIMOIRE_STRUCTURE_STALE_MANAGED",
                    f"managed scaffold differs from Arcana formula: {rel}",
                    path=rel,
                    hint=f"Copy from ARCANA_HOME/formulae/grimoire/{rel}.",
                )
                if human:
                    print(f"  STALE    managed scaffold differs from Arcana formula: {rel}")
            else:
                if human:
                    print(f"  OK       {rel}")
    else:
        reporter.error("GRIMOIRE_STRUCTURE_FORMULA_ROOT_MISSING", f"Arcana formula root missing: {formula_root}")
        if human:
            print(f"  WARN     Arcana formula root missing: {formula_root}")

    # 8. JSON requirements from the scaffold contract.
    for requirement in json_requirements(scaffold_contract):
        rel = requirement["path"]
        actual = root / rel
        if not actual.is_file():
            reporter.error("GRIMOIRE_STRUCTURE_JSON_MISSING", f"{rel} missing", path=rel)
            if human:
                print(f"  WARN     {rel} missing")
            continue
        try:
            cfg = json.loads(actual.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError) as exc:
            reporter.error("GRIMOIRE_STRUCTURE_JSON_UNREADABLE", f"{rel} unreadable: {exc}", path=rel)
            if human:
                print(f"  WARN     {rel} unreadable: {exc}")
            continue

        for key, expected_value in requirement["required_values"].items():
            actual_value = cfg.get(key)
            if actual_value != expected_value:
                reporter.error(
                    "GRIMOIRE_STRUCTURE_JSON_VALUE",
                    f"{rel} must set {key!r} to {expected_value!r} (got {actual_value!r})",
                    path=rel,
                )
                if human:
                    print(
                        f"  WARN     {rel} must set {key!r} to {expected_value!r} "
                        f"(got {actual_value!r})"
                    )
            else:
                if human:
                    print(f"  OK       {rel} ({key}={expected_value!r})")

    if not human:
        reporter.emit(args.format)
        return reporter.exit_code()

    print()
    print("==================================")
    if reporter.error_count() == 0:
        print("Grimoire structure validation passed")
        return 0
    print(f"Grimoire structure validation failed with {reporter.error_count()} issue(s)")
    return 1


if __name__ == "__main__":
    sys.exit(main())
