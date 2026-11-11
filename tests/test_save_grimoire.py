"""save_grimoire.py validates, commits, rebases, and pushes a grimoire (AB-10)."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RITE = REPO_ROOT / "rites" / "save_grimoire.py"
GOOD = Path(__file__).parent / "fixtures" / "good_grimoire"


def _git(root: Path, *args: str) -> str:
    proc = subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)
    return proc.stdout


def _identity(root: Path) -> None:
    _git(root, "config", "user.email", "t@example.com")
    _git(root, "config", "user.name", "Tester")


def _shared_setup(tmp_path: Path):
    """A bare remote plus two clones (alice, bob) of the good fixture."""
    seed = tmp_path / "seed"
    shutil.copytree(GOOD, seed)
    _git(seed, "init", "-q", "-b", "main")
    _identity(seed)
    _git(seed, "add", "-A")
    _git(seed, "commit", "-q", "-m", "scaffold")
    bare = tmp_path / "remote.git"
    _git(seed, "clone", "-q", "--bare", str(seed), str(bare))
    # The root hub is <directory>.md, so each clone keeps the fixture's name.
    alice = tmp_path / "alice" / "good_grimoire"
    bob = tmp_path / "bob" / "good_grimoire"
    alice.parent.mkdir()
    bob.parent.mkdir()
    subprocess.run(["git", "clone", "-q", str(bare), str(alice)], check=True)
    subprocess.run(["git", "clone", "-q", str(bare), str(bob)], check=True)
    _identity(alice)
    _identity(bob)
    return bare, alice, bob


def _run(root: Path, *extra: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(RITE), "--grimoire", str(root), "--format", "json", *extra],
        capture_output=True, text=True, timeout=600,
    )
    return {"returncode": result.returncode, "report": json.loads(result.stdout), "stderr": result.stderr}


def _add_page(root: Path, slug: str, title: str) -> Path:
    page = root / "chapters" / "recipes" / f"{slug}.md"
    page.write_text(
        f"---\ntype: concept\ntitle: \"{title}\"\ntags: [chapter/recipes, type/concept]\n"
        f"authority: grimoire\nlast_verified: 2026-11-11\n---\n\n# {title}\n",
        encoding="utf-8", newline="\n",
    )
    hub = root / "chapters" / "recipes" / "recipes.md"
    hub.write_text(hub.read_text(encoding="utf-8") + f"- {title} -> [[chapters/recipes/{slug}|{slug}]]\n", encoding="utf-8", newline="\n")
    return page


def test_plan_lists_changes_and_writes_nothing(tmp_path):
    _, alice, _ = _shared_setup(tmp_path)
    _add_page(alice, "focaccia", "Focaccia")

    out = _run(alice, "--no-fetch")
    report = out["report"]

    assert out["returncode"] == 0
    assert report["mode"] == "plan"
    assert report["status"] == "noop"
    assert report["mutations"] == []
    paths = {c["path"] for c in report["summary"]["changes"]}
    assert "chapters/recipes/focaccia.md" in paths
    assert report["summary"]["upstream"] == "origin/main"
    assert _git(alice, "status", "--porcelain").strip() != ""  # still unsaved


def test_nothing_to_save_is_noop(tmp_path):
    _, alice, _ = _shared_setup(tmp_path)
    out = _run(alice, "--apply", "--message", "x")
    assert out["returncode"] == 0
    assert out["report"]["status"] == "noop"


def test_apply_commits_and_pushes(tmp_path):
    bare, alice, bob = _shared_setup(tmp_path)
    _add_page(alice, "focaccia", "Focaccia")

    out = _run(alice, "--apply", "--message", "Add focaccia page")
    report = out["report"]

    assert out["returncode"] == 0, out
    assert report["status"] == "ok"
    assert [m["action"] for m in report["mutations"]] == ["commit", "push"]
    assert report["summary"]["pushed"] is True
    assert "Add focaccia page" in _git(bare, "log", "--oneline", "-1")
    assert _git(alice, "status", "--porcelain").strip() == ""

    # Bob receives it with a plain pull: the push was a normal fast-forward.
    _git(bob, "pull", "-q", "--ff-only")
    assert (bob / "chapters" / "recipes" / "focaccia.md").is_file()


def test_apply_refuses_when_validation_fails(tmp_path):
    _, alice, _ = _shared_setup(tmp_path)
    page = _add_page(alice, "broken", "Broken")
    page.write_text(page.read_text(encoding="utf-8") + "\nSee [[chapters/nope/missing|missing]].\n", encoding="utf-8")

    out = _run(alice, "--apply", "--message", "Add broken page", "--no-fetch")
    report = out["report"]

    assert out["returncode"] == 1
    assert report["status"] == "blocked"
    assert any("validation failed" in m["message"] for m in report["messages"])
    assert _git(alice, "log", "--oneline").count("\n") == 1  # only the scaffold commit


def test_conflict_is_blocked_with_rebase_aborted_and_commit_kept(tmp_path):
    bare, alice, bob = _shared_setup(tmp_path)
    hub = "chapters/recipes/recipes.md"

    # Bob changes the hub and shares it first.
    (bob / hub).write_text((bob / hub).read_text(encoding="utf-8") + "- Bob's line\n", encoding="utf-8", newline="\n")
    _git(bob, "add", "-A")
    _git(bob, "commit", "-q", "-m", "Bob edits hub")
    _git(bob, "push", "-q")

    # Alice changes the same spot without pulling.
    (alice / hub).write_text((alice / hub).read_text(encoding="utf-8") + "- Alice's line\n", encoding="utf-8", newline="\n")

    out = _run(alice, "--apply", "--message", "Alice edits hub")
    report = out["report"]

    assert out["returncode"] == 1
    assert report["status"] == "blocked"
    assert any("teammates changed the same lines" in m["message"] and hub in m["message"] for m in report["messages"])
    assert [m["action"] for m in report["mutations"]] == ["commit"]  # committed locally, not pushed
    assert not (alice / ".git" / "rebase-merge").exists()
    assert not (alice / ".git" / "rebase-apply").exists()
    assert "Alice edits hub" in _git(alice, "log", "--oneline", "-1")
    assert "Bob edits hub" in _git(bare, "log", "--oneline", "-1")
    assert _git(alice, "status", "--porcelain").strip() == ""


def test_not_a_git_repository_is_blocked(tmp_path):
    root = tmp_path / "g"
    shutil.copytree(GOOD, root)
    out = _run(root)
    assert out["returncode"] == 1
    assert out["report"]["status"] == "blocked"
    assert any("not a git repository" in m["message"] for m in out["report"]["messages"])
