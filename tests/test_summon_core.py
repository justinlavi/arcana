"""Unit tests for summon_core.py installer helpers."""

import io
import sys
from types import SimpleNamespace
from pathlib import Path

import summon_core
import summon


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
        "sync_skills",
        lambda log: calls.append(("skills",)) or True,
    )

    result = summon_core.finalize_install(
        ["cooking-grimoire"],
        {"grimoires": {"cooking-grimoire": {"online_path": "https://example.test/repo.git"}}},
        log=object(),
    )

    assert result is True
    assert [call[0] for call in calls] == ["library", "agents", "skills"]


class _FullLog:
    def __init__(self):
        self.events = []

    def info(self, m):
        self.events.append(("info", m))

    def ok(self, m):
        self.events.append(("ok", m))

    def warn(self, m):
        self.events.append(("warn", m))

    def err(self, m):
        self.events.append(("err", m))

    def line(self, m):
        self.events.append(("line", m))


def test_git_sets_timeout_and_disables_terminal_prompt(monkeypatch):
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["kwargs"] = kwargs
        return SimpleNamespace(returncode=0, stdout="out\n", stderr="")

    monkeypatch.setattr(summon_core.subprocess, "run", fake_run)
    success, out = summon_core.git("status")

    assert success is True and out == "out"
    assert captured["kwargs"]["timeout"] == summon_core.GIT_TIMEOUT
    assert captured["kwargs"]["env"]["GIT_TERMINAL_PROMPT"] == "0"


def test_git_returns_false_on_timeout(monkeypatch):
    def fake_run(cmd, **kwargs):
        raise summon_core.subprocess.TimeoutExpired(cmd, kwargs.get("timeout"))

    monkeypatch.setattr(summon_core.subprocess, "run", fake_run)
    success, out = summon_core.git("clone", "url", "dest")

    assert success is False
    assert out == ""


def test_install_arcana_recovers_partial_working_tree(tmp_path, monkeypatch):
    arcana_dir = tmp_path / "arcana"
    (arcana_dir / ".git").mkdir(parents=True)  # repo present, working tree empty
    monkeypatch.setattr(summon_core, "ARCANA_DIR", arcana_dir)

    calls = []

    def fake_git(*args, log=None, **_kwargs):
        calls.append(args)
        if "checkout" in args:
            (arcana_dir / "arcana.json").write_text("{}", encoding="utf-8")
        return True, ""

    result = summon_core.install_arcana("", _FullLog(), git_fn=fake_git)

    assert result is True
    assert any("checkout" in c for c in calls)  # recovery attempted (the CLI-only path)
    assert (arcana_dir / "arcana.json").exists()


def test_install_arcana_fails_when_recovery_cannot_populate(tmp_path, monkeypatch):
    arcana_dir = tmp_path / "arcana"
    (arcana_dir / ".git").mkdir(parents=True)
    monkeypatch.setattr(summon_core, "ARCANA_DIR", arcana_dir)

    def fake_git(*args, log=None, **_kwargs):
        return True, ""  # commands "succeed" but never populate a sentinel

    result = summon_core.install_arcana("", _FullLog(), git_fn=fake_git)
    assert result is False


def test_install_arcana_respects_cancel_event():
    class _Cancelled:
        def is_set(self):
            return True

    called = []

    def fake_git(*args, **_kwargs):
        called.append(args)
        return True, ""

    result = summon_core.install_arcana(
        "url", _FullLog(), git_fn=fake_git, cancel_event=_Cancelled()
    )
    assert result is False
    assert called == []


def test_host_detection_is_anchored():
    assert summon_core._is_github_host("github.com")
    assert summon_core._is_github_host("api.github.com")
    assert summon_core._is_github_host("github.acme.com")  # self-hosted GitHub Enterprise
    assert not summon_core._is_github_host("mygithub.com")
    assert summon_core._is_gitlab_host("gitlab.com")
    assert summon_core._is_gitlab_host("gitlab.acme.com")  # self-hosted GitLab
    # gitlab.github.io is a GitLab host; the old substring check matched both.
    assert summon_core._is_gitlab_host("gitlab.github.io")
    assert not summon_core._is_github_host("gitlab.github.io")


def test_inject_agent_file_is_idempotent_on_rerun(tmp_path):
    target = tmp_path / "AGENTS.md"
    summon_core.inject_agent_file(_FullLog(), target, "AGENTS")
    once = target.read_text(encoding="utf-8")
    assert once.count(summon_core.BEGIN_SENTINEL) == 1
    assert once.count(summon_core.END_SENTINEL) == 1
    # Re-running must not append a second block.
    summon_core.inject_agent_file(_FullLog(), target, "AGENTS")
    twice = target.read_text(encoding="utf-8")
    assert twice == once


def test_inject_agent_file_skips_when_current_block_present(tmp_path):
    # A file already carrying the current canonical block is left untouched.
    target = tmp_path / "AGENTS.md"
    target.write_text(
        "# AGENTS\n\n" + summon_core.canonical_routing_block() + "\n",
        encoding="utf-8", newline="\n",
    )
    before = target.read_text(encoding="utf-8")
    summon_core.inject_agent_file(_FullLog(), target, "AGENTS")
    assert target.read_text(encoding="utf-8") == before


def test_inject_agent_file_refreshes_stale_marked_block(tmp_path):
    # One clean BEGIN..END region whose content is out of date is refreshed in
    # place; surrounding content is preserved and no second block appears.
    target = tmp_path / "AGENTS.md"
    target.write_text(
        f"# AGENTS\nintro\n{summon_core.BEGIN_SENTINEL}\nstale body\n{summon_core.END_SENTINEL}\ntail\n",
        encoding="utf-8", newline="\n",
    )
    summon_core.inject_agent_file(_FullLog(), target, "AGENTS")
    after = target.read_text(encoding="utf-8")
    assert summon_core.canonical_routing_block() in after
    assert "stale body" not in after and "intro" in after and "tail" in after
    assert after.count(summon_core.BEGIN_SENTINEL) == 1


def test_inject_agent_file_inserts_into_blockless_file_preserving_content(tmp_path):
    # A file with content but no block signature gets the marked block inserted at
    # install time; existing user content is preserved.
    target = tmp_path / "AGENTS.md"
    target.write_text("# AGENTS\n\nmy own notes\n", encoding="utf-8", newline="\n")
    summon_core.inject_agent_file(_FullLog(), target, "AGENTS")
    after = target.read_text(encoding="utf-8")
    assert after.count(summon_core.BEGIN_SENTINEL) == 1
    assert "my own notes" in after


def test_inject_agent_file_never_duplicates_a_legacy_heading_block(tmp_path):
    # A pre-marker (heading-only) block has no clean markers; the install pass must
    # leave it for judgment, never append a second block.
    target = tmp_path / "AGENTS.md"
    original = "# AGENTS\n## Grimoire Knowledge Base\nlegacy body\n"
    target.write_text(original, encoding="utf-8", newline="\n")
    summon_core.inject_agent_file(_FullLog(), target, "AGENTS")
    after = target.read_text(encoding="utf-8")
    assert after == original  # untouched
    assert after.count(summon_core.BEGIN_SENTINEL) == 0


def test_dispatcher_parses_install_flags():
    parser = summon.build_parser()
    args = parser.parse_args(["--scope", "https://example.com/org"])
    assert args.scope == "https://example.com/org"
    assert args.arcana_url is None


def test_core_spawns_sister_scripts_with_the_running_interpreter():
    assert summon_core._subprocess_env() is None
    assert summon_core.system_python() == sys.executable
