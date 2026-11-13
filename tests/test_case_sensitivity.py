"""Case-exact links and case-collision portability.

A link that differs from the on-disk spelling only by case resolves on Windows
and macOS and breaks on Linux, in site builds, and in Obsidian on Linux. The
validators must flag it on every platform: as a case mismatch where the
filesystem ignores case, and as a broken link with a casing hint where it does
not.
"""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import _lib
import validate_portability

REPO_ROOT = Path(__file__).resolve().parent.parent
RITES = REPO_ROOT / "rites"
GOOD = Path(__file__).parent / "fixtures" / "good_grimoire"


def _run_json(script: str, grimoire: Path) -> dict:
    result = subprocess.run(
        [sys.executable, str(RITES / script), "--grimoire", str(grimoire), "--format", "json"],
        capture_output=True, text=True, timeout=60,
    )
    return {"returncode": result.returncode, "report": json.loads(result.stdout)}


def _case_insensitive(tmp_path: Path) -> bool:
    probe = tmp_path / "CaseProbe.txt"
    probe.write_text("x", encoding="utf-8")
    return (tmp_path / "caseprobe.txt").exists()


def _codes(report: dict) -> list:
    return [d["code"] for d in report["diagnostics"]]


def _hints(report: dict, code: str) -> list:
    return [d.get("hint", "") for d in report["diagnostics"] if d["code"] == code]


def test_spell_on_disk_returns_actual_casing(tmp_path):
    (tmp_path / "Chapters" / "Recipes").mkdir(parents=True)
    (tmp_path / "Chapters" / "Recipes" / "Sourdough.md").write_text("x", encoding="utf-8")
    _lib._LISTDIR_CACHE.clear()

    assert _lib.spell_on_disk("chapters/recipes/sourdough.md", tmp_path) == "Chapters/Recipes/Sourdough.md"
    assert _lib.spell_on_disk("Chapters/Recipes/Sourdough.md", tmp_path) == "Chapters/Recipes/Sourdough.md"
    assert _lib.spell_on_disk("chapters/recipes/nope.md", tmp_path) is None
    assert _lib.spell_on_disk("Chapters/../Chapters/Recipes", tmp_path) == "Chapters/../Chapters/Recipes"


def test_find_case_collisions_groups_names():
    groups = validate_portability.find_case_collisions(
        ["Sourdough.md", "sourdough.md", "recipes.md", "SOURDOUGH.md", "notes"]
    )
    assert groups == [["SOURDOUGH.md", "Sourdough.md", "sourdough.md"]]
    assert validate_portability.find_case_collisions(["a.md", "b.md"]) == []


def test_wrong_case_wikilink_is_flagged_on_every_platform(tmp_path):
    grimoire = tmp_path / "g"
    shutil.copytree(GOOD, grimoire)
    page = grimoire / "chapters" / "recipes" / "case_probe.md"
    page.write_text(
        "---\ntype: concept\ntitle: \"Case Probe\"\ntags: [chapter/recipes, type/concept]\n"
        "authority: grimoire\nlast_verified: 2026-11-10\n---\n\n# Case Probe\n\n"
        "See [[chapters/RECIPES/sourdough|sourdough]].\n",
        encoding="utf-8", newline="\n",
    )

    out = _run_json("validate_links.py", grimoire)
    codes = _codes(out["report"])

    assert out["returncode"] != 0
    if _case_insensitive(tmp_path):
        assert "LINK_CASE_MISMATCH" in codes, codes
        assert any("chapters/recipes/sourdough.md" in h for h in _hints(out["report"], "LINK_CASE_MISMATCH"))
    else:
        assert "LINK_WIKILINK_BROKEN" in codes, codes
        assert any("[[chapters/recipes/sourdough]]" in h for h in _hints(out["report"], "LINK_WIKILINK_BROKEN"))


def test_wrong_case_markdown_link_is_flagged_on_every_platform(tmp_path):
    grimoire = tmp_path / "g"
    shutil.copytree(GOOD, grimoire)
    readme = grimoire / "README.md"
    readme.write_text(
        readme.read_text(encoding="utf-8") + "\nSee [the hub](GOOD_GRIMOIRE.md).\n",
        encoding="utf-8", newline="\n",
    )

    out = _run_json("validate_links.py", grimoire)
    codes = _codes(out["report"])

    assert out["returncode"] != 0
    if _case_insensitive(tmp_path):
        assert "LINK_MARKDOWN_CASE_MISMATCH" in codes, codes
        assert any("good_grimoire.md" in h for h in _hints(out["report"], "LINK_MARKDOWN_CASE_MISMATCH"))
    else:
        assert "LINK_MARKDOWN_BROKEN" in codes, codes
        assert any("good_grimoire.md" in h for h in _hints(out["report"], "LINK_MARKDOWN_BROKEN"))


def test_exact_case_links_stay_clean(tmp_path):
    grimoire = tmp_path / "g"
    shutil.copytree(GOOD, grimoire)
    assert _run_json("validate_links.py", grimoire)["returncode"] == 0
    assert _run_json("validate_portability.py", grimoire)["returncode"] == 0
