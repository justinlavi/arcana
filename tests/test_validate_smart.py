"""Tests for git-aware smart validator selection (deletion awareness)."""

import subprocess
import sys
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
        validate, "git_changed_files", lambda root: [("D", "skills/arc/x/SKILL.md")]
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


def test_arcana_validator_selectors_resolve_named_rites():
    rites = validate.apply_validator_selection(
        validate.ARCANA_RITES,
        profile="arcana",
        only=["links,frontmatter", "skill-refs"],
    )

    assert rites == [
        "validate_frontmatter.py",
        "validate_links.py",
        "validate_skill_refs.py",
    ]


def test_grimoire_structure_selector_uses_grimoire_structure_rite():
    rites = validate.apply_validator_selection(
        validate.GRIMOIRE_RITES,
        profile="grimoire",
        only=["structure"],
    )

    assert rites == ["validate_grimoire_structure.py"]


def test_validator_selection_rejects_unknown_selector():
    try:
        validate.apply_validator_selection(
            validate.ARCANA_RITES,
            profile="arcana",
            only=["not-a-validator"],
        )
    except ValueError as exc:
        assert "unknown validator selector" in str(exc)
    else:
        raise AssertionError("unknown selectors should fail")


def test_positional_selectors_split_modes_from_validators():
    modes, selectors = validate.parse_positional_selectors(["smart", "links,frontmatter"])

    assert modes == ["smart"]
    assert selectors == ["links", "frontmatter"]


# --- End-to-end exit-code contract (0 = pass, 1 = failed, 2 = invalid usage) ---


def _run_validate(*args):
    return subprocess.run(
        [sys.executable, validate.__file__, *args],
        capture_output=True,
        text=True,
        timeout=120,
    )


def test_cli_valid_selector_exits_zero():
    result = _run_validate("links", "frontmatter", "--format", "json")
    assert result.returncode == 0


def test_cli_unknown_selector_exits_two():
    result = _run_validate("not-a-validator")
    assert result.returncode == 2
    assert "unknown validator selector" in result.stderr


def test_cli_conflicting_positional_modes_exit_two():
    result = _run_validate("parallel", "summary")
    assert result.returncode == 2
    assert "Conflicting validation modes" in result.stderr


def test_cli_flag_mode_conflicts_with_positional_mode_exits_two():
    result = _run_validate("summary", "--parallel")
    assert result.returncode == 2
    assert "Conflicting validation modes" in result.stderr


def test_cli_selection_resolving_to_zero_exits_two():
    result = _run_validate("--only", "links", "--exclude", "links")
    assert result.returncode == 2
    assert "selection resolved to zero validators" in result.stderr
