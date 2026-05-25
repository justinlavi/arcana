#!/usr/bin/env python3
"""DearPyGui front end for the Arcana Summoning Rite.

Sister module to `summon.py` (the dispatcher) and `summon_core.py` (the
install engine). This module is imported lazily by summon.py only when the
user is in GUI mode  headless installs never touch DearPyGui.

The main entry point is `run_gui(args)`. Everything else (settings
persistence, background workers with cancellation, theme system, the four
tabs, log panel) supports it.
"""

import json
import os
import re
import signal
import subprocess
import sys
import threading
import time
import uuid
from collections import deque
from datetime import datetime
from pathlib import Path
from queue import Queue

from summon_core import (
    ARCANA_DIR,
    CLAUDE_MD,
    CODEX_AGENTS_MD,
    DEFAULT_ARCANA_URL,
    GRIMOIRE_BLOCK,
    GRIMOIRES_HOME,
    LOCAL_LIBRARY,
    REPO_ROOT,
    RITE_DIR,
    SETTINGS_DEFAULTS,
    SETTINGS_PATH,
    _subprocess_env,
    check_git,
    discover_grimoires,
    git,
    inject_agent_file,
    install_arcana,
    install_grimoire,
    register_skills,
    resolve_arcana_url,
    system_python,
    update_local_library,
)


# ===========================================================================
# GUI mode (Dear PyGui)
# ===========================================================================
#
# Tabbed UI with threaded background workers, live log streaming, cancellation,
# settings persistence, and full coverage of the underlying rite scripts:
#  - Install:    discover (GitHub/GitLab) + select + install Arcana + grimoires
#  - Manage:     list installed + per-row update/remove/re-register, library
#                 sync (dry-run/apply), adopt unmanaged directories
#  - Settings:   custom Arcana URL, agent file targets, skip-skills toggle,
#                 theme  persisted to ~/.config/grimoire/summon.json
#  - Diagnostics: environment dump + downloadable bundle
#
# All long operations run in Worker threads; log lines flow through a
# thread-safe queue drained on the DPG main thread per frame. Cancellation
# uses a threading.Event + active-process slot so the running git subprocess
# can be terminated mid-operation.


# ---------------------------------------------------------------------------
# Settings persistence
# ---------------------------------------------------------------------------


def load_settings():
    """Load persisted settings; merge with defaults."""
    settings = dict(SETTINGS_DEFAULTS)
    if SETTINGS_PATH.is_file():
        try:
            with open(SETTINGS_PATH) as f:
                user = json.load(f)
            if isinstance(user, dict):
                for k, v in user.items():
                    if k in SETTINGS_DEFAULTS:
                        settings[k] = v
        except (json.JSONDecodeError, OSError):
            pass
    return settings


