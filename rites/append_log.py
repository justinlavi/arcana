#!/usr/bin/env python3
"""Append a parseable entry to a grimoire's log.md.

Format documented in formulae/log_entry.formula.md:

    ## [YYYY-MM-DD HH:MM] <op> | <title>
   - skill: /<skill_prefix>-<verb>
   - <key>: <value>
    ...

Scope: records grimoire *content* changes (pages/sources added, removed, or
changed). Valid ops and entry rules are defined in formulae/log_entry.formula.md.

Usage:
    python3 rites/append_log.py --grimoire <path> --op <op> --title "<title>" \
        [--skill /<skill_prefix>-<verb>] [--field key=value ...] \
        [--format human|json|jsonl]

Args:
    --grimoire   Path to the grimoire root (default: cwd)
    --op         One of: import, query, health-check, improve,
                 rebuild-index, create, manual
    --title      Short human-readable title for the entry
    --skill      The skill that performed the operation (or 'manual')
    --field      Repeatable: extra `key=value` lines to add to the entry body

Exit codes: 0 = appended, 1 = invalid arguments, 2 = log.md missing
"""

import argparse
import datetime
import os
import sys
from pathlib import Path

from diagnostics import ResultReporter, add_output_format_arg

# Grimoire-content operations. See formulae/log_entry.formula.md (Scope) for the entry rules.
VALID_OPS = {
    "import", "query", "health-check", "improve",
    "rebuild-index", "create", "manual",
}


def sanitize(value: str) -> str:
    """Collapse CR/LF to spaces so a value cannot forge extra log lines."""
    return value.replace("\r", " ").replace("\n", " ")


def main():
    parser = argparse.ArgumentParser(description="Append a log entry")
    parser.add_argument("--grimoire", type=Path, default=Path.cwd(),
                        help="Grimoire root (default: cwd)")
    parser.add_argument("--op", required=True, help=f"Operation tag (one of: {sorted(VALID_OPS)})")
    parser.add_argument("--title", required=True, help="Entry title")
    parser.add_argument("--skill", default="manual", help="Skill that performed the op")
    parser.add_argument("--field", action="append", default=[],
                        help="Extra `key=value` body line (repeatable)")
    add_output_format_arg(parser)
    args = parser.parse_args()
    human = args.format == "human"

    grimoire = args.grimoire.expanduser().resolve()
    reporter = ResultReporter("append_log", root=grimoire, mode="append")
    log = grimoire / "log.md"

    if args.op not in VALID_OPS:
        reporter.message("error", f"invalid op '{args.op}' (must be one of {sorted(VALID_OPS)})")
        if human:
            print(f"  [ERROR] Invalid op '{args.op}'. Must be one of: {sorted(VALID_OPS)}", file=sys.stderr)
        else:
            reporter.emit(args.format)
        return 1

    if not log.is_file():
        reporter.message("error", f"log.md not found at {log}", path=log)
        if human:
            print(f"  [ERROR] log.md not found at {log}", file=sys.stderr)
        else:
            reporter.emit(args.format)
        return 2

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "",
        f"## [{timestamp}] {sanitize(args.op)} | {sanitize(args.title)}",
        f"- skill: {sanitize(args.skill)}",
    ]
    skipped_fields = 0
    for kv in args.field:
        if "=" not in kv:
            reporter.message("warning", f"skipping malformed --field '{kv}' (expected key=value)")
            if human:
                print(f"  [WARN] Skipping malformed --field '{kv}' (expected key=value)", file=sys.stderr)
            skipped_fields += 1
            continue
        key, _, value = kv.partition("=")
        lines.append(f"- {sanitize(key).strip()}: {sanitize(value).strip()}")
    lines.append("")

    blob = ("\n".join(lines)).encode("utf-8")
    fd = os.open(log, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
    try:
        view = memoryview(blob)
        while view:
            view = view[os.write(fd, view):]
    finally:
        os.close(fd)

    reporter.mutation("append", path=log, detail=f"{sanitize(args.op)} | {sanitize(args.title)}")
    if human:
        print(f"  [OK]    Appended to {log}")
    else:
        reporter.emit(args.format, summary={"skipped_fields": skipped_fields})
    return 0


if __name__ == "__main__":
    sys.exit(main())
