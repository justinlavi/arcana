#!/usr/bin/env python3
"""Append a parseable entry to a grimoire's log.md.

Format documented in formulae/log_entry.formula.md:

    ## [YYYY-MM-DD HH:MM] <op> | <title>
    - skill: /<namespace>-<verb>
    - <key>: <value>
    ...

Usage:
    python3 rites/append_log.py --grimoire <path> --op <op> --title "<title>" \
        [--skill /<namespace>-<verb>] [--field key=value ...]

Args:
    --grimoire   Path to the grimoire root (default: cwd)
    --op         One of: ingest, query, lint, improve, file-answer,
                 rebuild-index, create, manual
    --title      Short human-readable title for the entry
    --skill      The skill that performed the operation (or 'manual')
    --field      Repeatable: extra `key=value` lines to add to the entry body

Exit codes: 0 = appended, 1 = invalid arguments, 2 = log.md missing
"""

import argparse
import datetime
import sys
from pathlib import Path

VALID_OPS = {"ingest", "query", "lint", "improve", "file-answer",
             "rebuild-index", "create", "manual"}


def main():
    parser = argparse.ArgumentParser(description="Append a log entry")
    parser.add_argument("--grimoire", type=Path, default=Path.cwd(),
                        help="Grimoire root (default: cwd)")
    parser.add_argument("--op", required=True, help=f"Operation tag (one of: {sorted(VALID_OPS)})")
    parser.add_argument("--title", required=True, help="Entry title")
    parser.add_argument("--skill", default="manual", help="Skill that performed the op")
    parser.add_argument("--field", action="append", default=[],
                        help="Extra `key=value` body line (repeatable)")
    args = parser.parse_args()

    if args.op not in VALID_OPS:
        print(f"  [ERROR] Invalid op '{args.op}'. Must be one of: {sorted(VALID_OPS)}", file=sys.stderr)
        return 1

    grimoire = args.grimoire.expanduser().resolve()
    log = grimoire / "log.md"
    if not log.is_file():
        print(f"  [ERROR] log.md not found at {log}", file=sys.stderr)
        return 2

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    lines = [
        "",
        f"## [{timestamp}] {args.op} | {args.title}",
        f"- skill: {args.skill}",
    ]
    for kv in args.field:
        if "=" not in kv:
            print(f"  [WARN] Skipping malformed --field '{kv}' (expected key=value)", file=sys.stderr)
            continue
        key, _, value = kv.partition("=")
        lines.append(f"- {key.strip()}: {value.strip()}")
    lines.append("")

    with open(log, "a", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"  [OK]    Appended to {log}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
