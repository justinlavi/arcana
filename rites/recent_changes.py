#!/usr/bin/env python3
"""Render a grimoire's recent content history from git.

The grimoire's change history is its git history. This read-only rite renders
the recent commits that touched knowledge content (``chapters/``, the root hub,
``README.md``, ``grimoire.json``) as a compact table an agent or a human can
scan, so /grm-health-check and similar workflows can relate findings to recent
edits without a separate hand-maintained log.

Usage:
    python3 rites/recent_changes.py --grimoire <path> [--since 90d] [--limit 50]
        [--path chapters ...] [--format human|json|jsonl]

``--since`` accepts ``<N>d`` (days), ``<N>w`` (weeks), or any value git's own
``--since`` understands ("2026-01-01", "3 months ago").

A grimoire that is not a git repository, or a machine without git, yields
status ``noop`` with a ``no history`` message; that is the honest state and is
not an error.

Exit codes: 0 = rendered (or no history available), 1 = git failed,
2 = argparse invalid arguments.
"""

from __future__ import annotations

import argparse
import re
import shutil
import subprocess
import sys
from pathlib import Path

from _lib import add_grimoire_arg, info, resolve_grimoire_arg, warn
from diagnostics import ResultReporter, add_output_format_arg

DEFAULT_PATHS = ["chapters", "README.md", "grimoire.json"]
SINCE_SHORTHAND_RE = re.compile(r"^(\d+)([dw])$")
FIELD_SEP = "\x1f"
STATUS_LABELS = {"A": "added", "M": "changed", "D": "removed", "R": "renamed", "C": "copied"}


def normalize_since(value: str) -> str:
    """Translate ``30d`` / ``6w`` shorthand into git's ``--since`` vocabulary."""
    match = SINCE_SHORTHAND_RE.fullmatch(value.strip())
    if not match:
        return value.strip()
    count, unit = int(match.group(1)), match.group(2)
    return f"{count} {'days' if unit == 'd' else 'weeks'} ago"


def content_paths(root: Path, extra: list[str]) -> list[str]:
    """Paths whose history counts as content history: defaults plus the root hub."""
    paths = list(DEFAULT_PATHS)
    hub = f"{root.name}.md"
    if hub not in paths:
        paths.append(hub)
    for item in extra:
        if item and item not in paths:
            paths.append(item)
    return paths


def git_log(root: Path, since: str, limit: int, paths: list[str]) -> tuple[int, str, str]:
    """Run git log with a machine-parseable record format."""
    cmd = [
        "git", "-C", str(root), "log",
        f"--since={since}", f"--max-count={limit}",
        "--date=short", "--name-status", "--no-renames",
        f"--format=%x1e%h{FIELD_SEP}%ad{FIELD_SEP}%an{FIELD_SEP}%s",
        "--", *paths,
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
    return proc.returncode, proc.stdout, proc.stderr


def parse_log(output: str) -> list[dict]:
    """Parse the record-separated git output into commit dicts."""
    commits: list[dict] = []
    for record in output.split("\x1e"):
        record = record.strip("\n")
        if not record.strip():
            continue
        header, _, body = record.partition("\n")
        parts = header.split(FIELD_SEP)
        if len(parts) < 4:
            continue
        files = []
        for line in body.splitlines():
            line = line.strip()
            if not line:
                continue
            status, _, path = line.partition("\t")
            files.append({
                "status": STATUS_LABELS.get(status[:1], status),
                "path": path.replace("\\", "/"),
            })
        commits.append({
            "sha": parts[0],
            "date": parts[1],
            "author": parts[2],
            "subject": parts[3],
            "files": files,
        })
    return commits


def render_human(commits: list[dict]) -> None:
    for commit in commits:
        print(f"  {commit['date']}  {commit['sha']}  {commit['subject']}  ({commit['author']})")
        for item in commit["files"]:
            print(f"      {item['status']:<8} {item['path']}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Render recent grimoire content history from git")
    add_grimoire_arg(parser)
    parser.add_argument("--since", default="90d", help="Window: <N>d, <N>w, or a git --since value (default: 90d)")
    parser.add_argument("--limit", type=int, default=50, help="Maximum commits to render (default: 50)")
    parser.add_argument("--path", action="append", default=[], help="Extra path to include (repeatable)")
    add_output_format_arg(parser)
    args = parser.parse_args()
    human = args.format == "human"

    root = resolve_grimoire_arg(args.grimoire)
    reporter = ResultReporter("recent_changes", root=root, mode="read")
    since = normalize_since(args.since)
    paths = content_paths(root, args.path)
    summary: dict = {"since": since, "history": "git", "commits": [], "commit_count": 0, "files_changed": 0}

    if human:
        print()
        print(f"Recent content changes - {root.name}")
        print(f"Since: {since}   Paths: {', '.join(paths)}")
        print()

    if shutil.which("git") is None or not (root / ".git").exists():
        summary["history"] = "none"
        reporter.message("warning", "no history: the grimoire is not a git repository or git is unavailable", path=root)
        reporter.set_status("noop")
        if human:
            warn("No history available: not a git repository, or git is not installed.")
        else:
            reporter.emit(args.format, summary=summary)
        return 0

    code, out, err = git_log(root, since, max(1, args.limit), paths)
    if code != 0:
        reporter.message("error", f"git log failed: {err.strip()}", path=root)
        if human:
            warn(f"git log failed: {err.strip()}")
        else:
            reporter.emit(args.format, summary=summary)
        return 1

    commits = parse_log(out)
    summary["commits"] = commits
    summary["commit_count"] = len(commits)
    summary["files_changed"] = len({item["path"] for commit in commits for item in commit["files"]})
    reporter.set_status("ok")

    if human:
        if commits:
            render_human(commits)
            print()
            info(f"{len(commits)} commit(s), {summary['files_changed']} file(s) touched")
        else:
            info("No content changes in this window.")
        return 0

    reporter.emit(args.format, summary=summary)
    return 0


if __name__ == "__main__":
    sys.exit(main())
