#!/usr/bin/env python3
"""Validates Arcana structure completeness.

Usage: python3 rites/validate_structure.py
Exit codes: 0 = success, 1 = validation errors found

Hub convention (v2):
    For any folder F that acts as a router, the hub file is F/<basename(F)>.md.
    The Arcana root hub is arcana.md; the grimoire/ invocation router is
    invocations/grimoire/grimoire.md; etc.

Documentation index coverage:
    Every docs/*.md page (and CONTRIBUTING.md) must be reachable from both
    routing surfaces - arcana.md and README.md - so a new doc never silently
    falls out of the primer. This makes that coverage a runtime validator check,
    not only a pytest assertion.
"""

import sys
from pathlib import Path

from _lib import default_arcana_root
from agent_targets import target_entries, validate_agent_targets
from diagnostics import DiagnosticReporter, add_output_format_arg
from rite_profiles import profile_entries, validate_rite_profiles
from summon_contract import mode_entries, validate_summon_contract

ARCANA_ROOT = default_arcana_root()

REQUIRED_DIRS = [
    "docs",
    "invocations/grimoire",
    "invocations/grimoire/validators",
    "invocations/arcana",
    "invocations/arcana/quality",
    "invocations/arcana/validators",
    "invocations/agent",
    "invocations/help",
    "invocations/library",
    "invocations/meta",
    "invocations/workspace",
    "formulae",
    "formulae/grimoire",
    "rites",
    "resources",
    "skills",
    "skills/arcana",
    "skills/grimoire",
    "skills/agent",
    "skills/library",
    "skills/workspace",
    "skills/help",
]

REQUIRED_FILES = [
    "arcana.md",
    "README.md",
    "UPDATE.md",
    "CHANGELOG.md",
    "VERSION",
    "arcana.json",
    "rites/summon.sh",
    "rites/sync_skills.py",
    "docs/installation.md",
    "docs/agent_targets.md",
    "docs/summoning_contract.md",
    "docs/agent_configuration.md",
    "docs/operating_model.md",
    "docs/governance.md",
    "docs/reference.md",
    "docs/page_schema.md",
]

FORBIDDEN_GRIMOIRE_LAYER_PATHS = [
    "chapters",
    "sources",
    "inbox",
    "log.md",
    "grimoire.json",
]

# Folders whose hub file must exist with the folder-name convention.
HUB_DIRS = [
    "invocations/grimoire",
    "invocations/grimoire/validators",
    "invocations/arcana",
    "invocations/arcana/quality",
    "invocations/arcana/validators",
    "invocations/agent",
    "invocations/help",
    "invocations/library",
    "invocations/meta",
    "invocations/workspace",
]


def hub_path(rel_dir):
    """Resolve the hub file path for a folder using the F/F.md convention."""
    folder = ARCANA_ROOT / rel_dir
    return folder / f"{folder.name}.md"


def _docs_files(root):
    """Return every docs/*.md page, sorted; empty when docs/ is absent."""
    docs = root / "docs"
    return sorted(docs.glob("*.md")) if docs.is_dir() else []