def save_settings(updated):
    """Atomically merge & write settings; only known keys are persisted."""
    settings = load_settings()
    for k, v in (updated or {}).items():
        if k in SETTINGS_DEFAULTS:
            settings[k] = v
    SETTINGS_PATH.parent.mkdir(parents=True, exist_ok=True)
    tmp = SETTINGS_PATH.with_suffix(".json.tmp")
    with open(tmp, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")
    tmp.replace(SETTINGS_PATH)
    return settings


def _import_sister_scripts():
    """Import sync_library + adopt_grimoire helpers.

    Tries the rites/ dir of THIS script first (running from inside an
    installed Arcana clone or a dev checkout), then falls back to the
    installed Arcana's rites/ dir. The fallback is what makes the bootstrap
    flow work  the curl|bash bootstrap drops only summon.py into a temp
    dir, but the user's already-installed ~/grimoires/arcana/rites/ has
    the full set of sister scripts.
    """
    candidates = []
    if (RITE_DIR / "sync_library.py").is_file():
        candidates.append(RITE_DIR)
    installed_rites = ARCANA_DIR / "rites"
    if (installed_rites / "sync_library.py").is_file() and installed_rites != RITE_DIR:
        candidates.append(installed_rites)
    if not candidates:
        raise ImportError(
            f"Could not locate sync_library.py / adopt_grimoire.py. "
            f"Looked in {RITE_DIR} and {installed_rites}. "
            f"Install Arcana first via the Install tab, then retry."
        )
    chosen = candidates[0]
    if str(chosen) not in sys.path:
        sys.path.insert(0, str(chosen))
    import sync_library
    import adopt_grimoire
    return sync_library, adopt_grimoire


# ---------------------------------------------------------------------------
# Worker / RunQueue / GuiLogger
# ---------------------------------------------------------------------------


class _ProcSlot:
    """Thread-safe holder for the active subprocess.Popen of a worker."""
    def __init__(self, cancel_event):
        self._lock = threading.Lock()
        self._proc = None
        self._cancel = cancel_event

    def set(self, proc):
        with self._lock:
            self._proc = proc
        if self._cancel.is_set():
            self.terminate_active()

    def clear(self):
        with self._lock:
            self._proc = None

    def terminate_active(self):
        with self._lock:
            p = self._proc
        if p is None:
            return
        try:
            p.terminate()
        except Exception:
            pass


class RunQueue:
    """Thread-safe per-run log buffer + queue.

    Producer (worker thread): push() to add events.
    Consumer (DPG main thread): drain() pops everything queued since last call.
    Bounded history at 10_000 lines to cap memory.
    """
    HISTORY_LIMIT = 10_000

    def __init__(self, title=""):
        self.title = title
        self.history = deque(maxlen=self.HISTORY_LIMIT)
        self._pending = Queue()
        self.done = False
        self.cancelled = False
        self.error = None
        self.summary = None
        self.created = time.time()

    def push(self, event):
        self.history.append(event)
        self._pending.put(event)

    def drain(self):
        out = []
        while True:
            try:
                out.append(self._pending.get_nowait())
            except Exception:
                break
        return out

    def mark_done(self, summary=None, error=None, cancelled=False):
        self.done = True
        self.cancelled = cancelled
        self.error = error
        self.summary = summary
        # Sentinel to signal end-of-stream.
        self._pending.put({"_done": True})


def _make_event(level, msg):
    return {"ts": time.time(), "level": level, "msg": str(msg)}


class GuiLogger:
    """Logger that writes to a RunQueue. Same surface as CLI Logger."""
    def __init__(self, run_queue):
        self.q = run_queue

    def info(self, msg):  self.q.push(_make_event("INFO",  msg))
    def ok(self, msg):    self.q.push(_make_event("OK",    msg))
    def warn(self, msg):  self.q.push(_make_event("WARN",  msg))
    def err(self, msg):   self.q.push(_make_event("ERROR", msg))
    def line(self, text): self.q.push(_make_event("LINE",  text))


class Worker:
    """Background thread running one operation; tracked by run_id.

    The function it runs receives (log, cancel_event, proc_slot, **kwargs).
    """
    def __init__(self, run_id, title, fn, kwargs, run_queue):
        self.run_id = run_id
        self.title = title
        self.fn = fn
        self.kwargs = kwargs
        self.run_queue = run_queue
        self.cancel_event = threading.Event()
        self.proc_slot = _ProcSlot(self.cancel_event)
        self.thread = threading.Thread(
            target=self._run, name=f"summon-worker-{run_id}", daemon=True,
        )

    def start(self):
        self.thread.start()

    def cancel(self):
        self.cancel_event.set()
        self.proc_slot.terminate_active()

    def _run(self):
        log = GuiLogger(self.run_queue)
        try:
            summary = self.fn(
                log=log,
                cancel_event=self.cancel_event,
                proc_slot=self.proc_slot,
                **self.kwargs,
            )
            self.run_queue.mark_done(
                summary=summary, cancelled=self.cancel_event.is_set(),
            )
        except Exception as e:
            err_msg = f"Worker crashed: {type(e).__name__}: {e}"
            log.err(err_msg)
            self.run_queue.mark_done(
                error=err_msg, cancelled=self.cancel_event.is_set(),
            )


# ---------------------------------------------------------------------------
# Cancellable git wrapper
# ---------------------------------------------------------------------------


def git_cancellable(*args, log=None, proc_slot=None):
    """git() variant using Popen + ProcSlot so workers can SIGTERM mid-op."""
    try:
        proc = subprocess.Popen(
            ["git"] + list(args),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            env=_subprocess_env(),
        )
    except FileNotFoundError:
        if log is not None:
            log.line("git executable not found on PATH")
        return False, ""

    if proc_slot is not None:
        proc_slot.set(proc)
    try:
        stdout, stderr = proc.communicate()
    finally:
        if proc_slot is not None:
            proc_slot.clear()

    if proc.returncode != 0 and log is not None and stderr:
        for line in stderr.rstrip().splitlines():
            log.line(line)
    return proc.returncode == 0, (stdout or "").strip()


def install_arcana_cancellable(arcana_url, log, cancel_event, proc_slot):
    """install_arcana with cancellation support."""
    log.info("Installing Arcana...")
    if cancel_event.is_set():
        log.warn("Cancelled before Arcana install")
        return False

    if (ARCANA_DIR / ".git").is_dir():
        log.info("Arcana already installed - pulling latest...")
        ok, _ = git_cancellable(
            "-C", str(ARCANA_DIR), "pull", "--ff-only",
            log=log, proc_slot=proc_slot,
        )
        if ok:
            log.ok(f"Arcana updated: {ARCANA_DIR}")
        else:
            log.warn("Arcana pull failed (local changes?) - skipping update")
            log.ok(f"Arcana exists: {ARCANA_DIR}")
    elif arcana_url:
        log.info(f"Cloning Arcana from {arcana_url}...")
        ok, _ = git_cancellable(
            "clone", arcana_url, str(ARCANA_DIR),
            log=log, proc_slot=proc_slot,
        )
        if ok:
            log.ok(f"Arcana cloned to {ARCANA_DIR}")
        else:
            log.err("Failed to clone Arcana - check network and git credentials")
            return False
    else:
        if ARCANA_DIR.is_dir():
            log.ok(f"Arcana exists: {ARCANA_DIR}")
        else:
            log.err("Cannot detect Arcana origin URL")
            return False
    return True


def install_grimoire_cancellable(key, entry, log, cancel_event, proc_slot):
    """install_grimoire with cancellation support."""
    name = entry.get("name", key)
    url = entry.get("online_path", "")
    target = GRIMOIRES_HOME / key

    if cancel_event.is_set():
        log.warn(f"Cancelled before installing {name}")
        return False

    if (target / ".git").is_dir():
        log.info(f"{name} already installed - pulling latest...")
        ok, _ = git_cancellable(
            "-C", str(target), "pull", "--ff-only",
            log=log, proc_slot=proc_slot,
        )
        if ok:
            log.ok(f"{name} updated: {target}")
        else:
            log.warn(f"{name} pull failed (local changes?) - skipping update")
            log.ok(f"{name} exists: {target}")
        return True
    elif target.is_dir():
        log.warn(f"{name} directory exists but is not a git repo - skipping")
        return True
    else:
        log.info(f"Cloning {name} from {url}...")
        ok, _ = git_cancellable(
            "clone", url, str(target),
            log=log, proc_slot=proc_slot,
        )
        if ok:
            log.ok(f"Cloned {name} to {target}")
            return True
        else:
            log.err(f"Failed to clone {name}")
            return False


# ---------------------------------------------------------------------------
# Settings-aware install pipeline
# ---------------------------------------------------------------------------


def finalize_install_with_settings(installed_keys, library, log, settings):
    """finalize_install honoring agent_targets and skip_skill_registration."""
    if installed_keys:
        update_local_library(installed_keys, library, log)

    targets = settings.get("agent_targets", ["claude", "codex"])
    if "claude" in targets:
        inject_agent_file(log, CLAUDE_MD, "CLAUDE.md")
    else:
        log.info("Skipping CLAUDE.md injection (per Settings)")
    if "codex" in targets:
        inject_agent_file(log, CODEX_AGENTS_MD, "AGENTS.md")
    else:
        log.info("Skipping AGENTS.md injection (per Settings)")

    if settings.get("skip_skill_registration"):
        log.info("Skipping skill registration (per Settings)")
        return True
    return register_skills(log)


# ---------------------------------------------------------------------------
# Worker functions  receive (log, cancel_event, proc_slot, **kwargs)
# ---------------------------------------------------------------------------


class _ResolveArgs:
    """Stub for resolve_arcana_url() which expects argparse skill-prefix shape."""
    def __init__(self, arcana_url=None):
        self.arcana_url = arcana_url


def _worker_discover(scope_url, token, log, cancel_event, proc_slot, **_kw):
    """Run discovery; returns {entries, count}."""
    entries = {}
    if scope_url and not cancel_event.is_set():
        discovered = discover_grimoires(scope_url, log, explicit_token=token)
        for k, v in discovered.items():
            if k not in entries:
                entries[k] = v
    elif not scope_url:
        log.info("No scope URL - skipping grimoire discovery")
    log.ok(f"Total available: {len(entries)} grimoire(s)")
    return {"entries": entries, "count": len(entries)}


def _worker_install_arcana(arcana_url, log, cancel_event, proc_slot, **_kw):
    """Install/update Arcana only."""
    if not check_git(log):
        return {"ok": False, "reason": "git not found"}
    GRIMOIRES_HOME.mkdir(parents=True, exist_ok=True)
    settings = load_settings()
    resolved_url = (
        arcana_url
        or settings.get("custom_arcana_url", "")
        or resolve_arcana_url(_ResolveArgs())
    )
    if not install_arcana_cancellable(resolved_url, log, cancel_event, proc_slot):
        return {"ok": False, "reason": "arcana install failed"}
    skills_ok = finalize_install_with_settings(
        [], {"grimoires": {}}, log, settings,
    )
    return {"ok": True, "skills_ok": skills_ok}


def _worker_install_full(arcana_url, library, keys, log, cancel_event, proc_slot, **_kw):
    """Install Arcana + a list of grimoires by key."""
    if not check_git(log):
        return {"ok": False, "reason": "git not found"}
    GRIMOIRES_HOME.mkdir(parents=True, exist_ok=True)

    settings = load_settings()
    resolved_url = (
        arcana_url
        or settings.get("custom_arcana_url", "")
        or resolve_arcana_url(_ResolveArgs())
    )
    if not install_arcana_cancellable(resolved_url, log, cancel_event, proc_slot):
        return {"ok": False, "reason": "arcana install failed"}

    installed = []
    for key in keys:
        if cancel_event.is_set():
            log.warn("Cancelled  stopping after current grimoire")
            break
        entry = library.get("grimoires", {}).get(key)
        if not entry:
            log.warn(f"Skipping {key}  not in library")
            continue
        if install_grimoire_cancellable(key, entry, log, cancel_event, proc_slot):
            installed.append(key)

    skills_ok = finalize_install_with_settings(installed, library, log, settings)
    return {"ok": True, "installed": installed, "skills_ok": skills_ok}


def _worker_update_grimoire(key, log, cancel_event, proc_slot, **_kw):
    """Pull latest for one installed grimoire (or Arcana)."""
    if key == "arcana":
        target = ARCANA_DIR
    else:
        target = GRIMOIRES_HOME / key
    if not (target / ".git").is_dir():
        log.err(f"{key} is not a git repo at {target}")
        return {"ok": False}
    log.info(f"Updating {key}...")
    ok, _ = git_cancellable(
        "-C", str(target), "pull", "--ff-only",
        log=log, proc_slot=proc_slot,
    )
    if ok:
        log.ok(f"{key} updated")
    else:
        log.err(f"{key} pull failed (local changes? diverged history?)")
    return {"ok": ok}


def _worker_remove_grimoire(key, log, cancel_event, proc_slot, **_kw):
    """rm -rf an installed grimoire and remove from library.json."""
    import shutil
    if key == "arcana":
        log.err("Refusing to remove Arcana itself via this action")
        return {"ok": False}
    target = GRIMOIRES_HOME / key
    if not target.is_dir():
        log.err(f"{key} does not exist at {target}")
        return {"ok": False}
    log.info(f"Removing {target}...")
    try:
        shutil.rmtree(target)
        log.ok(f"Removed {target}")
    except OSError as e:
        log.err(f"Could not remove: {e}")
        return {"ok": False}

    if LOCAL_LIBRARY.is_file():
        try:
            with open(LOCAL_LIBRARY) as f:
                lib = json.load(f)
            if key in lib.get("grimoires", {}):
                del lib["grimoires"][key]
                with open(LOCAL_LIBRARY, "w") as f:
                    json.dump(lib, f, indent=2)
                    f.write("\n")
                log.ok(f"Removed {key} from {LOCAL_LIBRARY}")
        except (json.JSONDecodeError, OSError) as e:
            log.warn(f"Could not update library.json: {e}")
    return {"ok": True}


def _worker_register_skills(log, cancel_event, proc_slot, **_kw):
    """Re-run skill registration for all grimoires."""
    settings = load_settings()
    if settings.get("skip_skill_registration"):
        log.warn("Skill registration is disabled in Settings  running anyway as explicit action")
    ok = register_skills(log)
    return {"ok": ok}


def _worker_sync_library(apply, log, cancel_event, proc_slot, **_kw):
    """Library sync (dry-run or apply)."""
    sync_library, _ = _import_sister_scripts()
    home = GRIMOIRES_HOME
    library_path = home / "library.json"
    log.info(f"Scanning {home}...")
    scan = sync_library.scan_grimoire_home(home)
    library = sync_library.load_library(library_path)
    diff = sync_library.diff_library(scan, library, home)

    drift = len(diff["missing"]) + len(diff["stale"]) + len(diff["mismatched"])
    if drift == 0:
        log.ok("Library is in sync with disk")
    else:
        for k in diff["missing"]:    log.ok(f"+ {k} (missing from library)")
        for s in diff["stale"]:      log.warn(f"- {s['key']} (stale)")
        for m in diff["mismatched"]: log.warn(f"~ {m['key']} (mismatched)")

    for w in scan["warnings"]:
        log.warn(w)
    if scan["unmanaged"]:
        for path in scan["unmanaged"]:
            log.info(f"Unmanaged: {path.name}/")

    if apply and drift > 0:
        new_lib = sync_library.build_synced_library(scan, library, home)
        sync_library.write_library(new_lib, library_path)
        log.ok(f"Library written: {library_path}")
    elif apply and drift == 0:
        log.info("Nothing to apply")

    return {
        "ok": True,
        "drift_count": drift,
        "missing": list(diff["missing"]),
        "stale": [s["key"] for s in diff["stale"]],
        "mismatched": [m["key"] for m in diff["mismatched"]],
        "unmanaged": [str(p) for p in scan["unmanaged"]],
        "warnings": list(scan["warnings"]),
        "applied": bool(apply and drift > 0),
    }


def _worker_adopt(directory, skill_prefix, name, description, log, cancel_event, proc_slot, **_kw):
    """Adopt an unmanaged directory by writing grimoire.json."""
    _, adopt_grimoire = _import_sister_scripts()
    home = GRIMOIRES_HOME
    target = Path(directory)
    if not target.is_absolute():
        target = home / directory
    target = target.resolve()

    if not target.is_dir():
        log.err(f"Directory does not exist: {target}")
        return {"ok": False}

    if not adopt_grimoire.SKILL_PREFIX_RE.fullmatch(skill_prefix):
        log.err(f"Invalid skill_prefix '{skill_prefix}' (must match {adopt_grimoire.SKILL_PREFIX_RE.pattern})")
        return {"ok": False}

    manifest_path = target / "grimoire.json"
    if manifest_path.is_file():
        log.err(f"grimoire.json already exists at {manifest_path}")
        return {"ok": False}

    existing = adopt_grimoire.find_existing_skill_prefixes(home)
    if skill_prefix in existing:
        log.err(f"Skill prefix '{skill_prefix}' is already used by '{existing[skill_prefix]}'")
        return {"ok": False, "collision_with": existing[skill_prefix]}

    final_name = name or target.name
    final_desc = description or f"{final_name} grimoire"
    manifest = {
        "name": final_name,
        "skill_prefix": skill_prefix,
        "description": final_desc,
    }
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    log.ok(f"Wrote {manifest_path}")
    log.info("Run Library Sync next, then Re-register Skills if this grimoire ships skills")
    return {"ok": True, "manifest_path": str(manifest_path)}


# ---------------------------------------------------------------------------
# Installed grimoire scan (for Manage tab)
# ---------------------------------------------------------------------------


def scan_installed():
    """Return a list of installed grimoire dicts for the Manage tab."""
    sync_library, _ = _import_sister_scripts()
    out = []
    arcana_info = _grimoire_status(ARCANA_DIR, is_arcana=True)
    if arcana_info:
        out.append(arcana_info)
    if not GRIMOIRES_HOME.is_dir():
        return out
    scan = sync_library.scan_grimoire_home(GRIMOIRES_HOME)
    for g in scan["grimoires"]:
        info = _grimoire_status(g["path"], is_arcana=False)
        if not info:
            continue
        info["name"] = g["manifest"].get("name", g["key"])
        info["skill_prefix"] = g["manifest"].get("skill_prefix", "")
        info["description"] = g["manifest"].get("description", "")
        if g["online_path"] and not info.get("online_path"):
            info["online_path"] = g["online_path"]
        out.append(info)
    return out


def _grimoire_status(path, is_arcana=False):
    if not path.is_dir() or not (path / ".git").is_dir():
        return None
    info = {
        "key": path.name,
        "name": path.name,
        "skill_prefix": "arc" if is_arcana else "",
        "description": "",
        "path": str(path),
        "online_path": "",
        "last_commit": "",
        "branch": "",
        "dirty": False,
        "is_arcana": is_arcana,
    }
    ok, url = git("-C", str(path), "remote", "get-url", "origin")
    if ok: info["online_path"] = url
    ok, branch = git("-C", str(path), "rev-parse", "--abbrev-ref", "HEAD")
    if ok: info["branch"] = branch
    ok, last = git("-C", str(path), "log", "-1", "--format=%h %s (%cr)")
    if ok: info["last_commit"] = last
    ok, status = git("-C", str(path), "status", "--porcelain")
    if ok and status: info["dirty"] = True

    manifest = path / ("arcana.json" if is_arcana else "grimoire.json")
    if manifest.is_file():
        try:
            m = json.loads(manifest.read_text())
            info["name"] = m.get("name", info["name"])
            info["skill_prefix"] = m.get("skill_prefix", info["skill_prefix"])
            info["description"] = m.get("description", "")
        except (json.JSONDecodeError, OSError):
            pass
    elif is_arcana:
        info["description"] = "Arcana  the Grimoire framework"
    return info


# ---------------------------------------------------------------------------
# Diagnostics
# ---------------------------------------------------------------------------


def _collect_diagnostics():
    """Return a dict of environment + path + probe data."""
    git_ok, git_ver = git("--version")
    py_for_pip = system_python()
    pip_check = subprocess.run(
        [py_for_pip, "-m", "pip", "--version"],
        capture_output=True, text=True,
        env=_subprocess_env(),
    )
    return {
        "python": sys.version.split()[0],
        "python_executable": sys.executable,
        "python_for_subprocesses": py_for_pip,
        "frozen": bool(getattr(sys, "frozen", False)),
        "platform": sys.platform,
        "git": git_ver if git_ok else "(not found)",
        "pip": pip_check.stdout.strip() if pip_check.returncode == 0 else "(not found)",
        "grimoires_home": str(GRIMOIRES_HOME),
        "arcana_dir": str(ARCANA_DIR),
        "arcana_installed": (ARCANA_DIR / ".git").is_dir(),
        "local_library": str(LOCAL_LIBRARY),
        "local_library_exists": LOCAL_LIBRARY.is_file(),
        "claude_md": str(CLAUDE_MD),
        "claude_md_exists": CLAUDE_MD.is_file(),
        "codex_agents_md": str(CODEX_AGENTS_MD),
        "codex_agents_md_exists": CODEX_AGENTS_MD.is_file(),
        "claude_skills_dir": str(Path.home() / ".claude" / "skills"),
        "claude_skills_present": (Path.home() / ".claude" / "skills").is_dir(),
        "codex_skills_dir": str(Path.home() / ".codex" / "skills"),
        "codex_skills_present": (Path.home() / ".codex" / "skills").is_dir(),
        "settings_path": str(SETTINGS_PATH),
        "settings_exists": SETTINGS_PATH.is_file(),
        "deps_path": os.environ.get("GRIMOIRE_SUMMON_PY_DEPS", ""),
        "display": os.environ.get("DISPLAY", ""),
        "wayland_display": os.environ.get("WAYLAND_DISPLAY", ""),
        "xdg_session_type": os.environ.get("XDG_SESSION_TYPE", ""),
    }


def _format_diagnostics_bundle(diag):
    lines = [
        "Grimoire Summon  diagnostic bundle",
        f"Generated: {datetime.now().isoformat()}",
        "",
    ]
    for k, v in diag.items():
        lines.append(f"{k}: {v}")
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------------------
# Dear PyGui setup helpers (import, DPI, fonts, theme, GL probe)
# ---------------------------------------------------------------------------


def _ensure_dearpygui():
    """Import Dear PyGui from system Python or the consented dependency cache."""
    dep_dir = Path(
        os.environ.get(
            "GRIMOIRE_SUMMON_PY_DEPS",
            Path.home() / ".cache" / "grimoire" / "summon-python",
        )
    )
    if dep_dir.is_dir() and str(dep_dir) not in sys.path:
        sys.path.insert(0, str(dep_dir))

    try:
        import dearpygui.dearpygui as dpg
        return dpg
    except ImportError:
        raise ImportError(
            "Dear PyGui is not installed. Re-run and answer y when asked to "
            "install GUI dependencies, install it manually, or run with --cli."
        )


# Palette derived from arcana_icon_1024.png  pinks / purples / indigos.
# Surfaces are intentionally desaturated dark gray-purple (NOT full indigo),
# so the magenta primary buttons and pink section headers  the actual
# signature colors of the icon  remain the loudest things on screen.
# Log levels keep the conventional terminal scheme (white/green/yellow/red)
# for instant recognition.
GUI_COLORS = {
    # ---- Surfaces  three tiers: window > card > inner ----
    # Each tier nudges saturation slightly higher so cards feel lifted,
    # but all stay in the dark-gray-with-a-hint-of-purple zone.
    "bg":              (12, 10, 18),     # window  near-black, faint cool tint
    "bg_card":         (22, 18, 32),     # section cards  neutral dark
    "bg_card_alt":     (30, 24, 42),     # nested lists / log - one step up
    "bg_input":        (18, 14, 26),     # input fields  minimal tint
    "bg_input_hov":    (42, 30, 60),     # hover  purple wakes up
    "border":          (60, 42, 90),     # softer purple, less saturated
    "border_strong":   (137, 12, 158),   # icon's magenta  focus accent
    # ---- Text ----
    "text":            (235, 230, 240),  # warm near-white
    "text_muted":      (145, 132, 170),  # muted gray-purple (secondary)
    "text_title":      (231, 100, 208),  # signature bright pink  primary headers
    "text_section_b":  (200, 80, 195),   # magenta  Discover, Library drift
    "text_section_c":  (175, 130, 225),  # lavender  Preview, Settings B, Adopt
    "text_section_d":  (255, 150, 215),  # pale pink  Diagnostics
    "accent":          (231, 100, 208),
    "accent_hover":    (255, 150, 215),
    # ---- Primary action (Install, Discover, Save, Apply, Adopt) ----
    # The strongest color on screen  the eye lands here.
    "btn_primary":     (137, 12, 158),   # icon's dark magenta
    "btn_primary_hov": (180, 35, 200),
    "btn_primary_act": (108, 0, 128),
    # ---- Secondary (Reload, Update, Re-register, navigation) ----
    # Just slightly lifted from the card bg so it reads as "clickable"
    # without competing with the primary magenta.
    "btn_secondary":     (40, 32, 56),
    "btn_secondary_hov": (60, 48, 86),
    "btn_secondary_act": (32, 26, 48),
    # ---- Danger (Remove, Cancel)  warm red, distinct from magenta ----
    "btn_danger":      (200, 70, 90),
    "btn_danger_hov":  (225, 95, 115),
    "btn_danger_act":  (170, 50, 70),
    # ---- Misc ----
    "separator":       (60, 42, 90),     # match border
    "checkmark":       (231, 100, 208),
    # ---- Log line colors  terminal-conventional, slightly tuned to palette ----
    "log_info":        (235, 230, 240),  # match body text (warm white)
    "log_ok":          (95, 230, 130),   # green
    "log_warn":        (255, 200, 60),   # yellow
    "log_err":         (255, 95, 115),   # red (leans pink to fit palette)
    "log_line":        (145, 132, 170),  # muted (raw subprocess output)
    "log_ts":          (90, 78, 115),    # very muted (timestamps)
    "badge_ok_bg":     (25, 70, 40),
    "badge_dirty_bg":  (90, 25, 50),
}


# ---------------------------------------------------------------------------
# UI metrics (replace inline magic numbers)
# ---------------------------------------------------------------------------
#
# All values are in pre-scale (1.0) pixels. They are calibrated against the
# theme styles set in _build_grimoire_theme:
#     FramePadding:  8 x 6     -> adds ~12 to each input/button height
#     ItemSpacing:   10 x 8    -> adds ~8 between stacked items
#     WindowPadding: 18 x 16   -> outer card padding
#     font:          ~18px     -> one text row ~24 (font + spacing)
# Tweak these together with the theme; everything else derives from them.
#
# Run-time sizing is preferred where possible (button widths via
# `btn_w(dpg, label, scale)`, list widths via `width=-1`); these constants
# only encode dimensions DPG cannot infer.


class M:
    """Centralized UI metrics. All in pre-scale pixels."""

    # ---- Widget heights (one row each, theme-tuned) ----
    TEXT       = 24    # one line of dpg.add_text
    INPUT      = 32    # input_text / button / combo
    CHECKBOX   = 28    # checkbox row
    SEPARATOR  = 12    # add_separator height
    SECTION_HEADER = 28  # icon-prefixed section title row + its separator

    # ---- Vertical spacing ----
    GAP_XS     = 4     # tightest (within a row)
    GAP_S      = 8     # default (between items inside a card)
    GAP        = 12    # between sections inside a tab
    GAP_L      = 18    # major divisions

    # ---- Card chrome (top + bottom padding from card theme + 1px border) ----
    CARD_PAD   = 28

    # ---- Inner scroll boxes (lists, log) ----
    LIST_S     = 150   # short - drift box
    LIST_M     = 220   # medium - discoverable grimoires
    LIST_L     = 280   # large - installed grimoires
    LIST_XL    = 360   # extra-large - diagnostics

    # ---- Viewport defaults ----
    # Sized to fit the Install tab fully visible (3 sections + button + log)
    # without scrolling on a 1080p display, with breathing room.
    VIEWPORT_W       = 1040
    VIEWPORT_H       = 960
    VIEWPORT_W_MIN   = 720
    VIEWPORT_H_MIN   = 600

    # ---- Modal ----
    MODAL_W       = 440
    MODAL_PAD     = 20    # interior padding (used to compute wrap width)

    # ---- Button sizing ----
    BTN_PAD_X     = 24    # extra width past rendered text
    BTN_MIN_W     = 64    # minimum so labels never get cropped
    BTN_BIG_H     = 36    # primary call-to-action height (Install)

    # ---- Font ----
    FONT_SIZE     = 18    # base font size; everything else (TEXT, INPUT, etc.)
                          # is calibrated against this. Changing this requires
                          # re-checking the row-height constants above.

    # ---- Common input widths (where -1 / -N is not applicable) ----
    SCOPE_INPUT_TRAIL = 130  # space reserved for the Discover button + gap
    INPUT_M           = 220  # Adopt: skill prefix input
    INPUT_L           = 280  # Adopt: directory / name / desc inputs
    SEARCH_W          = 280  # log + grimoire search inputs


def px(v, scale):
    """Pre-scale pixel -> actual pixel int. Use everywhere a DPG dim is set."""
    return int(round(v * scale))


def card_h(*content_heights):
    """Compute a section card's height from the heights of its content rows.

    Pass in pre-scale row heights (use M.TEXT, M.INPUT, M.CHECKBOX, M.GAP_S,
    plus inner-box heights like M.LIST_M). The card chrome (top+bottom
    padding + border) is added automatically.

    Example: a card with one description line, one input, and a 220px list:
        height=card_h(M.TEXT, M.INPUT, M.GAP_S, M.LIST_M)
    """
    return sum(content_heights) + M.CARD_PAD


def btn_w(dpg, label, scale, pad=None, min_w=None):
    """Auto-size a button to its label.

    Uses dpg.get_text_size when a font is bound; falls back to a char-count
    estimate otherwise. Always at least M.BTN_MIN_W so very short labels
    don't render as awkward squares.
    """
    pad   = M.BTN_PAD_X if pad   is None else pad
    min_w = M.BTN_MIN_W if min_w is None else min_w
    try:
        size = dpg.get_text_size(label)
        if size and size[0] > 0:
            return max(px(min_w, scale), int(size[0]) + px(pad, scale))
    except Exception:
        pass
    # Fallback: ~9px per character at base font (DejaVuSans/Helvetica @ 18pt).
    return max(px(min_w, scale), px(len(label) * 9 + pad, scale))


def _compute_dpi_scale():
    """Best-effort DPI scale factor. 1.0 on standard 1080p, ~1.5-2.0 on 4K."""
    override = os.environ.get("GRIMOIRE_GUI_SCALE", "").strip()
    if override:
        try:
            v = float(override)
            return max(0.5, min(4.0, v))
        except ValueError:
            pass
    # Skip Tk probe on macOS: Python 3.9 builds with bundled Tcl/Tk abort with
    # "Tcl_FindHashEntry on deleted table" on init+destroy. Cocoa-backed DPG
    # handles Retina backing automatically, so 1.0 is correct on Retina.
    if sys.platform != "darwin":
        try:
            import tkinter
            root = tkinter.Tk()
            root.withdraw()
            dpi = root.winfo_fpixels("1i")
            root.destroy()
            if dpi and dpi > 0:
                return max(1.0, min(3.0, dpi / 96.0))
        except Exception:
            pass
    try:
        if sys.platform.startswith("linux"):
            result = subprocess.run(
                ["xrandr", "--current"], capture_output=True, text=True, timeout=2,
            )
            if result.returncode == 0:
                m = re.search(r"current\s+(\d+)\s*x\s*(\d+)", result.stdout)
                if m:
                    height = int(m.group(2))
                    if height >= 2160:
                        return 1.8
                    if height >= 1440:
                        return 1.35
    except Exception:
        pass
    return 1.0


def _find_system_font():
    """Return a path to a usable TTF/OTF font, or None to use DPG default."""
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/dejavu/DejaVuSans.ttf",
        "/usr/share/fonts/noto/NotoSans-Regular.ttf",
        "/System/Library/Fonts/Helvetica.ttc",
        "/System/Library/Fonts/SFNS.ttf",
        "/Library/Fonts/Arial.ttf",
        "C:/Windows/Fonts/segoeui.ttf",
        "C:/Windows/Fonts/arial.ttf",
    ]
    for p in candidates:
        if Path(p).is_file():
            return p
    return None


