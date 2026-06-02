#!/usr/bin/env python3
"""Grimoire Library Sync - scan ~/grimoires/ and reconcile against the library.

Walks the grimoire home directory, identifies every valid grimoire (any
subdirectory containing a well-formed grimoire.json), and compares the result
against the local library at ~/grimoires/library.json.

Reports four kinds of drift:
  * Missing      - grimoire on disk but absent from the library
  * Stale        - library entry whose local_path no longer exists
  * Mismatched   - library entry whose local_path differs from where the
                   grimoire actually lives
  * Unmanaged    - directory under ~/grimoires/ with no grimoire.json
                   (cannot be auto-registered; reported for cleanup)

Also surfaces structural issues that don't block sync but warrant attention:
  * Skill prefix collisions across grimoires
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
from diagnostics import ResultReporter, add_output_format_arg

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_HOME = Path.home() / "grimoires"
ARCANA_NAME = "arcana"
ARCANA_MANIFEST = "arcana.json"


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
        grimoires:  [{key, path, manifest, online_path}]   - grimoires
        unmanaged:  [path]                                  - dirs without grimoire.json
        warnings:   [str]                                   - non-fatal issues
    """
    grimoires = []
    unmanaged = []
    warnings = []

    try:
        home_is_dir = home.is_dir()
    except OSError as exc:
        return {"grimoires": [], "unmanaged": [], "warnings": [f"{home}: could not access ({exc})"]}
    if not home_is_dir:
        return {"grimoires": [], "unmanaged": [], "warnings": [f"{home} does not exist"]}

    try:
        children = sorted(home.iterdir())
    except OSError as exc:
        return {"grimoires": [], "unmanaged": [], "warnings": [f"{home}: could not list ({exc})"]}

    for child in children:
        # An unstattable child (e.g. a restricted /tmp mount) must not crash the
        # whole scan; skip it with a warning and keep discovering the rest.
        try:
            if not child.is_dir():
                continue
            if child.name == ARCANA_NAME and (child / ARCANA_MANIFEST).is_file():
                continue
        except OSError as exc:
            warnings.append(f"{child.name}: could not access ({exc}); skipped")
            continue

        manifest, errors = load_manifest(child)
        if manifest is None:
            unmanaged.append(child)
            continue

        if errors:
            for e in errors:
                warnings.append(f"{child.name}: {e}")
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

    # Detect skill_prefix collisions across grimoires.
    seen = {}
    for g in grimoires:
        ns = g["manifest"].get("skill_prefix")
        if ns in seen:
            warnings.append(
                f"skill_prefix collision: '{ns}' used by both "
                f"'{seen[ns]}' and '{g['key']}' - skill registration will overwrite"
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
        missing     - keys on disk but not in library
        stale       - keys in library whose path doesn't exist
        mismatched  - keys whose library local_path differs from disk
        ok          - keys present in both with matching paths
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

        if key in disk_index:
            # Physically present under the active home: never stale. Correct the
            # recorded path when it differs from the canonical form.
            expected = expected_local_path(home, key)
            if raw != expected:
                mismatched.append(
                    {"key": key, "raw_path": raw, "expected_path": expected}
                )
            else:
                ok_keys.append(key)
            continue

        # Not present on disk under home: resolve the recorded path to classify
        # it as a still-valid out-of-home grimoire or a stale entry.
        resolved = resolve_local_path(raw)
        if not resolved.is_dir():
            stale.append({"key": key, "raw_path": raw})
            continue
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
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(library, f, indent=2)
        f.write("\n")
    tmp.replace(library_path)


class LibraryWriteConflict(Exception):
    """Raised when library.json keeps changing under a sync, so the reconciled
    result can't be written without clobbering a concurrent writer."""


def render_library_bytes(library):
    """Serialize the library exactly as write_library persists it."""
    return (json.dumps(library, indent=2) + "\n").encode("utf-8")


def library_from_bytes(raw):
    """Parse library bytes leniently, mirroring _lib.load_library's contract."""
    if not raw:
        return {"grimoires": {}}
    try:
        data = json.loads(raw)
    except json.JSONDecodeError:
        return {"grimoires": {}}
    if not isinstance(data.get("grimoires"), dict):
        data["grimoires"] = {}
    return data


def compare_and_swap_write(library_path, expected_bytes, library):
    """Write `library` only if the on-disk file still matches `expected_bytes`.

    Returns True on success, False when the file changed since it was read (a
    concurrent writer won the race) so the caller can re-read and retry instead
    of silently overwriting that writer's changes.
    """
    current = library_path.read_bytes() if library_path.is_file() else b""
    if current != expected_bytes:
        return False
    write_library(library, library_path)
    return True


def apply_synced_library(scan, library_path, home, retries=5):
    """Reconcile the library against disk and write it under compare-and-swap.

    Reading and writing library.json is a read-modify-write: a concurrent
    `/arc-library-sync` or `/arc-library-adopt` could otherwise be clobbered.
    Each attempt re-reads the current file, rebuilds from it plus the disk scan,
    and writes only if the file is unchanged; a conflict re-reads and retries so
    the concurrent change is incorporated rather than lost.

    Returns True when a write occurred, False when the library was already in
    sync (possibly reconciled by a concurrent process). Raises
    LibraryWriteConflict if the file keeps changing across `retries` attempts.
    """
    for _ in range(retries):
        current = library_path.read_bytes() if library_path.is_file() else b""
        library = library_from_bytes(current)
        new_library = build_synced_library(scan, library, home)
        if render_library_bytes(new_library) == current:
            return False
        if compare_and_swap_write(library_path, current, new_library):
            return True
    raise LibraryWriteConflict(
        f"{library_path} kept changing during {retries} sync attempts; "
        "re-run /arc-library-sync"
    )


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def print_report(scan, diff, home, library_path, apply_mode, human=True, reporter=None):
    if human:
        print()
        print(f"  Grimoire home:  {home}")
        print(f"  Library file:   {library_path}")
        print(f"  Mode:           {'apply' if apply_mode else 'dry-run (use --apply to write changes)'}")
        print()

    if scan["warnings"]:
        if human:
            print("  Structural warnings:")
        for w in scan["warnings"]:
            if human:
                warn(w)
            if reporter is not None:
                reporter.message("warning", w)
        if human:
            print()

    if scan["unmanaged"]:
        if human:
            print("  Unmanaged directories (no grimoire.json - won't be added):")
        for path in scan["unmanaged"]:
            if human:
                info(f"{path.name}/  -> add grimoire.json or move out of {home}")
            if reporter is not None:
                reporter.message(
                    "warning",
                    f"unmanaged: {path.name}/ (no grimoire.json - won't be added)",
                    path=path,
                )
        if human:
            print()

    if human:
        print(f"  Found {len(scan['grimoires'])} valid grimoire(s) on disk.")
        print(f"  Library currently lists {len(diff['ok']) + len(diff['mismatched']) + len(diff['stale'])} entry(ies).")
        print()

    drift_count = len(diff["missing"]) + len(diff["stale"]) + len(diff["mismatched"])

    if diff["missing"]:
        if human:
            print("  Missing from library (will be added):")
        for key in diff["missing"]:
            if human:
                ok(f"+ {key}")
            if reporter is not None:
                reporter.message("info", f"missing: {key} (will be added)")
        if human:
            print()

    if diff["stale"]:
        if human:
            print("  Stale library entries (will be removed):")
        for s in diff["stale"]:
            if human:
                warn(f"- {s['key']}  (path no longer resolves: {s['raw_path']})")
            if reporter is not None:
                reporter.message(
                    "warning",
                    f"stale: {s['key']} (path no longer resolves: {s['raw_path']})",
                )
        if human:
            print()

    if diff["mismatched"]:
        if human:
            print("  Mismatched local_path (will be corrected):")
        for m in diff["mismatched"]:
            if human:
                warn(
                    f"~ {m['key']}  current='{m['raw_path']}'  expected='{m['expected_path']}'"
                )
            if reporter is not None:
                reporter.message(
                    "warning",
                    f"mismatched: {m['key']} current='{m['raw_path']}' "
                    f"expected='{m['expected_path']}'",
                )
        if human:
            print()

    if drift_count == 0:
        if human:
            ok("Library is in sync with disk. No changes needed.")
            print()
        return False

    if not apply_mode:
        if human:
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
    add_output_format_arg(parser)
    args = parser.parse_args()
    human = args.format == "human"

    home = args.home.expanduser().resolve() if args.home else DEFAULT_HOME
    library_path = home / "library.json"

    reporter = ResultReporter(
        "sync_library", root=home, mode="apply" if args.apply else "plan"
    )

    if human:
        print()
        print("  Grimoire Library Sync")
        print("  ----------------------------")

    scan = scan_grimoire_home(home)
    library = load_library(library_path)
    diff = diff_library(scan, library, home)

    has_drift = print_report(
        scan, diff, home, library_path, args.apply, human=human, reporter=reporter
    )

    applied = False
    conflict = None
    if args.apply and has_drift:
        try:
            applied = apply_synced_library(scan, library_path, home)
        except LibraryWriteConflict as exc:
            conflict = str(exc)
            reporter.message("error", conflict)
            if human:
                print(f"  [ERROR] {conflict}", file=sys.stderr)
                print()
        if applied:
            reporter.mutation("write", path=library_path, detail="reconciled library")
            if human:
                ok(f"Library written: {library_path}")
                print()
                print("  Re-register skills to pick up any new grimoires:")
                print("    /arc-agent-register-skills")
                print()
        elif not conflict and human:
            ok("Library already reconciled by a concurrent process; nothing to write.")
            print()

    if not human:
        reporter.emit(
            args.format,
            summary={
                "missing": len(diff["missing"]),
                "stale": len(diff["stale"]),
                "mismatched": len(diff["mismatched"]),
                "ok": len(diff["ok"]),
                "unmanaged": len(scan["unmanaged"]),
                "applied": applied,
            },
        )

    sys.exit(1 if conflict else 0)


if __name__ == "__main__":
    main()
