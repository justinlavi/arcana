#!/usr/bin/env python3
"""Grimoire Library Sync — scan ~/grimoires/ and reconcile against the library.

Walks the grimoire home directory, identifies every valid grimoire (any
subdirectory containing a well-formed grimoire.json), and compares the result
against the local library at ~/grimoires/library.json.

Reports four kinds of drift:
  * Missing      — grimoire on disk but absent from the library
  * Stale        — library entry whose local_path no longer exists
  * Mismatched   — library entry whose local_path differs from where the
                   grimoire actually lives
  * Unmanaged    — directory under ~/grimoires/ with no grimoire.json
                   (cannot be auto-registered; reported for cleanup)

Also surfaces structural issues that don't block sync but warrant attention:
  * Namespace collisions across grimoires
  * grimoire.json `name` differing from the directory name

Defaults to a dry-run report. Pass --apply to write the reconciled library.

Usage:
    python3 sync_library.py [--apply] [--home PATH]
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

from _lib import (
    info,
    load_library,
    load_manifest,
    ok,
    resolve_local_path,
    warn,
)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_HOME = Path.home() / "grimoires"
ARCANA_NAME = "arcana"


# ---------------------------------------------------------------------------
# Disk discovery
# ---------------------------------------------------------------------------


def detect_origin_url(directory):
    """Return the git origin URL for a directory, or '' if not a git repo."""
    try:
        result = subprocess.run(
            ["git", "-C", str(directory), "remote", "get-url", "origin"],
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (subprocess.SubprocessError, FileNotFoundError):
        return ""

    if result.returncode != 0:
        return ""
    return result.stdout.strip()


def scan_grimoire_home(home):
    """Walk home, classify each subdirectory.

    Returns a dict with three lists:
        grimoires:  [{key, path, manifest, online_path}]   — domain grimoires
        unmanaged:  [path]                                  — dirs without grimoire.json
        warnings:   [str]                                   — non-fatal issues
    """
    grimoires = []
    unmanaged = []
    warnings = []

    if not home.is_dir():
        return {"grimoires": [], "unmanaged": [], "warnings": [f"{home} does not exist"]}

    for child in sorted(home.iterdir()):
        if not child.is_dir():
            continue

        manifest, errors = load_manifest(child)
        if manifest is None:
            unmanaged.append(child)
            continue

        if errors:
            for e in errors:
                warnings.append(f"{child.name}: {e}")
            continue

        # Skip Arcana itself — it is the engine, not a domain grimoire.
        if manifest.get("name") == ARCANA_NAME:
            continue

        # Surface name/directory mismatches as warnings (use directory as key).
        if manifest.get("name") != child.name:
            warnings.append(
                f"{child.name}: grimoire.json name='{manifest.get('name')}' "
                f"differs from directory name (library will use directory name)"
            )

        grimoires.append(
            {
                "key": child.name,
                "path": child,
                "manifest": manifest,
                "online_path": detect_origin_url(child),
            }
        )

    # Detect namespace collisions across grimoires.
    seen = {}
    for g in grimoires:
        ns = g["manifest"].get("namespace")
        if ns in seen:
            warnings.append(
                f"namespace collision: '{ns}' used by both "
                f"'{seen[ns]}' and '{g['key']}' — skill registration will overwrite"
            )
        else:
            seen[ns] = g["key"]

    return {"grimoires": grimoires, "unmanaged": unmanaged, "warnings": warnings}


# ---------------------------------------------------------------------------
# Library operations
# ---------------------------------------------------------------------------


def expected_local_path(home, key):
    """Return the canonical $HOME-based local_path for a grimoire."""
    home_marker = str(Path.home())
    actual = str(home / key)
    if actual.startswith(home_marker):
        return "$HOME" + actual[len(home_marker) :]
    return actual


def diff_library(scan, library, home):
    """Compute drift between disk state and library.

    Returns a dict of lists:
        missing     — keys on disk but not in library
        stale       — keys in library whose path doesn't exist
        mismatched  — keys whose library local_path differs from disk
        ok          — keys present in both with matching paths
    """
    disk_keys = {g["key"] for g in scan["grimoires"]}
    library_keys = set(library["grimoires"].keys())

    missing = sorted(disk_keys - library_keys)
    stale = []
    mismatched = []
    ok_keys = []

    disk_index = {g["key"]: g for g in scan["grimoires"]}

    for key in sorted(library_keys):
        entry = library["grimoires"][key]
        raw = entry.get("local_path", "")
        resolved = resolve_local_path(raw)

        if not resolved.is_dir():
            stale.append({"key": key, "raw_path": raw})
            continue

        if key in disk_index:
            expected = expected_local_path(home, key)
            if raw != expected:
                mismatched.append(
                    {"key": key, "raw_path": raw, "expected_path": expected}
                )
            else:
                ok_keys.append(key)
        else:
            # Library entry points to an existing directory that doesn't appear in
            # our scan (e.g., outside home, or scan classified it as unmanaged).
            # Treat as stale only if the directory lacks a valid grimoire.json.
            manifest, errors = load_manifest(resolved)
            if manifest is None or errors:
                stale.append({"key": key, "raw_path": raw})
            else:
                ok_keys.append(key)

    return {
        "missing": missing,
        "stale": stale,
        "mismatched": mismatched,
        "ok": ok_keys,
    }


def build_synced_library(scan, library, home):
    """Produce a new library dict reflecting current disk state.

    Preserves any unknown fields on existing entries; updates local_path and
    online_path; drops entries whose paths no longer resolve to valid grimoires;
    sorts entries alphabetically by key.
    """
    new_entries = {}
    disk_index = {g["key"]: g for g in scan["grimoires"]}

    # Carry forward library entries that still resolve to a valid grimoire,
    # whether or not they live under home (allows out-of-home grimoires).
    for key in library["grimoires"]:
        if key in disk_index:
            continue  # handled below from disk
        entry = dict(library["grimoires"][key])
        resolved = resolve_local_path(entry.get("local_path", ""))
        if not resolved.is_dir():
            continue
        manifest, errors = load_manifest(resolved)
        if manifest is None or errors:
            continue
        new_entries[key] = entry

    # Add/update entries from disk scan.
    for key in sorted(disk_index):
        g = disk_index[key]
        existing = library["grimoires"].get(key, {})
        entry = dict(existing)
        entry["local_path"] = expected_local_path(home, key)
        # Prefer existing online_path if present and non-empty; otherwise use
        # the detected git origin (or null).
        if not entry.get("online_path"):
            entry["online_path"] = g["online_path"] or None
        new_entries[key] = entry

    # Final sort by key for deterministic output.
    return {"grimoires": dict(sorted(new_entries.items()))}


def write_library(library, library_path):
    """Atomically write the library with stable formatting."""
    library_path.parent.mkdir(parents=True, exist_ok=True)
    tmp = library_path.with_suffix(library_path.suffix + ".tmp")
    with open(tmp, "w") as f:
        json.dump(library, f, indent=2)
        f.write("\n")
    tmp.replace(library_path)


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def print_report(scan, diff, home, library_path, apply_mode):
    print()
    print(f"  Grimoire home:  {home}")
    print(f"  Library file:   {library_path}")
    print(f"  Mode:           {'apply' if apply_mode else 'dry-run (use --apply to write changes)'}")
    print()

    if scan["warnings"]:
        print("  Structural warnings:")
        for w in scan["warnings"]:
            warn(w)
        print()

    if scan["unmanaged"]:
        print("  Unmanaged directories (no grimoire.json — won't be added):")
        for path in scan["unmanaged"]:
            info(f"{path.name}/  → add grimoire.json or move out of {home}")
        print()

    print(f"  Found {len(scan['grimoires'])} valid grimoire(s) on disk.")
    print(f"  Library currently lists {len(diff['ok']) + len(diff['mismatched']) + len(diff['stale'])} entry(ies).")
    print()

    drift_count = len(diff["missing"]) + len(diff["stale"]) + len(diff["mismatched"])

    if diff["missing"]:
        print("  Missing from library (will be added):")
        for key in diff["missing"]:
            ok(f"+ {key}")
        print()

    if diff["stale"]:
        print("  Stale library entries (will be removed):")
        for s in diff["stale"]:
            warn(f"- {s['key']}  (path no longer resolves: {s['raw_path']})")
        print()

    if diff["mismatched"]:
        print("  Mismatched local_path (will be corrected):")
        for m in diff["mismatched"]:
            warn(
                f"~ {m['key']}  current='{m['raw_path']}'  expected='{m['expected_path']}'"
            )
        print()

    if drift_count == 0:
        ok("Library is in sync with disk. No changes needed.")
        print()
        return False

    if not apply_mode:
        print(f"  {drift_count} drift item(s) detected. Re-run with --apply to write changes.")
        print()
    return True


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(description="Grimoire Library Sync")
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Write the reconciled library (default: dry-run / report only)",
    )
    parser.add_argument(
        "--home",
        type=Path,
        default=DEFAULT_HOME,
        help=f"Override grimoire home directory (default: {DEFAULT_HOME})",
    )
    args = parser.parse_args()

    home = args.home.expanduser().resolve() if args.home else DEFAULT_HOME
    library_path = home / "library.json"

    print()
    print("  Grimoire Library Sync")
    print("  ----------------------------")

    scan = scan_grimoire_home(home)
    library = load_library(library_path)
    diff = diff_library(scan, library, home)

    has_drift = print_report(scan, diff, home, library_path, args.apply)

    if args.apply and has_drift:
        new_library = build_synced_library(scan, library, home)
        write_library(new_library, library_path)
        ok(f"Library written: {library_path}")
        print()
        print("  Re-register skills to pick up any new grimoires:")
        print("    /grm-skills-register")
        print()

    sys.exit(0)


if __name__ == "__main__":
    main()