def _build_grimoire_theme(dpg, palette):
    """Build and return the bound Grimoire theme tag for the given palette."""
    c = palette
    with dpg.theme() as theme:
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_WindowBg, c["bg"])
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, c["bg_card"])
            dpg.add_theme_color(dpg.mvThemeCol_PopupBg, c["bg_card"])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBg, c["bg_input"])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgHovered, c["bg_input_hov"])
            dpg.add_theme_color(dpg.mvThemeCol_FrameBgActive, c["bg_input_hov"])
            dpg.add_theme_color(dpg.mvThemeCol_Border, c["border"])
            dpg.add_theme_color(dpg.mvThemeCol_BorderShadow, (0, 0, 0, 0))
            dpg.add_theme_color(dpg.mvThemeCol_Text, c["text"])
            dpg.add_theme_color(dpg.mvThemeCol_TextDisabled, c["text_muted"])
            dpg.add_theme_color(dpg.mvThemeCol_Button, c["btn_primary"])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, c["btn_primary_hov"])
            dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, c["btn_primary_act"])
            dpg.add_theme_color(dpg.mvThemeCol_CheckMark, c["checkmark"])
            dpg.add_theme_color(dpg.mvThemeCol_Separator, c["separator"])
            dpg.add_theme_color(dpg.mvThemeCol_SeparatorHovered, c["accent"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarBg, c["bg"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrab, c["btn_secondary"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabHovered, c["btn_secondary_hov"])
            dpg.add_theme_color(dpg.mvThemeCol_ScrollbarGrabActive, c["btn_secondary_act"])
            dpg.add_theme_color(dpg.mvThemeCol_TitleBg, c["bg"])
            dpg.add_theme_color(dpg.mvThemeCol_TitleBgActive, c["bg_card"])
            dpg.add_theme_color(dpg.mvThemeCol_Header, c["bg_input_hov"])
            dpg.add_theme_color(dpg.mvThemeCol_HeaderHovered, c["bg_input_hov"])
            dpg.add_theme_color(dpg.mvThemeCol_HeaderActive, c["bg_input"])
            dpg.add_theme_color(dpg.mvThemeCol_Tab, c["btn_secondary"])
            dpg.add_theme_color(dpg.mvThemeCol_TabHovered, c["btn_primary_hov"])
            dpg.add_theme_color(dpg.mvThemeCol_TabActive, c["btn_primary"])
            dpg.add_theme_color(dpg.mvThemeCol_TabUnfocused, c["btn_secondary"])
            dpg.add_theme_color(dpg.mvThemeCol_TabUnfocusedActive, c["btn_secondary_hov"])

            dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_WindowRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_PopupRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_ScrollbarRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_GrabRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_TabRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 18, 16)
            dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 8, 6)
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 8)
            dpg.add_theme_style(dpg.mvStyleVar_ItemInnerSpacing, 6, 4)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 1)
    return theme


