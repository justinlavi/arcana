#!/usr/bin/env python3
"""Join an existing grimoire: clone it into the grimoire home and register it.

The deterministic half of `/grm-setup`. Given a git URL, the rite derives the
grimoire's directory name from the repository name, clones (or fast-forwards)
it under `~/grimoires/`, checks that it carries a `grimoire.json` manifest,
records it in `~/grimoires/library.json`, and registers its skills. Credentials
are whatever git already holds for the host: the rite never asks for a token;
if the clone needs one, git's own credential helper prompts the way it does for
any repository.

Usage:
    python3 rites/install_grimoire.py <git-url> [--name <directory>] [--home <path>]
        [--no-skills] [--format human|json|jsonl]

Exit codes: 0 = installed and registered (or already current), 1 = blocked or
failed (clone failed, no manifest), 2 = argparse invalid arguments.
"""

from __future__ import annotations

import argparse
import contextlib
import io
import json
import re
import subprocess
import sys
from pathlib import Path

import summon_core
from _lib import load_manifest
from diagnostics import ResultReporter, add_output_format_arg

ARCANA_PATH = Path(__file__).resolve().parent.parent
SAFE_KEY_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


def derive_key(url: str) -> str:
    """Directory name for a grimoire, from the last path segment of its URL.

    Local paths (a bare repository on a shared drive, a Windows path with
    backslashes) are taken as paths; everything else goes through the same
    URL parser the installer uses for scopes.
    """
    raw = url.strip()
    looks_local = (
        "\\" in raw
        or re.match(r"^[A-Za-z]:[\\/]", raw) is not None
        or raw.startswith(("/", "./", "../", "~"))
        or Path(raw).exists()
    )
    if looks_local and "://" not in raw and not raw.startswith("git@"):
        name = Path(raw.replace("\\", "/").rstrip("/")).name
    else:
        _host, scope = summon_core.parse_scope_url(raw)
        name = summon_core._library_key_from_repo_path(scope)
    return re.sub(r"\.git$", "", name)


def _run_sync_skills(home: Path) -> tuple[bool, str]:
    cmd = [sys.executable, str(ARCANA_PATH / "rites" / "sync_skills.py"), "--format", "json"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    try:
        report = json.loads(proc.stdout)
        registered = report.get("summary", {}).get("registered", 0)
        return proc.returncode == 0, f"registered {registered} skill(s)"
    except json.JSONDecodeError:
        return proc.returncode == 0, proc.stdout.strip()[-200:]


def main() -> int:
    parser = argparse.ArgumentParser(description="Clone and register an existing grimoire")
    parser.add_argument("url", help="Git URL of the grimoire (https://..., git@host:path.git, or a local path)")
    parser.add_argument("--name", default="", help="Directory name under the grimoire home (default: repository name)")
    parser.add_argument("--home", type=Path, default=summon_core.GRIMOIRES_HOME, help="Grimoire home (default: ~/grimoires)")
    parser.add_argument("--no-skills", action="store_true", help="Skip skill registration after the clone")
    add_output_format_arg(parser)
    args = parser.parse_args()
    human = args.format == "human"

    home = args.home.expanduser().resolve()
    summon_core.GRIMOIRES_HOME = home
    summon_core.LOCAL_LIBRARY = home / "library.json"
    reporter = ResultReporter("install_grimoire", root=home, mode="apply")

    key = args.name.strip() or derive_key(args.url)
    if not key or not SAFE_KEY_RE.fullmatch(key):
        reporter.message("error", f"cannot derive a safe directory name from {args.url!r}; pass --name")
        if human:
            print(f"  [ERROR] Cannot derive a directory name from {args.url!r}; pass --name <directory>")
        else:
            reporter.emit(args.format)
        return 1

    target = home / key
    existed = (target / ".git").is_dir()
    summary = {"key": key, "path": str(target), "url": args.url, "manifest": "unknown", "skills": "skipped"}

    sink = contextlib.nullcontext() if human else contextlib.redirect_stdout(io.StringIO())
    with sink:
        log = summon_core.Logger()
        if human:
            print()
            print("  Join a grimoire")
            print("  ---------------")
            print()
        if not summon_core.check_git(log):
            reporter.message("error", "git is required but not found on PATH")
            cloned = False
        else:
            home.mkdir(parents=True, exist_ok=True)
            entry = {"name": key, "online_path": args.url}
            cloned = summon_core.install_grimoire(key, entry, log)

        if not cloned:
            reporter.message(
                "error",
                f"could not clone {args.url} into {target}: check the URL, your VPN, and that git "
                "already holds a credential for this host (git prompts once, the way it does for any repository)",
                path=target,
            )
        else:
            reporter.mutation("pull" if existed else "clone", path=target, detail=args.url)
            manifest, errors = load_manifest(target)
            if manifest is None or errors:
                summary["manifest"] = "missing" if manifest is None else "invalid"
                reporter.message(
                    "error",
                    f"{key} is on disk but is not a registered grimoire yet: "
                    + ("; ".join(errors) if errors else "no grimoire.json")
                    + ". Run /grm-adopt to write its manifest, then /grm-sync library.",
                    path=target,
                )
                reporter.set_status("blocked")
            else:
                summary["manifest"] = "ok"
                summon_core.update_local_library([key], {"grimoires": {key: entry}}, log)
                reporter.mutation("register", path=summon_core.LOCAL_LIBRARY, detail=key)
                if not args.no_skills:
                    ok, detail = _run_sync_skills(home)
                    summary["skills"] = "synced" if ok else "failed"
                    reporter.message("info" if ok else "warning", f"skill registration: {detail}")
                    if ok:
                        log.ok(f"Skills registered ({detail})")
                    else:
                        log.warn(f"Skill registration failed: {detail}")

    if human:
        print()
        if reporter.status() in ("ok", "noop"):
            print(f"  [OK]    {key} is installed at {target} and registered in the library.")
            print("  Open a fresh agent session so it sees the grimoire's skills.")
        else:
            for message in reporter.messages:
                if message["severity"] == "error":
                    print(f"  [ERROR] {message['message']}")
        return reporter.exit_code()

    reporter.emit(args.format, summary=summary)
    return reporter.exit_code()


if __name__ == "__main__":
    sys.exit(main())
