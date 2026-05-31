"""Temp-target tests for the artifact-cleanup rite."""

import json
import subprocess
import sys
from pathlib import Path

import clean_artifacts

REPO_ROOT = Path(__file__).resolve().parent.parent
RITE = REPO_ROOT / "rites" / "clean_artifacts.py"


def _artifacts(base):
    arts = base / "rites" / ".artifacts"
    arts.mkdir(parents=True)
    (arts / "x.log").write_text("data", encoding="utf-8")
    return arts


def test_clean_location_dry_run_keeps_files(tmp_path):
    arts = _artifacts(tmp_path)
    assert clean_artifacts.clean_location(tmp_path, "x", dry_run=True) == 1
    assert arts.exists()


def test_clean_location_apply_removes(tmp_path):
    arts = _artifacts(tmp_path)
    assert clean_artifacts.clean_location(tmp_path, "x", dry_run=False) == 1
    assert not arts.exists()


def test_clean_location_missing_artifacts_is_noop(tmp_path):
    assert clean_artifacts.clean_location(tmp_path, "x", dry_run=False) == 0


def test_clean_location_survives_rmtree_error(tmp_path, monkeypatch):
    _artifacts(tmp_path)

    def boom(_path):
        raise OSError("locked")

    monkeypatch.setattr(clean_artifacts.shutil, "rmtree", boom)
    # One failure must not propagate; it would otherwise abort a multi-location run.
    assert clean_artifacts.clean_location(tmp_path, "x", dry_run=False) == 0


def test_clean_location_human_false_suppresses_output(tmp_path, capsys):
    arts = _artifacts(tmp_path)
    assert clean_artifacts.clean_location(tmp_path, "x", dry_run=True, human=False) == 1
    assert capsys.readouterr().out == ""
    assert arts.exists()


def test_json_envelope_dry_run_is_clean():
    # --dry-run keeps the real Arcana .artifacts intact; stdout must be one JSON object.
    result = subprocess.run(
        [sys.executable, str(RITE), "--dry-run", "--format", "json"],
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["rite"] == "clean_artifacts"
    assert report["mode"] == "plan"
    # Plan mode writes nothing: no mutations and a noop status. Planned removals
    # (if any artifacts exist) surface as info messages and via summary counts.
    assert report["mutations"] == []
    assert report["status"] == "noop"
    assert "locations" in report["summary"]
    assert "files" in report["summary"]