def _build_button_themes(dpg):
    """Per-intent button color themes - bind via dpg.bind_item_theme on a button.

    The default global theme already paints buttons in the "primary" purple,
    so most call sites don't need to touch this. Use "secondary" for
    low-stakes navigation actions and "danger" for destructive ones.
    """
    c = GUI_COLORS
    themes = {}

    def make(fill, hov, act):
        with dpg.theme() as t:
            with dpg.theme_component(dpg.mvButton):
                dpg.add_theme_color(dpg.mvThemeCol_Button, fill)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonHovered, hov)
                dpg.add_theme_color(dpg.mvThemeCol_ButtonActive, act)
                dpg.add_theme_style(dpg.mvStyleVar_FrameRounding, 6)
                dpg.add_theme_style(dpg.mvStyleVar_FramePadding, 10, 6)
        return t

    themes["primary"]   = make(c["btn_primary"],   c["btn_primary_hov"],   c["btn_primary_act"])
    themes["secondary"] = make(c["btn_secondary"], c["btn_secondary_hov"], c["btn_secondary_act"])
    themes["danger"]    = make(c["btn_danger"],    c["btn_danger_hov"],    c["btn_danger_act"])

    # Card theme - bordered child windows used to wrap each section.
    with dpg.theme() as card_theme:
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, c["bg_card"])
            dpg.add_theme_color(dpg.mvThemeCol_Border, c["border"])
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 8)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 14, 12)
    themes["card"] = card_theme

    # Inner list theme - slightly different bg for nested list child_windows
    # (grimoire selection list, installed list, drift, diagnostics, log).
    # The mvAll component overrides the global ItemSpacing.y of 8px down to
    # 2px so line-by-line content (log lines, drift entries, diag rows)
    # stacks tightly instead of looking double-spaced. Within an installed
    # grimoire entry we add an explicit separator + spacer for breathing
    # room between grimoires; everything else benefits from the tight pack.
    with dpg.theme() as inner_theme:
        with dpg.theme_component(dpg.mvChildWindow):
            dpg.add_theme_color(dpg.mvThemeCol_ChildBg, c["bg_card_alt"])
            dpg.add_theme_color(dpg.mvThemeCol_Border, c["border"])
            dpg.add_theme_style(dpg.mvStyleVar_ChildRounding, 6)
            dpg.add_theme_style(dpg.mvStyleVar_ChildBorderSize, 1)
            dpg.add_theme_style(dpg.mvStyleVar_WindowPadding, 10, 8)
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_style(dpg.mvStyleVar_ItemSpacing, 10, 2)
    themes["inner"] = inner_theme

    return themes


def _bind_btn(state, item, kind):
    """Bind a per-intent button theme. kind in {primary, secondary, danger}."""
    theme = state.button_themes.get(kind)
    if theme:
        state.dpg.bind_item_theme(item, theme)


def _bind_card(state, item):
    """Bind the bordered-card theme to a child_window used as a section card."""
    theme = state.button_themes.get("card")
    if theme:
        state.dpg.bind_item_theme(item, theme)


def _bind_inner(state, item):
    """Bind the inner-list theme (lighter bg) to nested child_windows."""
    theme = state.button_themes.get("inner")
    if theme:
        state.dpg.bind_item_theme(item, theme)


def _section(dpg, state, label, color_key="text_title", icon="◆", height=None):
    """Open a bordered card with a colored icon-prefixed header.

    Usage:
        with _section(dpg, state, "Source", icon="◆", height=80):
            dpg.add_text("...")

    `height` is the inner card height in pre-scale pixels - explicit because
    DPG's `autosize_y=True` is unreliable when the card contains other
    fixed-height child windows (it falls back to filling available space,
    which makes short sections look like vertical voids). Pick a height that
    matches the content; rule of thumb in pre-scale pixels:
      - text row     ~24
      - input/button ~32
      - checkbox     ~28
      - separator    ~12
      - inner spacer ~8
      - card chrome  ~28  (top+bottom padding + border)
      - then add the height of any nested child_window verbatim.
    """
    c = GUI_COLORS
    scale = state.scale
    # Header row: bright accent icon + section title
    with dpg.group(horizontal=True):
        dpg.add_text(icon, color=c[color_key])
        dpg.add_text(label, color=c[color_key])
    # Underline accent
    dpg.add_separator()
    # Bordered card body - explicit height; autosize_y is too brittle in DPG.
    card_kwargs = dict(border=True, width=-1, no_scrollbar=True)
    if height is not None:
        card_kwargs["height"] = int(round(height * scale))
    else:
        # Fallback: let DPG try (works for content with no nested child_windows).
        card_kwargs["autosize_y"] = True
    card = dpg.add_child_window(**card_kwargs)
    _bind_card(state, card)
    dpg.add_spacer(height=px(M.GAP_S, scale))

    class _Ctx:
        def __enter__(self_inner):
            dpg.push_container_stack(card)
            return self_inner
        def __exit__(self_inner, *exc):
            dpg.pop_container_stack()
            return False

    return _Ctx()


def _resolve_launcher_icon():
    """Find the Arcana icon shipped under resources/. Returns (small, large)."""
    candidates_dirs = []
    meipass = getattr(sys, "_MEIPASS", None)
    if meipass:
        candidates_dirs.append(Path(meipass) / "resources")
    candidates_dirs += [
        ARCANA_DIR / "resources",
        REPO_ROOT / "resources",
        RITE_DIR.parent / "resources",
    ]
    small_name = "arcana_icon_256.png"
    large_name = "arcana_icon_512.png"
    for d in candidates_dirs:
        small = d / small_name
        large = d / large_name
        if small.is_file() or large.is_file():
            small_path = str(small) if small.is_file() else str(large) if large.is_file() else None
            large_path = str(large) if large.is_file() else str(small) if small.is_file() else None
            return small_path, large_path
    return None, None


def _apply_launcher_icon(dpg):
    """Bind the Arcana icon to the viewport's small + large icon slots."""
    small, large = _resolve_launcher_icon()
    if small is None and large is None:
        return
    try:
        if small:
            dpg.set_viewport_small_icon(small)
        if large:
            dpg.set_viewport_large_icon(large)
    except Exception:
        pass


def _setup_fonts(dpg, scale):
    """Load a system font at a DPI-scaled size; bind it as the global font."""
    base_size = px(M.FONT_SIZE, scale)
    font_path = _find_system_font()
    if not font_path:
        try:
            dpg.set_global_font_scale(max(1.0, scale * 1.3))
        except Exception:
            pass
        return None
    try:
        with dpg.font_registry():
            font = dpg.add_font(font_path, base_size)
        dpg.bind_font(font)
        return font
    except Exception:
        try:
            dpg.set_global_font_scale(max(1.0, scale * 1.3))
        except Exception:
            pass
        return None


def _extract_probe_hint(stderr_bytes):
    """Pull the most informative line from a failed probe's stderr."""
    text = (stderr_bytes or b"").decode("utf-8", errors="replace").strip()
    if not text:
        return ""
    keywords = ("glx", "glfw", "opengl", "egl", "error", "assert", "abort",
                "failed", "cannot", "unable", "libgl", "mesa")
    for line in text.splitlines():
        if any(k in line.lower() for k in keywords):
            return line.strip()[:200]
    return text.splitlines()[0].strip()[:200]


def _probe_gui(extra_env=None):
    """Test whether DearPyGui can open an OpenGL window with the given env."""
    env = dict(os.environ)
    env.pop("LD_LIBRARY_PATH", None)
    if extra_env:
        env.update(extra_env)
    code = (
        "import sys, os\n"
        "d = os.environ.get('GRIMOIRE_SUMMON_PY_DEPS', '')\n"
        "if d: sys.path.insert(0, d)\n"
        "import dearpygui.dearpygui as dpg\n"
        "dpg.create_context()\n"
        "try:\n"
        "    dpg.create_viewport(title='_probe', width=300, height=200)\n"
        "    dpg.setup_dearpygui()\n"
        "    dpg.show_viewport()\n"
        "    dpg.render_dearpygui_frame()\n"
        "finally:\n"
        "    dpg.destroy_context()\n"
    )
    try:
        result = subprocess.run(
            [system_python(), "-c", code],
            capture_output=True, timeout=8, env=env,
        )
    except Exception as e:
        return False, f"could not run probe: {e}"
    if result.returncode == 0:
        return True, ""
    return False, _extract_probe_hint(result.stderr)


