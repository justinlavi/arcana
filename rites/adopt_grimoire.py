#!/usr/bin/env python3
"""Adopt an unmanaged directory under ~/grimoires/ as a grimoire.

Writes a `grimoire.json` manifest into the target directory so the
registration and library rites recognize it. Validates the skill_prefix
isn't already used by another grimoire.

After adopting, run `/arc-library-sync --apply` to register the grimoire
in the local library, then `/arc-sync-skills` if it ships skills.

Usage:
    python3 adopt_grimoire.py <directory> --skill-prefix <prefix> [--description "<desc>"]
                                          [--name <name>] [--home <path>]
                                          [--format human|json|jsonl]

Args:
    <directory>   - directory name under ~/grimoires/ (e.g. "lus-grimoire")
                    or absolute path
    --skill-prefix   - short lowercase slug for the skill prefix (^[a-z][a-z0-9]*$)
    --description - one-line description (defaults to a placeholder)
    --name        - canonical name (defaults to the directory name)
    --home        - override grimoire home (default: ~/grimoires)
    --format      - output format: human (default), json, or jsonl

Exit codes: 0 = manifest written, 1 = validation failed, 2 = collision
"""

import argparse
import json
import sys
from pathlib import Path

from _lib import SKILL_PREFIX_RE, err, info, ok
from diagnostics import ResultReporter, add_output_format_arg

DEFAULT_HOME = Path.home() / "grimoires"


def find_existing_skill_prefixes(home):
    """Return {skill_prefix: directory_name} for every grimoire already manifested."""
    found = {}
    if not home.is_dir():
        return found
    for child in sorted(home.iterdir()):
        manifest = child / "grimoire.json"
        if not (child.is_dir() and manifest.is_file()):
            continue
        try:
            data = json.loads(manifest.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            continue
        ns = data.get("skill_prefix", "")
        if ns:
            found[ns] = child.name
    return found


def main():
    parser = argparse.ArgumentParser(description="Adopt an unmanaged grimoire")
    parser.add_argument("directory", help="Directory name under home (e.g. lus-grimoire) or absolute path")
    parser.add_argument(
        "--skill-prefix",
        dest="skill_prefix",
        required=True,
        help="Short lowercase slug for the skill prefix",
    )
    parser.add_argument("--description", default="", help="One-line description")
    parser.add_argument("--name", default="", help="Canonical name (defaults to directory name)")
    parser.add_argument("--home", type=Path, default=DEFAULT_HOME, help=f"Grimoire home (default: {DEFAULT_HOME})")
    add_output_format_arg(parser)
    args = parser.parse_args()
    human = args.format == "human"

    home = args.home.expanduser().resolve()
    reporter = ResultReporter("adopt_grimoire", root=home, mode="apply")

    if human:
        print()
        print("  Adopt Grimoire")
        print("  ----------------------------")
        print(f"  Home:        {home}")
        print()

    # Resolve the target directory.
    candidate = Path(args.directory)
    target = candidate if candidate.is_absolute() else home / args.directory
    target = target.resolve()

    if not target.is_dir():
        reporter.message("error", f"Directory does not exist: {target}", path=target)
        if human:
            err(f"Directory does not exist: {target}")
        else:
            reporter.emit(args.format)
        return 1

    if human:
        info(f"Target:      {target}")

    # Validate skill_prefix.
    if not SKILL_PREFIX_RE.fullmatch(args.skill_prefix):
        reporter.message(
            "error",
            f"Invalid skill_prefix '{args.skill_prefix}' (must match {SKILL_PREFIX_RE.pattern})",
        )
        if human:
            err(f"Invalid skill_prefix '{args.skill_prefix}' (must match {SKILL_PREFIX_RE.pattern})")
        else:
            reporter.emit(args.format)
        return 1
    if human:
        info(f"Skill prefix: {args.skill_prefix}")

    # Refuse to overwrite an existing manifest.
    manifest_path = target / "grimoire.json"
    if manifest_path.is_file():
        reporter.message("error", f"grimoire.json already exists at {manifest_path}", path=manifest_path)
        if human:
            err(f"grimoire.json already exists at {manifest_path}")
            info("To change an adopted grimoire's skill prefix, edit the manifest by hand.")
        else:
            reporter.emit(args.format)
        return 1

    # Detect skill_prefix collisions across home.
    existing = find_existing_skill_prefixes(home)
    if args.skill_prefix in existing:
        reporter.message(
            "error",
            f"Skill prefix '{args.skill_prefix}' is already used by '{existing[args.skill_prefix]}'. "
            "Pick a different skill prefix.",
        )
        if human:
            err(
                f"Skill prefix '{args.skill_prefix}' is already used by '{existing[args.skill_prefix]}'. "
                "Pick a different skill prefix."
            )
        else:
            reporter.emit(args.format)
        return 2

    name = args.name or target.name
    description = args.description or f"{name} grimoire"

    manifest = {
        "name": name,
        "skill_prefix": args.skill_prefix,
        "description": description,
    }

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    reporter.mutation("write", path=manifest_path, detail="grimoire.json")
    if human:
        ok(f"Wrote {manifest_path}")
        print()

        print("  Next steps:")
        print("    1. Run /arc-library-sync to verify, then --apply to register.")
        print("    2. If this grimoire ships skills, run /arc-sync-skills.")
        print()
    else:
        reporter.emit(args.format, summary={"name": name, "skill_prefix": args.skill_prefix})
    return 0


if __name__ == "__main__":
    sys.exit(main())
