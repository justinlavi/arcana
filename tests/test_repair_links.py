"""Temp-target tests for the wikilink repair rite."""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RITE = REPO_ROOT / "rites" / "repair_links.py"


def _run(grimoire: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RITE), "--grimoire", str(grimoire), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def _grimoire(root: Path) -> Path:
    (root / "chapters" / "recipes").mkdir(parents=True)
    (root / "grimoire.json").write_text(
        '{"name": "g", "skill_prefix": "gg", "description": "x"}\n', encoding="utf-8"
    )
    (root / "log.md").write_text("# Log\n", encoding="utf-8")
    (root / "g.md").write_text(
        '---\ntype: hub\ntitle: "G"\ntags: [hub/root]\n---\n# G\n', encoding="utf-8"
    )
    (root / "chapters" / "recipes" / "recipes.md").write_text(
        '---\ntype: hub\ntitle: "Recipes"\ntags: [hub/chapter]\n---\n# Recipes\n',
        encoding="utf-8",
    )
    (root / "chapters" / "recipes" / "sourdough.md").write_text(
        '---\ntype: concept\ntitle: "Sourdough"\ntags: []\n'
        "authority: grimoire\nlast_verified: 2026-05-25\n---\n# Sourdough\n",
        encoding="utf-8",
    )
    return root


def _append(page: Path, text: str) -> None:
    page.write_text(page.read_text(encoding="utf-8") + text, encoding="utf-8")


def test_repair_links_fixes_filename_only_wikilink(tmp_path):
    g = _grimoire(tmp_path / "g")
    page = g / "chapters" / "recipes" / "recipes.md"
    _append(page, "See [[sourdough]].\n")

    result = _run(g, "--apply")

    assert result.returncode == 0
    assert "[[chapters/recipes/sourdough|sourdough]]" in page.read_text(encoding="utf-8")


def test_repair_links_apply_succeeds_despite_unresolvable(tmp_path):
    g = _grimoire(tmp_path / "g")
    page = g / "chapters" / "recipes" / "recipes.md"
    _append(page, "See [[does_not_exist]].\n")

    apply_result = _run(g, "--apply")
    # Apply completed successfully; the unresolvable link is a reported follow-up.
    assert apply_result.returncode == 0
    assert "Unresolvable" in apply_result.stdout

    dry_result = _run(g)
    # Dry-run acts as a check: actionable work present -> non-zero.
    assert dry_result.returncode == 1


def test_repair_links_reports_placeholder_skip(tmp_path):
    g = _grimoire(tmp_path / "g")
    page = g / "chapters" / "recipes" / "recipes.md"
    _append(page, "See [[Title]].\n")

    result = _run(g)

    assert "Skipped" in result.stdout
    assert "[[Title]]" in result.stdout
    # The placeholder-like link is reported, never silently dropped or rewritten.
    assert "[[Title]]" in page.read_text(encoding="utf-8")


def test_repair_links_json_envelope_on_apply(tmp_path):
    g = _grimoire(tmp_path / "g")
    page = g / "chapters" / "recipes" / "recipes.md"
    _append(page, "See [[sourdough]].\n")

    result = _run(g, "--apply", "--format", "json")

    # Apply preserves its exit code (0) and stdout must be a single JSON object.
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["rite"] == "repair_links"
    assert report["mode"] == "apply"
    assert report["status"] == "ok"
    assert report["summary"]["repairs"] == 1
    assert report["summary"]["files_touched"] == 1
    assert report["mutations"][0]["action"] == "repair"
    assert "[[sourdough]] -> [[chapters/recipes/sourdough|sourdough]]" in (
        report["mutations"][0]["detail"]
    )
    # The repair was actually written.
    assert "[[chapters/recipes/sourdough|sourdough]]" in page.read_text(encoding="utf-8")


def test_repair_links_json_plan_mode_reports_unresolvable(tmp_path):
    g = _grimoire(tmp_path / "g")
    page = g / "chapters" / "recipes" / "recipes.md"
    _append(page, "See [[does_not_exist]].\n")

    result = _run(g, "--format", "json")

    # Dry-run preserves its non-zero exit for actionable work; stdout is clean JSON.
    assert result.returncode == 1
    report = json.loads(result.stdout)
    assert report["rite"] == "repair_links"
    assert report["mode"] == "plan"
    assert report["summary"]["unresolvable"] == 1
    assert any(m["severity"] == "warning" for m in report["messages"])
    # Plan mode records no disk mutations.
    assert report["mutations"] == []


def test_repair_links_json_clean_grimoire_is_noop(tmp_path):
    g = _grimoire(tmp_path / "g")

    result = _run(g, "--format", "json")

    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["status"] == "noop"
    assert report["summary"]["repairs"] == 0
    assert report["mutations"] == []
