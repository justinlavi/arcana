#!/usr/bin/env python3
"""Unified validation orchestrator - runs all validation rites.

Usage:
    python3 rites/validate.py              # sequential (default)
    python3 rites/validate.py --parallel   # parallel execution
    python3 rites/validate.py --smart      # git-aware: only run validators relevant to changed files
    python3 rites/validate.py --auto       # smart + auto-execute
    python3 rites/validate.py --summary    # sequential, summary-only output

Exit codes: 0 = all passed, 1 = one or more failed
"""

import argparse
import json
import os
import re
import subprocess
import sys
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

from diagnostics import add_output_format_arg, human_label, human_location

RITE_DIR = Path(__file__).resolve().parent
ARCANA_ROOT = Path(os.environ.get("ARCANA_HOME", RITE_DIR.parent))

RITES = [
    "validate_structure.py",
    "validate_encoding.py",
    "validate_portability.py",
    "validate_naming.py",
    "validate_semantics.py",
    "validate_format.py",
    "validate_frontmatter.py",
    "validate_links.py",
    "validate_orphans.py",
    "validate_provenance.py",
    "validate_skill_refs.py",
    "validate_security.py",
]


def run_rite(name):
    """Run a single validation rite. Returns (name, success, report)."""
    result = subprocess.run(
        [sys.executable, str(RITE_DIR / name), "--format", "json"],
        capture_output=True, text=True,
        env={**os.environ, "ARCANA_HOME": str(ARCANA_ROOT)},
    )
    try:
        report = json.loads(result.stdout)
    except json.JSONDecodeError:
        report = {
            "validator": Path(name).stem,
            "status": "fail",
            "root": str(ARCANA_ROOT),
            "checked": {},
            "summary": {"errors": 1, "warnings": 0, "diagnostics": 1},
            "diagnostics": [
                {
                    "code": "VALIDATE_INVALID_VALIDATOR_REPORT",
                    "severity": "error",
                    "path": str(RITE_DIR / name),
                    "line": None,
                    "message": "validator did not emit a valid JSON diagnostic report",
                    "hint": (result.stdout + result.stderr)[-2000:],
                    "validator": "validate",
                    "docs_reference": "invocations/arcana/validators/validators.md",
                }
            ],
        }
    report["returncode"] = result.returncode
    return name, result.returncode == 0, report


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
    # Portability and encoding scan path/content globally.
    if changed:
        needed.add("validate_portability.py")
        needed.add("validate_encoding.py")
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
                if "](" in content or "[[" in content:
                    needed.add("validate_links.py")
                if "/arc-" in content:
                    needed.add("validate_skill_refs.py")
                if content.startswith("---\n"):
                    needed.add("validate_frontmatter.py")
                    if "authority:" in content:
                        needed.add("validate_provenance.py")
            except OSError:
                pass

            # Any markdown change can affect orphan reachability.
            needed.add("validate_orphans.py")

        # Adding or removing a skill changes which references are valid.
        if f.startswith("skills/"):
            needed.add("validate_skill_refs.py")

    return [r for r in RITES if r in needed] if needed else list(RITES)


def render_diagnostics(report):
    for diagnostic in report.get("diagnostics", []):
        label = human_label(diagnostic.get("severity", "error"))
        location = human_location(diagnostic)
        code = diagnostic.get("code", "UNKNOWN")
        print(f"  [{label}] {code} {location}: {diagnostic.get('message', '')}")
        hint = diagnostic.get("hint")
        if hint:
            print(f"          hint: {hint}")


def empty_suite_report(rites, reports):
    failed = sum(1 for report in reports if report.get("returncode", 1) != 0)
    errors = sum(report.get("summary", {}).get("errors", 0) for report in reports)
    warnings = sum(report.get("summary", {}).get("warnings", 0) for report in reports)
    diagnostics = sum(report.get("summary", {}).get("diagnostics", 0) for report in reports)
    return {
        "validator": "validate",
        "status": "fail" if failed else "pass",
        "root": str(ARCANA_ROOT),
        "checked": {"validators": len(rites)},
        "summary": {
            "failed_validators": failed,
            "errors": errors,
            "warnings": warnings,
            "diagnostics": diagnostics,
        },
        "reports": reports,
    }


