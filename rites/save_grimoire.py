#!/usr/bin/env python3
"""Save a grimoire's changes: validate, commit, pull, push.

The deterministic half of `/grm-save`, the verb that lets someone who does not
use git by hand share what they changed. The rite stages everything git would
track, commits with the message the invocation composed, brings the branch up
to date with the remote by rebasing, and pushes. It refuses to commit a
grimoire that fails validation, stops cleanly when teammates' changes conflict
(the rebase is aborted and the local commit kept), and never force-pushes.

Mutation profile: plan_apply. The default run is a plan: it reports what would
be committed and whether the branch is ahead of or behind its upstream, and
writes nothing. `--apply` performs the save.

Usage:
    python3 rites/save_grimoire.py --grimoire <path> [--message "<text>"] [--apply]
        [--no-push] [--format human|json|jsonl]

Exit codes: 0 = plan rendered, saved, or nothing to save; 1 = blocked (not a git
repository, validation failed, no git identity, conflict) or git error;
2 = argparse invalid arguments.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from _lib import add_grimoire_arg, info, ok, resolve_grimoire_arg, warn
from diagnostics import ResultReporter, add_output_format_arg

ARCANA_PATH = Path(__file__).resolve().parent.parent
GIT_TIMEOUT = 300
STATUS_WORDS = {"A": "added", "M": "changed", "D": "removed", "R": "renamed", "?": "new", "C": "copied", "U": "conflicted"}


def git(root: Path, *args: str, timeout: int = GIT_TIMEOUT) -> tuple[int, str, str]:
    """Run git in the grimoire with prompts disabled; return (code, stdout, stderr)."""
    env = {"GIT_TERMINAL_PROMPT": "0"}
    import os
    full_env = dict(os.environ)
    full_env.update(env)
    try:
        proc = subprocess.run(
            ["git", "-C", str(root), *args],
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout, env=full_env,
        )
    except FileNotFoundError:
        return 127, "", "git is not installed"
    except subprocess.TimeoutExpired:
        return 124, "", f"git {' '.join(args)} timed out after {timeout}s"
    return proc.returncode, proc.stdout, proc.stderr


def working_changes(root: Path) -> list[dict]:
    """Parse `git status --porcelain` into {status, path} records."""
    code, out, _ = git(root, "status", "--porcelain", "--untracked-files=all")
    if code != 0:
        return []
    changes = []
    for line in out.splitlines():
        if len(line) < 4:
            continue
        flag = (line[0] if line[0] != " " else line[1])
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changes.append({"status": STATUS_WORDS.get(flag, flag), "path": path.replace("\\", "/")})
    return changes


def git_identity(root: Path) -> tuple[str, str]:
    name = git(root, "config", "user.name")[1].strip()
    email = git(root, "config", "user.email")[1].strip()
    return name, email


def upstream_state(root: Path, fetch: bool) -> dict:
    """Describe the branch, its upstream, and ahead/behind counts."""
    branch = git(root, "rev-parse", "--abbrev-ref", "HEAD")[1].strip()
    has_remote = git(root, "remote", "get-url", "origin")[0] == 0
    code, up, _ = git(root, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
    upstream = up.strip() if code == 0 else ""
    state = {"branch": branch, "remote": has_remote, "upstream": upstream, "ahead": 0, "behind": 0, "fetched": False}
    if upstream and fetch:
        fcode, _, ferr = git(root, "fetch", "--quiet", timeout=120)
        state["fetched"] = fcode == 0
        state["fetch_error"] = "" if fcode == 0 else ferr.strip()[-200:]
    if upstream:
        code, counts, _ = git(root, "rev-list", "--left-right", "--count", "@{upstream}...HEAD")
        if code == 0:
            behind, ahead = (counts.split() + ["0", "0"])[:2]
            state["behind"], state["ahead"] = int(behind), int(ahead)
    return state


def validation_passes(root: Path) -> tuple[bool, str]:
    cmd = [sys.executable, str(ARCANA_PATH / "rites" / "validate.py"), "--grimoire", str(root), "--summary"]
    try:
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    failing = [line.strip() for line in proc.stdout.splitlines() if "FAILED" in line]
    return proc.returncode == 0, ", ".join(failing) if failing else proc.stdout.strip()[-300:]


def conflicted_files(root: Path) -> list[str]:
    code, out, _ = git(root, "diff", "--name-only", "--diff-filter=U")
    return [line.strip() for line in out.splitlines() if line.strip()] if code == 0 else []


def main() -> int:
    parser = argparse.ArgumentParser(description="Save a grimoire's changes: validate, commit, pull, push")
    add_grimoire_arg(parser)
    parser.add_argument("--message", default="", help="Commit message (required with --apply when there are changes)")
    parser.add_argument("--apply", action="store_true", help="Commit, pull --rebase, and push (default: plan only)")
    parser.add_argument("--no-push", action="store_true", help="Commit and rebase but do not push")
    parser.add_argument("--no-fetch", action="store_true", help="Do not contact the remote while planning")
    add_output_format_arg(parser)
    args = parser.parse_args()
    human = args.format == "human"

    root = resolve_grimoire_arg(args.grimoire)
    mode = "apply" if args.apply else "plan"
    reporter = ResultReporter("save_grimoire", root=root, mode=mode)
    summary: dict = {"changes": [], "change_count": 0, "branch": "", "upstream": "", "ahead": 0, "behind": 0, "commit": "", "pushed": False}

    def finish(code: int) -> int:
        if human:
            return code
        reporter.emit(args.format, summary=summary)
        return code

    def block(text: str, path=None) -> int:
        reporter.message("error", text, path=path)
        reporter.set_status("blocked")
        if human:
            warn(text)
        return finish(1)

    if human:
        print()
        print(f"Save grimoire - {root.name} ({mode})")
        print()

    if not (root / ".git").exists():
        return block("this grimoire is not a git repository, so there is nothing to save to; initialise it with git first", path=root)

    changes = working_changes(root)
    summary["changes"] = changes
    summary["change_count"] = len(changes)
    state = upstream_state(root, fetch=not args.no_fetch)
    summary.update({k: state[k] for k in ("branch", "upstream", "ahead", "behind")})
    if state.get("fetch_error"):
        reporter.message("warning", f"could not reach the remote while checking for teammates' changes: {state['fetch_error']}")

    if human:
        if changes:
            info(f"{len(changes)} change(s) on branch {state['branch']}:")
            for item in changes[:60]:
                print(f"      {item['status']:<10} {item['path']}")
            if len(changes) > 60:
                print(f"      ... and {len(changes) - 60} more")
        else:
            info(f"No local changes on branch {state['branch']}.")
        if state["upstream"]:
            info(f"Upstream {state['upstream']}: {state['ahead']} to share, {state['behind']} to receive")
        elif state["remote"]:
            info("Remote 'origin' exists but this branch has no upstream yet; the save will set it.")
        else:
            info("No remote configured; the save will commit locally only.")

    if not changes and state["ahead"] == 0:
        reporter.set_status("noop")
        if human:
            ok("Nothing to save.")
        return finish(0)

    passed, detail = validation_passes(root)
    if not passed:
        return block(f"validation failed, fix it before saving: {detail}")
    reporter.message("info", "validation passed")

    if not args.apply:
        reporter.set_status("noop")
        if human:
            ok("Plan only. Re-run with --apply and a --message to save.")
        return finish(0)

    name, email = git_identity(root)
    if not name or not email:
        return block("git does not know who you are yet; run: git config --global user.name \"Your Name\" && git config --global user.email \"you@example.com\"")

    if changes:
        if not args.message.strip():
            return block("--message is required to commit")
        code, _, err = git(root, "add", "-A")
        if code != 0:
            return block(f"git add failed: {err.strip()}")
        code, _, err = git(root, "commit", "-q", "-m", args.message.strip())
        if code != 0:
            return block(f"git commit failed: {err.strip()}")
        sha = git(root, "rev-parse", "--short", "HEAD")[1].strip()
        summary["commit"] = sha
        reporter.mutation("commit", path=root, detail=f"{sha} {args.message.strip()[:72]}")
        if human:
            ok(f"Committed {sha}")

    if state["upstream"]:
        code, _, err = git(root, "pull", "--rebase", "--quiet")
        if code != 0:
            conflicts = conflicted_files(root)
            git(root, "rebase", "--abort")
            if conflicts:
                return block(
                    "teammates changed the same lines you did, so the save stopped before pushing; your commit is kept locally "
                    f"and nothing was lost. Files to reconcile: {', '.join(conflicts)}"
                )
            return block(f"could not bring the branch up to date: {err.strip()[-300:]}; your commit is kept locally")
        if human and state["behind"]:
            ok(f"Brought in {state['behind']} change(s) from {state['upstream']}")

    if args.no_push:
        reporter.message("info", "push skipped (--no-push)")
        if human:
            info("Push skipped.")
        return finish(0)

    if state["upstream"]:
        code, _, err = git(root, "push", "--quiet")
    elif state["remote"]:
        code, _, err = git(root, "push", "--quiet", "--set-upstream", "origin", state["branch"])
    else:
        reporter.message("info", "no remote configured; committed locally only")
        if human:
            info("No remote configured; your changes are committed locally.")
        return finish(0)
    if code != 0:
        return block(f"push failed: {err.strip()[-300:]}; your commit is kept locally")
    summary["pushed"] = True
    reporter.mutation("push", path=root, detail=f"{state['branch']} -> origin")
    if human:
        ok(f"Pushed {state['branch']} to origin. Your teammates will see it on their next /grm-update.")
    return finish(0)


if __name__ == "__main__":
    sys.exit(main())
