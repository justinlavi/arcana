"""Temp-target tests for the grimoire library sync rite."""

import json
from pathlib import Path

import sync_library


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