def emit_suite_report(report, output_format):
    if output_format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
        return
    if output_format == "jsonl":
        for validator_report in report["reports"]:
            for diagnostic in validator_report.get("diagnostics", []):
                print(json.dumps(diagnostic, sort_keys=True))
        print(json.dumps({"type": "summary", **report["summary"]}, sort_keys=True))


def run_sequential(rites, summary_only=False, output_format="human"):
    """Run rites sequentially. Returns number of failures."""
    failed = 0
    reports = []
    human = output_format == "human"

    if human and not summary_only:
        print("Running Arcana Validations")
        print("=======================================")
        print()

    for rite in rites:
        if human and not summary_only:
            print(f"Running {rite}...")
            print("----------------------------------------")

        name, ok, report = run_rite(rite)
        reports.append(report)

        if human and not summary_only:
            render_diagnostics(report)
        else:
            if human:
                if ok:
                    print(f"  {rite}")
                else:
                    print(f"  {rite} FAILED")

        if not ok:
            failed += 1

    suite_report = empty_suite_report(rites, reports)
    if not human:
        emit_suite_report(suite_report, output_format)

    if human and not summary_only:
        print()
        print("=======================================")

    return failed


def run_parallel(rites, output_format="human"):
    """Run rites in parallel. Returns number of failures."""
    failed = 0
    reports = []
    human = output_format == "human"

    if human:
        print("Running Arcana Validations in Parallel")
        print("==========================================")
        print()

    results_dir = RITE_DIR / ".artifacts"
    results_dir.mkdir(parents=True, exist_ok=True)

    with ProcessPoolExecutor() as executor:
        futures = {executor.submit(run_rite, r): r for r in rites}
        for future in as_completed(futures):
            name, ok, report = future.result()
            reports.append(report)

            log_path = results_dir / f"{Path(name).stem}.log"
            log_path.write_text(json.dumps(report, indent=2, sort_keys=True))

            if human:
                if ok:
                    print(f"  {name}")
                else:
                    print(f"  {name} FAILED")
                    render_diagnostics(report)
            if not ok:
                failed += 1

    suite_report = empty_suite_report(rites, reports)
    if not human:
        emit_suite_report(suite_report, output_format)

    if human:
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
    add_output_format_arg(parser)
    args = parser.parse_args()

    if args.smart:
        smart = determine_smart_rites()
        if args.format == "human":
            print("Smart Validation - Recommended:")
            for r in smart:
                print(f"  {r}")
            print()
            print("Run with --auto to execute, or individually: python3 rites/<name>.py")
        else:
            report = {
                "validator": "validate",
                "status": "pass",
                "root": str(ARCANA_ROOT),
                "checked": {"selected_validators": len(smart)},
                "summary": {
                    "failed_validators": 0,
                    "errors": 0,
                    "warnings": 0,
                    "diagnostics": 0,
                },
                "selected_validators": smart,
                "reports": [],
            }
            emit_suite_report(report, args.format)
        return 0

    if args.auto:
        smart = determine_smart_rites()
        if args.format == "human":
            print(f"Smart Validation - Running {len(smart)} relevant validator(s)")
            print()
        failed = run_sequential(smart, output_format=args.format)
    elif args.parallel:
        failed = run_parallel(RITES, output_format=args.format)
    elif args.summary:
        failed = run_sequential(RITES, summary_only=True, output_format=args.format)
    else:
        failed = run_sequential(RITES, output_format=args.format)

    if failed == 0:
        if args.format == "human":
            print("All validations passed")
        return 0
    else:
        if args.format == "human":
            print(f"{failed} validation(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
