"""Tests for git-aware smart validator selection (deletion awareness)."""

from types import SimpleNamespace

import validate


def test_git_changed_files_parses_name_status(monkeypatch):
    def fake_run(cmd, **kwargs):
        if "--name-status" in cmd:
            return SimpleNamespace(
                returncode=0,
                stdout="M\ta.md\nD\tb.md\nR100\told.md\tnew.md\n",
            )
        return SimpleNamespace(returncode=0, stdout="")

    monkeypatch.setattr(validate.subprocess, "run", fake_run)
    changes = validate.git_changed_files(validate.ARCANA_ROOT)

    assert ("M", "a.md") in changes
    assert ("D", "b.md") in changes
    assert ("D", "old.md") in changes  # rename: old side is a deletion
    assert ("A", "new.md") in changes  # rename: new side is an addition


def test_smart_arcana_deletion_selects_structure(monkeypatch):
    monkeypatch.setattr(validate, "git_changed_files", lambda root: [("D", "arcana.json")])
    rites = validate.determine_smart_rites("arcana", validate.ARCANA_ROOT)
    assert "validate_structure.py" in rites


def test_smart_arcana_deleted_skill_selects_skill_refs(monkeypatch):
    monkeypatch.setattr(
        validate, "git_changed_files", lambda root: [("D", "skills/arcana/x/SKILL.md")]
    )
    rites = validate.determine_smart_rites("arcana", validate.ARCANA_ROOT)
    assert "validate_skill_refs.py" in rites
    assert "validate_structure.py" in rites


def test_smart_grimoire_deletion_selects_structure_and_refs(monkeypatch):
    monkeypatch.setattr(
        validate, "git_changed_files", lambda root: [("D", "chapters/x/page.md")]
    )
    rites = validate.determine_smart_rites("grimoire", validate.ARCANA_ROOT)
    assert "validate_grimoire_structure.py" in rites
    assert "validate_orphans.py" in rites
    assert "validate_links.py" in rites


def test_smart_deletion_never_selects_empty(monkeypatch):
    # The bug: a deletion-only change used to select zero validators, so --auto
    # could green-light a deleted required file.
    monkeypatch.setattr(validate, "git_changed_files", lambda root: [("D", "arcana.json")])
    assert validate.determine_smart_rites("arcana", validate.ARCANA_ROOT)
