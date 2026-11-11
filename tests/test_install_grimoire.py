"""install_grimoire.py clones a grimoire into the home and registers it."""

import json
import shutil
import subprocess
import sys
from pathlib import Path

import install_grimoire

REPO_ROOT = Path(__file__).resolve().parent.parent
RITE = REPO_ROOT / "rites" / "install_grimoire.py"
GOOD = Path(__file__).parent / "fixtures" / "good_grimoire"


def _git(root: Path, *args: str) -> None:
    subprocess.run(["git", "-C", str(root), *args], check=True, capture_output=True, text=True)


def _bare_remote(tmp_path: Path, name: str, with_manifest: bool = True) -> Path:
    work = tmp_path / f"{name}-work"
    shutil.copytree(GOOD, work)
    if not with_manifest:
        (work / "grimoire.json").unlink()
    _git(work, "init", "-q", "-b", "main")
    _git(work, "config", "user.email", "t@example.com")
    _git(work, "config", "user.name", "Tester")
    _git(work, "add", "-A")
    _git(work, "commit", "-q", "-m", "scaffold")
    bare = tmp_path / f"{name}.git"
    _git(work, "clone", "-q", "--bare", str(work), str(bare))
    return bare


def _run(url: str, home: Path, *extra: str) -> dict:
    result = subprocess.run(
        [sys.executable, str(RITE), url, "--home", str(home), "--no-skills", "--format", "json", *extra],
        capture_output=True, text=True, timeout=120,
    )
    return {"returncode": result.returncode, "report": json.loads(result.stdout), "stderr": result.stderr}


def test_derive_key_from_urls():
    assert install_grimoire.derive_key("https://gitlab.example.com/team/kutta-grimoire.git") == "kutta-grimoire"
    assert install_grimoire.derive_key("git@github.com:you/cooking-grimoire.git") == "cooking-grimoire"
    assert install_grimoire.derive_key("https://github.com/you/notes") == "notes"


def test_join_clones_and_registers(tmp_path):
    remote = _bare_remote(tmp_path, "recipes-grimoire")
    home = tmp_path / "home"

    out = _run(str(remote), home)
    report = out["report"]

    assert out["returncode"] == 0, out
    assert report["status"] == "ok"
    assert (home / "recipes-grimoire" / "grimoire.json").is_file()
    actions = [m["action"] for m in report["mutations"]]
    assert actions == ["clone", "register"]
    library = json.loads((home / "library.json").read_text(encoding="utf-8"))
    entry = library["grimoires"]["recipes-grimoire"]
    assert entry["local_path"] == "$HOME/grimoires/recipes-grimoire"
    assert entry["online_path"] == str(remote)
    assert report["summary"]["manifest"] == "ok"
    assert report["summary"]["skills"] == "skipped"

    # Second run fast-forwards instead of re-cloning and stays registered.
    again = _run(str(remote), home)
    assert again["returncode"] == 0
    assert [m["action"] for m in again["report"]["mutations"]] == ["pull", "register"]


def test_join_without_manifest_is_blocked_with_adopt_hint(tmp_path):
    remote = _bare_remote(tmp_path, "notes", with_manifest=False)
    home = tmp_path / "home"

    out = _run(str(remote), home)
    report = out["report"]

    assert out["returncode"] == 1
    assert report["status"] == "blocked"
    assert report["summary"]["manifest"] == "missing"
    assert (home / "notes").is_dir()  # the clone is kept for /grm-adopt
    assert not (home / "library.json").exists()
    assert any("/grm-adopt" in m["message"] for m in report["messages"])


def test_bad_url_is_an_error_not_a_crash(tmp_path):
    home = tmp_path / "home"
    out = _run(str(tmp_path / "does-not-exist.git"), home, "--name", "ghost")
    assert out["returncode"] == 1
    assert out["report"]["status"] == "error"
    assert any("could not clone" in m["message"] for m in out["report"]["messages"])
