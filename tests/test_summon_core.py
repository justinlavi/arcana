"""Unit tests for summon_core.py installer helpers."""

import io
import sys
from types import SimpleNamespace
from pathlib import Path

import summon_core
import summon
import summon_gui


class _NonInteractiveStdin(io.StringIO):
    def isatty(self):
        return False


class _Log:
    def __init__(self):
        self.messages = []

    def info(self, message):
        self.messages.append(("info", message))


def test_prompt_text_returns_default_when_stdin_and_tty_are_unavailable(monkeypatch):
    monkeypatch.setattr(sys, "stdin", _NonInteractiveStdin(""))

    def fake_open(*_args, **_kwargs):
        raise OSError("no controlling terminal")

    monkeypatch.setattr("builtins.open", fake_open)

    assert summon_core._prompt_text("Choice [1]: ", default="1") == "1"


def test_prompt_cli_mode_defaults_to_arcana_only_without_interactive_input(monkeypatch):
    monkeypatch.setattr(sys, "stdin", _NonInteractiveStdin(""))

    def fake_open(*_args, **_kwargs):
        raise OSError("no controlling terminal")

    monkeypatch.setattr("builtins.open", fake_open)

    assert summon_core._prompt_cli_mode(scope_preselected=False) == "arcana_only"


def test_grimoire_block_comes_from_canonical_template():
    template = (
        Path(__file__).resolve().parents[1]
        / "rites"
        / "templates"
        / "grimoire_block.md"
    )

    assert summon_core.GRIMOIRE_BLOCK == "\n" + template.read_text(encoding="utf-8")


def test_dispatcher_mode_selection_respects_overrides_and_display(monkeypatch):
    assert summon._detect_gui_mode(SimpleNamespace(gui=True, cli=False)) == (True, "")
    assert summon._detect_gui_mode(SimpleNamespace(gui=False, cli=True)) == (False, "")

    monkeypatch.setattr(sys, "platform", "win32")
    assert summon._detect_gui_mode(SimpleNamespace(gui=False, cli=False)) == (True, "")

    monkeypatch.setattr(sys, "platform", "linux")
    monkeypatch.delenv("DISPLAY", raising=False)
    monkeypatch.delenv("WAYLAND_DISPLAY", raising=False)
    monkeypatch.delenv("XDG_SESSION_TYPE", raising=False)
    assert summon._detect_gui_mode(SimpleNamespace(gui=False, cli=False)) == (
        False,
        "no display server detected",
    )

    monkeypatch.setenv("DISPLAY", ":0")
    assert summon._detect_gui_mode(SimpleNamespace(gui=False, cli=False)) == (True, "")


def test_finalize_install_preserves_core_post_install_order(monkeypatch):
    calls = []

    monkeypatch.setattr(
        summon_core,
        "update_local_library",
        lambda installed_keys, library, log: calls.append(("library", installed_keys, library)),
    )
    monkeypatch.setattr(
        summon_core,
        "inject_agent_configs",
        lambda log: calls.append(("agents",)),
    )
    monkeypatch.setattr(
        summon_core,
        "register_skills",
        lambda log: calls.append(("skills",)) or True,
    )

    result = summon_core.finalize_install(
        ["cooking-grimoire"],
        {"grimoires": {"cooking-grimoire": {"online_path": "https://example.test/repo.git"}}},
        log=object(),
    )

    assert result is True
    assert [call[0] for call in calls] == ["library", "agents", "skills"]


def test_gui_default_post_install_matches_core_shape(monkeypatch):
    calls = []

    monkeypatch.setattr(
        summon_gui,
        "update_local_library",
        lambda installed_keys, library, log: calls.append(("library", installed_keys, library)),
    )
    monkeypatch.setattr(
        summon_gui,
        "inject_agent_file",
        lambda log, target_path, title: calls.append(("agent", target_path, title)),
    )
    monkeypatch.setattr(
        summon_gui,
        "register_skills",
        lambda log: calls.append(("skills",)) or True,
    )

    result = summon_gui.finalize_install_with_settings(
        ["cooking-grimoire"],
        {"grimoires": {"cooking-grimoire": {"online_path": "https://example.test/repo.git"}}},
        log=object(),
        settings={"agent_targets": ["claude", "codex"], "skip_skill_registration": False},
    )

    assert result is True
    assert [call[0] for call in calls] == ["library", "agent", "agent", "skills"]


def test_gui_settings_can_skip_skill_registration(monkeypatch):
    calls = []

    monkeypatch.setattr(summon_gui, "update_local_library", lambda *_args: calls.append("library"))
    monkeypatch.setattr(summon_gui, "inject_agent_file", lambda *_args: calls.append("agent"))
    monkeypatch.setattr(summon_gui, "register_skills", lambda *_args: calls.append("skills") or True)

    result = summon_gui.finalize_install_with_settings(
        [],
        {"grimoires": {}},
        log=_Log(),
        settings={"agent_targets": ["codex"], "skip_skill_registration": True},
    )

    assert result is True
    assert calls == ["agent"]
