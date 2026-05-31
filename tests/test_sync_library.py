"""Temp-target tests for the grimoire library sync rite."""

import json
import subprocess
import sys
from pathlib import Path

import sync_library

REPO_ROOT = Path(__file__).resolve().parent.parent
RITE = REPO_ROOT / "rites" / "sync_library.py"


def _make_grimoire(home: Path, key: str, skill_prefix: str = "gg") -> Path:
    g = home / key
    g.mkdir(parents=True)
    (g / "grimoire.json").write_text(
        json.dumps({"name": key, "skill_prefix": skill_prefix, "description": "test"}),
        encoding="utf-8",
    )
    return g


def test_present_grimoire_with_canonical_path_is_ok(tmp_path):
    home = tmp_path / "grimoires"
    _make_grimoire(home, "goodgrim")
    library = {"grimoires": {"goodgrim": {
        "local_path": sync_library.expected_local_path(home, "goodgrim"),
        "online_path": None,
    }}}

    scan = sync_library.scan_grimoire_home(home)
    diff = sync_library.diff_library(scan, library, home)

    assert "goodgrim" in diff["ok"]
    assert diff["stale"] == []


def test_present_grimoire_with_home_token_is_not_stale_or_dropped(tmp_path):
    home = tmp_path / "grimoires"
    _make_grimoire(home, "goodgrim")
    # A portable $HOME-tokened entry for a grimoire that physically exists under
    # the active home must never be reported stale or dropped on --apply.
    library = {"grimoires": {"goodgrim": {
        "local_path": "$HOME/grimoires/goodgrim",
        "online_path": None,
    }}}

    scan = sync_library.scan_grimoire_home(home)
    diff = sync_library.diff_library(scan, library, home)

    assert "goodgrim" not in {s["key"] for s in diff["stale"]}
    assert "goodgrim" in diff["ok"] or "goodgrim" in {m["key"] for m in diff["mismatched"]}

    new_library = sync_library.build_synced_library(scan, library, home)
    assert "goodgrim" in new_library["grimoires"]


def test_truly_missing_entry_is_stale(tmp_path):
    home = tmp_path / "grimoires"
    home.mkdir(parents=True)
    library = {"grimoires": {"ghost": {
        "local_path": str(tmp_path / "nowhere" / "ghost"),
        "online_path": None,
    }}}

    scan = sync_library.scan_grimoire_home(home)
    diff = sync_library.diff_library(scan, library, home)

    assert "ghost" in {s["key"] for s in diff["stale"]}
    new_library = sync_library.build_synced_library(scan, library, home)
    assert "ghost" not in new_library["grimoires"]


def _run(home: Path, *args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [sys.executable, str(RITE), "--home", str(home), *args],
        capture_output=True,
        text=True,
        timeout=30,
    )


def test_json_envelope_plan_mode_reports_drift(tmp_path):
    home = tmp_path / "grimoires"
    _make_grimoire(home, "newgrim")
    # Library has no entry for newgrim -> it's "missing" drift.
    (home / "library.json").write_text(
        json.dumps({"grimoires": {}}), encoding="utf-8"
    )

    result = _run(home, "--format", "json")

    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["rite"] == "sync_library"
    assert report["mode"] == "plan"
    # Plan mode never writes, so no mutations -> status derives from messages.
    assert report["mutations"] == []
    assert report["summary"]["missing"] == 1
    assert report["summary"]["applied"] is False
    # The missing grimoire is surfaced as a message.
    assert any("newgrim" in m["message"] for m in report["messages"])


def test_json_envelope_apply_mode_records_write_mutation(tmp_path):
    home = tmp_path / "grimoires"
    _make_grimoire(home, "newgrim")
    (home / "library.json").write_text(
        json.dumps({"grimoires": {}}), encoding="utf-8"
    )

    result = _run(home, "--apply", "--format", "json")

    assert result.returncode == 0
    report = json.loads(result.stdout)
    assert report["rite"] == "sync_library"
    assert report["mode"] == "apply"
    assert report["status"] == "ok"
    assert report["summary"]["applied"] is True
    actions = [m["action"] for m in report["mutations"]]
    assert "write" in actions
    # The library was actually reconciled on disk.
    written = json.loads((home / "library.json").read_text(encoding="utf-8"))
    assert "newgrim" in written["grimoires"]


def test_json_envelope_in_sync_is_noop(tmp_path):
    home = tmp_path / "grimoires"
    _make_grimoire(home, "goodgrim")
    (home / "library.json").write_text(
        json.dumps({"grimoires": {"goodgrim": {
            "local_path": sync_library.expected_local_path(home, "goodgrim"),
            "online_path": None,
        }}}),
        encoding="utf-8",
    )

    result = _run(home, "--apply", "--format", "json")

    assert result.returncode == 0
    report = json.loads(result.stdout)
    # No drift -> nothing written -> noop status, no mutations.
    assert report["status"] == "noop"
    assert report["mutations"] == []
    assert report["summary"]["applied"] is False
