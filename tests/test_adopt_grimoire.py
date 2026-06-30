"""Temp-target tests for the grimoire adoption rite."""

import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RITE = REPO_ROOT / "rites" / "adopt_grimoire.py"


def _adopt(home: Path, directory: str, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RITE), directory, "--home", str(home), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_adopt_grimoire_json_envelope(tmp_path):
    home = tmp_path / "grimoires"
    target = home / "dnd-grimoire"
    target.mkdir(parents=True)

    result = _adopt(home, "dnd-grimoire", "--skill-prefix", "dnd", "--format", "json")

    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["rite"] == "adopt_grimoire"
    assert report["status"] == "ok"
    assert report["mode"] == "apply"
    assert report["mutations"][0]["action"] == "write"
    assert report["mutations"][0]["path"] == "dnd-grimoire/grimoire.json"

    manifest_path = target / "grimoire.json"
    assert manifest_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["skill_prefix"] == "dnd"
    assert manifest["name"] == "dnd-grimoire"


def test_adopt_grimoire_json_collision_is_clean(tmp_path):
    home = tmp_path / "grimoires"

    # First grimoire claims the "dnd" skill prefix.
    first = home / "dnd-grimoire"
    first.mkdir(parents=True)
    (first / "grimoire.json").write_text(
        json.dumps({"name": "dnd-grimoire", "skill_prefix": "dnd", "description": "x"}) + "\n",
        encoding="utf-8",
    )

    # Second grimoire wants the same skill prefix -> collision (exit 2).
    second = home / "other-grimoire"
    second.mkdir(parents=True)

    result = _adopt(home, "other-grimoire", "--skill-prefix", "dnd", "--format", "json")

    assert result.returncode == 2
    report = json.loads(result.stdout)
    assert report["rite"] == "adopt_grimoire"
    assert report["status"] == "error"
    assert report["mutations"] == []
    assert any(msg["severity"] == "error" for msg in report["messages"])

    # No manifest was written for the second grimoire.
    assert not (second / "grimoire.json").is_file()


def test_adopt_grimoire_human_mode_writes_manifest(tmp_path):
    home = tmp_path / "grimoires"
    target = home / "dnd-grimoire"
    target.mkdir(parents=True)

    result = _adopt(home, "dnd-grimoire", "--skill-prefix", "dnd")

    assert result.returncode == 0
    assert "Wrote" in result.stdout
    manifest_path = target / "grimoire.json"
    assert manifest_path.is_file()
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    assert manifest["skill_prefix"] == "dnd"
