"""bin/arcana runs a rite with whatever Python the machine has, beside the engine or from the plugin."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SH = shutil.which("sh") or shutil.which("bash")


def _sh(*args: str, env: dict | None = None) -> subprocess.CompletedProcess:
    full = dict(os.environ)
    if env:
        full.update(env)
    return subprocess.run([SH, str(REPO_ROOT / "bin" / "arcana"), *args], capture_output=True, text=True, env=full, timeout=120)


@pytest.mark.skipif(SH is None, reason="no POSIX shell available")
def test_launcher_runs_a_rite_beside_the_engine():
    result = _sh("validate", "--help")
    assert result.returncode == 0, result.stderr
    assert "usage" in result.stdout.lower()


@pytest.mark.skipif(SH is None, reason="no POSIX shell available")
def test_launcher_lists_rites_and_refuses_unknown_ones():
    listing = _sh("--list")
    assert listing.returncode == 0
    names = listing.stdout.split()
    assert "validate" in names and "sync_skills" in names and not any(n.startswith("_") for n in names)

    missing = _sh("no_such_rite")
    assert missing.returncode == 2
    assert "no rite named" in missing.stderr


@pytest.mark.skipif(SH is None, reason="no POSIX shell available")
def test_plugin_copy_resolves_the_engine_through_arcana_home(tmp_path):
    plugin_bin = tmp_path / "plugin" / "bin"
    plugin_bin.mkdir(parents=True)
    for name in ("arcana", "arcana.py"):
        shutil.copy(REPO_ROOT / "bin" / name, plugin_bin / name)
    result = subprocess.run(
        [SH, str(plugin_bin / "arcana"), "recent_changes", "--help"],
        capture_output=True, text=True, env={**os.environ, "ARCANA_HOME": str(REPO_ROOT)}, timeout=120,
    )
    assert result.returncode == 0, result.stderr
    assert "--since" in result.stdout


@pytest.mark.skipif(sys.platform != "win32", reason="cmd launcher is Windows-only")
def test_cmd_launcher_runs_a_rite():
    result = subprocess.run(
        ["cmd", "/c", str(REPO_ROOT / "bin" / "arcana.cmd"), "validate", "--help"],
        capture_output=True, text=True, timeout=120,
    )
    assert result.returncode == 0, result.stderr
    assert "usage" in result.stdout.lower()


def test_plugin_tree_carries_the_launcher():
    assert (REPO_ROOT / "plugins" / "grm" / "bin" / "arcana").read_text(encoding="utf-8") == (REPO_ROOT / "bin" / "arcana").read_text(encoding="utf-8")
    assert (REPO_ROOT / "plugins" / "grm" / "bin" / "arcana.cmd").read_text(encoding="utf-8") == (REPO_ROOT / "bin" / "arcana.cmd").read_text(encoding="utf-8")
    assert (REPO_ROOT / "plugins" / "grm" / "bin" / "arcana.py").read_text(encoding="utf-8") == (REPO_ROOT / "bin" / "arcana.py").read_text(encoding="utf-8")
