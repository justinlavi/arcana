"""Contract tests for the full grimoire scaffold formula."""

import re
import shutil
import subprocess
import sys
from pathlib import Path

from scaffold_contract import (
    directory_entries,
    file_entries,
    load_scaffold_contract,
    managed_scaffold_files,
    uncovered_formula_paths,
    validate_contract_against_formula,
)

REPO_ROOT = Path(__file__).resolve().parent.parent
FORMULA_ROOT = REPO_ROOT / "formulae" / "grimoire"
RITES = REPO_ROOT / "rites"


def _run(script: str, grimoire: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RITES / script), "--grimoire", str(grimoire)],
        capture_output=True,
        text=True,
        timeout=30,
    )


def _replace_placeholders(root: Path, replacements: dict[str, str]) -> None:
    pattern = re.compile(r"\{\{[A-Z0-9_]+\}\}")
    for path in sorted(root.rglob("*")):
        if not path.is_file() or path.suffix not in {".md", ".json"}:
            continue
        text = path.read_text(encoding="utf-8")
        for key, value in replacements.items():
            text = text.replace(key, value)
        leftovers = sorted(set(pattern.findall(text)))
        assert not leftovers, f"{path.relative_to(root)} still has placeholders: {leftovers}"
        path.write_text(text, encoding="utf-8", newline="\n")


def _expand_target(path: str, replacements: dict[str, str]) -> Path:
    expanded = path
    for key, value in replacements.items():
        expanded = expanded.replace(key, value)
    return Path(expanded)


def _scaffold_from_contract(grimoire: Path, replacements: dict[str, str]) -> None:
    contract = load_scaffold_contract(REPO_ROOT)
    contract_errors = validate_contract_against_formula(contract, FORMULA_ROOT)
    assert not contract_errors
    assert uncovered_formula_paths(contract, FORMULA_ROOT) == []

    grimoire.mkdir()
    for entry in directory_entries(contract):
        if entry.get("create"):
            (grimoire / _expand_target(entry["path"], replacements)).mkdir(parents=True, exist_ok=True)

    for entry in file_entries(contract, include_root_hub=True):
        if not entry.get("create"):
            continue
        source = FORMULA_ROOT / entry["source"]
        target = grimoire / _expand_target(entry["target"], replacements)
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)


def test_grimoire_scaffold_contract_covers_formula_sources():
    contract = load_scaffold_contract(REPO_ROOT)

    assert validate_contract_against_formula(contract, FORMULA_ROOT) == []
    assert uncovered_formula_paths(contract, FORMULA_ROOT) == []
    assert set(managed_scaffold_files(contract)) == {
        ".editorconfig",
        ".gitattributes",
        ".obsidian/app.json",
        ".obsidian/graph.json",
        "inbox/README.md",
        "sources/README.md",
    }


def test_grimoire_scaffold_formula_expands_to_valid_grimoire(tmp_path):
    grimoire = tmp_path / "cooking-grimoire"
    replacements = {
        "{{GRIMOIRE_NAME}}": "Cooking",
        "{{GRIMOIRE_NAME_LOWER}}": "cooking",
        "{{GRIMOIRE_DIRECTORY}}": "cooking-grimoire",
        "{{GRIMOIRE_TOKEN}}": "COOKING",
        "{{GRIMOIRE_DOMAIN}}": "cooking",
        "{{GRIMOIRE_PURPOSE}}": "personal cooking knowledge",
        "{{GRIMOIRE_PURPOSE_DETAILED}}": "Recipes, techniques, equipment, and ingredient inventories.",
        "{{GRIMOIRE_REPO_URL}}": "https://git.example.com/you/cooking-grimoire.git",
        "{{SKILL_PREFIX}}": "cook",
        "{{CHAPTER_ROUTES}}": "- Recipes -> [[chapters/recipes/recipes|recipes]]",
        "{{CHAPTER_LIST}}": "- **recipes** - documented recipes and techniques",
        "{{CHAPTER_TREE}}": "|-- chapters/\n|   |-- recipes/\n|       |-- recipes.md",
        "{{EXAMPLE_CHAPTER}}": "recipes",
        "{{OWNER_DOMAIN}}": "Personal",
        "{{CREATION_DATE}}": "2026-05-25",
    }

    _scaffold_from_contract(grimoire, replacements)

    recipes = grimoire / "chapters" / "recipes"
    recipes.mkdir(parents=True)
    (recipes / "recipes.md").write_text(
        """---
type: hub
title: "Recipes"
aliases: ["recipes"]
tags: [chapter/recipes, type/hub, hub/chapter]
---

# Recipes

## Routes

Add recipe pages here as they are created.
""",
        encoding="utf-8",
        newline="\n",
    )

    _replace_placeholders(grimoire, replacements)

    for script in [
        "validate_grimoire_structure.py",
        "validate_frontmatter.py",
        "validate_links.py",
        "validate_orphans.py",
        "validate_provenance.py",
    ]:
        result = _run(script, grimoire)
        assert result.returncode == 0, (
            f"{script} failed for expanded scaffold\n"
            f"--- stdout ---\n{result.stdout}\n--- stderr ---\n{result.stderr}"
        )