_GUI_SW_RENDER_ENV = {
    "LIBGL_ALWAYS_SOFTWARE": "1",
    "GALLIUM_DRIVER": "llvmpipe",
}


def _select_gui_env():
    """Pick the first env that makes the GUI work on this machine."""
    ok, hw_err = _probe_gui()
    if ok:
        return {}, "hardware OpenGL"
    print(f"  [INFO]  Hardware OpenGL probe failed ({hw_err}) - retrying with software rendering")
    ok, sw_err = _probe_gui(extra_env=_GUI_SW_RENDER_ENV)
    if ok:
        return dict(_GUI_SW_RENDER_ENV), "software OpenGL (Mesa llvmpipe)"
    return None, (
        f"no usable OpenGL/GLX context "
        f"(hardware: {hw_err}; software: {sw_err}). "
        f"If you're on Wayland, install XWayland - "
        f"`sudo pacman -S xorg-xwayland` on Arch, "
        f"`sudo apt install xwayland` on Debian/Ubuntu. "
        f"Otherwise ensure Mesa is installed."
    )


# ---------------------------------------------------------------------------
# Tag skill_prefix
# ---------------------------------------------------------------------------

# Centralized so refactors stay sane. Use string concatenation for per-row
# dynamic tags (e.g. f"{TAG.INSTALL_GRIM_CHECK}::{key}").

class TAG:
    MAIN = "main_window"
    TAB_BAR = "tab_bar"
    TAB_INSTALL  = "tab_install"
    TAB_MANAGE   = "tab_manage"
    TAB_SETTINGS = "tab_settings"
    TAB_DIAG     = "tab_diag"

    # Install
    INSTALL_ARCANA_URL = "install_arcana_url"
    INSTALL_SCOPE_URL  = "install_scope_url"
    INSTALL_TOKEN      = "install_token"
    INSTALL_DISCOVER_BTN = "install_discover_btn"
    INSTALL_SEARCH     = "install_search"
    INSTALL_SELECT_ALL_CB = "install_select_all_cb"
    INSTALL_GRIMOIRE_LIST = "install_grimoire_list"
    INSTALL_SELECT_COUNT = "install_select_count"
    INSTALL_PREVIEW    = "install_preview"
    INSTALL_BTN        = "install_btn"
    INSTALL_GRIM_CHECK_PREFIX = "install_grim_check"

    # Manage
    MANAGE_INSTALLED_LIST = "manage_installed_list"
    MANAGE_DRIFT          = "manage_drift"
    MANAGE_ADOPT_DIR      = "manage_adopt_dir"
    MANAGE_ADOPT_NS       = "manage_adopt_ns"
    MANAGE_ADOPT_NAME     = "manage_adopt_name"
    MANAGE_ADOPT_DESC     = "manage_adopt_desc"

    # Settings
    SET_ARCANA_URL  = "set_arcana_url"
    SET_TGT_CLAUDE  = "set_tgt_claude"
    SET_TGT_CODEX   = "set_tgt_codex"
    SET_SKIP_SKILLS = "set_skip_skills"
    SET_STATUS      = "set_status"

    # Diagnostics
    DIAG_LIST = "diag_list"

    # Log
    LOG_LINES  = "log_lines"
    LOG_FILTER = "log_filter"
    LOG_SEARCH = "log_search"
    LOG_CANCEL = "log_cancel_btn"
    LOG_ACTIVE = "log_active_label"
    LOG_TOGGLE = "log_toggle_btn"
    LOG_PANEL  = "log_panel"
    LOG_REGION = "log_region"

    # Modal
    MODAL = "modal_window"


# ---------------------------------------------------------------------------
# GUI state (shared between worker callbacks and DPG main thread)
# ---------------------------------------------------------------------------


class GuiState:
    """Holds everything the GUI mutates from callbacks + worker results."""
    LEVEL_RANK = {"ERROR": 4, "WARN": 3, "OK": 2, "INFO": 1, "LINE": 0}
    FILTER_RANK = {"All": 0, "Info+": 1, "OK+": 2, "Warn+": 3, "Errors only": 4}

    def __init__(self, dpg, scale, settings):
        self.dpg = dpg
        self.scale = scale
        self.settings = settings
        # Per-intent button themes, populated by run_gui after context creation.
        self.button_themes = {}           # {"primary"/"secondary"/"danger": theme tag}
        # Library state
        self.discovered = {}              # key -> entry
        self.selected = set()             # selected grimoire keys
        self.installed = []               # list[dict] from scan_installed
        # Active worker
        self.active_run = None            # current Worker
        # Log state
        self.log_lines = deque(maxlen=10_000)
        self.log_filter = "All"
        self.log_search = ""


# ---------------------------------------------------------------------------
# Modal helper
# ---------------------------------------------------------------------------


