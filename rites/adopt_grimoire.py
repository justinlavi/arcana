#!/usr/bin/env python3
"""Adopt an unmanaged directory under ~/grimoire/ as a domain grimoire.

Writes a `grimoire.json` manifest into the target directory so the
registration and catalog rites recognize it. Validates the namespace
isn't already used by another grimoire.

After adopting, run `/grm-catalog-sync --apply` to register the grimoire
in the local catalog, then `/grm-skills-register` if it ships skills.

Usage:
    python3 adopt_grimoire.py <directory> --namespace <ns> [--description "<desc>"]
                                          [--name <name>] [--home <path>]

Args:
    <directory>   — directory name under ~/grimoire/ (e.g. "lus-grimoire")
                    or absolute path
    --namespace   — short lowercase slug for skill prefix (^[a-z][a-z0-9]*$)
    --description — one-line description (defaults to a placeholder)
    --name        — canonical name (defaults to the directory name)
    --home        — override grimoire home (default: ~/grimoire)

Exit codes: 0 = manifest written, 1 = validation failed, 2 = collision
"""

import argparse
import json
import re
import sys
from pathlib import Path

DEFAULT_HOME = Path.home() / "grimoire"
NAMESPACE_RE = re.compile(r"^[a-z][a-z0-9]*$")


def info(msg):
    print(f"  [INFO]  {msg}")


def ok(msg):
    print(f"  [OK]    {msg}")


def warn(msg):
    print(f"  [WARN]  {msg}")


def err(msg):
    print(f"  [ERROR] {msg}")


def find_existing_namespaces(home):
    """Return {namespace: directory_name} for every grimoire already manifested."""
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
        ns = data.get("namespace", "")
        if ns:
            found[ns] = child.name
    return found


def main():
    parser = argparse.ArgumentParser(description="Adopt an unmanaged grimoire")
    parser.add_argument("directory", help="Directory name under home (e.g. lus-grimoire) or absolute path")
    parser.add_argument("--namespace", required=True, help="Short lowercase slug for skill prefix")
    parser.add_argument("--description", default="", help="One-line description")
    parser.add_argument("--name", default="", help="Canonical name (defaults to directory name)")
    parser.add_argument("--home", type=Path, default=DEFAULT_HOME, help=f"Grimoire home (default: {DEFAULT_HOME})")
    args = parser.parse_args()

    home = args.home.expanduser().resolve()

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
        err(f"Directory does not exist: {target}")
        return 1

    info(f"Target:      {target}")

    # Validate namespace.
    if not NAMESPACE_RE.fullmatch(args.namespace):
        err(f"Invalid namespace '{args.namespace}' (must match {NAMESPACE_RE.pattern})")
        return 1
    info(f"Namespace:   {args.namespace}")

    # Refuse to overwrite an existing manifest.
    manifest_path = target / "grimoire.json"
    if manifest_path.is_file():
        err(f"grimoire.json already exists at {manifest_path}")
        info("To re-namespace an adopted grimoire, edit the manifest by hand.")
        return 1

    # Detect namespace collisions across home.
    existing = find_existing_namespaces(home)
    if args.namespace in existing:
        err(
            f"Namespace '{args.namespace}' is already used by '{existing[args.namespace]}'. "
            "Pick a different namespace."
        )
        return 2

    name = args.name or target.name
    description = args.description or f"{name} domain grimoire"

    manifest = {
        "name": name,
        "namespace": args.namespace,
        "description": description,
    }

    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    ok(f"Wrote {manifest_path}")
    print()

    print("  Next steps:")
    print("    1. Run /grm-catalog-sync to verify, then --apply to register.")
    print("    2. If this grimoire ships skills, run /grm-skills-register.")
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
