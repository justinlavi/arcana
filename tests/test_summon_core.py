"""Unit tests for summon_core.py installer helpers."""

import io
import sys
from pathlib import Path

import summon_core


class _NonInteractiveStdin(io.StringIO):
    def isatty(self):
        return False


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
