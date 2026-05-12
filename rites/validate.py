#!/usr/bin/env python3
"""Unified validation orchestrator — runs all validation rites.

Usage:
    python3 rites/validate.py              # sequential (default)
    python3 rites/validate.py --parallel   # parallel execution
    python3 rites/validate.py --smart      # git-aware: only run validators relevant to changed files
    python3 rites/validate.py --auto       # smart + auto-execute
    python3 rites/validate.py --summary    # sequential, summary-only output

Exit codes: 0 = all passed, 1 = one or more failed
"""

import argparse
import os
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

RITE_DIR = Path(__file__).resolve().parent
ARCANA_ROOT = Path(os.environ.get("GRIMOIRE_ARCANA", RITE_DIR.parent))

RITES = [
    "validate_structure.py",
    "validate_naming.py",
    "validate_semantics.py",
    "validate_format.py",
    "validate_links.py",
    "validate_skill_refs.py",
    "validate_security.py",
]


def run_rite(name):
    """Run a single validation rite. Returns (name, success, output)."""
    result = subprocess.run(
        [sys.executable, str(RITE_DIR / name)],
        capture_output=True, text=True,
        env={**os.environ, "GRIMOIRE_ARCANA": str(ARCANA_ROOT)},
    )
    return name, result.returncode == 0, result.stdout + result.stderr


def git_changed_files():
    """Get list of changed files from git."""
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True, text=True, cwd=str(ARCANA_ROOT),
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout.strip().splitlines()
        result = subprocess.run(
            ["git", "ls-files"],
            capture_output=True, text=True, cwd=str(ARCANA_ROOT),
        )
        return result.stdout.strip().splitlines() if result.returncode == 0 else []
    except FileNotFoundError:
        return []


def determine_smart_rites():
    """Determine which validators to run based on changed files."""
    changed = git_changed_files()
    if not changed:
        return list(RITES)

    needed = set()
    for f in changed:
        path = ARCANA_ROOT / f
        if not path.exists():
            continue

        if re.match(r"^(docs|invocations|formulae|rites|formulae/grimoire)/", f):
            needed.add("validate_structure.py")

        if f.endswith((".md", ".py")):
            needed.add("validate_naming.py")
            needed.add("validate_semantics.py")
            needed.add("validate_security.py")

        if re.match(r"^(invocations|formulae)/.+\.md$", f):
            needed.add("validate_format.py")

        if f.endswith(".md"):
            try:
                content = path.read_text(errors="replace")
                if "](" in content:
                    needed.add("validate_links.py")
                if "/grm-" in content:
                    needed.add("validate_skill_refs.py")
            except OSError:
                pass

        # Adding or removing a skill changes which references are valid.
        if f.startswith("skills/"):
            needed.add("validate_skill_refs.py")

    return [r for r in RITES if r in needed] if needed else list(RITES)


def run_sequential(rites, summary_only=False):
    """Run rites sequentially. Returns number of failures."""
    failed = 0

    if not summary_only:
        print("Running Arcana Validations")
        print("=======================================")
        print()

    for rite in rites:
        if not summary_only:
            print(f"Running {rite}...")
            print("----------------------------------------")

        name, ok, output = run_rite(rite)

        if not summary_only:
            print(output, end="")
        else:
            if ok:
                print(f"  {rite}")
            else:
                print(f"  {rite} FAILED")

        if not ok:
            if summary_only:
                pass
            failed += 1

    if not summary_only:
        print()
        print("=======================================")

    return failed


def run_parallel(rites):
    """Run rites in parallel. Returns number of failures."""
    failed = 0

    print("Running Arcana Validations in Parallel")
    print("==========================================")
    print()

    results_dir = RITE_DIR / ".artifacts"
    results_dir.mkdir(parents=True, exist_ok=True)

    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(run_rite, r): r for r in rites}
        for future in as_completed(futures):
            name, ok, output = future.result()

            log_path = results_dir / f"{Path(name).stem}.log"
            log_path.write_text(output)

            if ok:
                print(f"  {name}")
            else:
                print(f"  {name} FAILED")
                failed += 1

    print()
    print("==========================================")
    return failed


def main():
    parser = argparse.ArgumentParser(description="Unified Arcana validation orchestrator")
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--parallel", action="store_true", help="Run validators in parallel")
    group.add_argument("--smart", action="store_true", help="Show which validators are relevant")
    group.add_argument("--auto", action="store_true", help="Smart + auto-execute")
    group.add_argument("--summary", action="store_true", help="Summary-only output")
    args = parser.parse_args()

    if args.smart:
        smart = determine_smart_rites()
        print("Smart Validation - Recommended:")
        for r in smart:
            print(f"  {r}")
        print()
        print("Run with --auto to execute, or individually: python3 rites/<name>.py")
        return 0

    if args.auto:
        smart = determine_smart_rites()
        print(f"Smart Validation - Running {len(smart)} relevant validator(s)")
        print()
        failed = run_sequential(smart)
    elif args.parallel:
        failed = run_parallel(RITES)
    elif args.summary:
        failed = run_sequential(RITES, summary_only=True)
    else:
        failed = run_sequential(RITES)

    if failed == 0:
        print("All validations passed")
        return 0
    else:
        print(f"{failed} validation(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