def show_modal(dpg, scale, title, message, on_ok=None, danger=False, ok_label="OK", cancel_label="Cancel"):
    """Display a modal dialog. on_ok(value) called with True/False on close."""
    if dpg.does_item_exist(TAG.MODAL):
        dpg.delete_item(TAG.MODAL)

    def close(value):
        if dpg.does_item_exist(TAG.MODAL):
            dpg.delete_item(TAG.MODAL)
        if on_ok:
            on_ok(value)

    # Center the modal on the viewport instead of guessing pixels.
    try:
        vw = dpg.get_viewport_client_width() or px(M.VIEWPORT_W, scale)
        vh = dpg.get_viewport_client_height() or px(M.VIEWPORT_H, scale)
    except Exception:
        vw, vh = px(M.VIEWPORT_W, scale), px(M.VIEWPORT_H, scale)
    modal_w = px(M.MODAL_W, scale)
    pos_x = max(0, (vw - modal_w) // 2)
    pos_y = max(0, (vh // 4))  # a bit above center reads more naturally
    with dpg.window(
        label=title,
        tag=TAG.MODAL,
        modal=True,
        no_resize=True,
        no_collapse=True,
        width=modal_w,
        pos=(pos_x, pos_y),
    ):
        # wrap = -1 lets DPG use the available width inside the modal.
        dpg.add_text(message, wrap=-1)
        dpg.add_spacer(height=px(M.GAP_S, scale))
        with dpg.group(horizontal=True):
            ok_w = btn_w(dpg, ok_label, scale)
            if cancel_label:
                dpg.add_button(label=cancel_label,
                               width=btn_w(dpg, cancel_label, scale),
                               callback=lambda *_: close(False))
            dpg.add_button(label=ok_label, width=ok_w,
                           callback=lambda *_: close(True))


# ---------------------------------------------------------------------------
# Spawn / cancel helpers
# ---------------------------------------------------------------------------


def spawn_worker(state, title, fn, kwargs):
    """Cancel any prior run, then start a new Worker; return it."""
    if state.active_run and not state.active_run.run_queue.done:
        try:
            state.active_run.cancel()
        except Exception:
            pass
    rq = RunQueue(title=title)
    import uuid
    run_id = uuid.uuid4().hex[:12]
    worker = Worker(run_id, title, fn, kwargs, rq)
    state.active_run = worker
    worker.start()
    state.dpg.set_value(TAG.LOG_ACTIVE, f"    {title}")
    state.dpg.configure_item(TAG.LOG_CANCEL, show=True)
    return worker


def cancel_active_run(state):
    if state.active_run:
        try:
            state.active_run.cancel()
            state.dpg.set_value(TAG.LOG_ACTIVE, f"    Cancelling...")
        except Exception:
            pass


# ---------------------------------------------------------------------------
# Log rendering
# ---------------------------------------------------------------------------


_LEVEL_COLOR_KEY = {
    "INFO":  "log_info",   # white
    "OK":    "log_ok",     # green
    "WARN":  "log_warn",   # yellow
    "ERROR": "log_err",    # red
    "LINE":  "log_line",   # muted (raw subprocess output)
}

_LEVEL_PILL = {
    "INFO":  "INFO ",
    "OK":    "OK   ",
    "WARN":  "WARN ",
    "ERROR": "ERROR",
    "LINE":  "     ",   # blank - raw output keeps no pill
}


def _format_log_line(ev):
    """Plain-text formatter - used for clipboard/file save only.

    On-screen rendering uses per-line colored widgets; this stays for
    'Save to file' so saved logs stay readable in any editor.
    """
    ts = time.strftime("%H:%M:%S", time.localtime(ev["ts"]))
    if ev["level"] == "LINE":
        return f"[{ts}]          {ev['msg']}"
    return f"[{ts}] [{ev['level']:<5s}] {ev['msg']}"


def _line_matches_filter(ev, filter_label, search):
    rank = GuiState.LEVEL_RANK.get(ev["level"], 0)
    min_rank = GuiState.FILTER_RANK.get(filter_label, 0)
    if rank < min_rank:
        return False
    if search and search.lower() not in ev["msg"].lower():
        return False
    return True


# How many lines to render at most (DPG widget perf cap).
_LOG_VISIBLE_CAP = 600


def _add_log_widget(state, ev):
    """Append one colored log line as three side-by-side text spans:
        [HH:MM:SS]  [LEVEL]  message...
    Each span uses a level-appropriate color.
    """
    dpg = state.dpg
    c = GUI_COLORS
    color = c[_LEVEL_COLOR_KEY.get(ev["level"], "log_info")]
    ts = time.strftime("%H:%M:%S", time.localtime(ev["ts"]))
    pill = _LEVEL_PILL.get(ev["level"], "     ")
    with dpg.group(parent=TAG.LOG_LINES, horizontal=True):
        dpg.add_text(f"[{ts}]", color=c["log_ts"])
        if ev["level"] == "LINE":
            # Raw subprocess output - no pill, muted color, full message
            dpg.add_text(ev["msg"], color=color)
        else:
            dpg.add_text(pill, color=color)
            dpg.add_text(ev["msg"], color=color)


def render_log(state):
    """Re-render the log widget from filtered history.

    Called on filter/search change and on Clear; per-event appends use
    _add_log_widget directly to avoid wiping the whole list every frame.
    """
    dpg = state.dpg
    if not dpg.does_item_exist(TAG.LOG_LINES):
        return
    dpg.delete_item(TAG.LOG_LINES, children_only=True)
    matching = [ev for ev in state.log_lines
                if _line_matches_filter(ev, state.log_filter, state.log_search)]
    if len(matching) > _LOG_VISIBLE_CAP:
        # Surface a notice that older lines are clipped from the view; full
        # history is still in state.log_lines and exported on Save.
        c = GUI_COLORS
        with dpg.group(parent=TAG.LOG_LINES, horizontal=True):
            dpg.add_text(f"... ({len(matching) - _LOG_VISIBLE_CAP} older line(s) hidden - Save to export full log) ...",
                         color=c["text_muted"])
        matching = matching[-_LOG_VISIBLE_CAP:]
    for ev in matching:
        _add_log_widget(state, ev)
    _scroll_log_to_bottom(state)


def _scroll_log_to_bottom(state):
    """Scroll the log child window to the latest line."""
    dpg = state.dpg
    if dpg.does_item_exist(TAG.LOG_LINES):
        try:
            dpg.set_y_scroll(TAG.LOG_LINES, dpg.get_y_scroll_max(TAG.LOG_LINES))
        except Exception:
            pass


def drain_log_queue(state):
    """Called every frame by run_gui. Drains active worker's pending events.

    For perf: append new lines individually (cheap), only do a full re-render
    when filters or search change. The full-render path lives in render_log().
    """
    worker = state.active_run
    if worker is None:
        return
    events = worker.run_queue.drain()
    if not events:
        return
    saw_done = False
    for ev in events:
        if ev.get("_done"):
            saw_done = True
            continue
        state.log_lines.append(ev)
        if _line_matches_filter(ev, state.log_filter, state.log_search) \
                and state.dpg.does_item_exist(TAG.LOG_LINES):
            _add_log_widget(state, ev)
    _scroll_log_to_bottom(state)
    if saw_done:
        _on_run_done(state, worker)


def _on_run_done(state, worker):
    """Invoked when the active worker completes."""
    rq = worker.run_queue
    state.dpg.configure_item(TAG.LOG_CANCEL, show=False)
    title = worker.title
    if rq.cancelled:
        msg = f"  ✗  {title} (cancelled)"
    elif rq.error:
        msg = f"  ⚠  {title} (error - see log)"
    else:
        msg = f"  ✓  {title} (done)"
    state.dpg.set_value(TAG.LOG_ACTIVE, msg)

    # Domain-specific reactions
    summary = rq.summary
    if isinstance(summary, dict):
        if "entries" in summary:
            # Discovery finished - populate selection list
            state.discovered = summary["entries"]
            state.selected = set(state.discovered.keys())
            populate_install_list(state)
        if summary.get("ok") and (summary.get("installed") is not None or "skills_ok" in summary):
            # An install completed - refresh installed list
            try:
                state.installed = scan_installed()
                populate_installed_list(state)
            except Exception:
                pass
        if summary.get("drift_count") is not None:
            populate_drift(state, summary)
    state.active_run = None


# ---------------------------------------------------------------------------
# Install tab
# ---------------------------------------------------------------------------


def _build_install_tab(dpg, state):
    scale = state.scale
    c = GUI_COLORS

    # 1. Source
    with _section(dpg, state, "1.  Arcana source",
                  color_key="text_title", icon="◆",
                  height=card_h(M.TEXT, M.INPUT)):
        dpg.add_text("Where to install Arcana from. Leave blank for the default public repo.",
                     color=c["text_muted"])
        dpg.add_input_text(
            tag=TAG.INSTALL_ARCANA_URL,
            default_value=state.settings.get("custom_arcana_url", ""),
            hint="https://github.com/justinlavi/arcana.git",
            width=-1,
        )
    dpg.add_spacer(height=px(M.GAP, scale))

    # 2. Discover
    with _section(dpg, state, "2.  Discover grimoires",
                  color_key="text_section_b", icon="⊕",
                  height=card_h(
                      M.TEXT,        # description
                      M.INPUT,       # scope + Discover row
                      M.TEXT,        # token label
                      M.INPUT,       # token input
                      M.GAP_S,       # spacer
                      M.INPUT,       # search + select toolbar
                      M.LIST_M,      # grimoire list
                  )):
        dpg.add_text("Search a GitHub/GitLab org or repo (optional). Skip to install Arcana only.",
                     color=c["text_muted"])
        with dpg.group(horizontal=True):
            disc_w = btn_w(dpg, "Discover", scale)
            dpg.add_input_text(
                tag=TAG.INSTALL_SCOPE_URL,
                default_value=state.settings.get("last_scope_url", ""),
                hint="https://github.com/my-org",
                width=-(disc_w + px(M.GAP_S, scale)),
                on_enter=True,
                callback=lambda *_: _on_discover(state),
            )
            disc_btn = dpg.add_button(
                tag=TAG.INSTALL_DISCOVER_BTN, label="Discover",
                width=disc_w,
                callback=lambda *_: _on_discover(state),
            )
            _bind_btn(state, disc_btn, "primary")
        dpg.add_text("Token (optional - auto-detects from env / git credentials):",
                     color=c["text_muted"])
        dpg.add_input_text(
            tag=TAG.INSTALL_TOKEN,
            password=True,
            hint="In-memory only; never persisted",
            width=-1,
            on_enter=True,
            callback=lambda *_: _on_discover(state),
        )
        dpg.add_spacer(height=px(M.GAP_S, scale))

        with dpg.group(horizontal=True):
            dpg.add_input_text(
                tag=TAG.INSTALL_SEARCH,
                hint="Filter discovered grimoires...",
                width=px(M.SEARCH_W, scale),
                callback=lambda *_: populate_install_list(state),
            )
            sa_btn = dpg.add_button(label="Select all",
                                    width=btn_w(dpg, "Select all", scale),
                                    callback=lambda *_: _select_all(state, True))
            sn_btn = dpg.add_button(label="Select none",
                                    width=btn_w(dpg, "Select none", scale),
                                    callback=lambda *_: _select_all(state, False))
            si_btn = dpg.add_button(label="Invert",
                                    width=btn_w(dpg, "Invert", scale),
                                    callback=lambda *_: _select_invert(state))
            for b in (sa_btn, sn_btn, si_btn):
                _bind_btn(state, b, "secondary")
            dpg.add_text("", tag=TAG.INSTALL_SELECT_COUNT, color=c["text_muted"])

        gr_list = dpg.add_child_window(
            tag=TAG.INSTALL_GRIMOIRE_LIST,
            height=px(M.LIST_M, scale), border=True,
        )
        _bind_inner(state, gr_list)
        dpg.add_text(
            "Click Discover above (or skip to install Arcana only).",
            color=c["text_muted"], wrap=-1,
            parent=TAG.INSTALL_GRIMOIRE_LIST,
        )
    dpg.add_spacer(height=px(M.GAP, scale))

    # 3. Preview
    # Up to 5 preview lines (arcana + clone + claude + codex + skills).
    with _section(dpg, state, "3.  Preview",
                  color_key="text_section_c", icon="▤",
                  height=card_h(M.TEXT * 5)):
        with dpg.group(tag=TAG.INSTALL_PREVIEW):
            pass
        _render_preview(state)

    dpg.add_spacer(height=px(M.GAP_L, scale))
    install_btn = dpg.add_button(
        tag=TAG.INSTALL_BTN, label="Install Arcana",
        # Min width set generously so the label can grow ("Install Arcana +
        # 12 grimoire(s)") without re-flowing.
        width=btn_w(dpg, "Install Arcana + 99 grimoire(s)", scale),
        height=px(M.BTN_BIG_H, scale),
        callback=lambda *_: _on_install(state),
    )
    _bind_btn(state, install_btn, "primary")


def _render_preview(state):
    dpg = state.dpg
    if not dpg.does_item_exist(TAG.INSTALL_PREVIEW):
        return
    dpg.delete_item(TAG.INSTALL_PREVIEW, children_only=True)
    targets = state.settings.get("agent_targets", ["claude", "codex"])
    skip = state.settings.get("skip_skill_registration", False)
    sel = len(state.selected)
    items = [("arcana", "Clone or update Arcana to ~/grimoires/arcana/")]
    if sel > 0:
        items.append(("clone", f"Clone {sel} grimoire(s) into ~/grimoires/"))
    if "claude" in targets:
        items.append(("claude", "Inject Grimoire block into ~/.claude/CLAUDE.md"))
    if "codex" in targets:
        items.append(("codex", "Inject Grimoire block into ~/.codex/AGENTS.md"))
    if not skip:
        items.append(("skills", "Register /arc-*, /grm-*, and grimoire-prefix skills to agent skills/ dirs"))
    c = GUI_COLORS
    for pill, text in items:
        with dpg.group(parent=TAG.INSTALL_PREVIEW, horizontal=True):
            dpg.add_text(f"[{pill}]", color=c["accent"])
            dpg.add_text(text)


def _filtered_keys(state):
    q = state.dpg.get_value(TAG.INSTALL_SEARCH) or "" if state.dpg.does_item_exist(TAG.INSTALL_SEARCH) else ""
    q = q.lower()
    keys = sorted(state.discovered.keys())
    if not q:
        return keys
    out = []
    for k in keys:
        e = state.discovered[k]
        hay = f"{k} {e.get('name','')} {e.get('description','')} {e.get('online_path','')}".lower()
        if q in hay:
            out.append(k)
    return out


def populate_install_list(state):
    dpg = state.dpg
    if not dpg.does_item_exist(TAG.INSTALL_GRIMOIRE_LIST):
        return
    dpg.delete_item(TAG.INSTALL_GRIMOIRE_LIST, children_only=True)

    if not state.discovered:
        c = GUI_COLORS
        dpg.add_text(
            "No grimoires discovered yet. Click Discover above.",
            parent=TAG.INSTALL_GRIMOIRE_LIST,
            color=c["text_muted"],
            wrap=-1,
        )
        _refresh_install_count(state)
        return

    for key in _filtered_keys(state):
        e = state.discovered[key]
        label = e.get("name", key)
        desc = e.get("description", "")
        if desc:
            label = f"{label} - {desc}"
        tag = f"{TAG.INSTALL_GRIM_CHECK_PREFIX}::{key}"
        if dpg.does_item_exist(tag):
            dpg.delete_item(tag)
        def _cb(_s, _a, k=key):
            v = state.dpg.get_value(f"{TAG.INSTALL_GRIM_CHECK_PREFIX}::{k}")
            if v: state.selected.add(k)
            else: state.selected.discard(k)
            _refresh_install_count(state)
            _render_preview(state)
        dpg.add_checkbox(
            label=label,
            default_value=key in state.selected,
            tag=tag,
            parent=TAG.INSTALL_GRIMOIRE_LIST,
            callback=_cb,
        )
    _refresh_install_count(state)
    _render_preview(state)


def _refresh_install_count(state):
    dpg = state.dpg
    n = len(state.selected)
    if dpg.does_item_exist(TAG.INSTALL_SELECT_COUNT):
        dpg.set_value(TAG.INSTALL_SELECT_COUNT, f"  {n} selected" if n else "")
    if dpg.does_item_exist(TAG.INSTALL_BTN):
        dpg.configure_item(
            TAG.INSTALL_BTN,
            label=("Install Arcana" if n == 0 else f"Install Arcana + {n} grimoire(s)"),
        )


def _select_all(state, on):
    keys = _filtered_keys(state)
    if on:
        state.selected.update(keys)
    else:
        for k in keys:
            state.selected.discard(k)
    populate_install_list(state)


def _select_invert(state):
    for k in _filtered_keys(state):
        if k in state.selected:
            state.selected.discard(k)
        else:
            state.selected.add(k)
    populate_install_list(state)


def _on_discover(state):
    scope = state.dpg.get_value(TAG.INSTALL_SCOPE_URL).strip()
    token = state.dpg.get_value(TAG.INSTALL_TOKEN).strip()
    if scope:
        try:
            save_settings({"last_scope_url": scope})
            state.settings["last_scope_url"] = scope
        except Exception:
            pass
    spawn_worker(
        state,
        f"Discover {scope or '(no scope)'}",
        _worker_discover,
        {"scope_url": scope, "token": token},
    )


def _on_install(state):
    arcana_url = state.dpg.get_value(TAG.INSTALL_ARCANA_URL).strip()
    keys = sorted(state.selected)
    if keys:
        library = {"grimoires": dict(state.discovered)}
        spawn_worker(
            state,
            f"Install Arcana + {len(keys)}",
            _worker_install_full,
            {"arcana_url": arcana_url, "library": library, "keys": keys},
        )
    else:
        spawn_worker(
            state,
            "Install Arcana",
            _worker_install_arcana,
            {"arcana_url": arcana_url},
        )


# ---------------------------------------------------------------------------
# Manage tab
# ---------------------------------------------------------------------------


def _build_manage_tab(dpg, state):
    scale = state.scale
    c = GUI_COLORS

    with _section(dpg, state, "Installed grimoires",
                  color_key="text_title", icon="◆",
                  height=card_h(M.INPUT, M.GAP_S, M.LIST_L)):
        with dpg.group(horizontal=True):
            r = dpg.add_button(label="Reload",
                               width=btn_w(dpg, "Reload", scale),
                               callback=lambda *_: _refresh_installed(state))
            u = dpg.add_button(label="Update all",
                               width=btn_w(dpg, "Update all", scale),
                               callback=lambda *_: _bulk_update(state))
            rr = dpg.add_button(label="Re-register all skills",
                                width=btn_w(dpg, "Re-register all skills", scale),
                                callback=lambda *_: spawn_worker(state, "Register skills", _worker_register_skills, {}))
            for b in (r, u, rr):
                _bind_btn(state, b, "secondary")
        dpg.add_spacer(height=px(M.GAP_S, scale))
        inst_list = dpg.add_child_window(
            tag=TAG.MANAGE_INSTALLED_LIST,
            height=px(M.LIST_L, scale), border=True,
        )
        _bind_inner(state, inst_list)
        dpg.add_text("Loading...", color=c["text_muted"], parent=TAG.MANAGE_INSTALLED_LIST)

    dpg.add_spacer(height=px(M.GAP, scale))

    with _section(dpg, state, "Library drift",
                  color_key="text_section_b", icon="≈",
                  height=card_h(M.TEXT, M.INPUT, M.GAP_S, M.LIST_S)):
        dpg.add_text("Reconcile ~/grimoires/library.json against what's actually on disk.",
                     color=c["text_muted"])
        with dpg.group(horizontal=True):
            chk = dpg.add_button(label="Check (dry-run)",
                                 width=btn_w(dpg, "Check (dry-run)", scale),
                                 callback=lambda *_: spawn_worker(state, "Library sync", _worker_sync_library, {"apply": False}))
            apl = dpg.add_button(label="Apply sync",
                                 width=btn_w(dpg, "Apply sync", scale),
                                 callback=lambda *_: spawn_worker(state, "Library sync (apply)", _worker_sync_library, {"apply": True}))
            _bind_btn(state, chk, "secondary")
            _bind_btn(state, apl, "primary")
        dpg.add_spacer(height=px(M.GAP_S, scale))
        drift = dpg.add_child_window(
            tag=TAG.MANAGE_DRIFT,
            height=px(M.LIST_S, scale), border=True,
        )
        _bind_inner(state, drift)
        dpg.add_text("Click 'Check' to scan disk vs. library.json.",
                     color=c["text_muted"], parent=TAG.MANAGE_DRIFT)

    dpg.add_spacer(height=px(M.GAP, scale))

    with _section(dpg, state, "Adopt unmanaged directory",
                  color_key="text_section_c", icon="⊕",
                  height=card_h(
                      M.TEXT * 2,    # description (wraps to 2 lines)
                      (M.TEXT + M.INPUT) * 2,  # 2 rows of (label + input)
                      M.GAP_S,
                      M.INPUT,       # Adopt button
                  )):
        dpg.add_text(
            "For directories under ~/grimoires/ that lack a grimoire.json. "
            "Writes the manifest so the grimoire shows up in Manage and can ship skills.",
            color=c["text_muted"],
            wrap=-1,  # wrap to container width
        )
        with dpg.group(horizontal=True):
            with dpg.group():
                dpg.add_text("Directory", color=c["text_muted"])
                dpg.add_input_text(tag=TAG.MANAGE_ADOPT_DIR,
                                   hint="my-existing-folder",
                                   width=px(M.INPUT_L, scale))
            with dpg.group():
                dpg.add_text("Skill prefix", color=c["text_muted"])
                dpg.add_input_text(tag=TAG.MANAGE_ADOPT_NS,
                                   hint="lowercase, e.g. cook",
                                   width=px(M.INPUT_M, scale))
        with dpg.group(horizontal=True):
            with dpg.group():
                dpg.add_text("Name (optional)", color=c["text_muted"])
                dpg.add_input_text(tag=TAG.MANAGE_ADOPT_NAME,
                                   width=px(M.INPUT_L, scale))
            with dpg.group():
                dpg.add_text("Description (optional)", color=c["text_muted"])
                dpg.add_input_text(tag=TAG.MANAGE_ADOPT_DESC,
                                   width=px(M.INPUT_L, scale))
        dpg.add_spacer(height=px(M.GAP_S, scale))
        adopt_btn = dpg.add_button(label="Adopt directory",
                                   width=btn_w(dpg, "Adopt directory", scale),
                                   callback=lambda *_: _on_adopt(state))
        _bind_btn(state, adopt_btn, "primary")


def _refresh_installed(state):
    try:
        state.installed = scan_installed()
    except Exception as e:
        show_modal(state.dpg, state.scale, "Error", f"Could not scan installed: {e}",
                   on_ok=None, ok_label="Close", cancel_label="")
        return
    populate_installed_list(state)


def populate_installed_list(state):
    dpg = state.dpg
    if not dpg.does_item_exist(TAG.MANAGE_INSTALLED_LIST):
        return
    dpg.delete_item(TAG.MANAGE_INSTALLED_LIST, children_only=True)
    c = GUI_COLORS

    if not state.installed:
        dpg.add_text("No grimoires installed yet. Use the Install tab.",
                     parent=TAG.MANAGE_INSTALLED_LIST,
                     color=c["text_muted"])
        return

    for g in state.installed:
        with dpg.group(parent=TAG.MANAGE_INSTALLED_LIST):
            with dpg.group(horizontal=True):
                dpg.add_text(g.get("name", g["key"]), color=c["text_title"])
                if g.get("skill_prefix"):
                    dpg.add_text(f"  ({g['skill_prefix']})", color=c["text_muted"])
                if g.get("dirty"):
                    dpg.add_text("   dirty", color=c["log_err"])
                else:
                    dpg.add_text("   clean", color=c["log_ok"])
            if g.get("description"):
                dpg.add_text(g["description"], color=c["text_muted"], wrap=-1)
            with dpg.group(horizontal=True):
                dpg.add_text(g.get("path", ""), color=c["text_muted"])
            with dpg.group(horizontal=True):
                if g.get("branch"):
                    dpg.add_text(f"branch: {g['branch']}", color=c["text_muted"])
                if g.get("last_commit"):
                    dpg.add_text(f"   {g['last_commit']}", color=c["text_muted"])
            with dpg.group(horizontal=True):
                key = g["key"]
                upd = dpg.add_button(label="Update",
                                     width=btn_w(state.dpg, "Update", state.scale),
                                     callback=lambda s, a, u, k=key: spawn_worker(state, f"Update {k}", _worker_update_grimoire, {"key": k}))
                _bind_btn(state, upd, "secondary")
                if not g.get("is_arcana"):
                    rem = dpg.add_button(label="Remove",
                                         width=btn_w(state.dpg, "Remove", state.scale),
                                         callback=lambda s, a, u, k=key, n=g.get("name", key): _confirm_remove(state, k, n))
                    _bind_btn(state, rem, "danger")
                rrs = dpg.add_button(label="Re-register skills",
                                     width=btn_w(state.dpg, "Re-register skills", state.scale),
                                     callback=lambda s, a, u: spawn_worker(state, "Register skills", _worker_register_skills, {}))
                _bind_btn(state, rrs, "secondary")
            dpg.add_spacer(height=px(M.GAP_XS, state.scale))
            dpg.add_separator()
            dpg.add_spacer(height=px(M.GAP_XS, state.scale))


def _confirm_remove(state, key, name):
    def _on(value):
        if value:
            spawn_worker(state, f"Remove {key}", _worker_remove_grimoire, {"key": key})
    show_modal(
        state.dpg, state.scale,
        f"Remove {name}?",
        f"This will delete ~/grimoires/{key}/ and the matching entry in library.json.\n\n"
        f"The git remote is unaffected - you can re-clone later.",
        on_ok=_on, danger=True, ok_label="Remove",
    )


def _bulk_update(state):
    """Sequentially update each installed grimoire."""
    if not state.installed:
        return
    keys = [g["key"] for g in state.installed]
    def _bulk(log, cancel_event, proc_slot, **_kw):
        ok_count = 0
        for k in keys:
            if cancel_event.is_set():
                log.warn("Cancelled - stopping after current grimoire")
                break
            target = ARCANA_DIR if k == "arcana" else GRIMOIRES_HOME / k
            if not (target / ".git").is_dir():
                log.warn(f"{k} not a git repo - skipping")
                continue
            log.info(f"Updating {k}...")
            ok, _ = git_cancellable("-C", str(target), "pull", "--ff-only",
                                    log=log, proc_slot=proc_slot)
            if ok:
                log.ok(f"{k} updated")
                ok_count += 1
            else:
                log.warn(f"{k} pull failed")
        log.ok(f"Updated {ok_count}/{len(keys)} grimoire(s)")
        return {"ok": True, "updated": ok_count, "total": len(keys)}
    spawn_worker(state, f"Update all ({len(keys)})", _bulk, {})


def _on_adopt(state):
    directory = state.dpg.get_value(TAG.MANAGE_ADOPT_DIR).strip()
    skill_prefix = state.dpg.get_value(TAG.MANAGE_ADOPT_NS).strip()
    name = state.dpg.get_value(TAG.MANAGE_ADOPT_NAME).strip()
    desc = state.dpg.get_value(TAG.MANAGE_ADOPT_DESC).strip()
    if not directory or not skill_prefix:
        show_modal(state.dpg, state.scale, "Required fields",
                   "Directory and skill prefix are required.",
                   on_ok=None, ok_label="OK", cancel_label="")
        return
    spawn_worker(
        state, f"Adopt {directory}",
        _worker_adopt,
        {"directory": directory, "skill_prefix": skill_prefix,
         "name": name, "description": desc},
    )


def populate_drift(state, summary):
    dpg = state.dpg
    if not dpg.does_item_exist(TAG.MANAGE_DRIFT):
        return
    dpg.delete_item(TAG.MANAGE_DRIFT, children_only=True)
    c = GUI_COLORS
    drift = summary.get("drift_count", 0)
    if drift == 0:
        dpg.add_text("No drift - library is in sync with disk.",
                     parent=TAG.MANAGE_DRIFT, color=c["log_ok"])
    else:
        dpg.add_text(f"Drift items: {drift}", parent=TAG.MANAGE_DRIFT, color=c["text_title"])
    def add_section(label, items):
        if not items:
            return
        dpg.add_text(label, parent=TAG.MANAGE_DRIFT, color=c["text"])
        for item in items:
            dpg.add_text(f"   {item}", parent=TAG.MANAGE_DRIFT, color=c["text_muted"])
    add_section("Missing from library:", summary.get("missing"))
    add_section("Stale entries:",        summary.get("stale"))
    add_section("Mismatched paths:",     summary.get("mismatched"))
    add_section("Unmanaged dirs:",       summary.get("unmanaged"))
    add_section("Warnings:",             summary.get("warnings"))
    if summary.get("applied"):
        dpg.add_text("Library updated.", parent=TAG.MANAGE_DRIFT, color=c["log_ok"])


# ---------------------------------------------------------------------------
# Settings tab
# ---------------------------------------------------------------------------


def _build_settings_tab(dpg, state):
    scale = state.scale
    c = GUI_COLORS

    with _section(dpg, state, "Source overrides",
                  color_key="text_title", icon="◆",
                  height=card_h(M.TEXT, M.INPUT)):
        dpg.add_text("Custom Arcana repository URL (blank = auto-detect from local clone or default).",
                     color=c["text_muted"])
        dpg.add_input_text(
            tag=TAG.SET_ARCANA_URL,
            default_value=state.settings.get("custom_arcana_url", ""),
            width=-1,
        )

    dpg.add_spacer(height=px(M.GAP, scale))

    with _section(dpg, state, "Agent integration",
                  color_key="text_section_b", icon="✦",
                  height=card_h(M.TEXT, M.CHECKBOX * 3)):
        dpg.add_text("Which agent instruction files to modify when installing.",
                     color=c["text_muted"])
        targets = state.settings.get("agent_targets", ["claude", "codex"])
        dpg.add_checkbox(label="Claude Code  (~/.claude/CLAUDE.md and ~/.claude/skills/)",
                         tag=TAG.SET_TGT_CLAUDE, default_value=("claude" in targets))
        dpg.add_checkbox(label="Codex/ChatGPT (~/.codex/AGENTS.md and ~/.codex/skills/)",
                         tag=TAG.SET_TGT_CODEX,  default_value=("codex" in targets))
        dpg.add_checkbox(label="Skip skill registration entirely (advanced)",
                         tag=TAG.SET_SKIP_SKILLS,
                         default_value=state.settings.get("skip_skill_registration", False))

    dpg.add_spacer(height=px(M.GAP_L, scale))
    with dpg.group(horizontal=True):
        save_btn = dpg.add_button(label="Save settings",
                                  width=btn_w(dpg, "Save settings", scale),
                                  callback=lambda *_: _save_settings(state))
        _bind_btn(state, save_btn, "primary")
        dpg.add_text("", tag=TAG.SET_STATUS, color=c["text_muted"])


def _save_settings(state):
    targets = []
    if state.dpg.get_value(TAG.SET_TGT_CLAUDE): targets.append("claude")
    if state.dpg.get_value(TAG.SET_TGT_CODEX):  targets.append("codex")
    body = {
        "custom_arcana_url": state.dpg.get_value(TAG.SET_ARCANA_URL).strip(),
        "agent_targets": targets,
        "skip_skill_registration": bool(state.dpg.get_value(TAG.SET_SKIP_SKILLS)),
    }
    try:
        state.settings = save_settings(body)
        state.dpg.set_value(TAG.SET_STATUS, "Saved.")
        _render_preview(state)
    except Exception as e:
        state.dpg.set_value(TAG.SET_STATUS, f"Failed: {e}")


# ---------------------------------------------------------------------------
# Diagnostics tab
# ---------------------------------------------------------------------------


def _build_diag_tab(dpg, state):
    scale = state.scale
    c = GUI_COLORS
    with _section(dpg, state, "Environment",
                  color_key="text_section_d", icon="ⓘ",
                  height=card_h(M.INPUT, M.GAP_S, M.LIST_XL)):
        with dpg.group(horizontal=True):
            r = dpg.add_button(label="Refresh",
                               width=btn_w(dpg, "Refresh", scale),
                               callback=lambda *_: _refresh_diag(state))
            s = dpg.add_button(label="Save bundle...",
                               width=btn_w(dpg, "Save bundle...", scale),
                               callback=lambda *_: _save_diag_bundle(state))
            _bind_btn(state, r, "secondary")
            _bind_btn(state, s, "primary")
        dpg.add_spacer(height=px(M.GAP_S, scale))
        diag = dpg.add_child_window(
            tag=TAG.DIAG_LIST,
            height=px(M.LIST_XL, scale), border=True,
        )
        _bind_inner(state, diag)
        dpg.add_text("Loading...", color=c["text_muted"], parent=TAG.DIAG_LIST)
    _refresh_diag(state)


def _refresh_diag(state):
    dpg = state.dpg
    if not dpg.does_item_exist(TAG.DIAG_LIST):
        return
    dpg.delete_item(TAG.DIAG_LIST, children_only=True)
    c = GUI_COLORS
    diag = _collect_diagnostics()
    for k, v in diag.items():
        with dpg.group(parent=TAG.DIAG_LIST, horizontal=True):
            dpg.add_text(f"{k}:", color=c["text_muted"])
            dpg.add_text(str(v))


def _save_diag_bundle(state):
    """Save the diagnostic bundle to ~/grimoire-diagnostics-<timestamp>.txt."""
    text = _format_diagnostics_bundle(_collect_diagnostics())
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = Path.home() / f"grimoire-diagnostics-{ts}.txt"
    try:
        target.write_text(text, encoding="utf-8")
        show_modal(state.dpg, state.scale, "Bundle saved",
                   f"Saved to:\n{target}",
                   on_ok=None, ok_label="OK", cancel_label="")
    except OSError as e:
        show_modal(state.dpg, state.scale, "Save failed", str(e),
                   on_ok=None, ok_label="OK", cancel_label="")


# ---------------------------------------------------------------------------
# Header + log panel
# ---------------------------------------------------------------------------


def _build_header(dpg, state):
    """Branding-only header. Activity status lives in the log panel header
    below - it has more breathing room and is logically tied to the log
    itself, so the brand stays uncluttered as run titles change."""
    c = GUI_COLORS
    with dpg.group(horizontal=True):
        dpg.add_text("Arcana", color=c["text_title"])
        dpg.add_text("  Summoning Rite", color=c["text_muted"])
    dpg.add_separator()


def _build_log_panel(dpg, state):
    scale = state.scale
    c = GUI_COLORS
    with dpg.group(tag=TAG.LOG_PANEL):
        dpg.add_spacer(height=px(M.GAP_S, scale))
        # Header: distinct visual band so the log feels separate from tab content
        with dpg.group(horizontal=True):
            toggle = dpg.add_button(label="▾ Activity log", tag=TAG.LOG_TOGGLE,
                                    callback=lambda *_: _toggle_log(state),
                                    width=btn_w(dpg, "▾ Activity log", scale))
            _bind_btn(state, toggle, "secondary")
            dpg.add_text("", tag=TAG.LOG_ACTIVE, color=c["text_muted"])
            dpg.add_spacer(width=px(M.GAP, scale))
            dpg.add_text("Filter:", color=c["text_muted"])
            # Combo width = enough for the longest label ("Errors only").
            dpg.add_combo(
                tag=TAG.LOG_FILTER,
                items=["All", "Info+", "OK+", "Warn+", "Errors only"],
                default_value="All",
                width=btn_w(dpg, "Errors only", scale),
                callback=lambda *_: _on_log_filter(state),
            )
            dpg.add_input_text(
                tag=TAG.LOG_SEARCH,
                hint="Search log...",
                width=px(M.SEARCH_W // 2, scale),  # half search width
                callback=lambda *_: _on_log_filter(state),
            )
            clr = dpg.add_button(label="Clear",
                                 width=btn_w(dpg, "Clear", scale),
                                 callback=lambda *_: _on_log_clear(state))
            sav = dpg.add_button(label="Save",
                                 width=btn_w(dpg, "Save", scale),
                                 callback=lambda *_: _on_log_save(state))
            can = dpg.add_button(label="Cancel", tag=TAG.LOG_CANCEL,
                                 width=btn_w(dpg, "Cancel", scale), show=False,
                                 callback=lambda *_: cancel_active_run(state))
            _bind_btn(state, clr, "secondary")
            _bind_btn(state, sav, "secondary")
            _bind_btn(state, can, "danger")
        with dpg.group(tag=TAG.LOG_REGION):
            log_box = dpg.add_child_window(
                tag=TAG.LOG_LINES,
                height=px(M.LIST_M, scale), width=-1, border=True,
            )
            _bind_inner(state, log_box)


def _on_log_filter(state):
    state.log_filter = state.dpg.get_value(TAG.LOG_FILTER) or "All"
    state.log_search = state.dpg.get_value(TAG.LOG_SEARCH) or ""
    render_log(state)


def _on_log_clear(state):
    state.log_lines.clear()
    if state.dpg.does_item_exist(TAG.LOG_LINES):
        state.dpg.delete_item(TAG.LOG_LINES, children_only=True)


def _on_log_save(state):
    ts = datetime.now().strftime("%Y%m%d-%H%M%S")
    target = Path.home() / f"grimoire-summon-log-{ts}.txt"
    try:
        target.write_text(
            "\n".join(_format_log_line(ev) for ev in state.log_lines),
            encoding="utf-8",
        )
        show_modal(state.dpg, state.scale, "Log saved",
                   f"Saved to:\n{target}",
                   on_ok=None, ok_label="OK", cancel_label="")
    except OSError as e:
        show_modal(state.dpg, state.scale, "Save failed", str(e),
                   on_ok=None, ok_label="OK", cancel_label="")


def _toggle_log(state):
    dpg = state.dpg
    cur = dpg.is_item_shown(TAG.LOG_REGION)
    dpg.configure_item(TAG.LOG_REGION, show=not cur)
    dpg.configure_item(TAG.LOG_TOGGLE,
                       label=("▾ Activity log" if not cur else "▸ Activity log"))


# ---------------------------------------------------------------------------
# run_gui
# ---------------------------------------------------------------------------


def run_gui(args):
    """Dear PyGui flow: tabs, threading, live log, cancellation."""
    dpg = _ensure_dearpygui()

    gui_env, label = _select_gui_env()
    if gui_env is None:
        raise RuntimeError(label)
    if gui_env:
        os.environ.update(gui_env)
        print(f"  [INFO]  Using {label} for GUI rendering")

    settings = load_settings()
    # Carry --scope / --arcana-url into settings so the prefill works.
    if args.scope:
        settings["last_scope_url"] = args.scope
        try: save_settings({"last_scope_url": args.scope})
        except Exception: pass
    if args.arcana_url:
        settings["custom_arcana_url"] = args.arcana_url
        try: save_settings({"custom_arcana_url": args.arcana_url})
        except Exception: pass

    scale = _compute_dpi_scale()

    dpg.create_context()
    try:
        _setup_fonts(dpg, scale)
        dpg.bind_theme(_build_grimoire_theme(dpg, GUI_COLORS))

        state = GuiState(dpg, scale, settings)
        state.button_themes = _build_button_themes(dpg)

        # Pre-load installed list (cheap; lets the Manage tab render instantly).
        try:
            state.installed = scan_installed()
        except Exception:
            state.installed = []

        with dpg.window(tag=TAG.MAIN, label="Arcana", no_title_bar=True):
            _build_header(dpg, state)
            with dpg.tab_bar(tag=TAG.TAB_BAR):
                with dpg.tab(label="Install", tag=TAG.TAB_INSTALL):
                    _build_install_tab(dpg, state)
                with dpg.tab(label="Manage", tag=TAG.TAB_MANAGE):
                    _build_manage_tab(dpg, state)
                with dpg.tab(label="Settings", tag=TAG.TAB_SETTINGS):
                    _build_settings_tab(dpg, state)
                with dpg.tab(label="Diagnostics", tag=TAG.TAB_DIAG):
                    _build_diag_tab(dpg, state)
            _build_log_panel(dpg, state)

        dpg.create_viewport(
            title="Arcana - Summoning Rite",
            width=px(M.VIEWPORT_W, scale),
            height=px(M.VIEWPORT_H, scale),
            min_width=px(M.VIEWPORT_W_MIN, scale),
            min_height=px(M.VIEWPORT_H_MIN, scale),
        )
        _apply_launcher_icon(dpg)
        dpg.setup_dearpygui()
        dpg.set_primary_window(TAG.MAIN, True)
        dpg.show_viewport()

        # Initial population
        populate_install_list(state)
        populate_installed_list(state)

        signal.signal(signal.SIGINT, lambda *_: dpg.stop_dearpygui())

        # Custom render loop so we can drain the worker queue every frame.
        # Falling back to dpg.start_dearpygui() would not give us a hook to
        # pull worker events; this manual loop is the standard DPG pattern
        # for that requirement.
        while dpg.is_dearpygui_running():
            drain_log_queue(state)
            dpg.render_dearpygui_frame()
    finally:
        dpg.destroy_context()
