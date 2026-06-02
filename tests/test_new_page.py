"""Tests for the new_page stamping rite.

Invokes the rite as a subprocess against the good_grimoire fixture, the same way
the create-chapter flow does, and confirms the stamped page satisfies the
frontmatter schema validator.
"""

import datetime
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RITES = REPO_ROOT / "rites"
GOOD = Path(__file__).parent / "fixtures" / "good_grimoire"


def _run(grimoire: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RITES / "new_page.py"), "--grimoire", str(grimoire), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def _validate_frontmatter(grimoire: Path) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RITES / "validate_frontmatter.py"),
         "--grimoire", str(grimoire), "--format", "json"],
        capture_output=True,
        text=True,
        timeout=30,
    )


def _good_copy(tmp_path: Path) -> Path:
    grimoire = tmp_path / "g"
    shutil.copytree(GOOD, grimoire)
    return grimoire


def test_dry_run_previews_without_writing(tmp_path):
    g = _good_copy(tmp_path)
    target = g / "chapters/recipes/new_topic.md"

    result = _run(g, "--path", "chapters/recipes/new_topic.md",
                  "--type", "concept", "--title", "New Topic")

    assert result.returncode == 0, result.stderr
    assert "Would create" in result.stdout
    assert not target.exists()


def test_apply_creates_schema_valid_page_stamped_today(tmp_path):
    g = _good_copy(tmp_path)
    rel = "chapters/recipes/new_topic.md"
    target = g / rel

    result = _run(g, "--path", rel, "--type", "concept", "--title", "New Topic", "--apply")

    assert result.returncode == 0, result.stderr
    assert target.exists()
    text = target.read_text(encoding="utf-8")
    today = datetime.date.today().isoformat()
    assert f"last_verified: {today}" in text
    assert 'title: "New Topic"' in text
    assert "type: concept" in text
    assert "chapter/recipes" in text  # chapter facet derived from the path
    # The formula placeholders must be gone.
    assert "1970-01-01" not in text
    assert "[Title]" not in text

    # The stamped page must satisfy the schema validator that item 1 hardened.
    validation = _validate_frontmatter(g)
    assert validation.returncode == 0, validation.stdout


def test_refuses_to_overwrite_existing_page(tmp_path):
    g = _good_copy(tmp_path)
    # sourdough.md already exists in the fixture.
    result = _run(g, "--path", "chapters/recipes/sourdough.md",
                  "--type", "concept", "--title", "Dup", "--apply")

    assert result.returncode != 0
    assert "refusing to overwrite" in (result.stdout + result.stderr)


def test_path_must_live_under_chapters(tmp_path):
    g = _good_copy(tmp_path)
    result = _run(g, "--path", "sources/stray.md",
                  "--type", "concept", "--title", "Stray", "--apply")

    assert result.returncode != 0
    assert not (g / "sources/stray.md").exists()


def test_external_authority_requires_sources(tmp_path):
    g = _good_copy(tmp_path)
    result = _run(g, "--path", "chapters/recipes/ext.md",
                  "--type", "concept", "--title", "Ext", "--authority", "external", "--apply")

    assert result.returncode != 0
    assert not (g / "chapters/recipes/ext.md").exists()


def test_external_authority_with_sources_is_valid(tmp_path):
    g = _good_copy(tmp_path)
    rel = "chapters/recipes/ext.md"

    result = _run(g, "--path", rel, "--type", "concept", "--title", "Ext",
                  "--authority", "external", "--sources", "https://example.com/recipe", "--apply")

    assert result.returncode == 0, result.stderr
    text = (g / rel).read_text(encoding="utf-8")
    assert "authority: external" in text
    assert 'sources: ["https://example.com/recipe"]' in text

    validation = _validate_frontmatter(g)
    assert validation.returncode == 0, validation.stdout
