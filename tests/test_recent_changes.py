"""recent_changes.py renders grimoire content history from git."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import recent_changes

REPO_ROOT = Path(__file__).resolve().parent.parent
RITE = REPO_ROOT / "rites" / "recent_changes.py"
GOOD = Path(__file__).parent / "fixtures" / "good_grimoire"


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)


def _run(root: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RITE), "--grimoire", str(root), *extra],
        capture_output=True, text=True, timeout=60,
    )


def _repo_with_history(tmp_path: Path) -> Path:
    root = tmp_path / "g"
    shutil.copytree(GOOD, root)
    _git(root, "init", "-q")
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "Tester")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "scaffold")
    page = root / "chapters" / "recipes" / "focaccia.md"
    page.write_text(
        "---\ntype: concept\ntitle: \"Focaccia\"\ntags: [chapter/recipes, type/concept]\n"
        "authority: grimoire\nlast_verified: 2026-11-10\n---\n\n# Focaccia\n",
        encoding="utf-8", newline="\n",
    )
    (root / "notes.txt").write_text("not content\n", encoding="utf-8")
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", "Add focaccia page")
    return root


def test_normalize_since_shorthand():
    assert recent_changes.normalize_since("30d") == "30 days ago"
    assert recent_changes.normalize_since("2w") == "2 weeks ago"
    assert recent_changes.normalize_since("2026-01-01") == "2026-01-01"
    assert recent_changes.normalize_since("3 months ago") == "3 months ago"


def test_json_envelope_lists_content_commits_only(tmp_path):
    root = _repo_with_history(tmp_path)
    result = _run(root, "--format", "json")
    assert result.returncode == 0, result.stderr
    report = json.loads(result.stdout)

    assert report["rite"] == "recent_changes"
    assert report["status"] == "ok"
    assert report["mode"] == "read"
    assert report["mutations"] == []
    commits = report["summary"]["commits"]
    assert [c["subject"] for c in commits] == ["Add focaccia page", "scaffold"]
    focaccia = commits[0]
    assert {"status": "added", "path": "chapters/recipes/focaccia.md"} in focaccia["files"]
    # notes.txt is outside the content paths and must not appear.
    assert all("notes.txt" != f["path"] for c in commits for f in c["files"])
    assert report["summary"]["commit_count"] == 2


def test_human_output_renders_a_table(tmp_path):
    root = _repo_with_history(tmp_path)
    result = _run(root, "--since", "1w")
    assert result.returncode == 0
    assert "Add focaccia page" in result.stdout
    assert "chapters/recipes/focaccia.md" in result.stdout


def test_no_git_repository_is_noop_not_error(tmp_path):
    root = tmp_path / "g"
    shutil.copytree(GOOD, root)
    result = _run(root, "--format", "json")
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["status"] == "noop"
    assert report["summary"]["history"] == "none"
    assert any("no history" in m["message"] for m in report["messages"])
