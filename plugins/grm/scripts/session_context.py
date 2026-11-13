#!/usr/bin/env python3
"""Session-start hook for the grm plugin: keep the engine current, print routing context.

Runs at the start of every Claude Code session while the plugin is enabled.
Its stdout becomes session context, so it prints only what the agent needs:

1. The engine. Arcana lives at ``~/grimoires/arcana`` for every agent. When the
   checkout is absent the hook clones it from the marketplace repository the
   plugin was installed from; when it is present, clean, and on ``main`` it
   fast-forwards it. A dirty or diverged checkout is left alone and reported.
2. The Grimoire routing block, when the user's ``~/.claude/CLAUDE.md`` does not
   already carry one, so a plugin-only install needs no instruction-file edit.
3. The installed grimoires with their descriptions and paths, read from
   ``~/grimoires/library.json``.
4. One drift line from ``summon.py --check``, so the agent can offer
   ``/grm:update`` at the right moment.

The script is self-contained (stdlib only) because it must run before the
engine exists. Everything is time-boxed; a network that is unreachable
degrades to a one-line note, never an error.

Environment overrides (tests, forks): ``ARCANA_ENGINE_HOME`` (engine
checkout), ``ARCANA_ENGINE_URL`` (clone source), ``ARCANA_SESSION_HOME``
(grimoire home, default ``~/grimoires``), ``ARCANA_CLAUDE_HOME`` (default
``~/.claude``), ``ARCANA_SESSION_NO_NETWORK=1`` (skip fetch and clone).
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
PLUGIN_ROOT = HERE.parent
HOME = Path.home()
ENGINE_HOME = Path(os.environ.get("ARCANA_ENGINE_HOME") or HOME / "grimoires" / "arcana").expanduser()
GRIMOIRE_HOME = Path(os.environ.get("ARCANA_SESSION_HOME") or HOME / "grimoires").expanduser()
CLAUDE_HOME = Path(os.environ.get("ARCANA_CLAUDE_HOME") or HOME / ".claude").expanduser()
NO_NETWORK = os.environ.get("ARCANA_SESSION_NO_NETWORK") == "1"
BEGIN = "<!-- BEGIN GRIMOIRE KNOWLEDGE BASE -->"
END = "<!-- END GRIMOIRE KNOWLEDGE BASE -->"
GIT_TIMEOUT = 20
CHECK_TIMEOUT = 30


def git(*args: str, cwd: Path | None = None, timeout: int = GIT_TIMEOUT) -> tuple[int, str]:
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    try:
        proc = subprocess.run(
            ["git", *args], cwd=str(cwd) if cwd else None, capture_output=True,
            text=True, encoding="utf-8", errors="replace", timeout=timeout, env=env,
        )
    except FileNotFoundError:
        return 127, "git is not installed"
    except subprocess.TimeoutExpired:
        return 124, "timed out"
    return proc.returncode, (proc.stdout + proc.stderr).strip()


def engine_url() -> str:
    """The marketplace repository the plugin came from is the engine repository."""
    override = os.environ.get("ARCANA_ENGINE_URL")
    if override:
        return override
    marketplace = ""
    parts = PLUGIN_ROOT.as_posix().split("/")
    if "cache" in parts:
        index = parts.index("cache")
        if index + 1 < len(parts):
            marketplace = parts[index + 1]
    known = CLAUDE_HOME / "plugins" / "known_marketplaces.json"
    try:
        data = json.loads(known.read_text(encoding="utf-8"))
        source = data.get(marketplace, {}).get("source", {})
        if source.get("source") == "github" and source.get("repo"):
            return f"https://github.com/{source['repo']}.git"
        for key in ("url", "path"):
            if source.get(key):
                return str(source[key])
    except (OSError, json.JSONDecodeError, AttributeError):
        pass
    try:
        return json.loads((HERE / "engine.json").read_text(encoding="utf-8"))["url"]
    except (OSError, json.JSONDecodeError, KeyError):
        return "https://github.com/justinlavi/arcana.git"


def ensure_engine() -> str:
    """Clone or fast-forward the engine checkout; return a one-line status."""
    if not (ENGINE_HOME / ".git").is_dir():
        if ENGINE_HOME.exists() and any(ENGINE_HOME.iterdir()):
            return f"engine: {ENGINE_HOME} exists but is not a git checkout; leaving it alone"
        if NO_NETWORK:
            return f"engine: not installed at {ENGINE_HOME} (network disabled)"
        url = engine_url()
        ENGINE_HOME.parent.mkdir(parents=True, exist_ok=True)
        code, out = git("clone", "--quiet", url, str(ENGINE_HOME), timeout=180)
        if code != 0:
            return f"engine: clone of {url} failed ({out[-160:]}); run /grm:update once the host is reachable"
        return f"engine: installed at {ENGINE_HOME} from {url}"
    code, status = git("status", "--porcelain", cwd=ENGINE_HOME)
    if code != 0:
        return f"engine: present at {ENGINE_HOME} (git status failed: {status[-120:]})"
    if status.strip():
        return f"engine: present at {ENGINE_HOME} with local changes; not updated"
    branch = git("rev-parse", "--abbrev-ref", "HEAD", cwd=ENGINE_HOME)[1].strip()
    if branch != "main":
        return f"engine: present at {ENGINE_HOME} on branch {branch}; not updated"
    if NO_NETWORK:
        return f"engine: present at {ENGINE_HOME} (network disabled)"
    code, out = git("fetch", "--quiet", cwd=ENGINE_HOME)
    if code != 0:
        return f"engine: present at {ENGINE_HOME}; could not reach its remote"
    code, counts = git("rev-list", "--left-right", "--count", "@{upstream}...HEAD", cwd=ENGINE_HOME)
    behind = int(counts.split()[0]) if code == 0 and counts.split() else 0
    if behind:
        code, out = git("merge", "--ff-only", "--quiet", "@{upstream}", cwd=ENGINE_HOME)
        if code == 0:
            return f"engine: updated at {ENGINE_HOME} ({behind} new commit{'s' if behind != 1 else ''})"
        return f"engine: present at {ENGINE_HOME}; {behind} commit(s) behind but not fast-forwardable; run /grm:update"
    return f"engine: current at {ENGINE_HOME}"


def routing_block() -> str:
    for candidate in (ENGINE_HOME / "rites" / "templates" / "grimoire_block.md", HERE / "grimoire_block.md"):
        try:
            return candidate.read_text(encoding="utf-8").strip()
        except OSError:
            continue
    return ""


def instruction_file_has_block() -> bool:
    try:
        text = (CLAUDE_HOME / "CLAUDE.md").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return False
    return BEGIN in text and END in text


def installed_grimoires() -> list[str]:
    library = GRIMOIRE_HOME / "library.json"
    try:
        data = json.loads(library.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    lines = []
    for key, entry in sorted(data.get("grimoires", {}).items()):
        raw = str(entry.get("local_path", ""))
        path = Path(raw.replace("$HOME", str(HOME))).expanduser()
        description = ""
        try:
            description = json.loads((path / "grimoire.json").read_text(encoding="utf-8")).get("description", "")
        except (OSError, json.JSONDecodeError):
            description = "(grimoire.json missing)"
        lines.append(f"- {key}: {description} ({path.as_posix()})")
    return lines


def drift_line() -> str:
    summon = ENGINE_HOME / "rites" / "summon.py"
    if not summon.is_file():
        return ""
    python = sys.executable or "python3"
    try:
        proc = subprocess.run(
            [python, str(summon), "--check", "--format", "json", "--home", str(GRIMOIRE_HOME),
             "--transcript-path", str(GRIMOIRE_HOME / ".session-check.json")],
            capture_output=True, text=True, encoding="utf-8", errors="replace", timeout=CHECK_TIMEOUT,
        )
        report = json.loads(proc.stdout)
    except (OSError, subprocess.TimeoutExpired, json.JSONDecodeError):
        return ""
    if report.get("status") in ("ok", "noop") and proc.returncode == 0:
        return "setup: in sync"
    notes = [m.get("message", "") for m in report.get("messages", []) if m.get("severity") in ("warning", "error")]
    return "setup: drift detected; offer /grm:update (" + "; ".join(notes[:3]) + ")"


def main() -> int:
    out: list[str] = []
    out.append(ensure_engine())
    if not instruction_file_has_block():
        block = routing_block()
        if block:
            out.append("")
            out.append(block)
    grimoires = installed_grimoires()
    out.append("")
    out.append("## Installed grimoires")
    out.extend(grimoires or ["- none registered yet; /grm:setup joins or creates one"])
    drift = drift_line()
    if drift:
        out.append("")
        out.append(drift)
    text = "\n".join(out)
    if len(text) > 9500:
        text = text[:9500] + "\n... (truncated)"
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