def doc_index_violations(root):
    """Return (code, path, message) for any docs/ page or CONTRIBUTING.md the
    routing surfaces fail to reference.

    A new docs/ page must be reachable from both routing surfaces so it never
    silently falls out of the primer: arcana.md (the vault hub, which links docs
    as `[[docs/<stem>|...]]`) and README.md (the public doc, which links them as
    `(docs/<name>)`). This is the runtime form of the coverage tests/test_doc_indexes
    asserts; both share this single implementation.
    """
    hub = root / "arcana.md"
    readme = root / "README.md"
    hub_text = hub.read_text(encoding="utf-8", errors="replace") if hub.is_file() else None
    readme_text = readme.read_text(encoding="utf-8", errors="replace") if readme.is_file() else None

    violations = []
    for doc in _docs_files(root):
        if hub_text is not None and f"docs/{doc.stem}" not in hub_text:
            violations.append(("STRUCTURE_DOC_NOT_IN_HUB", f"docs/{doc.name}",
                               f"docs/{doc.name} is not routed from arcana.md"))
        if readme_text is not None and f"docs/{doc.name}" not in readme_text:
            violations.append(("STRUCTURE_DOC_NOT_IN_README", f"docs/{doc.name}",
                               f"docs/{doc.name} is not linked from README.md"))

    if (root / "CONTRIBUTING.md").is_file():
        if hub_text is not None and "CONTRIBUTING" not in hub_text:
            violations.append(("STRUCTURE_DOC_NOT_IN_HUB", "CONTRIBUTING.md",
                               "CONTRIBUTING.md is not referenced from arcana.md"))
        if readme_text is not None and "CONTRIBUTING" not in readme_text:
            violations.append(("STRUCTURE_DOC_NOT_IN_README", "CONTRIBUTING.md",
                               "CONTRIBUTING.md is not referenced from README.md"))
    return violations


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Validate Arcana structure completeness")
    add_output_format_arg(parser)
    args = parser.parse_args()
    human = args.format == "human"
    reporter = DiagnosticReporter("validate_structure", ARCANA_ROOT)

    if human:
        print()
        print("Validating Arcana Structure")
        print("==================================")
        print(f"Arcana root: {ARCANA_ROOT}")
        print()

    if human:
        print("Checking required directories...")
    for d in REQUIRED_DIRS:
        path = ARCANA_ROOT / d
        if not path.is_dir():
            reporter.error("STRUCTURE_MISSING_DIR", f"missing directory: {d}", path=d)
            if human:
                print(f"  MISSING  directory: {d}")
        else:
            if human:
                print(f"  OK       {d}")
    if human:
        print()

    if human:
        print("Checking required files...")
    for f in REQUIRED_FILES:
        path = ARCANA_ROOT / f
        if not path.is_file():
            reporter.error("STRUCTURE_MISSING_FILE", f"missing file: {f}", path=f)
            if human:
                print(f"  MISSING  file: {f}")
        else:
            if human:
                print(f"  OK       {f}")
    if human:
        print()

    if human:
        print("Checking Arcana root excludes grimoire layers...")
    for rel in FORBIDDEN_GRIMOIRE_LAYER_PATHS:
        path = ARCANA_ROOT / rel
        if path.exists():
            reporter.error(
                "STRUCTURE_FORBIDDEN_GRIMOIRE_LAYER",
                "grimoire layer belongs in formulae/grimoire/",
                path=rel,
            )
            if human:
                print(f"  FORBIDDEN root path: {rel} (grimoire layer belongs in formulae/grimoire/)")
        else:
            if human:
                print(f"  OK       no {rel}")
    if human:
        print()

    if human:
        print("Checking router hub files (folder-name convention)...")
    for d in HUB_DIRS:
        hub = hub_path(d)
        rel = hub.relative_to(ARCANA_ROOT)
        if not hub.is_file():
            reporter.error("STRUCTURE_MISSING_HUB", f"missing hub file: {rel}", path=rel)
            if human:
                print(f"  MISSING  hub file: {rel}")
        else:
            if human:
                print(f"  OK       {rel}")
    if human:
        print()

    if human:
        print("Checking documentation index coverage...")
    doc_violations = doc_index_violations(ARCANA_ROOT)
    for code, path, message in doc_violations:
        reporter.error(code, message, path=path, docs_reference="docs/governance.md")
        if human:
            print(f"  MISSING  {message}")
    if human and not doc_violations:
        print("  OK       every docs/ page is routed from arcana.md and linked from README.md")
    if human:
        print()

    if human:
        print("Checking mutating rite profiles...")
    rite_profile_contract, rite_profile_errors = validate_rite_profiles(ARCANA_ROOT)
    for error in rite_profile_errors:
        reporter.error(
            error["code"],
            error["message"],
            path=error.get("path"),
            hint=error.get("hint"),
        )
        if human:
            print(f"  PROFILE  {error.get('path', '-')}: {error['message']}")
    rite_profile_count = (
        len(profile_entries(rite_profile_contract))
        if rite_profile_contract is not None
        else 0
    )
    if human and not rite_profile_errors:
        print(f"  OK       {rite_profile_count} mutating rite profile(s)")
    if human:
        print()

    if human:
        print("Checking Summoning Rite contract...")
    summon_contract, summon_contract_errors = validate_summon_contract(ARCANA_ROOT)
    for error in summon_contract_errors:
        reporter.error(
            error["code"],
            error["message"],
            path=error.get("path"),
            hint=error.get("hint"),
        )
        if human:
            print(f"  CONTRACT {error.get('path', '-')}: {error['message']}")
    summon_mode_count = (
        len(mode_entries(summon_contract))
        if summon_contract is not None
        else 0
    )
    if human and not summon_contract_errors:
        print(f"  OK       {summon_mode_count} Summoning Rite mode(s)")
    if human:
        print()

    if human:
        print("Checking agent target registry...")
    agent_target_contract, agent_target_errors = validate_agent_targets(ARCANA_ROOT)
    for error in agent_target_errors:
        reporter.error(
            error["code"],
            error["message"],
            path=error.get("path"),
            hint=error.get("hint"),
        )
        if human:
            print(f"  AGENT   {error.get('path', '-')}: {error['message']}")
    agent_target_count = (
        len(target_entries(agent_target_contract))
        if agent_target_contract is not None
        else 0
    )
    if human and not agent_target_errors:
        print(f"  OK       {agent_target_count} agent target(s)")
    if human:
        print()

    if not human:
        reporter.emit(
            args.format,
            checked={
                "required_directories": len(REQUIRED_DIRS),
                "required_files": len(REQUIRED_FILES),
                "hub_directories": len(HUB_DIRS),
                "rite_profiles": rite_profile_count,
                "summon_modes": summon_mode_count,
                "agent_targets": agent_target_count,
            },
        )
        return reporter.exit_code()

    print("==================================")
    if reporter.error_count() == 0:
        print("Structure validation passed")
        return 0
    else:
        print(f"Structure validation failed with {reporter.error_count()} errors")
        return 1


if __name__ == "__main__":
    sys.exit(main())
