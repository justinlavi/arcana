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
        "sync_skills",
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
    monkeypatch.setattr(summon_gui, "sync_skills", lambda *_args: calls.append("skills") or True)

    result = summon_gui.finalize_install_with_settings(
        [],
        {"grimoires": {}},
        log=_Log(),
        settings={"agent_targets": ["codex"], "skip_skill_registration": True},
    )

    assert result is True
    assert calls == ["agent"]


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


def test_gui_install_arcana_cancellable_delegates_to_core(monkeypatch):
    recorded = {}

    def fake_install_arcana(arcana_url, log, git_fn=None, cancel_event=None):
        recorded["url"] = arcana_url
        recorded["git_fn"] = git_fn
        recorded["cancel_event"] = cancel_event
        return True

    monkeypatch.setattr(summon_gui, "install_arcana", fake_install_arcana)

    cancel_sentinel = object()
    result = summon_gui.install_arcana_cancellable("u", _FullLog(), cancel_sentinel, object())

    assert result is True
    assert recorded["url"] == "u"
    assert recorded["cancel_event"] is cancel_sentinel
    assert callable(recorded["git_fn"])  # proc-slot-bound cancellable git


def test_inject_agent_file_is_idempotent_on_rerun(tmp_path):
    target = tmp_path / "AGENTS.md"
    summon_core.inject_agent_file(_FullLog(), target, "AGENTS")
    once = target.read_text(encoding="utf-8")
    assert once.count(summon_core.BEGIN_SENTINEL) == 1
    assert once.count(summon_core.HEADING_SENTINEL) == 1
    # Re-running must not append a second block.
    summon_core.inject_agent_file(_FullLog(), target, "AGENTS")
    twice = target.read_text(encoding="utf-8")
    assert twice == once


def test_inject_agent_file_skips_marker_only_block(tmp_path):
    # A block with BEGIN/END markers but no heading - the case the old
    # heading-only check would double-inject - is detected and left untouched.
    target = tmp_path / "AGENTS.md"
    target.write_text(
        "# AGENTS\n\n"
        f"{summon_core.BEGIN_SENTINEL}\ncustom block, no heading\n{summon_core.END_SENTINEL}\n",
        encoding="utf-8", newline="\n",
    )
    before = target.read_text(encoding="utf-8")
    summon_core.inject_agent_file(_FullLog(), target, "AGENTS")
    after = target.read_text(encoding="utf-8")
    assert after == before
    assert after.count(summon_core.BEGIN_SENTINEL) == 1
    assert summon_core.HEADING_SENTINEL not in after


def test_inject_agent_file_skips_legacy_heading_only_block(tmp_path):
    # A legacy block with the heading but no markers is still detected.
    target = tmp_path / "AGENTS.md"
    target.write_text(
        "# AGENTS\n\n## Grimoire Knowledge Base\n\nlegacy block\n",
        encoding="utf-8", newline="\n",
    )
    before = target.read_text(encoding="utf-8")
    summon_core.inject_agent_file(_FullLog(), target, "AGENTS")
    after = target.read_text(encoding="utf-8")
    assert after == before
    assert after.count(summon_core.HEADING_SENTINEL) == 1
    assert summon_core.BEGIN_SENTINEL not in after


# ---------------------------------------------------------------------------
# GUI OpenGL probe: must run in the interpreter that owns Dear PyGui
# ---------------------------------------------------------------------------


def _capture_probe_run(monkeypatch):
    """Stub summon_gui.subprocess.run to capture (cmd, env) and report success."""
    captured = {}

    def fake_run(cmd, **kwargs):
        captured["cmd"] = cmd
        captured["env"] = kwargs.get("env")
        return SimpleNamespace(returncode=0, stderr=b"")

    monkeypatch.setattr(summon_gui.subprocess, "run", fake_run)
    return captured


def test_probe_gui_frozen_reinvokes_self(monkeypatch):
    # A frozen binary must probe by re-invoking itself, not a system python
    # that lacks the bundled Dear PyGui.
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    captured = _capture_probe_run(monkeypatch)

    ok, _ = summon_gui._probe_gui(mode="import")

    assert ok is True
    assert captured["cmd"] == [sys.executable]
    assert "-c" not in captured["cmd"]
    assert captured["env"]["GRIMOIRE_SUMMON_GL_PROBE"] == "import"


def test_probe_gui_source_uses_system_python(monkeypatch):
    # A source run probes with system_python() against the dependency cache.
    monkeypatch.delattr(sys, "frozen", raising=False)
    monkeypatch.setattr(summon_gui, "system_python", lambda: "py-under-test")
    captured = _capture_probe_run(monkeypatch)

    ok, _ = summon_gui._probe_gui()

    assert ok is True
    assert captured["cmd"] == ["py-under-test", "-c", summon_gui._PROBE_BOOTSTRAP]
    assert captured["env"]["GRIMOIRE_SUMMON_GL_PROBE"] == "viewport"
    assert captured["env"]["GRIMOIRE_SUMMON_PROBE_DIR"]


def test_select_gui_env_reports_missing_dpg_distinctly(monkeypatch):
    # A missing-module failure must not be reported as a GL/Wayland problem.
    monkeypatch.setattr(
        summon_gui, "_probe_gui",
        lambda *a, **k: (False, "ModuleNotFoundError: No module named 'dearpygui'"),
    )
    env, msg = summon_gui._select_gui_env()
    assert env is None
    assert "Dear PyGui is not available" in msg
    assert "OpenGL/GLX" not in msg


def test_select_gui_env_reports_gl_failure(monkeypatch):
    # A real GL failure keeps the OpenGL/GLX guidance.
    monkeypatch.setattr(
        summon_gui, "_probe_gui",
        lambda *a, **k: (False, "GLX: failed to create context"),
    )
    env, msg = summon_gui._select_gui_env()
    assert env is None
    assert "no usable OpenGL/GLX context" in msg
    assert "Dear PyGui is not available" not in msg


def _install_fake_dearpygui(monkeypatch):
    """Put a recording fake dearpygui.dearpygui in sys.modules; return the call log."""
    import types
    calls = []

    def rec(name):
        return lambda *a, **k: calls.append(name)

    fake = types.ModuleType("dearpygui.dearpygui")
    for fn in ("create_context", "create_viewport", "setup_dearpygui",
               "show_viewport", "render_dearpygui_frame", "destroy_context"):
        setattr(fake, fn, rec(fn))
    pkg = types.ModuleType("dearpygui")
    pkg.dearpygui = fake
    monkeypatch.setitem(sys.modules, "dearpygui", pkg)
    monkeypatch.setitem(sys.modules, "dearpygui.dearpygui", fake)
    return calls


def test_run_gl_probe_import_mode_does_not_touch_gl(monkeypatch):
    calls = _install_fake_dearpygui(monkeypatch)
    assert summon_gui.run_gl_probe("import") == 0
    assert calls == []


def test_run_gl_probe_viewport_mode_renders_one_frame(monkeypatch):
    calls = _install_fake_dearpygui(monkeypatch)
    assert summon_gui.run_gl_probe("viewport") == 0
    assert calls == [
        "create_context", "create_viewport", "setup_dearpygui",
        "show_viewport", "render_dearpygui_frame", "destroy_context",
    ]
