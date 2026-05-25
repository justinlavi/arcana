"""Contract tests for the full grimoire scaffold formula."""

import re
import shutil
import subprocess
import sys
from pathlib import Path

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


def test_grimoire_scaffold_formula_expands_to_valid_grimoire(tmp_path):
    grimoire = tmp_path / "cooking-grimoire"
    shutil.copytree(FORMULA_ROOT, grimoire)

    (grimoire / "root_hub.formula.md").rename(grimoire / "cooking-grimoire.md")
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
